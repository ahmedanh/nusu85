# GEMINI.md — SHAMEL Project

## Memory
Read `C:\Users\ahmed\SecondBrain\Memory-Index.md` at session start.
Log changes to `C:\Users\ahmed\SecondBrain\01-Projects\SHAMEL\Log.md`.

## Stack
- Django 4.x web app + REST API (`/api/v1/`, token: `Authorization: Bearer`)
- Flutter 3.41 mobile (RTL-first, `Directionality(textDirection: TextDirection.rtl)`)
- Face recognition: dlib (128-dim) or InsightFace ONNX (512-dim, `FACE_ENGINE=insightface`)
- PostgreSQL (VPS) + SQLite fallback (`USE_LOCAL_DB=true python manage.py runserver`)

## Critical Constraints
- **Tailwind CDN only** — `@apply` in template `<style>` blocks is silently ignored. All shared CSS goes in `base.html` only.
- **Template path**: `attendance/templates/templates/attendance/` (double `templates/`)
- **Arabic-first**: all UI text needs Arabic translation. Full RTL layout.
- **`is_allowed_entry` on Teacher**: field exists in DB but must NOT be exposed in UI — do not add toggle.
- **5 roles**: `admin` (global), `coordinator` (college-scoped only), `teacher`, `student`, `gate`

## Key Files
| File | Purpose |
|------|---------|
| `attendance/views.py` | All web views (~3500 lines) |
| `attendance/api.py` + `api_extra.py` | JSON API endpoints |
| `attendance/models.py` | 22 models |
| `attendance/templates/templates/attendance/base.html` | All shared CSS/JS hub |
| `mobile/lib/` | Flutter app |

## Commands
```bash
python manage.py runserver 0.0.0.0:8000 --noreload
python manage.py makemigrations attendance && python manage.py migrate
python e2e_test.py
python autotest2.py
C:\develop\flutter\bin\flutter.bat run -d emulator-5554 --debug
C:\develop\flutter\bin\flutter.bat analyze --no-pub
```

## Code Style
- Conventional commits: `fix:` `feat:` `docs:` `test:` `refactor:`
- No comments unless WHY is non-obvious
- No features beyond what the task requires
