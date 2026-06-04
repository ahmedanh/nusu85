"""
SHAMEL Thesis — Monochrome Wireframe Generator (Chapter 3 / UI Design)
Outputs grayscale blueprint-style wireframes for 6 key screens.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

OUT = os.path.join(os.path.dirname(__file__), 'wireframes')
os.makedirs(OUT, exist_ok=True)

# Grayscale palette
C = {
    'bg': '#FFFFFF',
    'surface': '#F5F5F5',
    'border': '#AAAAAA',
    'dark': '#333333',
    'mid': '#777777',
    'light': '#CCCCCC',
    'sidebar': '#E0E0E0',
    'header': '#DDDDDD',
    'btn': '#BBBBBB',
    'btn_primary': '#555555',
    'input': '#F0F0F0',
    'label': '#444444',
}

def wf_box(ax, x, y, w, h, label='', fc=None, ec=None, fontsize=8, bold=False, radius=0.01):
    fc = fc or C['surface']
    ec = ec or C['border']
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=0",
                          linewidth=1, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(rect)
    if label:
        ax.text(x + w/2, y + h/2, label, ha='center', va='center',
                fontsize=fontsize, color=C['dark' if bold else 'mid'],
                fontweight='bold' if bold else 'normal', zorder=4)

def wf_label(ax, x, y, text, fontsize=7, color=None, bold=False, align='left'):
    ax.text(x, y, text, fontsize=fontsize, color=color or C['label'],
            va='center', ha=align, fontweight='bold' if bold else 'normal', zorder=5)

def wf_input(ax, x, y, w, h=0.035, placeholder=''):
    wf_box(ax, x, y, w, h, fc=C['input'], ec=C['border'])
    if placeholder:
        ax.text(x + 0.01, y + h/2, placeholder, fontsize=6.5,
                color=C['light'], va='center', style='italic', zorder=5)

def wf_btn(ax, x, y, w, h=0.038, label='', primary=False):
    fc = C['btn_primary'] if primary else C['btn']
    tc = 'white' if primary else C['dark']
    wf_box(ax, x, y, w, h, fc=fc, ec=C['border'])
    ax.text(x + w/2, y + h/2, label, ha='center', va='center',
            fontsize=7, color=tc, fontweight='bold', zorder=5)

def wf_icon(ax, x, y, symbol='☰', size=10):
    ax.text(x, y, symbol, fontsize=size, ha='center', va='center',
            color=C['mid'], zorder=5)

def wf_divider(ax, x1, x2, y):
    ax.plot([x1, x2], [y, y], color=C['light'], lw=0.8, zorder=3)

def wf_table_row(ax, x, y, w, cols, h=0.030, header=False):
    fc = C['header'] if header else C['surface']
    wf_box(ax, x, y, w, h, fc=fc, ec=C['border'])
    col_w = w / len(cols)
    for i, col in enumerate(cols):
        ax.text(x + col_w * i + col_w/2, y + h/2, col, ha='center', va='center',
                fontsize=6.5, color=C['dark' if header else 'mid'],
                fontweight='bold' if header else 'normal', zorder=5)
    return y - h

def setup_figure(title, n_screens=1):
    fig, axes = plt.subplots(1, n_screens, figsize=(8 * n_screens, 9))
    fig.patch.set_facecolor(C['bg'])
    if n_screens == 1:
        axes = [axes]
    for ax in axes:
        ax.set_xlim(0, 1.0)
        ax.set_ylim(0, 1.0)
        ax.axis('off')
        ax.set_facecolor(C['bg'])
    fig.suptitle(title, fontsize=10, fontweight='bold', color=C['dark'], y=0.99)
    return fig, axes

# ── WIREFRAME 1: Login Screen
def wf_login():
    fig, [ax] = setup_figure('Wireframe WF-01: Login Screen')
    # outer frame
    wf_box(ax, 0.05, 0.05, 0.90, 0.90, fc=C['bg'], ec=C['border'])

    # center card
    wf_box(ax, 0.25, 0.25, 0.50, 0.55, fc=C['surface'], ec=C['border'])

    # logo placeholder
    wf_box(ax, 0.38, 0.69, 0.24, 0.08, fc=C['header'], ec=C['mid'])
    wf_label(ax, 0.50, 0.73, '[Logo]', fontsize=8, align='center')

    # title
    wf_label(ax, 0.50, 0.66, 'SHAMEL — Sign In', fontsize=9, bold=True, align='center')
    wf_label(ax, 0.50, 0.62, 'Enter credentials to access your dashboard', fontsize=7,
             color=C['mid'], align='center')

    # inputs
    wf_label(ax, 0.28, 0.57, 'Username', fontsize=7)
    wf_input(ax, 0.28, 0.53, 0.44, placeholder='student_id / employee_id')

    wf_label(ax, 0.28, 0.49, 'Password', fontsize=7)
    wf_input(ax, 0.28, 0.45, 0.44, placeholder='••••••••')

    # role select
    wf_label(ax, 0.28, 0.41, 'Role', fontsize=7)
    wf_box(ax, 0.28, 0.37, 0.44, 0.035, fc=C['input'], ec=C['border'])
    ax.text(0.49, 0.387, 'Student  ▾', ha='center', va='center', fontsize=7,
            color=C['mid'], zorder=5)

    wf_btn(ax, 0.28, 0.31, 0.44, label='Sign In', primary=True)

    wf_label(ax, 0.50, 0.27, 'Forgot password?', fontsize=7, color=C['mid'], align='center')

    # browser chrome
    wf_box(ax, 0.05, 0.90, 0.90, 0.05, fc=C['header'], ec=C['mid'])
    wf_label(ax, 0.12, 0.925, '← →  ⟳', fontsize=7, color=C['mid'])
    wf_box(ax, 0.25, 0.913, 0.55, 0.022, fc=C['bg'], ec=C['border'])
    wf_label(ax, 0.525, 0.924, 'shamel.sd/login', fontsize=6, color=C['mid'], align='center')

    plt.tight_layout()
    path = os.path.join(OUT, 'wf01_login.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf01_login.png")

# ── WIREFRAME 2: Admin Dashboard
def wf_admin_dashboard():
    fig, [ax] = setup_figure('Wireframe WF-02: Admin Dashboard')

    # Topbar
    wf_box(ax, 0.0, 0.92, 1.0, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, 0.03, 0.96, '≡  SHAMEL', fontsize=9, bold=True)
    wf_box(ax, 0.35, 0.937, 0.30, 0.028, fc=C['input'], ec=C['border'])
    wf_label(ax, 0.50, 0.951, '🔍 Search...', fontsize=7, color=C['light'], align='center')
    wf_label(ax, 0.88, 0.96, '🔔  👤', fontsize=9, color=C['mid'])

    # Sidebar
    wf_box(ax, 0.0, 0.0, 0.16, 0.92, fc=C['sidebar'], ec=C['border'])
    items = ['Dashboard', 'Gate Logs', 'Students', 'Teachers', 'Courses',
             'Schedules', 'Reports', 'Audit', 'Settings']
    for i, item in enumerate(items):
        y = 0.84 - i * 0.075
        if i == 0:
            wf_box(ax, 0.01, y - 0.015, 0.14, 0.030, fc=C['btn_primary'], ec=C['btn_primary'])
            wf_label(ax, 0.08, y, item, fontsize=7, color='white', align='center')
        else:
            wf_label(ax, 0.08, y, item, fontsize=7, color=C['dark'], align='center')

    # Main content
    MAIN_X = 0.18

    # Stat cards row
    stats = ['Total Students\n[1,240]', 'Active Sessions\n[8]',
             'Gate Logs Today\n[347]', 'Accuracy Rate\n[98.2%]']
    for i, stat in enumerate(stats):
        x = MAIN_X + i * 0.205
        wf_box(ax, x, 0.79, 0.19, 0.11, fc=C['surface'], ec=C['border'])
        lines = stat.split('\n')
        ax.text(x + 0.095, 0.855, lines[0], ha='center', va='center',
                fontsize=6.5, color=C['mid'], zorder=5)
        ax.text(x + 0.095, 0.820, lines[1], ha='center', va='center',
                fontsize=9, fontweight='bold', color=C['dark'], zorder=5)

    # Chart area
    wf_box(ax, MAIN_X, 0.44, 0.38, 0.33, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.19, 0.755, 'Attendance Rate — 30 Days', fontsize=7.5, bold=True, align='center')
    # fake chart lines
    import numpy as np
    np.random.seed(42)
    xs = np.linspace(MAIN_X + 0.02, MAIN_X + 0.36, 30)
    ys = 0.52 + 0.12 * np.sin(np.linspace(0, 6, 30)) + 0.02 * np.random.randn(30)
    ax.plot(xs, ys, color=C['mid'], lw=1.2, zorder=4)
    ax.fill_between(xs, 0.44, ys, color=C['light'], alpha=0.4, zorder=3)

    # Gate log table
    wf_box(ax, MAIN_X + 0.40, 0.44, 0.40, 0.33, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.60, 0.755, 'Recent Gate Logs', fontsize=7.5, bold=True, align='center')
    y = 0.725
    y = wf_table_row(ax, MAIN_X + 0.41, y, 0.38,
                     ['Student ID', 'Name', 'Time', 'Status'], header=True)
    for row in [('2021001', 'Ahmed N.', '08:12', '[OK] Allow'),
                ('2021042', 'Sara M.', '08:14', '[OK] Allow'),
                ('2020113', 'Omar K.', '08:17', '✗ Deny')]:
        y = wf_table_row(ax, MAIN_X + 0.41, y, 0.38, row)

    # Notifications panel
    wf_box(ax, MAIN_X, 0.10, 0.78, 0.32, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.39, 0.405, 'Notifications & Alerts', fontsize=7.5, bold=True, align='center')
    for i, notif in enumerate(['[INFO] Student 2021055 ineligible — 3 absences exceeded',
                                '[WARN] Camera #2 offline — Gate B',
                                '[INFO] Grade export completed — Dept. CS']):
        wf_box(ax, MAIN_X + 0.01, 0.355 - i * 0.07, 0.76, 0.055,
               fc=C['input'], ec=C['light'])
        wf_label(ax, MAIN_X + 0.02, 0.382 - i * 0.07, notif, fontsize=6.5)

    plt.tight_layout()
    path = os.path.join(OUT, 'wf02_admin_dashboard.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf02_admin_dashboard.png")

# ── WIREFRAME 3: Student Dashboard
def wf_student_dashboard():
    fig, [ax] = setup_figure('Wireframe WF-03: Student Dashboard')

    # Topbar
    wf_box(ax, 0.0, 0.92, 1.0, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, 0.03, 0.96, '≡  SHAMEL', fontsize=9, bold=True)
    wf_label(ax, 0.82, 0.96, 'Ahmed Nadir  👤', fontsize=7.5, color=C['mid'])

    # Sidebar
    wf_box(ax, 0.0, 0.0, 0.16, 0.92, fc=C['sidebar'], ec=C['border'])
    items = ['My Dashboard', 'Attendance', 'Schedule', 'Grades', 'Excuses', 'Exams']
    for i, item in enumerate(items):
        y = 0.84 - i * 0.10
        fc = C['btn_primary'] if i == 0 else C['sidebar']
        tc = 'white' if i == 0 else C['dark']
        if i == 0:
            wf_box(ax, 0.01, y - 0.018, 0.14, 0.033, fc=fc, ec=fc)
        wf_label(ax, 0.08, y, item, fontsize=7, color=tc, align='center')

    MAIN_X = 0.18

    # Welcome banner
    wf_box(ax, MAIN_X, 0.82, 0.80, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.40, 0.865, 'Welcome, Ahmed — Computer Science · Year 3', fontsize=8.5, bold=True, align='center')

    # Attendance gauge
    wf_box(ax, MAIN_X, 0.58, 0.20, 0.22, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.10, 0.775, 'Attendance %', fontsize=7, bold=True, align='center')
    circle = plt.Circle((MAIN_X + 0.10, 0.665), 0.062, color=C['mid'], fill=False, lw=2.5)
    ax.add_patch(circle)
    wf_label(ax, MAIN_X + 0.10, 0.665, '87%', fontsize=10, bold=True, align='center')
    wf_label(ax, MAIN_X + 0.10, 0.598, 'Min. required: 75%', fontsize=6, color=C['mid'], align='center')

    # Course breakdown table
    wf_box(ax, MAIN_X + 0.22, 0.58, 0.57, 0.22, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.505, 0.785, 'Course Attendance Breakdown', fontsize=7.5, bold=True, align='center')
    y = 0.755
    y = wf_table_row(ax, MAIN_X + 0.23, y, 0.55,
                     ['Course', 'Sessions', 'Attended', 'Rate', 'Status'], header=True)
    for row in [('Database Systems', '12', '11', '92%', '[OK] OK'),
                ('Algorithms', '10', '8', '80%', '[OK] OK'),
                ('Networking', '14', '10', '71%', '⚠ Low')]:
        y = wf_table_row(ax, MAIN_X + 0.23, y, 0.55, row)

    # Schedule
    wf_box(ax, MAIN_X, 0.30, 0.38, 0.26, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.19, 0.545, "Today's Schedule", fontsize=7.5, bold=True, align='center')
    for i, (t, c, r) in enumerate([('08:00 – 10:00', 'Database Systems', 'Room A-3'),
                                    ('10:30 – 12:30', 'Algorithms', 'Lab B-1'),
                                    ('14:00 – 16:00', 'Networking', 'Room C-2')]):
        ys = 0.505 - i * 0.072
        wf_box(ax, MAIN_X + 0.01, ys - 0.015, 0.36, 0.055, fc=C['input'], ec=C['light'])
        wf_label(ax, MAIN_X + 0.02, ys + 0.012, t, fontsize=6.5, bold=True)
        wf_label(ax, MAIN_X + 0.02, ys - 0.005, f'{c} — {r}', fontsize=6.5, color=C['mid'])

    # Excuses & notifications
    wf_box(ax, MAIN_X + 0.40, 0.30, 0.38, 0.26, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.59, 0.545, 'Recent Notifications', fontsize=7.5, bold=True, align='center')
    for i, n in enumerate(['Session started: Database Systems @ 08:00',
                            'Excuse approved for 2026-05-28',
                            'Grade posted: Algorithms Midterm']):
        wf_box(ax, MAIN_X + 0.41, 0.500 - i * 0.068, 0.36, 0.055,
               fc=C['input'], ec=C['light'])
        wf_label(ax, MAIN_X + 0.42, 0.527 - i * 0.068, n, fontsize=6.5)

    # Bottom bar — quick actions
    wf_box(ax, MAIN_X, 0.05, 0.78, 0.23, fc=C['surface'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.39, 0.26, 'Quick Actions', fontsize=7.5, bold=True, align='center')
    btns = ['Submit Excuse', 'View Grades', 'Download Transcript', 'View Exam Seats']
    for i, b in enumerate(btns):
        wf_btn(ax, MAIN_X + 0.01 + i * 0.195, 0.09, 0.185, label=b, primary=(i == 0))

    plt.tight_layout()
    path = os.path.join(OUT, 'wf03_student_dashboard.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf03_student_dashboard.png")

# ── WIREFRAME 4: Gate Scan Screen
def wf_gate_scan():
    fig, [ax] = setup_figure('Wireframe WF-04: Gate Entry Scan Screen')

    # Full layout — gate-focused
    wf_box(ax, 0.0, 0.92, 1.0, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, 0.40, 0.96, 'SHAMEL — Gate Entry Scanner', fontsize=9, bold=True, align='center')
    wf_label(ax, 0.85, 0.96, '● LIVE', fontsize=8, color=C['mid'])

    # Camera viewport
    wf_box(ax, 0.04, 0.35, 0.52, 0.55, fc='#EEEEEE', ec=C['dark'])
    wf_label(ax, 0.30, 0.62, '[CAMERA FEED]', fontsize=11, align='center', color=C['mid'])
    # Face detection box (dashed)
    det = FancyBboxPatch((0.14, 0.44), 0.22, 0.32,
                         boxstyle="round,pad=0", linewidth=1.5,
                         edgecolor=C['dark'], facecolor='none',
                         linestyle='--', zorder=4)
    ax.add_patch(det)
    wf_label(ax, 0.25, 0.445, 'Face Detection ROI', fontsize=6.5, color=C['dark'], align='center')

    # Corner markers
    for cx, cy in [(0.14, 0.76), (0.36, 0.76), (0.14, 0.44), (0.36, 0.44)]:
        ax.plot(cx, cy, 's', ms=6, color=C['dark'], zorder=5)

    wf_label(ax, 0.30, 0.37, 'Resolution: 640×480 @ 15fps  |  Engine: InsightFace buffalo_s', fontsize=6.5,
             color=C['mid'], align='center')

    # Right panel — result
    wf_box(ax, 0.58, 0.35, 0.38, 0.55, fc=C['surface'], ec=C['border'])
    wf_label(ax, 0.77, 0.87, 'Identification Result', fontsize=8.5, bold=True, align='center')
    wf_divider(ax, 0.59, 0.95, 0.855)

    # Photo placeholder
    wf_box(ax, 0.67, 0.74, 0.20, 0.10, fc=C['header'], ec=C['mid'])
    wf_label(ax, 0.77, 0.790, '[Photo]', fontsize=8, align='center')

    # Info fields
    fields = [('Student ID:', '2021042'), ('Name:', 'Sara Mohamed'),
              ('Department:', 'Computer Science'), ('Year:', '3rd'),
              ('Status:', 'ALLOWED [OK]'), ('Match Score:', '0.91 / 1.00')]
    for i, (lbl, val) in enumerate(fields):
        y = 0.715 - i * 0.058
        wf_label(ax, 0.60, y, lbl, fontsize=7, bold=True)
        wf_label(ax, 0.78, y, val, fontsize=7, color=C['mid'])

    # Action buttons
    wf_btn(ax, 0.60, 0.40, 0.16, label='[OK] Allow', primary=True)
    wf_btn(ax, 0.78, 0.40, 0.16, label='✗ Deny')

    # Log table at bottom
    wf_box(ax, 0.04, 0.06, 0.92, 0.27, fc=C['surface'], ec=C['border'])
    wf_label(ax, 0.50, 0.315, 'Today\'s Gate Log — Live Feed via WebSocket', fontsize=7.5, bold=True, align='center')
    y = 0.285
    y = wf_table_row(ax, 0.05, y, 0.90,
                     ['Time', 'Student ID', 'Name', 'Match Score', 'Direction', 'Status'], header=True)
    for row in [('08:02', '2021001', 'Ahmed N.', '0.93', '→ Entry', '[OK] Allow'),
                ('08:05', '2021042', 'Sara M.', '0.91', '→ Entry', '[OK] Allow'),
                ('08:09', '—', 'Unknown', '0.28', '→ Entry', '✗ Deny'),
                ('08:14', '2020113', 'Omar K.', '0.88', '← Exit', '[OK] Allow')]:
        y = wf_table_row(ax, 0.05, y, 0.90, row)

    plt.tight_layout()
    path = os.path.join(OUT, 'wf04_gate_scan.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf04_gate_scan.png")

# ── WIREFRAME 5: Mobile App — Student View
def wf_mobile_student():
    fig, [ax] = setup_figure('Wireframe WF-05: Mobile App — Student Home (Flutter)')
    # Simulate phone frame 375×812
    ax.set_xlim(0, 0.375)
    ax.set_ylim(0, 0.812)

    # Phone outline
    phone = FancyBboxPatch((0.01, 0.01), 0.355, 0.792,
                           boxstyle="round,pad=0.015", linewidth=2,
                           edgecolor=C['dark'], facecolor=C['bg'], zorder=1)
    ax.add_patch(phone)

    # Status bar
    wf_box(ax, 0.01, 0.775, 0.355, 0.028, fc=C['header'], ec=C['header'])
    ax.text(0.05, 0.789, '9:41', fontsize=6, color=C['dark'], va='center')
    ax.text(0.315, 0.789, '●●●  WiFi  🔋', fontsize=5.5, color=C['dark'], va='center')

    # Top AppBar
    wf_box(ax, 0.01, 0.725, 0.355, 0.05, fc=C['sidebar'], ec=C['border'])
    ax.text(0.1875, 0.75, 'SHAMEL', ha='center', va='center',
            fontsize=9, fontweight='bold', color=C['dark'])
    ax.text(0.34, 0.75, '🔔', fontsize=9, color=C['mid'], va='center', ha='center')

    # Greeting
    ax.text(0.0375, 0.705, 'Good Morning, Ahmed 👋', fontsize=8,
            fontweight='bold', color=C['dark'], va='center')
    ax.text(0.0375, 0.685, 'Computer Science · Year 3', fontsize=6.5,
            color=C['mid'], va='center')

    # Stat cards (horizontal scroll)
    stat_data = [('87%', 'Attendance'), ('3', 'Today\'s Classes'), ('1', 'Pending Excuse')]
    for i, (val, lbl) in enumerate(stat_data):
        x = 0.025 + i * 0.115
        wf_box(ax, x, 0.625, 0.105, 0.052, fc=C['surface'], ec=C['border'])
        ax.text(x + 0.0525, 0.656, val, ha='center', va='center',
                fontsize=9, fontweight='bold', color=C['dark'])
        ax.text(x + 0.0525, 0.636, lbl, ha='center', va='center',
                fontsize=5.5, color=C['mid'])

    # Section: Today's Schedule
    ax.text(0.0375, 0.608, "Today's Schedule", fontsize=8, fontweight='bold', color=C['dark'])
    for i, (t, c, r) in enumerate([('08:00', 'Database Systems', 'Room A-3'),
                                    ('10:30', 'Algorithms', 'Lab B-1')]):
        y = 0.565 - i * 0.075
        wf_box(ax, 0.025, y - 0.022, 0.325, 0.060, fc=C['surface'], ec=C['border'])
        ax.text(0.04, y + 0.018, t, fontsize=7, fontweight='bold', color=C['dark'])
        ax.text(0.04, y, c, fontsize=7, color=C['dark'])
        ax.text(0.04, y - 0.016, r, fontsize=6, color=C['mid'])
        ax.text(0.325, y, '▶', fontsize=8, color=C['mid'], ha='right', va='center')

    # Section: Notifications
    ax.text(0.0375, 0.415, 'Notifications', fontsize=8, fontweight='bold', color=C['dark'])
    for i, n in enumerate(['Session started: Database Systems',
                            'Grade posted: Algorithms Midterm']):
        y = 0.380 - i * 0.065
        wf_box(ax, 0.025, y - 0.018, 0.325, 0.050, fc=C['input'], ec=C['light'])
        ax.text(0.04, y + 0.010, '🔔', fontsize=7, color=C['mid'])
        ax.text(0.075, y + 0.010, n, fontsize=6.5, color=C['dark'])
        ax.text(0.04, y - 0.008, '2 min ago', fontsize=5.5, color=C['mid'])

    # Bottom nav bar
    wf_box(ax, 0.01, 0.01, 0.355, 0.06, fc=C['header'], ec=C['border'])
    nav_items = [('🏠', 'Home'), ('📅', 'Schedule'), ('📊', 'Grades'), ('📋', 'Excuses')]
    for i, (icon, label) in enumerate(nav_items):
        x = 0.055 + i * 0.085
        fc = C['btn_primary'] if i == 0 else C['header']
        ax.text(x, 0.048, icon, ha='center', va='center', fontsize=9)
        ax.text(x, 0.025, label, ha='center', va='center', fontsize=5.5,
                color=C['dark' if i == 0 else 'mid'])

    plt.tight_layout()
    path = os.path.join(OUT, 'wf05_mobile_student.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf05_mobile_student.png")

# ── WIREFRAME 6: Teacher — Mark Attendance
def wf_teacher_attendance():
    fig, [ax] = setup_figure('Wireframe WF-06: Teacher — Mark Attendance')

    # Topbar
    wf_box(ax, 0.0, 0.92, 1.0, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, 0.03, 0.96, '≡  SHAMEL', fontsize=9, bold=True)
    wf_label(ax, 0.75, 0.96, 'Prof. Khalid Ibrahim  |  Role: Teacher', fontsize=7.5, color=C['mid'])

    # Sidebar
    wf_box(ax, 0.0, 0.0, 0.16, 0.92, fc=C['sidebar'], ec=C['border'])
    items = ['Dashboard', 'My Courses', 'Mark Attendance', 'Grade Sheets', 'Students', 'Reports']
    for i, item in enumerate(items):
        y = 0.84 - i * 0.10
        if i == 2:
            wf_box(ax, 0.01, y - 0.018, 0.14, 0.033, fc=C['btn_primary'], ec=C['btn_primary'])
            wf_label(ax, 0.08, y, item, fontsize=7, color='white', align='center')
        else:
            wf_label(ax, 0.08, y, item, fontsize=7, color=C['dark'], align='center')

    MAIN_X = 0.18

    # Session header
    wf_box(ax, MAIN_X, 0.82, 0.80, 0.08, fc=C['header'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.02, 0.865, 'Session: Database Systems — Lecture 9  |  2026-06-04  |  Room A-3', fontsize=8, bold=True)

    # Filter row
    wf_label(ax, MAIN_X, 0.79, 'Filter:', fontsize=7, color=C['mid'])
    for i, label in enumerate(['All', 'Present', 'Absent', 'Excused']):
        x = MAIN_X + 0.08 + i * 0.085
        fc = C['btn_primary'] if i == 0 else C['btn']
        tc = 'white' if i == 0 else C['dark']
        wf_box(ax, x, 0.778, 0.075, 0.028, fc=fc, ec=C['border'])
        ax.text(x + 0.0375, 0.792, label, ha='center', va='center', fontsize=7, color=tc)

    wf_input(ax, MAIN_X + 0.55, 0.778, 0.22, placeholder='🔍 Search student...')
    wf_btn(ax, MAIN_X + 0.79, 0.778, 0.10, label='Export', primary=False)

    # Attendance table
    wf_box(ax, MAIN_X, 0.11, 0.80, 0.66, fc=C['surface'], ec=C['border'])
    y = 0.745
    y = wf_table_row(ax, MAIN_X + 0.01, y, 0.78,
                     ['#', 'Student ID', 'Name', 'Present', 'Late', 'Absent', 'Notes'], header=True)
    students = [
        ('1', '2021001', 'Ahmed Nadir Mohammed', '●', '', '', ''),
        ('2', '2021042', 'Sara Khalid Ibrahim', '●', '', '', ''),
        ('3', '2021055', 'Omar Salah Ahmed', '', '', '●', 'No face match'),
        ('4', '2021078', 'Fatima Hassan', '', '●', '', 'Late 8 min'),
        ('5', '2021099', 'Youssef Al-Amin', '●', '', '', ''),
        ('6', '2020113', 'Nada Osman', '', '', '●', 'Medical excuse'),
        ('7', '2021120', 'Bilal Mukhtar', '●', '', '', ''),
        ('8', '2021145', 'Heba Siddiq', '●', '', '', ''),
    ]
    for row in students:
        y = wf_table_row(ax, MAIN_X + 0.01, y, 0.78, row)

    # Summary bar
    wf_box(ax, MAIN_X, 0.06, 0.80, 0.04, fc=C['header'], ec=C['border'])
    wf_label(ax, MAIN_X + 0.02, 0.080, 'Present: 6  |  Late: 1  |  Absent: 2  |  Total: 9  |  Attendance Rate: 77.8%',
             fontsize=7.5, bold=True)

    wf_btn(ax, MAIN_X + 0.55, 0.017, 0.12, label='Save Draft')
    wf_btn(ax, MAIN_X + 0.68, 0.017, 0.12, label='Submit Final', primary=True)

    plt.tight_layout()
    path = os.path.join(OUT, 'wf06_teacher_attendance.png')
    plt.savefig(path, dpi=200, bbox_inches='tight', facecolor=C['bg'])
    plt.close()
    print(f"  [OK] wf06_teacher_attendance.png")

if __name__ == '__main__':
    print("Generating SHAMEL wireframes (monochrome)...")
    wf_login()
    wf_admin_dashboard()
    wf_student_dashboard()
    wf_gate_scan()
    wf_mobile_student()
    wf_teacher_attendance()
    print(f"\nAll wireframes saved → {OUT}")
