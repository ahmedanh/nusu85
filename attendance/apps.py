from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'attendance'

    def ready(self):
        import sys
        import os

        # Skip during management commands
        skip_cmds = {'migrate', 'makemigrations', 'collectstatic', 'check',
                     'shell', 'test', 'createsuperuser', 'createcachetable',
                     'showmigrations', 'sqlmigrate', 'dbshell', 'seed_demo'}
        if any(cmd in sys.argv for cmd in skip_cmds):
            return

        # Only start scheduler in the main reloader process (RUN_MAIN=true) on Windows
        # On Linux use fcntl file lock; on Windows use a simple env-var guard.
        if os.environ.get('SHAMEL_SCHEDULER_STARTED'):
            return
        os.environ['SHAMEL_SCHEDULER_STARTED'] = '1'

        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.interval import IntervalTrigger
            from apscheduler.triggers.cron import CronTrigger
            from .tasks import update_classroom_status, sync_offline_cache, check_attendance_compliance

            scheduler = BackgroundScheduler(
                job_defaults={'misfire_grace_time': 60, 'coalesce': True}
            )
            scheduler.add_job(update_classroom_status, IntervalTrigger(minutes=1),
                              id='classroom_status', replace_existing=True)
            scheduler.add_job(sync_offline_cache, IntervalTrigger(minutes=2),
                              id='offline_sync', replace_existing=True)
            scheduler.add_job(check_attendance_compliance, CronTrigger(hour=8, minute=0),
                              id='attendance_compliance', replace_existing=True)
            scheduler.start()
        except Exception:
            pass  # Never crash the server if scheduler fails
