# -*- coding: utf-8 -*-
"""
SHAMEL face-recognition engine abstraction.

Two backends behind one interface:
  • 'dlib'         — the legacy face_recognition library (128-dim).
  • 'insightface'  — InsightFace buffalo_s, ONNX, CPU (512-dim) — faster
                     and more accurate, recommended for the weak VPS.

Selection is driven by settings.FACE_ENGINE (default 'dlib' so existing
deployments and stored 128-dim embeddings keep working untouched).

IMPORTANT — embedding dimensions differ (128 vs 512). Switching engines
requires re-enrolling faces with the active engine (see the `reenroll_faces`
management command). The matcher only compares same-length vectors, so
mixing dimensions can never produce a false match.
"""
from __future__ import annotations
import threading
import numpy as np
from django.conf import settings


def active_engine() -> str:
    return getattr(settings, 'FACE_ENGINE', 'dlib')


# ── InsightFace lazy singleton ─────────────────────────────────────────────
_if_app = None
_if_lock = threading.Lock()


def _get_insightface():
    """Lazy-load buffalo_s once. Returns the FaceAnalysis app or None."""
    global _if_app
    if _if_app is not None:
        return _if_app
    with _if_lock:
        if _if_app is not None:
            return _if_app
        try:
            from insightface.app import FaceAnalysis
            app = FaceAnalysis(name='buffalo_s', providers=['CPUExecutionProvider'])
            app.prepare(ctx_id=-1, det_size=(320, 320))
            _if_app = app
        except Exception:
            _if_app = None
        return _if_app


# ── Unified API ────────────────────────────────────────────────────────────
def embedding_dim() -> int:
    return 512 if active_engine() == 'insightface' else 128


def encode(image: np.ndarray) -> list | None:
    """Detect the most prominent face in an RGB/BGR ndarray and return its
    embedding as a plain list of floats, or None if no face is found."""
    engine = active_engine()
    if engine == 'insightface':
        app = _get_insightface()
        if app is None:
            return None
        faces = app.get(image)
        if not faces:
            return None
        # pick the largest face
        faces.sort(key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]), reverse=True)
        emb = faces[0].normed_embedding  # already L2-normalised, 512-dim
        return [float(x) for x in emb]
    else:
        # dlib / face_recognition path
        try:
            import face_recognition
            locs = face_recognition.face_locations(image)
            if not locs:
                return None
            encs = face_recognition.face_encodings(image, locs)
            if not encs:
                return None
            return [float(x) for x in encs[0]]
        except Exception:
            return None


def match(known: list[list[float]], probe: list[float]):
    """Return (best_index, score 0..1) of the closest enrolled embedding,
    or (-1, 0.0) when nothing passes the engine threshold.

    Only same-dimension vectors are compared, so 128-dim and 512-dim
    embeddings can safely coexist in storage."""
    if not known or probe is None:
        return -1, 0.0
    p = np.asarray(probe, dtype=np.float32)
    engine = active_engine()

    if engine == 'insightface':
        # cosine similarity on L2-normalised vectors; threshold ~0.35
        threshold = getattr(settings, 'FACE_THRESHOLD', 0.35)
        best_i, best_s = -1, -1.0
        for i, k in enumerate(known):
            ka = np.asarray(k, dtype=np.float32)
            if ka.shape != p.shape:
                continue
            s = float(np.dot(ka, p) / ((np.linalg.norm(ka) * np.linalg.norm(p)) + 1e-8))
            if s > best_s:
                best_s, best_i = s, i
        return (best_i, best_s) if best_s >= threshold else (-1, max(best_s, 0.0))
    else:
        # dlib: euclidean distance, tolerance 0.5 → confidence = 1 - dist
        tol = getattr(settings, 'FACE_TOLERANCE', 0.5)
        best_i, best_d = -1, 1e9
        for i, k in enumerate(known):
            ka = np.asarray(k, dtype=np.float32)
            if ka.shape != p.shape:
                continue
            d = float(np.linalg.norm(ka - p))
            if d < best_d:
                best_d, best_i = d, i
        if best_i >= 0 and best_d <= tol:
            return best_i, max(0.0, 1.0 - best_d)
        return -1, 0.0


def available() -> bool:
    """Is the active engine usable right now?"""
    if active_engine() == 'insightface':
        return _get_insightface() is not None
    try:
        import face_recognition  # noqa: F401
        return True
    except Exception:
        return False
