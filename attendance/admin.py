from django.contrib import admin
from .models import (
    College, Course, Classroom, Role, User, UserRole,
    Teacher, Student, StudentBiometric, StudentFaceEmbedding,
    Schedule, Enrollment, AttendanceLog, AIAttendanceLog, Notification, Department,
    TeacherFaceEmbedding, TeacherAttendanceLog, GateEntryLog, LectureSession,
    CameraSource,
)


# 1. الأكاديميات والقاعات
@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display = ('college_id', 'college_name') # لاحظي استخدمنا college_id زي الموديل بالظبط
    search_fields = ('college_name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'credits')
    search_fields = ('title', 'course_code')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_busy') 
    list_filter = ('is_busy',)
    search_fields = ('name',)
# 2. المستخدمين والصلاحيات
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_degree', 'major', 'is_allowed_entry')
    list_filter = ('academic_degree', 'is_allowed_entry')
    search_fields = ('name', 'user__email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'student_code', 'department', 'is_allowed_entry')
    list_filter = ('department', 'is_allowed_entry') 
    search_fields = ('name', 'student_code')
# 3. المواعيد والتسجيل
@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('course', 'classroom', 'teacher', 'day_of_week', 'start_time', 'end_time')
    list_filter = ('day_of_week', 'classroom', 'course')
    search_fields = ('course__title', 'classroom__name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'classroom', 'semester')
    list_filter = ('semester', 'course')
    search_fields = ('student__name', 'course__title')

# 4. سجلات الحضور (الذكي واليدوي)
@admin.register(AIAttendanceLog)
class AIAttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'schedule', 'timestamp', 'confidence_score', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('student__name', 'schedule__course__title')

@admin.register(AttendanceLog)
class AttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'enrollment', 'timestamp', 'status')
    list_filter = ('status', 'timestamp')
    search_fields = ('student__name',)

# 5. البيانات التقنية (Biometrics)
@admin.register(StudentFaceEmbedding)
class FaceEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('student',)
    readonly_fields = ('embedding',)

# سجلات الجلسات المباشرة (المحاضرات الشغالة الآن)
@admin.register(LectureSession)
class LectureSessionAdmin(admin.ModelAdmin):
    list_display = ('schedule', 'actual_start_time', 'is_active')
    list_filter = ('is_active', 'actual_start_time')

# سجلات البوابة الذكية
@admin.register(GateEntryLog)
class GateEntryLogAdmin(admin.ModelAdmin):
    list_display = ('user_name', 'user_type', 'entry_time', 'location')
    list_filter = ('user_type', 'entry_time')

# حضور الدكاترة وبصماتهم
@admin.register(TeacherAttendanceLog)
class TeacherAttendanceLogAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'check_in_time', 'status')
    list_filter = ('status', 'check_in_time')

@admin.register(TeacherFaceEmbedding)
class TeacherFaceEmbeddingAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'updated_at')

# تسجيل الباقي بشكل بسيط
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(StudentBiometric)
admin.site.register(Notification)

@admin.register(CameraSource)
class CameraSourceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'source', 'location', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'location', 'source')
    list_editable = ('is_active',)
from .models import (
    AuditLog, Coordinator, FinancialStatus, Grade,
    SupportTicket, TicketResponse, ExcuseRequest,
    ExamSchedule, ExamSeat, CourseEvaluation, AsyncTask,
    SystemConfig, UserProfile, FaceLoginSession,
    ClassroomPermission,
)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'actor', 'action', 'target_model', 'target_id', 'ip_address')
    list_filter   = ('action', 'target_model')
    search_fields = ('actor__username', 'description', 'target_id')
    readonly_fields = ('actor', 'action', 'target_model', 'target_id', 'description', 'ip_address', 'timestamp')
    ordering = ['-timestamp']

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display  = ('name', 'college', 'university_email', 'is_active')
    list_filter   = ('college', 'is_active')
    search_fields = ('name', 'university_email')

@admin.register(FinancialStatus)
class FinancialStatusAdmin(admin.ModelAdmin):
    list_display  = ('student', 'is_paid', 'balance_due', 'semester', 'last_payment_date')
    list_filter   = ('is_paid', 'semester')
    search_fields = ('student__name', 'student__student_code')
    list_editable = ('is_paid', 'balance_due')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'semester', 'midterm_grade', 'final_grade', 'total_grade', 'letter_grade')
    list_filter   = ('semester', 'letter_grade', 'course')
    search_fields = ('student__name', 'course__title')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display  = ('id', 'subject', 'requester', 'ticket_type', 'priority', 'status', 'created_at')
    list_filter   = ('status', 'priority', 'ticket_type')
    search_fields = ('subject', 'requester__username', 'description')
    list_editable = ('status', 'priority')

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display  = ('ticket', 'responder', 'created_at', 'is_internal')
    list_filter   = ('is_internal',)

@admin.register(ExcuseRequest)
class ExcuseRequestAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'absence_date', 'excuse_type', 'status', 'created_at')
    list_filter   = ('status', 'excuse_type')
    search_fields = ('student__name', 'course__title')
    list_editable = ('status',)

@admin.register(ExamSchedule)
class ExamScheduleAdmin(admin.ModelAdmin):
    list_display  = ('course', 'classroom', 'exam_type', 'exam_date', 'start_time', 'end_time', 'semester')
    list_filter   = ('exam_type', 'semester', 'exam_date')
    search_fields = ('course__title', 'classroom__name')

@admin.register(ExamSeat)
class ExamSeatAdmin(admin.ModelAdmin):
    list_display  = ('exam_schedule', 'student', 'seat_number', 'verified', 'verified_at')
    list_filter   = ('verified',)
    search_fields = ('student__name', 'seat_number')

@admin.register(CourseEvaluation)
class CourseEvaluationAdmin(admin.ModelAdmin):
    list_display  = ('course', 'teacher', 'student', 'semester', 'overall', 'submitted_at')
    list_filter   = ('semester', 'overall')
    search_fields = ('course__title', 'teacher__name')
    readonly_fields = ('student', 'course', 'teacher', 'semester')

@admin.register(AsyncTask)
class AsyncTaskAdmin(admin.ModelAdmin):
    list_display  = ('task_name', 'status', 'created_by', 'created_at', 'finished_at')
    list_filter   = ('status',)
    readonly_fields = ('created_at', 'started_at', 'finished_at')

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display  = ('key', 'value', 'updated_at')
    search_fields = ('key',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display  = ('user', 'email_notifications', 'require_face_login', 'two_factor_enabled')
    list_filter   = ('email_notifications', 'require_face_login')

@admin.register(FaceLoginSession)
class FaceLoginSessionAdmin(admin.ModelAdmin):
    list_display  = ('auth_user', 'login_time', 'user_type', 'confidence_score')
    list_filter   = ('user_type',)

@admin.register(ClassroomPermission)
class ClassroomPermissionAdmin(admin.ModelAdmin):
    list_display  = ('teacher', 'classroom', 'batch', 'allowed_from', 'allowed_until')

# Customize Django admin site header
admin.site.site_header  = 'SHAMEL University — Admin'
admin.site.site_title   = 'SHAMEL Admin'
admin.site.index_title  = 'System Administration'
