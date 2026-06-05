---
applyTo: "**"
---

# SHAMEL Project Instructions

## Stack
- Django 4.x + REST API at `/api/v1/` (token: `Authorization: Bearer`)
- Flutter 3.41, RTL-first (`Directionality(textDirection: TextDirection.rtl)`)
- Face recognition: dlib (128-dim) or InsightFace ONNX (512-dim)
- PostgreSQL (VPS 84.46.251.93) + SQLite fallback (`USE_LOCAL_DB=true`)

## Key Files
- `attendance/views.py` — all web views (~3500 lines)
- `attendance/api.py` + `api_extra.py` — JSON API
- `attendance/models.py` — 22 models
- `attendance/base.html` — Tailwind CDN config, all shared CSS/JS
- `mobile/lib/` — Flutter app

## Critical Constraints
- **Tailwind CDN only** — `@apply` in template `<style>` blocks is silently ignored. Define shared CSS in `base.html` only.
- **Template path**: `attendance/templates/templates/attendance/` (double `templates/`)
- **Arabic-first**: all UI text needs Arabic. RTL layout.
- **`is_allowed_entry` on Teacher**: field exists but must NOT be toggled via UI.
- 5 roles: `admin` (global), `coordinator` (college-scoped), `teacher`, `student`, `gate`

## Commands
```bash
python manage.py runserver 0.0.0.0:8000 --noreload
python e2e_test.py
C:\develop\flutter\bin\flutter.bat analyze --no-pub
C:\develop\flutter\bin\flutter.bat run -d emulator-5554
```

## Obsidian Log
After any change, append to: `C:\Users\ahmed\SecondBrain\01-Projects\SHAMEL\Log.md`
