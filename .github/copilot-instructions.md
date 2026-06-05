# GitHub Copilot Instructions — SHAMEL Project

## Memory System
Primary memory is in the Obsidian vault at `C:\Users\ahmed\SecondBrain`.
Read `Memory-Index.md` before generating anything for this project.
After any task, append a compact summary to `C:\Users\ahmed\SecondBrain\01-Projects\SHAMEL\Log.md`.

## Stack
- Django 4.x (web + REST API at `/api/v1/`)
- Flutter 3.41 (mobile, RTL-first)
- Face recognition (dlib 128-dim or InsightFace 512-dim ONNX)
- PostgreSQL (VPS) with SQLite fallback

## Project Layout
- `attendance/views.py` — all web views (~3500 lines)
- `attendance/api.py` + `api_extra.py` — JSON API endpoints
- `attendance/models.py` — 22 models
- `mobile/lib/` — Flutter app
- Templates: `attendance/templates/templates/attendance/` (double templates/)

## Critical Rules
- Tailwind CDN only — `@apply` in template `<style>` blocks is silently ignored. Define shared classes in `base.html` only.
- Arabic-first (RTL). All UI text must have Arabic translations.
- 5 roles: admin (global), coordinator (college-scoped), teacher, student, gate
- `is_allowed_entry` on Teacher model exists but must NOT be toggled via UI.
- Do NOT add teacher gate toggle — intentionally removed.

## Code Style
- Conventional commits: `fix:`, `feat:`, `docs:`, `test:`, `refactor:`
- No comments unless WHY is non-obvious
- No features beyond what the task requires
- camelCase file naming
- Validate at system boundaries only

## Commands
```bash
# Django dev
python manage.py runserver 0.0.0.0:8000 --noreload

# Flutter
C:\develop\flutter\bin\flutter.bat run -d emulator-5554 --debug
C:\develop\flutter\bin\flutter.bat analyze --no-pub

# E2E tests
python e2e_test.py
python autotest2.py
```
