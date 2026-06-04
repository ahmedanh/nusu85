# SHAMEL Thesis Output — File Index
Generated: 2026-06-04

---

## Chapter 3 — Design & Architecture

### UML Diagrams (`diagrams/`)
| File | Figure | Description |
|------|--------|-------------|
| `fig3_1_architecture.png` | Fig 3.1 | System Architecture — Client/App/Service/Data layers; Flutter, Daphne ASGI, Redis, InsightFace+ONNX |
| `fig3_2_erd.png` | Fig 3.2 | Database ERD — 25 tables; HNSW pgvector index on embeddings, pg_trgm on name fields |
| `fig3_3_usecase.png` | Fig 3.3 | Use Case Diagram — 5 roles; mobile features: Push Notifications, Attendance History, Schedule |
| `fig3_4_sequence.png` | Fig 3.4 | Gate Entry Sequence — InsightFace ONNX → HNSW cosine search → WebSocket async broadcast |

**Specs:** 300 DPI, PNG, white background, academic color scheme

### Wireframes — Monochrome (`wireframes/`)
| File | Screen | Purpose |
|------|--------|---------|
| `wf01_login.png` | Login | Auth screen with role selector |
| `wf02_admin_dashboard.png` | Admin Dashboard | Stat cards, attendance chart, gate log table, notifications |
| `wf03_student_dashboard.png` | Student Dashboard | Attendance gauge, course breakdown, schedule, quick actions |
| `wf04_gate_scan.png` | Gate Scan | Camera viewport, face detection ROI, match result panel, live log |
| `wf05_mobile_student.png` | Mobile — Student | Flutter phone frame, bottom nav, schedule, notifications |
| `wf06_teacher_attendance.png` | Teacher Attendance | Attendance marking table with present/absent/late controls |

**Specs:** 200 DPI, PNG, pure grayscale (#333–#FFF), DejaVu Sans font, English labels

---

## Chapter 4 — Implementation Results

### Web Screenshots — High-Fidelity (`screenshots/web/`)

**Login**
- `01_login_light.png` — Light mode
- `02_login_dark.png` — Dark mode

**Admin Role (Dark)**
- `dashboard_admin.png` — Admin control panel (main dashboard)
- `04_admin_gate_logs.png` — Gate entry logs table
- `05_admin_faculty_mgmt.png` — Faculty management
- `06_admin_reports.png` — Reports hub
- `07_admin_search.png` — Global search
- `08_admin_schedule.png` — Schedule management
- `09_admin_classrooms.png` — Classroom status
- `10_admin_dashboard_light.png` — Admin dashboard light mode

**Teacher Role (Dark)**
- `dashboard_teacher.png` — Professor dashboard
- `12_teacher_timeline.png` — Session timeline
- `13_teacher_records.png` — Attendance records
- `14_teacher_schedule.png` — Schedule view

**Student Role (Dark)**
- `dashboard_student.png` — Student dashboard
- `16_student_courses.png` — My courses
- `17_student_schedule.png` — Weekly schedule
- `18_student_excuse.png` — Submit medical excuse
- `19_student_notifications.png` — Notifications

**Coordinator Role (Dark)**
- `dashboard_coordinator.png` — Coordinator dashboard
- `21_coordinator_students.png` — College students list
- `22_coordinator_grading.png` — Grading overview

**Gate Role (Dark)**
- `dashboard_gate.png` — Gate operator dashboard
- `24_gate_scan.png` — Live face scan screen
- `25_gate_logs.png` — Attendance logs

### Mobile Screenshots — Flutter App (`screenshots/mobile/`)
| File | Screen |
|------|--------|
| `mob_01_launch.png` | App launch / splash |
| `mob_02_login_filled.png` | Login screen with credentials entered |
| `mob_03_student_dashboard.png` | Student home dashboard |
| `mob_04_schedule.png` | Schedule tab |
| `mob_05_home_tab.png` | Home tab |
| `mob_06_drawer_open.png` | Navigation drawer open |
| `mob_07_dashboard_scrolled.png` | Dashboard scrolled down |
| `mob_08_drawer_scrolled.png` | Drawer scrolled |
| `mob_09_drawer.png` | Full navigation drawer |
| `mob_10_attendance_screen.png` | Attendance screen |
| `mob_11_back.png` | Back to home |

---

## Summary
- **4** UML diagrams (300 DPI) — Chapter 3 figures
- **6** monochrome wireframes (200 DPI) — Chapter 3 UI design section
- **25** web screenshots (1440×900) — Chapter 4 results
- **11** mobile screenshots (from emulator) — Chapter 4 Flutter app

Total files: **46 PNG files**
