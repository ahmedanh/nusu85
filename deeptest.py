# -*- coding: utf-8 -*-
"""
SHAMEL DEEP TEST HARNESS
Tests: every GET page, every POST form, every dropdown, every button action,
       PWA completeness, N+1 queries, template integrity, role security.
"""
import os, sys, django, json, re, time
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
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model
from django.urls import reverse, NoReverseMatch
from attendance.models import (Student, Teacher, Coordinator, Schedule, Classroom,
    Course, LectureSession, SupportTicket, Notification, Department, College)
User = get_user_model()

PASS, FAIL, WARN, INFO = [], [], [], []
def p(m): PASS.append(m)
def f(m): FAIL.append(m)
def w(m): WARN.append(m)
def i(m): INFO.append(m)

def client_for(username):
    c = Client()
    try:
        c.force_login(User.objects.get(username=username))
        return c
    except User.DoesNotExist:
        return None

admin_c   = client_for('admin')
coord_c   = client_for('coordinator_demo')
teacher_c = client_for('tchr_13')
student_c = client_for('std_13')
gate_c    = client_for('gate')
anon_c    = Client()

# Reference objects
T   = Teacher.objects.order_by('teacher_id').first()
S   = Student.objects.order_by('id').first()
CO  = Coordinator.objects.first()
SCH = Schedule.objects.order_by('id').first()
RM  = Classroom.objects.order_by('id').first()
CR  = Course.objects.order_by('id').first()
DEPT= Department.objects.first()
COL = College.objects.first()

def get(label, c, url, expect=(200,), check_error=True):
    try:
        r = c.get(url, follow=True)
        body = r.content.decode('utf-8', errors='replace')
        if check_error and ('Exception Type' in body or 'Traceback (most recent' in body):
            m = re.search(r'<pre class="exception_value">(.*?)</pre>', body, re.S)
            exc = (m.group(1).strip()[:90] if m else 'error page')
            f(f"{label} GET {url} → 500/error: {exc}")
            return None
        if r.status_code not in expect and r.status_code not in (200, 301, 302):
            f(f"{label} GET {url} → {r.status_code}")
            return None
        return r
    except Exception as e:
        f(f"{label} GET {url} → EXC: {str(e)[:80]}")
        return None

def post(label, c, url, data, expect_ok=True):
    try:
        r = c.post(url, data, follow=True)
        body = r.content.decode('utf-8', errors='replace')
        if 'Exception Type' in body or 'Traceback (most recent' in body:
            m = re.search(r'<pre class="exception_value">(.*?)</pre>', body, re.S)
            exc = (m.group(1).strip()[:90] if m else 'error')
            f(f"{label} POST {url} → 500: {exc}")
            return None
        if r.status_code >= 400:
            f(f"{label} POST {url} → {r.status_code}")
            return None
        p(f"{label} POST {url} → {r.status_code}")
        return r
    except Exception as e:
        f(f"{label} POST {url} → EXC: {str(e)[:80]}")
        return None

print("="*70)
print("  PHASE 1 — Every GET page renders (no 500, no template error)")
print("="*70)

ADMIN_PAGES = [
    '/admin-panel/', '/admin-panel/gate-reports/', '/notifications/',
    '/admin-panel/audit-log/', '/admin-panel/departments/', '/admin-panel/onboarding/',
    '/admin-panel/dean-evaluation/', '/admin-panel/faculty-timeline/',
    '/admin-panel/excuse-board/', '/admin-panel/exam-planner/', '/admin-panel/exam-seating/',
    '/admin-panel/exam-gate/', '/admin-panel/tickets/', '/faculty-management/',
    '/classrooms/', '/classrooms/status/', '/classrooms/add/', '/courses/', '/courses/add/',
    '/schedule/', '/schedule/add/', '/schedule/calendar/', '/reports/', '/reports/students/',
    '/reports/teachers/', '/search/', '/settings/', '/scan/', '/attendance-logs/',
    '/gate/', '/tickets/', '/tickets/create/', '/teacher/profile/',
    '/faculty-management/register-student/', '/faculty-management/register-teacher/',
    '/api/ping/',
]
ok = 0
for url in ADMIN_PAGES:
    if get('admin', admin_c, url): ok += 1
p(f"Admin pages: {ok}/{len(ADMIN_PAGES)} rendered clean")

for url in ['/professor-dashboard/', '/teacher/timeline/', '/teacher/profile/', '/attendance-logs/']:
    if get('teacher', teacher_c, url): ok += 1

for url in ['/student/dashboard/', '/student/profile/', '/student/courses/', '/student/schedule/', '/student/excuse/']:
    get('student', student_c, url)

for url in ['/coordinator/dashboard/', '/coordinator/students/', '/coordinator/faculty/',
            '/coordinator/assignments/', '/coordinator/register/', '/coordinator/grading/']:
    get('coord', coord_c, url)

print("\n" + "="*70)
print("  PHASE 2 — Every POST form with REAL data")
print("="*70)

# Add Course
if COL and DEPT:
    post('admin', admin_c, '/courses/add/', {
        'course_code': f'TEST{int(time.time())%10000}', 'title': 'Test Course Auto',
        'credits': '3', 'total_hours': '45', 'college': COL.pk, 'department': DEPT.pk,
        'year_level': '2',
    })

# Add Classroom
post('admin', admin_c, '/classrooms/add/', {
    'name': f'TestRoom{int(time.time())%10000}', 'capacity': '40',
    'location': 'Building A', 'building': 'A',
})

# Create Ticket
post('admin', admin_c, '/tickets/create/', {
    'subject': 'Auto test ticket', 'description': 'Testing ticket creation',
    'priority': 'medium', 'category': 'technical',
})

# Add Schedule (with conflict-free slot)
if T and CR and RM:
    post('admin', admin_c, '/schedule/add/', {
        'course': CR.pk, 'teacher': T.teacher_id, 'classroom': RM.pk,
        'day_of_week': 'Friday', 'start_time': '14:00', 'end_time': '15:30',
        'semester': 'Semester 1', 'batch': '2024',
    })

# Onboarding config save
post('admin', admin_c, '/admin-panel/onboarding/', {'key': 'test_key', 'value': 'test_val'})

# Email test (AJAX)
r = post('admin', admin_c, '/admin-panel/onboarding/', {
    'action': 'test_email', 'email_host': 'smtp.gmail.com', 'email_port': '587',
    'email_user': 'x@y.com', 'email_pass': 'wrong'})

print("\n" + "="*70)
print("  PHASE 3 — Dropdowns/selects have options + API endpoints")
print("="*70)

# Schedule add must have teachers, courses, rooms in dropdowns
r = admin_c.get('/schedule/add/?course_q=')
body = r.content.decode('utf-8', errors='replace')
for label, pattern in [('teacher options','teacher-sel'),('room options','room-sel'),('day options','day-sel')]:
    if pattern in body:
        p(f"Schedule/add has {label}")
    else:
        w(f"Schedule/add missing {label}")

# Faculty timeline dropdown
r = admin_c.get('/admin-panel/faculty-timeline/')
body = r.content.decode('utf-8', errors='replace')
opts = re.findall(r'<option value="(\d+)"', body)
if len(opts) >= 1:
    p(f"Faculty timeline dropdown: {len(opts)} teachers")
else:
    f("Faculty timeline dropdown EMPTY")

# API endpoints return JSON (skip /api/cameras/ — opens hardware, slow)
for url, key in [('/api/ping/','ok'),
                 ('/api/departments/', None), ('/api/student-search/?q=test', None)]:
    r = admin_c.get(url)
    try:
        d = json.loads(r.content)
        p(f"API {url} → valid JSON")
    except Exception:
        w(f"API {url} → not JSON ({r.status_code})")

# Conflict API structure
if SCH:
    r = admin_c.get(f'/api/check-conflict/?teacher_id={SCH.teacher_id}&day={SCH.day_of_week}&start={SCH.start_time}&end={SCH.end_time}')
    d = json.loads(r.content)
    if 'teacher_conflict' in d and 'room_conflict' in d:
        p("Conflict API returns teacher_conflict + room_conflict")
    else:
        f(f"Conflict API missing fields: {list(d.keys())}")

print("\n" + "="*70)
print("  PHASE 4 — Role-based security (IDOR / unauthorized access)")
print("="*70)

# Anon must redirect to login
for url in ['/admin-panel/', '/student/dashboard/', '/professor-dashboard/', '/coordinator/dashboard/']:
    r = anon_c.get(url)
    if r.status_code in (301,302) and 'login' in r.get('Location','').lower():
        p(f"Anon blocked from {url}")
    else:
        f(f"Anon reached {url} → {r.status_code}")

# Student cannot access admin
r = student_c.get('/admin-panel/', follow=False)
if r.status_code in (302,403):
    p("Student blocked from admin-panel")
else:
    f(f"SECURITY: Student reached admin-panel → {r.status_code}")

# Student cannot POST to course creation
r = student_c.post('/courses/add/', {'course_code':'HACK','title':'x'}, follow=False)
if r.status_code in (302,403):
    p("Student blocked from creating course")
else:
    w(f"Student course-add → {r.status_code}")

print("\n" + "="*70)
print("  PHASE 5 — PWA / Mobile completeness")
print("="*70)

import os.path as op
PWA_BASE = "attendance/static/pwa"
for fn in ['manifest.json', 'sw.js', 'pwa-init.js']:
    path = op.join(PWA_BASE, fn)
    if op.exists(path):
        p(f"PWA file exists: {fn}")
    else:
        f(f"PWA file MISSING: {fn}")

# manifest validity
try:
    with open(op.join(PWA_BASE,'manifest.json'), encoding='utf-8') as fh:
        man = json.load(fh)
    for key in ['name','short_name','start_url','display','icons']:
        if key in man:
            p(f"manifest.json has '{key}'")
        else:
            f(f"manifest.json MISSING '{key}'")
    if man.get('icons'):
        p(f"manifest has {len(man['icons'])} icons")
except Exception as e:
    f(f"manifest.json invalid: {e}")

# SW caches offline page + has ping-based detection
with open(op.join(PWA_BASE,'sw.js'), encoding='utf-8') as fh:
    sw = fh.read()
for feat, needle in [('offline fallback','offline'), ('cache install','install'),
                     ('fetch handler','fetch'), ('background sync','sync')]:
    if needle in sw.lower():
        p(f"SW has {feat}")
    else:
        w(f"SW missing {feat}")

# pwa-init uses server ping (not just navigator.onLine)
with open(op.join(PWA_BASE,'pwa-init.js'), encoding='utf-8') as fh:
    pwainit = fh.read()
if 'pingServer' in pwainit or '/api/ping/' in pwainit:
    p("PWA uses server-ping connectivity (emulator-safe)")
else:
    w("PWA relies on navigator.onLine only")

# Offline page route
r = anon_c.get('/offline/')
if r.status_code == 200:
    p("/offline/ page renders")
else:
    w(f"/offline/ → {r.status_code}")

# SW served at root scope
r = anon_c.get('/sw.js')
if r.status_code == 200 and 'javascript' in r.get('Content-Type',''):
    p("/sw.js served at root scope")
else:
    w(f"/sw.js → {r.status_code} {r.get('Content-Type','')}")

print("\n" + "="*70)
print("  PHASE 6 — Performance / N+1 query detection")
print("="*70)

HEAVY = [('admin','/admin-panel/'), ('admin','/courses/'), ('admin','/reports/students/'),
         ('admin','/reports/teachers/'), ('admin','/classrooms/'), ('admin','/attendance-logs/'),
         ('admin','/faculty-management/')]
for role, url in HEAVY:
    c = admin_c
    with CaptureQueriesContext(connection) as ctx:
        c.get(url)
    n = len(ctx.captured_queries)
    if n > 60:
        w(f"N+1 RISK: {url} ran {n} queries")
    elif n > 30:
        i(f"{url}: {n} queries (moderate)")
    else:
        p(f"{url}: {n} queries (good)")

print("\n" + "="*70)
print("  PHASE 7 — Template integrity (no broken {{ }} or missing vars)")
print("="*70)

# Check key pages don't show literal 'None' or broken template syntax
for role,c,url in [('admin',admin_c,'/courses/'), ('admin',admin_c,'/reports/'),
                   ('admin',admin_c,'/admin-panel/'), ('admin',admin_c,'/classrooms/')]:
    r = c.get(url)
    body = r.content.decode('utf-8', errors='replace')
    issues = []
    if '{{' in body and '}}' in body and re.search(r'\{\{\s*\w+', body):
        issues.append('unrendered {{var}}')
    if 'TemplateSyntaxError' in body:
        issues.append('TemplateSyntaxError')
    if issues:
        w(f"{url}: {', '.join(issues)}")
    else:
        p(f"{url}: template clean")

print("\n" + "="*70)
print(f"  RESULTS:  PASS={len(PASS)}  FAIL={len(FAIL)}  WARN={len(WARN)}  INFO={len(INFO)}")
print("="*70)
if FAIL:
    print("\n🔴 FAILURES:")
    for x in FAIL: print(f"   ✗ {x}")
if WARN:
    print("\n🟡 WARNINGS:")
    for x in WARN: print(f"   ⚠ {x}")
if INFO:
    print("\nℹ INFO:")
    for x in INFO: print(f"   · {x}")
print(f"\n✅ {len(PASS)} checks passed")
if '--verbose' in sys.argv or '-v' in sys.argv:
    print("\n── ALL PASSES ──")
    for x in PASS: print(f"   ✓ {x}")
