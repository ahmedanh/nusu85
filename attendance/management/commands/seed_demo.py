# -*- coding: utf-8 -*-
"""
seed_demo — creates a realistic set of demo users and data for SHAMEL.
Idempotent: safe to run multiple times (uses get_or_create everywhere).
"""
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction

from attendance.models import (
    College, Department, Classroom, Course, Teacher, Student,
    Coordinator, Schedule, Enrollment,
)


class Command(BaseCommand):
    help = "Seed the database with realistic demo users and academic data."

    @transaction.atomic
    def handle(self, *args, **options):
        out = self.stdout.write
        created = {'users': 0, 'teachers': 0, 'students': 0,
                   'coordinators': 0, 'schedules': 0}

        # ── College ──────────────────────────────────────────────
        college, _ = College.objects.get_or_create(
            college_name='كلية العلوم والتقنية',
            defaults={'name': 'Science & Technology'},
        )

        # ── Departments ──────────────────────────────────────────
        dept_cs, _ = Department.objects.get_or_create(
            name='Computer Science', defaults={'college': college})
        dept_math, _ = Department.objects.get_or_create(
            name='Mathematics', defaults={'college': college})

        # ── Classrooms ───────────────────────────────────────────
        room101, _ = Classroom.objects.get_or_create(
            name='قاعة 101',
            defaults={'location': 'المبنى الرئيسي', 'capacity': 50,
                      'classroom_type': 'Lecture'})
        room202, _ = Classroom.objects.get_or_create(
            name='قاعة 202',
            defaults={'location': 'المبنى الرئيسي', 'capacity': 30,
                      'classroom_type': 'Lecture'})

        # ── Admin ────────────────────────────────────────────────
        admin, c = User.objects.get_or_create(
            username='admin',
            defaults={'first_name': 'محمد العمر', 'is_staff': True,
                      'is_superuser': True, 'email': 'admin@shamel.edu.sd'})
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('Admin@SHAMEL2025!')
        admin.save()
        if c:
            created['users'] += 1
        out('  admin user ready')

        # ── Coordinators ─────────────────────────────────────────
        coord_data = [
            ('coord1', 'فاطمة حسن', dept_cs, 'fatima.hassan@shamel.edu.sd'),
            ('coord2', 'عمر الأمين', dept_math, 'omar.amin@shamel.edu.sd'),
        ]
        for username, name, dept, email in coord_data:
            u, c = User.objects.get_or_create(
                username=username,
                defaults={'first_name': name, 'email': email})
            u.set_password('Coord@SHAMEL2025!')
            u.first_name = name
            u.save()
            if c:
                created['users'] += 1
            co, cc = Coordinator.objects.get_or_create(
                auth_user=u,
                defaults={'name': name, 'college': college,
                          'phone_number': '0900000000',
                          'university_email': email})
            if cc:
                created['coordinators'] += 1
        out('  coordinators ready')

        # ── Teachers ─────────────────────────────────────────────
        teacher_data = [
            ('teacher1', 'د. أحمد الرشيد', dept_cs, 'ahmed.rashid@shamel.edu.sd'),
            ('teacher2', 'د. سارة النور', dept_math, 'sara.nour@shamel.edu.sd'),
            ('teacher3', 'د. خالد منصور', dept_cs, 'khalid.mansour@shamel.edu.sd'),
            ('teacher4', 'د. نادية إبراهيم', dept_math, 'nadia.ibrahim@shamel.edu.sd'),
        ]
        teachers = {}
        for username, name, dept, email in teacher_data:
            u, c = User.objects.get_or_create(
                username=username,
                defaults={'first_name': name, 'email': email})
            u.set_password('Teacher@SHAMEL2025!')
            u.first_name = name
            u.email = email
            u.save()
            if c:
                created['users'] += 1
            t, tc = Teacher.objects.get_or_create(
                auth_user=u,
                defaults={'name': name, 'gender': 'M', 'academic_degree': 'PhD',
                          'major': dept.name, 'department': dept, 'college': college,
                          'university_email': email})
            if tc:
                created['teachers'] += 1
            teachers[username] = t
        out('  teachers ready')

        # ── Course CS101 ─────────────────────────────────────────
        course, _ = Course.objects.get_or_create(
            course_code='CS101',
            defaults={'title': 'مقدمة في علوم الحاسوب', 'credits': 3,
                      'college': college, 'department': dept_cs,
                      'total_hours': 3})

        # ── Students ─────────────────────────────────────────────
        student_names = [
            'سارة محمد', 'أحمد علي', 'محمد إبراهيم', 'نور الهدى', 'يوسف الحسن',
            'منى عبدالله', 'كريم طارق', 'زينب الفاضل', 'عمر النور', 'هناء بشير',
        ]
        for i, name in enumerate(student_names, start=1):
            username = f'student{i}'
            code = f'CS-2024-{i:03d}'
            email = f'{username}@shamel.edu.sd'
            u, c = User.objects.get_or_create(
                username=username,
                defaults={'first_name': name, 'email': email})
            u.set_password('Student@SHAMEL2025!')
            u.first_name = name
            u.save()
            if c:
                created['users'] += 1
            s, sc = Student.objects.get_or_create(
                student_code=code,
                defaults={'name': name, 'department': dept_cs,
                          'auth_user': u, 'is_registered': True,
                          'is_allowed_entry': True,
                          'university_email': email, 'batch': '2024'})
            if not sc and s.auth_user_id != u.id:
                s.auth_user = u
                s.save()
            if sc:
                created['students'] += 1
            Enrollment.objects.get_or_create(
                student=s, course=course, classroom=room101,
                defaults={'semester': '1'})
        out('  students ready & enrolled in CS101')

        # ── Gate staff ───────────────────────────────────────────
        gate_group, _ = Group.objects.get_or_create(name='gate_staff')
        for username, name in [('gate1', 'حارس البوابة 1'),
                               ('gate2', 'حارس البوابة 2')]:
            u, c = User.objects.get_or_create(
                username=username,
                defaults={'first_name': name,
                          'email': f'{username}@shamel.edu.sd'})
            u.set_password('Gate@SHAMEL2025!')
            u.first_name = name
            u.save()
            u.groups.add(gate_group)
            if c:
                created['users'] += 1
        out('  gate staff ready (group: gate_staff)')

        # ── Schedules for CS101 ──────────────────────────────────
        sched_specs = [
            ('Sunday', teachers['teacher1'], room101),
            ('Tuesday', teachers['teacher1'], room101),
            ('Monday', teachers['teacher2'], room202),
            ('Wednesday', teachers['teacher2'], room202),
        ]
        for day, teacher, room in sched_specs:
            start = (datetime.time(8, 0) if day in ('Sunday', 'Tuesday')
                     else datetime.time(10, 0))
            end = (datetime.time(10, 0) if day in ('Sunday', 'Tuesday')
                   else datetime.time(12, 0))
            sch, sc = Schedule.objects.get_or_create(
                course=course, classroom=room, teacher=teacher,
                day_of_week=day, start_time=start,
                defaults={'end_time': end, 'batch': '2024', 'semester': '1'})
            if sc:
                created['schedules'] += 1
        out('  schedules ready')

        # ── Summary ──────────────────────────────────────────────
        out('')
        out(self.style.SUCCESS('═══ SEED COMPLETE ═══'))
        out(f"  New auth users:    {created['users']}")
        out(f"  New teachers:      {created['teachers']}")
        out(f"  New students:      {created['students']}")
        out(f"  New coordinators:  {created['coordinators']}")
        out(f"  New schedules:     {created['schedules']}")
        out('')
        out('  Login credentials:')
        out('    admin    / Admin@SHAMEL2025!')
        out('    coord1-2 / Coord@SHAMEL2025!')
        out('    teacher1-4 / Teacher@SHAMEL2025!')
        out('    student1-10 / Student@SHAMEL2025!')
        out('    gate1-2  / Gate@SHAMEL2025!')
