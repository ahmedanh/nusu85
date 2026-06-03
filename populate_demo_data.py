# -*- coding: utf-8 -*-
"""
SHAMEL — Comprehensive Demo Data Population Script
===================================================
• Populates ALL models with realistic Sudanese university data
• ONLINE half  → written directly to the active DB (PostgreSQL if reachable, else SQLite)
• OFFLINE half → written to edge_cache.db SQLite (simulates offline gateway scans)
• At the end   → triggers the sync task to reconcile offline → main DB

Run:  python populate_demo_data.py
"""
import os, sys, django, random, sqlite3
from datetime import datetime, timedelta, time
from pathlib import Path

os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))
os.environ['USE_LOCAL_DB'] = 'true'   # force SQLite — populate locally first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')
django.setup()

# Disable FK checks for SQLite (avoids mismatch errors from manually added columns)
from django.db import connection as _dbc
if _dbc.vendor == 'sqlite':
    _dbc.cursor().execute('PRAGMA foreign_keys=OFF;')

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from attendance.models import (
    Student, Teacher, Course, Classroom, Schedule, LectureSession,
    AIAttendanceLog, Department, College, Notification, SupportTicket,
    CameraSource, StudentFaceEmbedding, TeacherFaceEmbedding,
    AuditLog, Grade,
)

User = get_user_model()

# ─────────────────────────────────────────────────────────────────────────────
# REALISTIC SUDANESE UNIVERSITY DATA
# ─────────────────────────────────────────────────────────────────────────────

COLLEGES = [
    ('كلية الطب البشري',        'Medicine',       'MED'),
    ('كلية الحاسوب والمعلومات', 'Computer Science','CSI'),
    ('كلية الهندسة',             'Engineering',    'ENG'),
    ('كلية الصيدلة',             'Pharmacy',       'PHA'),
    ('كلية التمريض',             'Nursing',        'NUR'),
    ('كلية الأشعة والتصوير',    'Radiology',      'RAD'),
]

DEPARTMENTS_BY_COLLEGE = {
    'MED': ['الباثولوجيا', 'الباطنية', 'الجراحة', 'طب الأطفال', 'النساء والتوليد'],
    'CSI': ['هندسة البرمجيات', 'الذكاء الاصطناعي', 'قواعد البيانات', 'الشبكات'],
    'ENG': ['الهندسة الكهربائية', 'الهندسة المدنية', 'الميكانيكا'],
    'PHA': ['الصيدلة الإكلينيكية', 'الكيمياء الصيدلانية'],
    'NUR': ['تمريض داخلي', 'تمريض جراحي'],
    'RAD': ['أشعة تشخيصية', 'أشعة علاجية'],
}

STUDENT_NAMES = [
    'أحمد محمد عبدالله', 'فاطمة عمر الحسن', 'خالد إبراهيم النور',
    'مريم يوسف عثمان', 'عمر علي محمد', 'زينب عبدالرحمن سالم',
    'محمد الطاهر أحمد', 'هند بشير موسى', 'يوسف حمزة إدريس',
    'سارة وليد حسين', 'عبدالله مصطفى النيل', 'نور الدين أحمد',
    'آمنة عبدالعزيز حمد', 'إبراهيم سليمان عمر', 'ليلى محمود علي',
    'طارق حسن عبدالله', 'رهف يحيى إبراهيم', 'أسامة صالح بكر',
    'داليا عبدالمجيد النور', 'حسام الدين محمد سعيد',
    'ولاء عمر الشيخ', 'محمد عبدالله الرشيد', 'أميرة صلاح الدين',
    'قاسم إبراهيم حمدان', 'سلمى خالد الفاضل', 'عدنان موسى عبدالله',
    'حنان عثمان إدريس', 'ياسر علي الحسين', 'رغد محمد الأمين',
    'كريم عبدالله وداعة', 'نجوى سالم بابكر', 'تميم أحمد الزين',
    'شيماء عبدالرحمن دفع', 'فيصل محمد النعيم', 'عزة خالد حمدون',
    'منصور إبراهيم سبيل', 'رنا عمر التجاني', 'صلاح الدين أحمد',
    'إيمان حسن الباشا', 'بشرى عبدالله حليمة',
]

TEACHER_NAMES = [
    'د. عصام الدين محمد', 'د. نجاة عبدالرحيم', 'د. طاهر الزبير',
    'أ.د. سمير الحسن', 'د. فوزية عثمان', 'د. خالد البشير',
    'أ.د. رانيا النيل', 'د. عمر الفاروق', 'د. هند الريح',
    'د. صديق محمد بشير', 'أ.د. لميس عبدالله', 'د. حيدر علي',
]

COURSE_NAMES = {
    'CSI': [
        ('CS101', 'مقدمة في علم الحاسوب'),
        ('CS201', 'هياكل البيانات والخوارزميات'),
        ('CS301', 'قواعد البيانات المتقدمة'),
        ('CS401', 'الذكاء الاصطناعي وتعلم الآلة'),
        ('CS302', 'أمن المعلومات والشبكات'),
        ('CS402', 'تطوير تطبيقات الويب'),
    ],
    'MED': [
        ('MED101', 'التشريح البشري'),
        ('MED201', 'فسيولوجيا الجسم'),
        ('MED301', 'الباثولوجيا العامة'),
        ('MED401', 'الباطنية الإكلينيكية'),
    ],
    'ENG': [
        ('ENG101', 'الرياضيات الهندسية'),
        ('ENG201', 'الدوائر الكهربائية'),
        ('ENG301', 'الميكانيكا التطبيقية'),
    ],
}

DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']

TICKET_SUBJECTS = [
    'مشكلة في تسجيل الحضور', 'خطأ في جدول المحاضرات',
    'عدم ظهور الدرجات', 'مشكلة في بصمة الوجه',
    'طلب إعادة جلسة محاضرة', 'إشكالية في الكاميرا',
]

TICKET_BODIES = [
    'لاحظت أن حضوري لم يُسجَّل في محاضرة اليوم رغم حضوري الفعلي',
    'الجدول يُظهر محاضرة في قاعة مشغولة بالفعل',
    'درجات الامتحان النهائي لم تظهر في صفحتي',
    'الكاميرا لم تتعرف على وجهي رغم التسجيل المسبق',
    'طلب إعادة جلسة بسبب انقطاع الكهرباء',
    'الكاميرا في القاعة ٣ لا تعمل بشكل صحيح',
]

EXCUSE_REASONS = [
    'مرض موثَّق بشهادة طبية', 'وفاة في العائلة',
    'ظروف طارئة خارج السيطرة', 'حادث سير',
]


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

def rnd_time(h_start, h_end):
    h = random.randint(h_start, h_end - 1)
    m = random.choice([0, 15, 30, 45])
    return time(h, m)

def rnd_past(days=30):
    return timezone.now() - timedelta(
        days=random.randint(0, days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

print('='*60)
print('SHAMEL Demo Data Population')
print('='*60)

# ─────────────────────────────────────────────────────────────────────────────
# 1. COLLEGES & DEPARTMENTS
# ─────────────────────────────────────────────────────────────────────────────
print('\n[1/10] Colleges & Departments...')
college_objs = {}
for name_ar, name_en, code in COLLEGES:
    c, _ = College.objects.get_or_create(
        college_name=name_ar,
        defaults={}
    )
    college_objs[code] = c

dept_objs = {}
for code, depts in DEPARTMENTS_BY_COLLEGE.items():
    college = college_objs[code]
    for dept_name in depts:
        d, _ = Department.objects.get_or_create(
            name=dept_name,
            defaults={'college': college}
        )
        dept_objs[dept_name] = d

print(f'   Colleges: {College.objects.count()} | Depts: {Department.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 2. TEACHERS (12 teachers)
# ─────────────────────────────────────────────────────────────────────────────
print('\n[2/10] Teachers...')
teacher_objs = []
college_codes = list(college_objs.keys())
for i, name in enumerate(TEACHER_NAMES):
    username = f'tchr_demo_{i+1}'
    email = f'teacher{i+1}@shamel.edu.sd'
    u, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    u.set_password('Teacher@2026')
    u.save()
    college = college_objs[college_codes[i % len(college_codes)]]
    t, _ = Teacher.objects.get_or_create(
        auth_user=u,
        defaults={
            'name': name,
            'college': college,
            'university_email': email,
            'is_allowed_entry': True,
        }
    )
    teacher_objs.append(t)

print(f'   Teachers: {Teacher.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 3. STUDENTS (40 students)
# ─────────────────────────────────────────────────────────────────────────────
print('\n[3/10] Students...')
student_objs = []
for i, name in enumerate(STUDENT_NAMES):
    username = f'std_demo_{i+1}'
    email = f'student{i+1}@student.shamel.edu.sd'
    year = random.randint(1, 5)
    college = college_objs[random.choice(college_codes)]
    u, _ = User.objects.get_or_create(username=username, defaults={'email': email})
    u.set_password('Student@2026')
    u.save()
    dept = random.choice(list(dept_objs.values()))
    s, _ = Student.objects.get_or_create(
        auth_user=u,
        defaults={
            'name': name,
            'student_code': f'SU{2020+year}{str(i+1).zfill(4)}',
            'university_email': email,
            'department': dept,
            'batch': str(2020 + year),
            'is_allowed_entry': True,
            'is_registered': True,
        }
    )
    student_objs.append(s)

print(f'   Students: {Student.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 4. COURSES
# ─────────────────────────────────────────────────────────────────────────────
print('\n[4/10] Courses...')
course_objs = []
for col_code, courses in COURSE_NAMES.items():
    college = college_objs[col_code]
    for code, title in courses:
        c, _ = Course.objects.get_or_create(
            course_code=code,
            defaults={
                'title': title,
                'college': college_objs[col_code],
                'credits': random.choice([2, 3, 4]),
            }
        )
        course_objs.append(c)

print(f'   Courses: {Course.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 5. CLASSROOMS
# ─────────────────────────────────────────────────────────────────────────────
print('\n[5/10] Classrooms...')
classroom_data = [
    ('QA-101', 'قاعة أ-١٠١', 60),  ('QA-102', 'قاعة أ-١٠٢', 80),
    ('QB-201', 'قاعة ب-٢٠١', 120), ('QB-202', 'قاعة ب-٢٠٢', 100),
    ('LAB-1',  'مختبر الحاسوب ١', 40), ('LAB-2', 'مختبر الحاسوب ٢', 40),
    ('AMP-1',  'القاعة الكبرى', 300), ('CONF-1', 'قاعة المؤتمرات', 50),
]
classroom_objs = []
for code, name, cap in classroom_data:
    room, _ = Classroom.objects.get_or_create(
        name=code,
        defaults={
            'capacity': cap,
            'is_busy': False,
        }
    )
    classroom_objs.append(room)

print(f'   Classrooms: {Classroom.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 6. SCHEDULES
# ─────────────────────────────────────────────────────────────────────────────
print('\n[6/10] Schedules...')
schedule_objs = []
for i, course in enumerate(course_objs[:10]):
    teacher = teacher_objs[i % len(teacher_objs)]
    room = classroom_objs[i % len(classroom_objs)]
    day = DAYS[i % len(DAYS)]
    h_start = 8 + (i % 6) * 2
    start = time(h_start, 0)
    end = time(h_start + 1, 30)
    s, _ = Schedule.objects.get_or_create(
        course=course,
        teacher=teacher,
        classroom=room,
        day_of_week=day,
        defaults={'start_time': start, 'end_time': end}
    )
    schedule_objs.append(s)

print(f'   Schedules: {Schedule.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 7. CAMERA SOURCES
# ─────────────────────────────────────────────────────────────────────────────
print('\n[7/10] Camera Sources...')
cameras = [
    ('بوابة الدخول الرئيسية', '0', 'Main Gate', True),
    ('قاعة أ-١٠١', '1', 'Hall A-101', False),
    ('قاعة ب-٢٠١', '2', 'Hall B-201', False),
    ('مختبر الحاسوب', '3', 'Computer Lab', False),
]
for cname, src, loc, is_gate in cameras:
    CameraSource.objects.get_or_create(
        name=cname,
        defaults={'source': src, 'location': loc, 'is_active': True,
                  'is_gate': is_gate if hasattr(CameraSource, 'is_gate') else False}
    )
print(f'   Cameras: {CameraSource.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 8. ONLINE HALF — Lecture Sessions + Attendance Logs (direct to DB)
# ─────────────────────────────────────────────────────────────────────────────
print('\n[8/10] ONLINE: LectureSessions + AttendanceLogs...')
online_sessions = []
with transaction.atomic():
    for i, sched in enumerate(schedule_objs[:6]):  # first 6 = online half
        days_ago = random.randint(1, 15)
        start_dt = timezone.now() - timedelta(days=days_ago, hours=random.randint(1, 8))
        end_dt = start_dt + timedelta(minutes=90)
        session, _ = LectureSession.objects.get_or_create(
            schedule=sched,
            actual_start_time=start_dt,
            defaults={
                'actual_end_time': end_dt,
                'is_active': False,
                'duration_minutes': 90,
            }
        )
        online_sessions.append(session)

        # Attendance logs for 70-95% of students
        attending = random.sample(student_objs, k=int(len(student_objs) * random.uniform(0.7, 0.95)))
        for student in attending:
            status = random.choices(
                ['Present', 'Late', 'Absent'],
                weights=[75, 15, 10]
            )[0]
            confidence = round(random.uniform(0.78, 0.99), 3) if status != 'Absent' else round(random.uniform(0.3, 0.6), 3)
            AIAttendanceLog.objects.get_or_create(
                student=student,
                schedule=sched,
                timestamp=start_dt + timedelta(minutes=random.randint(0, 20)),
                defaults={
                    'status': status,
                    'confidence_score': confidence,
                    'method': 'face',
                    'session': session,
                }
            )

print(f'   Sessions (online): {len(online_sessions)} | Logs: {AIAttendanceLog.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# 9. OFFLINE HALF — Written to edge_cache.db SQLite
# ─────────────────────────────────────────────────────────────────────────────
print('\n[9/10] OFFLINE: Writing to edge_cache.db...')
cache_path = Path(__file__).parent / 'edge_cache.db'
conn = sqlite3.connect(str(cache_path))
conn.execute('''
    CREATE TABLE IF NOT EXISTS offline_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT NOT NULL,
        schedule_id  INTEGER NOT NULL,
        confidence   REAL    DEFAULT 0.85,
        status       TEXT    DEFAULT 'Present',
        timestamp    TEXT    NOT NULL,
        synced       INTEGER DEFAULT 0
    )
''')
conn.commit()

offline_sessions = schedule_objs[6:]  # last 4 = offline half
offline_log_count = 0
for sched in offline_sessions:
    days_ago = random.randint(0, 3)
    ts_base = (timezone.now() - timedelta(days=days_ago, hours=random.randint(1, 6))).isoformat()
    # Pick a random subset of students
    attending = random.sample(student_objs, k=int(len(student_objs) * random.uniform(0.6, 0.9)))
    for student in attending:
        status = random.choices(['Present', 'Late', 'Absent'], weights=[70, 20, 10])[0]
        confidence = round(random.uniform(0.72, 0.97), 3)
        ts = (timezone.now() - timedelta(
            days=days_ago,
            minutes=random.randint(0, 30)
        )).isoformat()
        conn.execute(
            'INSERT INTO offline_attendance (student_name, schedule_id, confidence, status, timestamp, synced) VALUES (?,?,?,?,?,?)',
            (student.name, sched.pk, confidence, status, ts, 0)
        )
        offline_log_count += 1

# Add some anomalies: low-confidence rejections, duplicate scans
for _ in range(5):
    student = random.choice(student_objs)
    sched = random.choice(offline_sessions) if offline_sessions else schedule_objs[0]
    conn.execute(
        'INSERT INTO offline_attendance (student_name, schedule_id, confidence, status, timestamp, synced) VALUES (?,?,?,?,?,?)',
        (student.name, sched.pk, round(random.uniform(0.3, 0.55), 3), 'Rejected', timezone.now().isoformat(), 0)
    )
    offline_log_count += 1

conn.commit()
conn.close()
print(f'   Offline records written: {offline_log_count} (synced=0)')

# ─────────────────────────────────────────────────────────────────────────────
# 10. SUPPORT TICKETS, NOTIFICATIONS, GRADES, AUDIT LOGS
# ─────────────────────────────────────────────────────────────────────────────
print('\n[10/10] Tickets, Notifications, Grades, Audit...')
admin_user = User.objects.filter(is_superuser=True).first()

# Tickets
with transaction.atomic():
    for i in range(12):
        student = random.choice(student_objs)
        user = student.auth_user or admin_user
        SupportTicket.objects.get_or_create(
            subject=TICKET_SUBJECTS[i % len(TICKET_SUBJECTS)],
            user=user,
            defaults={
                'body': TICKET_BODIES[i % len(TICKET_BODIES)],
                'status': random.choice(['open', 'open', 'in_progress', 'resolved']),
                'priority': random.choice(['low', 'medium', 'high']),
            }
        )

# Notifications
for u in User.objects.all()[:20]:
    for msg in [
        f'تم تسجيل حضورك بنجاح — {random.choice(course_objs).title if course_objs else "المادة"}',
        'تذكير: نسبة الحضور أدنى من 75% في مادة واحدة',
        'تم رفع جدول محاضرات الأسبوع القادم',
    ]:
        Notification.objects.get_or_create(
            user=u,
            body=msg,
            defaults={
                'title': msg[:50],
                'level': random.choice(['info', 'warning', 'error', 'success']),
                'is_read': random.choice([True, False]),
            }
        )

# Grades
with transaction.atomic():
    for course in course_objs[:6]:
        for student in random.sample(student_objs, k=min(15, len(student_objs))):
            Grade.objects.get_or_create(
                student=student,
                course=course,
                defaults={
                    'score': round(random.uniform(45, 100), 1),
                    'semester': random.choice(['S1-2025', 'S2-2025', 'S1-2026']),
                }
            )

# Audit logs
for _ in range(20):
    AuditLog.objects.create(
        user=admin_user,
        action=random.choice(['LOGIN', 'SCAN', 'EXPORT', 'UPDATE', 'CREATE']),
        target_model=random.choice(['Student', 'Schedule', 'Course', 'Classroom']),
        target_id=random.randint(1, 100),
        description=f'Demo audit entry #{random.randint(1000,9999)}',
        timestamp=rnd_past(10),
    )

print(f'   Tickets: {SupportTicket.objects.count()}')
print(f'   Notifications: {Notification.objects.count()}')
print(f'   Grades: {Grade.objects.count()}')

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('POPULATION COMPLETE')
print('='*60)
print(f'  Students       : {Student.objects.count()}')
print(f'  Teachers       : {Teacher.objects.count()}')
print(f'  Courses        : {Course.objects.count()}')
print(f'  Classrooms     : {Classroom.objects.count()}')
print(f'  Schedules      : {Schedule.objects.count()}')
print(f'  LectureSessions: {LectureSession.objects.count()}')
print(f'  AttendanceLogs : {AIAttendanceLog.objects.count()}  ← ONLINE half')
print(f'  Offline cache  : {offline_log_count} records  ← OFFLINE half (unsynced)')
print(f'  Tickets        : {SupportTicket.objects.count()}')
print(f'  Notifications  : {Notification.objects.count()}')
print(f'  Grades         : {Grade.objects.count()}')
print()
print('Next: run sync_test.py to flush offline → main DB')
print('='*60)
