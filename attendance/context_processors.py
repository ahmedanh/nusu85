from django.core.cache import cache
from .models import Notification


def extras(request):
    ctx = {}
    if request.user.is_authenticated:
        uid = request.user.pk

        # Notifications: always fresh (cheap count + slice)
        unread_qs = Notification.objects.filter(user=request.user, is_read=False)
        ctx['unread_count']         = unread_qs.count()
        ctx['recent_notifications'] = list(unread_qs[:5])
        ctx['notifications']        = ctx['recent_notifications']  # backward compat

        # Role profiles: cached 5 min — roles almost never change
        cache_key = f'role_profiles_{uid}'
        profiles = cache.get(cache_key)
        if profiles is None:
            from .models import Coordinator, Teacher, Student
            profiles = {
                'coordinator': Coordinator.objects.select_related('college').filter(auth_user=request.user).first(),
                'teacher':     Teacher.objects.select_related('department').filter(auth_user=request.user).first(),
                'student':     Student.objects.select_related('department').filter(auth_user=request.user).first(),
            }
            cache.set(cache_key, profiles, 300)

        ctx['coordinator_profile'] = profiles['coordinator']
        ctx['teacher_profile']     = profiles['teacher']
        ctx['student_profile']     = profiles['student']
    else:
        ctx['unread_count']         = 0
        ctx['recent_notifications'] = []
        ctx['notifications']        = []
        ctx['coordinator_profile']  = None
        ctx['teacher_profile']      = None
        ctx['student_profile']      = None
    return ctx
