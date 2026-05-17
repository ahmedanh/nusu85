from django.urls import path
from . import views

urlpatterns = [
    # الصفحة الأساسية لعملية الفحص (الواجهة)
    path('scan/', views.scan_page, name='scan_page'),
    
    # بث الفيديو المباشر من الكاميرا
    path('video_feed/', views.video_feed, name='video_feed'),
    
    # مسارات الـ AJAX لتحديث البيانات بدون تحميل الصفحة
    path('check-status/', views.check_status, name='check_status'),
    path('recent-scans/', views.recent_scans, name='recent_scans'),
    path('live-stats/', views.live_stats, name='live_stats'), 
    
    # صفحات عرض السجلات والدخول
    path('attendance-logs/', views.attendance_logs, name='attendance_logs'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('faculty-management/', views.faculty_management, name='faculty_management'),
    path('reports/', views.reports_view, name='reports_view'),
    path('attendance-success/', views.attendance_success, name='attendance_success'),
    path('attendance-error/', views.attendance_error, name='attendance_error'),
    path('professor-dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('admin-panel/', views.admin_control_panel, name='admin_panel'),
    path('stop-session/<int:session_id>/', views.stop_session, name='stop_session'),
    path('search/', views.global_search, name='global_search'),
    path('settings/', views.settings_view, name='settings_page'), # لعرض الصفحة
    path('settings/update/', views.update_settings, name='update_settings'), # لمعالجة حفظ البيانات
    path('api/chancellor-stats/', views.get_chancellor_stats, name='chancellor_stats_api'),
    path('export/teachers/', views.export_teachers_csv, name='export_teachers'),
    path('user/<str:user_type>/<int:user_id>/upload-face/', views.upload_face, name='upload_face'),
    path('gate/', views.gate_page, name='gate_page'),
    path('toggle-access/<str:user_type>/<int:user_id>/', views.toggle_user_access, name='toggle_access'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('reports/students/', views.student_attendance_report, name='student_report'),
    path('reports/students/export/', views.export_student_attendance_csv, name='export_student_csv'),
    path('reports/teachers/', views.teacher_attendance_report, name='teacher_report'),
    path('reports/teachers/export/', views.export_teacher_report_csv, name='export_teacher_csv'),
    path('dashboard/export-courses/', views.export_my_courses_csv, name='export_my_courses'),
    
    # Phase 3: Student & Teacher Views
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/support/', views.student_support, name='student_support'),
    
    path('teacher/open-session/<int:schedule_id>/', views.open_session, name='open_session'),
    path('teacher/timeline/', views.teacher_timeline, name='teacher_timeline'),
    path('teacher/attendance-records/', views.teacher_attendance_records, name='teacher_attendance_records'),
    
    # Phase 4: Coordinator Views
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/students/', views.coordinator_students, name='coordinator_students'),
    path('coordinator/faculty/', views.coordinator_faculty, name='coordinator_faculty'),
    path('coordinator/assignments/', views.coordinator_course_assignment, name='coordinator_course_assignment'),
    path('coordinator/register/', views.coordinator_register_user, name='coordinator_register_user'),
]