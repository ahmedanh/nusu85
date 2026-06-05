# -*- coding: utf-8 -*-
"""
Capture web screenshots — light theme, Arabic, viewport-bounded.
Uses /demo-login/?role=X endpoint so the SERVER creates sessions in its own DB.
"""
import pathlib, asyncio

OUT_DIR = pathlib.Path(__file__).parent / 'dddddd' / 'web_screenshots'
OUT_DIR.mkdir(parents=True, exist_ok=True)
BASE_URL = 'http://localhost:8000'

# Force light theme after page load
FORCE_LIGHT = """
    localStorage.setItem('acdc_theme', 'light');
    document.documentElement.classList.remove('dark');
"""
# Override localStorage reads before page scripts run
LIGHT_INIT = """
    const _orig = Storage.prototype.getItem;
    Storage.prototype.getItem = function(k) {
        if (k === 'acdc_theme') return 'light';
        return _orig.call(this, k);
    };
"""

PAGES = [
    # ── Auth (no login needed) ──
    ('web_01_login',          None,          '/login/'),
    ('web_02_face_login',     None,          '/login/face/'),
    # ── Admin ──
    ('web_03_admin_dash',     'admin',       '/admin-panel/'),
    ('web_04_gate_logs',      'admin',       '/admin-panel/gate-reports/'),
    ('web_05_schedule',       'admin',       '/schedule/'),
    ('web_06_student_detail', 'admin',       '/students/1/'),
    ('web_07_courses',        'admin',       '/courses/'),
    ('web_08_classrooms',     'admin',       '/classrooms/'),
    ('web_09_schedule_cal',   'admin',       '/schedule/calendar/'),
    ('web_10_audit',          'admin',       '/admin-panel/audit-log/'),
    ('web_11_notifications',  'admin',       '/admin-panel/notifications/'),
    ('web_12_departments',    'admin',       '/admin-panel/departments/'),
    ('web_13_onboarding',     'admin',       '/admin-panel/onboarding/'),
    ('web_14_enroll_face',    'admin',       '/enroll-face/'),
    ('web_31_teacher_detail', 'admin',       '/teachers/1/'),
    ('web_32_exam_gate',      'admin',       '/admin-panel/exam-gate/'),
    ('web_34_dean_eval',      'admin',       '/admin-panel/dean-evaluation/'),
    ('web_35_excuse_board',   'admin',       '/admin-panel/excuse-board/'),
    # ── Coordinator ──
    ('web_15_coord_dash',     'coordinator', '/coordinator/dashboard/'),
    ('web_16_coord_students', 'coordinator', '/coordinator/students/'),
    ('web_17_coord_faculty',  'coordinator', '/coordinator/faculty/'),
    ('web_18_coord_assign',   'coordinator', '/coordinator/assignments/'),
    ('web_19_coord_grading',  'coordinator', '/coordinator/grading/'),
    # ── Teacher ──
    ('web_20_teacher_dash',   'teacher',     '/professor-dashboard/'),
    ('web_21_teacher_sched',  'teacher',     '/schedule/'),
    ('web_22_teacher_records','teacher',     '/teacher/attendance-records/'),
    ('web_23_teacher_tl',     'teacher',     '/teacher/timeline/'),
    # ── Student ──
    ('web_24_student_dash',   'student',     '/student/dashboard/'),
    ('web_25_student_courses','student',     '/student/courses/'),
    ('web_26_student_sched',  'student',     '/student/schedule/'),
    ('web_27_student_excuse', 'student',     '/student/excuse/'),
    ('web_28_student_profile','student',     '/student/profile/'),
    # ── Gate ──
    ('web_29_gate_dash',      'gate',        '/gate/'),
    # ── Support ──
    ('web_30_tickets',        'student',     '/tickets/'),
]


async def do_demo_login(context, role):
    """Login via /demo-login/?role=X. Server creates session in its own DB."""
    page = await context.new_page()
    try:
        await page.goto(
            f'{BASE_URL}/demo-login/?role={role}',
            wait_until='domcontentloaded',
            timeout=12000,
        )
        await page.wait_for_timeout(600)
        url = page.url
        ok = '/login' not in url
        print(f'  demo-login {role}: {"OK" if ok else "FAILED"} → {url[-50:]}')
        return ok
    except Exception as e:
        print(f'  demo-login {role}: ERROR {e}')
        return False
    finally:
        await page.close()


async def capture_all():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # One persistent context per role (preserves session cookies)
        role_contexts = {}
        for role in ['admin', 'teacher', 'student', 'coordinator', 'gate']:
            ctx = await browser.new_context(
                viewport={'width': 1280, 'height': 900},
                locale='ar-SA',
            )
            await ctx.add_init_script(LIGHT_INIT)
            ok = await do_demo_login(ctx, role)
            if ok:
                role_contexts[role] = ctx
            else:
                await ctx.close()

        # Public context (no login)
        pub_ctx = await browser.new_context(
            viewport={'width': 1280, 'height': 900},
            locale='ar-SA',
        )
        await pub_ctx.add_init_script(LIGHT_INIT)

        for filename, role, path in PAGES:
            out_file = OUT_DIR / f'{filename}.png'
            ctx = role_contexts.get(role, pub_ctx) if role else pub_ctx
            page = await ctx.new_page()
            try:
                await page.goto(BASE_URL + path, wait_until='domcontentloaded', timeout=15000)
                await page.wait_for_timeout(1800)
                await page.evaluate(FORCE_LIGHT)
                await page.wait_for_timeout(300)
                await page.screenshot(
                    path=str(out_file),
                    clip={'x': 0, 'y': 0, 'width': 1280, 'height': 900},
                )
                final = page.url
                status = 'OK  ' if 'login' not in final else 'REDIR'
                print(f'{status} {filename}  ({final[-55:]})')
            except Exception as e:
                print(f'FAIL {filename}: {e}')
            finally:
                await page.close()

        for ctx in role_contexts.values():
            await ctx.close()
        await pub_ctx.close()
        await browser.close()

    print(f'\nDone. {len(PAGES)} screenshots → {OUT_DIR}')


if __name__ == '__main__':
    asyncio.run(capture_all())
