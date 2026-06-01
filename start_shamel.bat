@echo off
REM ============================================================
REM  SHAMEL — one-click server launcher
REM  Starts BOTH the Django dev server (:8000) and the Daphne
REM  ASGI server (:9000). The mobile app auto-discovers either.
REM  Double-click this file before testing in the emulator.
REM ============================================================
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   SHAMEL servers starting...
echo   Web / PWA : http://127.0.0.1:8000
echo   Mobile API: http://127.0.0.1:9000  (emulator: 10.0.2.2:9000)
echo ============================================================
echo.

set USE_LOCAL_DB=true
set PYTHONIOENCODING=utf-8

REM Django dev server (web + PWA + API) on 8000
start "SHAMEL Web :8000" cmd /k "set USE_LOCAL_DB=true&& set PYTHONIOENCODING=utf-8&& python manage.py runserver 0.0.0.0:8000"

REM Daphne ASGI (API + websockets + scheduler) on 9000
start "SHAMEL API :9000" cmd /k "set USE_LOCAL_DB=true&& set PYTHONIOENCODING=utf-8&& python run_daphne.py"

echo Both servers launched in separate windows.
echo Keep those windows open while testing. Close them to stop.
echo.
echo Login accounts:
echo   admin            / Admin@1234     (System admin)
echo   coordinator_demo / Coord@1234     (Coordinator)
echo   tchr_13          / Teacher@1234   (Teacher)
echo   std_13           / Student@1234   (Student)
echo   gate             / Gate@1234      (Gate)
echo.
pause
