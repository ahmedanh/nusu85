from django.apps import AppConfig

class AttendanceConfig(AppConfig):
    name = 'attendance'

    def ready(self):
        import sys
        argv = sys.argv
        if not any(cmd in argv for cmd in ['runserver', 'gunicorn']):
            if not any('gunicorn' in arg for arg in argv):
                return
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        from .tasks import update_classroom_status, sync_offline_cache
        scheduler = BackgroundScheduler()
        scheduler.add_job(update_classroom_status, IntervalTrigger(minutes=1),
                         id='classroom_status', replace_existing=True)
        scheduler.add_job(sync_offline_cache, IntervalTrigger(minutes=2),
                         id='offline_sync', replace_existing=True)
        scheduler.start()
