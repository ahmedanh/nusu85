from .models import Notification

def extras(request):
    if request.user.is_authenticated:
        # هنا بنجيب آخر 5 إشعارات للمستخدم اللي فاتح الصفحة حالياً
        notifications = Notification.objects.filter(user=request.user)[:5]
        return {'notifications': notifications}
    return {'notifications': []}