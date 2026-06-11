# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import JSONField

try:
    from pgvector.django import VectorField
except ImportError:
    VectorField = None


# ─────────────────────────────────────────────────────────────────────────────
# College / Department / Classroom
# ─────────────────────────────────────────────────────────────────────────────
class College(models.Model):
    college_id   = models.AutoField(primary_key=True)
    college_name = models.CharField(max_length=200)
    name         = models.CharField(max_length=200, blank=True)

    class Meta:
        db_table = 'attendance_college'

    def __str__(self):
        return self.college_name


class Department(models.Model):
    name    = models.CharField(max_length=200)
    college = models.ForeignKey(College, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'attendance_department'

    def __str__(self):
        return self.name


class Classroom(models.Model):
    CLASSROOM_TYPES = [('Lecture', 'Lecture'), ('Lab', 'Lab'), ('Hall', 'Hall')]
    name           = models.CharField(max_length=100)
    location       = models.CharField(max_length=200, blank=True)
    capacity       = models.IntegerField(default=30)
    classroom_type = models.CharField(max_length=50, choices=CLASSROOM_TYPES, default='Lecture')
    is_busy        = models.BooleanField(default=False)
    college        = models.ForeignKey('College', on_delete=models.SET_NULL, null=True, blank=True,
                                       help_text='اترك فارغاً للقاعات المشتركة بين الكليات')

    class Meta:
        db_table = 'attendance_classroom'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────────────────────────────────────
class Course(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title       = models.CharField(max_length=200)
    credits     = models.IntegerField(default=3)
    total_hours = models.IntegerField(default=3)
    college     = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    department  = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    year_level  = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_course'

    def __str__(self):
        return f'{self.course_code} - {self.title}'


# ─────────────────────────────────────────────────────────────────────────────
# Teacher
# ─────────────────────────────────────────────────────────────────────────────
class Teacher(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]
    DEGREE_CHOICES = [('BSc', 'BSc'), ('MSc', 'MSc'), ('PhD', 'PhD'), ('Prof', 'Professor')]

    teacher_id       = models.AutoField(primary_key=True)
    auth_user        = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name             = models.CharField(max_length=200)
    gender           = models.CharField(max_length=1, choices=GENDER_CHOICES, default='M')
    academic_degree  = models.CharField(max_length=10, choices=DEGREE_CHOICES, default='PhD')
    major            = models.CharField(max_length=200, blank=True)
    department       = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    college          = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    university_email = models.EmailField(blank=True)
    phone_number     = models.CharField(max_length=20, blank=True)
    is_allowed_entry = models.BooleanField(default=True)
    face_image       = models.ImageField(upload_to='teacher_faces/', null=True, blank=True)

    class Meta:
        db_table = 'attendance_teacher'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Student
# ─────────────────────────────────────────────────────────────────────────────
class Student(models.Model):
    auth_user        = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    student_code     = models.CharField(max_length=50, unique=True)
    name             = models.CharField(max_length=200)
    department       = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    university_email = models.EmailField(blank=True)
    phone_number     = models.CharField(max_length=20, blank=True)
    batch            = models.CharField(max_length=10, blank=True)
    is_registered    = models.BooleanField(default=False)
    is_allowed_entry = models.BooleanField(default=True)
    face_image       = models.ImageField(upload_to='student_faces/', null=True, blank=True)

    class Meta:
        db_table = 'attendance_student'

    def __str__(self):
        return f'{self.student_code} - {self.name}'


# ─────────────────────────────────────────────────────────────────────────────
# Coordinator
# ─────────────────────────────────────────────────────────────────────────────
class Coordinator(models.Model):
    auth_user        = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    name             = models.CharField(max_length=200)
    college          = models.ForeignKey(College, on_delete=models.SET_NULL, null=True, blank=True)
    university_email = models.EmailField(blank=True)
    phone_number     = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'attendance_coordinator'

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Schedule / Enrollment / LectureSession
# ─────────────────────────────────────────────────────────────────────────────
class Schedule(models.Model):
    DAYS = [('Sunday','Sunday'),('Monday','Monday'),('Tuesday','Tuesday'),
            ('Wednesday','Wednesday'),('Thursday','Thursday'),('Friday','Friday'),('Saturday','Saturday')]
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)
    teacher     = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    classroom   = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    batch                    = models.CharField(max_length=10, blank=True)
    semester                 = models.CharField(max_length=10, blank=True)
    total_lectures_required  = models.IntegerField(default=28)

    class Meta:
        db_table = 'attendance_schedule'

    def __str__(self):
        return f'{self.course} - {self.day_of_week} {self.start_time}'


class Enrollment(models.Model):
    student   = models.ForeignKey(Student, on_delete=models.CASCADE)
    course    = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    semester  = models.CharField(max_length=10, blank=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_enrollment'
        unique_together = ('student', 'course')

    def __str__(self):
        return f'{self.student} → {self.course}'


class LectureSession(models.Model):
    schedule          = models.ForeignKey(Schedule, on_delete=models.CASCADE, null=True, blank=True)
    is_active         = models.BooleanField(default=True)
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time   = models.DateTimeField(null=True, blank=True)
    duration_minutes  = models.IntegerField(null=True, blank=True)
    opened_by         = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'attendance_lecturesession'

    def __str__(self):
        return f'Session {self.id} - {self.schedule}'


# ─────────────────────────────────────────────────────────────────────────────
# Attendance / Face Embeddings
# ─────────────────────────────────────────────────────────────────────────────
class AIAttendanceLog(models.Model):
    STATUS_CHOICES = [('Present','Present'),('Absent','Absent'),('Late','Late'),('Excused','Excused')]
    student   = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule  = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    session   = models.ForeignKey(LectureSession, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Present')
    confidence_score = models.FloatField(null=True, blank=True)
    method    = models.CharField(max_length=50, default='face_recognition')

    class Meta:
        db_table = 'attendance_aiattendancelog'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['student', 'status']),
            models.Index(fields=['schedule', 'status']),
            models.Index(fields=['student', 'timestamp']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'schedule'],
                condition=models.Q(session__isnull=True),
                name='unique_student_schedule_nosession',
            ),
        ]

    def __str__(self):
        return f'{self.student} - {self.status} @ {self.timestamp}'


class StudentFaceEmbedding(models.Model):
    student   = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='face_embedding')
    embedding = VectorField(dimensions=512) if VectorField else models.JSONField(default=list)
    extra_embeddings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_studentfaceembedding'

    def __str__(self):
        return f'Embedding: {self.student}'


class TeacherFaceEmbedding(models.Model):
    teacher    = models.OneToOneField(Teacher, on_delete=models.CASCADE, related_name='face_embedding')
    face_vector = VectorField(dimensions=512) if VectorField else models.JSONField(default=list)
    extra_embeddings = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_teacherfaceembedding'

    def __str__(self):
        return f'Embedding: {self.teacher}'


# ─────────────────────────────────────────────────────────────────────────────
# Camera / Gate
# ─────────────────────────────────────────────────────────────────────────────
class CameraSource(models.Model):
    name       = models.CharField(max_length=100)
    source     = models.CharField(max_length=200, default='0')  # index or RTSP URL
    location   = models.CharField(max_length=200, blank=True)
    is_active  = models.BooleanField(default=True)
    is_gate    = models.BooleanField(default=False)

    class Meta:
        db_table = 'attendance_camerasource'

    def __str__(self):
        return self.name


class GateLog(models.Model):
    STATUS_CHOICES = [('Allowed','Allowed'),('Denied','Denied'),('Unknown','Unknown')]
    person_name  = models.CharField(max_length=200, blank=True)
    student      = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    teacher      = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unknown')
    timestamp    = models.DateTimeField(default=timezone.now)
    camera       = models.ForeignKey(CameraSource, on_delete=models.SET_NULL, null=True, blank=True)
    snapshot     = models.ImageField(upload_to='gate_snapshots/', null=True, blank=True)

    class Meta:
        db_table = 'attendance_gatelog'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status']),
            models.Index(fields=['student', 'timestamp']),
        ]

    def __str__(self):
        return f'{self.person_name} - {self.status} @ {self.timestamp}'


# ─────────────────────────────────────────────────────────────────────────────
# Notifications / Support
# ─────────────────────────────────────────────────────────────────────────────
class Notification(models.Model):
    LEVEL_CHOICES = [('info','info'),('warning','warning'),('danger','danger'),('success','success')]
    user      = models.ForeignKey(User, on_delete=models.CASCADE)
    title     = models.CharField(max_length=200)
    body      = models.TextField(blank=True)
    level     = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='info')
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_notification'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.user} - {self.title}'


class SupportTicket(models.Model):
    STATUS_CHOICES = [('open','Open'),('in_progress','In Progress'),('closed','Closed')]
    PRIORITY_CHOICES = [('low','Low'),('medium','Medium'),('high','High')]
    user       = models.ForeignKey(User, on_delete=models.CASCADE)
    subject    = models.CharField(max_length=300)
    body       = models.TextField()
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority   = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    admin_reply = models.TextField(blank=True)

    class Meta:
        db_table = 'attendance_supportticket'
        ordering = ['-created_at']

    @property
    def requester(self):
        return self.user

    def __str__(self):
        return f'#{self.id} {self.subject}'


# ─────────────────────────────────────────────────────────────────────────────
# Financial / Grade / Audit
# ─────────────────────────────────────────────────────────────────────────────
class FinancialStatus(models.Model):
    STATUS_CHOICES = [('Paid','Paid'),('Unpaid','Unpaid'),('Partial','Partial')]
    student    = models.OneToOneField(Student, on_delete=models.CASCADE)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unpaid')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_financialstatus'

    def __str__(self):
        return f'{self.student} - {self.status}'



class AuditLog(models.Model):
    user        = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action      = models.CharField(max_length=100)
    target_model = models.CharField(max_length=100, blank=True)
    target_id   = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    timestamp   = models.DateTimeField(auto_now_add=True)
    ip_address  = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_auditlog'
        ordering = ['-timestamp']

    @property
    def actor(self):
        return self.user

    def __str__(self):
        return f'{self.user} - {self.action} @ {self.timestamp}'


# ─────────────────────────────────────────────────────────────────────────────
# Phase 7 — Excuse / Exam / Course Evaluation
# ─────────────────────────────────────────────────────────────────────────────
class MedicalExcuse(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('approved','Approved'),('rejected','Rejected')]
    student     = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule    = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True)
    reason      = models.TextField()
    document    = models.FileField(upload_to='excuses/', null=True, blank=True)
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    review_note = models.TextField(blank=True)

    class Meta:
        db_table = 'attendance_medicalexcuse'

    def __str__(self):
        return f'Excuse: {self.student} - {self.status}'


class Exam(models.Model):
    course      = models.ForeignKey(Course, on_delete=models.CASCADE)
    exam_type   = models.CharField(max_length=50, default='Final')
    date        = models.DateField()
    start_time  = models.TimeField()
    end_time    = models.TimeField()
    classroom   = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    semester    = models.CharField(max_length=10, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_exam'

    def __str__(self):
        return f'{self.course} - {self.exam_type} ({self.date})'


class ExamSeat(models.Model):
    exam     = models.ForeignKey(Exam, on_delete=models.CASCADE)
    student  = models.ForeignKey(Student, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = 'attendance_examseat'
        unique_together = ('exam', 'student')


class CourseEvaluation(models.Model):
    student  = models.ForeignKey(Student, on_delete=models.CASCADE)
    course   = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10)
    rating   = models.IntegerField(default=3)
    comment  = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_courseevaluation'
        unique_together = ('student', 'course', 'semester')

    def __str__(self):
        return f'{self.student} eval {self.course}'


# ─────────────────────────────────────────────────────────────────────────────
# System Config (key-value store for onboarding wizard settings)
# ─────────────────────────────────────────────────────────────────────────────
class SystemConfig(models.Model):
    key        = models.CharField(max_length=100, unique=True)
    value      = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_system_config'

    def __str__(self):
        return f'{self.key} = {self.value[:50]}'


# ─────────────────────────────────────────────────────────────────────────────
# Async Task tracker
# ─────────────────────────────────────────────────────────────────────────────
class AsyncTask(models.Model):
    STATUS_CHOICES = [('pending','Pending'),('running','Running'),('done','Done'),('failed','Failed')]
    task_id    = models.CharField(max_length=100, unique=True)
    task_type  = models.CharField(max_length=100)
    status     = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    result     = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attendance_asynctask'


# ─────────────────────────────────────────────────────────────────────────────
# User Profile (settings preferences per user)
# ─────────────────────────────────────────────────────────────────────────────
class UserProfile(models.Model):
    user                          = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # Privacy
    show_phone_to_peers           = models.BooleanField(default=True)
    show_email_to_peers           = models.BooleanField(default=True)
    show_attendance_to_coordinator = models.BooleanField(default=True)
    # Notifications
    email_notifications           = models.BooleanField(default=True)
    attendance_alerts             = models.BooleanField(default=True)
    ticket_updates                = models.BooleanField(default=True)
    weekly_summary                = models.BooleanField(default=False)
    # Security
    require_face_login            = models.BooleanField(default=False)
    last_password_change          = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'attendance_userprofile'

    def __str__(self):
        return f'Profile: {self.user.username}'
