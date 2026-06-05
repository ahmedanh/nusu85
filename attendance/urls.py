from django.urls import path
from . import views
from . import api
from . import api_extra as apix

urlpatterns = [
    # ── Native-app REST API (JSON, token auth) ──────────────────────────
    path('api/v1/health',              api.health,                 name='api_health'),
    path('api/v1/auth/login',          api.login,                  name='api_login'),
    path('api/v1/me',                  api.me,                     name='api_me'),
    path('api/v1/dashboard',           api.dashboard,              name='api_dashboard'),
    path('api/v1/schedule',            api.schedule,               name='api_schedule'),
    path('api/v1/reports/summary',     api.reports_summary,        name='api_reports_summary'),
    path('api/v1/notifications',       api.notifications,          name='api_notifications'),
    path('api/v1/notifications/read',  api.mark_notifications_read, name='api_notifs_read'),
    path('api/v1/scan',                api.scan_submit,            name='api_scan_submit'),
    # ── Full section coverage (mirrors every web urlpattern) ────────────
    path('api/v1/courses',             apix.courses,               name='api_courses'),
    path('api/v1/courses/create',      apix.course_create,         name='api_course_create'),
    path('api/v1/classrooms',          apix.classrooms,            name='api_classrooms'),
    path('api/v1/classrooms/status',   apix.classrooms_status,     name='api_classrooms_status'),
    path('api/v1/classrooms/create',   apix.classroom_create,      name='api_classroom_create'),
    path('api/v1/departments',         apix.departments,           name='api_departments_v1'),
    path('api/v1/teachers',            apix.teachers,              name='api_teachers'),
    path('api/v1/teachers/<int:tid>',  apix.teacher_detail,        name='api_teacher_detail'),
    path('api/v1/students',            apix.students,              name='api_students'),
    path('api/v1/students/<int:sid>',  apix.student_detail,        name='api_student_detail'),
    path('api/v1/tickets',             apix.tickets,               name='api_tickets'),
    path('api/v1/tickets/create',      apix.ticket_create,         name='api_ticket_create'),
    path('api/v1/attendance-logs',     apix.attendance_logs,       name='api_attendance_logs'),
    path('api/v1/gate-logs',           apix.gate_logs,             name='api_gate_logs'),
    path('api/v1/audit-log',           apix.audit_log,             name='api_audit_log'),
    path('api/v1/exams',               apix.exams,                 name='api_exams'),
    path('api/v1/search',              apix.search,                name='api_search'),
    path('api/v1/settings',            apix.app_settings,          name='api_settings'),
    path('api/v1/coordinator/students', apix.coordinator_students, name='api_coord_students'),
    path('api/v1/gate/toggle-access',  apix.toggle_access,         name='api_toggle_access'),
    path('api/v1/dean-evaluations',    apix.dean_evaluations,      name='api_dean_evals'),
    path('api/v1/grades',              apix.grades,                name='api_grades'),
    path('api/v1/excuses',             apix.excuses,               name='api_excuses'),
    path('api/v1/tickets/<int:tid>',   apix.ticket_detail,         name='api_ticket_detail'),
    path('api/v1/teacher/timeline',    apix.teacher_timeline,      name='api_teacher_timeline'),
    path('api/v1/gate-reports',        apix.gate_reports,          name='api_gate_reports'),

    # Home redirect / unified login
    path('', views.login_view, name='home'),

    # Scanning / Camera
    path('scan/', views.scan_page, name='scan_page'),
    path('video_feed/', views.video_feed, name='video_feed'),
    path('stop_camera/', views.stop_camera, name='stop_camera'),
    path('check-status/', views.check_status, name='check_status'),
    path('recent-scans/', views.recent_scans, name='recent_scans'),
    path('live-stats/', views.live_stats, name='live_stats'),
    path('attendance-logs/', views.attendance_logs, name='attendance_logs'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('login/face/', views.face_login, name='face_login'),
    path('logout/', views.logout_view, name='logout'),
    path('demo-login/', views.demo_login, name='demo_login'),

    # Attendance feedback pages
    path('attendance-success/', views.attendance_success, name='attendance_success'),
    path('attendance-error/', views.attendance_error, name='attendance_error'),

    # Admin panel
    path('admin-panel/', views.admin_control_panel, name='admin_panel'),
    path('admin-panel/gate-reports/', views.gate_reports, name='gate_reports'),
    path('admin-panel/notifications/', views.admin_notifications, name='admin_notifications'),
    path('admin-panel/audit-log/', views.audit_log_view, name='audit_log'),
    path('admin-panel/departments/', views.departments_view, name='departments_view'),
    path('admin-panel/onboarding/', views.onboarding_wizard, name='onboarding_wizard'),
    path('admin-panel/dean-evaluation/', views.dean_evaluation_dashboard, name='dean_evaluation_dashboard'),
    path('admin-panel/faculty-timeline/', views.faculty_timeline, name='faculty_timeline'),
    path('admin-panel/excuse-board/', views.excuse_approval_board, name='excuse_approval_board'),
    path('admin-panel/exam-planner/', views.exam_planner, name='exam_planner'),
    path('admin-panel/exam-seating/', views.exam_seating_chart, name='exam_seating_chart'),
    path('admin-panel/exam-gate/', views.exam_gate_verify, name='exam_gate_verify'),
    path('admin-panel/tickets/', views.admin_tickets, name='admin_tickets'),

    # Faculty management
    path('faculty-management/', views.faculty_management, name='faculty_management'),
    path('faculty-management/register-student/', views.register_student, name='register_student'),
    path('faculty-management/register-teacher/', views.register_teacher, name='register_teacher'),

    # Reports
    path('reports/', views.reports_view, name='reports_view'),
    path('reports/students/', views.student_attendance_report, name='student_report'),
    path('reports/students/export/csv/', views.export_student_attendance_csv, name='export_student_csv'),
    path('reports/students/export/excel/', views.export_attendance_excel, name='export_attendance_excel'),
    path('reports/students/export/pdf/', views.export_student_report_pdf, name='export_student_pdf'),
    path('reports/teachers/', views.teacher_attendance_report, name='teacher_report'),
    path('reports/teachers/export/csv/', views.export_teacher_report_csv, name='export_teacher_csv'),
    path('reports/teachers/export/pdf/', views.export_teacher_report_pdf, name='export_teacher_pdf'),
    path('reports/grades/export/pdf/', views.export_grades_pdf, name='export_grades_pdf'),
    path('reports/analytics/export/pdf/', views.export_analytics_pdf, name='export_analytics_pdf'),
    path('search/export/pdf/', views.export_search_pdf, name='export_search_pdf'),

    # Search
    path('search/', views.global_search, name='global_search'),

    # Settings
    path('settings/', views.settings_view, name='settings_page'),
    path('settings/update/', views.update_settings, name='update_settings'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications_view'),
    path('notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),

    # Support Tickets
    path('tickets/', views.tickets_list, name='tickets_list'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    # Professor / Teacher dashboard
    path('professor-dashboard/', views.professor_dashboard, name='professor_dashboard'),
    path('teacher/open-session/<int:schedule_id>/', views.open_session, name='open_session'),
    path('teacher/timeline/', views.teacher_timeline, name='teacher_timeline'),
    path('teacher/attendance-records/', views.teacher_attendance_records, name='teacher_attendance_records'),
    path('teacher/profile/', views.teacher_profile_view, name='teacher_profile'),
    path('teacher/permissions/', views.teacher_permissions_view, name='teacher_permissions'),
    path('teachers/<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('teachers/<int:teacher_id>/edit/', views.edit_teacher, name='edit_teacher'),

    # Student views
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('student/courses/', views.student_courses, name='student_courses'),
    path('student/support/', views.student_support, name='student_support'),
    path('student/schedule/', views.student_schedule_view, name='student_schedule'),
    path('student/excuse/', views.excuse_portal, name='excuse_portal'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/<int:student_id>/edit/', views.edit_student, name='edit_student'),

    # Coordinator views
    path('coordinator/dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('coordinator/students/', views.coordinator_students, name='coordinator_students'),
    path('coordinator/faculty/', views.coordinator_faculty, name='coordinator_faculty'),
    path('coordinator/assignments/', views.coordinator_course_assignment, name='coordinator_course_assignment'),
    path('coordinator/register/', views.coordinator_register_user, name='coordinator_register_user'),
    path('coordinator/grading/', views.coordinator_grading, name='coordinator_grading'),
    path('coordinator/export-students/', views.export_coordinator_students_csv, name='export_coordinator_csv'),

    # Courses
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/add/', views.add_course, name='add_course'),
    path('courses/<int:course_id>/edit/', views.edit_course, name='edit_course'),
    path('courses/<int:course_id>/delete/', views.delete_course, name='delete_course'),

    # Classrooms
    path('classrooms/', views.classrooms_list, name='classrooms_list'),
    path('classrooms/status/', views.classrooms_status_view, name='classrooms_status'),
    path('classrooms/add/', views.add_classroom, name='add_classroom'),
    path('classrooms/<int:classroom_id>/edit/', views.edit_classroom, name='edit_classroom'),
    path('classrooms/<int:classroom_id>/delete/', views.delete_classroom, name='delete_classroom'),

    # Schedule
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/add/', views.add_schedule, name='add_schedule'),
    path('schedule/<int:schedule_id>/edit/', views.edit_schedule, name='edit_schedule'),
    path('schedule/<int:schedule_id>/delete/', views.delete_schedule, name='delete_schedule'),
    path('schedule/calendar/', views.schedule_calendar, name='schedule_calendar'),
    path('schedule/calendar/add-slot/', views.calendar_add_slot, name='calendar_add_slot'),
    path('schedule/calendar/delete-slot/<int:schedule_id>/', views.calendar_delete_slot, name='calendar_delete_slot'),
    path('attendance/check-warnings/', views.check_attendance_warnings, name='check_attendance_warnings'),

    # Face enrollment
    path('enroll-face/', views.enroll_face, name='enroll_face'),
    path('enroll-face/<str:person_type>/<int:person_id>/', views.enroll_face, name='enroll_face_person'),
    path('user/<str:user_type>/<int:user_id>/upload-face/', views.upload_face, name='upload_face'),

    # Gate
    path('gate/', views.gate_page, name='gate_page'),
    path('toggle-access/<str:user_type>/<int:user_id>/', views.toggle_user_access, name='toggle_access'),

    # API endpoints
    path('api/chancellor-stats/', views.get_chancellor_stats, name='chancellor_stats_api'),
    path('api/departments/', views.api_departments, name='api_departments'),
    path('api/student-search/', views.api_student_search, name='api_student_search'),
    path('api/check-conflict/', views.api_check_conflict, name='api_check_conflict'),

    # CSV exports
    path('export/teachers/', views.export_teachers_csv, name='export_teachers'),
    path('dashboard/export-courses/', views.export_my_courses_csv, name='export_my_courses'),

    # Stop session
    path('stop-session/<int:session_id>/', views.stop_session, name='stop_session'),

    # PWA
    path('sw.js',    views.pwa_sw,      name='pwa_sw'),
    path('offline/', views.pwa_offline,  name='pwa_offline'),
    path('manifest.json', views.pwa_manifest, name='pwa_manifest'),

    # Live Reload (called by deploy script)
    path('api/live-reload/', views.trigger_live_reload, name='live_reload_trigger'),
    path('api/ping/', views.api_ping, name='api_ping'),
    path('api/cameras/', views.api_list_cameras, name='api_list_cameras'),
]
