# -*- coding: utf-8 -*-
"""
SHAMEL gRPC Face Service
Runs alongside Django on port 50051 (configurable via GRPC_PORT env var).
Start: python manage.py run_grpc

Browser clients continue to use the existing HTTP endpoints.
Flutter / native clients should use this gRPC service for lower latency.
"""
import os
import io
import sys
import time
import base64
import logging
import threading
import queue
from concurrent import futures

# Must be importable standalone — set up Django settings before importing models
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')

import django
django.setup()

import grpc
import numpy as np
import cv2

from attendance.grpc_generated import face_service_pb2 as pb2
from attendance.grpc_generated import face_service_pb2_grpc as pb2_grpc
import attendance.face_engine as _fe_module
from attendance.models import (
    Student, Teacher,
    StudentFaceEmbedding, TeacherFaceEmbedding,
    GateLog, LectureSession, Enrollment, AIAttendanceLog,
)
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

# ── shared gate event bus (for LiveGateFeed streams) ─────────────────────────
_gate_event_queues: list[queue.Queue] = []
_gate_event_lock = threading.Lock()


def _broadcast_gate_event(name: str, status: str, person_type: str):
    ts = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with _gate_event_lock:
        dead = []
        for q in _gate_event_queues:
            try:
                q.put_nowait({'name': name, 'status': status, 'ts': ts, 'type': person_type})
            except queue.Full:
                dead.append(q)
        for q in dead:
            _gate_event_queues.remove(q)


def _decode_image(image_data: bytes):
    """Decode raw bytes → RGB ndarray. Returns None on failure."""
    arr = np.frombuffer(image_data, dtype=np.uint8)
    bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if bgr is None:
        return None
    return bgr[:, :, ::-1]  # BGR→RGB


def _authenticate_token(auth_token: str):
    """Validate Bearer token (DRF Token) and return User or None."""
    from rest_framework.authtoken.models import Token
    try:
        tok = Token.objects.select_related('user').get(key=auth_token.strip())
        return tok.user
    except Exception:
        return None


# ─────────────────────────────────────────────────────────────────────────────
class FaceServicer(pb2_grpc.FaceServiceServicer):

    # ── Gate Scan ──────────────────────────────────────────────────────────
    def ScanGate(self, request, context):
        from attendance.views import match_face_from_db, _gate_cooldown, _gate_cooldown_lock, _GATE_COOLDOWN_SEC
        from attendance.models import FinancialStatus

        user = _authenticate_token(request.auth_token)
        if not user:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return pb2.GateScanResponse(ok=False, error='unauthenticated')

        img = _decode_image(request.image_data)
        if img is None:
            return pb2.GateScanResponse(ok=False, error='bad_image')

        all_faces = _fe_module.encode_all(img)
        if not all_faces:
            return pb2.GateScanResponse(ok=True, detected=False)

        now_ts = time.time()
        results = []

        for face_data in all_faces:
            probe = face_data['embedding']
            bbox  = face_data['bbox']
            pb_bbox = pb2.BoundingBox(x1=bbox['x1'], y1=bbox['y1'], x2=bbox['x2'], y2=bbox['y2'])

            matched_name, matched_type, matched_pk = match_face_from_db(probe)
            if not matched_name:
                results.append(pb2.FaceResult(matched=False, bbox=pb_bbox))
                continue

            student = Student.objects.filter(pk=matched_pk).first() if matched_type == 'student' else None
            teacher = Teacher.objects.filter(pk=matched_pk).first() if matched_type == 'teacher' else None

            is_allowed  = True
            deny_reason = ''
            if student:
                is_allowed  = bool(student.is_allowed_entry)
                deny_reason = 'غير مسموح بالدخول' if not is_allowed else ''

            status_str  = 'Allowed' if is_allowed else 'Denied'
            person_key  = f'{matched_name}_{status_str}'

            with _gate_cooldown_lock:
                last = _gate_cooldown.get(person_key, 0)
                in_cooldown = (now_ts - last) < _GATE_COOLDOWN_SEC
                if not in_cooldown:
                    _gate_cooldown[person_key] = now_ts

            if not in_cooldown:
                GateLog.objects.create(
                    person_name=matched_name,
                    student=student,
                    teacher=teacher,
                    status=status_str,
                )
                _broadcast_gate_event(matched_name, status_str, matched_type or '')

            fees_paid = True
            registered = True
            student_code = ''
            phone = ''
            if student:
                student_code = student.student_code or ''
                phone        = student.phone_number or ''
                registered   = student.is_registered
                fs = FinancialStatus.objects.filter(student=student).first()
                fees_paid = fs.is_paid if fs else True
            elif teacher:
                phone = getattr(teacher, 'phone_number', '') or ''

            person = pb2.PersonInfo(
                name=matched_name,
                type='student' if student else 'teacher',
                allowed=is_allowed,
                deny_reason=deny_reason,
                cooldown=in_cooldown,
                student_code=student_code,
                phone=phone,
                registered=registered,
                fees_paid=fees_paid,
            )
            results.append(pb2.FaceResult(matched=True, bbox=pb_bbox, person=person))

        h, w = img.shape[:2]
        return pb2.GateScanResponse(
            ok=True, detected=True,
            results=results,
            frame_width=w, frame_height=h,
        )

    # ── Lecture Scan ───────────────────────────────────────────────────────
    def ScanLecture(self, request, context):
        from attendance.views import _gate_cooldown, _gate_cooldown_lock

        user = _authenticate_token(request.auth_token)
        if not user:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return pb2.LectureScanResponse(ok=False, error='unauthenticated')

        try:
            session = LectureSession.objects.select_related('schedule__course').get(
                pk=request.session_id, is_active=True
            )
        except LectureSession.DoesNotExist:
            return pb2.LectureScanResponse(ok=False, error='session_not_found')

        img = _decode_image(request.image_data)
        if img is None:
            return pb2.LectureScanResponse(ok=False, error='bad_image')

        course = session.schedule.course
        enrolled_students = list(
            Student.objects.filter(enrollment__course=course)
            .prefetch_related('studentfaceembedding')
        )

        known = []
        known_map = []
        for st in enrolled_students:
            try:
                emb_obj = st.studentfaceembedding
                if emb_obj.embedding:
                    known.append(list(emb_obj.embedding))
                    known_map.append(('student', st))
                for extra in (emb_obj.extra_embeddings or []):
                    if extra:
                        known.append(list(extra))
                        known_map.append(('student', st))
            except Exception:
                pass

        all_faces = _fe_module.encode_all(img)
        if not all_faces:
            return pb2.LectureScanResponse(ok=True, detected=False)

        COOLDOWN_SEC = 30
        now_ts = time.time()
        results = []

        for face_data in all_faces:
            probe = face_data['embedding']
            bbox  = face_data['bbox']
            pb_bbox = pb2.BoundingBox(x1=bbox['x1'], y1=bbox['y1'], x2=bbox['x2'], y2=bbox['y2'])

            best_i, best_s = _fe_module.match(known, probe)
            if best_i < 0:
                results.append(pb2.LecturePersonResult(matched=False, bbox=pb_bbox))
                continue

            _, matched_obj = known_map[best_i]
            person_key = f'lecture_{session.pk}_{matched_obj.pk}'

            with _gate_cooldown_lock:
                last = _gate_cooldown.get(person_key, 0)
                in_cooldown = (now_ts - last) < COOLDOWN_SEC
                if not in_cooldown:
                    _gate_cooldown[person_key] = now_ts

            already_logged = AIAttendanceLog.objects.filter(
                session=session, student=matched_obj
            ).exists()

            if not in_cooldown and not already_logged:
                AIAttendanceLog.objects.get_or_create(
                    session=session, student=matched_obj,
                    defaults={'status': 'present', 'confidence': best_s},
                )

            results.append(pb2.LecturePersonResult(
                name=matched_obj.name,
                type='student',
                matched=True,
                already_logged=already_logged,
                bbox=pb_bbox,
            ))

        return pb2.LectureScanResponse(ok=True, detected=True, results=results)

    # ── Face Login ─────────────────────────────────────────────────────────
    def LoginFace(self, request, context):
        from attendance.views import match_face_from_db

        img = _decode_image(request.image_data)
        if img is None:
            return pb2.LoginResponse(success=False, error='bad_image')

        enc = _fe_module.encode(img)
        if not enc:
            return pb2.LoginResponse(success=False, error='no_face_detected')

        matched_name, matched_type, matched_pk = match_face_from_db(enc)
        if not matched_name:
            return pb2.LoginResponse(success=False, error='face_not_registered')

        if matched_type == 'student':
            person = Student.objects.filter(pk=matched_pk).select_related('auth_user').first()
        else:
            person = Teacher.objects.filter(pk=matched_pk).select_related('auth_user').first()

        if not person or not person.auth_user:
            return pb2.LoginResponse(success=False, error='no_linked_account')

        # Return DRF token for Flutter
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=person.auth_user)

        redirect_url = '/attendance/student/dashboard/' if matched_type == 'student' else '/attendance/professor-dashboard/'
        if person.auth_user.is_superuser:
            redirect_url = '/attendance/admin-panel/'

        return pb2.LoginResponse(
            success=True,
            name=matched_name,
            redirect_url=redirect_url,
            session_key=token.key,
        )

    # ── Face Enrollment ────────────────────────────────────────────────────
    def EnrollFace(self, request, context):
        from attendance.views import load_known_faces

        user = _authenticate_token(request.auth_token)
        if not user:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return pb2.EnrollResponse(success=False, error='unauthenticated')

        img = _decode_image(request.image_data)
        if img is None:
            return pb2.EnrollResponse(success=False, error='bad_image')

        enc = _fe_module.encode(img)
        if not enc:
            return pb2.EnrollResponse(success=False, error='no_face_detected')

        angle_index = request.angle_index or 0

        try:
            if request.person_type == 'student':
                obj = Student.objects.get(pk=request.person_id)
                emb, _ = StudentFaceEmbedding.objects.get_or_create(
                    student=obj, defaults={'embedding': enc, 'extra_embeddings': []}
                )
                if angle_index == 0:
                    emb.embedding = enc
                else:
                    extras = list(emb.extra_embeddings or [])
                    idx = angle_index - 1
                    if idx < len(extras):
                        extras[idx] = enc
                    else:
                        extras.append(enc)
                    emb.extra_embeddings = extras
                emb.save()
            else:
                obj = Teacher.objects.get(pk=request.person_id)
                emb, _ = TeacherFaceEmbedding.objects.get_or_create(
                    teacher=obj, defaults={'face_vector': enc, 'extra_embeddings': []}
                )
                if angle_index == 0:
                    emb.face_vector = enc
                else:
                    extras = list(emb.extra_embeddings or [])
                    idx = angle_index - 1
                    if idx < len(extras):
                        extras[idx] = enc
                    else:
                        extras.append(enc)
                    emb.extra_embeddings = extras
                emb.save()

            load_known_faces()
            return pb2.EnrollResponse(success=True, angle_index=angle_index)

        except Exception as e:
            logger.error('gRPC EnrollFace error: %s', e)
            return pb2.EnrollResponse(success=False, error=str(e))

    # ── Live Gate Feed (server-side streaming) ─────────────────────────────
    def LiveGateFeed(self, request, context):
        user = _authenticate_token(request.auth_token)
        if not user:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return

        q: queue.Queue = queue.Queue(maxsize=50)
        with _gate_event_lock:
            _gate_event_queues.append(q)

        try:
            while context.is_active():
                try:
                    event = q.get(timeout=1.0)
                    yield pb2.GateEvent(
                        person_name=event['name'],
                        status=event['status'],
                        timestamp=event['ts'],
                        person_type=event['type'],
                    )
                except queue.Empty:
                    continue
        finally:
            with _gate_event_lock:
                if q in _gate_event_queues:
                    _gate_event_queues.remove(q)

    # ── Health Check ───────────────────────────────────────────────────────
    def HealthCheck(self, request, context):
        from attendance.face_engine import available, embedding_dim, active_engine

        eng_ok  = available()
        eng_dim = embedding_dim()
        eng_name = active_engine()

        student_count   = StudentFaceEmbedding.objects.count()
        teacher_count   = TeacherFaceEmbedding.objects.count()
        mismatch_count  = 0

        for emb in StudentFaceEmbedding.objects.all():
            v = list(emb.embedding or [])
            if v and len(v) != eng_dim:
                mismatch_count += 1

        for emb in TeacherFaceEmbedding.objects.all():
            v = list(emb.face_vector or [])
            if v and len(v) != eng_dim:
                mismatch_count += 1

        return pb2.HealthResponse(
            engine_available=eng_ok,
            engine_name=eng_name,
            student_embeddings=student_count,
            teacher_embeddings=teacher_count,
            dim_mismatch_count=mismatch_count,
            engine_dim=str(eng_dim),
        )


# ─────────────────────────────────────────────────────────────────────────────
def serve(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    pb2_grpc.add_FaceServiceServicer_to_server(FaceServicer(), server)
    listen_addr = f'[::]:{port}'
    server.add_insecure_port(listen_addr)
    server.start()
    logger.info('SHAMEL gRPC face service listening on %s', listen_addr)
    print(f'[gRPC] SHAMEL face service started on port {port}')
    return server


if __name__ == '__main__':
    port = int(os.environ.get('GRPC_PORT', 50051))
    srv = serve(port)
    try:
        srv.wait_for_termination()
    except KeyboardInterrupt:
        srv.stop(grace=5)
