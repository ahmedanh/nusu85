from django.contrib import admin
from .models import (
    College, Course, Classroom, Role, User, UserRole, 
    Teacher, Student, StudentBiometric, StudentFaceEmbedding, 
    Schedule, Enrollment, AttendanceLog, AIAttendanceLog, Notification ,Department ,TeacherFaceEmbedding, TeacherAttendanceLog, GateEntryLog, LectureSession 
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