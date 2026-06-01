# -*- coding: utf-8 -*-
"""
SHAMEL A→Z E2E test pipeline.
Introspects urlpatterns and exercises EVERY route across all roles, plus
exports (PDF/CSV/Excel for 500s), PWA files, conflict-check, and the full
api/v1 surface with token auth + status-code assertions.
"""
import os, sys, django, re, json, threading, time, io, urllib.request
os.environ['USE_LOCAL_DB'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.chdir("D:/مهم/ACDC_FINAL-main")
sys.path.insert(0, "D:/مهم/ACDC_FINAL-main")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
django.setup()

from django.conf import settings
for h in ('testserver',):
    if h not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append(h)

from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.contrib.auth import get_user_model
from attendance import urls as appurls
from attendance.models import (Student, Teacher, Coordinator, Schedule, Classroom,
    Course, SupportTicket, LectureSession)
from axes.models import AccessAttempt
User = get_user_model()
AccessAttempt.objects.all().delete()

PASS, FAIL, WARN = [], [], []
def p(m): PASS.append(m)
def f(m): FAIL.append(m)
def w(m): WARN.append(m)

def cl(username):
    c = Client()
    try:
        c.force_login(User.objects.get(username=username))
        return c
    except User.DoesNotExist:
        return None

admin = cl('admin'); coord = cl('coordinator_demo')
teacher = cl('tchr_13'); student = cl('std_13'); gate = cl('gate')
anon = Client()

# Real IDs for parametric routes
T = Teacher.objects.order_by('teacher_id').first()
S = Student.objects.order_by('id').first()
SC = Schedule.objects.order_by('id').first()
RM = Classroom.objects.order_by('id').first()
CR = Course.objects.order_by('id').first()
TK = SupportTicket.objects.order_by('id').first()
SE = LectureSession.objects.order_by('id').first()

PARAM = {
    'teacher_id': T.teacher_id if T else 1,
    'student_id': S.id if S else 1,
    'schedule_id': SC.id if SC else 1,
    'classroom_id': RM.id if RM else 1,
    'course_id': CR.id if CR else 1,
    'ticket_id': TK.id if TK else 1,
    'session_id': SE.id if SE else 1,
    'person_type': 'student', 'person_id': S.id if S else 1,
    'user_type': 'student', 'user_id': S.id if S else 1,
}

def body_err(body):
    if 'Exception Type' in body or 'Traceback (most recent' in body:
        m = re.search(r'<pre class="exception_value">(.*?)</pre>', body, re.S)
        return (m.group(1).strip()[:100] if m else 'error-page')
    return None

def hit(label, c, path, expect_ok=(200, 301, 302), method='GET', data=None):
    try:
        r = c.post(path, data or {}, follow=True) if method == 'POST' else c.get(path, follow=True)
        body = r.content.decode('utf-8', errors='replace')
        e = body_err(body)
        if e:
            f(f"[{label}] {method} {path} → 500: {e}")
            return None
        if r.status_code >= 500:
            f(f"[{label}] {method} {path} → {r.status_code}")
            return None
        return r
    except Exception as ex:
        f(f"[{label}] {method} {path} → EXC: {str(ex)[:90]}")
        return None

# ════════════════════════════════════════════════════════════════════════
print("="*72)
print("  STEP 1 — Introspect urlpatterns; GET every reachable route (admin)")
print("="*72)
get_routes, param_routes, skipped = [], [], []
for pat in appurls.urlpatterns:
    try:
        route = str(pat.pattern)
    except Exception:
        continue
    name = pat.name or ''
    # skip API (tested in step 2), pure-POST-ish, and stream/export handled separately
    if route.startswith('api/v1/'):
        continue
    if '<' in route:
        # fill params
        filled = route
        for key, val in PARAM.items():
            filled = filled.replace(f'<int:{key}>', str(val)).replace(f'<str:{key}>', str(val))
        filled = re.sub(r'<[^>]+>', '1', filled)
        param_routes.append('/' + filled)
    else:
        get_routes.append('/' + route)

okc = 0
for path in get_routes:
    # exports/stream tested separately
    if 'export' in path or 'video_feed' in path or 'logout' in path:
        continue
    if hit('admin', admin, path):
        okc += 1
p(f"Admin plain GET routes: {okc} clean (of {len([x for x in get_routes if 'export' not in x and 'video_feed' not in x and 'logout' not in x])})")

okp = 0
for path in param_routes:
    if 'delete' in path or 'export' in path or 'logout' in path or 'toggle' in path:
        continue
    if hit('admin', admin, path):
        okp += 1
p(f"Admin parametric GET routes: {okp} clean (of {len([x for x in param_routes if 'delete' not in x and 'export' not in x and 'logout' not in x and 'toggle' not in x])})")

print("\n" + "="*72)
print("  STEP 1b — Role dashboards (teacher/student/coordinator/gate)")
print("="*72)
ROLE_ROUTES = {
    'teacher': (teacher, ['/professor-dashboard/', '/teacher/timeline/', '/teacher/profile/',
                          '/teacher/attendance-records/', '/attendance-logs/', '/notifications/', '/tickets/']),
    'student': (student, ['/student/dashboard/', '/student/profile/', '/student/courses/',
                          '/student/schedule/', '/student/excuse/', '/student/support/', '/notifications/']),
    'coordinator': (coord, ['/coordinator/dashboard/', '/coordinator/students/', '/coordinator/faculty/',
                            '/coordinator/assignments/', '/coordinator/register/', '/coordinator/grading/']),
    'gate': (gate, ['/gate/']),
}
for role, (c, paths) in ROLE_ROUTES.items():
    rok = sum(1 for path in paths if hit(role, c, path))
    p(f"{role}: {rok}/{len(paths)} dashboards clean")

print("\n" + "="*72)
print("  STEP 1c — Exports (PDF/CSV/Excel) must not 500")
print("="*72)
EXPORTS = [
    '/reports/students/export/csv/', '/reports/students/export/excel/',
    '/reports/students/export/pdf/', '/reports/teachers/export/csv/',
    '/reports/teachers/export/pdf/', '/reports/grades/export/pdf/',
    '/reports/analytics/export/pdf/', '/export/teachers/',
]
for path in EXPORTS:
    r = admin.get(path, follow=True)
    if r.status_code == 200:
        ct = r.get('Content-Type', '')
        size = len(r.content)
        p(f"export {path} → 200 {ct.split(';')[0]} {size}B")
    elif r.status_code in (301, 302):
        p(f"export {path} → redirect")
    else:
        body = r.content.decode('utf-8', errors='replace')
        e = body_err(body) or f"status {r.status_code}"
        f(f"export {path} → {e}")

print("\n" + "="*72)
print("  STEP 1d — Conflict check + PWA")
print("="*72)
if SC:
    r = admin.get(f'/api/check-conflict/?teacher_id={SC.teacher_id}&day={SC.day_of_week}&start={SC.start_time}&end={SC.end_time}')
    try:
        d = json.loads(r.content)
        if 'teacher_conflict' in d and 'room_conflict' in d:
            p("conflict-check returns teacher_conflict + room_conflict")
        else:
            f(f"conflict-check missing fields: {list(d.keys())}")
    except Exception:
        f("conflict-check not JSON")

for path, ctype in [('/sw.js', 'javascript'), ('/manifest.json', 'json'), ('/offline/', '')]:
    r = anon.get(path)
    if r.status_code == 200:
        p(f"PWA {path} → 200 {r.get('Content-Type','').split(';')[0]}")
    else:
        f(f"PWA {path} → {r.status_code}")

print("\n" + "="*72)
print("  STEP 2 — REST API /api/v1 (token auth + status codes)")
print("="*72)
BASE = 'http://127.0.0.1:9000'
def api(path, token=None, method='GET', payload=None):
    url = BASE + path
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        r = urllib.request.urlopen(req, timeout=15)
        return r.getcode(), json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read())
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {'err': str(e)[:60]}

# health (no auth) → 200
code, _ = api('/api/v1/health')
p("api health 200") if code == 200 else f(f"api health {code}")
# login bad → 401
code, _ = api('/api/v1/auth/login', method='POST', payload={'username':'admin','password':'WRONG'})
p("api login bad → 401") if code == 401 else f(f"api login bad → {code}")
# login good → 200 + token
code, d = api('/api/v1/auth/login', method='POST', payload={'username':'admin','password':'Admin@1234'})
token = d.get('token')
p("api login good → 200 + token") if code == 200 and token else f(f"api login good → {code}")
# protected without token → 401
code, _ = api('/api/v1/dashboard')
p("api dashboard no-token → 401") if code == 401 else f(f"api dashboard no-token → {code}")
# staff-only as student → 403
_, sd = api('/api/v1/auth/login', method='POST', payload={'username':'std_13','password':'Student@1234'})
stoken = sd.get('token')
if stoken:
    code, _ = api('/api/v1/audit-log', token=stoken)
    p("api audit-log as student → 403") if code == 403 else w(f"api audit-log as student → {code}")
# all read endpoints with admin token → 200
API_GET = ['/api/v1/me','/api/v1/dashboard','/api/v1/schedule','/api/v1/reports/summary',
    '/api/v1/notifications','/api/v1/courses','/api/v1/classrooms','/api/v1/classrooms/status',
    '/api/v1/departments','/api/v1/teachers','/api/v1/students','/api/v1/tickets',
    '/api/v1/attendance-logs','/api/v1/gate-logs','/api/v1/audit-log','/api/v1/exams',
    '/api/v1/search?q=ahmed','/api/v1/settings','/api/v1/coordinator/students',
    f'/api/v1/teachers/{PARAM["teacher_id"]}', f'/api/v1/students/{PARAM["student_id"]}']
gok = 0
for path in API_GET:
    code, d = api(path, token=token)
    if code == 200 and d.get('ok'):
        gok += 1
    else:
        f(f"api {path} → {code}")
p(f"api read endpoints: {gok}/{len(API_GET)} → 200")

print("\n" + "="*72)
print("  STEP 2b — Concurrency (100 parallel API requests)")
print("="*72)
res = {'ok': 0, 'err': 0}
lock = threading.Lock()
paths = ['/api/v1/dashboard','/api/v1/courses','/api/v1/students','/api/v1/teachers','/api/v1/reports/summary']
def worker(pth):
    code, _ = api(pth, token=token)
    with lock:
        if code == 200: res['ok'] += 1
        else: res['err'] += 1
t0 = time.time()
ths = [threading.Thread(target=worker, args=(paths[i % len(paths)],)) for i in range(100)]
for t in ths: t.start()
for t in ths: t.join()
dt = time.time() - t0
if res['err'] == 0:
    p(f"concurrency 100 reqs → 0 errors, {100/dt:.0f} req/s")
else:
    f(f"concurrency: {res['err']} errors / 100")

print("\n" + "="*72)
print(f"  RESULTS:  PASS={len(PASS)}  FAIL={len(FAIL)}  WARN={len(WARN)}")
print("="*72)
if FAIL:
    print("\n🔴 FAILURES:")
    for x in FAIL: print(f"   ✗ {x}")
if WARN:
    print("\n🟡 WARN:")
    for x in WARN: print(f"   ⚠ {x}")
print("\nSUMMARY:")
for x in PASS: print(f"   ✓ {x}")
