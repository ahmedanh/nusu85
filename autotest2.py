# -*- coding: utf-8 -*-
"""SHAMEL DEEP Test Suite — tests POST forms, content rendering, embedded errors."""
import os, sys, django, re, json
os.environ['USE_LOCAL_DB'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.chdir("D:/مهم/ACDC_FINAL-main")
sys.path.insert(0, "D:/مهم/ACDC_FINAL-main")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
django.setup()
from django.conf import settings
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from django.contrib.auth import get_user_model
from attendance.models import (Student, Teacher, Coordinator, Schedule, Classroom,
    Course, LectureSession, SupportTicket, Notification, College, Department)
User = get_user_model()

PASS, FAIL = [], []

def C(username):
    c = Client()
    c.force_login(User.objects.get(username=username))
    return c

def check_body(label, body, status):
    """Detect Django error pages / template errors embedded in 200 responses."""
    errors = []
    if 'Exception Type' in body and 'Traceback' in body:
        m = re.search(r'Exception Value:.*?<pre[^>]*>(.*?)</pre>', body, re.S)
        errors.append('DJANGO ERROR: ' + (m.group(1).strip()[:80] if m else '?'))
    if 'TemplateSyntaxError' in body:
        errors.append('TEMPLATE SYNTAX ERROR')
    if 'TemplateDoesNotExist' in body:
        errors.append('TEMPLATE MISSING')
    # Unrendered template variables
    bad_vars = re.findall(r'\{\{\s*[\w.]+\s*\}\}', body)
    if bad_vars:
        errors.append(f'UNRENDERED VARS: {bad_vars[:3]}')
    # Unrendered template tags
    if '{% ' in body and '%}' in body:
        tags = re.findall(r'\{%\s*\w+', body)
        errors.append(f'UNRENDERED TAGS: {tags[:3]}')
    return errors

def GET(label, client, url, expect=(200, 302)):
    try:
        r = client.get(url, follow=True)
        body = r.content.decode('utf-8', errors='replace')
        errs = check_body(label, body, r.status_code)
        if errs:
            FAIL.append(f"[{label}] GET {url} → {'; '.join(errs)}")
            return False, body
        if r.status_code not in (expect if isinstance(expect, tuple) else (expect,)):
            FAIL.append(f"[{label}] GET {url} → {r.status_code}")
            return False, body
        PASS.append(f"[{label}] GET {url} → {r.status_code}")
        return True, body
    except Exception as e:
        FAIL.append(f"[{label}] GET {url} → EXC: {str(e)[:80]}")
        return False, ''

def POST(label, client, url, data, expect=(200, 302)):
    try:
        r = client.post(url, data, follow=True)
        body = r.content.decode('utf-8', errors='replace')
        errs = check_body(label, body, r.status_code)
        if errs:
            FAIL.append(f"[{label}] POST {url} → {'; '.join(errs)}")
            return False, body
        if r.status_code not in (expect if isinstance(expect, tuple) else (expect,)):
            FAIL.append(f"[{label}] POST {url} → {r.status_code}")
            return False, body
        PASS.append(f"[{label}] POST {url} → {r.status_code}")
        return True, body
    except Exception as e:
        FAIL.append(f"[{label}] POST {url} → EXC: {str(e)[:80]}")
        return False, ''

admin = C('admin')
coord = C('coordinator_demo')
teacher = C('tchr_13')
student = C('std_13')
print("Logins OK")

# ── Reference data ───────────────────────────────────────────────────────────
college = College.objects.first()
dept = Department.objects.first()
course = Course.objects.first()
room = Classroom.objects.first()
t = Teacher.objects.filter(auth_user__username='tchr_13').first()

# ════════════════════════════════════════════════════════════════════════════
# 1. CONTENT RENDERING — every page must render without template errors
# ════════════════════════════════════════════════════════════════════════════
print("\n── CONTENT (template errors) ──")
ALL_PAGES = [
    (admin, '/admin-panel/'), (admin, '/admin-panel/gate-reports/'),
    (admin, '/admin-panel/audit-log/'), (admin, '/admin-panel/departments/'),
    (admin, '/admin-panel/onboarding/'), (admin, '/admin-panel/dean-evaluation/'),
    (admin, '/admin-panel/faculty-timeline/'), (admin, '/admin-panel/excuse-board/'),
    (admin, '/admin-panel/exam-planner/'), (admin, '/admin-panel/exam-seating/'),
    (admin, '/admin-panel/exam-gate/'), (admin, '/admin-panel/tickets/'),
    (admin, '/faculty-management/'), (admin, '/classrooms/'),
    (admin, '/classrooms/status/'), (admin, '/courses/'),
    (admin, '/schedule/'), (admin, '/schedule/calendar/'),
    (admin, '/reports/'), (admin, '/reports/students/'), (admin, '/reports/teachers/'),
    (admin, '/search/'), (admin, '/settings/'), (admin, '/scan/'),
    (admin, '/attendance-logs/'), (admin, '/gate/'), (admin, '/notifications/'),
    (admin, '/tickets/'), (admin, '/tickets/create/'),
    (teacher, '/professor-dashboard/'), (teacher, '/teacher/timeline/'),
    (teacher, '/teacher/profile/'),
    (student, '/student/dashboard/'), (student, '/student/profile/'),
    (student, '/student/courses/'), (student, '/student/schedule/'),
    (student, '/student/excuse/'),
    (coord, '/coordinator/dashboard/'), (coord, '/coordinator/students/'),
    (coord, '/coordinator/faculty/'), (coord, '/coordinator/assignments/'),
    (coord, '/coordinator/register/'), (coord, '/coordinator/grading/'),
]
for cl, url in ALL_PAGES:
    GET('render', cl, url)

# ════════════════════════════════════════════════════════════════════════════
# 2. POST FORMS — create operations
# ════════════════════════════════════════════════════════════════════════════
print("\n── POST forms ──")

# Create a ticket
POST('ticket', student, '/tickets/create/', {
    'subject': 'Test ticket', 'category': 'technical',
    'priority': 'medium', 'description': 'Auto test description'
})

# Create a classroom
POST('classroom', admin, '/classrooms/add/', {
    'name': 'TEST-ROOM-99', 'capacity': '50', 'building': 'A', 'floor': '1'
})

# Create a course
POST('course', admin, '/courses/add/', {
    'title': 'Auto Test Course', 'course_code': 'AUTO101',
    'credit_hours': '3', 'college': college.pk if college else '',
})

# ════════════════════════════════════════════════════════════════════════════
# 3. API ENDPOINTS — JSON responses
# ════════════════════════════════════════════════════════════════════════════
print("\n── API endpoints ──")
API_URLS = [
    '/api/ping/', '/api/departments/', '/check-status/', '/recent-scans/',
    '/live-stats/',
]
for url in API_URLS:
    try:
        r = admin.get(url)
        if r.status_code == 200:
            try:
                json.loads(r.content)
                PASS.append(f"[api] {url} → valid JSON")
            except:
                if r['Content-Type'].startswith('application/json'):
                    FAIL.append(f"[api] {url} → invalid JSON")
                else:
                    PASS.append(f"[api] {url} → 200")
        elif r.status_code in (302, 404):
            PASS.append(f"[api] {url} → {r.status_code}")
        else:
            FAIL.append(f"[api] {url} → {r.status_code}")
    except Exception as e:
        FAIL.append(f"[api] {url} → EXC: {str(e)[:60]}")

# ════════════════════════════════════════════════════════════════════════════
# 4. SECURITY — role isolation
# ════════════════════════════════════════════════════════════════════════════
print("\n── Security ──")
# Student cannot reach scan station
r = student.get('/scan/', follow=False)
if r.status_code in (302, 403):
    PASS.append('[sec] Student blocked from /scan/')
else:
    FAIL.append(f'[sec] Student reached /scan/ → {r.status_code}')

# Student cannot reach faculty management
r = student.get('/faculty-management/', follow=False)
if r.status_code in (302, 403):
    PASS.append('[sec] Student blocked from /faculty-management/')
else:
    FAIL.append(f'[sec] Student reached /faculty-management/ → {r.status_code}')

# Teacher cannot reach coordinator dashboard
r = teacher.get('/coordinator/dashboard/', follow=False)
if r.status_code in (302, 403):
    PASS.append('[sec] Teacher blocked from /coordinator/dashboard/')
else:
    FAIL.append(f'[sec] Teacher reached /coordinator/dashboard/ → {r.status_code}')

# ════════════════════════════════════════════════════════════════════════════
# 5. DATA INTEGRITY — pages show real data not placeholders
# ════════════════════════════════════════════════════════════════════════════
print("\n── Data integrity ──")
ok, body = GET('data', admin, '/reports/')
if ok:
    if 'No department data available' in body:
        FAIL.append('[data] /reports/ — empty departments')
    else:
        PASS.append('[data] /reports/ — has data')

# ════════════════════════════════════════════════════════════════════════════
# RESULTS
# ════════════════════════════════════════════════════════════════════════════
print(f"\n{'='*60}")
print(f"  PASS: {len(PASS)}   FAIL: {len(FAIL)}")
print(f"{'='*60}")
if FAIL:
    print("\nFAILURES:")
    for f in FAIL: print(f"  X {f}")
else:
    print("\n  ALL TESTS PASSED")
