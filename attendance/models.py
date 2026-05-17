from django.db import models
from django.contrib.auth.models import User as AuthUser

# 1. الإداريات
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    college = models.ForeignKey('College', on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class Notification(models.Model):
    TYPES = (('info', 'info'), ('success', 'success'), ('warning', 'warning'), ('error', 'error'))
    user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    notif_type = models.CharField(max_length=10, choices=TYPES, default='info')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta: ordering = ['-created_at']

class College(models.Model):
    college_id = models.AutoField(primary_key=True)
    college_name = models.TextField()
    name = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self): return self.college_name

# 2. القاعات والمواد
class Course(models.Model):
    id = models.AutoField(primary_key=True)
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    credits = models.IntegerField()
    college = models.ForeignKey('College', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    total_hours = models.IntegerField(default=3)
    COURSE_TYPES = (('Mandatory', 'إلزامي'), ('Optional', 'اختياري'))
    course_type = models.CharField(max_length=50, choices=COURSE_TYPES, default='Mandatory')
    def __str__(self): return f"{self.course_code} - {self.title}"

class Classroom(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    is_busy = models.BooleanField(default=False) # أضفناه للآدمن
    is_occupied = models.BooleanField(default=False) 
    capacity = models.IntegerField(default=50)
    CLASSROOM_TYPES = (('Lecture', 'محاضرة'), ('Exam', 'امتحان'), ('Lab', 'مختبر'))
    classroom_type = models.CharField(max_length=50, choices=CLASSROOM_TYPES, default='Lecture')
    floor = models.CharField(max_length=10, null=True, blank=True)
    building = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self): return f"{self.name} ({self.location})"

# 3. الأدوار والمستخدمين
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    role_name = models.CharField(max_length=50)
    def __str__(self): return self.role_name

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password_hash = models.BinaryField()
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.email

class UserRole(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

# 4. الدكاترة والطلاب
class Teacher(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    academic_degree = models.CharField(max_length=100)
    major = models.CharField(max_length=100)
    is_allowed_entry = models.BooleanField(default=True) # أضفناه للآدمن
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    university_email = models.EmailField(unique=True, null=True, blank=True)
    blood_type = models.CharField(max_length=5, null=True, blank=True)
    specialization_type = models.CharField(max_length=100, null=True, blank=True)
    college = models.ForeignKey('College', on_delete=models.SET_NULL, null=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    profile_photo = models.ImageField(upload_to='teacher_profiles/', null=True, blank=True)
    def __str__(self): return self.name

class Student(models.Model):
    id = models.AutoField(primary_key=True)
    student_code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    encrypted_data = models.BinaryField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    is_allowed_entry = models.BooleanField(default=True) # أضفناه للآدمن
    is_trained = models.BooleanField(default=False)
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    university_email = models.EmailField(unique=True, null=True, blank=True)
    blood_type = models.CharField(max_length=5, null=True, blank=True)
    is_medically_fit = models.BooleanField(default=True)
    medical_notes = models.TextField(null=True, blank=True)
    is_registered = models.BooleanField(default=False)
    batch = models.CharField(max_length=20, default="2024")
    semester = models.CharField(max_length=20, default="1")
    profile_photo = models.ImageField(upload_to='student_profiles/', null=True, blank=True)
    def __str__(self): return self.name

# 5. جداول الدكاترة والبصمات (التي كانت ناقصة)
class TeacherFaceEmbedding(models.Model):
    teacher = models.OneToOneField(Teacher, on_delete=models.CASCADE)
    face_vector = models.TextField() 
    updated_at = models.DateTimeField(auto_now=True)

class TeacherAttendanceLog(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='Present')

class StudentBiometric(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    face_vector = models.TextField()

class StudentFaceEmbedding(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    embedding = models.TextField()

# 6. الجداول والانتساب
class Schedule(models.Model):
    DAYS = [('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')]
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10, choices=DAYS)
    start_time = models.TimeField()
    end_time = models.TimeField()
    batch = models.CharField(max_length=20, default="2024")
    total_lectures_required = models.IntegerField(default=12)
    semester = models.CharField(max_length=20, default="1")
    def __str__(self): return f"{self.course.title} - {self.day_of_week}"

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)

# 7. سجلات الحضور والبوابة
class AttendanceLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    status = models.CharField(max_length=20)
    class Meta: verbose_name = "Manual Attendance Log"

class AIAttendanceLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    confidence_score = models.FloatField()
    status = models.CharField(max_length=20, default='Present')

class LectureSession(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    actual_start_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(null=True, blank=True)
    topic = models.CharField(max_length=255, null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    timer_duration = models.IntegerField(null=True, blank=True)

class GateEntryLog(models.Model):
    user_name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=50) 
    entry_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, default='Main Gate')

# --- 3. Completely NEW Models ---

class Coordinator(models.Model):
    auth_user = models.OneToOneField(AuthUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    college = models.ForeignKey(College, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20)
    university_email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

class FinancialStatus(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    balance_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_payment_date = models.DateField(null=True, blank=True)
    semester = models.CharField(max_length=20)
    notes = models.TextField(blank=True, null=True)

class Grade(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    midterm_grade = models.FloatField(null=True, blank=True)
    final_grade = models.FloatField(null=True, blank=True)
    attendance_grade = models.FloatField(null=True, blank=True)
    total_grade = models.FloatField(null=True, blank=True)
    letter_grade = models.CharField(max_length=2, null=True, blank=True)
    entered_by = models.ForeignKey(Coordinator, on_delete=models.SET_NULL, null=True)
    entered_at = models.DateTimeField(auto_now_add=True)

class SupportTicket(models.Model):
    requester = models.ForeignKey(AuthUser, on_delete=models.CASCADE, related_name='submitted_tickets')
    subject = models.CharField(max_length=255)
    REQ_TYPES = (('Email', 'تغيير إيميل'), ('Password', 'تغيير باسورد'), ('ID', 'تغيير ID'))
    request_type = models.CharField(max_length=50, choices=REQ_TYPES)
    description = models.TextField()
    STATUS_CHOICES = (('open', 'مفتوح'), ('in_progress', 'قيد المعالجة'), ('resolved', 'محلول'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_by = models.ForeignKey(AuthUser, on_delete=models.SET_NULL, null=True, related_name='resolved_tickets')
    resolved_at = models.DateTimeField(null=True, blank=True)

class ClassroomPermission(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    batch = models.CharField(max_length=20)
    allowed_from = models.TimeField()
    allowed_until = models.TimeField()

class FaceLoginSession(models.Model):
    auth_user = models.ForeignKey(AuthUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(max_length=50)
    confidence_score = models.FloatField()