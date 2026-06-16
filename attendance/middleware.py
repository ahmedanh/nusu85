"""
SHAMEL custom middleware stack.
"""
from django.db import close_old_connections
from django.core.cache import cache

SESSION_CACHE_TTL = 30  # seconds to cache user object


class CloseOldConnectionsMiddleware:
    """
    1. close_old_connections() at request start — fixes stale VPS connections.
    2. Cache authenticated User objects — eliminates per-request DB round-trip
       to the remote PostgreSQL VPS on every page load.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        close_old_connections()

        # ── Try to serve user from cache ────────────────────────────────
        session_key = request.COOKIES.get('sessionid')
        cache_key   = f'shamel_user_{session_key}' if session_key else None

        if cache_key:
            cached_user = cache.get(cache_key)
            if cached_user is not None:
                request._cached_user = cached_user

        # ── Process request ──────────────────────────────────────────────
        response = self.get_response(request)

        # ── Cache the resolved user after this request ───────────────────
        if cache_key and not cache.get(cache_key):
            user = getattr(request, '_cached_user', None) or getattr(request, 'user', None)
            if user is not None and getattr(user, 'pk', None):
                cache.set(cache_key, user, SESSION_CACHE_TTL)

        # ── Force fresh HTML ─────────────────────────────────────────────
        # Dynamic, per-user pages must NOT be cached by the browser (no header
        # = heuristic caching → users see stale UI after we ship template/JS/CSS
        # changes). Force revalidation on every HTML navigation. Static assets
        # (handled by WhiteNoise) keep their own long-cache headers.
        ctype = response.get('Content-Type', '')
        if ctype.startswith('text/html'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response


class ContentSecurityPolicyMiddleware:
    """Adds Content-Security-Policy header to all responses."""

    CSP = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "  https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' "
        "  https://cdn.tailwindcss.com https://fonts.googleapis.com https://cdn.jsdelivr.net; "
        "font-src 'self' data: https://fonts.gstatic.com; "
        "img-src 'self' data: blob:; "
        "connect-src 'self' ws: wss:; "
        "media-src 'self' blob:; "
        "worker-src blob:; "
        "frame-ancestors 'none';"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = self.CSP
        return response
