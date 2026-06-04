#!/usr/bin/env python3
"""
SHAMEL System — Full Screen Inventory Generator
================================================
Produces a single PDF named 'Shamel_Full_Inventory.pdf' containing one
viewport-clipped screenshot per (role, route, viewport, theme, lang) combination.

Usage:
    python screen_inventory.py

Requirements:
    pip install playwright fpdf2 pillow
    playwright install chromium
"""

from __future__ import annotations

import os
import re
import sys
import time
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ── Force UTF-8 output on Windows (avoids cp1252 UnicodeEncodeError) ─────────
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from playwright.sync_api import sync_playwright, Page, BrowserContext, Error as PWError
from fpdf import FPDF
from PIL import Image

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────────────────────

BASE_URL = "http://127.0.0.1:8000"
# Use C:\shamel_inv\ to avoid Arabic characters in path (Windows cp1252 safe)
_WORK_DIR = Path("C:/shamel_inv_light")
_WORK_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_PDF = _WORK_DIR / "Shamel_Inventory_Light.pdf"
TMP_DIR    = _WORK_DIR / "tmp_png"
TMP_DIR.mkdir(parents=True, exist_ok=True)

# Credentials for each role (username, password).
# Gate users have no password; we use direct session-cookie injection via
# the /demo-login/ shortcut (DEBUG=True only).  For roles without a demo
# shortcut we POST to /login/ with known credentials.
ROLE_CREDS: dict[str, tuple[str, str]] = {
    "admin":       ("admin",   "admin"),
    "coordinator": ("coord1",  "admin"),
    "teacher":     ("teacher2","admin"),
    "student":     ("student2","admin"),
    "gate":        ("gate1",   "admin"),
}

# ── Viewports ─────────────────────────────────────────────────────────────────
VIEWPORTS = {
    "Desktop": {"width": 1920, "height": 1080},
    "Mobile":  {"width": 390,  "height": 844},
}

# ── Theme tokens ──────────────────────────────────────────────────────────────
THEMES = ["Light"]   # Light theme only for this documentation pass

# ── Language / direction tokens ───────────────────────────────────────────────
LANGS = ["Arabic", "English"]   # Arabic → ?lang=ar (RTL), English → ?lang=en (LTR)

# ── Per-role route map ────────────────────────────────────────────────────────
# Each entry is (label, path_or_relative_url).
# Parametric routes use a fixed sample ID that is known to exist in the DB.

ROLE_ROUTES: dict[str, list[tuple[str, str]]] = {

    # ── PUBLIC (no login required) ────────────────────────────────────────────
    "public": [
        ("Login Page",              "/login/"),
        ("Face Login",              "/login/face/"),
        ("Attendance Success",      "/attendance-success/"),
        ("Attendance Error",        "/attendance-error/"),
    ],

    # ── ADMIN (superuser — sees everything) ───────────────────────────────────
    "admin": [
        # Dashboard / home
        ("Admin Control Panel",     "/admin-panel/"),
        ("Faculty Management",      "/faculty-management/"),
        ("Reports Overview",        "/reports/"),
        ("Student Attendance Rpt",  "/reports/students/"),
        ("Teacher Attendance Rpt",  "/reports/teachers/"),
        ("Global Search",           "/search/"),
        ("Notifications",           "/notifications/"),
        ("Settings",                "/settings/"),
        # Admin-only pages
        ("Gate Reports",            "/admin-panel/gate-reports/"),
        ("Admin Notifications",     "/admin-panel/notifications/"),
        ("Audit Log",               "/admin-panel/audit-log/"),
        ("Departments",             "/admin-panel/departments/"),
        ("Onboarding Wizard",       "/admin-panel/onboarding/"),
        ("Dean Evaluation",         "/admin-panel/dean-evaluation/"),
        ("Faculty Timeline",        "/admin-panel/faculty-timeline/"),
        ("Excuse Approval Board",   "/admin-panel/excuse-board/"),
        ("Exam Planner",            "/admin-panel/exam-planner/"),
        ("Exam Seating Chart",      "/admin-panel/exam-seating/"),
        ("Exam Gate Verify",        "/admin-panel/exam-gate/"),
        ("Support Tickets",         "/admin-panel/tickets/"),
        # CRUD
        ("Courses List",            "/courses/"),
        ("Add Course",              "/courses/add/"),
        ("Classrooms List",         "/classrooms/"),
        ("Add Classroom",           "/classrooms/add/"),
        ("Classroom Status",        "/classrooms/status/"),
        ("Schedule View",           "/schedule/"),
        ("Schedule Calendar",       "/schedule/calendar/"),
        ("Add Schedule",            "/schedule/add/"),
        ("Enroll Face",             "/enroll-face/"),
        ("Gate Page",               "/gate/"),
        # Registration wizards
        ("Register Student",        "/faculty-management/register-student/"),
        ("Register Teacher",        "/faculty-management/register-teacher/"),
        # Scan
        ("Live Scan",               "/scan/"),
    ],

    # ── COORDINATOR ───────────────────────────────────────────────────────────
    "coordinator": [
        ("Coordinator Dashboard",   "/coordinator/dashboard/"),
        ("Coordinator Students",    "/coordinator/students/"),
        ("Coordinator Faculty",     "/coordinator/faculty/"),
        ("Course Assignments",      "/coordinator/assignments/"),
        ("Register User",           "/coordinator/register/"),
        ("Grading",                 "/coordinator/grading/"),
        ("Reports Overview",        "/reports/"),
        ("Student Attendance Rpt",  "/reports/students/"),
        ("Global Search",           "/search/"),
        ("Notifications",           "/notifications/"),
        ("Settings",                "/settings/"),
        ("Courses List",            "/courses/"),
        ("Classrooms List",         "/classrooms/"),
        ("Schedule View",           "/schedule/"),
        ("Support Tickets",         "/admin-panel/tickets/"),
    ],

    # ── TEACHER ───────────────────────────────────────────────────────────────
    "teacher": [
        ("Professor Dashboard",     "/professor-dashboard/"),
        ("Teacher Timeline",        "/teacher/timeline/"),
        ("Attendance Records",      "/teacher/attendance-records/"),
        ("Teacher Profile",         "/teacher/profile/"),
        ("Teacher Permissions",     "/teacher/permissions/"),
        ("Schedule View",           "/schedule/"),
        ("Reports Overview",        "/reports/"),
        ("Notifications",           "/notifications/"),
        ("Settings",                "/settings/"),
        ("Support Tickets",         "/admin-panel/tickets/"),
        ("Create Ticket",           "/tickets/create/"),
    ],

    # ── STUDENT ───────────────────────────────────────────────────────────────
    "student": [
        ("Student Dashboard",       "/student/dashboard/"),
        ("Student Profile",         "/student/profile/"),
        ("Student Courses",         "/student/courses/"),
        ("Student Schedule",        "/student/schedule/"),
        ("Student Support",         "/student/support/"),
        ("Excuse Portal",           "/student/excuse/"),
        ("Notifications",           "/notifications/"),
        ("Settings",                "/settings/"),
        ("Create Ticket",           "/tickets/create/"),
    ],

    # ── GATE OPERATOR ─────────────────────────────────────────────────────────
    "gate": [
        ("Gate Page",               "/gate/"),
        ("Live Scan",               "/scan/"),
        ("Classroom Status",        "/classrooms/status/"),
        ("Notifications",           "/notifications/"),
        ("Settings",                "/settings/"),
    ],
}

# ──────────────────────────────────────────────────────────────────────────────
# DATA STRUCTURES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class Shot:
    """Represents one captured screenshot + its metadata."""
    role:       str
    route_label:str
    path:       str
    viewport:   str
    theme:      str
    lang:       str
    png_path:   Path
    error:      Optional[str] = None

    @property
    def label(self) -> str:
        return f"{self.viewport}  |  {self.role.capitalize()}  |  {self.route_label}  |  {self.theme}  |  {self.lang}"

# ──────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def login(page: Page, username: str, password: str) -> bool:
    """POST login credentials; return True on success."""
    try:
        page.goto(f"{BASE_URL}/login/", wait_until="domcontentloaded", timeout=20_000)
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", password)
        page.click("button[type='submit']")
        page.wait_for_load_state("domcontentloaded", timeout=15_000)
        # If we are still on /login/ it failed
        if "/login" in page.url:
            return False
        return True
    except PWError:
        return False


def ensure_session(context: BrowserContext, role: str) -> Page:
    """
    Return a fresh Page that is already authenticated as the given role.
    Uses /demo-login/?role=<role> when possible, falls back to real login.
    """
    page = context.new_page()

    # Try demo shortcut first (fast, always works in DEBUG=True)
    try:
        page.goto(f"{BASE_URL}/demo-login/?role={role}", wait_until="domcontentloaded", timeout=20_000)
        if "/login" not in page.url:
            return page
    except PWError:
        pass

    # Fall back to real credentials
    if role in ROLE_CREDS:
        u, p = ROLE_CREDS[role]
        if login(page, u, p):
            return page

    # For public role: no login needed
    return page


# ──────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def set_theme(page: Page, theme: str) -> None:
    """
    Inject dark/light class on <html> and persist it via localStorage,
    matching the project's Tailwind darkMode:'class' setup.
    """
    dark = (theme == "Dark")
    page.evaluate(f"""
        (dark => {{
            const html = document.documentElement;
            if (dark) {{
                html.classList.add('dark');
                html.classList.remove('light');
            }} else {{
                html.classList.remove('dark');
                html.classList.add('light');
            }}
            try {{ localStorage.setItem('theme', dark ? 'dark' : 'light'); }} catch(e) {{}}
        }})({str(dark).lower()})
    """)

def set_dark_storage(context: BrowserContext, theme: str) -> None:
    """Pre-seed localStorage so pages load in the correct theme from the start."""
    dark = (theme == "Dark")
    context.add_init_script(f"""
        (() => {{
            try {{
                localStorage.setItem('theme', '{('dark' if dark else 'light')}');
                const html = document.documentElement;
                if ({str(dark).lower()}) {{
                    html.classList.add('dark');
                }} else {{
                    html.classList.remove('dark');
                }}
            }} catch(e) {{}}
        }})();
    """)


# ──────────────────────────────────────────────────────────────────────────────
# LANGUAGE HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def set_lang(page: Page, lang: str) -> None:
    """
    Inject the language cookie/localStorage token.
    The project reads a 'lang' cookie to switch between AR (RTL) and EN (LTR).
    If the app doesn't honour the cookie, we patch the <html> dir attribute.
    """
    code = "ar" if lang == "Arabic" else "en"
    page.evaluate(f"""
        (() => {{
            try {{ localStorage.setItem('lang', '{code}'); }} catch(e) {{}}
            document.documentElement.setAttribute('lang', '{code}');
            document.documentElement.setAttribute('dir', '{"rtl" if code == "ar" else "ltr"}');
        }})()
    """)
    # Also set cookie
    try:
        page.context.add_cookies([{
            "name": "lang", "value": code,
            "url": BASE_URL,
        }])
    except Exception:
        pass


# ──────────────────────────────────────────────────────────────────────────────
# SCREENSHOT CAPTURE
# ──────────────────────────────────────────────────────────────────────────────

MATERIAL_ICONS_CSS = "https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined"
WAIT_AFTER_LOAD_MS = 900     # extra settle time for charts / animations
FONT_WAIT_MS       = 2_000   # extra wait for web fonts on first load

# Routes whose responses are streaming / long-poll (SSE / video feed).
# We still capture them but skip networkidle wait entirely.
STREAMING_PATHS = {
    "/scan/", "/video_feed/", "/schedule/add/",
    "/schedule/calendar/add-slot/",
    "/admin-panel/notifications/",  # SSE long-poll — never reaches networkidle
    "/notifications/",              # same pattern
    "/live-stats/", "/check-status/", "/recent-scans/",
}

def wait_for_page_ready(page: Page, path: str = "") -> None:
    """
    Wait for:
    1. Network idle (capped at 4 s — never block on SSE/long-poll pages)
    2. Web fonts loaded (document.fonts.ready)
    3. Material Symbols font rendered
    4. Optional banner dismissal
    """
    is_streaming = any(path.startswith(p) for p in STREAMING_PATHS)

    if not is_streaming:
        try:
            page.wait_for_load_state("networkidle", timeout=4_000)
        except PWError:
            pass  # continue even if a slow request is still in-flight

    # Wait for fonts (non-blocking — just evaluate the promise, don't wait_for_function)
    try:
        page.evaluate("() => document.fonts.ready")
    except PWError:
        pass

    # Wait for Material Symbols font — short timeout only
    try:
        page.wait_for_function(
            "() => document.fonts.check('16px Material Symbols Outlined')",
            timeout=3_000,
        )
    except PWError:
        pass

    # Dismiss any cookie / notification permission banners
    try:
        for sel in ["button:text('Accept')", "button:text('OK')", ".toast-close", "[data-dismiss]"]:
            btn = page.query_selector(sel)
            if btn and btn.is_visible():
                btn.click()
    except PWError:
        pass

    time.sleep(WAIT_AFTER_LOAD_MS / 1000)


def capture(
    page: Page,
    role: str,
    route_label: str,
    path: str,
    vp_name: str,
    vp: dict,
    theme: str,
    lang: str,
    index: int,
) -> Shot:
    """
    Navigate to one URL, apply theme/lang, and take a viewport-clipped screenshot.
    Returns a Shot descriptor.
    """
    slug = re.sub(r"[^\w]+", "_", f"{index:04d}_{role}_{vp_name}_{theme}_{lang}_{route_label}")
    png_path = TMP_DIR / f"{slug}.png"

    shot = Shot(
        role=role, route_label=route_label, path=path,
        viewport=vp_name, theme=theme, lang=lang, png_path=png_path,
    )

    # ── CHECKPOINT RESUME: skip if PNG already captured from a previous run ──
    if png_path.exists() and png_path.stat().st_size > 2_000:
        return shot   # already captured — reuse without re-navigating

    # Build full URL; add ?lang= param so server-side i18n also picks it up
    lang_code = "ar" if lang == "Arabic" else "en"
    sep = "&" if "?" in path else "?"
    url = f"{BASE_URL}{path}{sep}lang={lang_code}"

    is_streaming = any(path.startswith(p) for p in STREAMING_PATHS)

    try:
        # Set viewport
        page.set_viewport_size(vp)

        # Navigate — streaming pages use "commit" (HTTP response started) to avoid
        # hanging on domcontentloaded which SSE/long-poll pages never fire fully
        goto_event = "commit" if is_streaming else "domcontentloaded"
        page.goto(url, wait_until=goto_event, timeout=12_000)

        # Extra brief settle for streaming pages so at least the shell renders
        if is_streaming:
            time.sleep(1.2)

        # Apply theme & lang *after* DOM is loaded
        set_theme(page, theme)
        set_lang(page, lang)

        # Wait for everything to settle (streaming paths skip networkidle)
        wait_for_page_ready(page, path)

        # Strict viewport clip — no full_page scroll
        page.screenshot(
            path=str(png_path),
            full_page=False,
            clip={"x": 0, "y": 0, "width": vp["width"], "height": vp["height"]},
            type="png",
        )

    except PWError as e:
        # Capture a red-bordered error placeholder
        shot.error = str(e)[:120]
        _make_error_placeholder(png_path, vp, shot.error)

    return shot


def _make_error_placeholder(path: Path, vp: dict, msg: str) -> None:
    """Create a grey placeholder PNG when a page fails to load."""
    from PIL import ImageDraw, ImageFont
    img = Image.new("RGB", (vp["width"], vp["height"]), color=(230, 230, 235))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, vp["width"] - 1, vp["height"] - 1],
                   outline=(200, 60, 60), width=6)
    draw.text((30, 30), "ERROR", fill=(200, 60, 60))
    # Wrap long error message
    lines = textwrap.wrap(msg, width=60)
    for i, line in enumerate(lines[:8]):
        draw.text((30, 70 + i * 22), line, fill=(100, 100, 100))
    img.save(str(path))


# ──────────────────────────────────────────────────────────────────────────────
# PDF BUILDER
# ──────────────────────────────────────────────────────────────────────────────

LABEL_HEIGHT_MM = 10   # space reserved at the bottom of each PDF page for label
MARGIN_MM       = 0    # zero margin — full bleed to the page edge

class InventoryPDF(FPDF):
    """Custom FPDF2 subclass that renders a page per screenshot."""

    def __init__(self):
        super().__init__(unit="mm")
        self.set_auto_page_break(False)
        self.set_margins(0, 0, 0)
        # Try a Unicode-capable core font (Helvetica is built-in, no TTF needed)
        self._label_font = "Helvetica"

    def add_shot(self, shot: Shot) -> None:
        """Add one landscape or portrait page for the given screenshot."""
        img = Image.open(shot.png_path)
        px_w, px_h = img.size

        # Convert pixels → mm at 96 dpi (browser default)
        DPI = 96
        img_w_mm = px_w * 25.4 / DPI
        img_h_mm = px_h * 25.4 / DPI

        # Page height = image height + label strip
        page_w_mm = img_w_mm
        page_h_mm = img_h_mm + LABEL_HEIGHT_MM

        self.add_page(format=(page_w_mm, page_h_mm))

        # ── Image (full width, no scroll) ────────────────────────────────────
        self.image(str(shot.png_path), x=0, y=0, w=img_w_mm, h=img_h_mm)

        # ── Label strip at bottom ─────────────────────────────────────────────
        # Background
        self.set_fill_color(15, 30, 60)         # navy #0F1E3C
        self.rect(0, img_h_mm, page_w_mm, LABEL_HEIGHT_MM, style="F")

        # Error badge (if any)
        if shot.error:
            self.set_fill_color(180, 40, 40)
            self.rect(0, img_h_mm, 14, LABEL_HEIGHT_MM, style="F")
            self.set_xy(1, img_h_mm + 2.5)
            self.set_font(self._label_font, "B", 6)
            self.set_text_color(255, 255, 255)
            self.cell(12, 5, "ERR", align="C")

        # Label text — build ASCII-safe version for FPDF core fonts
        label_ascii = _to_ascii_label(shot.label)
        self.set_xy(15 if shot.error else 2, img_h_mm + 2.5)
        self.set_font(self._label_font, "", 6.5)
        self.set_text_color(200, 200, 200)
        self.cell(page_w_mm - 4, 5, label_ascii, align="L")

        # Theme / viewport badges (right side)
        badges = f"[{shot.theme[:1]}]  [{shot.viewport[:3]}]  [{shot.lang[:2]}]"
        self.set_xy(0, img_h_mm + 2.5)
        self.set_font(self._label_font, "B", 6.5)
        self.set_text_color(201, 162, 39)   # gold
        self.cell(page_w_mm - 2, 5, badges, align="R")


def _to_ascii_label(text: str) -> str:
    """
    Convert label to Latin-1 safe string for FPDF core fonts.
    Arabic characters are transliterated to a bracket-wrapped phonetic tag.
    """
    result = []
    for ch in text:
        if ord(ch) < 256:
            result.append(ch)
        else:
            result.append("?")
    return "".join(result)


# ──────────────────────────────────────────────────────────────────────────────
# COVER PAGE
# ──────────────────────────────────────────────────────────────────────────────

def build_cover(pdf: InventoryPDF, total_pages: int, roles_count: dict) -> None:
    """Insert a styled cover page (A4 landscape) at position 1."""
    # We insert it after all pages are added, using FPDF2's page insertion
    # approach: build cover content then swap pages.
    # Simpler: we just add it first before shots.
    A4_W, A4_H = 297, 210  # landscape mm
    pdf.add_page(format=(A4_W, A4_H))

    # Background gradient simulation: dark navy fill
    pdf.set_fill_color(11, 37, 69)
    pdf.rect(0, 0, A4_W, A4_H, style="F")

    # Accent band at top
    pdf.set_fill_color(201, 162, 39)
    pdf.rect(0, 0, A4_W, 3, style="F")
    pdf.rect(0, A4_H - 3, A4_W, 3, style="F")

    # Vertical left accent strip
    pdf.set_fill_color(201, 162, 39)
    pdf.rect(0, 0, 8, A4_H, style="F")

    # Title
    pdf.set_xy(18, 30)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(201, 162, 39)
    pdf.cell(0, 12, "SHAMEL", ln=True)

    pdf.set_xy(18, 48)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 8, "Full Screen Inventory", ln=True)

    pdf.set_xy(18, 64)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(160, 180, 210)
    pdf.cell(0, 6, "Automated UI Audit  |  All Roles x Viewports x Themes x Languages", ln=True)

    # Stats table
    stats = [
        ("Total Pages",    str(total_pages)),
        ("Roles",          ", ".join(roles_count.keys())),
        ("Viewports",      "Desktop (1920x1080)  +  Mobile (390x844)"),
        ("Themes",         "Light  +  Dark"),
        ("Languages",      "Arabic (RTL)  +  English (LTR)"),
        ("Captured",       time.strftime("%Y-%m-%d  %H:%M:%S")),
    ]

    y = 88
    for label, val in stats:
        pdf.set_xy(18, y)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(201, 162, 39)
        pdf.cell(55, 6, label, align="L")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(220, 225, 235)
        pdf.cell(0, 6, val)
        y += 9

    # Role breakdown boxes
    box_x = 18
    box_y = y + 10
    for role, cnt in roles_count.items():
        pdf.set_fill_color(20, 55, 100)
        pdf.rect(box_x, box_y, 42, 28, style="F")
        pdf.set_fill_color(201, 162, 39)
        pdf.rect(box_x, box_y, 42, 4, style="F")
        pdf.set_xy(box_x, box_y + 5)
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(42, 5, role.upper(), align="C", ln=True)
        pdf.set_xy(box_x, box_y + 12)
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(201, 162, 39)
        pdf.cell(42, 10, str(cnt), align="C")
        pdf.set_xy(box_x, box_y + 22)
        pdf.set_font("Helvetica", "", 6)
        pdf.set_text_color(160, 175, 200)
        pdf.cell(42, 4, "pages", align="C")
        box_x += 48

    # Footer
    pdf.set_xy(0, A4_H - 12)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(80, 100, 130)
    pdf.cell(A4_W, 6,
             "Generated by screen_inventory.py  |  SHAMEL Academic Management System",
             align="C")


# ──────────────────────────────────────────────────────────────────────────────
# SECTION DIVIDERS
# ──────────────────────────────────────────────────────────────────────────────

def add_section_divider(pdf: InventoryPDF, role: str, vp: str, theme: str, lang: str, count: int) -> None:
    """A slim A4-landscape banner separating each (role, vp, theme, lang) group."""
    W, H = 297, 60
    pdf.add_page(format=(W, H))

    pdf.set_fill_color(11, 37, 69)
    pdf.rect(0, 0, W, H, style="F")
    pdf.set_fill_color(201, 162, 39)
    pdf.rect(0, 0, W, 3, style="F")

    # Left colored bar per role
    role_colors = {
        "admin": (220, 60, 60),
        "coordinator": (60, 120, 220),
        "teacher": (60, 180, 100),
        "student": (180, 100, 220),
        "gate": (220, 140, 60),
        "public": (130, 130, 130),
    }
    r, g, b = role_colors.get(role, (100, 100, 100))
    pdf.set_fill_color(r, g, b)
    pdf.rect(0, 3, 6, H - 3, style="F")

    pdf.set_xy(12, 12)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(r, g, b)
    pdf.cell(0, 8, role.upper())

    pdf.set_xy(12, 26)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(200, 210, 225)
    pdf.cell(0, 6, f"{vp}  |  {theme} Mode  |  {lang}  |  {count} screens")

    badges = [
        (vp[:3],    (50, 80, 140)),
        (theme[:1], (60, 120, 60) if theme == "Light" else (30, 30, 80)),
        (lang[:2],  (100, 60, 140)),
    ]
    bx = W - 10
    for txt, (br, bg, bb) in reversed(badges):
        pdf.set_fill_color(br, bg, bb)
        pdf.rect(bx - 18, 14, 17, 8, style="F")
        pdf.set_xy(bx - 18, 14)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(17, 8, txt, align="C")
        bx -= 22


# ──────────────────────────────────────────────────────────────────────────────
# TABLE OF CONTENTS (plain-text, no hyperlinks for compatibility)
# ──────────────────────────────────────────────────────────────────────────────

def add_toc_page(pdf: InventoryPDF, shots: list[Shot]) -> None:
    W, H = 297, 210
    pdf.add_page(format=(W, H))
    pdf.set_fill_color(11, 37, 69)
    pdf.rect(0, 0, W, H, style="F")
    pdf.set_fill_color(201, 162, 39)
    pdf.rect(0, 0, W, 3, style="F")

    pdf.set_xy(10, 10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(201, 162, 39)
    pdf.cell(0, 8, "Table of Contents")

    # Summarize groups
    from itertools import groupby
    groups: dict[tuple, list] = {}
    for s in shots:
        key = (s.role, s.viewport, s.theme, s.lang)
        groups.setdefault(key, []).append(s)

    col_w = (W - 20) / 2
    x_positions = [10, 10 + col_w]
    col = 0
    y  = 24

    for (role, vp, theme, lang), group_shots in groups.items():
        if y > H - 18:
            col += 1
            if col >= 2:
                break
            y = 24

        x = x_positions[col]
        pdf.set_xy(x, y)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(201, 162, 39)
        pdf.cell(col_w - 4, 5,
                 f"{role.upper()}  |  {vp}  |  {theme}  |  {lang}  ({len(group_shots)} screens)")
        y += 5

        for s in group_shots:
            if y > H - 18:
                break
            status = "ERR" if s.error else "   "
            pdf.set_xy(x + 4, y)
            pdf.set_font("Helvetica", "", 5.5)
            pdf.set_text_color(180, 195, 215)
            pdf.cell(col_w - 8, 4, f"{status}  {s.route_label[:55]}")
            y += 4

        y += 3


# ──────────────────────────────────────────────────────────────────────────────
# FLUTTER MOBILE CAPTURE (via ADB screencap)
# ──────────────────────────────────────────────────────────────────────────────

import subprocess
import shutil

ADB = shutil.which("adb") or r"C:\Users\ahmed\AppData\Local\Android\Sdk\platform-tools\adb.exe"

# Flutter screens to capture: (label, tap_sequence)
# tap_sequence = list of (x, y, delay_ms) — coordinates in 1080×2400 space
# ── Flutter screen definitions ────────────────────────────────────────────────
# Mirror of web ROLE_ROUTES but for the native Flutter app.
# Format: (role, label, theme, nav_steps)
# nav_steps = list of ADB actions: ("tap", x, y) | ("back",) | ("home",) | ("sleep", ms)
# Coordinates for 1080×2400 emulator screen.
# Bottom-nav positions (admin role): profile=72, notifs=213, reports=354, scan=497, home=636
# Drawer open (RTL): hamburger at x=1010,y=135
# Drawer item y-positions vary by role — captured empirically from previous screenshots.

PKG = "sd.shamel.shamel"

# Helper constants — bottom nav (admin)
_NAV = {
    "profile": ("tap", 72,  2255),
    "notifs":  ("tap", 213, 2255),
    "reports": ("tap", 354, 2255),
    "scan":    ("tap", 497, 2255),
    "home":    ("tap", 636, 2255),
}
_DRAWER = ("tap", 1010, 135)   # open hamburger
_SLEEP_NAV  = ("sleep", 1500)  # wait after navigation
_SLEEP_FAST = ("sleep", 700)

# Drawer item y-positions (admin, measured from screenshots)
_D = {
    # الإدارة group
    "teachers":    ("tap", 840, 553),
    "students":    ("tap", 840, 636),
    "courses":     ("tap", 840, 720),
    "classrooms":  ("tap", 840, 804),
    "departments": ("tap", 840, 888),
    "schedule":    ("tap", 840, 972),
    # العمليات group (after scroll)
    "cls_status":  ("tap", 840, 1090),
    "att_logs":    ("tap", 840, 1174),
    "gate_logs":   ("tap", 840, 1258),
    "gate_rep":    ("tap", 840, 1342),
    "exams":       ("tap", 840, 1426),
    "timeline":    ("tap", 840, 1510),
    # الأكاديمي
    "grades":      ("tap", 840, 1628),
    "excuses":     ("tap", 840, 1712),
    "dean_eval":   ("tap", 840, 1796),
    # النظام
    "tickets":     ("tap", 840, 1914),
    "audit":       ("tap", 840, 1998),
    "search":      ("tap", 840, 2082),
    "settings":    ("tap", 840, 2166),
}

def _drawer_nav(*keys):
    """Open drawer + tap item(s) + wait."""
    steps = [_DRAWER, _SLEEP_FAST]
    for k in keys:
        steps.append(_D[k])
    steps.append(_SLEEP_NAV)
    return steps

def _tab(key):
    return [_NAV[key], _SLEEP_NAV]

# ── Comprehensive Flutter role→screens map ─────────────────────────────────────
# (role, label, theme, nav_steps_list)
FLUTTER_ROLE_SCREENS: dict[str, list[tuple]] = {

    "public": [
        # Login screen — app starts here when logged out; we'll capture before login
        ("Login Screen", "Light", [("login_screen", True)]),
    ],

    "admin": [
        # ── Bottom nav tabs ──────────────────────────────────────────────
        ("Dashboard",           "Light", _tab("home")),
        ("Dashboard",           "Dark",  _tab("home")),
        ("Notifications",       "Light", _tab("notifs")),
        ("Notifications",       "Dark",  _tab("notifs")),
        ("Reports",             "Light", _tab("reports")),
        ("Reports",             "Dark",  _tab("reports")),
        ("Scan Station",        "Light", _tab("scan")),
        ("Scan Station",        "Dark",  _tab("scan")),
        ("Profile",             "Light", _tab("profile")),
        ("Profile",             "Dark",  _tab("profile")),
        # ── Drawer — الإدارة ─────────────────────────────────────────────
        ("Teachers List",       "Light", _drawer_nav("teachers")),
        ("Teachers List",       "Dark",  _drawer_nav("teachers")),
        ("Students List",       "Light", _drawer_nav("students")),
        ("Students List",       "Dark",  _drawer_nav("students")),
        ("Courses List",        "Light", _drawer_nav("courses")),
        ("Courses List",        "Dark",  _drawer_nav("courses")),
        ("Classrooms List",     "Light", _drawer_nav("classrooms")),
        ("Classrooms List",     "Dark",  _drawer_nav("classrooms")),
        ("Departments List",    "Light", _drawer_nav("departments")),
        ("Departments List",    "Dark",  _drawer_nav("departments")),
        ("Schedule",            "Light", _drawer_nav("schedule")),
        ("Schedule",            "Dark",  _drawer_nav("schedule")),
        # ── Drawer — العمليات ────────────────────────────────────────────
        ("Classroom Status",    "Light", _drawer_nav("cls_status")),
        ("Classroom Status",    "Dark",  _drawer_nav("cls_status")),
        ("Attendance Logs",     "Light", _drawer_nav("att_logs")),
        ("Attendance Logs",     "Dark",  _drawer_nav("att_logs")),
        ("Gate Logs",           "Light", _drawer_nav("gate_logs")),
        ("Gate Logs",           "Dark",  _drawer_nav("gate_logs")),
        ("Gate Reports",        "Light", _drawer_nav("gate_rep")),
        ("Gate Reports",        "Dark",  _drawer_nav("gate_rep")),
        ("Exams List",          "Light", _drawer_nav("exams")),
        ("Exams List",          "Dark",  _drawer_nav("exams")),
        ("Teacher Timeline",    "Light", _drawer_nav("timeline")),
        ("Teacher Timeline",    "Dark",  _drawer_nav("timeline")),
        # ── Drawer — الأكاديمي ───────────────────────────────────────────
        ("Grades",              "Light", _drawer_nav("grades")),
        ("Grades",              "Dark",  _drawer_nav("grades")),
        ("Medical Excuses",     "Light", _drawer_nav("excuses")),
        ("Medical Excuses",     "Dark",  _drawer_nav("excuses")),
        ("Dean Evaluations",    "Light", _drawer_nav("dean_eval")),
        ("Dean Evaluations",    "Dark",  _drawer_nav("dean_eval")),
        # ── Drawer — النظام ──────────────────────────────────────────────
        ("Support Tickets",     "Light", _drawer_nav("tickets")),
        ("Support Tickets",     "Dark",  _drawer_nav("tickets")),
        ("Audit Log",           "Light", _drawer_nav("audit")),
        ("Audit Log",           "Dark",  _drawer_nav("audit")),
        ("Global Search",       "Light", _drawer_nav("search")),
        ("Global Search",       "Dark",  _drawer_nav("search")),
        ("Settings",            "Light", _drawer_nav("settings")),
        ("Settings",            "Dark",  _drawer_nav("settings")),
    ],

    "coordinator": [
        ("Dashboard",           "Light", _tab("home")),
        ("Dashboard",           "Dark",  _tab("home")),
        ("Notifications",       "Light", _tab("notifs")),
        ("Notifications",       "Dark",  _tab("notifs")),
        ("Reports",             "Light", _tab("reports")),
        ("Reports",             "Dark",  _tab("reports")),
        ("Profile",             "Light", _tab("profile")),
        ("Profile",             "Dark",  _tab("profile")),
        ("Students List",       "Light", _drawer_nav("students")),
        ("Students List",       "Dark",  _drawer_nav("students")),
        ("Teachers List",       "Light", _drawer_nav("teachers")),
        ("Courses List",        "Light", _drawer_nav("courses")),
        ("Classrooms List",     "Light", _drawer_nav("classrooms")),
        ("Schedule",            "Light", _drawer_nav("schedule")),
        ("Attendance Logs",     "Light", _drawer_nav("att_logs")),
        ("Exams List",          "Light", _drawer_nav("exams")),
        ("Grades",              "Light", _drawer_nav("grades")),
        ("Medical Excuses",     "Light", _drawer_nav("excuses")),
        ("Support Tickets",     "Light", _drawer_nav("tickets")),
        ("Global Search",       "Light", _drawer_nav("search")),
        ("Settings",            "Light", _drawer_nav("settings")),
        ("Settings",            "Dark",  _drawer_nav("settings")),
    ],

    "teacher": [
        ("Dashboard",           "Light", _tab("home")),
        ("Dashboard",           "Dark",  _tab("home")),
        ("Schedule Tab",        "Light", _tab("notifs")),   # teacher: sched,scan,notifs,profile
        ("Scan Station",        "Light", _tab("scan")),
        ("Scan Station",        "Dark",  _tab("scan")),
        ("Notifications",       "Light", _tab("reports")),
        ("Profile",             "Light", _tab("profile")),
        ("Profile",             "Dark",  _tab("profile")),
        ("Teacher Timeline",    "Light", _drawer_nav("timeline")),
        ("Teacher Timeline",    "Dark",  _drawer_nav("timeline")),
        ("Attendance Logs",     "Light", _drawer_nav("att_logs")),
        ("Courses List",        "Light", _drawer_nav("courses")),
        ("Classrooms List",     "Light", _drawer_nav("classrooms")),
        ("Support Tickets",     "Light", _drawer_nav("tickets")),
        ("Settings",            "Light", _drawer_nav("settings")),
        ("Settings",            "Dark",  _drawer_nav("settings")),
    ],

    "student": [
        ("Dashboard",           "Light", _tab("home")),
        ("Dashboard",           "Dark",  _tab("home")),
        ("Schedule Tab",        "Light", _tab("notifs")),
        ("Reports Tab",         "Light", _tab("reports")),
        ("Notifications",       "Light", _tab("scan")),
        ("Profile",             "Light", _tab("profile")),
        ("Profile",             "Dark",  _tab("profile")),
        ("Courses List",        "Light", _drawer_nav("courses")),
        ("Attendance Logs",     "Light", _drawer_nav("att_logs")),
        ("Grades",              "Light", _drawer_nav("grades")),
        ("Medical Excuses",     "Light", _drawer_nav("excuses")),
        ("Support Tickets",     "Light", _drawer_nav("tickets")),
        ("Global Search",       "Light", _drawer_nav("search")),
        ("Settings",            "Light", _drawer_nav("settings")),
        ("Settings",            "Dark",  _drawer_nav("settings")),
    ],

    "gate": [
        ("Dashboard",           "Light", _tab("home")),
        ("Dashboard",           "Dark",  _tab("home")),
        ("Scan Station",        "Light", _tab("scan")),
        ("Scan Station",        "Dark",  _tab("scan")),
        ("Notifications",       "Light", _tab("notifs")),
        ("Profile",             "Light", _tab("profile")),
        ("Gate Logs",           "Light", _drawer_nav("gate_logs")),
        ("Gate Reports",        "Light", _drawer_nav("gate_rep")),
        ("Classroom Status",    "Light", _drawer_nav("cls_status")),
        ("Settings",            "Light", _drawer_nav("settings")),
        ("Settings",            "Dark",  _drawer_nav("settings")),
    ],
}

# Demo login credentials (same as web)
FLUTTER_ROLE_LOGINS = {
    "admin":       ("admin",   "admin"),
    "coordinator": ("coord1",  "admin"),
    "teacher":     ("teacher2","admin"),
    "student":     ("student2","admin"),
    "gate":        ("gate1",   "admin"),
}


def _adb(*args, timeout=8):
    """Run ADB command, ignore errors."""
    try:
        subprocess.run([ADB] + list(args), capture_output=True, timeout=timeout)
    except Exception:
        pass

def _flutter_login(username: str, password: str) -> bool:
    """
    Type credentials into the Flutter login screen via ADB.
    Assumes app is on the login screen (not yet authenticated).
    """
    time.sleep(2)
    # Tap username field (approx center of form, top input)
    _adb("shell", "input", "tap", "540", "1020")
    time.sleep(0.5)
    _adb("shell", "input", "text", username)
    time.sleep(0.3)
    # Tap password field
    _adb("shell", "input", "tap", "540", "1200")
    time.sleep(0.5)
    _adb("shell", "input", "text", password)
    time.sleep(0.3)
    # Tap login button
    _adb("shell", "input", "tap", "540", "1420")
    time.sleep(3)   # wait for auth + nav to dashboard
    return True

def _flutter_logout():
    """Open drawer → tap logout (bottom of list)."""
    _adb("shell", "input", "tap", "1010", "135")   # open drawer
    time.sleep(0.8)
    # Scroll drawer to bottom to expose logout
    _adb("shell", "input", "swipe", "540", "1800", "540", "800", "400")
    time.sleep(0.5)
    # Logout button is at bottom of drawer list
    _adb("shell", "input", "tap", "840", "2100")
    time.sleep(2)

def _flutter_set_theme(dark: bool):
    """Navigate to Settings and toggle dark mode if needed."""
    # Open drawer → settings
    _adb("shell", "input", "tap", "1010", "135")
    time.sleep(0.8)
    _adb("shell", "input", "swipe", "540", "1800", "540", "800", "400")
    time.sleep(0.5)
    # Tap settings (near bottom)
    _adb("shell", "input", "tap", "840", "2000")
    time.sleep(1.2)
    # The settings screen has a dark-mode toggle switch; tap it
    # Position: ~right side of the theme row (~x=950, y=600 based on SettingsScreen layout)
    _adb("shell", "input", "tap", "950", "600")
    time.sleep(0.8)
    # Go back to dashboard
    _adb("shell", "input", "keyevent", "4")
    time.sleep(0.5)
    _adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
    time.sleep(1.5)

def _flutter_screencap(png_path: Path) -> bool:
    """Capture current screen via ADB → local PNG. Returns True on success."""
    remote = f"/sdcard/shamel_cap_{int(time.time()*1000)}.png"
    _adb("shell", "screencap", "-p", remote, timeout=10)
    result = subprocess.run(
        [ADB, "pull", remote, str(png_path)],
        capture_output=True, timeout=20,
    )
    _adb("shell", "rm", remote)
    return png_path.exists() and png_path.stat().st_size > 1000

def _execute_nav(steps: list) -> None:
    """Execute a nav_steps list."""
    for step in steps:
        if step[0] == "tap":
            _adb("shell", "input", "tap", str(step[1]), str(step[2]))
        elif step[0] == "sleep":
            time.sleep(step[1] / 1000)
        elif step[0] == "back":
            _adb("shell", "input", "keyevent", "4")
        elif step[0] == "home":
            _adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
            time.sleep(0.5)
        elif step[0] == "login_screen":
            pass  # handled separately


def capture_flutter_screens() -> list[Shot]:
    """
    Capture all Flutter screens for all roles in both Light + Dark mode.
    Returns list of Shot objects (role='flutter_<role>', viewport='Mobile').
    """
    shots: list[Shot] = []

    if not Path(ADB).exists():
        print(f"  ADB not found — skipping Flutter capture")
        return shots

    result = subprocess.run([ADB, "devices"], capture_output=True, text=True, timeout=10)
    lines = [l for l in result.stdout.splitlines() if "\t" in l and "offline" not in l]
    if not lines:
        print("  No ADB device — skipping Flutter capture")
        return shots

    total_flutter = sum(len(v) for v in FLUTTER_ROLE_SCREENS.values())
    print(f"  ── Flutter Mobile (ADB) — {total_flutter} screens across {len(FLUTTER_ROLE_SCREENS)} roles ──")

    shot_num = 0

    for role, screen_defs in FLUTTER_ROLE_SCREENS.items():
        print(f"    Role: {role.upper()} ({len(screen_defs)} screens)")

        # ── Login as this role ────────────────────────────────────────────
        if role == "public":
            # Force logout first, then capture login screen
            _adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
            time.sleep(3)
            # If on dashboard, logout
            _flutter_logout()
            time.sleep(1)
        else:
            # Kill + relaunch to get to login screen
            _adb("shell", "am", "force-stop", PKG)
            time.sleep(1)
            _adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
            time.sleep(3)
            # If still on login screen, login
            u, p = FLUTTER_ROLE_LOGINS[role]
            _flutter_login(u, p)

        current_theme = "Light"  # app starts in light by default

        for label, theme, nav_steps in screen_defs:
            shot_num += 1

            # Switch theme if needed
            if theme != current_theme:
                _flutter_set_theme(dark=(theme == "Dark"))
                current_theme = theme

            # Navigate
            if nav_steps and nav_steps[0][0] != "login_screen":
                # Back to dashboard/home first
                _adb("shell", "input", "keyevent", "4")
                time.sleep(0.3)
                _adb("shell", "monkey", "-p", PKG, "-c", "android.intent.category.LAUNCHER", "1")
                time.sleep(1)
                _execute_nav(nav_steps)

            slug = re.sub(r"[^\w]+", "_", f"fl_{role}_{theme}_{label}")[:80]
            png_path = TMP_DIR / f"{slug}.png"

            tag = f"[flutter {shot_num:03d}/{total_flutter}]"
            if png_path.exists() and png_path.stat().st_size > 1000:
                print(f"    {tag} [skip] {role} | {theme} | {label}")
            else:
                ok = _flutter_screencap(png_path)
                if not ok:
                    _make_error_placeholder(png_path, {"width": 1080, "height": 2400}, "ADB capture failed")
                print(f"    {tag} {role:12} | {theme:5} | {label}")

            shots.append(Shot(
                role=f"flutter_{role}",
                route_label=label,
                path="",
                viewport="Mobile",
                theme=theme,
                lang="Arabic",
                png_path=png_path,
            ))

        # Reset theme to Light before switching role
        if current_theme == "Dark":
            _flutter_set_theme(dark=False)

    print(f"\n    ✓ {len(shots)} Flutter shots captured\n")
    return shots


# ──────────────────────────────────────────────────────────────────────────────
# MAIN ORCHESTRATOR
# ──────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 72)
    print("  SHAMEL Full Screen Inventory Generator")
    print("=" * 72)
    print(f"  Base URL : {BASE_URL}")
    print(f"  Output   : {OUTPUT_PDF}")
    print(f"  Temp dir : {TMP_DIR}")
    print()

    # Calculate total expected shots
    all_role_routes = list(ROLE_ROUTES.items())
    # Add public routes under "public" role (no login)
    total_expected = 0
    for role, routes in all_role_routes:
        total_expected += len(routes) * len(VIEWPORTS) * len(THEMES) * len(LANGS)
    print(f"  Planned shots: {total_expected}")
    print()

    all_shots: list[Shot] = []
    shot_index = 0
    roles_count: dict[str, int] = {}

    with sync_playwright() as pw:

        for role, routes in all_role_routes:
            role_shots = 0
            print(f"  ── Role: {role.upper()} ({len(routes)} routes) ──")

            for vp_name, vp in VIEWPORTS.items():
                for theme in THEMES:
                    for lang in LANGS:

                        # Each (vp, theme, lang) combo gets its own browser context
                        # so cookies / localStorage are cleanly separated.
                        browser = pw.chromium.launch(headless=True, args=[
                            "--disable-web-security",
                            "--no-sandbox",
                            "--font-render-hinting=none",
                        ])
                        context = browser.new_context(
                            viewport=vp,
                            device_scale_factor=1,
                            locale="ar-SA" if lang == "Arabic" else "en-US",
                            timezone_id="Asia/Riyadh",
                            color_scheme="dark" if theme == "Dark" else "light",
                        )

                        # Pre-seed theme in localStorage via init script
                        set_dark_storage(context, theme)

                        # Authenticate
                        if role == "public":
                            page = context.new_page()
                        else:
                            page = ensure_session(context, role)

                        # Load Material Symbols font once (warms browser cache)
                        try:
                            page.goto(f"{BASE_URL}/login/",
                                      wait_until="domcontentloaded", timeout=15_000)
                            page.wait_for_function(
                                "() => document.fonts.check('16px Material Symbols Outlined')",
                                timeout=FONT_WAIT_MS,
                            )
                        except PWError:
                            pass

                        # Re-authenticate if the font warmup navigated away
                        if role != "public" and "/login" in page.url:
                            page = ensure_session(context, role)

                        # ── Capture each route ────────────────────────────────
                        for route_label, path in routes:
                            shot_index += 1
                            tag = f"[{shot_index:04d}/{total_expected}]"
                            print(f"    {tag} {role:12} | {vp_name:7} | {theme:5} | {lang:7} | {route_label}")

                            shot = capture(
                                page=page,
                                role=role,
                                route_label=route_label,
                                path=path,
                                vp_name=vp_name,
                                vp=vp,
                                theme=theme,
                                lang=lang,
                                index=shot_index,
                            )
                            all_shots.append(shot)
                            role_shots += 1

                            if shot.error:
                                print(f"          !! ERROR: {shot.error[:80]}")

                        context.close()
                        browser.close()

            roles_count[role] = role_shots
            print(f"    -> {role_shots} shots captured for {role}\n")

    # ── Flutter mobile capture (ADB) — DISABLED for light-theme web pass ──────
    CAPTURE_FLUTTER = False
    if CAPTURE_FLUTTER:
        flutter_shots = capture_flutter_screens()
        all_shots.extend(flutter_shots)
        if flutter_shots:
            roles_count["flutter"] = len(flutter_shots)

    # ── Build PDF ──────────────────────────────────────────────────────────────
    print("  Building PDF …")
    pdf = InventoryPDF()
    pdf.set_creator("SHAMEL screen_inventory.py")
    pdf.set_title("SHAMEL Full Screen Inventory — Web + Flutter")
    pdf.set_author("Auto-generated by Playwright + FPDF2 + ADB")

    # Cover page (page 1)
    build_cover(pdf, len(all_shots), roles_count)

    # Table of contents (page 2)
    add_toc_page(pdf, all_shots)

    # Group shots and emit section dividers
    from itertools import groupby

    def group_key(s: Shot):
        return (s.role, s.viewport, s.theme, s.lang)

    sorted_shots = sorted(all_shots, key=group_key)

    for (role, vp, theme, lang), group_iter in groupby(sorted_shots, key=group_key):
        group = list(group_iter)
        add_section_divider(pdf, role, vp, theme, lang, len(group))
        for shot in group:
            pdf.add_shot(shot)

    pdf.output(str(OUTPUT_PDF))
    print(f"\n  ✓ PDF saved → {OUTPUT_PDF}")
    print(f"    Pages      : {len(all_shots) + 2}  (cover + TOC + {len(all_shots)} screens)")
    print(f"    File size  : {OUTPUT_PDF.stat().st_size / 1024 / 1024:.1f} MB")

    # ── Cleanup temp PNGs ──────────────────────────────────────────────────────
    removed = 0
    for f in TMP_DIR.glob("*.png"):
        f.unlink()
        removed += 1
    print(f"    Temp PNGs  : {removed} removed")
    print()
    print("  Done.")


if __name__ == "__main__":
    # Ensure Django dev server is reachable
    import urllib.request
    try:
        urllib.request.urlopen(f"{BASE_URL}/login/", timeout=5)
    except Exception as e:
        print(f"ERROR: Cannot reach {BASE_URL}  ({e})")
        print("       Start the Django server first:  python manage.py runserver")
        sys.exit(1)

    main()
