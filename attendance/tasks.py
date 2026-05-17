from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone
from .models import Schedule, Classroom, LectureSession

def update_classroom_status():
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%A')
    
    # Release busy classrooms where session time has passed
    classrooms = Classroom.objects.filter(is_busy=True)
    for room in classrooms:
        schedules = Schedule.objects.filter(
            classroom=room, 
            day_of_week=current_day,
            start_time__lte=current_time,
            end_time__gte=current_time
        )
        if not schedules.exists():
            # Time has passed
            room.is_busy = False
            room.is_occupied = False
            room.save(update_fields=['is_busy', 'is_occupied'])
            
            # Close associated active sessions
            LectureSession.objects.filter(
                schedule__classroom=room, is_active=True
            ).update(is_active=False, actual_end_time=now)

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        update_classroom_status,
        trigger=IntervalTrigger(minutes=1),
        id='update_classroom_status',
        name='Update classroom status based on schedule',
        replace_existing=True,
    )
    scheduler.start()
