from django.contrib import admin
from .models import (
    College, Department, Classroom, Course,
    Teacher, Student, Coordinator,
    Schedule, Enrollment, LectureSession,
    AIAttendanceLog, StudentFaceEmbedding, TeacherFaceEmbedding,
    CameraSource, GateLog,
    Notification, SupportTicket,
    FinancialStatus, AuditLog,
    MedicalExcuse, Exam, ExamSeat, CourseEvaluation,
    SystemConfig, AsyncTask,
)

# ── College / Department / Classroom ─────────────────────────────────────────

@admin.register(College)
class CollegeAdmin(admin.ModelAdmin):
    list_display  = ('college_id', 'college_name')
    search_fields = ('college_name',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('id', 'name', 'college')
    list_filter   = ('college',)
    search_fields = ('name',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display  = ('name', 'location', 'capacity', 'classroom_type', 'is_busy')
    list_filter   = ('classroom_type', 'is_busy')
    search_fields = ('name', 'location')

# ── Course ────────────────────────────────────────────────────────────────────

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('course_code', 'title', 'credits', 'college', 'department', 'year_level')
    list_filter   = ('college', 'department', 'year_level')
    search_fields = ('title', 'course_code')

# ── People ────────────────────────────────────────────────────────────────────

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display  = ('name', 'academic_degree', 'major', 'college', 'department', 'is_allowed_entry')
    list_filter   = ('academic_degree', 'college', 'is_allowed_entry')
    search_fields = ('name', 'university_email')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ('student_code', 'name', 'department', 'batch', 'is_registered', 'is_allowed_entry')
    list_filter   = ('department', 'is_registered', 'is_allowed_entry')
    search_fields = ('name', 'student_code', 'university_email')

@admin.register(Coordinator)
class CoordinatorAdmin(admin.ModelAdmin):
    list_display  = ('name', 'college', 'university_email')
    list_filter   = ('college',)
    search_fields = ('name', 'university_email')

# ── Schedule / Enrollment / Sessions ─────────────────────────────────────────

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display  = ('course', 'teacher', 'classroom', 'day_of_week', 'start_time', 'end_time', 'semester')
    list_filter   = ('day_of_week', 'semester')
    search_fields = ('course__title', 'teacher__name', 'classroom__name')

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display  = ('student', 'course', 'classroom', 'semester', 'enrolled_at')
    list_filter   = ('semester', 'course')
    search_fields = ('student__name', 'course__title')

@admin.register(LectureSession)
class LectureSessionAdmin(admin.ModelAdmin):
    list_display  = ('id', 'schedule', 'is_active', 'actual_start_time', 'actual_end_time', 'opened_by')
    list_filter   = ('is_active',)
    search_fields = ('schedule__course__title',)

# ── Attendance & Embeddings ───────────────────────────────────────────────────

@admin.register(AIAttendanceLog)
class AIAttendanceLogAdmin(admin.ModelAdmin):
    list_display  = ('student', 'schedule', 'timestamp', 'status', 'confidence_score', 'method')
    list_filter   = ('status', 'method')
    search_fields = ('student__name', 'schedule__course__title')
    date_hierarchy = 'timestamp'

@admin.register(StudentFaceEmbedding)
class StudentFaceEmbeddingAdmin(admin.ModelAdmin):
    list_display  = ('student', 'created_at', 'updated_at')
    readonly_fields = ('embedding',)

@admin.register(TeacherFaceEmbedding)
class TeacherFaceEmbeddingAdmin(admin.ModelAdmin):
    list_display  = ('teacher', 'created_at', 'updated_at')
    readonly_fields = ('face_vector',)

# ── Camera / Gate ─────────────────────────────────────────────────────────────

@admin.register(CameraSource)
class CameraSourceAdmin(admin.ModelAdmin):
    list_display  = ('name', 'source', 'location', 'is_active', 'is_gate')
    list_filter   = ('is_active', 'is_gate')
    list_editable = ('is_active',)
    search_fields = ('name', 'location')

@admin.register(GateLog)
class GateLogAdmin(admin.ModelAdmin):
    list_display  = ('person_name', 'student', 'teacher', 'status', 'timestamp', 'camera')
    list_filter   = ('status',)
    search_fields = ('person_name',)
    date_hierarchy = 'timestamp'

# ── Notifications / Tickets ───────────────────────────────────────────────────

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'level', 'is_read', 'created_at')
    list_filter   = ('level', 'is_read')
    search_fields = ('user__username', 'title')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display  = ('id', 'subject', 'user', 'status', 'priority', 'created_at')
    list_filter   = ('status', 'priority')
    list_editable = ('status', 'priority')
    search_fields = ('subject', 'user__username')
    date_hierarchy = 'created_at'

# ── Financial / Grades / Audit ────────────────────────────────────────────────

@admin.register(FinancialStatus)
class FinancialStatusAdmin(admin.ModelAdmin):
    list_display  = ('student', 'status', 'amount_due', 'amount_paid', 'updated_at')
    list_filter   = ('status',)
    search_fields = ('student__name', 'student__student_code')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'user', 'action', 'target_model', 'target_id', 'ip_address')
    list_filter   = ('action', 'target_model')
    search_fields = ('user__username', 'description', 'target_id')
    readonly_fields = ('user', 'action', 'target_model', 'target_id', 'description', 'ip_address', 'timestamp')
    date_hierarchy = 'timestamp'

# ── Exams / Excuses / Evaluations ─────────────────────────────────────────────

@admin.register(MedicalExcuse)
class MedicalExcuseAdmin(admin.ModelAdmin):
    list_display  = ('student', 'schedule', 'status', 'submitted_at', 'reviewed_by')
    list_filter   = ('status',)
    search_fields = ('student__name',)

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display  = ('course', 'exam_type', 'date', 'start_time', 'end_time', 'classroom', 'semester')
    list_filter   = ('exam_type', 'semester')
    search_fields = ('course__title',)
    date_hierarchy = 'date'

@admin.register(ExamSeat)
class ExamSeatAdmin(admin.ModelAdmin):
    list_display  = ('exam', 'student', 'seat_number')
    search_fields = ('student__name',)

@admin.register(CourseEvaluation)
class CourseEvaluationAdmin(admin.ModelAdmin):
    list_display  = ('course', 'student', 'semester', 'rating', 'submitted_at')
    list_filter   = ('semester', 'rating')
    search_fields = ('course__title', 'student__name')
    readonly_fields = ('student', 'course', 'semester')

# ── System ────────────────────────────────────────────────────────────────────

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display  = ('key', 'value', 'updated_at')
    search_fields = ('key',)

@admin.register(AsyncTask)
class AsyncTaskAdmin(admin.ModelAdmin):
    list_display  = ('task_id', 'task_type', 'status', 'created_at', 'updated_at')
    list_filter   = ('status', 'task_type')
    readonly_fields = ('task_id', 'created_at', 'updated_at')

# ── Admin site branding ───────────────────────────────────────────────────────
admin.site.site_header = 'SHAMEL University — Admin'
admin.site.site_title  = 'SHAMEL Admin'
admin.site.index_title = 'System Administration'
