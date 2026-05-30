# -*- coding: utf-8 -*-
"""
SHAMEL — Screenshot suite v3
• Exact fixed dimensions — no full_page (content clipped to viewport)
  Desktop : 1920 × 1080
  Mobile  : 390  × 844
• All sessions pre-generated before Playwright
• Also generates documentation folder with annotated B&W wireframe images

Outputs:
  screenshots/desktop/   ← exact 1920×1080
  screenshots/mobile/    ← exact 390×844
  screenshots/docs/      ← annotated black-on-white for graduation docs
"""

import os, sys, django, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

os.chdir("D:/مهم/ACDC_FINAL-main")
sys.path.insert(0, "D:/مهم/ACDC_FINAL-main")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from attendance.models import Student, Teacher, Coordinator

User = get_user_model()

def make_session(user):
    c = Client()
    c.force_login(user)
    return c.cookies["sessionid"].value

admin_user   = User.objects.filter(is_superuser=True).first()
teacher_user = Teacher.objects.select_related('auth_user').first().auth_user
student_user = Student.objects.select_related('auth_user').first().auth_user
coord_user   = Coordinator.objects.select_related('auth_user').first().auth_user

SESSION = {
    'admin':       make_session(admin_user),
    'teacher':     make_session(teacher_user),
    'student':     make_session(student_user),
    'coordinator': make_session(coord_user),
    'anon':        None,
}
print("✅ Sessions:", {r: (s[:12]+'…' if s else 'anon') for r,s in SESSION.items()})

BASE  = "http://127.0.0.1:8000"
OUT_D = Path("screenshots/desktop");  OUT_D.mkdir(parents=True, exist_ok=True)
OUT_M = Path("screenshots/mobile");   OUT_M.mkdir(parents=True, exist_ok=True)
OUT_DOC = Path("screenshots/docs");   OUT_DOC.mkdir(parents=True, exist_ok=True)

VIEWPORT_D = {"width": 1920, "height": 1080}
VIEWPORT_M = {"width": 390,  "height": 844}

# (slug, url, role, timeout_ms, description for docs)
PAGES = [
    ("01_login",                      "/login/",                               "anon",        12000,
     "Login Screen — Username & password form with SHAMEL branding. Entry point for all users."),
    ("02_admin_panel",                "/admin-panel/",                         "admin",       15000,
     "Admin Dashboard — System overview: total students, teachers, attendance rate, real-time charts."),
    ("03_admin_gate_reports",         "/admin-panel/gate-reports/",            "admin",       15000,
     "Gate Reports — Log of all physical gate entry/exit events captured by face recognition."),
    ("04_admin_notifications",        "/admin-panel/notifications/",           "admin",       15000,
     "Admin Notifications — System-wide alerts: low attendance, errors, sync status."),
    ("05_admin_audit_log",            "/admin-panel/audit-log/",               "admin",       20000,
     "Audit Log — Full history of admin actions (creates, edits, deletes) with timestamps."),
    ("06_admin_departments",          "/admin-panel/departments/",             "admin",       15000,
     "Departments Management — CRUD for colleges and departments tree structure."),
    ("07_admin_onboarding",           "/admin-panel/onboarding/",              "admin",       15000,
     "Onboarding Wizard — Step-by-step setup guide for first-time system configuration."),
    ("08_admin_dean_evaluation",      "/admin-panel/dean-evaluation/",         "admin",       15000,
     "Dean Evaluation Dashboard — Attendance KPIs per college for executive review."),
    ("09_admin_faculty_timeline",     "/admin-panel/faculty-timeline/",        "admin",       15000,
     "Faculty Timeline — Visual schedule of all teachers across the week."),
    ("10_admin_excuse_board",         "/admin-panel/excuse-board/",            "admin",       15000,
     "Excuse Approval Board — Pending absence excuse requests awaiting admin decision."),
    ("11_admin_exam_planner",         "/admin-panel/exam-planner/",            "admin",       15000,
     "Exam Planner — Schedule exams, assign rooms and invigilators."),
    ("12_admin_exam_seating",         "/admin-panel/exam-seating/",            "admin",       15000,
     "Exam Seating Chart — Visual seat assignment map for examination halls."),
    ("13_admin_exam_gate",            "/admin-panel/exam-gate/",               "admin",       15000,
     "Exam Gate Verify — Face-scan verification at exam hall entrance."),
    ("14_admin_tickets",              "/admin-panel/tickets/",                 "admin",       15000,
     "Support Tickets (Admin) — All user-submitted support requests with status management."),
    ("15_faculty_management",         "/faculty-management/",                  "admin",       25000,
     "Faculty Management — Full directory of students and teachers with search and filters."),
    ("16_register_student",           "/faculty-management/register-student/", "admin",       15000,
     "Register Student — Form to enroll a new student with photo upload for face recognition."),
    ("17_register_teacher",           "/faculty-management/register-teacher/", "admin",       15000,
     "Register Teacher — Form to add a new teacher with department and academic rank."),
    ("18_reports_home",               "/reports/",                             "admin",       20000,
     "Reports Hub — Central page linking to all attendance analytics and export options."),
    ("19_reports_students",           "/reports/students/",                    "admin",       20000,
     "Student Attendance Report — Per-student attendance table with CSV/Excel/PDF export."),
    ("20_reports_teachers",           "/reports/teachers/",                    "admin",       25000,
     "Teacher Attendance Report — Teacher schedule adherence report with export options."),
    ("21_search",                     "/search/",                              "admin",       15000,
     "Global Search — System-wide search across students, teachers, courses, and logs."),
    ("22_settings",                   "/settings/",                            "admin",       15000,
     "System Settings — Configure language, theme, notifications, and detection thresholds."),
    ("23_notifications",              "/notifications/",                       "admin",       15000,
     "Notifications Inbox — All system notifications with read/unread status management."),
    ("24_tickets_list",               "/tickets/",                             "admin",       15000,
     "Support Tickets List — All tickets submitted by the current user with status tracking."),
    ("25_tickets_create",             "/tickets/create/",                      "admin",       15000,
     "Create Support Ticket — Form to submit a new technical or academic support request."),
    ("26_scan",                       "/scan/",                                "admin",       20000,
     "Scan Station — Live MJPEG camera feed with real-time face detection and attendance marking."),
    ("27_attendance_logs",            "/attendance-logs/",                     "admin",       15000,
     "Attendance Logs — Raw timestamped log of every face-scan event with confidence scores."),
    ("28_gate",                       "/gate/",                                "admin",       15000,
     "Gate Monitor — Security staff interface: face scan results with allow/deny status."),
    ("29_courses",                    "/courses/",                             "admin",       25000,
     "Courses List — Full catalog of all academic courses with college and credit hour details."),
    ("30_courses_add",                "/courses/add/",                         "admin",       25000,
     "Add Course — Form to create a new course with code, title, college, and credit hours."),
    ("31_classrooms",                 "/classrooms/",                          "admin",       15000,
     "Classrooms List — All physical rooms with capacity, type, and current occupancy status."),
    ("32_classrooms_status",          "/classrooms/status/",                   "admin",       20000,
     "Classrooms Status — Live occupancy map showing which rooms are currently in use."),
    ("33_classrooms_add",             "/classrooms/add/",                      "admin",       15000,
     "Add Classroom — Form to register a new room with name, capacity, type, and college."),
    ("34_schedule",                   "/schedule/",                            "admin",       20000,
     "Schedule List — Complete timetable showing all courses, teachers, rooms, and time slots."),
    ("35_schedule_add",               "/schedule/add/",                        "admin",       20000,
     "Add Schedule Slot — Form to assign a course/teacher/room to a specific day and time."),
    ("36_schedule_calendar",          "/schedule/calendar/",                   "admin",       20000,
     "Schedule Calendar — Visual weekly calendar view of all scheduled lectures."),
    ("37_enroll_face",                "/enroll-face/",                         "admin",       15000,
     "Face Enrollment — Camera capture interface to register a person's facial embeddings."),
    ("38_professor_dashboard",        "/professor-dashboard/",                 "teacher",     20000,
     "Teacher Dashboard — Active lecture session, real-time attendance list, today's schedule."),
    ("39_teacher_timeline",           "/teacher/timeline/",                    "teacher",     15000,
     "Teacher Timeline — Week-view of the teacher's own lecture schedule."),
    ("40_teacher_attendance_records", "/teacher/attendance-records/",          "teacher",     25000,
     "Teacher Attendance Records — Detailed per-session attendance with filter by course/date."),
    ("41_teacher_profile",            "/teacher/profile/",                     "teacher",     15000,
     "Teacher Profile — Personal info, academic rank, department, and face photo management."),
    ("42_student_dashboard",          "/student/dashboard/",                   "student",     20000,
     "Student Dashboard — Personal attendance summary, upcoming classes, recent alerts."),
    ("43_student_profile",            "/student/profile/",                     "student",     15000,
     "Student Profile — Student personal info, ID, enrollment year, and attendance history."),
    ("44_student_courses",            "/student/courses/",                     "student",     15000,
     "My Courses — List of enrolled courses with attendance percentage per subject."),
    ("45_student_schedule",           "/student/schedule/",                    "student",     15000,
     "My Schedule — Student's personal weekly timetable pulled from enrollment data."),
    ("46_student_excuse",             "/student/excuse/",                      "student",     15000,
     "Excuse Portal — Submit absence excuse with supporting document upload."),
    ("47_student_support",            "/student/support/",                     "student",     15000,
     "Student Support — Help center with FAQ and link to submit a support ticket."),
    ("48_coordinator_dashboard",      "/coordinator/dashboard/",               "coordinator", 20000,
     "Coordinator Dashboard — College-level KPIs: student count, attendance rate, course stats."),
    ("49_coordinator_students",       "/coordinator/students/",                "coordinator", 20000,
     "Coordinator Students — Full student roster for the coordinator's college with search."),
    ("50_coordinator_faculty",        "/coordinator/faculty/",                 "coordinator", 15000,
     "Coordinator Faculty — Teaching staff list for the college with schedules and stats."),
    ("51_coordinator_assignments",    "/coordinator/assignments/",             "coordinator", 15000,
     "Course Assignments — Assign courses to teachers and manage the college timetable."),
    ("52_coordinator_register",       "/coordinator/register/",                "coordinator", 15000,
     "Register User (Coordinator) — Add new students or teachers within the coordinator's college."),
    ("53_coordinator_grading",        "/coordinator/grading/",                 "coordinator", 15000,
     "Grading Overview — View and manage grade entries for courses in the college."),
    ("54_offline",                    "/offline/",                             "anon",        12000,
     "Offline Page — PWA fallback screen shown when the device has no internet connection."),
]


# ── Playwright capture ────────────────────────────────────────────────────────
from playwright.sync_api import sync_playwright

def capture(browser, url, role, timeout_ms, viewport, out_path):
    sid = SESSION[role]
    ctx = browser.new_context(
        viewport=viewport,
        permissions=[],                          # deny all permissions (camera, mic, etc.)
    )
    # Block camera/microphone at the browser level
    ctx.grant_permissions([], origin=BASE)
    if sid:
        ctx.add_cookies([{"name":"sessionid","value":sid,"domain":"127.0.0.1","path":"/"}])
    page = ctx.new_page()
    ok = False
    try:
        page.goto(BASE + url, wait_until="domcontentloaded", timeout=timeout_ms)
        try: page.wait_for_load_state("networkidle", timeout=min(timeout_ms//2, 8000))
        except Exception: pass
        page.keyboard.press("Escape")
    except Exception as e:
        print(f" ⚠nav({type(e).__name__})", end="")
    try:
        # Exact viewport screenshot — no full_page, so always exactly W×H
        page.screenshot(path=str(out_path), full_page=False, timeout=timeout_ms)
        ok = True
    except Exception as e:
        print(f" ❌ss({type(e).__name__})", end="")
    try: page.close()
    except Exception: pass
    try: ctx.close()
    except Exception: pass
    return ok


# ── Annotated docs image ──────────────────────────────────────────────────────
def make_doc_image(desktop_path: Path, mobile_path: Path, slug: str, description: str, out_path: Path):
    """White background, side-by-side desktop+mobile thumbnails, English description."""
    DOC_W, DOC_H = 2100, 900
    THUMB_D_W, THUMB_D_H = 960, 540     # desktop thumbnail (half 1920×1080)
    THUMB_M_W, THUMB_M_H = 195, 422     # mobile thumbnail (half 390×844)
    PAD = 40
    GREY = (220, 220, 220)
    BLACK = (20, 20, 20)
    DARK  = (60, 60, 60)

    doc = Image.new("RGB", (DOC_W, DOC_H), "white")
    draw = ImageDraw.Draw(doc)

    # Title bar
    draw.rectangle([0, 0, DOC_W, 70], fill=(30, 30, 30))
    try:
        title_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 28)
        sub_font   = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   20)
        body_font  = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   18)
        label_font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 16)
    except Exception:
        title_font = sub_font = body_font = label_font = ImageFont.load_default()

    title_text = slug.replace("_", " ").replace("-", " ").title()
    draw.text((PAD, 18), f"SHAMEL System — {title_text}", font=title_font, fill="white")

    # Description box
    desc_y = 90
    draw.rectangle([PAD, desc_y, DOC_W - PAD, desc_y + 70], fill=(245, 245, 245), outline=GREY, width=1)
    draw.text((PAD + 10, desc_y + 10), "Description:", font=label_font, fill=DARK)
    draw.text((PAD + 10, desc_y + 32), description, font=body_font, fill=BLACK)

    # Desktop thumbnail
    desk_x = PAD
    desk_y = desc_y + 90
    draw.rectangle([desk_x - 2, desk_y - 22, desk_x + THUMB_D_W + 2, desk_y + THUMB_D_H + 2],
                   fill=GREY, outline=(180,180,180), width=1)
    draw.text((desk_x, desk_y - 20), "Desktop View  (1920 × 1080)", font=label_font, fill=DARK)
    if desktop_path.exists():
        try:
            img = Image.open(desktop_path).convert("RGB")
            img = img.resize((THUMB_D_W, THUMB_D_H), Image.LANCZOS)
            doc.paste(img, (desk_x, desk_y))
        except Exception:
            draw.text((desk_x + 20, desk_y + 20), "[Image unavailable]", font=body_font, fill=DARK)
    else:
        draw.text((desk_x + 20, desk_y + 20), "[Not captured]", font=body_font, fill=DARK)

    # Mobile thumbnail
    mob_x = desk_x + THUMB_D_W + PAD * 2
    mob_y = desk_y
    draw.rectangle([mob_x - 2, mob_y - 22, mob_x + THUMB_M_W + 2, mob_y + THUMB_M_H + 2],
                   fill=GREY, outline=(180,180,180), width=1)
    draw.text((mob_x, mob_y - 20), "Mobile View  (390 × 844)", font=label_font, fill=DARK)
    if mobile_path.exists():
        try:
            img2 = Image.open(mobile_path).convert("RGB")
            img2 = img2.resize((THUMB_M_W, THUMB_M_H), Image.LANCZOS)
            doc.paste(img2, (mob_x, mob_y))
        except Exception:
            draw.text((mob_x + 10, mob_y + 20), "[Image unavailable]", font=body_font, fill=DARK)
    else:
        draw.text((mob_x + 10, mob_y + 20), "[Not captured]", font=body_font, fill=DARK)

    # Annotations column
    ann_x = mob_x + THUMB_M_W + PAD * 2
    ann_y = mob_y
    ann_w = DOC_W - ann_x - PAD

    draw.rectangle([ann_x, ann_y - 22, ann_x + ann_w, ann_y + THUMB_M_H + 2],
                   fill=(250, 250, 250), outline=GREY, width=1)
    draw.text((ann_x + 8, ann_y - 20), "Screen Details", font=label_font, fill=DARK)

    # Role badge
    role_map = {
        "01": "Public", "02": "Admin", "03": "Admin", "04": "Admin", "05": "Admin",
        "06": "Admin", "07": "Admin", "08": "Admin", "09": "Admin", "10": "Admin",
        "11": "Admin", "12": "Admin", "13": "Admin", "14": "Admin", "15": "Admin",
        "16": "Admin", "17": "Admin", "18": "Admin", "19": "Admin", "20": "Admin",
        "21": "Admin", "22": "Admin", "23": "Admin", "24": "Admin", "25": "Admin",
        "26": "Admin", "27": "Admin", "28": "Admin", "29": "Admin", "30": "Admin",
        "31": "Admin", "32": "Admin", "33": "Admin", "34": "Admin", "35": "Admin",
        "36": "Admin", "37": "Admin", "38": "Teacher", "39": "Teacher", "40": "Teacher",
        "41": "Teacher", "42": "Student", "43": "Student", "44": "Student", "45": "Student",
        "46": "Student", "47": "Student", "48": "Coordinator", "49": "Coordinator",
        "50": "Coordinator", "51": "Coordinator", "52": "Coordinator", "53": "Coordinator",
        "54": "Public",
    }
    num = slug[:2]
    role_label = role_map.get(num, "Admin")
    role_colors = {"Admin": (30,90,180), "Teacher": (20,140,80), "Student": (160,60,20),
                   "Coordinator": (120,30,150), "Public": (60,60,60)}
    rc = role_colors.get(role_label, (60,60,60))

    draw.rectangle([ann_x+8, ann_y+8, ann_x+130, ann_y+30], fill=rc)
    draw.text((ann_x+12, ann_y+10), f"Role: {role_label}", font=label_font, fill="white")

    # Key features list (derived from description)
    features = [
        f"• Screen {num} of 54",
        f"• Requires {role_label} login",
        f"• Responsive: desktop + mobile",
        f"• Arabic/English bilingual UI",
    ]
    fy = ann_y + 45
    for feat in features:
        draw.text((ann_x + 8, fy), feat, font=body_font, fill=BLACK)
        fy += 26

    # Footer
    draw.line([0, DOC_H - 36, DOC_W, DOC_H - 36], fill=GREY, width=1)
    draw.text((PAD, DOC_H - 28), "SHAMEL — Smart Holistic Attendance Management  |  Sudan University of Science and Technology",
              font=body_font, fill=DARK)
    draw.text((DOC_W - 220, DOC_H - 28), f"Screen {num} / 54", font=body_font, fill=DARK)

    doc.save(str(out_path), "PNG", optimize=True)


# ── Main ──────────────────────────────────────────────────────────────────────
total = len(PAGES)
print(f"\n📸 Capturing {total} pages × 2 viewports ({total*2} screenshots)…\n")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--disable-web-security"])

    for i, (slug, url, role, timeout_ms, desc) in enumerate(PAGES, 1):
        dp = OUT_D / f"{slug}.png"
        mp = OUT_M / f"{slug}.png"

        print(f"[{i:02d}/{total}] {slug}  ", end="", flush=True)

        # Desktop
        print("D:", end="", flush=True)
        ok_d = capture(browser, url, role, timeout_ms, VIEWPORT_D, dp)
        if ok_d: print(f"{Image.open(dp).size[1]}px ", end="", flush=True)
        time.sleep(0.6)

        # Mobile
        print("M:", end="", flush=True)
        ok_m = capture(browser, url, role, timeout_ms, VIEWPORT_M, mp)
        if ok_m: print(f"{Image.open(mp).size[1]}px ", end="", flush=True)
        time.sleep(0.6)

        print()

    browser.close()

print("\n🎨 Generating documentation images…\n")
for i, (slug, url, role, timeout_ms, desc) in enumerate(PAGES, 1):
    dp  = OUT_D   / f"{slug}.png"
    mp  = OUT_M   / f"{slug}.png"
    out = OUT_DOC / f"{slug}_doc.png"
    make_doc_image(dp, mp, slug, desc, out)
    print(f"  ✅  {slug}_doc.png")

d_ok  = sum(1 for p in PAGES if (OUT_D   / f"{p[0]}.png").exists())
m_ok  = sum(1 for p in PAGES if (OUT_M   / f"{p[0]}.png").exists())
doc_ok = sum(1 for p in PAGES if (OUT_DOC / f"{p[0]}_doc.png").exists())

print(f"\n🎉  Done!")
print(f"   screenshots/desktop/  — {d_ok} files @ 1920×1080")
print(f"   screenshots/mobile/   — {m_ok} files @ 390×844")
print(f"   screenshots/docs/     — {doc_ok} annotated documentation images")
