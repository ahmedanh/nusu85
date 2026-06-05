# -*- coding: utf-8 -*-
"""
seed_test_accounts.py
Create/reset clean test accounts for every role with rich pre-seeded data.

Credentials (password = Test@1234):
  test_admin       superuser / admin
  test_coordinator coordinator  (CSI college)
  test_teacher     teacher      (3 courses, 12 sessions, 10 students)
  test_student     student      (attendance, grades, excuses, notifications)
  test_gate        gate staff   (gate logs)

Run:  python seed_test_accounts.py
"""
import os, sys, django, random
from datetime import timedelta, time
from pathlib import Path

os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))
os.environ['USE_LOCAL_DB'] = 'true'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from attendance.models import (
    College, Department, Course, Classroom, Schedule, LectureSession,
    AIAttendanceLog, Student, Teacher, Coordinator, Enrollment,
    GateLog, Grade, MedicalExcuse, Notification, AuditLog, CameraSource,
)

User = get_user_model()
PASSWORD = 'Test@1234'

# ── helpers ──────────────────────────────────────────────────────────────────

def upsert_user(username, first_name, last_name, email,
                is_super=False, is_staff=False):
    u, _ = User.objects.get_or_create(username=username)
    u.first_name = first_name
    u.last_name  = last_name
    u.email      = email
    u.is_superuser = is_super
    u.is_staff     = is_super or is_staff
    u.set_password(PASSWORD)
    u.save()
    return u

def get_college(name):
    c, _ = College.objects.get_or_create(college_name=name, defaults={'name': name})
    return c

def get_dept(name, college):
    d, _ = Department.objects.get_or_create(name=name, college=college)
    return d

def get_course(code, title, dept, college, credits=3):
    c, _ = Course.objects.get_or_create(
        course_code=code,
        defaults={'title': title, 'department': dept,
                  'college': college, 'credits': credits, 'total_hours': credits * 15}
    )
    return c

def get_classroom(name, capacity=40):
    cl, _ = Classroom.objects.get_or_create(name=name, defaults={'capacity': capacity})
    return cl

# ── seed ─────────────────────────────────────────────────────────────────────

with transaction.atomic():

    # ── Infra ────────────────────────────────────────────────────────────────
    csi       = get_college('كلية الحاسوب والمعلومات')
    med       = get_college('كلية الطب البشري')
    dept_cs   = get_dept('هندسة البرمجيات', csi)
    dept_ai   = get_dept('الذكاء الاصطناعي', csi)
    room_a    = get_classroom('قاعة A-101', 50)
    room_b    = get_classroom('قاعة B-202', 35)
    room_c    = get_classroom('مختبر C-303', 25)
    cam, _    = CameraSource.objects.get_or_create(
        name='البوابة الرئيسية',
        defaults={'source': 'rtsp://192.168.1.100:554/main',
                  'location': 'gate', 'is_active': True, 'is_gate': True}
    )
    cs101 = get_course('TS101', 'مقدمة في علم الحاسوب',            dept_cs, csi)
    cs201 = get_course('TS201', 'هياكل البيانات والخوارزميات',     dept_cs, csi)
    cs301 = get_course('TS301', 'قواعد البيانات المتقدمة',         dept_ai, csi)

    # ── [1/5] ADMIN ──────────────────────────────────────────────────────────
    print('[1/5] test_admin')
    admin_u = upsert_user('test_admin', 'أحمد', 'النظام',
                          'test.admin@shamel.edu', is_super=True)
    for i in range(10):
        AuditLog.objects.get_or_create(
            user=admin_u,
            action=f'login',
            target_model='User',
            target_id=str(admin_u.pk),
            description=f'تسجيل دخول المسؤول — جلسة {i+1}',
            defaults={'timestamp': timezone.now() - timedelta(hours=i*4),
                      'ip_address': f'192.168.1.{10+i}'}
        )

    # ── [2/5] COORDINATOR ────────────────────────────────────────────────────
    print('[2/5] test_coordinator')
    coord_u = upsert_user('test_coordinator', 'منسق', 'الكلية',
                          'test.coordinator@shamel.edu')
    Coordinator.objects.filter(auth_user=coord_u).delete()
    Coordinator.objects.create(
        auth_user=coord_u,
        name='د. منسق كلية الحاسوب',
        college=csi,
        university_email='coordinator@shamel.edu',
        phone_number='0912345001',
    )

    # ── [3/5] TEACHER ────────────────────────────────────────────────────────
    print('[3/5] test_teacher')
    teacher_u = upsert_user('test_teacher', 'محمد', 'الأستاذ',
                             'test.teacher@shamel.edu')
    Teacher.objects.filter(auth_user=teacher_u).delete()
    teacher = Teacher.objects.create(
        auth_user=teacher_u,
        name='د. محمد عبدالله الأستاذ',
        gender='M',
        academic_degree='دكتوراه',
        major='علم الحاسوب',
        department=dept_cs,
        college=csi,
        university_email='test.teacher@shamel.edu',
        phone_number='0912345002',
        is_allowed_entry=True,
    )

    # 3 schedules (Sun/Mon/Tue, different times)
    sched_cfg = [
        (cs101, room_a, 'Sun', time(8,  0), time(9,  30)),
        (cs201, room_b, 'Mon', time(10, 0), time(11, 30)),
        (cs301, room_c, 'Tue', time(12, 0), time(13, 30)),
    ]
    schedules = []
    for course, room, day, st, et in sched_cfg:
        sched, _ = Schedule.objects.get_or_create(
            course=course, teacher=teacher, classroom=room,
            defaults={'day_of_week': day, 'start_time': st, 'end_time': et,
                      'batch': '2024', 'semester': '2024-2025 S2'}
        )
        schedules.append(sched)

    # 4 past lecture sessions per schedule
    sessions = []
    for sched in schedules:
        for week in range(1, 5):
            dt_start = timezone.now() - timedelta(weeks=week)
            dt_start = dt_start.replace(
                hour=sched.start_time.hour, minute=0, second=0, microsecond=0)
            dt_end = dt_start + timedelta(minutes=90)
            qs = LectureSession.objects.filter(schedule=sched,
                                               actual_start_time__date=dt_start.date())
            if qs.exists():
                sess = qs.first()
            else:
                sess = LectureSession.objects.create(
                    schedule=sched,
                    is_active=False,
                    actual_start_time=dt_start,
                    actual_end_time=dt_end,
                    duration_minutes=90,
                    opened_by=teacher_u,
                )
            sessions.append(sess)

    # ── [4/5] STUDENTS ───────────────────────────────────────────────────────
    print('[4/5] test_student + peers')
    STUDENTS = [
        ('test_student',  'طالب',   'الاختبار', 'TS2024001', True),
        ('ts_student_02', 'فاطمة',  'عمر',      'TS2024002', True),
        ('ts_student_03', 'خالد',   'إبراهيم',  'TS2024003', True),
        ('ts_student_04', 'مريم',   'يوسف',     'TS2024004', True),
        ('ts_student_05', 'عمر',    'علي',      'TS2024005', True),
        ('ts_student_06', 'زينب',   'سالم',     'TS2024006', True),
        ('ts_student_07', 'محمد',   'الطاهر',   'TS2024007', True),
        ('ts_student_08', 'هند',    'بشير',     'TS2024008', False),  # blocked
        ('ts_student_09', 'يوسف',  'حمزة',     'TS2024009', True),
        ('ts_student_10', 'سارة',   'وليد',     'TS2024010', True),
    ]
    student_objs = []
    for uname, fn, ln, code, allowed in STUDENTS:
        su = upsert_user(uname, fn, ln, f'{uname}@shamel.edu')
        Student.objects.filter(auth_user=su).delete()
        st = Student.objects.create(
            auth_user=su,
            name=f'{fn} {ln}',
            student_code=code,
            department=dept_cs,
            university_email=f'{uname}@shamel.edu',
            phone_number=f'091{code[-5:]}',
            batch='2024',
            is_registered=True,
            is_allowed_entry=allowed,
        )
        student_objs.append(st)

    test_student = student_objs[0]

    # Enroll all in all 3 courses
    enroll_map = [(cs101, room_a), (cs201, room_b), (cs301, room_c)]
    for st in student_objs:
        for course, room in enroll_map:
            Enrollment.objects.get_or_create(
                student=st, course=course,
                defaults={'classroom': room, 'semester': '2024-2025 S2'}
            )

    # Attendance logs — realistic mix
    STATUSES = ['present', 'present', 'present', 'absent', 'late']
    for st in student_objs:
        for sess in sessions:
            AIAttendanceLog.objects.get_or_create(
                student=st, session=sess,
                defaults={
                    'schedule': sess.schedule,
                    'timestamp': sess.actual_start_time + timedelta(
                        minutes=random.randint(0, 20)),
                    'status': random.choice(STATUSES),
                    'confidence_score': round(random.uniform(0.78, 0.99), 3),
                    'method': 'face',
                }
            )

    # Grades for test_student
    for course, score, letter in [
        (cs101, 88, 'B+'), (cs201, 74, 'C+'), (cs301, 95, 'A')
    ]:
        Grade.objects.get_or_create(
            student=test_student, course=course,
            defaults={'score': score, 'grade': letter, 'semester': '2024-2025 S2'}
        )
    # Grades for a few peers too
    for st in student_objs[1:4]:
        for course, score, letter in [(cs101, 80, 'B'), (cs201, 65, 'C')]:
            Grade.objects.get_or_create(
                student=st, course=course,
                defaults={'score': score, 'grade': letter, 'semester': '2024-2025 S2'}
            )

    # Medical excuses for test_student
    excuse_cfg = [
        (schedules[0], 'التزام طبي — مستشفى الخرطوم', 'approved',
         'مقبول — وثيقة مرفقة'),
        (schedules[1], 'وعكة صحية مفاجئة',              'pending',  ''),
        (schedules[2], 'حادث سير — تقرير شرطة',         'rejected',
         'لا تنطبق شروط العذر'),
    ]
    for sched, reason, status, note in excuse_cfg:
        MedicalExcuse.objects.get_or_create(
            student=test_student, schedule=sched,
            defaults={
                'reason': reason,
                'status': status,
                'review_note': note,
                'reviewed_by': admin_u if status != 'pending' else None,
            }
        )

    # Notifications for test_student
    notif_cfg = [
        ('حضور مسجل', 'تم تسجيل حضورك في محاضرة CS101.',           'info'),
        ('عذر مقبول', 'تم قبول عذرك الطبي للمحاضرة الأولى.',       'success'),
        ('تحذير حضور','نسبة حضورك في CS201 أقل من 75%. انتبه!',    'warning'),
        ('درجات محدثة','تم تحديث درجاتك في مقرر قواعد البيانات.', 'info'),
        ('تذكير',      'محاضرة غداً الساعة 8:00 صباحاً.',           'info'),
    ]
    for title, body, level in notif_cfg:
        Notification.objects.get_or_create(
            user=test_student.auth_user, title=title,
            defaults={'body': body, 'level': level, 'is_read': False,
                      'created_at': timezone.now() - timedelta(days=random.randint(0, 7))}
        )

    # ── [5/5] GATE ───────────────────────────────────────────────────────────
    print('[5/5] test_gate')
    gate_u = upsert_user('test_gate', 'حارس', 'البوابة',
                         'test.gate@shamel.edu', is_staff=False)
    # Gate access via group, NOT is_staff (is_staff → admin dashboard)
    from django.contrib.auth.models import Group
    gate_group, _ = Group.objects.get_or_create(name='gate_staff')
    gate_u.groups.add(gate_group)

    # Student gate logs (mix of granted/denied)
    for i, st in enumerate(student_objs):
        GateLog.objects.get_or_create(
            student=st,
            timestamp=timezone.now() - timedelta(hours=i+1),
            defaults={
                'person_name': st.name,
                'status': 'denied' if not st.is_allowed_entry else random.choice(['granted', 'granted', 'denied']),
                'camera': cam,
            }
        )
    # Teacher gate log
    GateLog.objects.get_or_create(
        teacher=teacher,
        timestamp=timezone.now() - timedelta(minutes=20),
        defaults={'person_name': teacher.name, 'status': 'granted', 'camera': cam}
    )
    # Extra historical gate logs for the gate dashboard stats
    for i in range(20):
        st = random.choice(student_objs)
        GateLog.objects.create(
            student=st,
            person_name=st.name,
            status=random.choice(['granted', 'granted', 'granted', 'denied']),
            camera=cam,
            timestamp=timezone.now() - timedelta(hours=i+10),
        )

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print('=' * 58)
    print('  SHAMEL — Test Accounts Seeded (password: Test@1234)')
    print('=' * 58)
    print('  Role          Username            Details')
    print('  ' + '-'*54)
    print(f'  Admin         test_admin          superuser, 10 audit logs')
    print(f'  Coordinator   test_coordinator    college: CSI')
    print(f'  Teacher       test_teacher        3 courses, 12 sessions')
    print(f'  Student       test_student        grades, 3 excuses, notifications')
    print(f'  Gate          test_gate           30+ gate logs')
    print('=' * 58)
    print(f'  Peer students: ts_student_02 … ts_student_10')
    print(f'  ts_student_08 is_allowed_entry=False (denied at gate)')
    print('=' * 58)
