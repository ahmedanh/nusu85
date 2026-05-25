const {Document,Packer,Paragraph,TextRun,Table,TableRow,TableCell,HeadingLevel,AlignmentType,BorderStyle,WidthType,ShadingType,Header,Footer,PageNumber,LevelFormat,PageBreak}=require('/sessions/vigilant-loving-clarke/lib/node_modules/docx');
const fs=require('fs');
const C={primary:'1E40AF',secondary:'0F766E',danger:'DC2626',success:'16A34A',gray:'64748B',light:'F1F5F9',hdr:'1E3A5F',white:'FFFFFF'};
const b={style:BorderStyle.SINGLE,size:1,color:'D1D5DB'};
const bs={top:b,bottom:b,left:b,right:b};
function cell(t,o={}){const{bold=false,color='1E293B',bg='FFFFFF',w=2340,sz=19,al=AlignmentType.LEFT}=o;return new TableCell({borders:bs,width:{size:w,type:WidthType.DXA},shading:{fill:bg,type:ShadingType.CLEAR},margins:{top:80,bottom:80,left:110,right:110},children:[new Paragraph({alignment:al,children:[new TextRun({text:String(t),font:'Arial',size:sz,bold,color})]})]})}
function hcell(t,w=2340){return cell(t,{bold:true,color:C.white,bg:C.hdr,w,sz:19})}
function tbl(rows,cols){return new Table({width:{size:9360,type:WidthType.DXA},columnWidths:cols,rows})}
function hd(t,lv=HeadingLevel.HEADING_1,co=C.primary){return new Paragraph({heading:lv,spacing:{before:lv===HeadingLevel.HEADING_1?400:220,after:100},children:[new TextRun({text:t,bold:true,color:co,font:'Arial',size:lv===HeadingLevel.HEADING_1?34:26})]})}
function p(t,o={}){return new Paragraph({spacing:{before:50,after:50},children:[new TextRun({text:t,font:'Arial',size:21,...o})]})}
function pb(){return new Paragraph({children:[new PageBreak()]})}

const py=[
  ['manage.py',21,'NO','Django management entry point (runserver, migrate, shell)'],
  ['acdc_config/__init__.py',0,'NO','Package init'],
  ['acdc_config/settings.py',198,'NO','Core settings: PostgreSQL, Channels, WhiteNoise, Celery, email'],
  ['acdc_config/urls.py',29,'NO','Root URL conf — mounts /attendance/, /admin/, password-reset'],
  ['acdc_config/asgi.py',21,'NO','ASGI config for Django Channels WebSocket (daphne/uvicorn)'],
  ['acdc_config/wsgi.py',16,'NO','WSGI config for HTTP deployment (gunicorn)'],
  ['attendance/__init__.py',0,'NO','App package init'],
  ['attendance/models.py',453,'NO','26 model classes (Student, Teacher, Enrollment, Attendance, FaceEmbedding/pgvector, Notification, Ticket, ExamPlan, GateLog…)'],
  ['attendance/views.py',2498,'NO','104 view functions: dashboards, CRUD, AI scan, gate, reports, exports, settings, notifications, tickets, search'],
  ['attendance/urls.py',137,'NO','91 URL patterns mapping to all 104 views'],
  ['attendance/admin.py',197,'NO','Django /admin/ registrations for all 26 models with custom list_display/filters'],
  ['attendance/apps.py',41,'NO','App config — loads face_recognition model on startup via AppConfig.ready()'],
  ['attendance/consumers.py',42,'NO','Django Channels WebSocket consumer — pushes live scan results to browser'],
  ['attendance/routing.py',7,'NO','Channels URL router: ws/scan/ → ScanConsumer'],
  ['attendance/context_processors.py',28,'NO','Injects unread_count, notifications, coordinator/teacher/student profile into every template'],
  ['attendance/context_processors_1.py',1,'YES — ORPHAN','Empty stub, not imported anywhere. Delete safely.'],
  ['attendance/notifications.py',30,'NO','notify_user() helper that creates Notification model records'],
  ['attendance/tasks.py',117,'NO','Celery tasks: email reports, daily summaries, cleanup, face re-index'],
  ['attendance/crypto_utils.py',37,'NO','AES-256 encrypt/decrypt for face embeddings (PyCryptodome)'],
  ['attendance/edge_cache.py',37,'NO','In-memory LRU cache for face embeddings — speeds up rapid scanning'],
  ['attendance/management/__init__.py',0,'NO','Package init'],
  ['attendance/management/commands/__init__.py',0,'NO','Package init'],
  ['attendance/management/commands/seed_demo.py',202,'YES (dev only)','Creates demo data for testing. Remove from production.'],
  ['create_templates.py',23,'YES','One-off scaffold script — already completed, not part of Django app'],
  ['generate_thesis.py',0,'YES','Empty file (0 bytes)'],
  ['generate_thesis_v2.py',42,'YES','Documentation utility — not part of Django app'],
  ['inspect_face.py',8,'YES','Dev-only face debug script'],
  ['test_cam.py',91,'YES','Dev-only camera test script'],
];

const models=[
  ['College','college_id, college_name, college_code','Has many: Department, Teacher, Course, Coordinator'],
  ['Department','id, name, college(FK)','Belongs to: College. Has many: Student, Teacher'],
  ['Student','id, name, student_code, gender, batch, is_registered, is_active, is_allowed_entry, university_email, phone_number, department(FK), face_image, auth_user(FK)','Has: Enrollment, Attendance, FaceEmbedding, GateLog, FinancialStatus(1:1), Ticket'],
  ['Teacher','teacher_id, name, academic_degree, major, gender, phone, university_email, is_allowed_entry, face_image, department(FK), college(FK), auth_user(FK)','Has: LectureSchedule, DeanEvaluation'],
  ['Coordinator','id, user(FK), college(FK), department(FK)','Belongs to: College, Department'],
  ['Course','course_id, title, course_code, year_level, college(FK), is_active, credit_hours','Has: LectureSchedule, Enrollment, CourseEvaluation'],
  ['Classroom','id, name, building, capacity, is_active, has_camera','Used by: LectureSchedule, ExamSeat'],
  ['LectureSchedule','id, course(FK), teacher(FK), classroom(FK), day_of_week, start_time, end_time, semester','Has: LectureSession, Enrollment'],
  ['LectureSession','id, schedule(FK), date, started_at, ended_at, is_active','Has: Attendance, AIAttendanceLog'],
  ['Enrollment','id, student(FK), schedule(FK), semester, is_active','Joins: Student ↔ LectureSchedule'],
  ['Attendance','id, student(FK), session(FK), status(Present/Absent/Late/Excused), timestamp, method','Belongs to: Student, LectureSession'],
  ['AIAttendanceLog','id, session(FK), recognized_student(FK), confidence, captured_at','Raw AI recognition log before confirmed Attendance'],
  ['FaceEmbedding','id, student(FK), embedding(VectorField 128-dim), enrolled_at, is_active','pgvector cosine similarity search for face match'],
  ['GateLog','id, student(FK), entry_type, timestamp, allowed, gate_number','Campus gate entry/exit records'],
  ['FinancialStatus','id, student(FK OneToOne), amount_due, amount_paid, status(Paid/Unpaid/Partial)','OneToOne with Student'],
  ['Notification','id, user(FK), title, body, level(info/warning/danger/success), is_read, created_at, link','In-app notifications; injected by context_processors.py'],
  ['Ticket','id, requester(FK), subject, description, status, category, priority, assigned_to(FK)','Has: TicketMessage'],
  ['TicketMessage','id, ticket(FK), sender(FK), body, sent_at, is_staff_reply','Threaded reply in a Ticket'],
  ['AuditLog','id, user(FK), action, model_name, object_id, timestamp, details(JSON)','Admin action audit trail'],
  ['ExamPlan','id, course(FK), exam_date, start_time, end_time, classroom(FK), invigilator(FK)','Has: ExamSeat'],
  ['ExamSeat','id, exam_plan(FK), student(FK), seat_number','Student seat assignment for an exam'],
  ['CourseEvaluation','id, course(FK), student(FK), rating(1-5), comments','Student feedback on a course'],
  ['DeanEvaluation','id, teacher(FK), evaluator(FK), period, score, criteria(JSON)','Admin/dean evaluation of teacher performance'],
  ['ClassroomPermission','STUB — not fully migrated','Intended: classroom access per teacher'],
  ['SupportRequest','id, student(FK), message, status, created_at','Lightweight student support request'],
  ['GateEntryLog','STUB','Planned merge with GateLog'],
];

const pages=[
  ['Login','/attendance/login/','login_view','Public','Django auth, sessions','Username/password → role-based redirect (admin/coordinator/teacher/student dashboard). CSRF, messages framework.'],
  ['Face Login','/attendance/login/face/','face_login','Public','face_recognition, OpenCV, pgvector, HTML5 getUserMedia','Webcam frame via AJAX → 128-dim embedding → pgvector cosine search → auto login on match.'],
  ['Admin Control Panel','/attendance/admin-panel/','admin_control_panel','Admin/Staff','Django ORM aggregations, Chart.js','KPI cards (students, teachers, sessions, rate), activity feed, quick-action buttons, WebSocket live stats.'],
  ['AI Scan Page','/attendance/scan/','scan_page','Admin/Staff/Teacher','OpenCV, face_recognition, pgvector, Django Channels, edge_cache','MJPEG live stream → detect faces → pgvector match → create Attendance → push result via WebSocket.'],
  ['Attendance Logs','/attendance/attendance-logs/','attendance_logs','Admin/Staff','Django ORM','Paginated list of all Attendance records. Filters: date, course, student, status. Method/confidence shown.'],
  ['Professor Dashboard','/attendance/professor-dashboard/','professor_dashboard','Teacher','Django ORM','Today\'s lectures, attendance rate per course, Open Session buttons, recent records, CSV export.'],
  ['Teacher Attendance Records','/attendance/teacher/attendance-records/','teacher_attendance_records','Teacher','Django ORM, openpyxl','Own course attendance. Course/date filters. Session stats. Excel export.'],
  ['Teacher Timeline','/attendance/teacher/timeline/','teacher_timeline','Teacher','Django ORM, Chart.js','Visual timeline of past/upcoming sessions with open/closed status and attendance rate.'],
  ['Teacher Profile','/attendance/teacher/profile/','teacher_profile_view','Teacher','Django ORM','Own profile: name, degree, major, gender, department, email, phone, face image. Read-only.'],
  ['Teacher Detail (Admin)','/attendance/teachers/<id>/','teacher_detail','Admin/Coordinator','Django ORM','Full profile + course assignments + evaluation scores for any teacher.'],
  ['Edit Teacher','/attendance/teachers/<id>/edit/','edit_teacher','Admin/Staff','Django ORM','Edit: name, degree, major, gender, college, dept, email, phone, face image, is_allowed_entry.'],
  ['Student Dashboard','/attendance/student/dashboard/','student_dashboard','Student','Django ORM, Chart.js','Enrolled courses + attendance %, at-risk warnings (<75%), next lecture, financial status, quick links.'],
  ['Student Profile','/attendance/student/profile/','student_profile','Student','Django ORM','Own profile: personal + academic data, face image, financial status, enrollment summary.'],
  ['Student Courses','/attendance/student/courses/','student_courses','Student','Django ORM','Enrolled courses with attendance %, teacher, schedule, status (Active/At-Risk).'],
  ['Student Schedule','/attendance/student/schedule/','student_schedule_view','Student','Django ORM','Weekly timetable calendar grid from active enrollments.'],
  ['Student Support','/attendance/student/support/','student_support','Student','Django ORM','Open tickets list, create ticket link, excuse portal link, FAQ.'],
  ['Excuse Portal','/attendance/student/excuse/','excuse_portal','Student','Django ORM','Submit absence excuse: session picker, reason, document upload. Goes to admin excuse board.'],
  ['Student Detail (Admin)','/attendance/students/<id>/','student_detail','Admin/Coordinator','Django ORM','Full student profile, per-course attendance, financial status, toggle entry access button.'],
  ['Edit Student','/attendance/students/<id>/edit/','edit_student','Admin/Coordinator','Django ORM, AJAX dept API','Edit all student fields. Admin-only college/dept (AJAX load). Status checkboxes. Face image upload.'],
  ['Register Student','/attendance/faculty-management/register-student/','register_student','Admin/Staff','Django ORM, auth','Creates auth.User + Student atomically. Name, code, college, dept, batch, email, phone, password.'],
  ['Register Teacher','/attendance/faculty-management/register-teacher/','register_teacher','Admin/Staff','Django ORM, auth','Creates auth.User + Teacher. Name, degree, major, gender, college, dept, email, phone, password.'],
  ['Coordinator Dashboard','/attendance/coordinator/dashboard/','coordinator_dashboard','Coordinator','Django ORM, Chart.js','College-scoped KPIs, enrollment activity, quick links to manage students/faculty/assignments/grading.'],
  ['Coordinator Students','/attendance/coordinator/students/','coordinator_students','Coordinator','Django ORM','Paginated college-filtered student list. Search, CSV export, attendance %, eligibility.'],
  ['Coordinator Faculty','/attendance/coordinator/faculty/','coordinator_faculty','Coordinator','Django ORM','College-filtered teacher list with course counts and detail/edit links.'],
  ['Coordinator Assignments','/attendance/coordinator/assignments/','coordinator_course_assignment','Coordinator','Django ORM, AJAX conflict API','Assign teachers to schedules. AJAX conflict detection. Creates LectureSchedule.'],
  ['Coordinator Register','/attendance/coordinator/register/','coordinator_register_user','Coordinator','Django ORM, auth','Register student/teacher in coordinator\'s college. Batch year + semester selectors.'],
  ['Coordinator Grading','/attendance/coordinator/grading/','coordinator_grading','Coordinator','Django ORM','Batch grade overview, trigger calculations, grade distribution, export PDF.'],
  ['Faculty Management','/attendance/faculty-management/','faculty_management','Admin/Staff','Django ORM','Admin hub: register student/teacher links, counts, recent additions.'],
  ['Courses List','/attendance/courses/','courses_list','Admin/Coordinator','Django ORM','All courses with CRUD (add/edit/delete). College filter, active status.'],
  ['Classrooms List','/attendance/classrooms/','classrooms_list','Admin/Coordinator','Django ORM','All rooms with real-time busy/free status from active sessions. Camera indicator. CRUD.'],
  ['Classrooms Status','/attendance/classrooms/status/','classrooms_status_view','Admin/Staff','Django ORM','Dashboard: all rooms with real-time occupancy, teacher, course, enrolled count.'],
  ['Schedule Grid','/attendance/schedule/','schedule_view','Admin/Coordinator/Teacher','Django ORM','Weekly schedule grid. Filters: college, dept, teacher. Add/edit/delete links.'],
  ['Add/Edit Schedule','/attendance/schedule/add-edit/','add_schedule / edit_schedule','Admin/Coordinator','Django ORM, AJAX','Form: course, teacher, classroom, day, time, semester. AJAX conflict detection.'],
  ['Reports Hub','/attendance/reports/','reports_view','Admin/Staff/Coordinator','Django ORM','Links to student report, teacher report, grade report each with CSV/Excel/PDF export buttons.'],
  ['Student Attendance Report','/attendance/reports/students/','student_attendance_report','Admin/Coordinator','Django ORM, openpyxl, WeasyPrint','Detailed report: present/absent counts, %, at-risk flag. Export: CSV, Excel (openpyxl), PDF (WeasyPrint).'],
  ['Teacher Attendance Report','/attendance/reports/teachers/','teacher_attendance_report','Admin/Staff','Django ORM, WeasyPrint','Teacher session delivery rate. CSV and PDF export.'],
  ['Gate Page','/attendance/gate/','gate_page','Gate Staff/Admin','face_recognition, OpenCV, pgvector','Webcam face match → check is_allowed_entry → create GateLog. Manual code fallback.'],
  ['Gate Reports','/attendance/admin-panel/gate-reports/','gate_reports','Admin','Django ORM','GateLog report: date/student filters, allowed/denied counts.'],
  ['Enroll Face','/attendance/enroll-face/','enroll_face','Admin/Staff','face_recognition, pgvector, AES-256 crypto_utils','Multi-frame webcam capture → 128-dim encode → AES-256 encrypt → store in FaceEmbedding (pgvector).'],
  ['Notifications','/attendance/notifications/','notifications_view','All users','Django ORM','Full notification list. Mark read/delete per item or all. Level icons (info/warning/danger/success).'],
  ['Admin Notifications','/attendance/admin-panel/notifications/','admin_notifications','Admin/Staff','Django ORM','Admin-panel styled notification list. Mark all read.'],
  ['Settings','/attendance/settings/','settings_view','All users','Django ORM, auth','4 tabs: Account (name/email/photo), Security (password change), Privacy toggles, Notification toggles.'],
  ['Tickets List','/attendance/tickets/','tickets_list','All users','Django ORM','Students see own tickets; admin sees all. Filters: status/priority/category.'],
  ['Create Ticket','/attendance/tickets/create/','create_ticket','All users','Django ORM','Submit ticket: subject, category, priority, description. Creates Ticket(status=open).'],
  ['Ticket Detail','/attendance/tickets/<id>/','ticket_detail','All users','Django ORM','Threaded TicketMessage view + reply form. Staff changes status/assignee.'],
  ['Global Search','/attendance/search/','global_search','Admin/Staff/Coordinator','Django ORM Q objects','icontains search across Students, Teachers, Courses, Classrooms, Tickets. Results grouped by type.'],
  ['Departments','/attendance/admin-panel/departments/','departments_view','Admin','Django ORM','Departments grouped by college with student/teacher counts. CRUD.'],
  ['Audit Log','/attendance/admin-panel/audit-log/','audit_log_view','Admin','Django ORM','Paginated AuditLog: user, action, model, timestamp, JSON details. Filter by user/date.'],
  ['Dean Evaluation','/attendance/admin-panel/dean-evaluation/','dean_evaluation_dashboard','Admin/Dean','Django ORM, Chart.js','Teacher evaluation scores, criteria breakdown (JSON field), radar charts, period filter.'],
  ['Faculty Timeline','/attendance/admin-panel/faculty-timeline/','faculty_timeline','Admin','Django ORM','Chronological timeline of all teacher activities. Teacher filter.'],
  ['Excuse Approval Board','/attendance/admin-panel/excuse-board/','excuse_approval_board','Admin/Coordinator','Django ORM','Approve/reject student absence excuses. Updates Attendance.status to Excused on approval.'],
  ['Exam Planner','/attendance/admin-panel/exam-planner/','exam_planner','Admin/Coordinator','Django ORM','Create ExamPlan. Conflict check. Auto-generates ExamSeat for all enrolled students.'],
  ['Exam Seating Chart','/attendance/admin-panel/exam-seating/','exam_seating_chart','Admin/Coordinator','Django ORM','Visual seat grid with student names. Exam/classroom selector. Printable layout.'],
  ['Exam Gate Verify','/attendance/admin-panel/exam-gate/','exam_gate_verify','Admin/Gate Staff','Django ORM, face_recognition','Verify exam entry: face or code → check ExamSeat + is_allowed_entry. Pass/fail display.'],
  ['Onboarding Wizard','/attendance/admin-panel/onboarding/','onboarding_wizard','Admin','Django ORM','Step-by-step setup: college → dept → teacher → schedule → demo seed. Progress indicator.'],
  ['Admin Tickets','/attendance/admin-panel/tickets/','admin_tickets','Admin/Staff','Django ORM','All tickets across all users. Multi-filter. Bulk status change, reassign, staff replies.'],
  ['Password Reset Flow','/attendance/password-reset/ (4 routes)','PasswordResetView (Django built-in)','Public','django.contrib.auth, email backend','Email → token link → new password → confirmation. Custom ACDC-styled templates.'],
  ['Teacher Permissions','/attendance/teacher/permissions/','teacher_permissions_view','Teacher','Django ORM (ClassroomPermission stub)','Displays classroom permissions. Partial implementation pending ClassroomPermission migration.'],
];

const bugs=[
  ['teacher_profile.html','teacher.profile_photo / specialization_type / blood_type — none exist','Changed to face_image / major / department.name'],
  ['student_profile.html','semester / blood_type / nationality / is_eligible_for_entry / financialstatus.is_paid / balance_due — none exist','Removed invalid fields; mapped to is_allowed_entry / status==Paid / amount_due'],
  ['admin_notifications.html','notif.notif_type / notif.message / level==error','Changed to notif.level / notif.title / level==danger'],
  ['notifications.html','n.notif_type / n.message / level==error; file truncated at line 116','Fixed field names; fixed truncation via Python rfind'],
  ['edit_teacher.html','specialization_type select — field does not exist','Replaced with gender select (Male/Female)'],
  ['edit_student.html','nationality / blood_type / date_of_birth / semester inputs','Removed all; replaced with is_registered select'],
  ['search_results.html','s.is_eligible_for_entry — does not exist','Changed to s.is_allowed_entry'],
  ['settings.html','profile_photo.url on student/teacher','Changed to face_image.url'],
  ['views.py','File truncated at line 2344 — 6 views missing: admin_notifications, notifications_view, settings_view, update_settings, mark_notification_read, export_coordinator_students_csv','Reconstructed file; all 6 views written and appended'],
  ['views.py','edit_student missing colleges context; coordinator_register_user missing batch_years/semester_choices; student_profile missing student_fields; edit_teacher not saving gender','All context vars added; gender save added to POST handler'],
];

const ch=[];

// COVER
ch.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:1600,after:200},children:[new TextRun({text:'ACDC',font:'Arial',size:120,bold:true,color:C.primary})]}));
ch.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:0,after:160},children:[new TextRun({text:'Automated Campus & Department Control',font:'Arial',size:32,color:C.gray})]}));
ch.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:200,after:80},children:[new TextRun({text:'Comprehensive Technical Report',font:'Arial',size:44,bold:true,color:C.secondary})]}));
ch.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:80,after:80},children:[new TextRun({text:'Files — Models — Pages — Relationships — Bug Fixes',font:'Arial',size:24,color:C.gray,italics:true})]}));
ch.push(new Paragraph({alignment:AlignmentType.CENTER,spacing:{before:500,after:60},children:[new TextRun({text:'Graduation Project  |  May 2026',font:'Arial',size:22,color:C.gray})]}));
ch.push(pb());

// SECTION 1 — Summary
ch.push(hd('Executive Summary'));
ch.push(tbl([
  new TableRow({children:[hcell('Metric',2340),hcell('Value',2340),hcell('Metric',2340),hcell('Value',2340)]}),
  new TableRow({children:[cell('Python files',{w:2340}),cell('28',{w:2340,bold:true,color:C.primary}),cell('HTML templates',{w:2340}),cell('85',{w:2340,bold:true,color:C.primary})]}),
  new TableRow({children:[cell('DB models',{w:2340,bg:C.light}),cell('26',{w:2340,bold:true,color:C.primary,bg:C.light}),cell('URL routes',{w:2340,bg:C.light}),cell('91',{w:2340,bold:true,color:C.primary,bg:C.light})]}),
  new TableRow({children:[cell('View functions',{w:2340}),cell('104',{w:2340,bold:true,color:C.primary}),cell('User roles',{w:2340}),cell('5',{w:2340,bold:true,color:C.primary})]}),
  new TableRow({children:[cell('Total lines',{w:2340,bg:C.light}),cell('4,575+',{w:2340,bold:true,color:C.primary,bg:C.light}),cell('Export formats',{w:2340,bg:C.light}),cell('CSV / Excel / PDF',{w:2340,bold:true,color:C.primary,bg:C.light})]}),
],[2340,2340,2340,2340]));
ch.push(p(''));
ch.push(p('Stack: Django 4.x · PostgreSQL + pgvector · Django Channels (WebSocket/Redis) · face_recognition + OpenCV · Celery · Tailwind CSS · WeasyPrint · openpyxl · PyCryptodome AES-256 · WhiteNoise'));
ch.push(pb());

// SECTION 2 — Python Files
ch.push(hd('Section 1 — Python Files (28)'));
ch.push(tbl([
  new TableRow({children:[hcell('File',3000),hcell('Lines',600),hcell('Remove?',900),hcell('Description',4860)]}),
  ...py.map(([f,l,r,d],i)=>new TableRow({children:[
    cell(f,{w:3000,sz:17,bg:i%2?C.light:'FFFFFF'}),
    cell(l,{w:600,sz:17,al:AlignmentType.CENTER,bg:i%2?C.light:'FFFFFF'}),
    cell(r,{w:900,sz:17,color:r.startsWith('YES')?C.danger:C.success,bold:true,bg:i%2?C.light:'FFFFFF'}),
    cell(d,{w:4860,sz:16,bg:i%2?C.light:'FFFFFF'}),
  ]}))
],[3000,600,900,4860]));
ch.push(pb());

// File relations
ch.push(hd('Section 1b — Key File Relationships'));
ch.push(tbl([
  new TableRow({children:[hcell('File',2400),hcell('Depends On',3480),hcell('Used By',3480)]}),
  new TableRow({children:[cell('models.py',{w:2400}),cell('Django ORM, pgvector',{w:3480}),cell('views.py, admin.py, tasks.py, notifications.py, context_processors.py, consumers.py',{w:3480})]}),
  new TableRow({children:[cell('views.py',{w:2400,bg:C.light}),cell('models.py, tasks.py, crypto_utils.py, edge_cache.py, notifications.py',{w:3480,bg:C.light}),cell('urls.py (all 104 routes)',{w:3480,bg:C.light})]}),
  new TableRow({children:[cell('urls.py',{w:2400}),cell('views.py',{w:3480}),cell('acdc_config/urls.py (include)',{w:3480})]}),
  new TableRow({children:[cell('context_processors.py',{w:2400,bg:C.light}),cell('models.py (Notification, Student, Teacher, Coordinator)',{w:3480,bg:C.light}),cell('Every template (settings.py TEMPLATES)',{w:3480,bg:C.light})]}),
  new TableRow({children:[cell('consumers.py',{w:2400}),cell('Django Channels',{w:3480}),cell('routing.py → asgi.py',{w:3480})]}),
  new TableRow({children:[cell('tasks.py',{w:2400,bg:C.light}),cell('models.py, notifications.py, Celery',{w:3480,bg:C.light}),cell('views.py (dispatch), Celery Beat',{w:3480,bg:C.light})]}),
  new TableRow({children:[cell('crypto_utils.py',{w:2400}),cell('PyCryptodome AES-256',{w:3480}),cell('views.py (face enrollment/login)',{w:3480})]}),
  new TableRow({children:[cell('edge_cache.py',{w:2400,bg:C.light}),cell('Python stdlib threading',{w:3480,bg:C.light}),cell('views.py (scan_page, video_feed)',{w:3480,bg:C.light})]}),
],[2400,3480,3480]));
ch.push(pb());

// SECTION 3 — Models
ch.push(hd('Section 2 — Database Models (26 Classes)'));
ch.push(p('All in attendance/models.py · PostgreSQL + pgvector (128-dim face embeddings)'));
ch.push(p(''));
ch.push(tbl([
  new TableRow({children:[hcell('Model',1600),hcell('Key Fields',3800),hcell('Relations',3960)]}),
  ...models.map(([m,f,r],i)=>new TableRow({children:[
    cell(m,{w:1600,bold:true,sz:19,bg:i%2?C.light:'FFFFFF'}),
    cell(f,{w:3800,sz:16,bg:i%2?C.light:'FFFFFF'}),
    cell(r,{w:3960,sz:16,color:C.secondary,bg:i%2?C.light:'FFFFFF'}),
  ]}))
],[1600,3800,3960]));
ch.push(pb());

// SECTION 4 — Templates
ch.push(hd('Section 3 — HTML Templates (85 Files)'));
ch.push(p('Location: attendance/templates/attendance/ · Extend base.html or base_auth.html · Tailwind CSS + Material Symbols · Dark mode via dark: variant'));
ch.push(p(''));
ch.push(tbl([
  new TableRow({children:[hcell('Category',2000),hcell('Details',7360)]}),
  new TableRow({children:[cell('base.html',{w:2000,bold:true}),cell('Main shell: sidebar, top bar, dark mode toggle, notification bell, WebSocket script. All authenticated pages extend this.',{w:7360})]}),
  new TableRow({children:[cell('base_auth.html',{w:2000,bold:true,bg:C.light}),cell('Auth shell: no sidebar, centered layout. Used by login, face_login, password reset pages.',{w:7360,bg:C.light})]}),
  new TableRow({children:[cell('reports/*.html (5 files)',{w:2000,bold:true}),cell('PDF/print templates rendered by WeasyPrint. Not direct user pages.',{w:7360})]}),
  new TableRow({children:[cell('🗑 ORPHAN FOLDER',{w:2000,bold:true,color:C.danger,bg:C.light}),cell('attendance/templates/templates/attendance/ — entire folder never reached by APP_DIRS. Delete safely.',{w:7360,bg:C.light,color:C.danger})]}),
  new TableRow({children:[cell('🗑 coordinator_register_user.html',{w:2000,bold:true,color:C.danger}),cell('Never rendered — view uses coordinator_register.html instead. Delete safely.',{w:7360,color:C.danger})]}),
],[2000,7360]));
ch.push(pb());

// SECTION 5 — Interactive Pages
ch.push(hd(`Section 4 — Interactive Pages (${pages.length} Pages)`));
ch.push(tbl([
  new TableRow({children:[hcell('Page',1800),hcell('URL',2200),hcell('View',1700),hcell('Roles',1200),hcell('Tools',1400),hcell('What it does',1060)]}),
  ...pages.map(([pg,url,view,roles,tools,desc],i)=>new TableRow({children:[
    cell(pg,{w:1800,bold:true,sz:17,bg:i%2?C.light:'FFFFFF'}),
    cell(url,{w:2200,sz:15,color:C.secondary,bg:i%2?C.light:'FFFFFF'}),
    cell(view,{w:1700,sz:15,bg:i%2?C.light:'FFFFFF'}),
    cell(roles,{w:1200,sz:15,bg:i%2?C.light:'FFFFFF'}),
    cell(tools,{w:1400,sz:15,bg:i%2?C.light:'FFFFFF'}),
    cell(desc,{w:1060,sz:14,bg:i%2?C.light:'FFFFFF'}),
  ]}))
],[1800,2200,1700,1200,1400,1060]));
ch.push(pb());

// SECTION 6 — Bug Fixes
ch.push(hd('Section 5 — Bug Fixes (3 Rounds)'));
ch.push(tbl([
  new TableRow({children:[hcell('File',2000),hcell('Bug Found',3680),hcell('Fix Applied',3680)]}),
  ...bugs.map(([f,bug,fix],i)=>new TableRow({children:[
    cell(f,{w:2000,bold:true,sz:17,bg:i%2?C.light:'FFFFFF'}),
    cell(bug,{w:3680,sz:16,color:C.danger,bg:i%2?C.light:'FFFFFF'}),
    cell(fix,{w:3680,sz:16,color:C.success,bg:i%2?C.light:'FFFFFF'}),
  ]}))
],[2000,3680,3680]));
ch.push(p(''));
ch.push(p('Round 3 verification: all 91 URL names matched to view functions · all 85 templates have closed block tags · views.py syntax: SYNTAX OK',{color:C.secondary}));
ch.push(pb());

// SECTION 7 — Removable
ch.push(hd('Section 6 — Removable Files & Recommendations'));
ch.push(tbl([
  new TableRow({children:[hcell('Item',3500),hcell('Action',1200),hcell('Reason',4660)]}),
  new TableRow({children:[cell('attendance/context_processors_1.py',{w:3500}),cell('DELETE',{w:1200,bold:true,color:C.danger}),cell('Empty 1-line stub, not imported anywhere',{w:4660})]}),
  new TableRow({children:[cell('attendance/templates/templates/ (folder)',{w:3500,bg:C.light}),cell('DELETE',{w:1200,bold:true,color:C.danger,bg:C.light}),cell('APP_DIRS never reads this nested path — complete orphan',{w:4660,bg:C.light})]}),
  new TableRow({children:[cell('coordinator_register_user.html',{w:3500}),cell('DELETE',{w:1200,bold:true,color:C.danger}),cell('View uses coordinator_register.html; this file is never rendered',{w:4660})]}),
  new TableRow({children:[cell('create_templates.py / generate_thesis*.py',{w:3500,bg:C.light}),cell('DELETE',{w:1200,bold:true,color:C.danger,bg:C.light}),cell('One-off utility scripts, not part of Django app',{w:4660,bg:C.light})]}),
  new TableRow({children:[cell('inspect_face.py / test_cam.py',{w:3500}),cell('DELETE (prod)',{w:1200,bold:true,color:C.danger}),cell('Dev-only debug scripts',{w:4660})]}),
  new TableRow({children:[cell('seed_demo.py',{w:3500,bg:C.light}),cell('KEEP (dev)',{w:1200,bold:true,color:C.success,bg:C.light}),cell('Keep for dev/testing; remove from production deployment',{w:4660,bg:C.light})]}),
  new TableRow({children:[cell('ClassroomPermission / GateEntryLog models',{w:3500}),cell('COMPLETE or REMOVE',{w:1200,bold:true,color:'D97706'}),cell('Stubs with try/except import guards — finish migration or delete',{w:4660})]}),
],[3500,1200,4660]));
ch.push(p(''));
ch.push(hd('Production Deployment Checklist',HeadingLevel.HEADING_2,C.secondary));
['Set DEBUG=False and configure ALLOWED_HOSTS in settings.py',
 'Use daphne or uvicorn for ASGI/WebSocket support (not gunicorn alone)',
 'Replace WhiteNoise with Nginx for high-traffic static file serving',
 'Configure Celery Beat for automated tasks (daily summaries, cleanup)',
 'Store AES encryption key in environment variables, not hardcoded',
 'Run python manage.py collectstatic before deployment',
].forEach(t=>ch.push(new Paragraph({spacing:{before:40,after:40},numbering:{reference:'bullets',level:0},children:[new TextRun({text:t,font:'Arial',size:21})]})));

const doc=new Document({
  numbering:{config:[{reference:'bullets',levels:[{level:0,format:LevelFormat.BULLET,text:'•',alignment:AlignmentType.LEFT,style:{paragraph:{indent:{left:720,hanging:360}}}}]}]},
  styles:{
    default:{document:{run:{font:'Arial',size:21}}},
    paragraphStyles:[
      {id:'Heading1',name:'Heading 1',basedOn:'Normal',next:'Normal',quickFormat:true,run:{size:34,bold:true,font:'Arial',color:C.primary},paragraph:{spacing:{before:400,after:150},outlineLevel:0,border:{bottom:{style:BorderStyle.SINGLE,size:4,color:C.primary,space:4}}}},
      {id:'Heading2',name:'Heading 2',basedOn:'Normal',next:'Normal',quickFormat:true,run:{size:26,bold:true,font:'Arial',color:C.secondary},paragraph:{spacing:{before:220,after:100},outlineLevel:1}},
    ]
  },
  sections:[{
    properties:{page:{size:{width:12240,height:15840},margin:{top:1000,right:1000,bottom:1000,left:1000}}},
    headers:{default:new Header({children:[new Paragraph({alignment:AlignmentType.RIGHT,border:{bottom:{style:BorderStyle.SINGLE,size:2,color:C.primary,space:4}},children:[new TextRun({text:'ACDC — Comprehensive Technical Report',font:'Arial',size:18,color:C.gray,italics:true})]})]})} ,
    footers:{default:new Footer({children:[new Paragraph({alignment:AlignmentType.CENTER,border:{top:{style:BorderStyle.SINGLE,size:2,color:C.primary,space:4}},children:[new TextRun({text:'Page ',font:'Arial',size:18,color:C.gray}),new TextRun({children:[PageNumber.CURRENT],font:'Arial',size:18,color:C.gray}),new TextRun({text:' of ',font:'Arial',size:18,color:C.gray}),new TextRun({children:[PageNumber.TOTAL_PAGES],font:'Arial',size:18,color:C.gray}),new TextRun({text:'  |  ACDC Graduation Project 2026',font:'Arial',size:18,color:C.gray})]})]})},
    children:ch
  }]
});

Packer.toBuffer(doc).then(buf=>{
  fs.writeFileSync('/sessions/vigilant-loving-clarke/mnt/ACDC_FINAL-main/ACDC_Project_Report.docx',buf);
  console.log('OK size='+Math.round(buf.length/1024)+'KB');
}).catch(e=>{console.error('ERR:',e.message);process.exit(1);});
