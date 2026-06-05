# -*- coding: utf-8 -*-
"""
SHAMEL Web App — Full Screenshot Capture
Captures all pages across all roles in dark/light mode.
Output: thesis_output/screenshots/web/

Strategy: Use Django's test client to get session cookies (bypasses axes rate limit),
then inject cookies into Playwright browser context.
"""
import sys
import os
import time
import django

sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
os.environ["USE_LOCAL_DB"] = "true"

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# Reset axes lockouts before starting
try:
    from axes.models import AccessAttempt
    deleted, _ = AccessAttempt.objects.all().delete()
    if deleted:
        print(f"[INFO] Cleared {deleted} axes lockout(s)")
except Exception as e:
    print(f"[WARN] Could not clear axes: {e}")

BASE_URL = "http://localhost:8000"
OUT_DIR = Path(__file__).parent / "screenshots" / "web"
OUT_DIR.mkdir(parents=True, exist_ok=True)

CREDENTIALS = {
    "admin":   ("admin",           "admin123"),
    "teacher": ("teacher1",        "teacher123"),
    "student": ("std_demo_1",      None),   # password looked up via force_login
    "coord":   ("coordinator",     None),
    "gate":    ("gate",            None),
}

STREAMING_PATHS = {"/attendance/scan/", "/attendance/video_feed/", "/attendance/live-stats/"}

stats = {"ok": 0, "skip": 0, "blank": 0}


def get_session_cookie_via_django(role):
    """Use Django force_login to create a real session and return its cookie value."""
    from django.test import Client
    from django.contrib.auth import get_user_model
    User = get_user_model()
    username, _ = CREDENTIALS[role]
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"[WARN] User {username} not found in DB")
        return None, None

    c = Client(SERVER_NAME="localhost", SERVER_PORT="8000")
    c.force_login(user)

    session_id = c.cookies.get("sessionid")
    csrf_token = c.cookies.get("csrftoken")
    if session_id is None:
        print(f"[WARN] No sessionid for {role}")
        return None, None

    return session_id.value, csrf_token.value if csrf_token else None


def inject_cookies(ctx, session_id, csrf_token):
    """Inject session cookies into a Playwright browser context."""
    cookies = [{
        "name": "sessionid",
        "value": session_id,
        "domain": "localhost",
        "path": "/",
        "httpOnly": True,
        "secure": False,
    }]
    if csrf_token:
        cookies.append({
            "name": "csrftoken",
            "value": csrf_token,
            "domain": "localhost",
            "path": "/",
            "httpOnly": False,
            "secure": False,
        })
    ctx.add_cookies(cookies)


def set_dark(page):
    try:
        page.evaluate("""() => {
            document.documentElement.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }""")
    except Exception:
        pass


def set_light(page):
    try:
        page.evaluate("""() => {
            document.documentElement.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        }""")
    except Exception:
        pass


def capture(page, name, url, wait_ms=800, dark=True):
    path = OUT_DIR / f"{name}.png"
    is_streaming = any(url.startswith(p) for p in STREAMING_PATHS)
    wait_until = "commit" if is_streaming else "networkidle"

    try:
        page.goto(f"{BASE_URL}{url}", wait_until=wait_until, timeout=20000)
    except PWTimeout:
        pass  # Some pages (streaming) timeout intentionally
    except Exception as e:
        msg = str(e)[:80]
        print(f"[SKIP] {name} — nav error: {msg}")
        stats["skip"] += 1
        return

    # Check if redirected to login (access denied)
    current = page.url
    if "/login/" in current and "/attendance/login/" not in url:
        print(f"[SKIP] {name} — redirected to login")
        stats["skip"] += 1
        return

    # Check 404
    try:
        content = page.content()
        if "404" in page.title() or "Page not found" in page.title():
            print(f"[SKIP] {name} — 404")
            stats["skip"] += 1
            return
    except Exception:
        pass

    # Apply theme
    if dark:
        set_dark(page)
    else:
        set_light(page)

    time.sleep(wait_ms / 1000)

    try:
        page.screenshot(path=str(path), full_page=True)
    except Exception as e:
        print(f"[SKIP] {name} — screenshot error: {str(e)[:80]}")
        stats["skip"] += 1
        return

    size_kb = path.stat().st_size // 1024
    note = " [BLANK]" if size_kb < 10 else ""
    if note:
        stats["blank"] += 1
    else:
        stats["ok"] += 1
    print(f"[OK] {name}.png ({size_kb} KB){note}")



def run():
    # Pre-collect all session cookies BEFORE entering sync_playwright event loop
    print("[INFO] Pre-fetching session cookies via Django ORM...")
    session_cookies = {}
    for role in CREDENTIALS:
        sid, csrf = get_session_cookie_via_django(role)
        if sid:
            session_cookies[role] = (sid, csrf)
            print(f"[INFO] Got session for {role}: {sid[:8]}...")
        else:
            session_cookies[role] = (None, None)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        def make_ctx(role, dark=True):
            """Create authenticated browser context for role using pre-fetched cookie."""
            ctx = browser.new_context(viewport={"width": 1440, "height": 900})
            sid, csrf = session_cookies.get(role, (None, None))
            if sid:
                inject_cookies(ctx, sid, csrf)
            else:
                print(f"[WARN] No session for {role}")
            pg = ctx.new_page()
            # Prime localStorage theme
            pg.goto(f"{BASE_URL}/attendance/login/", wait_until="domcontentloaded", timeout=20000)
            if dark:
                set_dark(pg)
            else:
                set_light(pg)
            return ctx, pg

        # ── LOGIN PAGE (no auth needed) ──────────────────────────────────────
        print("\n-- Login pages --")
        ctx0 = browser.new_context(viewport={"width": 1440, "height": 900})
        pg0 = ctx0.new_page()
        pg0.goto(f"{BASE_URL}/attendance/login/", wait_until="networkidle", timeout=15000)
        set_light(pg0)
        time.sleep(0.8)
        pg0.screenshot(path=str(OUT_DIR / "web_00_login_light.png"), full_page=True)
        sz = (OUT_DIR / "web_00_login_light.png").stat().st_size // 1024
        print(f"[OK] web_00_login_light.png ({sz} KB)")
        stats["ok"] += 1

        set_dark(pg0)
        time.sleep(0.5)
        pg0.screenshot(path=str(OUT_DIR / "web_00_login_dark.png"), full_page=True)
        sz = (OUT_DIR / "web_00_login_dark.png").stat().st_size // 1024
        print(f"[OK] web_00_login_dark.png ({sz} KB)")
        stats["ok"] += 1
        ctx0.close()

        # ── ADMIN DARK ───────────────────────────────────────────────────────
        print("\n-- Admin pages (dark) --")
        ctx_a, pg_a = make_ctx( "admin", dark=True)
        admin_pages = [
            ("web_01_admin_dashboard",       "/attendance/admin-panel/"),
            ("web_02_admin_gate",            "/attendance/gate/"),
            ("web_03_admin_faculty",         "/attendance/faculty-management/"),
            ("web_04_admin_students_list",   "/attendance/faculty-management/register-student/"),
            ("web_05_admin_courses",         "/attendance/courses/"),
            ("web_06_admin_classrooms",      "/attendance/classrooms/"),
            ("web_07_admin_classrooms_status","/attendance/classrooms/status/"),
            ("web_08_admin_schedule",        "/attendance/schedule/"),
            ("web_09_admin_schedule_calendar","/attendance/schedule/calendar/"),
            ("web_10_admin_reports",         "/attendance/reports/"),
            ("web_11_admin_reports_students","/attendance/reports/students/"),
            ("web_12_admin_reports_teachers","/attendance/reports/teachers/"),
            ("web_13_admin_search",          "/attendance/search/"),
            ("web_14_admin_settings",        "/attendance/settings/"),
            ("web_15_admin_notifications",   "/attendance/notifications/"),
            ("web_16_admin_tickets",         "/attendance/tickets/"),
            ("web_17_admin_scan",            "/attendance/scan/"),
            ("web_18_admin_attendance_logs", "/attendance/attendance-logs/"),
            ("web_19_admin_recent_scans",    "/attendance/recent-scans/"),
        ]
        for name, url in admin_pages:
            capture(pg_a, name, url, dark=True)
        ctx_a.close()

        # ── TEACHER DARK ─────────────────────────────────────────────────────
        print("\n-- Teacher pages (dark) --")
        ctx_t, pg_t = make_ctx( "teacher", dark=True)
        teacher_pages = [
            ("web_20_teacher_dashboard",     "/attendance/professor-dashboard/"),
            ("web_21_teacher_timeline",      "/attendance/teacher/timeline/"),
            ("web_22_teacher_records",       "/attendance/teacher/attendance-records/"),
            ("web_23_teacher_schedule",      "/attendance/schedule/"),
            ("web_24_teacher_notifications", "/attendance/notifications/"),
            ("web_25_teacher_tickets",       "/attendance/tickets/"),
        ]
        for name, url in teacher_pages:
            capture(pg_t, name, url, dark=True)
        ctx_t.close()

        # ── STUDENT DARK ─────────────────────────────────────────────────────
        print("\n-- Student pages (dark) --")
        ctx_s, pg_s = make_ctx( "student", dark=True)
        student_pages = [
            ("web_26_student_dashboard",     "/attendance/student/dashboard/"),
            ("web_27_student_courses",       "/attendance/student/courses/"),
            ("web_28_student_schedule",      "/attendance/student/schedule/"),
            ("web_29_student_excuse",        "/attendance/student/excuse/"),
            ("web_30_student_profile",       "/attendance/student/profile/"),
            ("web_31_student_notifications", "/attendance/notifications/"),
            ("web_32_student_tickets",       "/attendance/tickets/"),
            ("web_33_student_support",       "/attendance/student/support/"),
        ]
        for name, url in student_pages:
            capture(pg_s, name, url, dark=True)
        ctx_s.close()

        # ── COORDINATOR DARK ─────────────────────────────────────────────────
        print("\n-- Coordinator pages (dark) --")
        ctx_c, pg_c = make_ctx( "coord", dark=True)
        coord_pages = [
            ("web_34_coord_dashboard",    "/attendance/coordinator/dashboard/"),
            ("web_35_coord_students",     "/attendance/coordinator/students/"),
            ("web_36_coord_faculty",      "/attendance/coordinator/faculty/"),
            ("web_37_coord_grading",      "/attendance/coordinator/grading/"),
            ("web_38_coord_register",     "/attendance/coordinator/register/"),
            ("web_39_coord_assignments",  "/attendance/coordinator/assignments/"),
        ]
        for name, url in coord_pages:
            capture(pg_c, name, url, dark=True)
        ctx_c.close()

        # ── GATE DARK ────────────────────────────────────────────────────────
        print("\n-- Gate pages (dark) --")
        ctx_g, pg_g = make_ctx( "gate", dark=True)
        gate_pages = [
            ("web_40_gate_dashboard",        "/attendance/gate/"),
            ("web_41_gate_scan",             "/attendance/scan/"),
            ("web_42_gate_attendance_logs",  "/attendance/attendance-logs/"),
            ("web_43_gate_recent_scans",     "/attendance/recent-scans/"),
        ]
        for name, url in gate_pages:
            wms = 1500 if "scan" in url else 800
            capture(pg_g, name, url, wait_ms=wms, dark=True)
        ctx_g.close()

        # ── LIGHT MODE VARIANTS ──────────────────────────────────────────────
        print("\n-- Light mode variants --")
        ctx_al, pg_al = make_ctx( "admin", dark=False)
        capture(pg_al, "web_44_admin_dashboard_light", "/attendance/admin-panel/", dark=False)
        ctx_al.close()

        ctx_sl, pg_sl = make_ctx( "student", dark=False)
        capture(pg_sl, "web_45_student_dashboard_light", "/attendance/student/dashboard/", dark=False)
        ctx_sl.close()

        ctx_gl, pg_gl = make_ctx( "gate", dark=False)
        capture(pg_gl, "web_46_gate_light", "/attendance/gate/", dark=False)
        ctx_gl.close()

        browser.close()

    print("\n" + "=" * 50)
    print(f"SUMMARY: {stats['ok']} captured | {stats['skip']} skipped | {stats['blank']} blank")
    print(f"Output: {OUT_DIR}")


if __name__ == "__main__":
    run()
