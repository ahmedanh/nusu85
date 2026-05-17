from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'

    def ready(self):
        import sys
        if 'runserver' not in sys.argv:
            return
            
        from apscheduler.schedulers.background import BackgroundScheduler
        from .tasks import update_classroom_status
        
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            update_classroom_status, 
            'interval', 
            minutes=1, 
            id='update_classroom_status_job', 
            replace_existing=True
        )
        scheduler.start()
