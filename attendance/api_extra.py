# -*- coding: utf-8 -*-
"""
SHAMEL native-app REST API — extended section coverage.

List / detail / action endpoints mirroring every web urlpattern so the
native app contains the full system. Reuses the auth helpers from api.py.
"""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q

from .api import (
    api_auth, api_staff, _is_staff, _role_of, _bearer,
    _user_from_token,
)
from .models import (
    Student, Teacher, Coordinator, Schedule, LectureSession,
    AIAttendanceLog, Notification, Course, Classroom,
    Department, College, SupportTicket,
)


def _page(qs, request, size=50):
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0
    total = qs.count()
    return list(qs[offset:offset + size]), total, offset


# ── Courses ────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def courses(request):
    user = request.api_user  # set by @api_auth decorator
    qs = Course.objects.select_related('college', 'department').all()

    # Determine caller's college for scoped filtering
    role = _role_of(user)
    caller_college_id = None
    if role == 'student':
        try:
            st = Student.objects.select_related('department__college').get(auth_user=user)
            caller_college_id = st.department.college_id if st.department else None
        except Exception:
            pass
    elif role == 'coordinator':
        try:
            caller_college_id = Coordinator.objects.get(auth_user=user).college_id
        except Exception:
            pass

    # ?scope=mine → caller's college only (default for student)
    # ?scope=all  → unrestricted (admin/coordinator/teacher default)
    scope = request.GET.get('scope', 'mine' if role == 'student' else 'all')
    if scope == 'mine' and caller_college_id:
        qs = qs.filter(college_id=caller_college_id)

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(title__icontains=q) | Q(course_code__icontains=q))
    rows, total, offset = _page(qs.order_by('title'), request)
    data = [{
        'id': c.id, 'code': c.course_code, 'title': c.title,
        'credits': c.credits, 'hours': c.total_hours, 'year': c.year_level,
        'college': getattr(c.college, 'college_name', None),
        'department': getattr(c.department, 'name', None),
    } for c in rows]
    return JsonResponse({
        'ok': True, 'total': total, 'count': len(data), 'courses': data,
        'scope': scope, 'college_id': caller_college_id,
    })


@api_staff
@csrf_exempt
@require_http_methods(['POST'])
def course_create(request):
    try:
        p = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        p = request.POST
    if not p.get('course_code') or not p.get('title'):
        return JsonResponse({'ok': False, 'message': 'الكود والعنوان مطلوبان'}, status=400)
    c = Course.objects.create(
        course_code=p['course_code'], title=p['title'],
        credits=p.get('credits') or 3, total_hours=p.get('total_hours') or 45,
        year_level=p.get('year_level') or None,
        college_id=p.get('college') or None, department_id=p.get('department') or None,
    )
    return JsonResponse({'ok': True, 'id': c.id})


# ── Classrooms ─────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def classrooms(request):
    qs = Classroom.objects.select_related('college').order_by('name')
    rows, total, offset = _page(qs, request)
    data = [{
        'id': r.id, 'name': r.name, 'location': r.location,
        'capacity': r.capacity, 'type': r.classroom_type, 'is_busy': r.is_busy,
        'college': getattr(r.college, 'college_name', None),
    } for r in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'classrooms': data})


@api_auth
@require_http_methods(['GET'])
def classrooms_status(request):
    from django.db import close_old_connections
    close_old_connections()
    rows = Classroom.objects.order_by('name')
    data = [{'id': r.id, 'name': r.name, 'is_busy': r.is_busy,
             'location': r.location, 'capacity': r.capacity} for r in rows]
    busy = sum(1 for r in data if r['is_busy'])
    return JsonResponse({'ok': True, 'count': len(data), 'busy': busy,
                         'free': len(data) - busy, 'classrooms': data})


@api_staff
@csrf_exempt
@require_http_methods(['POST'])
def classroom_create(request):
    try:
        p = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        p = request.POST
    if not p.get('name'):
        return JsonResponse({'ok': False, 'message': 'الاسم مطلوب'}, status=400)
    r = Classroom.objects.create(
        name=p['name'], capacity=p.get('capacity') or 30,
        location=p.get('location') or '', classroom_type=p.get('type') or 'lecture',
    )
    return JsonResponse({'ok': True, 'id': r.id})


# ── Departments ────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def departments(request):
    rows = Department.objects.select_related('college').order_by('name')
    data = [{'id': d.id, 'name': d.name, 'college': getattr(d.college, 'college_name', None)} for d in rows]
    return JsonResponse({'ok': True, 'count': len(data), 'departments': data})


# ── Teachers ───────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def teachers(request):
    role = _role_of(request.api_user)
    if role not in ('admin', 'coordinator', 'teacher'):
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    qs = Teacher.objects.select_related('department', 'college').order_by('name')
    if role == 'coordinator':
        co = Coordinator.objects.filter(auth_user=request.api_user).first()
        if co:
            qs = qs.filter(college=co.college)
    elif role == 'teacher':
        # teachers can only view their own record
        qs = qs.filter(auth_user=request.api_user)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(name__icontains=q)
    rows, total, offset = _page(qs, request)
    data = [{
        'id': t.teacher_id, 'name': t.name, 'degree': t.academic_degree,
        'major': t.major, 'email': t.university_email, 'phone': t.phone_number,
        'department': getattr(t.department, 'name', None),
        'college': getattr(t.college, 'college_name', None),
        'allowed_entry': t.is_allowed_entry,
    } for t in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'teachers': data})


@api_auth
@require_http_methods(['GET'])
def teacher_detail(request, tid):
    t = Teacher.objects.select_related('department', 'college').filter(teacher_id=tid).first()
    if not t:
        return JsonResponse({'ok': False, 'message': 'غير موجود'}, status=404)
    return JsonResponse({'ok': True, 'teacher': {
        'id': t.teacher_id, 'name': t.name, 'degree': t.academic_degree,
        'major': t.major, 'email': t.university_email, 'phone': t.phone_number,
        'department': getattr(t.department, 'name', None),
        'college': getattr(t.college, 'college_name', None),
        'allowed_entry': t.is_allowed_entry,
        'sessions': LectureSession.objects.filter(schedule__teacher=t).count(),
        'courses': Schedule.objects.filter(teacher=t).values('course').distinct().count(),
    }})


# ── Students ───────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def students(request):
    role = _role_of(request.api_user)
    qs = Student.objects.select_related('department').order_by('name')
    if role == 'student':
        # students see only themselves
        qs = qs.filter(auth_user=request.api_user)
    elif role == 'coordinator':
        co = Coordinator.objects.filter(auth_user=request.api_user).first()
        if co:
            qs = qs.filter(department__college=co.college)
    elif role == 'gate':
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    # admin + teacher: full list (teachers need to look up students in their courses)
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(student_code__icontains=q))
    rows, total, offset = _page(qs, request)
    data = [{
        'id': s.id, 'name': s.name, 'code': s.student_code,
        'department': getattr(s.department, 'name', None),
        'batch': getattr(s, 'batch', None), 'email': s.university_email,
    } for s in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'students': data})


@api_auth
@require_http_methods(['GET'])
def student_detail(request, sid):
    s = Student.objects.select_related('department').filter(id=sid).first()
    if not s:
        return JsonResponse({'ok': False, 'message': 'غير موجود'}, status=404)
    total = AIAttendanceLog.objects.filter(student=s).count()
    present = AIAttendanceLog.objects.filter(student=s, status='Present').count()
    return JsonResponse({'ok': True, 'student': {
        'id': s.id, 'name': s.name, 'code': s.student_code,
        'department': getattr(s.department, 'name', None),
        'batch': getattr(s, 'batch', None), 'email': s.university_email,
        'phone': s.phone_number, 'total_records': total, 'present': present,
        'attendance_pct': round(present / total * 100, 1) if total else 0,
    }})


# ── Tickets ────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def tickets(request):
    user = request.api_user
    qs = SupportTicket.objects.all() if _is_staff(user) else SupportTicket.objects.filter(user=user)
    rows, total, offset = _page(qs.select_related('user').order_by('-id'), request)
    data = [{
        'id': t.id, 'subject': t.subject, 'body': t.body, 'status': t.status,
        'priority': t.priority, 'user': t.user.username if t.user else None,
        'reply': t.admin_reply or '',
    } for t in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'tickets': data})


@api_auth
@csrf_exempt
@require_http_methods(['POST'])
def ticket_create(request):
    try:
        p = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        p = request.POST
    subject = (p.get('subject') or '').strip()
    body = (p.get('body') or p.get('description') or '').strip()
    if not subject or not body:
        return JsonResponse({'ok': False, 'message': 'الموضوع والوصف مطلوبان'}, status=400)
    from django.db import connection as _conn
    try:
        if _conn.vendor == 'postgresql':
            with _conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO attendance_supportticket "
                    "(subject, description, body, status, priority, ticket_type, "
                    "created_at, updated_at, requester_id, user_id, admin_reply) "
                    "VALUES (%s,%s,%s,'open',%s,'general',NOW(),NOW(),%s,%s,'') RETURNING id",
                    [subject, body, body, p.get('priority', 'medium'),
                     request.api_user.id, request.api_user.id])
                tid = cur.fetchone()[0]
        else:
            tid = SupportTicket.objects.create(
                user=request.api_user, subject=subject, body=body,
                status='open', priority=p.get('priority', 'medium')).id
        return JsonResponse({'ok': True, 'id': tid})
    except Exception as e:
        return JsonResponse({'ok': False, 'message': 'خطأ: ' + str(e)[:80]}, status=500)


# ── Attendance logs ────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def attendance_logs(request):
    qs = AIAttendanceLog.objects.select_related('student', 'schedule__course').order_by('-timestamp')
    role = _role_of(request.api_user)
    if role == 'student':
        s = Student.objects.filter(auth_user=request.api_user).first()
        qs = qs.filter(student=s) if s else qs.none()
    elif role == 'teacher':
        t = Teacher.objects.filter(auth_user=request.api_user).first()
        qs = qs.filter(schedule__teacher=t) if t else qs.none()
    rows, total, offset = _page(qs, request)
    data = [{
        'id': l.id, 'student': getattr(l.student, 'name', None),
        'course': getattr(getattr(l.schedule, 'course', None), 'title', None),
        'status': l.status, 'confidence': l.confidence_score,
        'timestamp': l.timestamp.isoformat() if l.timestamp else None,
    } for l in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'logs': data})


# ── Gate logs ──────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def gate_logs(request):
    from django.db import OperationalError, ProgrammingError
    from .models import GateLog
    if _role_of(request.api_user) not in ('admin', 'gate'):
        return JsonResponse({'ok': False, 'error': 'forbidden'}, status=403)
    try:
        rows, total, _ = _page(GateLog.objects.order_by('-timestamp'), request)
        data = [{'id': g.id, 'person': g.person_name, 'status': g.status,
                 'timestamp': g.timestamp.isoformat() if g.timestamp else None} for g in rows]
        return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'logs': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'count': 0, 'logs': [], 'unavailable': True})


# ── Audit log (staff) ──────────────────────────────────────────────────────
@api_staff
@require_http_methods(['GET'])
def audit_log(request):
    from django.db import OperationalError, ProgrammingError
    from .models import AuditLog
    try:
        rows, total, _ = _page(AuditLog.objects.select_related('user').order_by('-timestamp'), request)
        data = [{'id': a.id, 'user': a.user.username if a.user else None,
                 'action': a.action, 'target': a.target_model, 'description': a.description,
                 'timestamp': a.timestamp.isoformat() if a.timestamp else None} for a in rows]
        return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'entries': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'count': 0, 'entries': [], 'unavailable': True})


# ── Exams ──────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def exams(request):
    from django.db import OperationalError, ProgrammingError
    from .models import Exam
    try:
        rows, total, _ = _page(Exam.objects.select_related('course', 'classroom').order_by('-date'), request)
        data = [{'id': e.id, 'course': getattr(e.course, 'title', None), 'type': e.exam_type,
                 'date': str(e.date) if e.date else None, 'start': str(e.start_time),
                 'end': str(e.end_time), 'classroom': getattr(e.classroom, 'name', None),
                 'semester': e.semester} for e in rows]
        return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'exams': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'count': 0, 'exams': [], 'unavailable': True})


# ── Global search ──────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def search(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'ok': True, 'students': [], 'teachers': [], 'courses': []})
    st = [{'id': s.id, 'name': s.name, 'code': s.student_code}
          for s in Student.objects.filter(Q(name__icontains=q) | Q(student_code__icontains=q))[:10]]
    tc = [{'id': t.teacher_id, 'name': t.name}
          for t in Teacher.objects.filter(name__icontains=q)[:10]]
    cr = [{'id': c.id, 'title': c.title, 'code': c.course_code}
          for c in Course.objects.filter(Q(title__icontains=q) | Q(course_code__icontains=q))[:10]]
    return JsonResponse({'ok': True, 'students': st, 'teachers': tc, 'courses': cr})


# ── Settings ───────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def app_settings(request):
    from django.conf import settings as dj
    return JsonResponse({'ok': True, 'settings': {
        'face_engine': getattr(dj, 'FACE_ENGINE', 'dlib'),
        'version': 'SHAMEL v4.2', 'role': _role_of(request.api_user),
    }})


# ── Coordinator students ───────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def coordinator_students(request):
    co = Coordinator.objects.filter(auth_user=request.api_user).first()
    qs = Student.objects.select_related('department')
    if co and co.college_id:
        qs = qs.filter(department__college=co.college)
    rows, total, offset = _page(qs.order_by('name'), request)
    data = [{'id': s.id, 'name': s.name, 'code': s.student_code,
             'department': getattr(s.department, 'name', None)} for s in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'students': data})


# ── Toggle gate access (staff) ─────────────────────────────────────────────
@api_staff
@csrf_exempt
@require_http_methods(['POST'])
def toggle_access(request):
    try:
        p = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        p = request.POST
    t = Teacher.objects.filter(teacher_id=p.get('teacher_id')).first()
    if not t:
        return JsonResponse({'ok': False, 'message': 'الأستاذ غير موجود'}, status=404)
    t.is_allowed_entry = not t.is_allowed_entry
    t.save(update_fields=['is_allowed_entry'])
    return JsonResponse({'ok': True, 'allowed_entry': t.is_allowed_entry})


# ── Dean evaluation ────────────────────────────────────────────────────────
@api_staff
@require_http_methods(['GET'])
def dean_evaluations(request):
    from django.db import OperationalError, ProgrammingError
    from django.db.models import Avg
    from .models import CourseEvaluation
    try:
        qs = CourseEvaluation.objects.select_related('student', 'course').order_by('-submitted_at')
        avg = qs.aggregate(a=Avg('rating'))['a'] or 0
        rows, total, _ = _page(qs, request)
        data = [{'id': e.id, 'course': getattr(e.course, 'title', None),
                 'student': getattr(e.student, 'name', None),
                 'rating': e.rating, 'comment': e.comment,
                 'semester': e.semester} for e in rows]
        return JsonResponse({'ok': True, 'total': total, 'count': len(data),
                             'avg_rating': round(avg, 2), 'evaluations': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'count': 0, 'avg_rating': 0,
                             'evaluations': [], 'unavailable': True})


# ── Medical excuses ────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def excuses(request):
    from django.db import OperationalError, ProgrammingError
    from .models import MedicalExcuse
    try:
        qs = MedicalExcuse.objects.select_related('student').order_by('-submitted_at')
        role = _role_of(request.api_user)
        if role == 'student':
            s = Student.objects.filter(auth_user=request.api_user).first()
            qs = qs.filter(student=s) if s else qs.none()
        elif role == 'teacher':
            s = Student.objects.filter(auth_user=request.api_user).first()
            qs = qs.none()  # teachers don't manage excuses via API
        elif role == 'coordinator':
            co = Coordinator.objects.filter(auth_user=request.api_user).first()
            qs = qs.filter(student__department__college=co.college) if co else qs.none()
        elif role == 'gate':
            qs = qs.none()
        rows, total, _ = _page(qs, request)
        data = [{'id': e.id, 'student': getattr(e.student, 'name', None),
                 'reason': e.reason, 'status': e.status,
                 'note': e.review_note,
                 'submitted': e.submitted_at.isoformat() if e.submitted_at else None} for e in rows]
        return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'excuses': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'count': 0, 'excuses': [], 'unavailable': True})


# ── Ticket detail ──────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def ticket_detail(request, tid):
    t = SupportTicket.objects.select_related('user').filter(id=tid).first()
    if not t:
        return JsonResponse({'ok': False, 'message': 'غير موجود'}, status=404)
    # students may only see their own tickets
    if not _is_staff(request.api_user) and t.user_id != request.api_user.id:
        return JsonResponse({'ok': False, 'message': 'غير مصرح'}, status=403)
    return JsonResponse({'ok': True, 'ticket': {
        'id': t.id, 'subject': t.subject, 'body': t.body, 'status': t.status,
        'priority': t.priority, 'user': t.user.username if t.user else None,
        'reply': t.admin_reply or '',
        'created': t.created_at.isoformat() if t.created_at else None,
    }})


# ── Teacher timeline (sessions) ────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def teacher_timeline(request):
    role = _role_of(request.api_user)
    qs = LectureSession.objects.select_related('schedule__course', 'schedule__teacher').order_by('-actual_start_time')
    if role == 'teacher':
        t = Teacher.objects.filter(auth_user=request.api_user).first()
        qs = qs.filter(schedule__teacher=t) if t else qs.none()
    rows, total, _ = _page(qs, request)
    data = [{'id': s.id,
             'course': getattr(getattr(s.schedule, 'course', None), 'title', None),
             'teacher': getattr(getattr(s.schedule, 'teacher', None), 'name', None),
             'active': s.is_active,
             'start': s.actual_start_time.isoformat() if s.actual_start_time else None,
             'end': s.actual_end_time.isoformat() if getattr(s, 'actual_end_time', None) else None} for s in rows]
    return JsonResponse({'ok': True, 'total': total, 'count': len(data), 'sessions': data})


# ── Gate reports (entry log summary) ───────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def gate_reports(request):
    from django.db import OperationalError, ProgrammingError
    from .models import GateLog
    try:
        qs = GateLog.objects.order_by('-timestamp')
        total = qs.count()
        granted = qs.filter(status__icontains='grant').count()
        denied = qs.filter(status__icontains='den').count()
        rows, _, _ = _page(qs, request, size=30)
        data = [{'id': g.id, 'person': g.person_name, 'status': g.status,
                 'timestamp': g.timestamp.isoformat() if g.timestamp else None} for g in rows]
        return JsonResponse({'ok': True, 'total': total, 'granted': granted,
                             'denied': denied, 'count': len(data), 'logs': data})
    except (OperationalError, ProgrammingError):
        return JsonResponse({'ok': True, 'total': 0, 'granted': 0, 'denied': 0,
                             'count': 0, 'logs': [], 'unavailable': True})


# ── Lecture session: active session + enrolled students (Flutter teacher view) ─
@api_auth
@require_http_methods(['GET'])
def active_session(request):
    """GET /api/v1/sessions/active — teacher's current active session + enrolled students."""
    t = Teacher.objects.filter(auth_user=request.api_user).first()
    if not t:
        return JsonResponse({'ok': False, 'error': 'not_teacher'}, status=403)
    session = LectureSession.objects.filter(
        schedule__teacher=t, is_active=True
    ).select_related('schedule__course', 'schedule__classroom').first()
    if not session:
        return JsonResponse({'ok': True, 'session': None, 'enrolled': []})
    enrolled = list(
        __import__('attendance.models', fromlist=['Enrollment']).Enrollment
        .objects.filter(course=session.schedule.course)
        .select_related('student').order_by('student__name')
    )
    present_ids = set(AIAttendanceLog.objects.filter(
        session=session, status='Present').values_list('student_id', flat=True))
    return JsonResponse({'ok': True, 'session': {
        'id': session.id,
        'course': session.schedule.course.title if session.schedule and session.schedule.course else '',
        'course_code': session.schedule.course.course_code if session.schedule and session.schedule.course else '',
        'classroom': session.schedule.classroom.name if session.schedule and session.schedule.classroom else '',
        'start': session.actual_start_time.isoformat() if session.actual_start_time else None,
    }, 'enrolled': [
        {'id': e.student.id, 'name': e.student.name,
         'code': e.student.student_code or '',
         'present': e.student_id in present_ids}
        for e in enrolled
    ]})


# ── Lecture attendance: bulk sync from offline queue (Flutter) ─────────────────
@api_auth
@csrf_exempt
@require_http_methods(['POST'])
def sync_lecture_attendance(request):
    """POST /api/v1/lecture-attendance/sync
    Body: {"records": [{"session_id":1,"student_id":5,"method":"manual","timestamp":"..."}]}
    Idempotent — ignores duplicates (unique_student_per_session constraint).
    """
    t = Teacher.objects.filter(auth_user=request.api_user).first()
    if not t:
        return JsonResponse({'ok': False, 'error': 'not_teacher'}, status=403)
    try:
        body = json.loads(request.body)
    except (ValueError, TypeError):
        return JsonResponse({'ok': False, 'error': 'bad_json'}, status=400)
    records = body.get('records', [])
    if not isinstance(records, list):
        return JsonResponse({'ok': False, 'error': 'records_must_be_list'}, status=400)

    from django.utils.dateparse import parse_datetime
    from django.utils import timezone as tz
    from .models import Student, Enrollment

    saved = 0
    skipped = 0
    for rec in records:
        try:
            session_id = int(rec.get('session_id', 0))
            student_id = int(rec.get('student_id', 0))
        except (TypeError, ValueError):
            skipped += 1
            continue

        session = LectureSession.objects.filter(
            pk=session_id, schedule__teacher=t).first()
        if not session:
            skipped += 1
            continue
        student = Student.objects.filter(pk=student_id).first()
        if not student:
            skipped += 1
            continue
        if not Enrollment.objects.filter(
                student=student, course=session.schedule.course).exists():
            skipped += 1
            continue

        ts_raw = rec.get('timestamp')
        ts = parse_datetime(ts_raw) if ts_raw else None
        if ts is None:
            ts = tz.now()

        method = str(rec.get('method', 'manual'))[:50]
        status = str(rec.get('status', 'Present'))
        if status not in ('Present', 'Absent', 'Late', 'Excused'):
            status = 'Present'

        _, created = AIAttendanceLog.objects.get_or_create(
            student=student, session=session,
            defaults={
                'schedule': session.schedule,
                'status': status,
                'method': method,
                'timestamp': ts,
            },
        )
        if created:
            saved += 1
        else:
            skipped += 1

    return JsonResponse({'ok': True, 'saved': saved, 'skipped': skipped})
