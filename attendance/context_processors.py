from .models import Notification


# Alias used in settings.py TEMPLATES context_processors
def notifications_processor(request):
    return extras(request)


def extras(request):
    ctx = {}
    if request.user.is_authenticated:
        unread_qs = Notification.objects.filter(user=request.user, is_read=False)
        ctx['unread_count']         = unread_qs.count()
        ctx['recent_notifications'] = unread_qs[:5]
        ctx['notifications']        = unread_qs[:5]

        from .models import Coordinator, Teacher, Student
        ctx['coordinator_profile'] = Coordinator.objects.filter(auth_user=request.user).first()
        ctx['teacher_profile']     = Teacher.objects.filter(auth_user=request.user).first()
        ctx['student_profile']     = Student.objects.filter(auth_user=request.user).first()
    else:
        ctx['unread_count']         = 0
        ctx['recent_notifications'] = []
        ctx['notifications']        = []
        ctx['coordinator_profile']  = None
        ctx['teacher_profile']      = None
        ctx['student_profile']      = None
    return ctx
