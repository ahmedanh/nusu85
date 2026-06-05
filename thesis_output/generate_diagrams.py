"""
SHAMEL Thesis — Diagram Generator
Generates Fig 3.1 (Architecture), 3.2 (ERD), 3.3 (Use Case), 3.4 (Sequence)
Output: thesis_output/diagrams/*.png  @300dpi
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

OUT = os.path.join(os.path.dirname(__file__), 'diagrams')
os.makedirs(OUT, exist_ok=True)

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def box(ax, x, y, w, h, label, sublabel=None, fc='#E8EEF8', ec='#2C4A7C', lw=1.5,
        fontsize=11, bold=False):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0",
                          linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    cy = y + h / 2 + (0.018 if sublabel else 0)
    ax.text(x + w / 2, cy, label, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color='#0B1E38', zorder=4)
    if sublabel:
        ax.text(x + w / 2, y + h / 2 - 0.03, sublabel, ha='center', va='center',
                fontsize=9, color='#4A6080', zorder=4, style='italic')


def arr(ax, x1, y1, x2, y2, label='', color='#2C4A7C', lw=1.5):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color=color, lw=lw),
                zorder=5)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.02, my + 0.02, label, fontsize=9, color='#334466',
                ha='center', va='bottom', zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.85))


def layer_bg(ax, x, y, w, h, label, fc='#F0F4FC', ec='#8AAAD0'):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0",
                          linewidth=1.5, edgecolor=ec, facecolor=fc,
                          linestyle='--', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.02, y + h - 0.025, label, fontsize=10, color='#4A6A90',
            fontweight='bold', va='top', zorder=2)


# ─────────────────────────────────────────────
# FIG 3.1 — SYSTEM ARCHITECTURE
# ─────────────────────────────────────────────
def fig_architecture():
    fig, ax = plt.subplots(figsize=(22, 14), constrained_layout=True)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 14)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Layer backgrounds  (x, y, w, h)
    layer_bg(ax, 0.3, 10.5, 21.4, 3.0,  'CLIENT LAYER',              '#EEF4FF', '#6690CC')
    layer_bg(ax, 0.3,  6.0, 21.4, 4.1,  'APPLICATION LAYER',         '#F0FFF4', '#4A9A6A')
    layer_bg(ax, 0.3,  3.0, 21.4, 2.7,  'SERVICE / PROCESSING LAYER','#FFF8F0', '#C07A2A')
    layer_bg(ax, 0.3,  0.3, 21.4, 2.4,  'DATA LAYER',                '#FFF0F0', '#C04A4A')

    # CLIENT LAYER — y=11.0, h=2.0
    box(ax, 0.6,  11.0, 4.5, 2.0, 'Web Browser',
        'Admin / Teacher / Student / Gate', fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=11)
    box(ax, 5.8,  11.0, 4.5, 2.0, 'Flutter Mobile App',
        'Android — REST + WebSocket',        fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=11)
    box(ax, 11.0, 11.0, 4.5, 2.0, 'Gate Camera',
        'RTSP / USB — Face Capture',         fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=11)
    box(ax, 16.2, 11.0, 4.5, 2.0, 'PWA / Offline',
        'Service Worker Cache',              fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=11)

    # APPLICATION LAYER — row1 y=8.2, row2 y=6.4
    box(ax, 0.6,  8.2, 5.5, 1.6, 'Nginx Reverse Proxy',  ':80/:443 -> :9000',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)
    box(ax, 7.2,  8.2, 6.0, 1.6, 'Daphne ASGI Server',  ':9000 — HTTP + WebSocket',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)
    box(ax, 14.4, 8.2, 6.0, 1.6, 'Django Channels',     'WebSocket Consumers',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)

    box(ax, 0.6,  6.2, 4.0, 1.6, 'Django MVT',    'Views / Templates', fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 5.2,  6.2, 4.0, 1.6, 'REST API',      '/api/v1/ — Token Auth', fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 9.8,  6.2, 4.0, 1.6, 'Auth & RBAC',   '5 Roles — Session/JWT', fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 14.4, 6.2, 3.5, 1.6, 'Edge Cache',    'SQLite — Offline API',  fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 18.3, 6.2, 3.0, 1.6, 'Async Tasks',   'AsyncTask Model',       fc='#CCE8CC', ec='#1A6A3A')

    # SERVICE LAYER — y=3.3, h=1.8
    box(ax, 0.6,  3.3, 5.0, 1.8, 'InsightFace + ONNX',
        'buffalo_s — 512-dim cosine >= 0.65',   fc='#FFE8CC', ec='#B05010', bold=True)
    box(ax, 6.6,  3.3, 4.5, 1.8, 'face_engine.py',
        'Dlib fallback — 128-dim Euclidean',    fc='#FFE8CC', ec='#B05010')
    box(ax, 12.1, 3.3, 4.0, 1.8, 'Email / SMTP',
        'Ineligible alerts\nExam reminders',    fc='#FFE8CC', ec='#B05010')
    box(ax, 17.1, 3.3, 4.2, 1.8, 'WeasyPrint / PDF',
        'Reports export\nGrade sheets',         fc='#FFE8CC', ec='#B05010')

    # DATA LAYER — y=0.5, h=1.8
    box(ax, 0.6,  0.5, 5.0, 1.8, 'PostgreSQL',
        '25 tables | HNSW Index (pgvector)\npg_trgm Fuzzy Search', fc='#FFD8D8', ec='#AA2222', bold=True)
    box(ax, 6.6,  0.5, 4.5, 1.8, 'Redis Cache',
        'Session state\nAttendance pub/sub | Channel layers', fc='#FFD8D8', ec='#AA2222', bold=True)
    box(ax, 12.1, 0.5, 4.0, 1.8, 'SQLite Fallback',
        'db_local.sqlite3\nOffline dev/edge',  fc='#FFD8D8', ec='#AA2222')
    box(ax, 17.1, 0.5, 4.2, 1.8, 'Static / Media',
        'Nginx served\nFace images | PDF exports', fc='#FFD8D8', ec='#AA2222')

    # Arrows — client -> nginx
    for cx, ex in [(2.85, 3.35), (8.05, 4.80), (13.25, 5.50), (18.45, 5.50)]:
        arr(ax, cx, 11.0, ex, 9.8, color='#336699')

    # Nginx -> Daphne
    arr(ax, 6.1, 9.0, 7.2, 9.0, 'proxy', color='#2A7A4A')
    # Daphne -> Channels
    arr(ax, 13.2, 9.0, 14.4, 9.0, 'WS', color='#2A7A4A')
    # Daphne -> MVT / REST
    arr(ax, 10.2, 8.2, 2.6, 7.8, color='#2A7A4A')
    arr(ax, 10.2, 8.2, 7.2, 7.8, color='#2A7A4A')

    # App -> Service
    arr(ax, 2.6, 6.2, 3.1, 5.1, color='#C07A2A')
    arr(ax, 7.2, 6.2, 8.85, 5.1, color='#C07A2A')

    # Service -> Data
    arr(ax, 3.1, 3.3, 3.1, 2.3, color='#C04A4A')
    arr(ax, 8.85, 3.3, 8.85, 2.3, color='#C04A4A')
    arr(ax, 2.6, 6.2, 2.6, 2.3, 'DB', color='#C04A4A', lw=1.0)

    # Title & caption
    fig.text(0.5, 0.995,
             'Figure 3.1: SHAMEL System Architecture — Flutter Mobile, ASGI/WebSocket, Redis & InsightFace',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.002,
             'Dashed borders = architectural layers.  Solid arrows = data/request flow.',
             ha='center', va='bottom', fontsize=9, color='#5A7090', style='italic')

    path = os.path.join(OUT, 'fig3_1_architecture.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('  [OK] fig3_1_architecture.png')


# ─────────────────────────────────────────────
# FIG 3.2 — DATABASE ERD
# ─────────────────────────────────────────────
def fig_erd():
    fig, ax = plt.subplots(figsize=(24, 16), constrained_layout=True)
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 16)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    def entity(x, y, w, h, name, fields, note=None, highlight=False):
        hdr_c = '#1A3A6A' if highlight else '#2C4A7C'
        bdy_c = '#E8F0FF' if highlight else '#EEF3FF'
        hdr_h = 0.70
        hdr = FancyBboxPatch((x, y + h - hdr_h), w, hdr_h,
                             boxstyle="round,pad=0", linewidth=1.8,
                             edgecolor=hdr_c, facecolor=hdr_c, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w / 2, y + h - hdr_h / 2, name, ha='center', va='center',
                fontsize=11, fontweight='bold', color='white', zorder=4)
        bdy = FancyBboxPatch((x, y), w, h - hdr_h,
                             boxstyle="round,pad=0", linewidth=1.8,
                             edgecolor=hdr_c, facecolor=bdy_c, zorder=3)
        ax.add_patch(bdy)
        row_h = 0.36
        for i, (pk, fname, ftype) in enumerate(fields):
            yf = y + h - hdr_h - 0.30 - i * row_h
            prefix = '[PK] ' if pk == 'PK' else ('[FK] ' if pk == 'FK' else '     ')
            ax.text(x + 0.12, yf, f"{prefix}{fname}", fontsize=9, color='#1A2A4A',
                    va='center', zorder=4)
            ax.text(x + w - 0.12, yf, ftype, fontsize=8, color='#4A6080',
                    va='center', ha='right', zorder=4, style='italic')
        if note:
            ax.text(x + w / 2, y + 0.12, note, fontsize=8, color='#AA4400',
                    ha='center', va='bottom', zorder=4, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.2', fc='#FFF0E0', ec='#CC6600', lw=1))

    def rel(x1, y1, x2, y2, label='', style='1:N'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#445577', lw=1.3),
                    zorder=5)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if label:
            ax.text(mx, my + 0.15, label, fontsize=8, color='#334466',
                    ha='center', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.85))
        ax.text(mx + 0.25, my - 0.12, style, fontsize=8, color='#667799', ha='center', zorder=6)

    # Row 1 — y=11.5
    entity(0.3,  11.5, 3.8, 3.8, 'College',
           [('PK','id','INT'), ('','name','VARCHAR'), ('','code','VARCHAR'), ('','coordinator_id','FK')])
    entity(4.5,  11.5, 4.0, 3.8, 'Department',
           [('PK','id','INT'), ('FK','college_id','->College'), ('','name','VARCHAR'), ('','code','VARCHAR')])
    entity(9.0,  11.5, 4.0, 3.8, 'Course',
           [('PK','id','INT'), ('FK','department_id','->Dept'), ('','name','VARCHAR'),
            ('','code','VARCHAR'), ('','credit_hours','INT')])
    entity(13.5, 11.5, 4.5, 3.8, 'Student',
           [('PK','id','INT'), ('FK','department_id','->Dept'), ('','student_id','VARCHAR'),
            ('','name_ar','VARCHAR [pg_trgm]'), ('','is_allowed_entry','BOOL')])
    entity(18.5, 11.5, 4.8, 3.8, 'Teacher',
           [('PK','id','INT'), ('FK','department_id','->Dept'), ('','employee_id','VARCHAR'),
            ('','name_ar','VARCHAR'), ('','specialization','VARCHAR')])

    # Row 2 — y=6.5
    entity(0.3, 6.5, 4.5, 4.5, 'StudentFaceEmbedding',
           [('PK','id','INT'), ('FK','student_id','->Student'),
            ('','embedding','VECTOR(512)'), ('','engine','VARCHAR'),
            ('','enrolled_at','DATETIME'), ('','is_active','BOOL')],
           note='[HNSW Index on embedding]\n(pgvector cosine distance)',
           highlight=True)
    entity(5.5, 6.5, 4.3, 4.0, 'Schedule',
           [('PK','id','INT'), ('FK','course_id','->Course'),
            ('FK','teacher_id','->Teacher'), ('FK','classroom_id','->Room'),
            ('','day_of_week','INT'), ('','start_time','TIME')])
    entity(10.5, 6.5, 4.3, 4.0, 'LectureSession',
           [('PK','id','INT'), ('FK','schedule_id','->Schedule'),
            ('','date','DATE'), ('','status','VARCHAR'),
            ('','started_at','DATETIME'), ('','ended_at','DATETIME')])
    entity(15.5, 6.5, 4.3, 4.0, 'AIAttendanceLog',
           [('PK','id','INT'), ('FK','session_id','->Session'),
            ('FK','student_id','->Student'), ('','confidence','FLOAT'),
            ('','method','VARCHAR'), ('','marked_at','DATETIME')])
    entity(20.2, 6.5, 3.5, 3.5, 'GateLog',
           [('PK','id','INT'), ('FK','student_id','->Student'),
            ('','entry_time','DATETIME'), ('','match_score','FLOAT'),
            ('','direction','VARCHAR')])

    # Row 3 — y=1.5
    entity(0.3, 1.5, 4.3, 4.5, 'MedicalExcuse',
           [('PK','id','INT'), ('FK','student_id','->Student'),
            ('','date_from','DATE'), ('','date_to','DATE'),
            ('','status','VARCHAR'), ('','document','FILE')])
    entity(5.3, 1.5, 4.3, 4.0, 'Exam / ExamSeat',
           [('PK','id','INT'), ('FK','course_id','->Course'),
            ('FK','student_id','->Student'), ('','hall','VARCHAR'),
            ('','seat_no','INT'), ('','exam_date','DATETIME')])
    entity(10.3, 1.5, 4.3, 4.0, 'Grade',
           [('PK','id','INT'), ('FK','session_id','->Session'),
            ('FK','student_id','->Student'), ('','midterm','FLOAT'),
            ('','final','FLOAT'), ('','total','FLOAT')])
    entity(15.3, 1.5, 4.3, 3.8, 'Notification',
           [('PK','id','INT'), ('FK','user_id','->User'),
            ('','title','VARCHAR'), ('','body','TEXT'),
            ('','is_read','BOOL'), ('','created_at','DATETIME')])
    entity(20.3, 1.5, 3.4, 3.8, 'AuditLog',
           [('PK','id','INT'), ('FK','user_id','->User'),
            ('','action','VARCHAR'), ('','table_name','VARCHAR'),
            ('','record_id','INT')])

    # Index note box
    ax.text(0.3, 1.0,
            '[Performance Indexes]  HNSW (pgvector) on StudentFaceEmbedding.embedding -- O(log N) ANN search  |'
            '  pg_trgm GIN on Student.name_ar, Course.name  |  B-tree on all FK + date columns',
            fontsize=9, color='#443300', va='top',
            bbox=dict(boxstyle='round,pad=0.4', fc='#FFF8EE', ec='#CC8800', lw=1))

    # Relations row1
    rel(4.1,  13.4, 4.5,  13.4, 'has',    '1:N')
    rel(8.5,  13.4, 9.0,  13.4, 'offers', '1:N')
    rel(13.0, 13.4, 13.5, 13.4, 'enrolls','1:N')
    rel(18.0, 13.4, 18.5, 13.4, 'teaches','1:N')
    # row2 horizontals
    rel(9.8,  8.5, 10.5, 8.5, 'generates','1:N')
    rel(14.8, 8.5, 15.5, 8.5, 'records',  '1:N')
    rel(19.8, 8.5, 20.2, 8.5, 'gate log', '1:N')
    # student -> face embed (vertical)
    rel(15.75, 11.5, 2.55, 11.0, 'face embed', '1:1')

    fig.text(0.5, 0.998,
             'Figure 3.2: SHAMEL Database ERD — HNSW pgvector Index & pg_trgm Trigram Indexes',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.001,
             '[PK] = Primary Key  |  [FK] = Foreign Key  |  [HNSW] = pgvector ANN index  |  [pg_trgm] = trigram index',
             ha='center', va='bottom', fontsize=9, color='#5A7090', style='italic')

    path = os.path.join(OUT, 'fig3_2_erd.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('  [OK] fig3_2_erd.png')


# ─────────────────────────────────────────────
# FIG 3.3 — USE CASE DIAGRAM
# ─────────────────────────────────────────────
def fig_usecase():
    fig, ax = plt.subplots(figsize=(22, 16), constrained_layout=True)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 16)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    def actor(x, y, label, color='#2C4A7C'):
        # head
        ax.plot(x, y + 0.90, 'o', ms=18, color=color, zorder=5,
                markerfacecolor=color, markeredgecolor=color)
        # torso
        ax.plot([x, x], [y + 0.30, y - 0.50], color=color, lw=2.5, zorder=5)
        # arms
        ax.plot([x - 0.50, x + 0.50], [y + 0.10, y + 0.10], color=color, lw=2.5, zorder=5)
        # legs
        ax.plot([x, x - 0.40], [y - 0.50, y - 1.20], color=color, lw=2.5, zorder=5)
        ax.plot([x, x + 0.40], [y - 0.50, y - 1.20], color=color, lw=2.5, zorder=5)
        ax.text(x, y - 1.60, label, ha='center', va='top', fontsize=10,
                fontweight='bold', color=color, zorder=5,
                bbox=dict(boxstyle='round,pad=0.2', fc='white', ec='none', alpha=0.85))

    def usecase(x, y, w, h, label, sublabel=None, mobile=False):
        ec = '#1A6A9A' if mobile else '#2C4A7C'
        fc = '#D8F0FF' if mobile else '#EEF3FF'
        ell = mpatches.Ellipse((x, y), w, h, linewidth=1.5,
                                edgecolor=ec, facecolor=fc, zorder=3)
        ax.add_patch(ell)
        dy = 0.12 if sublabel else 0
        ax.text(x, y + dy, label, ha='center', va='center',
                fontsize=9.5, color='#0B1E38', zorder=4,
                fontweight='bold' if mobile else 'normal')
        if sublabel:
            ax.text(x, y - 0.30, sublabel, ha='center', va='center',
                    fontsize=8, color='#3A6A8A', zorder=4, style='italic')

    def uc_line(ax1, ay, ux, uy, dashed=False):
        ls = '--' if dashed else '-'
        ax.plot([ax1, ux], [ay, uy], color='#8899AA', lw=1.0, ls=ls, zorder=2)

    # System boundary
    rect = FancyBboxPatch((3.0, 0.8), 15.5, 14.5,
                          boxstyle="round,pad=0", linewidth=2.5,
                          edgecolor='#2C4A7C', facecolor='#F8FAFF', zorder=1)
    ax.add_patch(rect)
    ax.text(10.75, 15.0, 'SHAMEL System', ha='center', va='center',
            fontsize=14, fontweight='bold', color='#0B1E38')

    # Mobile sub-boundary
    rect_m = FancyBboxPatch((3.2, 1.0), 7.0, 7.5,
                            boxstyle="round,pad=0", linewidth=1.8,
                            edgecolor='#1A6A9A', facecolor='#EEF8FF',
                            linestyle='--', zorder=2)
    ax.add_patch(rect_m)
    ax.text(6.7, 8.3, 'Mobile App (Flutter)', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#1A6A9A')

    # Web sub-boundary
    rect_w = FancyBboxPatch((10.8, 1.0), 7.5, 13.5,
                            boxstyle="round,pad=0", linewidth=1.8,
                            edgecolor='#4A7A4A', facecolor='#F0FFF0',
                            linestyle='--', zorder=2)
    ax.add_patch(rect_w)
    ax.text(14.55, 14.3, 'Web Interface', ha='center', va='center',
            fontsize=10, fontweight='bold', color='#2A6A2A')

    # ── ACTORS left (x=1.4)
    actor(1.4, 13.5, 'Student',     '#1A5A9A')
    actor(1.4, 10.2, 'Teacher',     '#2A6A2A')
    actor(1.4,  7.0, 'Gate\nOperator', '#8A4A2A')
    actor(1.4,  3.8, 'Coordinator', '#5A2A8A')

    # ── ACTORS right (x=20.0)
    actor(20.0, 13.0, 'Admin',        '#AA2222')
    actor(20.0,  9.5, 'SMTP\nServer', '#666666')
    actor(20.0,  6.0, 'Face\nEngine', '#AA6600')

    # ── MOBILE USE CASES (x=6.7, stacked vertically)
    usecase(6.7, 7.4, 5.5, 1.0, 'View Attendance History',    '(Mobile)',            mobile=True)
    usecase(6.7, 5.9, 5.5, 1.0, 'Receive Push Notifications', '(Mobile)',            mobile=True)
    usecase(6.7, 4.4, 5.5, 1.0, 'View Schedule',              '(Mobile)',            mobile=True)
    usecase(6.7, 2.9, 5.5, 1.0, 'Submit Medical Excuse',      '(Mobile)',            mobile=True)
    usecase(6.7, 1.5, 5.5, 1.0, 'View Course Sessions',       '(Mobile — Teacher)', mobile=True)

    # ── WEB USE CASES (x=14.55, stacked)
    usecase(14.55, 13.5, 6.0, 1.0, 'Manage Users / Roles')
    usecase(14.55, 12.0, 6.0, 1.0, 'View Audit Logs')
    usecase(14.55, 10.5, 6.0, 1.0, 'System Configuration')
    usecase(14.55,  9.0, 6.0, 1.0, 'Mark Attendance')
    usecase(14.55,  7.5, 6.0, 1.0, 'Export Reports (PDF/Excel)')
    usecase(14.55,  6.0, 6.0, 1.0, 'Manage Excuses')
    usecase(14.55,  4.5, 6.0, 1.0, 'Face Scan at Gate', 'InsightFace ONNX')
    usecase(14.55,  3.0, 6.0, 1.0, 'Generate Grade Sheets')
    usecase(14.55,  1.5, 6.0, 1.0, 'Send Alert Notifications', 'SMTP')

    # Lines — Student
    for uy in [7.4, 5.9, 4.4, 2.9]:
        uc_line(2.3, 13.5, 3.95, uy)
    for uy in [9.0, 6.0, 7.5]:
        uc_line(2.3, 13.5, 11.55, uy)

    # Teacher
    for uy in [1.5, 5.9]:
        uc_line(2.3, 10.2, 3.95, uy)
    for uy in [9.0, 7.5, 3.0]:
        uc_line(2.3, 10.2, 11.55, uy)

    # Gate
    uc_line(2.3, 7.0, 11.55, 4.5)

    # Coordinator
    for uy in [6.0, 3.0, 1.5]:
        uc_line(2.3, 3.8, 11.55, uy)

    # Admin (right)
    for uy in [13.5, 12.0, 10.5]:
        uc_line(19.0, 13.0, 17.55, uy)

    # SMTP
    uc_line(19.0, 9.5, 17.55, 1.5, dashed=True)

    # FaceEngine
    uc_line(19.0, 6.0, 17.55, 4.5, dashed=True)

    # Legend
    ax.add_patch(mpatches.Ellipse((3.5, 0.35), 1.2, 0.45, linewidth=1.2,
                                   edgecolor='#1A6A9A', facecolor='#D8F0FF', zorder=5))
    ax.text(4.3, 0.35, '= Mobile App Feature', fontsize=9, va='center', color='#1A6A9A', zorder=6)
    ax.add_patch(mpatches.Ellipse((9.0, 0.35), 1.2, 0.45, linewidth=1.2,
                                   edgecolor='#2C4A7C', facecolor='#EEF3FF', zorder=5))
    ax.text(9.8, 0.35, '= Web Feature', fontsize=9, va='center', color='#2C4A7C', zorder=6)

    fig.text(0.5, 0.998,
             'Figure 3.3: SHAMEL Use Case Diagram — Mobile App Features (Flutter)',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#0B1E38')

    path = os.path.join(OUT, 'fig3_3_usecase.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('  [OK] fig3_3_usecase.png')


# ─────────────────────────────────────────────
# FIG 3.4 — SEQUENCE: GATE ENTRY
# ─────────────────────────────────────────────
def fig_sequence():
    fig, ax = plt.subplots(figsize=(22, 13), constrained_layout=True)
    ax.set_xlim(0, 22)
    ax.set_ylim(0, 13)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    parts = [
        ('Camera / Gate\nHardware',         1.5,  '#2C4A7C'),
        ('face_engine.py\n(InsightFace+ONNX)', 5.0, '#B05010'),
        ('Django\nViews/API',               8.8,  '#2A6A2A'),
        ('PostgreSQL\n(HNSW Index)',        12.5,  '#AA2222'),
        ('Redis\nChannel Layer',            16.0,  '#AA6600'),
        ('Gate Operator\nUI / Flutter App', 19.5,  '#1A5A9A'),
    ]

    TOP = 11.8
    BOTTOM = 0.6

    # Lifelines + header boxes
    for label, x, color in parts:
        head = FancyBboxPatch((x - 1.2, TOP), 2.4, 0.9,
                              boxstyle="round,pad=0", linewidth=2,
                              edgecolor=color, facecolor=color, zorder=3)
        ax.add_patch(head)
        ax.text(x, TOP + 0.45, label, ha='center', va='center',
                fontsize=9, fontweight='bold', color='white', zorder=4,
                multialignment='center')
        ax.plot([x, x], [TOP, BOTTOM], color=color, lw=1.2, ls='--', alpha=0.45, zorder=1)

    def msg(y, x1, x2, label, color='#334466', ret=False, note=None):
        style = '<-' if ret else '->'
        ls = 'dashed' if ret else 'solid'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.5,
                                   linestyle=ls),
                    zorder=5)
        lx = (x1 + x2) / 2
        ax.text(lx, y + 0.12, label, ha='center', va='bottom',
                fontsize=9, color=color, zorder=6,
                bbox=dict(boxstyle='round,pad=0.18', fc='white', ec='none', alpha=0.92))
        if note:
            ax.text(lx, y - 0.18, note, ha='center', va='top',
                    fontsize=8, color='#AA4400', style='italic', zorder=6)

    def act_box(x, y_top, y_bot, color='#CCDDFF', ec='#445577'):
        w = 0.32
        rect = FancyBboxPatch((x - w / 2, y_bot), w, y_top - y_bot,
                              boxstyle="round,pad=0", linewidth=1.2,
                              edgecolor=ec, facecolor=color, zorder=2)
        ax.add_patch(rect)

    def step(y, text):
        ax.text(0.1, y, text, fontsize=8, color='#667788', va='center', style='italic')

    # Activation boxes
    act_box(5.0,  10.5,  7.8, '#FFE8CC', '#B05010')
    act_box(8.8,   9.6,  7.2, '#E0F0E0', '#2A6A2A')
    act_box(12.5,  8.4,  6.8, '#FFD8D8', '#AA2222')
    act_box(16.0,  5.6,  3.8, '#FFE8CC', '#AA6600')
    act_box(19.5,  3.2,  2.0, '#D8E8FF', '#1A5A9A')

    # Messages — evenly spaced y from 10.8 down to 2.0
    msg(10.8, 1.5,  5.0, '1.  Frame: JPEG/RTSP  640x480', '#2C4A7C')
    step(10.8, 'Step 1')

    msg(10.1, 5.0,  5.0, '2.  Detect face bounding box (RetinaFace)', '#B05010')
    ax.text(5.0, 9.85, '     RetinaFace detector', fontsize=8, color='#885520', style='italic')

    msg( 9.4, 5.0,  5.0, '3.  Crop + align face ROI', '#B05010')

    msg( 8.7, 5.0,  5.0, '4.  InsightFace ONNX inference  ->  512-dim embedding', '#B05010')
    ax.text(5.0, 8.45, '     buffalo_s model, CPU', fontsize=8, color='#885520', style='italic')
    step(9.4, 'Step 2')

    msg( 8.0, 5.0,  8.8, '5.  POST /api/v1/scan/ { embedding }', '#2A6A2A')
    step(8.0, 'Step 3')

    msg( 7.3, 8.8, 12.5,
         '6.  SELECT student WHERE embedding <=> $1 < 0.65',
         '#AA2222',
         note='HNSW cosine ANN search — O(log N)')
    step(7.3, 'Step 4')

    msg( 6.6, 12.5, 12.5, '7.  Top-1 match + confidence score', '#AA2222')

    msg( 5.9, 12.5,  8.8, '8.  Student record + match_score', '#2A6A2A', ret=True)
    step(5.9, 'Step 5')

    msg( 5.2, 8.8,  8.8,
         '9.  Create GateLog entry + mark attendance',
         '#2A6A2A',
         note='INSERT attendance_gatelog')

    msg( 4.5, 8.8, 16.0,
         '10. Publish to Redis channel  gate.attendance.{student_id}',
         '#AA6600')
    step(4.5, 'Step 6')

    msg( 3.8, 16.0, 19.5,
         '11. WebSocket broadcast  { student, match_score, timestamp }',
         '#1A5A9A',
         note='Async via Django Channels consumer')
    step(3.8, 'Step 7')

    msg( 3.1, 1.5,  1.5,
         '12. LED / Door relay trigger  (green=allow, red=deny)',
         '#2C4A7C', ret=True)
    step(3.1, 'Step 8')

    msg( 2.4, 19.5, 19.5,
         '13. UI update: photo + name  | attendance confirmed toast',
         '#1A5A9A')
    step(2.4, 'Step 9')

    # Highlight box around HNSW note
    note_box = FancyBboxPatch((9.0, 6.8), 7.5, 0.7,
                              boxstyle="round,pad=0.05", linewidth=1.0,
                              edgecolor='#AA4400', facecolor='#FFF4EE',
                              linestyle='--', zorder=7)
    ax.add_patch(note_box)

    fig.text(0.5, 0.998,
             'Figure 3.4: Gate Entry Sequence — InsightFace ONNX + HNSW pgvector + WebSocket Async Broadcast',
             ha='center', va='top', fontsize=13, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.001,
             'Dashed lifeline = idle  |  Activation box = executing  |  Dashed arrow = return message',
             ha='center', va='bottom', fontsize=9, color='#5A7090', style='italic')

    path = os.path.join(OUT, 'fig3_4_sequence.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('  [OK] fig3_4_sequence.png')


# ─────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("Generating SHAMEL thesis diagrams...")
    fig_architecture()
    fig_erd()
    fig_usecase()
    fig_sequence()
    print(f"\nAll diagrams saved -> {OUT}")
