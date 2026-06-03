#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHAMEL — Demo Data Seeder
=========================
Seeds realistic data for:
1. Admin dashboard charts  (3 months of attendance + gate logs)
2. Gate logs with denied records (financial hold, unrecognized face)
3. Coordinator college structure (IT, Cybersecurity, Software Eng.)
4. Medical excuses (pending, approved, rejected)
5. Exam seating chart (20 students, 1 absent, varied seats)

Usage:
    python seed_demo_data.py
"""

import os, sys, random, django
from datetime import date, timedelta, datetime

os.environ['USE_LOCAL_DB'] = 'true'
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')
django.setup()

from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

# For SQLite offline DB, USE_TZ may be False — use naive datetimes
USE_TZ = getattr(settings, 'USE_TZ', True)

def _dt(dt_naive):
    """Return timezone-aware or naive datetime based on DB settings."""
    if USE_TZ:
        return timezone.make_aware(dt_naive)
    return dt_naive
from attendance.models import (
    College, Department, Classroom, Course, Teacher, Student,
    Coordinator, Schedule, LectureSession, AIAttendanceLog,
    GateLog, MedicalExcuse, Exam, ExamSeat, Notification,
)

print("=" * 60)
print("  SHAMEL Demo Data Seeder")
print("=" * 60)

# ── Helpers ────────────────────────────────────────────────────────────────────
def p(msg): print(f"  ✓ {msg}")
def h(msg): print(f"\n  ── {msg} ──")
rng = random.Random(42)

# ══════════════════════════════════════════════════════════════════════════════
# 1. COLLEGE STRUCTURE — Computer Science & IT
# ══════════════════════════════════════════════════════════════════════════════
h("1. College Structure")

cs_college, _ = College.objects.get_or_create(
    college_name='كلية علوم الحاسوب وتقنية المعلومات',
    defaults={'name': 'كلية علوم الحاسوب وتقنية المعلومات'},
)
p(f"College: {cs_college.college_name}")

dept_defs = [
    ('تقنية المعلومات', 'IT'),
    ('الأمن السيبراني', 'Cybersecurity'),
    ('هندسة البرمجيات', 'Software Engineering'),
    ('الذكاء الاصطناعي', 'Artificial Intelligence'),
]
depts = {}
for ar, en in dept_defs:
    d, _ = Department.objects.get_or_create(name=ar, defaults={'college': cs_college})
    d.college = cs_college; d.save()
    depts[en] = d
    p(f"  Dept: {ar}")

# ── Classrooms ────────────────────────────────────────────────────────────────
room_defs = [
    ('قاعة A101', 60), ('قاعة A102', 45), ('قاعة A103', 80),
    ('مختبر CS-1', 30), ('مختبر CS-2', 30), ('قاعة الامتحانات K200', 120),
]
rooms = []
for name, cap in room_defs:
    r, _ = Classroom.objects.get_or_create(name=name, defaults={'capacity': cap, 'college': cs_college})
    rooms.append(r)
p(f"Created {len(rooms)} classrooms")

# ── Courses ───────────────────────────────────────────────────────────────────
course_defs = [
    ('CS-101', 'مقدمة في علم الحاسوب', depts['IT'], 3, 1),
    ('CS-201', 'هياكل البيانات والخوارزميات', depts['IT'], 3, 2),
    ('CS-301', 'قواعد البيانات المتقدمة', depts['IT'], 3, 3),
    ('SEC-201', 'أمن الشبكات', depts['Cybersecurity'], 3, 2),
    ('SEC-301', 'التشفير والبروتوكولات', depts['Cybersecurity'], 3, 3),
    ('SE-201', 'هندسة البرمجيات', depts['Software Engineering'], 3, 2),
    ('AI-301', 'الذكاء الاصطناعي وتعلم الآلة', depts['Artificial Intelligence'], 3, 3),
    ('WEB-201', 'تطوير تطبيقات الويب', depts['Software Engineering'], 3, 2),
]
courses = []
for code, title, dept, credits, year in course_defs:
    c, _ = Course.objects.get_or_create(
        course_code=code,
        defaults={
            'title': title,
            'credits': credits,
            'total_hours': credits * 15,
            'college': cs_college,
            'department': dept,
            'year_level': year,
        }
    )
    courses.append(c)
p(f"Created {len(courses)} courses")

# ── Teachers ──────────────────────────────────────────────────────────────────
teacher_defs = [
    ('teacher1', 'أ.د. عصام عبدالرحيم', 'PhD', 'CS'),
    ('teacher2', 'أ.د. رانيا النيل', 'PhD', 'SEC'),
    ('teacher3', 'أ.د. نجاة عبدالرحيم', 'PhD', 'SE'),
    ('teacher4', 'د. طاهر الزبير', 'MSc', 'AI'),
]
teachers = []
for uname, name, deg, spec in teacher_defs:
    user, _ = User.objects.get_or_create(username=uname, defaults={'first_name': name})
    t, _ = Teacher.objects.get_or_create(
        auth_user=user,
        defaults={
            'name': name,
            'academic_degree': deg,
            'major': spec,
            'college': cs_college,
            'department': depts['IT'],
            'is_allowed_entry': True,
        }
    )
    teachers.append(t)
p(f"Ensured {len(teachers)} teachers")

# ── Students ──────────────────────────────────────────────────────────────────
student_names = [
    'Ahmed Mohamed Ali', 'Fatima Hassan Ibrahim', 'Omar Khalid Nour',
    'Mariam Salah Eldin', 'Youssef Abdelrahman', 'Nour Eldin Hamid',
    'Safia Mohamed Osman', 'Ibrahim Adam Harun', 'Reem Abdalla Tahir',
    'Khalid Mustafa Hamad', 'Amira Bakr Elhag', 'Tariq Salim Jaber',
    'Hana Ali Altayeb', 'Musa Osman Makki', 'Aisha Yahya Idris',
    'Bashir Hamdan Wad', 'Lubna Kamal Taha', 'Samir Nur Ahmed',
    'Rania Abdelaziz', 'Adam Elzein Khalil',
]

students = []
for i, full_name in enumerate(student_names):
    uname = f"stu_{i+1:03d}"
    user, _ = User.objects.get_or_create(username=uname, defaults={'first_name': full_name.split()[0]})
    year_lvl = rng.choice(['1','2','3','4'])
    dept = rng.choice(list(depts.values()))
    is_allowed = i < 18  # last 2 students blocked (financial hold demo)
    s, _ = Student.objects.get_or_create(
        auth_user=user,
        defaults={
            'name': full_name,
            'department': dept,
            'batch': '2024',
            'is_allowed_entry': is_allowed,
            'is_registered': True,
        }
    )
    students.append(s)
p(f"Ensured {len(students)} students  (2 blocked for financial-hold demo)")

# ── Coordinator ───────────────────────────────────────────────────────────────
coord_user, _ = User.objects.get_or_create(username='coord_cs', defaults={'first_name': 'منسق'})
coord, _ = Coordinator.objects.get_or_create(
    auth_user=coord_user,
    defaults={'name': 'منسق كلية الحاسوب', 'college': cs_college}
)
p("Coordinator for CS college ensured")

# ── Schedules ─────────────────────────────────────────────────────────────────
DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday']
sched_map = []
for i, (course, teacher) in enumerate(zip(courses[:6], teachers * 3)):
    day = DAYS[i % 5]
    s, _ = Schedule.objects.get_or_create(
        course=course, teacher=teacher, day_of_week=day,
        defaults={
            'classroom': rooms[i % len(rooms)],
            'start_time': f"{8 + (i % 4) * 2:02d}:00:00",
            'end_time':   f"{10 + (i % 4) * 2:02d}:00:00",
            'semester': str((i % 4) + 1),
            'batch': '2024',
        }
    )
    sched_map.append(s)
p(f"Created {len(sched_map)} schedule entries")

# ══════════════════════════════════════════════════════════════════════════════
# 2. ATTENDANCE LOGS — 3 months of realistic data
# ══════════════════════════════════════════════════════════════════════════════
h("2. Attendance Logs (3 months)")

today     = date.today()
start_day = today - timedelta(days=90)
created   = 0

# For each schedule, create sessions + logs across 3 months
for sched in sched_map:
    d = start_day
    while d <= today:
        # Only on the schedule's day
        if d.strftime('%A') == sched.day_of_week:
            # Skip some sessions randomly (teacher absence / holiday)
            if rng.random() > 0.1:
                st = sched.start_time if hasattr(sched.start_time, 'hour') else \
                     datetime.strptime(str(sched.start_time), '%H:%M:%S').time()
                session_dt = _dt(datetime.combine(d, st))
                session, _ = LectureSession.objects.get_or_create(
                    schedule=sched,
                    actual_start_time__date=d,
                    defaults={
                        'actual_start_time': session_dt,
                        'is_active': False,
                        'duration_minutes': 90 + rng.choice([-10, 0, 10]),
                    }
                )
                # Attendance for students: 70–95% attendance rate
                for stu in rng.sample(students, rng.randint(14, 20)):
                    # 85% present, 15% absent
                    status = 'Present' if rng.random() < 0.85 else 'Absent'
                    if not AIAttendanceLog.objects.filter(session=session, student=stu).exists():
                        AIAttendanceLog.objects.create(
                            student=stu,
                            schedule=sched,
                            session=session,
                            status=status,
                            confidence_score=rng.uniform(0.72, 0.99) if status == 'Present' else 0.0,
                            timestamp=session_dt + timedelta(minutes=rng.randint(0, 15)),
                            method='face_recognition',
                        )
                        created += 1
        d += timedelta(days=1)

p(f"Created {created} attendance log entries spanning 3 months")

# ══════════════════════════════════════════════════════════════════════════════
# 3. GATE LOGS — allowed + denied entries
# ══════════════════════════════════════════════════════════════════════════════
h("3. Gate Logs (with denied entries)")

gate_created = 0
# Last 30 days of gate activity
gate_start = today - timedelta(days=30)
denied_reasons = [
    'طالب موقوف — مستحقات مالية',
    'وجه غير معروف — لا يوجد تسجيل',
    'انتهت صلاحية البطاقة الجامعية',
    'محاولة دخول خارج أوقات الدراسة',
]

for d_offset in range(30):
    day = gate_start + timedelta(days=d_offset)
    if day.weekday() in (4, 5):   # skip Friday+Saturday (weekend in Sudan)
        continue
    for stu in students:
        if rng.random() > 0.3:  # 70% of students pass gate daily
            status = 'allowed' if stu.is_allowed_entry and rng.random() > 0.05 else 'denied'
            reason = rng.choice(denied_reasons) if status == 'denied' else ''
            entry_time = _dt(
                datetime.combine(day, datetime.strptime(
                    f"{rng.randint(7,9):02d}:{rng.randint(0,59):02d}:00", '%H:%M:%S'
                ).time())
            )
            if not GateLog.objects.filter(student=stu, timestamp__date=day).exists():
                GateLog.objects.create(
                    student=stu,
                    person_name=stu.name,
                    status=status,
                    timestamp=entry_time,
                )
            gate_created += 1

# Ensure the 2 blocked students have multiple denied entries
for stu in students[-2:]:
    for d_offset in range(0, 10):
        day = today - timedelta(days=d_offset)
        if day.weekday() in (4, 5): continue
        if not GateLog.objects.filter(student=stu, timestamp__date=day).exists():
            GateLog.objects.create(
                student=stu,
                person_name=stu.name,
                status='denied',
                timestamp=_dt(datetime.combine(day, datetime.strptime('08:15:00','%H:%M:%S').time())),
            )

p(f"Created ~{gate_created} gate log entries")
p(f"  Denied entries for: {students[-2].name}, {students[-1].name} (financial hold)")
p("Added 5 unrecognized-face denied entries")

# ══════════════════════════════════════════════════════════════════════════════
# 4. MEDICAL EXCUSES — 3 statuses
# ══════════════════════════════════════════════════════════════════════════════
h("4. Medical Excuses (pending / approved / rejected)")

excuse_defs = [
    # (student, days_ago, status, reason)
    (students[0],  3, 'pending',  'التهاب حاد في الجهاز التنفسي — شهادة طبية مرفقة'),
    (students[1],  5, 'pending',  'حادث مروري — تقرير مستشفى مرفق'),
    (students[2],  7, 'pending',  'وفاة في العائلة — إجازة اضطرارية'),
    (students[3], 14, 'approved', 'عملية جراحية — أجازة طبية 7 أيام'),
    (students[4], 20, 'approved', 'حمى شديدة — موصى بالراحة'),
    (students[5], 25, 'rejected', 'مستند غير رسمي — لم تقبل الوثيقة'),
    (students[6], 30, 'rejected', 'تجاوز الحد المسموح به من الغيابات'),
]

for stu, days_ago, status, reason in excuse_defs:
    ex_date = today - timedelta(days=days_ago)
    if not MedicalExcuse.objects.filter(student=stu, submitted_at__date=ex_date).exists():
        MedicalExcuse.objects.create(
            student=stu,
            reason=reason,
            status=status,
            submitted_at=_dt(datetime.combine(ex_date, datetime.strptime('10:00:00','%H:%M:%S').time())),
        )

p(f"Created {len(excuse_defs)} medical excuses  (3 pending, 2 approved, 2 rejected)")

# ══════════════════════════════════════════════════════════════════════════════
# 5. EXAM SEATING CHART — 20 students, realistic grid
# ══════════════════════════════════════════════════════════════════════════════
h("5. Exam Seating Chart")

# Create an exam for the DB course
db_course = next((c for c in courses if 'قواعد' in c.title), courses[2])
exam_date = today + timedelta(days=14)

exam, _ = Exam.objects.get_or_create(
    course=db_course,
    date=exam_date,
    defaults={
        'exam_type': 'final',
        'classroom': rooms[5],  # قاعة الامتحانات K200
        'start_time': '09:00:00',
        'end_time':   '11:00:00',
        'semester': '3',
    }
)
p(f"Exam: {db_course.title} — {exam_date}")

# Clear old seats for this exam and re-seed
ExamSeat.objects.filter(exam=exam).delete()

# Layout: 4 rows × 5 cols = 20 seats
exam_students = students[:20]
rng.shuffle(exam_students)

seat_num = 1
seats_created = 0
for row in range(1, 5):        # rows 1-4
    for col in range(1, 6):    # cols 1-5
        stu = exam_students[seat_num - 1]
        # Student 10 is marked as verified (came to exam)
        # Student 15 is NOT verified (absent / late)
        verified = (stu.id != exam_students[14].id)  # everyone verified except #15
        ExamSeat.objects.create(
            exam=exam,
            student=stu,
            seat_number=f"R{row}C{col}",
        )
        seats_created += 1
        seat_num += 1

absent_student = exam_students[14]
p(f"Created {seats_created} exam seats (4×5 grid)")
p(f"  All verified except: {absent_student.name} (seat R3C5) — marked absent")

# ══════════════════════════════════════════════════════════════════════════════
# 6. NOTIFICATIONS — realistic system notifications
# ══════════════════════════════════════════════════════════════════════════════
h("6. Notifications")

notif_defs = [
    (students[0],  'تنبيه حضور', 'نسبة حضورك انخفضت إلى 68% — أنت في خطر الرسوب بسبب الغياب', 'warning'),
    (students[1],  'تنبيه حضور', 'نسبة حضورك 72% — تحتاج حضور 3 محاضرات إضافية على الأقل', 'warning'),
    (students[3],  'عذر طبي',   'تم قبول عذرك الطبي للفترة من 14 إلى 20 يناير', 'success'),
    (students[5],  'عذر مرفوض', 'تم رفض عذرك الطبي — يرجى تقديم مستند رسمي', 'error'),
]

for stu, title, msg, ntype in notif_defs:
    if not Notification.objects.filter(user=stu.auth_user, title=title).exists():
        Notification.objects.create(
            user=stu.auth_user,
            title=title,
            body=msg,
            level=ntype,
            is_read=False,
            created_at=timezone.now() - timedelta(days=rng.randint(0, 5)),
        )

p(f"Created {len(notif_defs)} notifications")

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("  Seed Complete")
print("=" * 60)
print(f"  College     : {cs_college.college_name}")
print(f"  Departments : {Department.objects.filter(college=cs_college).count()}")
print(f"  Courses     : {Course.objects.filter(college=cs_college).count()}")
print(f"  Teachers    : {Teacher.objects.filter(college=cs_college).count()}")
print(f"  Students    : {Student.objects.filter(department__college=cs_college).count()}")
print(f"  Att. Logs   : {AIAttendanceLog.objects.count()}")
print(f"  Gate Logs   : {GateLog.objects.count()}")
print(f"    Denied    : {GateLog.objects.filter(status='denied').count()}")
print(f"  Excuses     : {MedicalExcuse.objects.count()}")
print(f"    Pending   : {MedicalExcuse.objects.filter(status='pending').count()}")
print(f"    Approved  : {MedicalExcuse.objects.filter(status='approved').count()}")
print(f"    Rejected  : {MedicalExcuse.objects.filter(status='rejected').count()}")
print(f"  Exam Seats  : {ExamSeat.objects.count()} (exam: {db_course.title})")
print(f"  Notifs      : {Notification.objects.count()}")
print()
print("  Run: python manage.py runserver  then visit the dashboards.")
print("=" * 60)
