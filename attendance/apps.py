from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'

    def ready(self):
        import sys
        if 'runserver' not in sys.argv:
            return
            
        from .tasks import start_scheduler
        start_scheduler()
