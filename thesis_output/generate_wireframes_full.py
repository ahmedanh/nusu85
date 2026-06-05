"""
SHAMEL System — Full Wireframe Generator
54 screens: 39 web + 15 mobile
Grayscale, academic blueprint style, 200dpi
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT = r"D:\مهم\ACDC_FINAL-main\thesis_output\wireframes"
os.makedirs(OUT, exist_ok=True)

# ── Color palette ──────────────────────────────────────────────
BG    = '#FFFFFF'
TEXT  = '#333333'
BORD  = '#AAAAAA'
HEAD  = '#DDDDDD'
BTN   = '#555555'
LIGHT = '#F5F5F5'
MID   = '#CCCCCC'

def save(fig, name):
    fig.savefig(os.path.join(OUT, name), dpi=200, bbox_inches='tight',
                facecolor=BG)
    plt.close(fig)
    print(f"  [OK] {name}")

# ── Helpers ────────────────────────────────────────────────────
def web_fig(title):
    fig, ax = plt.subplots(figsize=(14, 9))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1440); ax.set_ylim(0, 900)
    ax.invert_yaxis()
    ax.axis('off')
    ax.text(720, 18, title, ha='center', va='center',
            fontsize=11, fontweight='bold', color=TEXT,
            fontfamily='DejaVu Sans')
    return fig, ax

def mob_fig(title):
    fig, ax = plt.subplots(figsize=(5, 10))
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 375); ax.set_ylim(0, 812)
    ax.invert_yaxis()
    ax.axis('off')
    # Phone frame
    rect = FancyBboxPatch((5,5), 365, 802, boxstyle="round,pad=5",
                          linewidth=2, edgecolor=BORD, facecolor=BG)
    ax.add_patch(rect)
    ax.text(187, 22, title, ha='center', va='center',
            fontsize=6, fontweight='bold', color=TEXT, fontfamily='DejaVu Sans')
    return fig, ax

def box(ax, x, y, w, h, fc=HEAD, ec=BORD, lw=1, radius=3):
    r = FancyBboxPatch((x, y), w, h,
                       boxstyle=f"round,pad=1",
                       linewidth=lw, edgecolor=ec, facecolor=fc)
    ax.add_patch(r)

def rect(ax, x, y, w, h, fc=HEAD, ec=BORD, lw=1):
    r = mpatches.Rectangle((x, y), w, h,
                            linewidth=lw, edgecolor=ec, facecolor=fc)
    ax.add_patch(r)

def label(ax, x, y, txt, size=8, color=TEXT, ha='center', va='center', bold=False):
    fw = 'bold' if bold else 'normal'
    ax.text(x, y, txt, ha=ha, va=va, fontsize=size,
            color=color, fontfamily='DejaVu Sans', fontweight=fw)

def nav_web(ax, active=''):
    """Top navbar for web pages"""
    rect(ax, 0, 30, 1440, 45, fc=BTN, ec=BTN)
    label(ax, 120, 52, 'SHAMEL', size=12, color=BG, bold=True)
    items = ['Dashboard','Students','Schedule','Reports','Settings']
    for i, it in enumerate(items):
        label(ax, 350+i*130, 52, it, size=8, color=MID)
    label(ax, 1380, 52, '[USER]', size=8, color=MID)

def sidebar_web(ax, items, active=0):
    """Left sidebar"""
    rect(ax, 0, 75, 180, 825, fc=LIGHT, ec=BORD)
    for i, it in enumerate(items):
        y = 110 + i*36
        fc2 = MID if i==active else LIGHT
        rect(ax, 2, y-12, 176, 28, fc=fc2, ec='none')
        label(ax, 90, y+2, it, size=8, ha='center')

def stat_cards(ax, x0, y0, cards, w=200, h=70):
    for i, (title, val) in enumerate(cards):
        x = x0 + i*(w+20)
        box(ax, x, y0, w, h, fc=LIGHT)
        label(ax, x+w//2, y0+20, title, size=7, color=BORD)
        label(ax, x+w//2, y0+48, val, size=16, bold=True)

def table_header(ax, x, y, cols, widths):
    rect(ax, x, y, sum(widths), 24, fc=HEAD, ec=BORD)
    cx = x
    for col, w in zip(cols, widths):
        label(ax, cx+w//2, y+12, col, size=7, bold=True)
        cx += w

def table_rows(ax, x, y0, n_rows, widths, row_h=22):
    total_w = sum(widths)
    for i in range(n_rows):
        fc2 = BG if i%2==0 else LIGHT
        rect(ax, x, y0+i*row_h, total_w, row_h, fc=fc2, ec=BORD, lw=0.5)
        cx = x
        for w in widths:
            rect(ax, cx, y0+i*row_h, w, row_h, fc='none', ec=BORD, lw=0.3)
            cx += w

def btn(ax, x, y, w, h, text, fc=BTN, tc=BG):
    box(ax, x, y, w, h, fc=fc, ec=BTN)
    label(ax, x+w//2, y+h//2, text, size=7, color=tc, bold=True)

def search_bar(ax, x, y, w, h=28):
    box(ax, x, y, w, h, fc=BG, ec=BORD)
    label(ax, x+14, y+h//2, '[SEARCH] Search...', size=8, color=BORD, ha='left')

def chart_area(ax, x, y, w, h, title=''):
    rect(ax, x, y, w, h, fc=LIGHT, ec=BORD)
    if title:
        label(ax, x+w//2, y+14, title, size=8, bold=True)
    # Fake bar chart
    bar_w = (w-60) / 7
    for i in range(7):
        bh = np.random.randint(20, h-50)
        rect(ax, x+30+i*(bar_w+4), y+h-bh-10, bar_w, bh, fc=MID, ec=BORD, lw=0.5)

def line_chart(ax, x, y, w, h, title=''):
    rect(ax, x, y, w, h, fc=LIGHT, ec=BORD)
    if title:
        label(ax, x+w//2, y+14, title, size=8, bold=True)
    xs = np.linspace(x+20, x+w-20, 12)
    ys = y+h-20 - np.random.randint(10, h-40, 12)
    ax.plot(xs, ys, color=BTN, linewidth=1.5)

# ═══════════════════════════════════════════════════════════════
# AUTH PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_01_login():
    fig, ax = web_fig("Wireframe WF-001: Login Page")
    # Center card
    box(ax, 520, 200, 400, 460, fc=LIGHT, ec=BORD, lw=2)
    label(ax, 720, 250, 'SHAMEL', size=20, bold=True)
    label(ax, 720, 280, 'Smart Attendance Management System', size=8, color=BORD)
    # Fields
    for i, (lbl, yy) in enumerate([('Username / Email', 340), ('Password', 420)]):
        label(ax, 560, yy-14, lbl, size=8, ha='left')
        box(ax, 560, yy, 320, 32, fc=BG, ec=BORD)
    btn(ax, 560, 480, 320, 36, 'LOGIN')
    label(ax, 720, 540, 'Forgot password?', size=8, color=BTN)
    save(fig, 'wf_web_01_login.png')

def wf_web_02_password_reset():
    fig, ax = web_fig("Wireframe WF-002: Password Reset")
    box(ax, 520, 220, 400, 380, fc=LIGHT, ec=BORD, lw=2)
    label(ax, 720, 260, 'Reset Password', size=14, bold=True)
    label(ax, 720, 290, 'Enter your email to receive reset link', size=8, color=BORD)
    label(ax, 560, 346, 'Email Address', size=8, ha='left')
    box(ax, 560, 360, 320, 32, fc=BG, ec=BORD)
    btn(ax, 560, 420, 320, 36, 'SEND RESET LINK')
    label(ax, 720, 480, 'Back to Login', size=8, color=BTN)
    save(fig, 'wf_web_02_password_reset.png')

# ═══════════════════════════════════════════════════════════════
# ADMIN PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_03_admin_dashboard():
    fig, ax = web_fig("Wireframe WF-003: Admin Dashboard")
    nav_web(ax)
    sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                     'Courses','Schedule','Classrooms','Reports',
                     'Analytics','Settings','Notifications','Audit'], 0)
    # Content area x=190
    label(ax, 820, 100, 'Admin Control Panel', size=13, bold=True, ha='center')
    stat_cards(ax, 200, 120, [('Total Students','1,240'),('Sessions Today','18'),
                               ('Gate Entries','342'),('Face Accuracy','94.2%')], w=240)
    # Chart
    chart_area(ax, 200, 220, 600, 200, 'Weekly Attendance Rate (%)')
    # Gate log table
    label(ax, 310, 440, 'Recent Gate Log', size=9, bold=True, ha='center')
    cols = ['Time','Student','Photo','Score','Direction','Status']
    ws = [80,160,60,80,100,100]
    table_header(ax, 200, 455, cols, ws)
    table_rows(ax, 200, 479, 6, ws)
    # Notifications panel
    rect(ax, 840, 220, 340, 300, fc=LIGHT, ec=BORD)
    label(ax, 1010, 238, '[BELL] Notifications', size=9, bold=True)
    for i in range(5):
        rect(ax, 850, 255+i*46, 320, 38, fc=BG, ec=BORD, lw=0.5)
        label(ax, 860, 262+i*46, f'Notification item {i+1}', size=7, ha='left')
        label(ax, 860, 276+i*46, '2 min ago', size=6, color=BORD, ha='left')
    save(fig, 'wf_web_03_admin_dashboard.png')

def wf_web_04_admin_gate_logs():
    fig, ax = web_fig("Wireframe WF-004: Admin Gate Logs")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 1)
    label(ax, 820, 95, 'Gate Logs', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 400)
    btn(ax, 620, 110, 120, 28, 'Filter by Date')
    btn(ax, 760, 110, 100, 28, 'Export CSV')
    cols = ['Time','Student ID','Student Name','Photo','Score','Direction','Status','Action']
    ws = [90,90,160,60,80,90,90,90]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 14, ws)
    # Pagination
    label(ax, 720, 495, '< 1  2  3  4  5 >', size=9, color=BTN)
    save(fig, 'wf_web_04_admin_gate_logs.png')

def wf_web_05_admin_faculty():
    fig, ax = web_fig("Wireframe WF-005: Faculty Management")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 2)
    label(ax, 820, 95, 'Faculty Management', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 350)
    btn(ax, 1060, 110, 130, 28, '+ Add Teacher')
    cols = ['ID','Name','Department','Email','Courses','Status','Actions']
    ws = [60,180,160,200,80,80,90]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 12, ws)
    label(ax, 720, 490, '< 1  2  3 >', size=9, color=BTN)
    save(fig, 'wf_web_05_admin_faculty.png')

def wf_web_06_admin_students():
    fig, ax = web_fig("Wireframe WF-006: Students List")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 3)
    label(ax, 820, 95, 'Students', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 300)
    # Filters
    for i, f in enumerate(['College','Department','Year']):
        box(ax, 520+i*130, 110, 120, 28, fc=BG, ec=BORD)
        label(ax, 540+i*130, 124, f, size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, '+ Add Student')
    cols = ['ID','Name','College','Dept','Year','Attendance%','Status','Actions']
    ws = [60,160,120,120,60,90,80,80]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 13, ws)
    label(ax, 720, 495, '< 1  2  3  4 >', size=9, color=BTN)
    save(fig, 'wf_web_06_admin_students.png')

def wf_web_07_admin_courses():
    fig, ax = web_fig("Wireframe WF-007: Courses Management")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 4)
    label(ax, 820, 95, 'Courses', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 300)
    btn(ax, 1060, 110, 130, 28, '+ Add Course')
    cols = ['Code','Course Name','Department','Credits','Teacher','Students','Actions']
    ws = [80,200,150,70,160,80,110]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 12, ws)
    label(ax, 720, 490, '< 1  2 >', size=9, color=BTN)
    save(fig, 'wf_web_07_admin_courses.png')

def wf_web_08_admin_schedule():
    fig, ax = web_fig("Wireframe WF-008: Schedule Table")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 5)
    label(ax, 820, 95, 'Schedule', size=13, bold=True, ha='center')
    btn(ax, 200, 110, 120, 28, 'Table View', fc=BTN)
    btn(ax, 330, 110, 120, 28, 'Calendar View', fc=LIGHT, tc=TEXT)
    btn(ax, 1060, 110, 130, 28, '+ Add Schedule')
    cols = ['Day','Time','Course','Teacher','Classroom','Students','Actions']
    ws = [90,120,200,160,100,80,100]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 14, ws)
    save(fig, 'wf_web_08_admin_schedule.png')

def wf_web_09_admin_schedule_calendar():
    fig, ax = web_fig("Wireframe WF-009: Schedule Calendar View")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 5)
    label(ax, 820, 95, 'Schedule — Calendar View', size=13, bold=True, ha='center')
    btn(ax, 200, 110, 120, 28, 'Table View', fc=LIGHT, tc=TEXT)
    btn(ax, 330, 110, 120, 28, 'Calendar View', fc=BTN)
    days = ['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday']
    col_w = 200
    x0 = 200
    for i, d in enumerate(days):
        rect(ax, x0+i*col_w, 155, col_w, 30, fc=HEAD, ec=BORD)
        label(ax, x0+i*col_w+col_w//2, 170, d, size=8, bold=True)
    times = ['08:00','09:30','11:00','12:30','14:00','15:30']
    for r, t in enumerate(times):
        label(ax, x0-30, 200+r*100+30, t, size=7, color=BORD)
        for c in range(6):
            rect(ax, x0+c*col_w, 200+r*100, col_w, 100, fc=BG, ec=BORD, lw=0.5)
            if (r+c)%3==0:
                box(ax, x0+c*col_w+4, 205+r*100, col_w-8, 80, fc=LIGHT, ec=MID)
                label(ax, x0+c*col_w+col_w//2, 242+r*100, f'CS-{100+c+r}', size=7)
                label(ax, x0+c*col_w+col_w//2, 258+r*100, f'Room A{r+1}', size=6, color=BORD)
    save(fig, 'wf_web_09_admin_schedule_calendar.png')

def wf_web_10_admin_classrooms():
    fig, ax = web_fig("Wireframe WF-010: Classrooms")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 6)
    label(ax, 820, 95, 'Classrooms', size=13, bold=True, ha='center')
    btn(ax, 1060, 110, 130, 28, '+ Add Classroom')
    # Grid of classroom cards
    for i in range(12):
        r, c = divmod(i, 4)
        x = 200 + c*300; y = 140 + r*180
        box(ax, x, y, 270, 155, fc=LIGHT, ec=BORD, lw=1.5)
        label(ax, x+135, y+25, f'Room {101+i}', size=10, bold=True)
        label(ax, x+135, y+50, 'Building A — Floor 2', size=7, color=BORD)
        label(ax, x+135, y+75, f'Capacity: {30+i*5}', size=8)
        status = 'Occupied' if i%3==0 else 'Available'
        fc_s = MID if status=='Occupied' else LIGHT
        box(ax, x+80, y+100, 110, 22, fc=fc_s, ec=BORD)
        label(ax, x+135, y+111, status, size=7)
        btn(ax, x+70, y+128, 60, 18, 'Edit', fc=LIGHT, tc=TEXT)
        btn(ax, x+140, y+128, 60, 18, 'Delete', fc=LIGHT, tc=TEXT)
    save(fig, 'wf_web_10_admin_classrooms.png')

def wf_web_11_admin_reports():
    fig, ax = web_fig("Wireframe WF-011: Reports Hub")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 7)
    label(ax, 820, 95, 'Reports', size=13, bold=True, ha='center')
    reports = [
        ('Attendance Report','Full attendance by course/student','PDF','Excel','CSV'),
        ('Gate Log Report','All gate entry/exit records','PDF','Excel','CSV'),
        ('Grade Report','Course grades and GPA','PDF','Excel','CSV'),
        ('Student Report','Enrolled students overview','PDF','Excel','CSV'),
        ('Faculty Report','Teachers and course load','PDF','Excel','CSV'),
        ('At-Risk Students','Below 75% attendance','PDF','Excel','CSV'),
    ]
    for i, (title, desc, *fmts) in enumerate(reports):
        r, c = divmod(i, 2)
        x = 200+c*600; y = 130+r*190
        box(ax, x, y, 560, 165, fc=LIGHT, ec=BORD, lw=1.5)
        label(ax, x+280, y+28, title, size=11, bold=True)
        label(ax, x+280, y+52, desc, size=8, color=BORD)
        for j, fmt in enumerate(fmts):
            btn(ax, x+120+j*130, y+100, 100, 32, f'[DL] {fmt}')
    save(fig, 'wf_web_11_admin_reports.png')

def wf_web_12_admin_analytics():
    fig, ax = web_fig("Wireframe WF-012: Analytics")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 8)
    label(ax, 820, 95, 'Analytics', size=13, bold=True, ha='center')
    # Date range
    box(ax, 200, 110, 160, 28, fc=BG, ec=BORD)
    label(ax, 210, 124, 'From: 2026-01-01', size=7, ha='left')
    box(ax, 375, 110, 160, 28, fc=BG, ec=BORD)
    label(ax, 385, 124, 'To: 2026-06-01', size=7, ha='left')
    btn(ax, 550, 110, 80, 28, 'Apply')
    chart_area(ax, 200, 155, 590, 200, 'Monthly Attendance Rate')
    line_chart(ax, 810, 155, 420, 200, 'Daily Gate Entries')
    chart_area(ax, 200, 380, 280, 180, 'By Department')
    chart_area(ax, 500, 380, 280, 180, 'By Year')
    rect(ax, 800, 380, 430, 180, fc=LIGHT, ec=BORD)
    label(ax, 1015, 398, 'At-Risk Students (< 75%)', size=9, bold=True)
    cols = ['Student','Dept','Attendance%']
    ws = [180,130,120]
    table_header(ax, 810, 415, cols, ws)
    table_rows(ax, 810, 439, 5, ws)
    save(fig, 'wf_web_12_admin_analytics.png')

def wf_web_13_admin_search():
    fig, ax = web_fig("Wireframe WF-013: Global Search")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], -1)
    label(ax, 820, 95, 'Search Results', size=13, bold=True, ha='center')
    box(ax, 300, 110, 740, 34, fc=BG, ec=BTN, lw=2)
    label(ax, 320, 127, '[SEARCH]  "attendance report"', size=9, ha='left')
    btn(ax, 1050, 110, 80, 34, 'Search')
    for i, (section, items) in enumerate([
        ('Students', ['Ahmed Ali — ID:2021001','Sara Hassan — ID:2021042','Omar Musa — ID:2022015']),
        ('Teachers', ['Dr. Khaled — Computer Science','Prof. Amira — Math']),
        ('Courses', ['CS301 — Algorithms','CS401 — AI & Machine Learning']),
    ]):
        y = 165 + i*160
        label(ax, 210, y, section, size=10, bold=True, ha='left')
        for j, item in enumerate(items):
            box(ax, 200, y+18+j*38, 900, 30, fc=LIGHT, ec=BORD)
            label(ax, 220, y+33+j*38, item, size=8, ha='left')
    save(fig, 'wf_web_13_admin_search.png')

def wf_web_14_admin_settings():
    fig, ax = web_fig("Wireframe WF-014: System Settings")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 9)
    label(ax, 820, 95, 'System Settings', size=13, bold=True, ha='center')
    sections = [
        ('General', ['University Name','Academic Year','Timezone']),
        ('Face Recognition', ['Engine (dlib/insightface)','Tolerance Threshold','Min Confidence']),
        ('Attendance Policy', ['Min Attendance %','Late Grace Period (min)','Auto-mark Absent After']),
        ('Email Notifications', ['SMTP Host','SMTP Port','From Address']),
    ]
    col_w = 560
    for si, (sec, fields) in enumerate(sections):
        r, c = divmod(si, 2)
        bx = 200+c*col_w; by = 130+r*230
        box(ax, bx, by, col_w-20, 200, fc=LIGHT, ec=BORD, lw=1.5)
        label(ax, bx+20, by+20, sec, size=10, bold=True, ha='left')
        for fi, f in enumerate(fields):
            label(ax, bx+20, by+55+fi*46, f, size=8, ha='left')
            box(ax, bx+20, by+67+fi*46, col_w-60, 26, fc=BG, ec=BORD)
    btn(ax, 580, 820, 160, 36, 'Save Settings')
    save(fig, 'wf_web_14_admin_settings.png')

def wf_web_15_admin_notifications():
    fig, ax = web_fig("Wireframe WF-015: Notifications")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 10)
    label(ax, 820, 95, 'Notifications', size=13, bold=True, ha='center')
    btn(ax, 200, 110, 100, 28, 'All')
    btn(ax, 308, 110, 100, 28, 'Unread', fc=LIGHT, tc=TEXT)
    btn(ax, 416, 110, 100, 28, 'System', fc=LIGHT, tc=TEXT)
    btn(ax, 1100, 110, 90, 28, 'Mark All Read', fc=LIGHT, tc=TEXT)
    for i in range(12):
        y = 155+i*52
        is_unread = i%3 == 0
        box(ax, 200, y, 980, 44, fc=LIGHT if is_unread else BG, ec=BORD)
        if is_unread:
            rect(ax, 200, y, 4, 44, fc=BTN, ec='none')
        label(ax, 225, y+14, f'[BELL] Notification title {i+1}', size=9, ha='left', bold=is_unread)
        label(ax, 225, y+30, 'Notification description text here...', size=7, color=BORD, ha='left')
        label(ax, 1150, y+22, f'{i+1}h ago', size=7, color=BORD)
    save(fig, 'wf_web_15_admin_notifications.png')

def wf_web_16_admin_audit():
    fig, ax = web_fig("Wireframe WF-016: Audit Log")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Gate Logs','Faculty','Students',
                                   'Courses','Schedule','Classrooms','Reports',
                                   'Analytics','Settings','Notifications','Audit'], 11)
    label(ax, 820, 95, 'Audit Log', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 300)
    box(ax, 515, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 525, 124, 'Filter: Action', size=7, color=BORD, ha='left')
    box(ax, 660, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 670, 124, 'Filter: User', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, 'Export CSV')
    cols = ['Timestamp','User','Role','Action','Object','IP Address','Details']
    ws = [130,130,80,120,160,110,130]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 14, ws)
    label(ax, 720, 495, '< 1  2  3  4  5 >', size=9, color=BTN)
    save(fig, 'wf_web_16_admin_audit.png')

# ═══════════════════════════════════════════════════════════════
# TEACHER PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_17_teacher_dashboard():
    fig, ax = web_fig("Wireframe WF-017: Teacher Dashboard")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 0)
    label(ax, 820, 95, 'Professor Dashboard', size=13, bold=True, ha='center')
    stat_cards(ax, 200, 120, [('My Courses','5'),('Sessions Today','2'),
                               ('Avg Attendance','78%'),('Pending Records','3')], w=240)
    # Course cards
    label(ax, 250, 215, 'My Courses', size=10, bold=True, ha='left')
    for i in range(5):
        x = 200 + i*240
        box(ax, x, 235, 220, 120, fc=LIGHT, ec=BORD, lw=1.5)
        label(ax, x+110, x-80, f'CS{301+i}', size=11, bold=True)  # placeholder
        label(ax, x+110, 262, f'CS{301+i} — Algorithms {i+1}', size=9, bold=True)
        label(ax, x+110, 282, f'Section {i+1} — 35 students', size=7, color=BORD)
        label(ax, x+110, 306, f'Attendance: {72+i*4}%', size=8)
        btn(ax, x+60, 328, 100, 22, 'View Sessions')
    # Today sessions
    label(ax, 250, 380, "Today's Sessions", size=10, bold=True, ha='left')
    cols = ['Course','Time','Classroom','Students','Status','Action']
    ws = [180,120,120,80,100,100]
    table_header(ax, 200, 398, cols, ws)
    table_rows(ax, 200, 422, 3, ws)
    save(fig, 'wf_web_17_teacher_dashboard.png')

def wf_web_18_teacher_sessions():
    fig, ax = web_fig("Wireframe WF-018: Lecture Sessions")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 1)
    label(ax, 820, 95, 'Lecture Sessions', size=13, bold=True, ha='center')
    box(ax, 200, 110, 150, 28, fc=BG, ec=BORD)
    label(ax, 210, 124, 'Filter: Course', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, '+ Open Session')
    cols = ['Date','Course','Classroom','Start','End','Students Present','Status','Actions']
    ws = [90,150,100,70,70,120,90,110]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 13, ws)
    label(ax, 720, 490, '< 1  2  3 >', size=9, color=BTN)
    save(fig, 'wf_web_18_teacher_sessions.png')

def wf_web_19_teacher_attendance():
    fig, ax = web_fig("Wireframe WF-019: Mark Attendance")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 2)
    label(ax, 820, 95, 'Mark Attendance', size=13, bold=True, ha='center')
    # Session info
    box(ax, 200, 110, 900, 38, fc=LIGHT, ec=BORD)
    label(ax, 220, 120, 'Session: CS301 — Algorithms | Date: 2026-06-04 | Room: A101', size=8, ha='left')
    label(ax, 220, 136, 'Status: IN PROGRESS', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 36, 'Save & Close')
    cols = ['#','Student ID','Student Name','Present','Absent','Late','Notes']
    ws = [40,90,200,70,70,70,220]
    table_header(ax, 200, 165, cols, ws)
    for i in range(16):
        fc2 = BG if i%2==0 else LIGHT
        rect(ax, 200, 189+i*38, sum(ws), 38, fc=fc2, ec=BORD, lw=0.5)
        label(ax, 220, 208+i*38, str(i+1), size=7)
        label(ax, 245, 208+i*38, f'2021{100+i:03d}', size=7)
        label(ax, 335, 208+i*38, f'Student Name {i+1}', size=7, ha='left')
        # Checkboxes
        for j, xc in enumerate([505, 575, 645]):
            box(ax, xc+15, 196+i*38, 22, 22, fc=BG, ec=BORD)
            if j==0 and i%5!=3: label(ax, xc+26, 208+i*38, '[OK]', size=6)
    save(fig, 'wf_web_19_teacher_attendance.png')

def wf_web_20_teacher_timeline():
    fig, ax = web_fig("Wireframe WF-020: Session Timeline")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 3)
    label(ax, 820, 95, 'Session Timeline', size=13, bold=True, ha='center')
    box(ax, 200, 110, 150, 28, fc=BG, ec=BORD)
    label(ax, 210, 124, 'Filter: Course', size=7, color=BORD, ha='left')
    # Timeline items
    ax.plot([280, 280], [145, 850], color=BORD, linewidth=2)
    for i in range(10):
        y = 165 + i*68
        # Dot
        circle = plt.Circle((280, y), 8, fc=BTN, ec=BTN)
        ax.add_patch(circle)
        box(ax, 310, y-24, 850, 54, fc=LIGHT, ec=BORD)
        label(ax, 330, y-12, f'2026-05-{28-i:02d}', size=7, color=BORD, ha='left', bold=True)
        label(ax, 330, y+4, f'CS{301+i%5} — Lecture Session  |  Room A{i%4+1}  |  08:00–09:30', size=8, ha='left')
        label(ax, 330, y+18, f'Present: {30+i} / 35  |  Absent: {5-i%5}', size=7, color=BORD, ha='left')
        btn(ax, 1080, y-8, 70, 24, 'View')
    save(fig, 'wf_web_20_teacher_timeline.png')

def wf_web_21_teacher_records():
    fig, ax = web_fig("Wireframe WF-021: Attendance Records")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 4)
    label(ax, 820, 95, 'Attendance Records', size=13, bold=True, ha='center')
    box(ax, 200, 110, 160, 28, fc=BG, ec=BORD)
    label(ax, 210, 124, 'Select Course', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, 'Export Excel')
    cols = ['Student ID','Student Name','Total Sessions','Present','Absent','Late','Attendance%','Status']
    ws = [80,160,110,70,70,70,100,100]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 14, ws)
    save(fig, 'wf_web_21_teacher_records.png')

def wf_web_22_teacher_schedule():
    fig, ax = web_fig("Wireframe WF-022: Teacher Schedule")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Sessions','Attendance','Timeline',
                                   'Records','Schedule'], 5)
    label(ax, 820, 95, 'My Schedule', size=13, bold=True, ha='center')
    days = ['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday']
    col_w = 195; x0 = 200
    for i, d in enumerate(days):
        rect(ax, x0+i*col_w, 120, col_w, 28, fc=HEAD, ec=BORD)
        label(ax, x0+i*col_w+col_w//2, 134, d, size=8, bold=True)
    times = ['08:00','09:30','11:00','12:30','14:00','15:30','17:00']
    for r, t in enumerate(times):
        label(ax, x0-30, 162+r*90+30, t, size=7, color=BORD)
        for c in range(6):
            rect(ax, x0+c*col_w, 162+r*90, col_w, 90, fc=BG, ec=BORD, lw=0.5)
            if (r+c)%4<2:
                box(ax, x0+c*col_w+4, 166+r*90, col_w-8, 80, fc=LIGHT, ec=MID)
                label(ax, x0+c*col_w+col_w//2, 198+r*90, f'CS-{200+c}', size=8)
                label(ax, x0+c*col_w+col_w//2, 214+r*90, f'Room B{c+1}', size=6, color=BORD)
    save(fig, 'wf_web_22_teacher_schedule.png')

# ═══════════════════════════════════════════════════════════════
# STUDENT PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_23_student_dashboard():
    fig, ax = web_fig("Wireframe WF-023: Student Dashboard")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 0)
    label(ax, 820, 95, 'Student Dashboard', size=13, bold=True, ha='center')
    # Gauge
    box(ax, 200, 120, 200, 200, fc=LIGHT, ec=BORD, lw=1.5)
    label(ax, 300, 175, 'Attendance', size=9, bold=True)
    circle = plt.Circle((300, 225), 55, fc='none', ec=BORD, linewidth=8)
    ax.add_patch(circle)
    label(ax, 300, 225, '82%', size=18, bold=True)
    label(ax, 300, 300, 'Overall', size=7, color=BORD)
    # Stat cards
    stat_cards(ax, 420, 120, [('Enrolled Courses','6'),('Present','48'),
                               ('Absent','10'),('Medical Excuses','2')], w=190)
    # Course table
    label(ax, 250, 345, 'Course Attendance', size=10, bold=True, ha='left')
    cols = ['Course','Sessions','Present','Absent','Attendance%','Status']
    ws = [200,90,80,80,100,110]
    table_header(ax, 200, 362, cols, ws)
    table_rows(ax, 200, 386, 6, ws)
    # Today schedule
    label(ax, 820, 345, "Today's Schedule", size=10, bold=True, ha='left')
    for i in range(3):
        box(ax, 810, 362+i*68, 370, 58, fc=LIGHT, ec=BORD)
        label(ax, 830, 380+i*68, f'CS{301+i} — Course Name', size=9, bold=True, ha='left')
        label(ax, 830, 398+i*68, f'08:{i*2}0 — Room A{i+1}', size=7, color=BORD, ha='left')
    save(fig, 'wf_web_23_student_dashboard.png')

def wf_web_24_student_courses():
    fig, ax = web_fig("Wireframe WF-024: My Courses")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 1)
    label(ax, 820, 95, 'My Courses', size=13, bold=True, ha='center')
    for i in range(6):
        r, c = divmod(i, 2)
        x = 200+c*600; y = 120+r*220
        box(ax, x, y, 560, 195, fc=LIGHT, ec=BORD, lw=1.5)
        label(ax, x+20, y+28, f'CS{301+i} — Course Title {i+1}', size=11, bold=True, ha='left')
        label(ax, x+20, y+52, f'Dr. Teacher Name  |  Credits: {3+i%2}', size=8, color=BORD, ha='left')
        # Progress bar
        pct = 65+i*5
        rect(ax, x+20, y+75, 520, 14, fc=MID, ec=BORD, lw=0.5)
        rect(ax, x+20, y+75, int(520*pct/100), 14, fc=BTN, ec='none')
        label(ax, x+20, y+105, f'Attendance: {pct}%  |  Present: {30+i}  |  Absent: {5-i%4}', size=8, ha='left')
        btn(ax, x+20, y+135, 120, 28, 'View Sessions')
        btn(ax, x+150, y+135, 120, 28, 'View Grades')
    save(fig, 'wf_web_24_student_courses.png')

def wf_web_25_student_schedule():
    fig, ax = web_fig("Wireframe WF-025: Student Schedule")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 2)
    label(ax, 820, 95, 'My Schedule', size=13, bold=True, ha='center')
    days = ['Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday']
    col_w = 195; x0 = 200
    for i, d in enumerate(days):
        rect(ax, x0+i*col_w, 120, col_w, 28, fc=HEAD, ec=BORD)
        label(ax, x0+i*col_w+col_w//2, 134, d, size=8, bold=True)
    times = ['08:00','09:30','11:00','12:30','14:00','15:30','17:00']
    for r, t in enumerate(times):
        label(ax, x0-30, 162+r*90+30, t, size=7, color=BORD)
        for c in range(6):
            rect(ax, x0+c*col_w, 162+r*90, col_w, 90, fc=BG, ec=BORD, lw=0.5)
            if (r*6+c)%5<3:
                box(ax, x0+c*col_w+4, 166+r*90, col_w-8, 80, fc=LIGHT, ec=MID)
                label(ax, x0+c*col_w+col_w//2, 198+r*90, f'CS-{301+c}', size=8)
                label(ax, x0+c*col_w+col_w//2, 214+r*90, f'Hall {c+1}', size=6, color=BORD)
    save(fig, 'wf_web_25_student_schedule.png')

def wf_web_26_student_excuse():
    fig, ax = web_fig("Wireframe WF-026: Medical Excuse")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 3)
    label(ax, 820, 95, 'Submit Medical Excuse', size=13, bold=True, ha='center')
    # Form
    box(ax, 350, 120, 740, 560, fc=LIGHT, ec=BORD, lw=1.5)
    fields = [('Course',360,160),('Date From',360,230),('Date To',700,230),
              ('Reason',360,300),('Description (optional)',360,400)]
    for (lbl, x, y) in fields:
        label(ax, x, y-12, lbl, size=8, ha='left')
        if lbl == 'Description (optional)':
            box(ax, x, y, 700, 80, fc=BG, ec=BORD)
        elif lbl == 'Reason':
            box(ax, x, y, 700, 32, fc=BG, ec=BORD)
        else:
            box(ax, x, y, 300, 32, fc=BG, ec=BORD)
    # File upload
    label(ax, 360, 506, 'Attach Medical Document', size=8, ha='left')
    rect(ax, 360, 520, 700, 70, fc=BG, ec=BORD)
    label(ax, 710, 555, '[UPLOAD] Click to upload or drag file here', size=9, color=BORD)
    btn(ax, 560, 620, 320, 38, 'SUBMIT EXCUSE')
    # Past excuses
    label(ax, 250, 700, 'Previous Excuses', size=10, bold=True, ha='left')
    cols = ['Date From','Date To','Course','Status','Actions']
    ws = [130,130,200,120,100]
    table_header(ax, 200, 718, cols, ws)
    table_rows(ax, 200, 742, 3, ws)
    save(fig, 'wf_web_26_student_excuse.png')

def wf_web_27_student_grades():
    fig, ax = web_fig("Wireframe WF-027: Grades")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 4)
    label(ax, 820, 95, 'My Grades', size=13, bold=True, ha='center')
    # GPA card
    box(ax, 200, 115, 200, 80, fc=LIGHT, ec=BORD, lw=1.5)
    label(ax, 300, 145, 'Cumulative GPA', size=8, bold=True)
    label(ax, 300, 168, '3.42 / 4.0', size=14, bold=True)
    cols = ['Course','Credits','Midterm','Final','Practical','Grade','Letter']
    ws = [200,70,90,90,90,90,80]
    table_header(ax, 200, 215, cols, ws)
    table_rows(ax, 200, 239, 8, ws)
    save(fig, 'wf_web_27_student_grades.png')

def wf_web_28_student_notifications():
    fig, ax = web_fig("Wireframe WF-028: Student Notifications")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 5)
    label(ax, 820, 95, 'Notifications', size=13, bold=True, ha='center')
    for i in range(14):
        y = 120+i*52
        is_unread = i%4==0
        box(ax, 200, y, 980, 44, fc=LIGHT if is_unread else BG, ec=BORD)
        if is_unread:
            rect(ax, 200, y, 4, 44, fc=BTN, ec='none')
        icons = ['[BELL]','[WARN]','[OK]','[INFO]']
        label(ax, 225, y+14, f'{icons[i%4]} Notification Title {i+1}', size=9,
              ha='left', bold=is_unread)
        label(ax, 225, y+30, 'Notification message content goes here...', size=7,
              color=BORD, ha='left')
        label(ax, 1150, y+22, f'{i+1}h ago', size=7, color=BORD)
    save(fig, 'wf_web_28_student_notifications.png')

def wf_web_29_student_profile():
    fig, ax = web_fig("Wireframe WF-029: Student Profile")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Courses','Schedule','Excuse',
                                   'Grades','Notifications','Profile'], 6)
    label(ax, 820, 95, 'My Profile', size=13, bold=True, ha='center')
    # Avatar
    circle = plt.Circle((300, 200), 60, fc=HEAD, ec=BORD, linewidth=2)
    ax.add_patch(circle)
    label(ax, 300, 200, '[AVATAR]', size=10, color=BORD)
    label(ax, 300, 278, 'Change Photo', size=7, color=BTN)
    # Info
    box(ax, 400, 120, 700, 350, fc=LIGHT, ec=BORD, lw=1.5)
    fields = [('Full Name','Ahmed Ali Hassan',120),('Student ID','2021001234',160),
              ('Email','ahmed@university.edu',200),('Phone','+249 912 345 678',240),
              ('College','College of Computer Science',280),
              ('Department','Computer Science',320),('Year','3rd Year',360)]
    for lbl, val, y in fields:
        label(ax, 420, y+85, lbl+':', size=8, color=BORD, ha='left')
        label(ax, 580, y+85, val, size=8, ha='left')
    btn(ax, 680, 500, 160, 36, 'Edit Profile')
    btn(ax, 860, 500, 160, 36, 'Change Password')
    save(fig, 'wf_web_29_student_profile.png')

# ═══════════════════════════════════════════════════════════════
# COORDINATOR PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_30_coordinator_dashboard():
    fig, ax = web_fig("Wireframe WF-030: Coordinator Dashboard")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Students','Faculty',
                                   'Grading','Register Student'], 0)
    label(ax, 820, 95, 'Coordinator Dashboard — College of CS', size=13, bold=True, ha='center')
    stat_cards(ax, 200, 120, [('College Students','342'),('College Attendance','79%'),
                               ('Pending Excuses','12'),('Ungraded Courses','4')], w=240)
    # At-risk
    label(ax, 250, 220, 'At-Risk Students (Attendance < 75%)', size=10, bold=True, ha='left')
    cols = ['Student ID','Name','Dept','Attendance%','Absent Sessions','Actions']
    ws = [90,180,140,100,120,100]
    table_header(ax, 200, 238, cols, ws)
    table_rows(ax, 200, 262, 8, ws)
    # Pending excuses
    label(ax, 850, 220, 'Pending Medical Excuses', size=10, bold=True, ha='left')
    cols2 = ['Student','Course','Date','Action']
    ws2 = [160,140,80,80]
    table_header(ax, 840, 238, cols2, ws2)
    table_rows(ax, 840, 262, 8, ws2)
    save(fig, 'wf_web_30_coordinator_dashboard.png')

def wf_web_31_coordinator_students():
    fig, ax = web_fig("Wireframe WF-031: College Students")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Students','Faculty',
                                   'Grading','Register Student'], 1)
    label(ax, 820, 95, 'Students — College of CS', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 300)
    box(ax, 515, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 525, 124, 'Filter: Dept', size=7, color=BORD, ha='left')
    box(ax, 660, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 670, 124, 'Filter: Year', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, 'Export Excel')
    cols = ['ID','Name','Department','Year','Attendance%','Status','Excuses','Actions']
    ws = [70,160,140,60,90,80,70,100]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 13, ws)
    label(ax, 720, 495, '< 1  2  3  4 >', size=9, color=BTN)
    save(fig, 'wf_web_31_coordinator_students.png')

def wf_web_32_coordinator_faculty():
    fig, ax = web_fig("Wireframe WF-032: College Faculty")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Students','Faculty',
                                   'Grading','Register Student'], 2)
    label(ax, 820, 95, 'Faculty — College of CS', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 350)
    cols = ['ID','Name','Department','Email','Courses','Avg Attendance','Actions']
    ws = [60,180,140,200,80,110,100]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 12, ws)
    label(ax, 720, 490, '< 1  2 >', size=9, color=BTN)
    save(fig, 'wf_web_32_coordinator_faculty.png')

def wf_web_33_coordinator_grading():
    fig, ax = web_fig("Wireframe WF-033: Grade Sheets Overview")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Students','Faculty',
                                   'Grading','Register Student'], 3)
    label(ax, 820, 95, 'Grade Sheets', size=13, bold=True, ha='center')
    box(ax, 200, 110, 160, 28, fc=BG, ec=BORD)
    label(ax, 210, 124, 'Filter: Department', size=7, color=BORD, ha='left')
    cols = ['Course Code','Course Name','Teacher','Students','Graded','Status','Actions']
    ws = [90,200,160,80,80,90,100]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 12, ws)
    label(ax, 720, 490, '< 1  2  3 >', size=9, color=BTN)
    save(fig, 'wf_web_33_coordinator_grading.png')

def wf_web_34_coordinator_register():
    fig, ax = web_fig("Wireframe WF-034: Register New Student")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Students','Faculty',
                                   'Grading','Register Student'], 4)
    label(ax, 820, 95, 'Register New Student', size=13, bold=True, ha='center')
    box(ax, 300, 115, 840, 660, fc=LIGHT, ec=BORD, lw=1.5)
    fields_left = [('Full Name (Arabic)',115),('Full Name (English)',185),
                   ('National ID',255),('Date of Birth',325),('Gender',395)]
    fields_right = [('Email',115),('Phone',185),('College',255),
                    ('Department',325),('Year of Study',395)]
    for lbl, oy in fields_left:
        label(ax, 320, oy+140, lbl, size=8, ha='left')
        box(ax, 320, oy+154, 360, 28, fc=BG, ec=BORD)
    for lbl, oy in fields_right:
        label(ax, 730, oy+140, lbl, size=8, ha='left')
        box(ax, 730, oy+154, 360, 28, fc=BG, ec=BORD)
    label(ax, 320, 582, 'Profile Photo', size=8, ha='left')
    rect(ax, 320, 596, 200, 120, fc=BG, ec=BORD)
    label(ax, 420, 656, '[UPLOAD]', size=9, color=BORD)
    btn(ax, 560, 730, 320, 38, 'REGISTER STUDENT')
    save(fig, 'wf_web_34_coordinator_register.png')

# ═══════════════════════════════════════════════════════════════
# GATE PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_35_gate_dashboard():
    fig, ax = web_fig("Wireframe WF-035: Gate Dashboard")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Live Scan','Gate Logs'], 0)
    label(ax, 820, 95, 'Gate Control Center', size=13, bold=True, ha='center')
    stat_cards(ax, 200, 120, [('Entries Today','234'),('Camera Status','Online'),
                               ('Last Scan','2 min ago'),('Rejected','8')], w=240)
    # Camera status
    box(ax, 200, 220, 300, 180, fc=LIGHT, ec=BORD, lw=1.5)
    label(ax, 350, 248, 'Camera Status', size=10, bold=True)
    for i, cam in enumerate(['Gate Camera 1','Gate Camera 2','Classroom A1']):
        y = 265+i*46
        rect(ax, 220, y, 260, 34, fc=BG, ec=BORD)
        label(ax, 240, y+17, cam, size=8, ha='left')
        box(ax, 390, y+6, 70, 20, fc=HEAD, ec=BORD)
        label(ax, 425, y+16, 'Online', size=7)
    # Classroom status
    label(ax, 530, 220, 'Active Classrooms', size=10, bold=True, ha='left')
    cols = ['Classroom','Course','Teacher','Students','Status']
    ws = [110,160,140,80,90]
    table_header(ax, 520, 238, cols, ws)
    table_rows(ax, 520, 262, 6, ws)
    # Recent log
    label(ax, 250, 425, 'Recent Gate Log', size=10, bold=True, ha='left')
    cols2 = ['Time','Student','Score','Direction','Status']
    ws2 = [90,200,80,100,90]
    table_header(ax, 200, 443, cols2, ws2)
    table_rows(ax, 200, 467, 8, ws2)
    save(fig, 'wf_web_35_gate_dashboard.png')

def wf_web_36_gate_scan():
    fig, ax = web_fig("Wireframe WF-036: Live Gate Scan")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Live Scan','Gate Logs'], 1)
    label(ax, 820, 95, 'Live Face Scan', size=13, bold=True, ha='center')
    # Camera feed
    rect(ax, 200, 115, 560, 420, fc='#111111', ec=BORD, lw=2)
    label(ax, 480, 280, '[CAMERA FEED]', size=14, color=BG)
    label(ax, 480, 310, 'Live Video Stream', size=9, color=MID)
    # Face box overlay
    rect(ax, 380, 175, 200, 240, fc='none', ec=BG, lw=2)
    label(ax, 480, 165, 'Face Detected', size=8, color=BG)
    # Result panel
    box(ax, 790, 115, 440, 420, fc=LIGHT, ec=BORD, lw=1.5)
    label(ax, 1010, 145, 'Scan Result', size=11, bold=True)
    # Last result
    rect(ax, 810, 165, 400, 100, fc=BG, ec=BORD)
    circle = plt.Circle((860, 215), 35, fc=HEAD, ec=BORD)
    ax.add_patch(circle)
    label(ax, 860, 215, '[FACE]', size=8, color=BORD)
    label(ax, 970, 195, 'Ahmed Ali Hassan', size=10, bold=True, ha='left')
    label(ax, 970, 215, 'ID: 2021001234', size=8, color=BORD, ha='left')
    label(ax, 970, 235, 'Score: 0.92  |  ENTRY ALLOWED', size=8, ha='left')
    btn(ax, 870, 280, 140, 32, 'Override Allow', fc=LIGHT, tc=TEXT)
    btn(ax, 1020, 280, 140, 32, 'Override Deny', fc=LIGHT, tc=TEXT)
    # Log
    label(ax, 810, 335, 'Recent Scans', size=9, bold=True, ha='left')
    cols = ['Time','Student','Score','Result']
    ws = [80,160,80,80]
    table_header(ax, 810, 352, cols, ws)
    table_rows(ax, 810, 376, 5, ws)
    save(fig, 'wf_web_36_gate_scan.png')

def wf_web_37_gate_logs():
    fig, ax = web_fig("Wireframe WF-037: Gate Logs")
    nav_web(ax); sidebar_web(ax, ['Dashboard','Live Scan','Gate Logs'], 2)
    label(ax, 820, 95, 'Gate Logs', size=13, bold=True, ha='center')
    search_bar(ax, 200, 110, 300)
    box(ax, 515, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 525, 124, 'Date Filter', size=7, color=BORD, ha='left')
    box(ax, 660, 110, 130, 28, fc=BG, ec=BORD)
    label(ax, 670, 124, 'Direction', size=7, color=BORD, ha='left')
    btn(ax, 1060, 110, 130, 28, 'Export CSV')
    cols = ['Time','Student ID','Student Name','Photo','Score','Direction','Status','Camera']
    ws = [90,80,160,60,80,90,80,110]
    table_header(ax, 200, 155, cols, ws)
    table_rows(ax, 200, 179, 14, ws)
    label(ax, 720, 495, '< 1  2  3  4  5 >', size=9, color=BTN)
    save(fig, 'wf_web_37_gate_logs.png')

# ═══════════════════════════════════════════════════════════════
# SHARED PAGES
# ═══════════════════════════════════════════════════════════════

def wf_web_38_tickets():
    fig, ax = web_fig("Wireframe WF-038: Support Tickets")
    nav_web(ax)
    label(ax, 820, 95, 'Support Tickets', size=13, bold=True, ha='center')
    # Create form
    box(ax, 200, 115, 480, 300, fc=LIGHT, ec=BORD, lw=1.5)
    label(ax, 220, 138, 'New Support Ticket', size=10, bold=True, ha='left')
    label(ax, 220, 172, 'Subject', size=8, ha='left')
    box(ax, 220, 184, 440, 28, fc=BG, ec=BORD)
    label(ax, 220, 228, 'Category', size=8, ha='left')
    box(ax, 220, 240, 440, 28, fc=BG, ec=BORD)
    label(ax, 220, 284, 'Message', size=8, ha='left')
    box(ax, 220, 296, 440, 80, fc=BG, ec=BORD)
    btn(ax, 340, 396, 200, 32, 'SUBMIT TICKET')
    # Tickets list
    label(ax, 730, 120, 'My Tickets', size=10, bold=True, ha='left')
    cols = ['#','Subject','Category','Date','Status','Actions']
    ws = [50,220,130,100,90,90]
    table_header(ax, 720, 138, cols, ws)
    table_rows(ax, 720, 162, 10, ws)
    save(fig, 'wf_web_38_tickets.png')

def wf_web_39_enroll_face():
    fig, ax = web_fig("Wireframe WF-039: Face Enrollment")
    nav_web(ax)
    label(ax, 720, 95, 'Face Enrollment', size=13, bold=True, ha='center')
    # Steps
    steps = ['1. Position Face','2. Capture Samples','3. Process','4. Confirm']
    for i, s in enumerate(steps):
        x = 260+i*240
        circle2 = plt.Circle((x, 130), 18, fc=BTN if i<2 else LIGHT, ec=BTN, linewidth=2)
        ax.add_patch(circle2)
        label(ax, x, 130, str(i+1), size=9, color=BG if i<2 else TEXT, bold=True)
        label(ax, x, 160, s, size=7, color=BTN if i<2 else BORD)
        if i<3:
            ax.plot([x+20, x+220], [130,130], color=MID, linewidth=1.5)
    # Camera
    rect(ax, 380, 185, 400, 380, fc='#111111', ec=BORD, lw=2)
    label(ax, 580, 360, '[CAMERA FEED]', size=12, color=BG)
    label(ax, 580, 390, 'Center your face in the frame', size=9, color=MID)
    # Face guide oval
    from matplotlib.patches import Ellipse
    ell = Ellipse((580, 360), 160, 220, fc='none', ec=BG, linewidth=2, linestyle='--')
    ax.add_patch(ell)
    # Samples
    label(ax, 820, 185, 'Captured Samples', size=10, bold=True, ha='left')
    for i in range(6):
        r, c = divmod(i, 3)
        x = 820+c*130; y = 210+r*130
        rect(ax, x, y, 110, 100, fc=LIGHT if i>=2 else HEAD, ec=BORD)
        label(ax, x+55, y+50, f'[FACE {i+1}]' if i<2 else '[empty]',
              size=8, color=TEXT if i<2 else BORD)
    btn(ax, 460, 590, 240, 36, 'CAPTURE SAMPLE')
    btn(ax, 720, 590, 200, 36, 'ENROLL (2/6)', fc=LIGHT, tc=BORD)
    save(fig, 'wf_web_39_enroll_face.png')

# ═══════════════════════════════════════════════════════════════
# MOBILE WIREFRAMES
# ═══════════════════════════════════════════════════════════════

def mob_topbar(ax, title, back=False):
    rect(ax, 10, 35, 355, 44, fc=BTN, ec=BTN)
    if back:
        label(ax, 30, 57, '<', size=12, color=BG, bold=True, ha='left')
    label(ax, 187, 57, title, size=9, color=BG, bold=True)

def mob_bottomnav(ax, items, active=0):
    rect(ax, 10, 752, 355, 50, fc=LIGHT, ec=BORD)
    w = 355//len(items)
    for i, (icon, lbl) in enumerate(items):
        x = 10 + i*w + w//2
        label(ax, x, 768, icon, size=7, color=BTN if i==active else BORD)
        label(ax, x, 784, lbl, size=6, color=BTN if i==active else BORD)

def mob_stat_row(ax, y, items):
    w = 335//len(items)
    for i, (lbl, val) in enumerate(items):
        x = 20+i*(w+6)
        box(ax, x, y, w, 60, fc=LIGHT, ec=BORD)
        label(ax, x+w//2, y+20, lbl, size=6, color=BORD)
        label(ax, x+w//2, y+44, val, size=13, bold=True)

def wf_mob_01_login():
    fig, ax = mob_fig("Wireframe WF-M01: Mobile Login")
    rect(ax, 10, 35, 355, 772, fc=BG, ec=BORD, lw=0.5)
    label(ax, 187, 120, 'SHAMEL', size=18, bold=True)
    label(ax, 187, 148, 'Smart Attendance System', size=7, color=BORD)
    circle = plt.Circle((187, 230), 50, fc=HEAD, ec=BORD, linewidth=1.5)
    ax.add_patch(circle)
    label(ax, 187, 230, '[LOGO]', size=8, color=BORD)
    for i, (lbl, y) in enumerate([('Username',320),('Password',395)]):
        label(ax, 30, y-12, lbl, size=8, ha='left')
        box(ax, 20, y, 335, 38, fc=LIGHT, ec=BORD)
    box(ax, 20, 462, 335, 40, fc=BTN, ec=BTN)
    label(ax, 187, 482, 'LOGIN', size=9, color=BG, bold=True)
    label(ax, 187, 530, 'Forgot password?', size=8, color=BTN)
    save(fig, 'wf_mob_01_login.png')

def wf_mob_02_admin_home():
    fig, ax = mob_fig("Wireframe WF-M02: Admin Home")
    mob_topbar(ax, 'Admin Dashboard')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 0)
    mob_stat_row(ax, 85, [('Students','1240'),('Teachers','86'),('Today','18')])
    label(ax, 30, 165, 'Quick Access', size=8, bold=True, ha='left')
    for i, (icon, lbl) in enumerate([('[S]','Students'),('[T]','Teachers'),
                                      ('[R]','Reports'),('[G]','Gate Logs')]):
        r, c = divmod(i, 2)
        x = 20+c*175; y = 180+r*110
        box(ax, x, y, 160, 95, fc=LIGHT, ec=BORD)
        label(ax, x+80, y+38, icon, size=14, color=BORD)
        label(ax, x+80, y+72, lbl, size=8)
    label(ax, 30, 415, 'Recent Activity', size=8, bold=True, ha='left')
    for i in range(7):
        box(ax, 20, 430+i*42, 335, 36, fc=LIGHT if i%2 else BG, ec=BORD)
        label(ax, 40, 448+i*42, f'[BELL] Activity item {i+1}', size=7, ha='left')
        label(ax, 330, 448+i*42, f'{i+1}m', size=6, color=BORD)
    save(fig, 'wf_mob_02_admin_home.png')

def wf_mob_03_admin_schedule():
    fig, ax = mob_fig("Wireframe WF-M03: Admin Schedule")
    mob_topbar(ax, 'Schedule')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 1)
    # Day tabs
    days = ['Sat','Sun','Mon','Tue','Wed','Thu']
    dw = 355//len(days)
    for i, d in enumerate(days):
        fc2 = BTN if i==0 else LIGHT
        tc2 = BG if i==0 else TEXT
        rect(ax, 10+i*dw, 80, dw, 28, fc=fc2, ec=BORD, lw=0.5)
        label(ax, 10+i*dw+dw//2, 94, d, size=7, color=tc2)
    # Schedule items
    for i in range(8):
        y = 120+i*76
        box(ax, 20, y, 335, 66, fc=LIGHT, ec=BORD)
        rect(ax, 20, y, 4, 66, fc=BTN, ec='none')
        label(ax, 42, y+18, f'08:{i*2:02d} — 09:30', size=7, color=BORD, ha='left')
        label(ax, 42, y+36, f'CS{301+i} — Course Name', size=8, bold=True, ha='left')
        label(ax, 42, y+52, f'Room A{i%4+1}  |  Dr. Teacher', size=7, color=BORD, ha='left')
    save(fig, 'wf_mob_03_admin_schedule.png')

def wf_mob_04_admin_reports():
    fig, ax = mob_fig("Wireframe WF-M04: Admin Reports")
    mob_topbar(ax, 'Reports')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 2)
    # Summary stats
    label(ax, 30, 88, 'Attendance Overview', size=8, bold=True, ha='left')
    mob_stat_row(ax, 102, [('Avg Attend.','79%'),('Absences','342'),('At-Risk','28')])
    # Chart placeholder
    label(ax, 30, 182, 'By Course', size=8, bold=True, ha='left')
    rect(ax, 20, 196, 335, 180, fc=LIGHT, ec=BORD)
    bar_w = 28
    for i in range(8):
        bh = 40+i*12
        rect(ax, 30+i*40, 196+180-bh-10, bar_w, bh, fc=MID, ec=BORD, lw=0.5)
        label(ax, 30+i*40+bar_w//2, 380, f'CS{i+1}', size=5, color=BORD)
    label(ax, 30, 400, 'Course Breakdown', size=8, bold=True, ha='left')
    for i in range(6):
        box(ax, 20, 415+i*50, 335, 42, fc=LIGHT if i%2 else BG, ec=BORD)
        label(ax, 40, 433+i*50, f'CS{301+i} — Course Name', size=8, ha='left')
        pct = 65+i*5
        rect(ax, 40, 446+i*50, 240, 8, fc=MID, ec=BORD, lw=0.3)
        rect(ax, 40, 446+i*50, int(240*pct/100), 8, fc=BTN, ec='none')
        label(ax, 300, 443+i*50, f'{pct}%', size=7)
    save(fig, 'wf_mob_04_admin_reports.png')

def wf_mob_05_admin_profile():
    fig, ax = mob_fig("Wireframe WF-M05: Admin Profile")
    mob_topbar(ax, 'Profile')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 3)
    # Avatar
    circle = plt.Circle((187, 155), 55, fc=HEAD, ec=BORD, linewidth=2)
    ax.add_patch(circle)
    label(ax, 187, 155, '[AVATAR]', size=9, color=BORD)
    label(ax, 187, 226, 'Admin User Name', size=11, bold=True)
    label(ax, 187, 248, 'System Administrator', size=8, color=BORD)
    # Info fields
    fields = [('Full Name','Admin User'),('Email','admin@shamel.sd'),
              ('Phone','+249 912 000 001'),('Role','Administrator'),('Last Login','Today 08:00')]
    for i, (lbl, val) in enumerate(fields):
        y = 278+i*54
        rect(ax, 20, y, 335, 44, fc=LIGHT, ec=BORD)
        label(ax, 36, y+14, lbl, size=7, color=BORD, ha='left')
        label(ax, 36, y+30, val, size=8, ha='left')
    box(ax, 60, 558, 255, 38, fc=BTN, ec=BTN)
    label(ax, 187, 577, 'LOGOUT', size=9, color=BG, bold=True)
    save(fig, 'wf_mob_05_admin_profile.png')

def wf_mob_06_admin_register_student():
    fig, ax = mob_fig("Wireframe WF-M06: Register Student")
    mob_topbar(ax, 'Register Student', back=True)
    fields = [('Full Name',92),('Student ID',162),('Email',232),
              ('Phone',302),('College',372),('Department',442),('Year',512)]
    for lbl, y in fields:
        label(ax, 30, y-10, lbl, size=7, color=BORD, ha='left')
        box(ax, 20, y, 335, 36, fc=LIGHT, ec=BORD)
    box(ax, 60, 568, 255, 40, fc=BTN, ec=BTN)
    label(ax, 187, 588, 'REGISTER', size=9, color=BG, bold=True)
    save(fig, 'wf_mob_06_admin_register_student.png')

def wf_mob_07_teacher_home():
    fig, ax = mob_fig("Wireframe WF-M07: Teacher Home")
    mob_topbar(ax, 'Teacher Dashboard')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 0)
    mob_stat_row(ax, 85, [('Courses','5'),('Today','2'),('Avg%','78')])
    label(ax, 30, 165, 'My Courses', size=8, bold=True, ha='left')
    for i in range(5):
        box(ax, 20, 180+i*76, 335, 66, fc=LIGHT, ec=BORD)
        rect(ax, 20, 180+i*76, 4, 66, fc=BTN, ec='none')
        label(ax, 42, 200+i*76, f'CS{301+i} — Course Title {i+1}', size=8, bold=True, ha='left')
        label(ax, 42, 218+i*76, f'Section {i+1}  |  {30+i} students', size=7, color=BORD, ha='left')
        pct = 68+i*4
        rect(ax, 42, 232+i*76, 200, 6, fc=MID, ec=BORD, lw=0.3)
        rect(ax, 42, 232+i*76, int(200*pct/100), 6, fc=BTN, ec='none')
        label(ax, 256, 228+i*76, f'{pct}%', size=6, color=BORD)
    label(ax, 30, 566, "Today's Sessions", size=8, bold=True, ha='left')
    for i in range(2):
        box(ax, 20, 580+i*76, 335, 66, fc=LIGHT, ec=BORD)
        label(ax, 42, 600+i*76, f'CS{301+i} — 08:{i*2}0 AM', size=8, bold=True, ha='left')
        label(ax, 42, 618+i*76, f'Room A{i+1}  |  Active', size=7, color=BORD, ha='left')
        btn(ax, 248, 592+i*76, 95, 26, 'Mark Attend.')
    save(fig, 'wf_mob_07_teacher_home.png')

def wf_mob_08_teacher_schedule():
    fig, ax = mob_fig("Wireframe WF-M08: Teacher Schedule")
    mob_topbar(ax, 'My Schedule')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 1)
    days = ['Sat','Sun','Mon','Tue','Wed','Thu']
    dw = 355//len(days)
    for i, d in enumerate(days):
        fc2 = BTN if i==1 else LIGHT
        tc2 = BG if i==1 else TEXT
        rect(ax, 10+i*dw, 80, dw, 28, fc=fc2, ec=BORD, lw=0.5)
        label(ax, 10+i*dw+dw//2, 94, d, size=7, color=tc2)
    for i in range(6):
        box(ax, 20, 120+i*86, 335, 76, fc=LIGHT, ec=BORD)
        label(ax, 40, 140+i*86, f'{8+i}:00 — {9+i}:30', size=7, color=BORD, ha='left')
        label(ax, 40, 158+i*86, f'CS{301+i} — Algorithms {i+1}', size=9, bold=True, ha='left')
        label(ax, 40, 176+i*86, f'Room B{i+1}  |  35 students', size=7, color=BORD, ha='left')
    save(fig, 'wf_mob_08_teacher_schedule.png')

def wf_mob_09_teacher_reports():
    fig, ax = mob_fig("Wireframe WF-M09: Teacher Reports")
    mob_topbar(ax, 'Attendance Reports')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 2)
    box(ax, 20, 80, 335, 28, fc=LIGHT, ec=BORD)
    label(ax, 36, 94, 'Select Course: CS301 - Algorithms', size=7, ha='left')
    mob_stat_row(ax, 118, [('Sessions','24'),('Avg%','78'),('At-Risk','4')])
    rect(ax, 20, 195, 335, 160, fc=LIGHT, ec=BORD)
    label(ax, 187, 212, 'Attendance Trend', size=8, bold=True)
    xs = np.linspace(30, 345, 10)
    ys = 285 + np.random.randint(-40, 20, 10)
    ax.plot(xs+20, ys, color=BTN, linewidth=1.5)
    label(ax, 30, 374, 'Student List', size=8, bold=True, ha='left')
    for i in range(10):
        box(ax, 20, 390+i*36, 335, 30, fc=LIGHT if i%2 else BG, ec=BORD)
        label(ax, 36, 405+i*36, f'Student {i+1} — {72+i*2}%', size=7, ha='left')
        pct = 72+i*2
        rect(ax, 200, 402+i*36, 140, 8, fc=MID, ec=BORD, lw=0.3)
        rect(ax, 200, 402+i*36, int(140*pct/100), 8, fc=BTN, ec='none')
    save(fig, 'wf_mob_09_teacher_reports.png')

def wf_mob_10_teacher_profile():
    fig, ax = mob_fig("Wireframe WF-M10: Teacher Profile")
    mob_topbar(ax, 'Profile')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 3)
    circle = plt.Circle((187, 155), 55, fc=HEAD, ec=BORD, linewidth=2)
    ax.add_patch(circle)
    label(ax, 187, 155, '[AVATAR]', size=9, color=BORD)
    label(ax, 187, 226, 'Dr. Teacher Name', size=11, bold=True)
    label(ax, 187, 248, 'Computer Science Department', size=8, color=BORD)
    fields = [('Email','teacher@shamel.sd'),('Phone','+249 912 000 002'),
              ('Department','CS'),('Courses','5'),('Total Sessions','48')]
    for i, (lbl, val) in enumerate(fields):
        y = 274+i*54
        rect(ax, 20, y, 335, 44, fc=LIGHT, ec=BORD)
        label(ax, 36, y+14, lbl, size=7, color=BORD, ha='left')
        label(ax, 36, y+30, val, size=8, ha='left')
    box(ax, 60, 554, 255, 38, fc=BTN, ec=BTN)
    label(ax, 187, 573, 'LOGOUT', size=9, color=BG, bold=True)
    save(fig, 'wf_mob_10_teacher_profile.png')

def wf_mob_11_student_home():
    fig, ax = mob_fig("Wireframe WF-M11: Student Home")
    mob_topbar(ax, 'My Attendance')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 0)
    # Gauge
    box(ax, 90, 85, 195, 155, fc=LIGHT, ec=BORD, lw=1.5)
    circle = plt.Circle((187, 148), 50, fc='none', ec=BORD, linewidth=8)
    ax.add_patch(circle)
    label(ax, 187, 148, '82%', size=16, bold=True)
    label(ax, 187, 175, 'Overall Attendance', size=7, color=BORD)
    mob_stat_row(ax, 252, [('Present','48'),('Absent','10'),('Excuses','2')])
    label(ax, 30, 330, "Today's Classes", size=8, bold=True, ha='left')
    for i in range(3):
        box(ax, 20, 345+i*72, 335, 62, fc=LIGHT, ec=BORD)
        label(ax, 40, 363+i*72, f'{8+i*2}:00 — CS{301+i}', size=8, bold=True, ha='left')
        label(ax, 40, 381+i*72, f'Room A{i+1}  |  Dr. Teacher', size=7, color=BORD, ha='left')
        status = ['Present','Present','Absent'][i]
        box(ax, 255, 358+i*72, 85, 24, fc=HEAD, ec=BORD)
        label(ax, 297, 370+i*72, status, size=7)
    label(ax, 30, 566, 'Notifications', size=8, bold=True, ha='left')
    for i in range(3):
        box(ax, 20, 580+i*52, 335, 44, fc=LIGHT if i==0 else BG, ec=BORD)
        label(ax, 40, 598+i*52, f'[BELL] Notification {i+1}', size=7, ha='left', bold=(i==0))
        label(ax, 40, 612+i*52, '2h ago', size=6, color=BORD, ha='left')
    save(fig, 'wf_mob_11_student_home.png')

def wf_mob_12_student_schedule():
    fig, ax = mob_fig("Wireframe WF-M12: Student Schedule")
    mob_topbar(ax, 'My Schedule')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 1)
    days = ['Sat','Sun','Mon','Tue','Wed','Thu']
    dw = 355//len(days)
    for i, d in enumerate(days):
        fc2 = BTN if i==2 else LIGHT
        tc2 = BG if i==2 else TEXT
        rect(ax, 10+i*dw, 80, dw, 28, fc=fc2, ec=BORD, lw=0.5)
        label(ax, 10+i*dw+dw//2, 94, d, size=7, color=tc2)
    for i in range(7):
        box(ax, 20, 120+i*86, 335, 76, fc=LIGHT, ec=BORD)
        label(ax, 40, 140+i*86, f'{8+i}:00 — {9+i}:30', size=7, color=BORD, ha='left')
        label(ax, 40, 158+i*86, f'CS{301+i%6} — Course Title', size=9, bold=True, ha='left')
        label(ax, 40, 176+i*86, f'Hall {i%4+1}  |  Dr. Name', size=7, color=BORD, ha='left')
    save(fig, 'wf_mob_12_student_schedule.png')

def wf_mob_13_student_reports():
    fig, ax = mob_fig("Wireframe WF-M13: Student Reports")
    mob_topbar(ax, 'Attendance Reports')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 2)
    mob_stat_row(ax, 85, [('Overall','82%'),('Present','48'),('Absent','10')])
    rect(ax, 20, 158, 335, 155, fc=LIGHT, ec=BORD)
    label(ax, 187, 174, 'Attendance by Course', size=8, bold=True)
    for i in range(6):
        bh = 30+i*12
        rect(ax, 32+i*52, 158+155-bh-15, 40, bh, fc=MID, ec=BORD, lw=0.5)
        label(ax, 52+i*52, 316, f'CS{i+1}', size=5, color=BORD)
    label(ax, 30, 328, 'Course Details', size=8, bold=True, ha='left')
    for i in range(6):
        box(ax, 20, 342+i*64, 335, 56, fc=LIGHT if i%2 else BG, ec=BORD)
        label(ax, 40, 360+i*64, f'CS{301+i} — Course Name', size=8, bold=True, ha='left')
        label(ax, 40, 376+i*64, f'Present: {30+i}  Absent: {6-i%4}', size=7, color=BORD, ha='left')
        pct = 65+i*5
        rect(ax, 40, 388+i*64, 240, 6, fc=MID, ec=BORD, lw=0.3)
        rect(ax, 40, 388+i*64, int(240*pct/100), 6, fc=BTN, ec='none')
        label(ax, 295, 384+i*64, f'{pct}%', size=6)
    save(fig, 'wf_mob_13_student_reports.png')

def wf_mob_14_student_profile():
    fig, ax = mob_fig("Wireframe WF-M14: Student Profile")
    mob_topbar(ax, 'My Profile')
    mob_bottomnav(ax, [('[H]','Home'),('[S]','Schedule'),('[R]','Reports'),('[P]','Profile')], 3)
    circle = plt.Circle((187, 155), 55, fc=HEAD, ec=BORD, linewidth=2)
    ax.add_patch(circle)
    label(ax, 187, 155, '[AVATAR]', size=9, color=BORD)
    label(ax, 187, 226, 'Ahmed Ali Hassan', size=11, bold=True)
    label(ax, 187, 248, '3rd Year — Computer Science', size=8, color=BORD)
    fields = [('Student ID','2021001234'),('Email','ahmed@student.edu'),
              ('Phone','+249 912 345 678'),('GPA','3.42 / 4.0'),('Attendance','82%')]
    for i, (lbl, val) in enumerate(fields):
        y = 270+i*54
        rect(ax, 20, y, 335, 44, fc=LIGHT, ec=BORD)
        label(ax, 36, y+14, lbl, size=7, color=BORD, ha='left')
        label(ax, 36, y+30, val, size=8, ha='left')
    box(ax, 60, 554, 255, 38, fc=BTN, ec=BTN)
    label(ax, 187, 573, 'LOGOUT', size=9, color=BG, bold=True)
    save(fig, 'wf_mob_14_student_profile.png')

def wf_mob_15_gate_home():
    fig, ax = mob_fig("Wireframe WF-M15: Gate Operator Home")
    mob_topbar(ax, 'Gate Control')
    mob_bottomnav(ax, [('[H]','Home'),('[L]','Logs'),('[P]','Profile')], 0)
    mob_stat_row(ax, 85, [('Today','234'),('Denied','8'),('Camera','OK')])
    # Scan button
    rect(ax, 20, 163, 335, 90, fc=BTN, ec=BTN)
    label(ax, 187, 208, '[SCAN] START FACE SCAN', size=10, color=BG, bold=True)
    label(ax, 30, 268, 'Recent Activity', size=8, bold=True, ha='left')
    for i in range(12):
        box(ax, 20, 282+i*38, 335, 32, fc=LIGHT if i%2 else BG, ec=BORD)
        icons = ['[OK]','[OK]','[X]','[OK]']
        label(ax, 42, 298+i*38, f'{icons[i%4]} Student Name {i+1}  —  08:{i*5:02d}', size=7, ha='left')
        label(ax, 330, 298+i*38, 'IN' if i%3!=2 else 'OUT', size=6, color=BORD)
    save(fig, 'wf_mob_15_gate_home.png')

# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

if __name__ == '__main__':
    np.random.seed(42)
    print("Generating SHAMEL wireframes...")

    # Web pages
    wf_web_01_login()
    wf_web_02_password_reset()
    wf_web_03_admin_dashboard()
    wf_web_04_admin_gate_logs()
    wf_web_05_admin_faculty()
    wf_web_06_admin_students()
    wf_web_07_admin_courses()
    wf_web_08_admin_schedule()
    wf_web_09_admin_schedule_calendar()
    wf_web_10_admin_classrooms()
    wf_web_11_admin_reports()
    wf_web_12_admin_analytics()
    wf_web_13_admin_search()
    wf_web_14_admin_settings()
    wf_web_15_admin_notifications()
    wf_web_16_admin_audit()
    wf_web_17_teacher_dashboard()
    wf_web_18_teacher_sessions()
    wf_web_19_teacher_attendance()
    wf_web_20_teacher_timeline()
    wf_web_21_teacher_records()
    wf_web_22_teacher_schedule()
    wf_web_23_student_dashboard()
    wf_web_24_student_courses()
    wf_web_25_student_schedule()
    wf_web_26_student_excuse()
    wf_web_27_student_grades()
    wf_web_28_student_notifications()
    wf_web_29_student_profile()
    wf_web_30_coordinator_dashboard()
    wf_web_31_coordinator_students()
    wf_web_32_coordinator_faculty()
    wf_web_33_coordinator_grading()
    wf_web_34_coordinator_register()
    wf_web_35_gate_dashboard()
    wf_web_36_gate_scan()
    wf_web_37_gate_logs()
    wf_web_38_tickets()
    wf_web_39_enroll_face()

    # Mobile pages
    wf_mob_01_login()
    wf_mob_02_admin_home()
    wf_mob_03_admin_schedule()
    wf_mob_04_admin_reports()
    wf_mob_05_admin_profile()
    wf_mob_06_admin_register_student()
    wf_mob_07_teacher_home()
    wf_mob_08_teacher_schedule()
    wf_mob_09_teacher_reports()
    wf_mob_10_teacher_profile()
    wf_mob_11_student_home()
    wf_mob_12_student_schedule()
    wf_mob_13_student_reports()
    wf_mob_14_student_profile()
    wf_mob_15_gate_home()

    # Verify
    files = [f for f in os.listdir(OUT) if f.endswith('.png') and f.startswith('wf_')]
    print(f"\nGenerated {len(files)} wireframe PNGs:")
    for f in sorted(files):
        print(f"  {f}")
