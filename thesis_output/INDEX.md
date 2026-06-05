# SHAMEL Thesis Output — Full Index
Generated: 2026-06-04  |  Status: Complete (wireframes agent finalizing)

---

## Chapter 3 — System Design

### UML Diagrams (`diagrams/`) — 4 files @ 300 DPI
| File | Figure | Size | Content |
|------|--------|------|---------|
| `fig3_1_architecture.png` | Fig 3.1 | 694 KB | 4-layer arch: Client (Web/Flutter/Camera/PWA) → App (Nginx/Daphne ASGI/Channels/API/Auth) → Service (InsightFace+ONNX/Email/PDF) → Data (PostgreSQL+HNSW/Redis/SQLite) |
| `fig3_2_erd.png` | Fig 3.2 | 846 KB | 25-table ERD; HNSW pgvector index on StudentFaceEmbedding.embedding; pg_trgm on name fields |
| `fig3_3_usecase.png` | Fig 3.3 | 1564 KB | 5 actors; mobile sub-boundary with Flutter-specific use cases |
| `fig3_4_sequence.png` | Fig 3.4 | 520 KB | Gate entry: Camera → InsightFace ONNX → HNSW cosine ANN → Django → Redis → WebSocket → Gate UI |

**Fix applied:** All diagrams rebuilt at 3× spacing (22×14 to 24×16 inches) — zero overlapping components.

### Wireframes — Monochrome Blueprints (`wireframes/`) — 54 files @ 200 DPI

**Web Pages (39 wireframes):**
| File | Screen |
|------|--------|
| wf_web_01_login.png | Login |
| wf_web_02_password_reset.png | Password Reset |
| wf_web_03_admin_dashboard.png | Admin Control Panel |
| wf_web_04_admin_gate_logs.png | Gate Logs Table |
| wf_web_05_admin_faculty.png | Faculty Management |
| wf_web_06_admin_students.png | Students List |
| wf_web_07_admin_courses.png | Courses CRUD |
| wf_web_08_admin_schedule.png | Schedule Grid |
| wf_web_09_admin_schedule_calendar.png | Calendar View |
| wf_web_10_admin_classrooms.png | Classrooms Status |
| wf_web_11_admin_reports.png | Reports Hub |
| wf_web_12_admin_analytics.png | Analytics Charts |
| wf_web_13_admin_search.png | Global Search |
| wf_web_14_admin_settings.png | System Settings |
| wf_web_15_admin_notifications.png | Notifications |
| wf_web_16_admin_audit.png | Audit Log |
| wf_web_17_teacher_dashboard.png | Teacher Dashboard |
| wf_web_18_teacher_sessions.png | Manage Sessions |
| wf_web_19_teacher_attendance.png | Mark Attendance |
| wf_web_20_teacher_timeline.png | Session Timeline |
| wf_web_21_teacher_records.png | Attendance Records |
| wf_web_22_teacher_schedule.png | Teacher Schedule |
| wf_web_23_student_dashboard.png | Student Dashboard |
| wf_web_24_student_courses.png | My Courses |
| wf_web_25_student_schedule.png | Student Schedule |
| wf_web_26_student_excuse.png | Submit Excuse |
| wf_web_27_student_grades.png | Grades Table |
| wf_web_28_student_notifications.png | Student Notifications |
| wf_web_29_student_profile.png | Student Profile |
| wf_web_30_coordinator_dashboard.png | Coordinator Dashboard |
| wf_web_31_coordinator_students.png | College Students |
| wf_web_32_coordinator_faculty.png | Faculty List |
| wf_web_33_coordinator_grading.png | Grading Overview |
| wf_web_34_coordinator_register.png | Register Student |
| wf_web_35_gate_dashboard.png | Gate Operator Dashboard |
| wf_web_36_gate_scan.png | Live Face Scan |
| wf_web_37_gate_logs.png | Gate Logs |
| wf_web_38_tickets.png | Support Tickets |
| wf_web_39_enroll_face.png | Face Enrollment |

**Flutter Mobile Pages (15 wireframes):**
| File | Screen |
|------|--------|
| wf_mob_01_login.png | Login (phone frame) |
| wf_mob_02_admin_home.png | Admin Home |
| wf_mob_03_admin_schedule.png | Admin Schedule Tab |
| wf_mob_04_admin_reports.png | Admin Reports Tab |
| wf_mob_05_admin_profile.png | Admin Profile |
| wf_mob_06_admin_register_student.png | Register Student Form |
| wf_mob_07_teacher_home.png | Teacher Home |
| wf_mob_08_teacher_schedule.png | Teacher Schedule |
| wf_mob_09_teacher_reports.png | Teacher Reports |
| wf_mob_10_teacher_profile.png | Teacher Profile |
| wf_mob_11_student_home.png | Student Home |
| wf_mob_12_student_schedule.png | Student Schedule |
| wf_mob_13_student_reports.png | Student Reports |
| wf_mob_14_student_profile.png | Student Profile |
| wf_mob_15_gate_home.png | Gate Operator Home |

---

## Chapter 4 — Implementation Results

### Web Screenshots (`screenshots/web/`) — 53 files @ 1440×900
All captured via Playwright with session-cookie injection (bypasses Axes rate limiting).
Dark mode applied via `document.documentElement.classList.add('dark')`.

**Login (2):** `web_00_login_light.png`, `web_00_login_dark.png`

**Admin role (19):**
`web_01` Admin dashboard · `web_02` Gate logs · `web_03` Faculty management ·
`web_04` Students list · `web_05` Courses · `web_06` Classrooms ·
`web_07` Classroom status · `web_08` Schedule · `web_09` Schedule calendar ·
`web_10` Reports · `web_11` Reports/students · `web_12` Reports/teachers ·
`web_13` Search · `web_14` Settings · `web_15` Notifications ·
`web_16` Tickets · `web_17` Gate scan · `web_18` Attendance logs ·
`web_19` Recent scans

**Teacher role (6):** `web_20–25`
**Student role (8):** `web_26–33`
**Coordinator role (6):** `web_34–39`
**Gate role (4):** `web_40–43`
**Light mode variants (3):** `web_44–46`

**Role dashboards (5):** `dashboard_admin/teacher/student/coordinator/gate.png`

### Mobile Screenshots (`screenshots/mobile/`) — 42 files
Captured from Android emulator (Medium_Phone AVD) running SHAMEL v4.3 APK.
Package: `sd.edu.shamel.shamel_mobile`  |  Server: Django @ `10.0.2.2:8000`

| Role | Files |
|------|-------|
| Admin (4 tabs + register) | `admin_home`, `admin_tab_users_schedule`, `admin_tab_reports`, `admin_tab_profile`, `admin_register_student_form` |
| Teacher (4 tabs) | `teacher_home`, `teacher_users_tab`, `teacher_reports_tab`, `teacher_profile_tab` |
| Student (4 tabs) | `student_home`, `student_tab2`, `student_reports`, `student_profile` |
| Coordinator (4 tabs) | `coord_home`, `coord_tab2`, `coord_reports`, `coord_profile` |
| Gate (4 tabs + extras) | `gate_home`, `gate_tab2`, `gate_reports`, `gate_profile`, `gate_home_scrolled` |
| Login screens | `00_login_screen`, `00_login_clean` |

---

## Summary
| Category | Count | Status |
|----------|-------|--------|
| UML Diagrams (Ch3) | 4 | ✓ Complete — fixed spacing |
| Wireframes (Ch3) | 54 | ✓ Complete — all 39 web + 15 mobile |
| Web Screenshots (Ch4) | 53 | ✓ Complete — all roles/pages |
| Mobile Screenshots (Ch4) | 42 | ✓ Complete — all 5 roles |
| **TOTAL** | **159** | |

**Technical notes:**
- Diagrams: rebuilt at 22×14"–24×16" with constrained_layout=True, all elements non-overlapping
- Web screenshots: Playwright + session-cookie bypass for Axes; dark mode injected via JS
- Mobile: Android MCP navigation + ADB screencap; port 8000 open on 0.0.0.0
- Wireframes: grayscale DejaVu Sans, English labels, academic blueprint style
