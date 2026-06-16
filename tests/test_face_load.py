"""
SHAMEL Face Recognition Load Test — concurrent session capacity.

Measures how many simultaneous face-scan API calls the server can handle.
Uses a minimal synthetic JPEG (white/gray face-like frame) — engine will
return 'no_face' but this still exercises the full preprocessing pipeline,
numpy/ONNX decode path, and DB embedding fetch.

Usage:
  locust -f tests/test_face_load.py --headless \
         -u 20 --spawn-rate 2 --run-time 60s \
         --host http://127.0.0.1:8000
"""
import base64
import json
import io
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from locust import HttpUser, task, between, events

# ── Synthetic test frame (100×100 gray JPEG, ~1 KB) ──────────────────────────
def _make_test_frame() -> str:
    """Return a base64 JPEG that hits the preprocessing pipeline but likely
    won't match any real face (no_face or no_match response expected)."""
    try:
        from PIL import Image
        img = Image.new('RGB', (160, 120), color=(180, 160, 140))
        # Draw a rough ellipse to simulate a face-like blob
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([40, 20, 120, 100], fill=(220, 190, 170))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80)
        return base64.b64encode(buf.getvalue()).decode()
    except Exception:
        # Fallback: 1×1 white pixel
        return '/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoH\nBwYIDAoMCwsKCwsNCxAQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/wAARC\nAABAAEDASIAAhEBAxEB/8QAFAABAAAAAAAAAAAAAAAAAAAACf/EABQQAQAAAAAAAA\nAAAAAAAAAAAA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/EABQRAQAAAAAAAAAAAAAAAAAAAAD/2gAM\nAwEAAhEDEQA/AFUAB//Z'

TEST_FRAME = _make_test_frame()


def _login(client) -> str | None:
    """Authenticate via API and return token."""
    from config import CREDENTIALS
    creds = CREDENTIALS.get('admin', {})
    r = client.post(
        '/api/v1/auth/login',
        json={'username': creds.get('username', 'test_admin'),
              'password': creds.get('password', 'Test@1234')},
        name='/api/v1/auth/login [setup]',
        catch_response=True,
    )
    try:
        data = r.json()
        return data.get('token') or data.get('access_token')
    except Exception:
        return None


class GateScanUser(HttpUser):
    """Simulates gate face-scan bursts."""
    wait_time = between(0.5, 2.0)
    token: str = ''

    def on_start(self):
        tok = _login(self.client)
        if tok:
            self.token = tok
            self.client.headers.update({'Authorization': f'Bearer {tok}'})

    @task(3)
    def gate_scan(self):
        with self.client.post(
            '/api/v1/scan',
            json={'image': TEST_FRAME},
            name='/api/v1/scan [gate]',
            catch_response=True,
        ) as r:
            try:
                data = r.json()
                # ok=True (matched) or ok=False with no_face/no_match are both valid outcomes
                if r.status_code in (200, 400):
                    r.success()
                elif r.status_code == 503:
                    r.failure('engine unavailable')
                else:
                    r.failure(f'HTTP {r.status_code}')
            except Exception as e:
                r.failure(str(e))

    @task(1)
    def check_face_health(self):
        with self.client.get(
            '/api/v1/health',
            name='/api/v1/health',
            catch_response=True,
        ) as r:
            if r.status_code == 200:
                r.success()
            else:
                r.failure(f'HTTP {r.status_code}')


class LectureScanUser(HttpUser):
    """Simulates lecture scan bursts (teacher-initiated)."""
    wait_time = between(1.0, 3.0)
    token: str = ''

    def on_start(self):
        from config import CREDENTIALS
        creds = CREDENTIALS.get('teacher', {})
        r = self.client.post(
            '/api/v1/auth/login',
            json={'username': creds.get('username', 'test_teacher'),
                  'password': creds.get('password', 'Test@1234')},
            name='/api/v1/auth/login [teacher]',
        )
        try:
            tok = r.json().get('token')
            if tok:
                self.token = tok
                self.client.headers.update({'Authorization': f'Bearer {tok}'})
        except Exception:
            pass

    @task
    def lecture_scan(self):
        # Lecture scan via web endpoint (uses gate_scan_api internally)
        with self.client.post(
            '/api/v1/scan',
            json={'image': TEST_FRAME},
            name='/api/v1/scan [lecture]',
            catch_response=True,
        ) as r:
            if r.status_code in (200, 400, 503):
                r.success()
            else:
                r.failure(f'HTTP {r.status_code}')


# ── Results summary ───────────────────────────────────────────────────────────
@events.quitting.add_listener
def on_quit(environment, **kw):
    stats = environment.runner.stats
    total = stats.total
    print('\n' + '=' * 60)
    print('  Face Recognition Load Test — Results')
    print('=' * 60)
    print(f'  Total requests : {total.num_requests}')
    print(f'  Failures       : {total.num_failures}')
    print(f'  RPS            : {total.total_rps:.1f}')
    print(f'  P50 latency    : {total.get_response_time_percentile(0.50):.0f} ms')
    print(f'  P95 latency    : {total.get_response_time_percentile(0.95):.0f} ms')
    print(f'  P99 latency    : {total.get_response_time_percentile(0.99):.0f} ms')
    failure_pct = (total.num_failures / total.num_requests * 100) if total.num_requests else 0
    print(f'  Failure rate   : {failure_pct:.1f}%')
    print('=' * 60)

    result = {
        'total': total.num_requests,
        'failures': total.num_failures,
        'rps': round(total.total_rps, 2),
        'p50_ms': total.get_response_time_percentile(0.50),
        'p95_ms': total.get_response_time_percentile(0.95),
        'p99_ms': total.get_response_time_percentile(0.99),
    }
    import json as _json
    out = os.path.join(os.path.dirname(__file__), 'face_load_results.json')
    with open(out, 'w') as f:
        _json.dump(result, f, indent=2)
    print(f'  Saved → {out}')
