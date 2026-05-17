from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.utils import timezone


def update_classroom_status():
    """Release classrooms whose scheduled time has passed and close active sessions."""
    from .models import Schedule, Classroom, LectureSession
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%A')

    classrooms = Classroom.objects.filter(is_busy=True)
    for room in classrooms:
        schedules = Schedule.objects.filter(
            classroom=room,
            day_of_week=current_day,
            start_time__lte=current_time,
            end_time__gte=current_time
        )
        if not schedules.exists():
            room.is_busy = False
            room.is_occupied = False
            room.save(update_fields=['is_busy', 'is_occupied'])

            LectureSession.objects.filter(
                schedule__classroom=room, is_active=True
            ).update(is_active=False, actual_end_time=now)


def check_attendance_compliance():
    """
    Phase 4: Automated attendance compliance checker.
    - < 80%: Creates a warning Notification.
    - < 75%: Creates a critical Notification and sends an email.
    Runs every 24 hours (configurable).
    """
    from .models import Student, AIAttendanceLog, Notification
    from django.db.models import Count, Q
    from django.core.mail import send_mail
    from django.conf import settings

    students = Student.objects.annotate(
        total_logs=Count('aiattendancelog'),
        present_logs=Count('aiattendancelog', filter=Q(aiattendancelog__status='Present'))
    ).filter(total_logs__gt=0)

    for student in students:
        rate = (student.present_logs / student.total_logs) * 100

        # Skip students who already have a recent notification (avoid spam)
        auth_user = student.auth_user
        if not auth_user:
            continue

        if rate < 75:
            # Critical — create notification and send email
            Notification.objects.create(
                user=auth_user,
                message=f"CRITICAL: Your attendance is {rate:.1f}%. You are at risk of losing eligibility.",
                notif_type='error'
            )
            try:
                send_mail(
                    subject='CRITICAL: Attendance Warning — ACDC System',
                    message=(
                        f"Dear {student.name},\n\n"
                        f"Your current attendance rate is {rate:.1f}%, which is below the 75% eligibility threshold.\n"
                        f"Please contact your coordinator immediately.\n\n"
                        f"— ACDC Academic Compliance System"
                    ),
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@university.edu'),
                    recipient_list=[auth_user.email],
                    fail_silently=True,
                )
            except Exception:
                pass  # Email failure should not break the task

        elif rate < 80:
            # Warning only
            Notification.objects.create(
                user=auth_user,
                message=f"Warning: Your attendance is {rate:.1f}%. Minimum required is 80%.",
                notif_type='warning'
            )


def start_scheduler():
    """Start the APScheduler background scheduler with all registered tasks."""
    scheduler = BackgroundScheduler()

    scheduler.add_job(
        update_classroom_status,
        trigger=IntervalTrigger(minutes=1),
        id='update_classroom_status',
        name='Release busy classrooms when schedule ends',
        replace_existing=True,
    )

    scheduler.add_job(
        check_attendance_compliance,
        trigger=IntervalTrigger(hours=24),
        id='check_attendance_compliance',
        name='Daily attendance compliance alerts',
        replace_existing=True,
    )

    scheduler.start()
