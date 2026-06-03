# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**SHAMEL** — Smart Holistic Attendance Management & Compliance System.
Academic attendance platform for Sudanese universities:
- **Django 4.x** web app + REST API (`/api/v1/`)
- **Flutter 3.41** native Android app (same API, offline-capable)
- **Face recognition** at gate entry (dlib or InsightFace ONNX)
- **PWA** for mobile-web fallback

Production: `shamel.sd` (Ubuntu VPS, Daphne/Channels ASGI on :9000, Nginx reverse proxy)

---

## Commands

### Django (Web)

```bash
# Dev server (SQLite auto-fallback if VPS PostgreSQL unreachable)
python manage.py runserver 0.0.0.0:8000 --noreload

# Daphne ASGI (production-like, needed for WebSocket consumers)
daphne -b 0.0.0.0 -p 9000 acdc_config.asgi:application

# Migrations
python manage.py makemigrations attendance
python manage.py migrate

# Populate demo data (creates all role accounts + sample records)
python populate_demo_data.py

# Seed face embeddings after engine switch
python manage.py reenroll_faces

# Full E2E test — exercises every route across all roles (no external deps)
python e2e_test.py       # fast role-based URL sweep
python autotest2.py      # deep: exports PDF/CSV/Excel, API token auth, conflicts

# Screen inventory PDF (Playwright + ADB — requires Django running on :8000)
python screen_inventory.py
python compress_v2.py     # compress output → 57% smaller
```

### Flutter (Mobile)

```bash
cd mobile

# Run on emulator (uses http://10.0.2.2:8000 or :9000 — auto-discovers)
C:\develop\flutter\bin\flutter.bat run -d emulator-5554 --debug

# Release APK
C:\develop\flutter\bin\flutter.bat build apk --release
# Output: build/app/outputs/flutter-apk/app-release.apk

# Static analysis (must pass before commit)
C:\develop\flutter\bin\flutter.bat analyze --no-pub

# Install on emulator
adb install -r build/app/outputs/flutter-apk/app-release.apk
```

### Deploy (VPS)

```bash
./deploy.sh
# Runs: pip install → migrate → collectstatic → systemctl restart shamel + nginx → live-reload signal
```

---

## Architecture

### Django (`/attendance/`)

Single Django app. All logic is in:

| File | Purpose |
|------|---------|
| `models.py` | 22 models (see below) |
| `views.py` | ~3500 lines — all web views + HTML rendering |
| `api.py` + `api_extra.py` | `/api/v1/` JSON endpoints (token auth via `Authorization: Bearer`) |
| `urls.py` | All routes — both HTML pages and `/api/v1/` |
| `face_engine.py` | Dlib/InsightFace abstraction (swap via `FACE_ENGINE` env var) |
| `middleware.py` | `CloseOldConnectionsMiddleware`: closes stale PG connections + caches auth User (30s TTL) to eliminate per-request VPS round-trips |
| `consumers.py` | Django Channels WebSocket — live attendance feed |
| `edge_cache.py` | SQLite-backed edge cache for offline API responses |
| `email_utils.py` | SMTP notifications (ineligible students, exam reminders) |
| `tasks.py` | Async tasks via `AsyncTask` model |
| `notifications.py` | Notification push helpers |

**Template path quirk:** templates live in `attendance/templates/templates/attendance/` (double `templates/`). The settings `DIRS` points to `attendance/templates/templates`.

**`base.html`** is the central hub (1400+ lines). It contains:
- Tailwind CDN config (`darkMode: "class"`)
- Material Symbols font (served locally from `static/fonts/material-symbols.ttf`)
- All shared CSS: pagination (`.tbl-pager`), sticky columns, skeleton shimmer, multi-step wizard (`.shmwiz-*`), responsive table cards (`.resp-table`), empty-state (`.empty-state`)
- `ShamelTables()` JS: auto-applies pagination + sticky + responsive cards + empty states to all `<table>` elements
- Chart.js dark-mode defaults (injected at DOMContentLoaded, re-applied on theme toggle)
- `initWizard()` JS: multi-step forms with live `✓` validation

**Tailwind CDN limitation:** `@apply` directives in `<style>` tags inside individual templates are NOT compiled. Use real CSS properties or define utility classes in `base.html`'s `<style>` block. Classes `.inp`, `.label-xs`, `.tab-btn` are defined in `base.html` for this reason.

### Key Models

```
College → Department → Course
                     → Teacher (is_allowed_entry: students only, NOT teachers)
                     → Student (is_allowed_entry: toggleable — based on enrollment status)
                     → Coordinator (scoped to one College)
Course + Teacher + Classroom → Schedule → LectureSession → AIAttendanceLog
Student → StudentFaceEmbedding (128-dim dlib OR 512-dim InsightFace)
Teacher → TeacherFaceEmbedding
GateLog, Notification, SupportTicket, MedicalExcuse, Exam→ExamSeat, Grade, AuditLog
```

**Teacher access toggle is intentionally removed.** Teachers are employed staff — gate entry is implicit. Only students have `is_allowed_entry` toggled (enrollment/fee-based). Do not add toggle_access back for teachers.

### Role-Based Access (5 roles)

| Role | Scope | Dashboard focus |
|------|-------|----------------|
| `admin` (superuser) | Global — whole university | System infra: gate logs, camera accuracy, audit, all-university stats |
| `coordinator` | One college only | Academic KPIs: pending excuses, ungraded courses, college attendance %, student at-risk |
| `teacher` | Their courses only | Sessions, attendance records, timeline |
| `student` | Their enrollment | Attendance %, schedule, excuses |
| `gate` | Gate entry point | Gate logs, classroom status, face scan |

Coordinators see **college-scoped data only** — never global system stats or gate infrastructure. This is enforced in both Django views and the Flutter dashboard.

### Database Strategy

Settings auto-detects PostgreSQL reachability at startup:
- VPS reachable → PostgreSQL (production data)
- VPS unreachable → `db_local.sqlite3` (offline fallback)

Force SQLite locally: `USE_LOCAL_DB=true python manage.py runserver`

### PWA

`/static/pwa/sw.js` — Service Worker with dynamic version injection.
`/static/pwa/pwa-init.js` — Registers SW, shows update banner. **Install prompt is intentionally suppressed** (`beforeinstallprompt` is `preventDefault()`'d — no floating button). Users install via browser address-bar icon.
`/offline/` — Offline fallback page (served from cache when network unavailable).

### Face Recognition

Two engines behind `face_engine.py`:
- **dlib** (default): 128-dim euclidean, tolerance 0.5. Legacy — used by existing stored embeddings.
- **InsightFace** (`FACE_ENGINE=insightface`): buffalo_s ONNX CPU, 512-dim cosine, threshold 0.35. Faster on weak VPS.

Switching engines requires `python manage.py reenroll_faces` — stored embeddings are engine-specific (different dimensions). The matcher rejects cross-dimension comparisons.

---

## Flutter App (`/mobile/`)

### Structure

```
lib/
  main.dart          — App entry; MultiProvider(AuthState, ThemeController)
  api.dart           — HTTP client; auto-discovers Django at 10.0.2.2:9000/:8000
  auth.dart          — AuthState provider; JWT token in flutter_secure_storage
  theme.dart         — ShamelColors constants + light/dark ThemeData
  theme_controller.dart — ThemeController (shared_preferences persistence)
  widgets.dart       — StatCard, Shimmer, SkeletonBox, SkeletonList, LoadingOrError
  sections.dart      — Section/SectionGroup; sectionsFor(role) → drawer items per role
  screens/
    home_screen.dart       — Shell: Scaffold + BottomNavigationBar + IndexedStack + MenuDrawer
    dashboard_screen.dart  — Role-split: admin (infra) vs coordinator (academic) vs teacher/student
    login_screen.dart      — resizeToAvoidBottomInset:true; dark-mode card bg
    scan_screen.dart       — CameraController, face capture, API.scan()
    schedule_screen.dart   — bare widget (no Scaffold) — used both in IndexedStack tab and drawer
    resource_list_screen.dart — Generic paginated list with search; used by most drawer sections
    create_screens.dart    — Generic form scaffold (_FormScaffold) for create flows
    detail_screens.dart    — Generic detail scaffold (_DetailScaffold)
    menu_drawer.dart       — Full drawer built from sectionsFor(role)
```

### Navigation Model

`HomeScreen` uses `IndexedStack` (all tabs build simultaneously, even offstage).
- **SkeletonList** must use `shrinkWrap: true` — unbounded height crashes IndexedStack layout.
- Drawer sections push via `Navigator.push(MaterialPageRoute(...))`.
- `ScheduleScreen` is a bare body widget. When pushed from drawer it's wrapped in a `Scaffold+AppBar` (in `sections.dart`) so the back button appears. In the IndexedStack tab it uses the parent HomeScreen's AppBar.

### API Client

`Api.discover()` probes `10.0.2.2:9000 → :8000 → 127.0.0.1:9000 → :8000` in order.
Token stored in `flutter_secure_storage` under key `shamel_token`.
All authenticated requests: `Authorization: Bearer <token>`.

### Dark Mode

`ThemeController` reads/writes `shared_preferences` key `theme_mode`.
`ShamelApp` wraps in `Directionality(textDirection: TextDirection.rtl)` — app is RTL-first.
Dialog/dropdown backgrounds must use `Theme.of(context).colorScheme.surface`, not hardcoded white.

---

## Environment Variables (`.env`)

```
SECRET_KEY=...
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,...
DATABASE_NAME=...
DATABASE_USER=...
DATABASE_PASSWORD=...
DATABASE_HOST=84.46.251.93
DATABASE_PORT=5432
USE_LOCAL_DB=false        # set true to force SQLite
FACE_ENGINE=dlib          # or insightface
FACE_THRESHOLD=0.35       # insightface cosine
FACE_TOLERANCE=0.5        # dlib euclidean
DEPLOY_SECRET=...         # for live-reload push after deploy
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

---

## Known Constraints

- **Streaming routes** (`/scan/`, `/video_feed/`, `/admin-panel/notifications/`, `/live-stats/`) never reach `networkidle` — use `wait_until="commit"` in Playwright scripts.
- **No Tailwind PostCSS pipeline** — CDN only. `@apply` in template `<style>` blocks is silently ignored. Define all shared classes in `base.html`.
- **Dual-template path** — `TEMPLATES[0]['DIRS']` = `attendance/templates/templates`. The inner `templates/` is the app-level directory Django's `APP_DIRS` also scans. Some templates have copies in both paths; the outer path takes precedence.
- **`is_allowed_entry` on Teacher model** — field exists in DB but must NOT be toggled via UI. It's a legacy artifact; gate checks for teachers should be skipped or always pass.
