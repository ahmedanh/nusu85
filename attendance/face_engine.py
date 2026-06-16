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


def _preprocess(image: np.ndarray) -> np.ndarray:
    """Robust lighting normalisation for all indoor/outdoor conditions.

    Pipeline:
      1. White-balance via gray-world assumption (removes colour casts)
      2. Auto-gamma from mean luminance (dark / dim / bright / blown-out)
      3. Histogram stretching for severely dark images (mean < 50)
      4. CLAHE on LAB L-channel (strong contrast, preserves colour)
    """
    try:
        import cv2
        # image arrives as RGB from callers
        bgr = image[:, :, ::-1]

        # 1) Gray-world white balance — removes projector / sodium-lamp colour cast
        b_ch, g_ch, r_ch = cv2.split(bgr.astype(np.float32))
        b_mean, g_mean, r_mean = b_ch.mean(), g_ch.mean(), r_ch.mean()
        if b_mean > 0 and g_mean > 0 and r_mean > 0:
            global_mean = (b_mean + g_mean + r_mean) / 3.0
            bgr = cv2.merge([
                np.clip(b_ch * (global_mean / b_mean), 0, 255).astype(np.uint8),
                np.clip(g_ch * (global_mean / g_mean), 0, 255).astype(np.uint8),
                np.clip(r_ch * (global_mean / r_mean), 0, 255).astype(np.uint8),
            ])

        # 2) Auto-gamma from mean luminance
        gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
        mean_b = float(gray.mean())
        if mean_b < 50:          # severe darkness (night / blackout room)
            gamma = 2.5
        elif mean_b < 80:        # dark room / back-lit
            gamma = 1.8
        elif mean_b < 115:       # slightly dim
            gamma = 1.3
        elif mean_b > 210:       # blown-out / harsh flash
            gamma = 0.55
        elif mean_b > 175:       # bright
            gamma = 0.80
        else:
            gamma = 1.0
        if gamma != 1.0:
            lut = np.array(
                [min(255, int(((i / 255.0) ** (1.0 / gamma)) * 255))
                 for i in range(256)], dtype=np.uint8)
            bgr = cv2.LUT(bgr, lut)

        # 3) Histogram stretching for severely dark images after gamma
        if mean_b < 50:
            gray2 = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
            p1, p99 = np.percentile(gray2, [1, 99])
            if p99 > p1:
                alpha = 255.0 / (p99 - p1)
                bgr = np.clip((bgr.astype(np.float32) - p1) * alpha, 0, 255).astype(np.uint8)

        # 4) CLAHE on LAB L-channel
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge((l, a, b))
        bgr = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        return bgr[:, :, ::-1]  # back to RGB
    except Exception:
        return image


def encode(image: np.ndarray) -> list | None:
    """Detect the most prominent face in an RGB/BGR ndarray and return its
    embedding as a plain list of floats, or None if no face is found."""
    image = _preprocess(image)
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
        # cosine similarity on L2-normalised vectors; threshold ~0.30
        # Lower fallback (0.25) gives more robustness in bad lighting while
        # still rejecting random strangers (same-person sim is usually 0.5+)
        threshold = getattr(settings, 'FACE_THRESHOLD', 0.22)
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


def encode_all(image: np.ndarray) -> list[dict]:
    """Return embedding + bbox for ALL detected faces in one pass."""
    image = _preprocess(image)
    engine = active_engine()
    if engine == 'insightface':
        app = _get_insightface()
        if app is None:
            return []
        try:
            faces = app.get(image)
            result = []
            for f in faces:
                x1, y1, x2, y2 = [float(v) for v in f.bbox]
                result.append({
                    'embedding': [float(x) for x in f.normed_embedding],
                    'bbox': {'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2},
                    'score': float(f.det_score) if hasattr(f, 'det_score') else 1.0,
                })
            return result
        except Exception:
            return []
    return []


def detect(image: np.ndarray) -> list[dict]:
    """Return list of detected faces with bbox and confidence. No embedding computed."""
    engine = active_engine()
    if engine == 'insightface':
        app = _get_insightface()
        if app is None:
            return []
        try:
            faces = app.get(image)
            result = []
            for f in faces:
                x1, y1, x2, y2 = [float(v) for v in f.bbox]
                result.append({
                    'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2,
                    'score': float(f.det_score) if hasattr(f, 'det_score') else 1.0,
                })
            return result
        except Exception:
            return []
    return []


def available() -> bool:
    """Is the active engine usable right now?"""
    if active_engine() == 'insightface':
        return _get_insightface() is not None
    try:
        import face_recognition  # noqa: F401
        return True
    except Exception:
        return False
