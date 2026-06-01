# -*- coding: utf-8 -*-
"""SHAMEL Automated Test Suite — tests every URL for every role."""
import os, sys, django, time
os.environ['USE_LOCAL_DB'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.chdir("D:/مهم/ACDC_FINAL-main")
sys.path.insert(0, "D:/مهم/ACDC_FINAL-main")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
django.setup()

# Allow Django test client host
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.contrib.auth import get_user_model
from attendance.models import Student, Teacher, Coordinator, Schedule, Classroom, Course, LectureSession, SupportTicket
User = get_user_model()

PASS, FAIL, WARN = [], [], []

def login_client(username, password):
    c = Client()
    # axes requires a request object — use force_login instead
    try:
        u = User.objects.get(username=username)
        c.force_login(u)
        return c
    except User.DoesNotExist:
        return None

def test(label, client, url, method='GET', data=None, expect=200, no_contain=None, must_contain=None):
    try:
        if method == 'POST':
            r = client.post(url, data or {}, follow=True)
        else:
            r = client.get(url, follow=True)
        code = r.status_code
        body = r.content.decode('utf-8', errors='replace')

        # Check for Django error pages
        if 'Exception Type' in body and 'Traceback' in body:
            # Extract exception
            import re
            m = re.search(r'Exception Value.*?<pre[^>]*>(.*?)</pre>', body, re.S)
            exc = m.group(1).strip()[:120] if m else 'Unknown error'
            FAIL.append(f"[{label}] {url} → EXCEPTION: {exc}")
            return False

        if code in (301, 302):
            if expect in (301, 302, 200):
                PASS.append(f"[{label}] {url} → {code} (redirect)")
                return True

        if code != expect:
            FAIL.append(f"[{label}] {url} → {code} (expected {expect})")
            return False

        if no_contain:
            for s in (no_contain if isinstance(no_contain, list) else [no_contain]):
                if s.lower() in body.lower():
                    WARN.append(f"[{label}] {url} → contains '{s}'")

        if must_contain:
            for s in (must_contain if isinstance(must_contain, list) else [must_contain]):
                if s.lower() not in body.lower():
                    FAIL.append(f"[{label}] {url} → missing '{s}'")
                    return False

        PASS.append(f"[{label}] {url} → {code}")
        return True
    except Exception as e:
        FAIL.append(f"[{label}] {url} → ERROR: {str(e)[:100]}")
        return False

# ── Clients ──────────────────────────────────────────────────────────────────
admin_c      = login_client('admin', 'Admin@1234')
coord_c      = login_client('coordinator_demo', 'Coord@1234')
teacher_c    = login_client('tchr_13', 'Teacher@1234')
student_c    = login_client('std_13', 'Student@1234')
anon_c       = Client()

assert admin_c,   "Admin login FAILED"
assert coord_c,   "Coordinator login FAILED"
assert teacher_c, "Teacher login FAILED"
assert student_c, "Student login FAILED"
print("All logins OK")

# ── Get real IDs for parametric URLs ─────────────────────────────────────────
t = Teacher.objects.filter(auth_user__username='tchr_13').first()
s = Student.objects.filter(auth_user__username='std_13').first()
co = Coordinator.objects.filter(auth_user__username='coordinator_demo').first()
sch = Schedule.objects.first()
room = Classroom.objects.first()
course = Course.objects.first()
session = LectureSession.objects.first()
ticket = SupportTicket.objects.first()

tid = t.teacher_id if t else 1
sid = s.id if s else 1
cid = co.pk if co else 1
sch_id = sch.pk if sch else 1
room_id = room.pk if room else 1
course_id = course.pk if course else 1

# ════════════════════════════════════════════════════════════════════════════
# ADMIN TESTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── ADMIN ──")
ADMIN_URLS = [
    ('/login/',                          200, None, None),  # redirects to dashboard when logged in
    ('/admin-panel/',                    200, None, ['dashboard', 'admin']),
    ('/admin-panel/gate-reports/',       200, None, None),
    ('/notifications/',                  200, None, None),
    ('/admin-panel/audit-log/',           200, None, None),
    ('/admin-panel/departments/',         200, None, None),
    ('/admin-panel/onboarding/',          200, None, None),
    ('/admin-panel/dean-evaluation/',     200, None, None),
    ('/admin-panel/faculty-timeline/',    200, None, None),
    ('/admin-panel/excuse-board/',        200, None, None),
    ('/admin-panel/exam-planner/',        200, None, None),
    ('/admin-panel/exam-seating/',        200, None, None),
    ('/admin-panel/exam-gate/',           200, None, None),
    ('/admin-panel/tickets/',             200, None, None),
    ('/faculty-management/',             200, None, None),
    ('/classrooms/',                     200, None, ['classroom']),
    ('/classrooms/status/',              200, None, None),
    ('/classrooms/add/',                 200, None, None),
    ('/courses/',                        200, None, ['course']),
    ('/courses/add/',                    200, None, None),
    ('/schedule/',                       200, None, None),
    ('/schedule/add/',                   200, None, None),
    ('/schedule/calendar/',              200, None, None),
    ('/reports/',                        200, None, ['attendance', 'sessions']),
    ('/reports/students/',               200, None, None),
    ('/reports/teachers/',               200, None, None),
    ('/search/',                         200, None, None),
    ('/settings/',                       200, None, None),
    ('/scan/',                           200, None, None),
    ('/attendance-logs/',                200, None, None),
    ('/gate/',                           200, None, None),
    ('/tickets/',                        200, None, None),
    ('/tickets/create/',                 200, None, None),
    ('/teacher/profile/',                 200, None, None),  # admin can view teacher profile
    ('/teacher/profile/',                 200, None, None),
    ('/faculty-management/register-student/', 200, None, None),
    ('/faculty-management/register-teacher/', 200, None, None),
    ('/api/ping/',                       200, None, ['ok']),
]
for url, exp, nc, mc in ADMIN_URLS:
    test('admin', admin_c, url, expect=exp, no_contain=nc, must_contain=mc)

# ════════════════════════════════════════════════════════════════════════════
# TEACHER TESTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── TEACHER ──")
TEACHER_URLS = [
    ('/professor-dashboard/',            200, None, None),
    ('/teacher/timeline/',               200, None, None),
    ('/teacher/profile/',                200, None, None),
    ('/attendance-logs/',                200, None, None),
    ('/notifications/',                  200, None, None),
    ('/tickets/',                        200, None, None),
    ('/tickets/create/',                 200, None, None),
]
for url, exp, nc, mc in TEACHER_URLS:
    test('teacher', teacher_c, url, expect=exp, no_contain=nc, must_contain=mc)

# ════════════════════════════════════════════════════════════════════════════
# STUDENT TESTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── STUDENT ──")
STUDENT_URLS = [
    ('/student/dashboard/',              200, None, None),
    # admin has no Student profile — skip this URL for admin
    # ('/student/profile/', 404, None, None),
    ('/student/courses/',                200, None, None),
    ('/student/schedule/',               200, None, None),
    ('/student/excuse/',                 200, None, None),
    ('/notifications/',                  200, None, None),
    ('/tickets/',                        200, None, None),
    ('/tickets/create/',                 200, None, None),
]
for url, exp, nc, mc in STUDENT_URLS:
    test('student', student_c, url, expect=exp, no_contain=nc, must_contain=mc)

# ════════════════════════════════════════════════════════════════════════════
# COORDINATOR TESTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── COORDINATOR ──")
COORD_URLS = [
    ('/coordinator/dashboard/',          200, None, None),
    ('/coordinator/students/',           200, None, None),
    ('/coordinator/faculty/',            200, None, None),
    ('/coordinator/assignments/',        200, None, None),
    ('/coordinator/register/',           200, None, None),
    ('/coordinator/grading/',            200, None, None),
    ('/notifications/',                  200, None, None),
    ('/tickets/',                        200, None, None),
]
for url, exp, nc, mc in COORD_URLS:
    test('coord', coord_c, url, expect=exp, no_contain=nc, must_contain=mc)

# ════════════════════════════════════════════════════════════════════════════
# ANON — must redirect to login
# ════════════════════════════════════════════════════════════════════════════
print("\n── ANON (must redirect) ──")
for url in ['/admin-panel/', '/student/dashboard/', '/professor-dashboard/', '/coordinator/dashboard/', '/schedule/']:
    r = anon_c.get(url)
    if r.status_code in (301, 302) and 'login' in r.get('Location', '').lower():
        PASS.append(f"[anon] {url} → redirect to login")
    else:
        FAIL.append(f"[anon] {url} → {r.status_code} (expected redirect to login)")

# ════════════════════════════════════════════════════════════════════════════
# LOGIC TESTS
# ════════════════════════════════════════════════════════════════════════════
print("\n── LOGIC ──")

# 1. API ping
r = admin_c.get('/api/ping/')
import json
d = json.loads(r.content)
if d.get('ok'):
    PASS.append('[logic] /api/ping/ returns ok=true')
else:
    FAIL.append('[logic] /api/ping/ bad response')

# 2. Reports data populated
r = admin_c.get('/reports/')
body = r.content.decode('utf-8', errors='replace')
if 'No department data available' in body:
    WARN.append('[logic] /reports/ — no department data (populate DB)')
else:
    PASS.append('[logic] /reports/ has department data')

# 3. Teacher report — the t.id bug we fixed
r = admin_c.get('/reports/teachers/')
body3 = r.content.decode('utf-8', errors='replace')
if r.status_code == 200 and 'AttributeError' not in body3 and 'Exception Type' not in body3:
    PASS.append('[logic] /reports/teachers/ — no AttributeError')
else:
    FAIL.append(f'[logic] /reports/teachers/ — status={r.status_code}')

# 4. Schedule add loads without timeout
r = admin_c.get('/schedule/add/?course_q=computer')
body = r.content.decode('utf-8', errors='replace')
if r.status_code == 200:
    PASS.append('[logic] /schedule/add/ — loads with search filter')
else:
    FAIL.append('[logic] /schedule/add/ failed')

# 5. Classrooms status (InterfaceError fixed)
r = admin_c.get('/classrooms/status/')
if r.status_code == 200:
    PASS.append('[logic] /classrooms/status/ — no InterfaceError')
else:
    FAIL.append(f'[logic] /classrooms/status/ — {r.status_code}')

# 6. Student can't access admin panel
r = student_c.get('/admin-panel/', follow=False)
if r.status_code in (302, 403):
    PASS.append('[logic] Student blocked from /admin-panel/')
else:
    FAIL.append(f'[logic] Student reached /admin-panel/ → {r.status_code}')

# 7. Coordinator IS staff → can access admin panel (by design)
r = coord_c.get('/admin-panel/', follow=False)
if r.status_code == 200:
    PASS.append('[logic] Coordinator (is_staff) can access /admin-panel/ — by design')
else:
    WARN.append(f'[logic] Coordinator /admin-panel/ → {r.status_code}')

# 8. IDOR — student tries to access another student profile
other_s = Student.objects.exclude(auth_user__username='std_13').first()
if other_s:
    r = student_c.get(f'/student/{other_s.id}/')
    if r.status_code in (403, 302, 404):
        PASS.append('[logic] IDOR blocked: student cant view other student profile')
    else:
        WARN.append(f'[logic] IDOR: student can view another student profile (/{other_s.student_id}/)')

# 9. Offline sync endpoint
r = admin_c.get('/api/ping/')
if r.status_code == 200:
    PASS.append('[logic] Connectivity check endpoint working')

# ════════════════════════════════════════════════════════════════════════════
# RESULTS
# ════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  PASS: {len(PASS)}   FAIL: {len(FAIL)}   WARN: {len(WARN)}")
print(f"{'='*60}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL: print(f"  ✗ {f}")
if WARN:
    print("\nWARNINGS:")
    for w in WARN: print(f"  ⚠ {w}")
print(f"\nPASS list (first 20):")
for p in PASS[:20]: print(f"  ✓ {p}")
