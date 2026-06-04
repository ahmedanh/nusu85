"""
SHAMEL Thesis — Diagram Generator
Generates Fig 3.1 (Architecture), 3.2 (ERD), 3.3 (Use Case), 3.4 (Sequence)
Output: thesis_output/diagrams/*.png  @300dpi
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patheffects as pe
import os

OUT = os.path.join(os.path.dirname(__file__), 'diagrams')
os.makedirs(OUT, exist_ok=True)

FONT_TITLE = {'fontsize': 10, 'fontweight': 'bold', 'fontfamily': 'DejaVu Sans'}
FONT_LABEL = {'fontsize': 8, 'fontfamily': 'DejaVu Sans'}
FONT_SMALL = {'fontsize': 6.5, 'fontfamily': 'DejaVu Sans'}

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def box(ax, x, y, w, h, label, sublabel=None, fc='#E8EEF8', ec='#2C4A7C', lw=1.2,
        fontsize=8, bold=False, radius=0.02):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle=f"round,pad=0",
                          linewidth=lw, edgecolor=ec, facecolor=fc, zorder=3)
    ax.add_patch(rect)
    weight = 'bold' if bold else 'normal'
    cy = y + h/2 + (0.012 if sublabel else 0)
    ax.text(x + w/2, cy, label, ha='center', va='center',
            fontsize=fontsize, fontweight=weight, color='#0B1E38', zorder=4)
    if sublabel:
        ax.text(x + w/2, y + h/2 - 0.022, sublabel, ha='center', va='center',
                fontsize=6, color='#4A6080', zorder=4, style='italic')

def arr(ax, x1, y1, x2, y2, label='', color='#2C4A7C', style='->', lw=1.2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw),
                zorder=5)
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx+0.01, my+0.01, label, fontsize=6, color='#334466',
                ha='center', va='bottom', zorder=6,
                bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.8))

def layer_bg(ax, x, y, w, h, label, fc='#F0F4FC', ec='#8AAAD0'):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0",
                          linewidth=1, edgecolor=ec, facecolor=fc,
                          linestyle='--', zorder=1)
    ax.add_patch(rect)
    ax.text(x + 0.01, y + h - 0.015, label, fontsize=7, color='#4A6A90',
            fontweight='bold', va='top', zorder=2)

# ─────────────────────────────────────────────
# FIG 3.1 — SYSTEM ARCHITECTURE
# ─────────────────────────────────────────────
def fig_architecture():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_xlim(0, 1.4)
    ax.set_ylim(0, 0.9)
    ax.axis('off')
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Layer backgrounds
    layer_bg(ax, 0.01, 0.73, 1.38, 0.15, 'CLIENT LAYER', '#EEF4FF', '#6690CC')
    layer_bg(ax, 0.01, 0.44, 1.38, 0.27, 'APPLICATION LAYER', '#F0FFF4', '#4A9A6A')
    layer_bg(ax, 0.01, 0.22, 1.38, 0.20, 'SERVICE / PROCESSING LAYER', '#FFF8F0', '#C07A2A')
    layer_bg(ax, 0.01, 0.01, 1.38, 0.19, 'DATA LAYER', '#FFF0F0', '#C04A4A')

    # CLIENT LAYER
    box(ax, 0.04, 0.76, 0.22, 0.09, 'Web Browser', 'Admin / Teacher / Student / Gate',
        fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=8)
    box(ax, 0.32, 0.76, 0.22, 0.09, 'Flutter Mobile App', 'Android — REST + WebSocket',
        fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=8)
    box(ax, 0.60, 0.76, 0.22, 0.09, 'Gate Camera', 'RTSP / USB — Face Capture',
        fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=8)
    box(ax, 0.88, 0.76, 0.22, 0.09, 'PWA / Offline', 'Service Worker Cache',
        fc='#DDEAFF', ec='#3366BB', bold=True, fontsize=8)

    # APPLICATION LAYER
    box(ax, 0.04, 0.58, 0.28, 0.09, 'Nginx Reverse Proxy', ':80/:443 → :9000',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)
    box(ax, 0.38, 0.58, 0.30, 0.09, 'Daphne ASGI Server', ':9000 — HTTP + WebSocket',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)
    box(ax, 0.74, 0.58, 0.28, 0.09, 'Django Channels', 'WebSocket Consumers',
        fc='#E0F0E0', ec='#2A7A4A', bold=True)

    box(ax, 0.04, 0.46, 0.20, 0.09, 'Django MVT', 'Views / Templates',
        fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 0.28, 0.46, 0.20, 0.09, 'REST API', '/api/v1/ — Token Auth',
        fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 0.52, 0.46, 0.20, 0.09, 'Auth & RBAC', '5 Roles — Session/JWT',
        fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 0.76, 0.46, 0.20, 0.09, 'Edge Cache', 'SQLite — Offline API',
        fc='#CCE8CC', ec='#1A6A3A')
    box(ax, 1.00, 0.46, 0.20, 0.09, 'Async Tasks', 'AsyncTask Model',
        fc='#CCE8CC', ec='#1A6A3A')

    # SERVICE LAYER
    box(ax, 0.04, 0.25, 0.28, 0.12, 'InsightFace + ONNX', 'buffalo_s — 512-dim\nCosine Similarity ≥ 0.65',
        fc='#FFE8CC', ec='#B05010', bold=True, fontsize=8)
    box(ax, 0.38, 0.25, 0.22, 0.12, 'face_engine.py', 'Dlib fallback\n128-dim Euclidean',
        fc='#FFE8CC', ec='#B05010')
    box(ax, 0.65, 0.25, 0.22, 0.12, 'Email / SMTP', 'Ineligible alerts\nExam reminders',
        fc='#FFE8CC', ec='#B05010')
    box(ax, 0.92, 0.25, 0.24, 0.12, 'WeasyPrint / PDF', 'Reports export\nGrade sheets',
        fc='#FFE8CC', ec='#B05010')

    # DATA LAYER
    box(ax, 0.04, 0.04, 0.28, 0.14, 'PostgreSQL', '25 tables\nHNSW Index (pgvector)\npg_trgm Fuzzy Search',
        fc='#FFD8D8', ec='#AA2222', bold=True, fontsize=8)
    box(ax, 0.38, 0.04, 0.22, 0.14, 'Redis Cache', 'Session state\nAttendance pub/sub\nChannel layers',
        fc='#FFD8D8', ec='#AA2222', bold=True)
    box(ax, 0.65, 0.04, 0.22, 0.14, 'SQLite Fallback', 'db_local.sqlite3\nOffline dev/edge',
        fc='#FFD8D8', ec='#AA2222')
    box(ax, 0.92, 0.04, 0.24, 0.14, 'Static / Media', 'Nginx served\nFace images\nPDF exports',
        fc='#FFD8D8', ec='#AA2222')

    # Arrows — client to app
    for xc, xe in [(0.15, 0.20), (0.43, 0.43), (0.71, 0.65), (0.99, 0.99)]:
        arr(ax, xc, 0.76, xe, 0.67, color='#336699')

    # Nginx → Daphne
    arr(ax, 0.32, 0.625, 0.38, 0.625, 'proxy', color='#2A7A4A')
    # Daphne → Channels
    arr(ax, 0.68, 0.625, 0.74, 0.625, 'WS', color='#2A7A4A')
    # Daphne → MVT/API
    arr(ax, 0.53, 0.58, 0.14, 0.55, color='#2A7A4A')
    arr(ax, 0.53, 0.58, 0.38, 0.55, color='#2A7A4A')

    # App → Service
    arr(ax, 0.14, 0.46, 0.18, 0.37, color='#C07A2A')
    arr(ax, 0.38, 0.46, 0.49, 0.37, color='#C07A2A')

    # Service → Data
    arr(ax, 0.18, 0.25, 0.18, 0.18, color='#C04A4A')
    arr(ax, 0.49, 0.25, 0.49, 0.18, color='#C04A4A')
    arr(ax, 0.14, 0.46, 0.14, 0.18, 'DB queries', color='#C04A4A', lw=0.8)

    # Title & caption
    fig.text(0.5, 0.97, 'Figure 3.1: SHAMEL System Architecture — Updated with Flutter Mobile, ASGI/WebSocket, Redis & InsightFace',
             ha='center', va='top', fontsize=10, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.005, 'Dashed borders indicate architectural layers. Solid arrows denote data/request flow.',
             ha='center', va='bottom', fontsize=7.5, color='#5A7090', style='italic')

    plt.tight_layout(rect=[0, 0.01, 1, 0.96])
    path = os.path.join(OUT, 'fig3_1_architecture.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] fig3_1_architecture.png")

# ─────────────────────────────────────────────
# FIG 3.2 — DATABASE ERD (simplified key entities)
# ─────────────────────────────────────────────
def fig_erd():
    fig, ax = plt.subplots(figsize=(16, 11))
    ax.set_xlim(0, 1.6)
    ax.set_ylim(0, 1.1)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    def entity(x, y, w, h, name, fields, note=None, highlight=False):
        hdr_c = '#1A3A6A' if highlight else '#2C4A7C'
        bdy_c = '#EEF3FF' if not highlight else '#E8F0FF'
        # header
        hdr = FancyBboxPatch((x, y + h - 0.055), w, 0.055,
                             boxstyle="round,pad=0", linewidth=1.5,
                             edgecolor=hdr_c, facecolor=hdr_c, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 0.0275, name, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', zorder=4)
        # body
        bdy = FancyBboxPatch((x, y), w, h - 0.055,
                             boxstyle="round,pad=0", linewidth=1.5,
                             edgecolor=hdr_c, facecolor=bdy_c, zorder=3)
        ax.add_patch(bdy)
        for i, (pk, fname, ftype) in enumerate(fields):
            yf = y + h - 0.055 - 0.03 - i * 0.025
            prefix = '🔑 ' if pk == 'PK' else ('🔗 ' if pk == 'FK' else '   ')
            ax.text(x + 0.008, yf, f"{prefix}{fname}", fontsize=6, color='#1A2A4A',
                    va='center', zorder=4)
            ax.text(x + w - 0.008, yf, ftype, fontsize=5.5, color='#4A6080',
                    va='center', ha='right', zorder=4, style='italic')
        if note:
            ax.text(x + w/2, y + 0.008, note, fontsize=5.5, color='#AA4400',
                    ha='center', va='bottom', zorder=4, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.15', fc='#FFF0E0', ec='#CC6600', lw=0.8))

    def rel(ax, x1, y1, x2, y2, label='', style='1:N'):
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle='->', color='#445577', lw=1.1),
                    zorder=5)
        mx, my = (x1+x2)/2, (y1+y2)/2
        if label:
            ax.text(mx, my + 0.01, label, fontsize=5.5, color='#334466',
                    ha='center', zorder=6,
                    bbox=dict(boxstyle='round,pad=0.1', fc='white', ec='none', alpha=0.85))
        ax.text(mx + 0.02, my - 0.01, style, fontsize=5.5, color='#667799',
                ha='center', zorder=6)

    # Entities
    entity(0.02, 0.78, 0.20, 0.20, 'College',
           [('PK','id','INT'),('','name','VARCHAR'),('','code','VARCHAR'),('','coordinator_id','FK')])

    entity(0.26, 0.78, 0.22, 0.20, 'Department',
           [('PK','id','INT'),('FK','college_id','→College'),('','name','VARCHAR'),('','code','VARCHAR')])

    entity(0.52, 0.78, 0.22, 0.20, 'Course',
           [('PK','id','INT'),('FK','department_id','→Dept'),('','name','VARCHAR'),('','code','VARCHAR'),
            ('','credit_hours','INT')])

    entity(0.78, 0.78, 0.24, 0.22, 'Student',
           [('PK','id','INT'),('FK','department_id','→Dept'),('','student_id','VARCHAR'),
            ('','name_ar','VARCHAR'),('','is_allowed_entry','BOOL')])

    entity(1.06, 0.78, 0.24, 0.22, 'Teacher',
           [('PK','id','INT'),('FK','department_id','→Dept'),('','employee_id','VARCHAR'),
            ('','name_ar','VARCHAR'),('','specialization','VARCHAR')])

    entity(0.02, 0.46, 0.24, 0.28, 'StudentFaceEmbedding',
           [('PK','id','INT'),('FK','student_id','→Student'),
            ('','embedding','VECTOR(512)'),('','engine','VARCHAR'),
            ('','enrolled_at','DATETIME'),('','is_active','BOOL')],
           note='⚡ HNSW Index on embedding\n(pgvector cosine distance)',
           highlight=True)

    entity(0.30, 0.46, 0.24, 0.24, 'Schedule',
           [('PK','id','INT'),('FK','course_id','→Course'),
            ('FK','teacher_id','→Teacher'),('FK','classroom_id','→Room'),
            ('','day_of_week','INT'),('','start_time','TIME')])

    entity(0.58, 0.46, 0.24, 0.24, 'LectureSession',
           [('PK','id','INT'),('FK','schedule_id','→Schedule'),
            ('','date','DATE'),('','status','VARCHAR'),
            ('','started_at','DATETIME'),('','ended_at','DATETIME')])

    entity(0.86, 0.46, 0.24, 0.24, 'AIAttendanceLog',
           [('PK','id','INT'),('FK','session_id','→Session'),
            ('FK','student_id','→Student'),('','confidence','FLOAT'),
            ('','method','VARCHAR'),('','marked_at','DATETIME')])

    entity(1.14, 0.46, 0.20, 0.22, 'GateLog',
           [('PK','id','INT'),('FK','student_id','→Student'),
            ('','entry_time','DATETIME'),('','match_score','FLOAT'),
            ('','direction','VARCHAR')])

    entity(0.02, 0.16, 0.24, 0.24, 'MedicalExcuse',
           [('PK','id','INT'),('FK','student_id','→Student'),
            ('','date_from','DATE'),('','date_to','DATE'),
            ('','status','VARCHAR'),('','document','FILE')])

    entity(0.30, 0.16, 0.24, 0.22, 'Exam / ExamSeat',
           [('PK','id','INT'),('FK','course_id','→Course'),
            ('FK','student_id','→Student'),('','hall','VARCHAR'),
            ('','seat_no','INT'),('','exam_date','DATETIME')])

    entity(0.58, 0.16, 0.24, 0.22, 'Grade',
           [('PK','id','INT'),('FK','session_id','→Session'),
            ('FK','student_id','→Student'),('','midterm','FLOAT'),
            ('','final','FLOAT'),('','total','FLOAT')])

    entity(0.86, 0.16, 0.24, 0.20, 'Notification',
           [('PK','id','INT'),('FK','user_id','→User'),
            ('','title','VARCHAR'),('','body','TEXT'),
            ('','is_read','BOOL'),('','created_at','DATETIME')])

    entity(1.14, 0.16, 0.20, 0.20, 'AuditLog',
           [('PK','id','INT'),('FK','user_id','→User'),
            ('','action','VARCHAR'),('','table_name','VARCHAR'),
            ('','record_id','INT')])

    # Index note box
    ax.text(0.02, 0.08, '⚡ Performance Indexes:', fontsize=7, fontweight='bold',
            color='#663300', va='top')
    ax.text(0.02, 0.065,
            '• HNSW Index (pgvector) on StudentFaceEmbedding.embedding — O(log N) ANN search\n'
            '• pg_trgm GIN Index on Student.name_ar, Course.name, Student.student_id — Fuzzy search\n'
            '• B-tree Indexes on all FK columns and date fields — Standard query optimization',
            fontsize=6.5, color='#443300', va='top',
            bbox=dict(boxstyle='round,pad=0.3', fc='#FFF8EE', ec='#CC8800', lw=0.8))

    # Relations
    rel(ax, 0.22, 0.92, 0.26, 0.92, 'has', '1:N')
    rel(ax, 0.48, 0.92, 0.52, 0.92, 'offers', '1:N')
    rel(ax, 0.74, 0.92, 0.78, 0.92, 'enrolls', '1:N')
    rel(ax, 1.02, 0.92, 1.06, 0.92, 'teaches', '1:N')
    rel(ax, 0.86, 0.83, 0.26, 0.83, 'face embed', '1:1')
    rel(ax, 0.54, 0.58, 0.58, 0.58, 'generates', '1:N')
    rel(ax, 0.82, 0.58, 0.86, 0.58, 'records', '1:N')
    rel(ax, 1.10, 0.58, 1.14, 0.58, 'gate log', '1:N')

    fig.text(0.5, 0.99, 'Figure 3.2: SHAMEL Database ERD — Updated with HNSW pgvector Index & pg_trgm Trigram Indexes',
             ha='center', va='top', fontsize=10, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.005, 'PK = Primary Key  |  FK = Foreign Key  |  🔑 = PK  |  🔗 = FK  |  ⚡ = Performance Index',
             ha='center', va='bottom', fontsize=7.5, color='#5A7090', style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 0.98])
    path = os.path.join(OUT, 'fig3_2_erd.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] fig3_2_erd.png")

# ─────────────────────────────────────────────
# FIG 3.3 — USE CASE DIAGRAM
# ─────────────────────────────────────────────
def fig_usecase():
    fig, ax = plt.subplots(figsize=(16, 12))
    ax.set_xlim(0, 1.6)
    ax.set_ylim(0, 1.2)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    def actor(x, y, label, color='#2C4A7C'):
        # stick figure
        ax.plot(x, y + 0.06, 'o', ms=10, color=color, zorder=5)
        ax.plot([x, x], [y + 0.02, y - 0.04], color=color, lw=1.5, zorder=5)
        ax.plot([x - 0.03, x + 0.03], [y, y], color=color, lw=1.5, zorder=5)
        ax.plot([x, x - 0.025], [y - 0.04, y - 0.085], color=color, lw=1.5, zorder=5)
        ax.plot([x, x + 0.025], [y - 0.04, y - 0.085], color=color, lw=1.5, zorder=5)
        ax.text(x, y - 0.11, label, ha='center', va='top', fontsize=7,
                fontweight='bold', color=color, zorder=5,
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec='none', alpha=0.8))

    def usecase(x, y, w, h, label, sublabel=None, mobile=False):
        ec = '#1A6A9A' if mobile else '#2C4A7C'
        fc = '#D8F0FF' if mobile else '#EEF3FF'
        ell = mpatches.Ellipse((x, y), w, h, linewidth=1.2,
                                edgecolor=ec, facecolor=fc, zorder=3)
        ax.add_patch(ell)
        dy = 0.008 if sublabel else 0
        ax.text(x, y + dy, label, ha='center', va='center',
                fontsize=6.5, color='#0B1E38', zorder=4,
                fontweight='bold' if mobile else 'normal')
        if sublabel:
            ax.text(x, y - 0.018, sublabel, ha='center', va='center',
                    fontsize=5.5, color='#3A6A8A', zorder=4, style='italic')

    def uc_line(ax, ax_x, ay, ux, uy, dashed=False):
        ls = '--' if dashed else '-'
        ax.plot([ax_x, ux], [ay, uy], color='#8899AA', lw=0.8, ls=ls, zorder=2)

    # System boundary
    rect = FancyBboxPatch((0.25, 0.05), 1.10, 1.08,
                          boxstyle="round,pad=0", linewidth=2,
                          edgecolor='#2C4A7C', facecolor='#F8FAFF', zorder=1)
    ax.add_patch(rect)
    ax.text(0.80, 1.10, 'SHAMEL System', ha='center', va='center',
            fontsize=11, fontweight='bold', color='#0B1E38')

    # Mobile sub-boundary
    rect_m = FancyBboxPatch((0.27, 0.07), 0.52, 0.48,
                            boxstyle="round,pad=0", linewidth=1.2,
                            edgecolor='#1A6A9A', facecolor='#EEF8FF',
                            linestyle='--', zorder=2)
    ax.add_patch(rect_m)
    ax.text(0.53, 0.53, 'Mobile App (Flutter)', ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#1A6A9A')

    # Web sub-boundary
    rect_w = FancyBboxPatch((0.82, 0.07), 0.51, 0.98,
                            boxstyle="round,pad=0", linewidth=1.2,
                            edgecolor='#4A7A4A', facecolor='#F0FFF0',
                            linestyle='--', zorder=2)
    ax.add_patch(rect_w)
    ax.text(1.075, 1.02, 'Web Interface', ha='center', va='center',
            fontsize=7.5, fontweight='bold', color='#2A6A2A')

    # ACTORS — left
    actor(0.10, 1.00, 'Student', '#1A5A9A')
    actor(0.10, 0.70, 'Teacher', '#2A6A2A')
    actor(0.10, 0.40, 'Gate\nOperator', '#8A4A2A')
    actor(0.10, 0.10, 'Coordinator', '#5A2A8A')

    # ACTORS — right
    actor(1.50, 0.85, 'Admin', '#AA2222')
    actor(1.50, 0.45, 'SMTP\nServer', '#666666')
    actor(1.50, 0.15, 'Face\nEngine', '#AA6600')

    # ── MOBILE USE CASES
    usecase(0.42, 0.43, 0.26, 0.07, 'View Attendance History', '(Mobile)', mobile=True)
    usecase(0.53, 0.33, 0.26, 0.07, 'Receive Push Notifications', '(Mobile)', mobile=True)
    usecase(0.42, 0.23, 0.26, 0.07, 'View Schedule', '(Mobile)', mobile=True)
    usecase(0.53, 0.13, 0.26, 0.07, 'Submit Medical Excuse', '(Mobile)', mobile=True)
    usecase(0.42, 0.43 - 0.24, 0.26, 0.07, 'View Course Sessions', '(Mobile — Teacher)', mobile=True)

    # ── WEB USE CASES — right panel
    usecase(1.08, 0.97, 0.30, 0.07, 'Manage Users / Roles')
    usecase(1.08, 0.87, 0.30, 0.07, 'View Audit Logs')
    usecase(1.08, 0.77, 0.30, 0.07, 'System Configuration')
    usecase(1.08, 0.67, 0.30, 0.07, 'Mark Attendance')
    usecase(1.08, 0.57, 0.30, 0.07, 'Export Reports (PDF/Excel)')
    usecase(1.08, 0.47, 0.30, 0.07, 'Manage Excuses')
    usecase(1.08, 0.37, 0.30, 0.07, 'Face Scan at Gate', 'InsightFace ONNX')
    usecase(1.08, 0.27, 0.30, 0.07, 'Generate Grade Sheets')
    usecase(1.08, 0.17, 0.30, 0.07, 'Send Alert Notifications', 'SMTP')

    # Lines — Student (left actor at 0.10)
    for uy in [1.00, 0.43, 0.33, 0.23, 0.13]:
        uc_line(ax, 0.10, 1.00, 0.29, uy)
    for uy in [0.67, 0.47, 0.57]:
        uc_line(ax, 0.10, 1.00, 0.93, uy)

    # Teacher
    for uy in [0.43 - 0.24, 0.33]:
        uc_line(ax, 0.10, 0.70, 0.40, uy)
    for uy in [0.67, 0.57, 0.27]:
        uc_line(ax, 0.10, 0.70, 0.93, uy)

    # Gate
    uc_line(ax, 0.10, 0.40, 0.93, 0.37)

    # Coordinator
    for uy in [0.47, 0.27, 0.17]:
        uc_line(ax, 0.10, 0.10, 0.93, uy)

    # Admin (right)
    for uy in [0.97, 0.87, 0.77]:
        uc_line(ax, 1.50, 0.85, 1.23, uy)

    # SMTP
    uc_line(ax, 1.50, 0.45, 1.23, 0.17, dashed=True)

    # FaceEngine
    uc_line(ax, 1.50, 0.15, 1.23, 0.37, dashed=True)

    # Legend
    ax.add_patch(mpatches.Ellipse((0.27, 0.010), 0.06, 0.025, linewidth=1,
                                   edgecolor='#1A6A9A', facecolor='#D8F0FF'))
    ax.text(0.31, 0.010, '= Mobile App Feature', fontsize=6.5, va='center', color='#1A6A9A')
    ax.add_patch(mpatches.Ellipse((0.55, 0.010), 0.06, 0.025, linewidth=1,
                                   edgecolor='#2C4A7C', facecolor='#EEF3FF'))
    ax.text(0.59, 0.010, '= Web Feature', fontsize=6.5, va='center', color='#2C4A7C')

    fig.text(0.5, 0.995, 'Figure 3.3: SHAMEL Use Case Diagram — Updated with Mobile App Features (Flutter)',
             ha='center', va='top', fontsize=10, fontweight='bold', color='#0B1E38')

    plt.tight_layout(rect=[0, 0.01, 1, 0.99])
    path = os.path.join(OUT, 'fig3_3_usecase.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] fig3_3_usecase.png")

# ─────────────────────────────────────────────
# FIG 3.4 — SEQUENCE: GATE ENTRY
# ─────────────────────────────────────────────
def fig_sequence():
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.set_xlim(0, 1.6)
    ax.set_ylim(0, 1.0)
    ax.axis('off')
    fig.patch.set_facecolor('white')

    # Participants
    parts = [
        ('Camera / Gate\nHardware', 0.08, '#2C4A7C'),
        ('face_engine.py\n(InsightFace+ONNX)', 0.30, '#B05010'),
        ('Django\nViews/API', 0.52, '#2A6A2A'),
        ('PostgreSQL\n(HNSW Index)', 0.74, '#AA2222'),
        ('Redis\nChannel Layer', 0.96, '#AA6600'),
        ('Gate Operator\nUI / Flutter App', 1.18, '#1A5A9A'),
    ]

    TOP = 0.94
    BOTTOM = 0.04

    # Lifelines
    for label, x, color in parts:
        # head box
        head = FancyBboxPatch((x - 0.075, TOP), 0.15, 0.055,
                              boxstyle="round,pad=0", linewidth=1.5,
                              edgecolor=color, facecolor=color, zorder=3)
        ax.add_patch(head)
        ax.text(x, TOP + 0.0275, label, ha='center', va='center',
                fontsize=6.5, fontweight='bold', color='white', zorder=4,
                multialignment='center')
        # dashed lifeline
        ax.plot([x, x], [TOP, BOTTOM], color=color, lw=1, ls='--', alpha=0.5, zorder=1)

    def msg(y, x1, x2, label, color='#334466', activation=False, ret=False, note=None):
        ls = '--' if ret else '->'
        style = '<-' if ret else '->'
        ax.annotate('', xy=(x2, y), xytext=(x1, y),
                    arrowprops=dict(arrowstyle=style, color=color, lw=1.2,
                                   linestyle='dashed' if ret else 'solid'),
                    zorder=5)
        direction = 1 if x2 > x1 else -1
        lx = (x1 + x2) / 2
        ax.text(lx, y + 0.008, label, ha='center', va='bottom',
                fontsize=6.5, color=color, zorder=6,
                bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9))
        if note:
            ax.text(lx, y - 0.015, note, ha='center', va='top',
                    fontsize=5.5, color='#AA4400', style='italic', zorder=6)

    def activation_box(x, y_top, y_bot, color='#CCDDFF', ec='#445577'):
        w = 0.018
        rect = FancyBboxPatch((x - w/2, y_bot), w, y_top - y_bot,
                              boxstyle="round,pad=0", linewidth=1,
                              edgecolor=ec, facecolor=color, zorder=2)
        ax.add_patch(rect)

    def step_label(y, text, x=0.005):
        ax.text(x, y, text, fontsize=6, color='#667788', va='center', style='italic')

    # Activation boxes
    activation_box(0.30, 0.86, 0.60, '#FFE8CC', '#B05010')
    activation_box(0.52, 0.80, 0.50, '#E0F0E0', '#2A6A2A')
    activation_box(0.74, 0.68, 0.56, '#FFD8D8', '#AA2222')
    activation_box(0.96, 0.44, 0.30, '#FFE8CC', '#AA6600')
    activation_box(1.18, 0.26, 0.18, '#D8E8FF', '#1A5A9A')

    # Messages
    msg(0.88, 0.08, 0.30, '1. Frame: JPEG/RTSP — 640×480', '#2C4A7C')
    step_label(0.88, 'Step 1')

    msg(0.82, 0.30, 0.30, '2. Detect face bounding box', '#B05010')
    ax.text(0.30, 0.80, '  RetinaFace detector', fontsize=5.5, color='#885520', style='italic')

    msg(0.76, 0.30, 0.30, '3. Crop + align face ROI', '#B05010')

    msg(0.70, 0.30, 0.30, '4. InsightFace ONNX inference\n   → 512-dim embedding vector', '#B05010')
    ax.text(0.30, 0.68, '  buffalo_s model, CPU', fontsize=5.5, color='#885520', style='italic')
    step_label(0.76, 'Step 2')

    msg(0.64, 0.30, 0.52, '5. POST /api/v1/scan/ { embedding }', '#2A6A2A')
    step_label(0.64, 'Step 3')

    msg(0.58, 0.52, 0.74,
        '6. SELECT student WHERE\n   embedding <=> $1 < 0.65',
        '#AA2222',
        note='HNSW cosine ANN search — O(log N)')
    step_label(0.58, 'Step 4')

    msg(0.52, 0.74, 0.74, '7. Top-1 match + confidence score', '#AA2222')

    msg(0.46, 0.74, 0.52, '8. Student record + match_score', '#2A6A2A', ret=True)
    step_label(0.46, 'Step 5')

    msg(0.40, 0.52, 0.52, '9. Create GateLog entry\n   + mark attendance', '#2A6A2A',
        note='INSERT attendance_gatelog')

    msg(0.34, 0.52, 0.96,
        '10. Publish to Redis channel\n    gate.attendance.{student_id}',
        '#AA6600')
    step_label(0.34, 'Step 6')

    msg(0.28, 0.96, 1.18,
        '11. WebSocket broadcast\n    { student, match_score, timestamp }',
        '#1A5A9A',
        note='Async via Django Channels consumer')
    step_label(0.28, 'Step 7')

    msg(0.22, 0.08, 0.08, '12. LED / Door relay trigger\n    (green = allow, red = deny)', '#2C4A7C', ret=True)
    step_label(0.22, 'Step 8')

    msg(0.16, 1.18, 1.18, '13. UI update: photo + name\n    attendance confirmed toast', '#1A5A9A')
    step_label(0.16, 'Step 9')

    # Boundary box around HNSW note
    note_box = FancyBboxPatch((0.62, 0.545), 0.24, 0.042,
                              boxstyle="round,pad=0.005", linewidth=0.8,
                              edgecolor='#AA4400', facecolor='#FFF4EE',
                              linestyle='--', zorder=7)
    ax.add_patch(note_box)

    fig.text(0.5, 0.98, 'Figure 3.4: Gate Entry Sequence — InsightFace ONNX + HNSW pgvector + WebSocket Async Broadcast',
             ha='center', va='top', fontsize=10, fontweight='bold', color='#0B1E38')
    fig.text(0.5, 0.005,
             'Dashed lifeline = idle participant  |  Activated box = executing  |  -- arrow = return message',
             ha='center', va='bottom', fontsize=7.5, color='#5A7090', style='italic')

    plt.tight_layout(rect=[0, 0.01, 1, 0.97])
    path = os.path.join(OUT, 'fig3_4_sequence.png')
    plt.savefig(path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  [OK] fig3_4_sequence.png")

# ─────────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────────
if __name__ == '__main__':
    print("Generating SHAMEL thesis diagrams...")
    fig_architecture()
    fig_erd()
    fig_usecase()
    fig_sequence()
    print(f"\nAll diagrams saved → {OUT}")
