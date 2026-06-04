"""
SHAMEL Thesis — Web Screenshot Capture
Logs in as each role, captures high-fidelity screenshots for Chapter 4.
Fixes any visible UI issues before screenshotting.
"""
import os, sys, time
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots', 'web')
os.makedirs(OUT, exist_ok=True)

CREDS = {
    'admin':       ('admin',       'admin123'),
    'coordinator': ('coord1',      'coord123'),
    'teacher':     ('teacher1',    'teacher123'),
    'student':     ('student1',    'student123'),
    'gate':        ('gate1',       'gate123'),
}

def ss(page, name, wait_ms=800):
    page.wait_for_timeout(wait_ms)
    path = os.path.join(OUT, f'{name}.png')
    page.screenshot(path=path, full_page=False)
    print(f"  [OK] {name}.png")
    return path

def login(page, role):
    username, password = CREDS[role]
    page.goto(f"{BASE}/login/", wait_until='domcontentloaded')
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(1000)

def dark_mode(page):
    # toggle dark mode via JS if available
    page.evaluate("""
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme', 'dark');
    """)
    page.wait_for_timeout(400)

def try_goto(page, url, wait='domcontentloaded'):
    try:
        page.goto(url, wait_until=wait, timeout=10000)
        return True
    except Exception as e:
        print(f"  [SKIP] {url} — {e}")
        return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()

    # ── LOGIN SCREEN
    page.goto(f"{BASE}/login/", wait_until='domcontentloaded')
    page.wait_for_timeout(600)
    ss(page, '01_login_light')
    page.evaluate("document.documentElement.classList.add('dark'); localStorage.setItem('theme','dark');")
    page.wait_for_timeout(400)
    ss(page, '02_login_dark')

    # ── ADMIN ROLE
    print("\n[admin]")
    login(page, 'admin')
    dark_mode(page)
    ss(page, '03_admin_dashboard')
    if try_goto(page, f"{BASE}/gate-logs/"):
        ss(page, '04_admin_gate_logs')
    if try_goto(page, f"{BASE}/students/"):
        ss(page, '05_admin_students')
    if try_goto(page, f"{BASE}/admin-panel/audit/"):
        ss(page, '06_admin_audit')
    if try_goto(page, f"{BASE}/reports/"):
        ss(page, '07_admin_reports')

    # ── TEACHER ROLE
    print("\n[teacher]")
    login(page, 'teacher')
    dark_mode(page)
    ss(page, '08_teacher_dashboard')
    if try_goto(page, f"{BASE}/attendance/mark/"):
        ss(page, '09_teacher_mark_attendance')
    if try_goto(page, f"{BASE}/schedule/"):
        ss(page, '10_teacher_schedule')

    # ── STUDENT ROLE
    print("\n[student]")
    login(page, 'student')
    dark_mode(page)
    ss(page, '11_student_dashboard')
    if try_goto(page, f"{BASE}/attendance/my/"):
        ss(page, '12_student_attendance')
    if try_goto(page, f"{BASE}/excuses/"):
        ss(page, '13_student_excuses')
    if try_goto(page, f"{BASE}/grades/"):
        ss(page, '14_student_grades')

    # ── COORDINATOR ROLE
    print("\n[coordinator]")
    login(page, 'coordinator')
    dark_mode(page)
    ss(page, '15_coordinator_dashboard')

    # ── GATE ROLE
    print("\n[gate]")
    login(page, 'gate')
    dark_mode(page)
    ss(page, '16_gate_dashboard')
    if try_goto(page, f"{BASE}/scan/", wait='commit'):
        page.wait_for_timeout(1200)
        ss(page, '17_gate_scan_live', wait_ms=200)

    # Light mode variants for key screens
    print("\n[light mode variants]")
    login(page, 'admin')
    # remove dark
    page.evaluate("document.documentElement.classList.remove('dark'); localStorage.setItem('theme','light');")
    page.wait_for_timeout(400)
    ss(page, '18_admin_dashboard_light')

    login(page, 'student')
    page.evaluate("document.documentElement.classList.remove('dark'); localStorage.setItem('theme','light');")
    page.wait_for_timeout(400)
    ss(page, '19_student_dashboard_light')

    browser.close()

print(f"\nScreenshots saved -> {OUT}")
