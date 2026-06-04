"""
SHAMEL Thesis — Web Screenshots v2 (correct URL routes)
"""
import os
from playwright.sync_api import sync_playwright

BASE = "http://localhost:8000"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'screenshots', 'web')
os.makedirs(OUT, exist_ok=True)

CREDS = {
    'admin':       ('admin',       'admin123'),
    'teacher':     ('teacher1',    'teacher123'),
    'student':     ('student1',    'student123'),
    'coordinator': ('coord1',      'coord123'),
    'gate':        ('gate1',       'gate123'),
}

def ss(page, name, wait_ms=700):
    page.wait_for_timeout(wait_ms)
    path = os.path.join(OUT, f'{name}.png')
    page.screenshot(path=path, full_page=False)
    sz = os.path.getsize(path) // 1024
    print(f"  [OK] {name}.png  ({sz}KB)")

def login(page, role):
    u, pw = CREDS[role]
    page.goto(f"{BASE}/attendance/login/", wait_until='domcontentloaded')
    page.wait_for_timeout(500)
    page.fill('input[name="username"]', u)
    page.fill('input[name="password"]', pw)
    page.click('button[type="submit"]')
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(1200)

def dark(page):
    page.evaluate("""
        document.documentElement.classList.add('dark');
        localStorage.setItem('theme','dark');
    """)
    page.wait_for_timeout(350)

def light(page):
    page.evaluate("""
        document.documentElement.classList.remove('dark');
        localStorage.setItem('theme','light');
    """)
    page.wait_for_timeout(350)

def goto(page, path, commit=False):
    try:
        wu = 'commit' if commit else 'domcontentloaded'
        page.goto(f"{BASE}/{path}", wait_until=wu, timeout=10000)
        page.wait_for_timeout(700)
        return True
    except Exception as e:
        print(f"  [SKIP] /{path} — {e}")
        return False

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
    page = ctx.new_page()

    # LOGIN PAGE
    goto(page, 'attendance/login/')
    ss(page, '01_login_light')
    dark(page)
    ss(page, '02_login_dark')

    # ADMIN
    print("\n[admin]")
    login(page, 'admin')
    dark(page)
    ss(page, '03_admin_dashboard')

    if goto(page, 'attendance/gate/'):
        ss(page, '04_admin_gate_logs')
    if goto(page, 'attendance/faculty-management/'):
        ss(page, '05_admin_faculty_mgmt')
    if goto(page, 'attendance/reports/'):
        ss(page, '06_admin_reports')
    if goto(page, 'attendance/search/'):
        ss(page, '07_admin_search')
    if goto(page, 'attendance/schedule/'):
        ss(page, '08_admin_schedule')
    if goto(page, 'attendance/classrooms/status/'):
        ss(page, '09_admin_classrooms')

    # light variant
    light(page)
    goto(page, 'attendance/')
    ss(page, '10_admin_dashboard_light')

    # TEACHER
    print("\n[teacher]")
    login(page, 'teacher')
    dark(page)
    ss(page, '11_teacher_dashboard')
    if goto(page, 'attendance/teacher/timeline/'):
        ss(page, '12_teacher_timeline')
    if goto(page, 'attendance/teacher/attendance-records/'):
        ss(page, '13_teacher_records')
    if goto(page, 'attendance/schedule/'):
        ss(page, '14_teacher_schedule')

    # STUDENT
    print("\n[student]")
    login(page, 'student')
    dark(page)
    ss(page, '15_student_dashboard')
    if goto(page, 'attendance/student/courses/'):
        ss(page, '16_student_courses')
    if goto(page, 'attendance/student/schedule/'):
        ss(page, '17_student_schedule')
    if goto(page, 'attendance/student/excuse/'):
        ss(page, '18_student_excuse')
    if goto(page, 'attendance/notifications/'):
        ss(page, '19_student_notifications')

    # COORDINATOR
    print("\n[coordinator]")
    login(page, 'coordinator')
    dark(page)
    ss(page, '20_coordinator_dashboard')
    if goto(page, 'attendance/coordinator/students/'):
        ss(page, '21_coordinator_students')
    if goto(page, 'attendance/coordinator/grading/'):
        ss(page, '22_coordinator_grading')

    # GATE
    print("\n[gate]")
    login(page, 'gate')
    dark(page)
    ss(page, '23_gate_dashboard')
    if goto(page, 'attendance/scan/', commit=True):
        page.wait_for_timeout(1500)
        ss(page, '24_gate_scan', wait_ms=200)
    if goto(page, 'attendance/attendance-logs/'):
        ss(page, '25_gate_logs')

    browser.close()
    print("\nDone.")
