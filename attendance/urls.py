from django.urls import path
from . import views

urlpatterns = [
    path('scan/', views.scan_page, name='scan_page'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('check-status/', views.check_status, name='check_status'),
    path('recent-scans/', views.recent_scans, name='recent_scans'),
    path('live-stats/', views.live_stats, name='live_stats'),
    path('attendance-logs/', views.attendance_logs, name='attendance_logs'),
    path('login/', views.login_view, name='login'),
    path('login/face/', views.face_login, name='face_login'),
    path('logout/', views.logout_view, name='logout'),
    path('faculty-management/', views.faculty_management, name='faculty_management'),
    path('reports/', views.reports_view, name='reports_view'),
    path('attendance-success/', views.attendance_success, name='attendance_success'),
    path('attendance-error/', views.attendance_error, name='attendance_error'),
    path('professor-dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('admin-panel/', views.admin_control_panel, name='admin_panel'),
    path('admin-panel/gate-reports/', views.gate_reports, name='gate_reports'),
    path('admin-panel/notifications/', views.admin_notifications, name='admin_notifications'),
    path('stop-session/<int:session_id>/', views.stop_session, name='stop_session'),
    path('search/', views.global_search, name='global_search'),
    path('settings/', views.settings_view, name='settings_page'),
    path('settings/update/', views.update_settings, name='update_settings'),
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

    # Student views
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/support/', views.student_support, name='student_support'),

    # Teacher views
    path('teacher/open-session/<int:schedule_id>/', views.open_session, name='open_session'),
    path('teacher/timeline/', views.teacher_timeline, name='teacher_timeline'),
    path('teacher/attendance-records/', views.teacher_attendance_records, name='teacher_attendance_records'),
    path('teacher/profile/', views.teacher_profile_view, name='teacher_profile'),
    path('teacher/permissions/', views.teacher_permissions_view, name='teacher_permissions'),

    # Coordinator views
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/students/', views.coordinator_students, name='coordinator_students'),
    path('coordinator/faculty/', views.coordinator_faculty, name='coordinator_faculty'),
    path('coordinator/assignments/', views.coordinator_course_assignment, name='coordinator_course_assignment'),
    path('coordinator/register/', views.coordinator_register_user, name='coordinator_register_user'),
    path('coordinator/grading/', views.coordinator_grading, name='coordinator_grading'),
    path('coordinator/export-students/', views.export_coordinator_students_csv, name='export_coordinator_csv'),

    # Shared views
    path('classrooms/status/', views.classrooms_status_view, name='classrooms_status'),

    # PDF exports
    path('reports/students/pdf/', views.export_student_report_pdf, name='export_student_pdf'),
    path('reports/teachers/pdf/', views.export_teacher_report_pdf, name='export_teacher_pdf'),
    path('reports/grades/pdf/', views.export_grades_pdf, name='export_grades_pdf'),
]
