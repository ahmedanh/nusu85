# -*- coding: utf-8 -*-
"""
SHAMEL — Targeted Seed for Documentation Accounts
Run:  python seed_target_accounts.py
"""
import os, sys, random, django
from pathlib import Path
from datetime import timedelta, time as dtime

os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))
# os.environ['USE_LOCAL_DB'] = 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')
django.setup()

# Fix psycopg2 database-level drift for is_occupied on remote VPS
from django.db import connection as _conn
if _conn.vendor == 'postgresql':
    with _conn.cursor() as cur:
        # Create missing tables if they don't exist
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance_medicalexcuse (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES attendance_student(id) ON DELETE CASCADE,
                    schedule_id INTEGER REFERENCES attendance_schedule(id) ON DELETE SET NULL,
                    reason TEXT NOT NULL,
                    document VARCHAR(100),
                    status VARCHAR(10) NOT NULL DEFAULT 'pending',
                    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    reviewed_by_id INTEGER REFERENCES auth_user(id) ON DELETE SET NULL,
                    review_note TEXT NOT NULL DEFAULT ''
                );
            """)
        except Exception:
            pass

        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS attendance_exam (
                    id SERIAL PRIMARY KEY,
                    course_id INTEGER NOT NULL REFERENCES attendance_course(id) ON DELETE CASCADE,
                    exam_type VARCHAR(50) NOT NULL DEFAULT 'Final',
                    date DATE NOT NULL,
                    start_time TIME NOT NULL,
                    end_time TIME NOT NULL,
                    classroom_id INTEGER REFERENCES attendance_classroom(id) ON DELETE SET NULL,
                    semester VARCHAR(10) NOT NULL DEFAULT '',
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
        except Exception:
            pass

        for query in [
            "ALTER TABLE attendance_classroom ALTER COLUMN is_occupied DROP NOT NULL",
            "ALTER TABLE attendance_camerasource ALTER COLUMN created_at DROP NOT NULL",
            "ALTER TABLE attendance_department ALTER COLUMN created_at DROP NOT NULL",
            "ALTER TABLE attendance_course ALTER COLUMN year_level DROP NOT NULL",
            "ALTER TABLE attendance_grade ALTER COLUMN entered_at DROP NOT NULL",
            "ALTER TABLE attendance_notification ALTER COLUMN message DROP NOT NULL"
        ]:
            try:
                cur.execute(query)
            except Exception:
                pass
        # Reset PK sequences for Postgres tables
        try:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND (table_name LIKE 'attendance_%' OR table_name LIKE 'auth_%')
            """)
            tables = [row[0] for row in cur.fetchall()]
            for table in tables:
                try:
                    cur.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table}")
                except Exception:
                    pass
        except Exception:
            pass

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction, connection

from attendance.models import (
    Student, Teacher, Course, Classroom, Schedule, LectureSession,
    AIAttendanceLog, Department, College, Notification, SupportTicket,
    AuditLog, Grade, MedicalExcuse, GateLog, Coordinator, Enrollment,
)

User = get_user_model()

def p(msg): print(f'  [OK] {msg}')

def rnd_past(days=30):
    return timezone.now() - timedelta(
        days=random.randint(1, days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

# ─── 1. COLLEGE + DEPARTMENT ──────────────────────────────────────────────────
print('\n[1/9] College & Department...')
college, _ = College.objects.get_or_create(
    college_name='كلية الحاسوب والمعلومات',
    defaults={'name': 'كلية الحاسوب والمعلومات'}
)
dept, _ = Department.objects.get_or_create(
    name='هندسة البرمجيات',
    defaults={'college': college}
)
if not dept.college_id:
    dept.college = college; dept.save()
p(f'College: {college.college_name} | Dept: {dept.name}')

# ─── 2. ADMIN ─────────────────────────────────────────────────────────────────
print('\n[2/9] Admin...')
admin_u, _ = User.objects.get_or_create(username='admin', defaults={
    'email': 'admin@shamel.sd', 'first_name': 'مدير', 'last_name': 'النظام',
    'is_staff': True, 'is_superuser': True,
})
admin_u.set_password('Admin@2026')
admin_u.is_staff = True; admin_u.is_superuser = True; admin_u.save()
p('admin / Admin@2026')

# ─── 3. COORDINATOR ──────────────────────────────────────────────────────────
print('\n[3/9] Coordinator...')
coord_u, _ = User.objects.get_or_create(username='coordinator', defaults={
    'email': 'coord@shamel.sd', 'first_name': 'منسق', 'last_name': 'الكلية',
})
coord_u.set_password('Coord@2026'); coord_u.save()
coord_obj, _ = Coordinator.objects.get_or_create(
    auth_user=coord_u,
    defaults={'name': 'أ. منسق الكلية', 'college': college, 'university_email': 'coord@shamel.sd'}
)
if not coord_obj.college_id:
    coord_obj.college = college; coord_obj.save()
p('coordinator / Coord@2026')

# ─── 4. GATE ─────────────────────────────────────────────────────────────────
print('\n[4/9] Gate...')
gate_u, _ = User.objects.get_or_create(username='gate', defaults={
    'email': 'gate@shamel.sd', 'first_name': 'حارس', 'last_name': 'البوابة',
})
gate_u.set_password('Gate@2026'); gate_u.save()
p('gate / Gate@2026')

# ─── 5. TEACHER tch_13 ───────────────────────────────────────────────────────
print('\n[5/9] Teacher tch_13...')
tch_u, _ = User.objects.get_or_create(username='tch_13', defaults={
    'email': 'teacher13@shamel.sd', 'first_name': 'أحمد', 'last_name': 'الطاهر',
})
tch_u.set_password('Tch@2026'); tch_u.save()
teacher, _ = Teacher.objects.get_or_create(
    auth_user=tch_u,
    defaults={
        'name': 'د. أحمد الطاهر محمد',
        'university_email': 'teacher13@shamel.sd',
        'department': dept,
        'college': college,
        'academic_degree': 'PhD',
        'major': 'هندسة البرمجيات',
        'is_allowed_entry': True,
    }
)
if not teacher.department_id: teacher.department = dept; teacher.save()
if not teacher.college_id:    teacher.college = college; teacher.save()
p('tch_13 / Tch@2026')

# ─── 6. STUDENT std_13 ───────────────────────────────────────────────────────
print('\n[6/9] Student std_13...')
std_u, _ = User.objects.get_or_create(username='std_13', defaults={
    'email': 'student13@shamel.sd', 'first_name': 'خالد', 'last_name': 'إبراهيم',
})
std_u.set_password('Std@2026'); std_u.save()
student, _ = Student.objects.get_or_create(
    student_code='CS-2023-013',
    defaults={
        'auth_user': std_u,
        'name': 'خالد إبراهيم النور',
        'university_email': 'student13@shamel.sd',
        'department': dept,
        'batch': '2023',
        'is_registered': True,
        'is_allowed_entry': True,
    }
)
if student.auth_user_id != std_u.pk:
    student.auth_user = std_u; student.save()
if not student.department_id:
    student.department = dept; student.save()
p('std_13 / Std@2026')

# ─── 7. COURSES + CLASSROOMS + SCHEDULES + SESSIONS + ATTENDANCE ──────────────
print('\n[7/9] Courses, Schedules, Sessions, Attendance...')

COURSES_DATA = [
    ('هندسة البرمجيات',         'CS301', 3),
    ('قواعد البيانات المتقدمة', 'CS302', 3),
    ('الذكاء الاصطناعي',        'CS401', 3),
    ('أمن المعلومات',           'CS402', 2),
    ('تطوير تطبيقات الويب',     'CS303', 3),
    ('الشبكات الحاسوبية',       'CS304', 2),
]
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
TIMES = [
    (dtime(8, 0),  dtime(9, 30)),
    (dtime(9, 30), dtime(11, 0)),
    (dtime(11, 0), dtime(12, 30)),
    (dtime(13, 0), dtime(14, 30)),
    (dtime(14, 30),dtime(16, 0)),
    (dtime(16, 0), dtime(17, 30)),
]
ATTENDANCE_WEIGHTS = ['Present'] * 7 + ['Late'] * 2 + ['Absent']

course_objs, schedule_objs = [], []

with transaction.atomic():
    for i, (title, code, credits) in enumerate(COURSES_DATA):
        course, _ = Course.objects.get_or_create(
            course_code=code,
            defaults={
                'title': title, 'credits': credits, 'total_hours': credits * 16,
                'department': dept, 'college': college, 'year_level': 3,
            }
        )
        course_objs.append(course)

        room, _ = Classroom.objects.get_or_create(
            name=f'قاعة {100 + i + 1}',
            defaults={
                'capacity': 60,
                'location': f'المبنى الرئيسي — الطابق {(i % 3) + 1}',
                'classroom_type': 'Lecture',
                'college': college,
            }
        )

        # Enroll student (needs classroom)
        Enrollment.objects.get_or_create(
            student=student, course=course,
            defaults={'semester': 'S1-2026', 'classroom': room}
        )

        sched, _ = Schedule.objects.get_or_create(
            course=course, teacher=teacher, classroom=room,
            day_of_week=DAYS[i % len(DAYS)],
            start_time=TIMES[i % len(TIMES)][0],
            end_time=TIMES[i % len(TIMES)][1],
            defaults={'semester': 'S1-2026', 'batch': '2023'}
        )
        schedule_objs.append(sched)

        # 12 past sessions per schedule
        for w in range(12):
            session_dt_start = timezone.now() - timedelta(weeks=w, hours=2)
            session_dt_end   = session_dt_start + timedelta(minutes=90)
            session, _ = LectureSession.objects.get_or_create(
                schedule=sched,
                actual_start_time__date=session_dt_start.date(),
                defaults={
                    'is_active': False,
                    'actual_start_time': session_dt_start,
                    'actual_end_time':   session_dt_end,
                    'duration_minutes':  90,
                    'opened_by': tch_u,
                }
            )

            # Attendance for std_13 (one per session — skip if exists)
            att_ts = session_dt_start + timedelta(minutes=random.randint(0, 8))
            if not AIAttendanceLog.objects.filter(
                student=student, schedule=sched,
                timestamp__date=session_dt_start.date()
            ).exists():
                status = random.choice(ATTENDANCE_WEIGHTS)
                AIAttendanceLog.objects.create(
                    student=student, schedule=sched,
                    session=session,
                    status=status,
                    confidence_score=round(random.uniform(0.75, 0.99), 3),
                    method='face_recognition',
                    timestamp=att_ts,
                )

p(f'Courses: {len(course_objs)} | Schedules: {len(schedule_objs)}')

# Grades
with transaction.atomic():
    for course in course_objs:
        score = round(random.uniform(62, 96), 1)
        letter = 'A+' if score >= 95 else 'A' if score >= 88 else 'B+' if score >= 80 else 'B' if score >= 73 else 'C+'
        Grade.objects.get_or_create(
            student=student, course=course, semester='S1-2026',
            defaults={'score': score, 'grade': letter}
        )
p('Grades created')

# Medical Excuses
EXCUSE_DATA = [
    ('مرض حاد — حمى وإنفلونزا', 'approved', schedule_objs[0]),
    ('حادث مروري — إصابة طفيفة', 'approved', schedule_objs[1]),
    ('وفاة في العائلة',           'approved', schedule_objs[2]),
    ('رحلة علمية رسمية مرخّصة',  'pending',  schedule_objs[3]),
    ('عملية جراحية طارئة',       'rejected',  schedule_objs[4]),
]
with transaction.atomic():
    for reason, status, sched in EXCUSE_DATA:
        MedicalExcuse.objects.get_or_create(
            student=student, reason=reason,
            defaults={
                'schedule': sched,
                'status': status,
                'review_note': 'تمت المراجعة وقبول العذر' if status == 'approved' else
                               'مرفوض — لا يوجد مستند داعم' if status == 'rejected' else '',
                'reviewed_by': coord_u if status != 'pending' else None,
            }
        )
p('Medical excuses created')

# ─── 8. GATE LOGS + NOTIFICATIONS + TICKETS ──────────────────────────────────
print('\n[8/9] Gate logs, Notifications, Tickets...')

GATE_STATUSES = ['Allowed', 'Allowed', 'Allowed', 'Allowed', 'Denied']
with transaction.atomic():
    for i in range(25):
        status = random.choice(GATE_STATUSES)
        GateLog.objects.create(
            person_name=student.name,
            student=student,
            status=status,
            timestamp=rnd_past(14),
        )
    for i in range(20):
        status = random.choice(GATE_STATUSES)
        GateLog.objects.create(
            person_name=teacher.name,
            teacher=teacher,
            status=status,
            timestamp=rnd_past(14),
        )
p('Gate logs: 45 entries')

NOTIF_DATA = [
    (std_u, 'تم تسجيل حضورك بنجاح ✓',
     'تم تسجيل حضورك في مادة هندسة البرمجيات بثقة 94.2% بتاريخ اليوم 08:05', 'success'),
    (std_u, 'تحذير: نسبة حضور منخفضة ⚠',
     'نسبة حضورك في مادة أمن المعلومات CS402 وصلت إلى 68% — الحد الأدنى 75%', 'warning'),
    (std_u, 'درجة جديدة 🎓',
     'تم رصد درجتك في قواعد البيانات المتقدمة CS302: 88.5 / 100 — تقدير: B+', 'success'),
    (std_u, 'موعد امتحان 📅',
     'امتحان الذكاء الاصطناعي CS401 — الأحد 2026-06-15 الساعة 09:00 — قاعة 201', 'info'),
    (std_u, 'عذر مقبول ✓',
     'تمت الموافقة على عذرك الطبي المقدم بتاريخ 2026-05-20 بواسطة منسق الكلية', 'success'),
    (tch_u, 'جلسة جديدة مجدولة 📚',
     'جلسة هندسة البرمجيات CS301 — الأحد 08:00—09:30 — قاعة 101', 'info'),
    (tch_u, 'طالب في خطر ⚠',
     'خالد إبراهيم النور — نسبة حضور 68% في CS402 — يحتاج متابعة', 'warning'),
    (tch_u, 'تقرير حضور أسبوعي ✓',
     'تم إنشاء وتصدير تقرير الحضور الأسبوعي لمادة CS301 — 28 حاضر من 35', 'success'),
    (coord_u, 'تقرير الكلية الشهري 📊',
     'نسبة الحضور الإجمالية لكلية الحاسوب هذا الشهر: 82.4% — أعلى من المستوى المطلوب', 'info'),
    (coord_u, 'أعذار طبية معلقة ⚠',
     'يوجد 3 أعذار طبية بانتظار مراجعتك في نظام SHAMEL', 'warning'),
    (gate_u, 'تقرير البوابة اليومي ✓',
     'تم تسجيل 47 دخول صحيح و 3 محاولات مرفوضة اليوم', 'success'),
    (gate_u, 'تنبيه أمني 🔴',
     'محاولة دخول مرفوضة — لم يتم التعرف على الوجه — الثقة 34.1% — الساعة 08:47', 'error'),
]
for usr, title, body, level in NOTIF_DATA:
    Notification.objects.get_or_create(
        user=usr, title=title,
        defaults={'body': body, 'level': level, 'is_read': random.choice([True, False])}
    )
p('Notifications: 12 entries')

TICKETS = [
    (std_u,   'لا يظهر جدول مادة أمن المعلومات CS402',
     'الجدول الدراسي لمادة CS402 لا يظهر في صفحتي الشخصية منذ أسبوعين',
     'open', 'medium'),
    (std_u,   'خطأ في تسجيل الحضور بتاريخ 2026-05-28',
     'سجّل النظام غيابي في مادة CS301 بتاريخ 2026-05-28 رغم حضوري وتسجيل وجهي',
     'in_progress', 'high'),
    (std_u,   'طلب استعراض العذر الطبي المرفوض',
     'أطلب إعادة مراجعة العذر الطبي المرفوض — لديّ وثيقة إضافية من المستشفى',
     'pending', 'low'),
    (tch_u,   'مشكلة في كاميرا القاعة 104',
     'كاميرا القاعة 104 لا تعمل بشكل صحيح أثناء جلسة التعرف على الوجه — تعطل مرتين هذا الأسبوع',
     'open', 'high'),
    (tch_u,   'طلب إضافة مادة CS501 للفصل القادم',
     'أطلب إضافة مادة هياكل البيانات المتقدمة CS501 للفصل الدراسي القادم S2-2026',
     'pending', 'low'),
    (coord_u, 'طلب تقرير الأداء الأكاديمي الشامل',
     'يرجى توفير تقرير مفصّل عن أداء الحضور والدرجات لكلية الحاسوب للفصل S1-2026',
     'in_progress', 'medium'),
]
for usr, subj, body, status, priority in TICKETS:
    SupportTicket.objects.get_or_create(
        subject=subj, user=usr,
        defaults={'body': body, 'status': status, 'priority': priority}
    )
p('Support tickets: 6 entries')

# ─── 9. RICH AUDIT LOG ───────────────────────────────────────────────────────
print('\n[9/9] Rich audit log...')

# AuditLog.timestamp is auto_now_add — set via update() after creation
AuditLog.objects.filter(description__startswith='Demo audit entry').delete()

AUDIT_ENTRIES = [
    (std_u,   'FACE_MATCH',    'Student',        str(student.pk),
     'تسجيل حضور بيومتري — ثقة 94.2% — خالد إبراهيم النور — CS301', '192.168.1.45'),
    (std_u,   'FACE_MATCH',    'Student',        str(student.pk),
     'تسجيل حضور بيومتري — ثقة 91.8% — خالد إبراهيم النور — CS302', '192.168.1.45'),
    (gate_u,  'FACE_MATCH',    'GateLog',        '',
     'دخول بوابة رئيسية مصادق بيومترياً — ثقة 96.3% — خالد إبراهيم النور', '192.168.1.10'),
    (gate_u,  'FACE_REJECT',   'GateLog',        '',
     'رفض دخول بوابة — ثقة منخفضة 34.1% — شخص غير مسجّل', '192.168.1.10'),
    (admin_u, 'AES_ENCRYPT',   'Student',        str(student.pk),
     'تشفير AES-256 لبيانات الوجه البيومترية — CS-2023-013 — خالد إبراهيم النور', '127.0.0.1'),
    (admin_u, 'AES_ENCRYPT',   'Teacher',        str(teacher.pk if teacher else ''),
     'تشفير AES-256 لبصمة وجه الأستاذ — د. أحمد الطاهر — TCH-013', '127.0.0.1'),
    (admin_u, 'CREATE',        'Student',        str(student.pk),
     'إنشاء حساب طالب جديد: خالد إبراهيم النور (CS-2023-013) — كلية الحاسوب', '127.0.0.1'),
    (admin_u, 'CREATE',        'Teacher',        str(teacher.pk if teacher else ''),
     'إنشاء حساب أستاذ جديد: د. أحمد الطاهر محمد — قسم هندسة البرمجيات', '127.0.0.1'),
    (admin_u, 'UPDATE',        'Course',         str(course_objs[0].pk),
     f'تحديث بيانات المادة {course_objs[0].course_code} — تعديل عدد الساعات إلى 3', '127.0.0.1'),
    (admin_u, 'UPDATE',        'Schedule',       str(schedule_objs[0].pk),
     f'تعديل جدول {course_objs[0].course_code} — تغيير القاعة من 101 إلى 103', '127.0.0.1'),
    (admin_u, 'DELETE',        'Schedule',       '99',
     'حذف جدول متعارض CS299 — تعارض زمني مع CS302 — الأحد 09:30', '127.0.0.1'),
    (admin_u, 'EXPORT',        'Student',        '',
     'تصدير بيانات طلاب كلية الحاسوب (CSV) — 48 سجل — S1-2026', '127.0.0.1'),
    (admin_u, 'EXPORT',        'Course',         '',
     'تصدير تقرير الحضور PDF — الفصل S1-2026 — كلية الحاسوب', '127.0.0.1'),
    (tch_u,   'EXPORT',        'Schedule',       '',
     'تصدير جدول محاضرات الأسبوع (Excel) — د. أحمد الطاهر', '192.168.1.62'),
    (tch_u,   'GRADE',         'Grade',          '',
     'رصد درجات مادة CS301 هندسة البرمجيات — 24 طالب — S1-2026', '192.168.1.62'),
    (tch_u,   'SESSION_START', 'LectureSession', str(schedule_objs[0].pk),
     'بدء جلسة CS301 — قاعة 101 — 08:00 — د. أحمد الطاهر', '192.168.1.62'),
    (tch_u,   'SESSION_END',   'LectureSession', str(schedule_objs[0].pk),
     'إنهاء جلسة CS301 — مدة 90 دقيقة — 28 طالب حاضر من 35', '192.168.1.62'),
    (admin_u, 'PERMISSION',    'User',           str(tch_u.pk),
     'منح صلاحية الوصول لجميع قاعات كلية الحاسوب — د. أحمد الطاهر', '127.0.0.1'),
    (admin_u, 'PERMISSION',    'User',           str(coord_u.pk),
     'تعيين منسق — صلاحية كاملة على كلية الحاسوب والمعلومات', '127.0.0.1'),
    (coord_u, 'APPROVE',       'MedicalExcuse',  '',
     'قبول عذر طبي — خالد إبراهيم النور — مرض حاد حمى وإنفلونزا', '192.168.1.71'),
    (admin_u, 'SYSTEM',        'CameraSource',   '',
     'إضافة كاميرا بوابة رئيسية جديدة — IP: 192.168.1.200 — دقة 4K', '127.0.0.1'),
    (admin_u, 'BACKUP',        'Database',       '',
     'نسخ احتياطي تلقائي ناجح — حجم: 124MB — 2026-06-04 02:00 صباحاً', '127.0.0.1'),
    (admin_u, 'UPDATE',        'Classroom',      '',
     'تحديث بيانات قاعة 104 — إضافة كاميرا ذكية Hikvision DS-2CD', '127.0.0.1'),
    (admin_u, 'CREATE',        'Exam',           '',
     'جدولة امتحان CS401 الذكاء الاصطناعي — 2026-06-15 الساعة 09:00 — قاعة 201', '127.0.0.1'),
    (admin_u,  'LOGIN',        'User',           str(admin_u.pk),
     'تسجيل دخول مدير النظام — IP: 127.0.0.1', '127.0.0.1'),
    (std_u,    'LOGIN',        'User',           str(std_u.pk),
     'تسجيل دخول الطالب خالد إبراهيم النور — IP: 192.168.1.45', '192.168.1.45'),
    (tch_u,    'LOGIN',        'User',           str(tch_u.pk),
     'تسجيل دخول الأستاذ د. أحمد الطاهر — IP: 192.168.1.62', '192.168.1.62'),
    (coord_u,  'LOGIN',        'User',           str(coord_u.pk),
     'تسجيل دخول المنسق — IP: 192.168.1.71', '192.168.1.71'),
    (gate_u,   'LOGIN',        'User',           str(gate_u.pk),
     'تسجيل دخول حارس البوابة — IP: 192.168.1.10', '192.168.1.10'),
]

created_ids = []
with transaction.atomic():
    for usr, action, model, tid, desc, ip in AUDIT_ENTRIES:
        obj = AuditLog(
            user=usr, action=action,
            target_model=model, target_id=tid,
            description=desc, ip_address=ip,
        )
        obj.save()
        created_ids.append(obj.pk)

# Spread timestamps over past 30 days via Django ORM (bypasses auto_now_add)
for pk in created_ids:
    days_back = random.randint(1, 30)
    hrs  = random.randint(7, 18)
    mins = random.randint(0, 59)
    dt = timezone.now() - timedelta(days=days_back, hours=hrs, minutes=mins)
    AuditLog.objects.filter(pk=pk).update(timestamp=dt)
p(f'Audit log: {len(AUDIT_ENTRIES)} diverse entries (timestamps spread over 30 days)')

# ─── SUMMARY ─────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('SHAMEL Seed Complete')
print('='*60)
print(f'  Students:      {Student.objects.count()}')
print(f'  Teachers:      {Teacher.objects.count()}')
print(f'  Courses:       {Course.objects.count()}')
print(f'  Schedules:     {Schedule.objects.count()}')
print(f'  Sessions:      {LectureSession.objects.count()}')
print(f'  Attendance:    {AIAttendanceLog.objects.count()}')
print(f'  Enrollments:   {Enrollment.objects.count()}')
print(f'  Gate logs:     {GateLog.objects.count()}')
print(f'  Grades:        {Grade.objects.count()}')
print(f'  Excuses:       {MedicalExcuse.objects.count()}')
print(f'  Tickets:       {SupportTicket.objects.count()}')
print(f'  Notifications: {Notification.objects.count()}')
print(f'  Audit logs:    {AuditLog.objects.count()}')
print()
print('ACCOUNTS:')
print('  admin       / Admin@2026')
print('  coordinator / Coord@2026')
print('  gate        / Gate@2026')
print('  tch_13      / Tch@2026')
print('  std_13      / Std@2026')
