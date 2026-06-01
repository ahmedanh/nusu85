"""
SHAMEL context processors.
Heavily cached to avoid 5+ VPS round-trips on every page load.
"""
from django.core.cache import cache
from .models import Notification

# Cache TTLs (seconds)
_NOTIF_TTL   = 15   # notifications refresh every 15s
_PROFILE_TTL = 120  # role profiles are stable — refresh every 2 min


def notifications_processor(request):
    return extras(request)


def extras(request):
    ctx = {
        'unread_count':          0,
        'recent_notifications':  [],
        'notifications':         [],
        'coordinator_profile':   None,
        'teacher_profile':       None,
        'student_profile':       None,
    }
    if not request.user.is_authenticated:
        return ctx

    uid = request.user.pk

    # ── Notification count + list (2 queries → 1 cached) ────────────────
    notif_key = f'shamel_notif_{uid}'
    notif_data = cache.get(notif_key)
    if notif_data is None:
        unread = list(
            Notification.objects.filter(user_id=uid, is_read=False)
            .order_by('-created_at')[:5]
        )
        notif_data = {'count': len(unread), 'items': unread}
        cache.set(notif_key, notif_data, _NOTIF_TTL)

    ctx['unread_count']         = notif_data['count']
    ctx['recent_notifications'] = notif_data['items']
    ctx['notifications']        = notif_data['items']

    # ── Role profiles (3 queries → 1 cached per user) ───────────────────
    profile_key = f'shamel_profiles_{uid}'
    profiles = cache.get(profile_key)
    if profiles is None:
        from .models import Coordinator, Teacher, Student
        profiles = {
            'coordinator': Coordinator.objects.filter(auth_user_id=uid).first(),
            'teacher':     Teacher.objects.filter(auth_user_id=uid).first(),
            'student':     Student.objects.filter(auth_user_id=uid).first(),
        }
        cache.set(profile_key, profiles, _PROFILE_TTL)

    ctx['coordinator_profile'] = profiles['coordinator']
    ctx['teacher_profile']     = profiles['teacher']
    ctx['student_profile']     = profiles['student']

    return ctx
