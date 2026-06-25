# -*- coding: utf-8 -*-
"""
SHAMEL native-app REST API (JSON).

Stateless auth via Django signed tokens — NO new DB table, NO migration,
works identically on the VPS PostgreSQL and the local SQLite fallback.

All endpoints return JSON. Auth endpoints accept username/password and
return a signed bearer token; protected endpoints expect
    Authorization: Bearer <token>
"""
import json
import base64
import functools

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, get_user_model
from django.core import signing
from django.utils import timezone
from django.db.models import Count, Q

from .models import (
    Student, Teacher, Coordinator, Schedule, LectureSession,
    AIAttendanceLog, Notification, Course, Classroom,
    Department, College, SupportTicket,
)

User = get_user_model()


def _is_staff(user):
    return user.is_superuser or user.is_staff


def api_staff(view):
    """Require an authenticated staff/admin user."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        token = _bearer(request)
        user = _user_from_token(token) if token else None
        if not user:
            return JsonResponse({'ok': False, 'error': 'unauthorized'}, status=401)
        if not _is_staff(user):
            return JsonResponse({'ok': False, 'error': 'forbidden',
                                 'message': 'هذه الصفحة للمشرفين فقط'}, status=403)
        request.api_user = user
        return view(request, *args, **kwargs)
    return wrapper

TOKEN_SALT = 'shamel.api.token.v1'
TOKEN_MAX_AGE = 60 * 60 * 24 * 14  # 14 days


# ──────────────────────────────────────────────────────────────────────────
# Token helpers
# ──────────────────────────────────────────────────────────────────────────
def make_token(user):
    return signing.dumps({'uid': user.pk, 'u': user.username}, salt=TOKEN_SALT)


def _user_from_token(token):
    try:
        data = signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)
        return User.objects.filter(pk=data['uid']).first()
    except (signing.BadSignature, signing.SignatureExpired, KeyError, Exception):
        return None


def _bearer(request):
    hdr = request.META.get('HTTP_AUTHORIZATION', '')
    if hdr.startswith('Bearer '):
        return hdr[7:].strip()
    return None  # GET/POST token params removed — header-only for security (tokens in URLs appear in logs)


def api_auth(view):
    """Decorator: require a valid bearer token; injects request.api_user."""
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        token = _bearer(request)
        user = _user_from_token(token) if token else None
        if not user:
            return JsonResponse({'ok': False, 'error': 'unauthorized',
                                 'message': 'انتهت الجلسة — سجّل الدخول مجدداً'}, status=401)
        request.api_user = user
        return view(request, *args, **kwargs)
    return wrapper


def _role_of(user):
    if user.is_superuser or user.is_staff:
        return 'admin'  # admin takes priority — coordinator record does not demote a staff user
    if Coordinator.objects.filter(auth_user=user).exists():
        return 'coordinator'
    if Teacher.objects.filter(auth_user=user).exists():
        return 'teacher'
    if Student.objects.filter(auth_user=user).exists():
        return 'student'
    if user.groups.filter(name__in=['gate_staff', 'GATE_STAFF']).exists():
        return 'gate'
    return 'admin' if user.is_staff else 'student'


def _profile_payload(user):
    role = _role_of(user)
    base = {
        'id': user.pk, 'username': user.username,
        'name': user.get_full_name() or user.username,
        'email': user.email, 'role': role,
    }
    if role == 'student':
        s = Student.objects.filter(auth_user=user).select_related('department').first()
        if s:
            base.update({'name': s.name, 'student_code': s.student_code,
                         'department': getattr(s.department, 'name', None),
                         'batch': getattr(s, 'batch', None)})
    elif role == 'teacher':
        t = Teacher.objects.filter(auth_user=user).select_related('department', 'college').first()
        if t:
            base.update({'name': t.name, 'teacher_id': t.teacher_id,
                         'degree': t.academic_degree,
                         'department': getattr(t.department, 'name', None),
                         'college': getattr(t.college, 'college_name', None)})
    elif role == 'coordinator':
        c = Coordinator.objects.filter(auth_user=user).select_related('college').first()
        if c:
            base.update({'name': c.name,
                         'college': getattr(c.college, 'college_name', None)})
    return base


# ──────────────────────────────────────────────────────────────────────────
# Auth
# ──────────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(['POST'])
def face_login_api(request):
    """
    POST /api/v1/auth/face-login
    Body: { "image": "<base64 JPEG>" }
    Returns: { "ok": true, "token": "...", "user": {...} }

    Uses the central InsightFace DB — no local OS biometrics.
    """
    import numpy as np
    import cv2
    from .views import match_face_from_db, FACE_ENGINE_AVAILABLE, NUMPY_AVAILABLE, CV2_AVAILABLE, _fe

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'ok': False, 'message': 'طلب غير صالح'}, status=400)

    b64_data = payload.get('image') or ''
    if not b64_data:
        return JsonResponse({'ok': False, 'message': 'لم يتم إرسال صورة'}, status=400)

    # Strip data-URL prefix if present
    if ',' in b64_data:
        b64_data = b64_data.split(',', 1)[1]
    b64_data = b64_data.strip().replace(' ', '+')
    pad = 4 - len(b64_data) % 4
    if pad != 4:
        b64_data += '=' * pad

    try:
        img_bytes = base64.b64decode(b64_data)
    except Exception:
        return JsonResponse({'ok': False, 'message': 'بيانات الصورة غير صالحة'}, status=400)

    if not (FACE_ENGINE_AVAILABLE and NUMPY_AVAILABLE and CV2_AVAILABLE):
        return JsonResponse({'ok': False, 'message': 'محرك التعرف على الوجه غير متاح'}, status=503)

    try:
        img_arr = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img_arr is None:
            return JsonResponse({'ok': False, 'message': 'تعذّر فك تشفير الصورة'}, status=400)
        live_encoding = _fe.encode(img_arr[:, :, ::-1])  # BGR→RGB
    except Exception as e:
        return JsonResponse({'ok': False, 'message': 'خطأ في معالجة الصورة'}, status=500)

    if live_encoding is None:
        return JsonResponse({'ok': False, 'code': 'no_face', 'message': 'لم يُكتشف وجه — قرّب وجهك من الكاميرا'})

    matched_name, matched_type, matched_pk = match_face_from_db(live_encoding)

    if not matched_name:
        return JsonResponse({'ok': False, 'code': 'face_not_registered',
                             'message': 'الوجه غير مسجل — سجّل الدخول بكلمة المرور'})

    # Resolve auth user from match
    auth_user = None
    if matched_type == 'student':
        person = Student.objects.filter(pk=matched_pk).select_related('auth_user').first()
        if person:
            auth_user = person.auth_user
    else:
        person = Teacher.objects.filter(pk=matched_pk).select_related('auth_user').first()
        if person:
            auth_user = person.auth_user

    if not auth_user:
        return JsonResponse({'ok': False, 'message': 'الوجه معروف لكن لا يوجد حساب مرتبط — راجع الإدارة'})

    if not auth_user.is_active:
        return JsonResponse({'ok': False, 'message': 'الحساب معطّل'}, status=403)

    return JsonResponse({
        'ok': True,
        'token': make_token(auth_user),
        'user': _profile_payload(auth_user),
    })


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = request.POST
    username = (payload.get('username') or '').strip()
    password = payload.get('password') or ''
    if not username or not password:
        return JsonResponse({'ok': False, 'error': 'missing_credentials',
                             'message': 'أدخل اسم المستخدم وكلمة المرور'}, status=400)

    # Respect django-axes by passing the request
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({'ok': False, 'error': 'invalid_credentials',
                             'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'}, status=401)
    if not user.is_active:
        return JsonResponse({'ok': False, 'error': 'inactive',
                             'message': 'الحساب معطّل'}, status=403)

    return JsonResponse({
        'ok': True,
        'token': make_token(user),
        'user': _profile_payload(user),
    })


@api_auth
@require_http_methods(['GET'])
def me(request):
    return JsonResponse({'ok': True, 'user': _profile_payload(request.api_user)})


# ──────────────────────────────────────────────────────────────────────────
# Dashboard (role-aware summary)
# ──────────────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def dashboard(request):
    user = request.api_user
    role = _role_of(user)
    today = timezone.now().date()
    data = {'role': role}

    if role in ('admin', 'coordinator'):
        data.update({
            'students': Student.objects.count(),
            'teachers': Teacher.objects.count(),
            'courses': Course.objects.count(),
            'classrooms': Classroom.objects.count(),
            'active_sessions': LectureSession.objects.filter(is_active=True).count(),
            'attendance_today': AIAttendanceLog.objects.filter(timestamp__date=today).count(),
        })
    elif role == 'teacher':
        t = Teacher.objects.filter(auth_user=user).first()
        if t:
            data.update({
                'my_courses': Schedule.objects.filter(teacher=t).values('course').distinct().count(),
                'my_sessions': LectureSession.objects.filter(schedule__teacher=t).count(),
                'active_sessions': LectureSession.objects.filter(schedule__teacher=t, is_active=True).count(),
            })
    elif role == 'student':
        s = Student.objects.filter(auth_user=user).first()
        if s:
            total = AIAttendanceLog.objects.filter(student=s).count()
            present = AIAttendanceLog.objects.filter(student=s, status='Present').count()
            data.update({
                'total_records': total,
                'present': present,
                'attendance_pct': round(present / total * 100, 1) if total else 0,
            })
    data['unread_notifications'] = Notification.objects.filter(user=user, is_read=False).count()
    return JsonResponse({'ok': True, 'data': data})


# ──────────────────────────────────────────────────────────────────────────
# Schedule
# ──────────────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def schedule(request):
    user = request.api_user
    role = _role_of(user)
    qs = Schedule.objects.select_related('course', 'teacher', 'classroom').all()
    if role == 'teacher':
        t = Teacher.objects.filter(auth_user=user).first()
        qs = qs.filter(teacher=t) if t else qs.none()
    elif role == 'student':
        s = Student.objects.filter(auth_user=user).first()
        # student sees schedules for their batch/department courses
        qs = qs.filter(Q(batch=getattr(s, 'batch', '')) | Q(batch='')) if s else qs.none()
    rows = []
    for x in qs.order_by('day_of_week', 'start_time')[:200]:
        rows.append({
            'id': x.id,
            'course': getattr(x.course, 'title', None),
            'course_code': getattr(x.course, 'course_code', None),
            'teacher': getattr(x.teacher, 'name', None),
            'classroom': getattr(x.classroom, 'name', None),
            'day': x.day_of_week,
            'start': str(x.start_time), 'end': str(x.end_time),
            'semester': x.semester,
        })
    return JsonResponse({'ok': True, 'count': len(rows), 'schedule': rows})


# ──────────────────────────────────────────────────────────────────────────
# Reports / attendance summary
# ──────────────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def reports_summary(request):
    today = timezone.now().date()
    total = AIAttendanceLog.objects.count()
    present = AIAttendanceLog.objects.filter(status='Present').count()
    by_day = (AIAttendanceLog.objects
              .filter(status='Present')
              .extra(select={'d': "date(timestamp)"})
              .values('d').annotate(c=Count('id')).order_by('-d')[:7])
    return JsonResponse({
        'ok': True,
        'total_records': total,
        'present': present,
        'avg_attendance': round(present / total * 100, 1) if total else 0,
        'today': AIAttendanceLog.objects.filter(timestamp__date=today).count(),
        'recent_days': list(by_day),
    })


# ──────────────────────────────────────────────────────────────────────────
# Notifications
# ──────────────────────────────────────────────────────────────────────────
@api_auth
@require_http_methods(['GET'])
def notifications(request):
    qs = Notification.objects.filter(user=request.api_user).order_by('-id')[:50]
    rows = [{
        'id': n.id,
        'title': getattr(n, 'title', '') or '',
        'body': getattr(n, 'body', '') or getattr(n, 'message', '') or '',
        'level': getattr(n, 'level', '') or getattr(n, 'notif_type', '') or 'info',
        'is_read': n.is_read,
    } for n in qs]
    return JsonResponse({'ok': True, 'count': len(rows), 'notifications': rows})


@api_auth
@csrf_exempt
@require_http_methods(['POST'])
def mark_notifications_read(request):
    Notification.objects.filter(user=request.api_user, is_read=False).update(is_read=True)
    return JsonResponse({'ok': True})


# ──────────────────────────────────────────────────────────────────────────
# Face scan submit (native camera → base64 → match → log attendance)
# ──────────────────────────────────────────────────────────────────────────
@api_auth
@csrf_exempt
@require_http_methods(['POST'])
def scan_submit(request):
    """Accept a base64 JPEG, match against enrolled faces, log attendance.
    Returns the matched person + confidence, or an actionable error."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        payload = request.POST
    b64 = payload.get('image') or payload.get('image_data') or ''
    schedule_id = payload.get('schedule_id')
    if not b64:
        return JsonResponse({'ok': False, 'error': 'no_image',
                             'message': 'لم تصل صورة'}, status=400)

    # Engine-agnostic recognition (dlib or InsightFace via settings.FACE_ENGINE)
    from . import face_engine as fe
    from . import views as _v
    if not fe.available():
        return JsonResponse({'ok': False, 'error': 'engine_unavailable',
                             'message': 'محرك التعرف غير متوفر على الخادم'}, status=503)

    try:
        if ',' in b64:
            b64 = b64.split(',')[1]
        b64 = b64.strip().replace(' ', '+')
        b64 += '=' * (-len(b64) % 4)
        img_bytes = base64.b64decode(b64)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'bad_image',
                             'message': 'الصورة غير صالحة'}, status=400)

    try:
        import numpy as np
        from PIL import Image
        import io as _io
        img = np.array(Image.open(_io.BytesIO(img_bytes)).convert('RGB'))

        probe = fe.encode(img)
        if probe is None:
            return JsonResponse({'ok': False, 'error': 'no_face',
                                 'message': 'لم يُكتشف وجه — وجّه الكاميرا للوجه مباشرة'})

        # Unified DB match — same path as gate_scan_api / lecture_scan_api
        probe_list = probe if isinstance(probe, list) else probe.tolist()
        name, person_type, _person_pk = _v.match_face_from_db(probe_list)
        if not name:
            return JsonResponse({'ok': False, 'error': 'no_match',
                                 'message': 'الوجه غير مسجّل في النظام'})
        confidence = 1.0

        student = Student.objects.filter(name=name).first() if person_type == 'student' else None
        logged = False
        if student and schedule_id:
            sch = Schedule.objects.filter(id=schedule_id).first()
            if sch:
                AIAttendanceLog.objects.get_or_create(
                    student=student, schedule=sch,
                    defaults={
                        'confidence_score': confidence,
                        'status': 'Present',
                        'timestamp': timezone.now(),
                    },
                )
                logged = True
        return JsonResponse({'ok': True, 'matched': name, 'confidence': confidence,
                             'logged': logged, 'engine': fe.active_engine()})
    except Exception:
        return JsonResponse({'ok': False, 'error': 'processing_error',
                             'message': 'تعذّر تحليل الصورة'}, status=500)


# ──────────────────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────────────────
@require_http_methods(['GET'])
def health(request):
    return JsonResponse({'ok': True, 'service': 'shamel-api', 'version': 'v1',
                         'time': timezone.now().isoformat()})


# ──────────────────────────────────────────────────────────────────────────
# App Version — used by Flutter client for in-app update check
# ──────────────────────────────────────────────────────────────────────────
# Bump APP_VERSION_CODE whenever a new APK is released.
# Place the APK at /static/apk/shamel-latest.apk before incrementing.
APP_VERSION_CODE = 5          # integer — compare against Flutter build number
APP_VERSION_NAME = '1.3.1'   # display string
APP_VERSION_APK  = 'shamel-v1.2-production.apk'  # actual filename in /static/apk/

@require_http_methods(['GET'])
def app_version(request):
    from django.templatetags.static import static
    apk_url = request.build_absolute_uri(static(f'apk/{APP_VERSION_APK}')) + f'?v={APP_VERSION_CODE}'
    return JsonResponse({
        'version_code': APP_VERSION_CODE,
        'version_name': APP_VERSION_NAME,
        'apk_url': apk_url,
        'notes': 'تصميم محسّن للهاتف في صفحة المسح والبوابة، تسجيل دخول ببصمة الوجه، ونظام عمل بدون إنترنت.',
    })
