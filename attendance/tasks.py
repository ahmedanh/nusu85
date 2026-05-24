from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from django.conf import settings


def update_classroom_status():
    """Every minute: auto-update classroom busy/free status based on schedule."""
    from .models import Schedule, Classroom, LectureSession
    now = timezone.now()
    current_time = now.time()
    current_day = now.strftime('%A')

    for room in Classroom.objects.filter(is_busy=True):
        active = Schedule.objects.filter(
            classroom=room, day_of_week=current_day,
            start_time__lte=current_time, end_time__gte=current_time
        ).exists()
        if not active:
            room.is_busy = False
            room.is_occupied = False
            room.save(update_fields=['is_busy', 'is_occupied'])
            LectureSession.objects.filter(
                schedule__classroom=room, is_active=True
            ).update(is_active=False, actual_end_time=now)


def sync_offline_cache():
    """Every 2 minutes: push offline attendance records to PostgreSQL."""
    import sqlite3, os
    from .models import AIAttendanceLog, Student, Schedule
    cache_path = os.path.join(settings.BASE_DIR, 'edge_cache.db')
    if not os.path.exists(cache_path):
        return
    try:
        conn = sqlite3.connect(cache_path)
        rows = conn.execute(
            "SELECT id,student_name,schedule_id,confidence,status,timestamp "
            "FROM offline_attendance WHERE synced=0"
        ).fetchall()
        synced = []
        for row in rows:
            student = Student.objects.filter(name__icontains=row[1]).first()
            schedule = Schedule.objects.filter(id=row[2]).first()
            if student and schedule:
                AIAttendanceLog.objects.get_or_create(
                    student=student, schedule=schedule, timestamp=row[5],
                    defaults={'confidence_score': row[3], 'status': row[4]}
                )
                synced.append(row[0])
        if synced:
            conn.execute(
                f"UPDATE offline_attendance SET synced=1 WHERE id IN ({','.join(['?']*len(synced))})",
                synced
            )
            conn.commit()
        conn.close()
    except Exception:
        pass


def check_attendance_compliance():
    """Daily at 8am: check 75% threshold, send in-app + email alerts per FR-06."""
    from django.core.mail import send_mail
    from .models import Student, AIAttendanceLog, Notification, UserProfile, Schedule, Course
    from django.contrib.auth.models import User
    from collections import defaultdict

    admin_users = list(User.objects.filter(is_staff=True))
    students    = Student.objects.filter(auth_user__isnull=False).select_related('auth_user')

    for student in students:
        logs = AIAttendanceLog.objects.filter(student=student).select_related('schedule__course')
        total = logs.count()
        if total == 0:
            continue
        present = logs.filter(status='Present').count()
        pct = (present / total) * 100

        if pct < 75:
            level = 'error'
        elif pct < 80:
            level = 'warning'
        else:
            continue

        # -- In-app notification for admins --
        admin_msg = f"{student.name}: نسبة حضور {pct:.1f}% ({'أقل من الحد' if pct < 75 else 'تحذير'})"
        for admin in admin_users:
            Notification.objects.create(user=admin, message=admin_msg, notif_type=level)

        # -- In-app notification for student themselves --
        if student.auth_user:
            # get user profile to check if attendance_alerts enabled
            prof, _ = UserProfile.objects.get_or_create(user=student.auth_user)
            if prof.attendance_alerts:
                Notification.objects.create(
                    user=student.auth_user,
                    message=f"تحذير: نسبة حضورك الإجمالية {pct:.1f}% — الحد الأدنى المطلوب 75%",
                    notif_type='warning',
                    link='/attendance/student/dashboard/',
                )

                # Per-course breakdown
                course_buckets = defaultdict(lambda: {'present': 0, 'total': 0, 'name': ''})
                for log in logs:
                    cname = log.schedule.course.title if (log.schedule and log.schedule.course) else 'غير محدد'
                    course_buckets[cname]['name']  = cname
                    course_buckets[cname]['total'] += 1
                    if log.status == 'Present':
                        course_buckets[cname]['present'] += 1

                for cname, data in course_buckets.items():
                    cpct = (data['present'] / data['total'] * 100) if data['total'] else 0
                    if cpct < 75:
                        Notification.objects.create(
                            user=student.auth_user,
                            message=f"تحذير: نسبة حضورك في مادة {cname} هي {cpct:.1f}% — الحد الأدنى 75%",
                            notif_type='warning',
                            link='/attendance/student/dashboard/',
                        )

        # -- Email (only if profile.email_notifications) --
        if student.auth_user and student.university_email:
            try:
                prof, _ = UserProfile.objects.get_or_create(user=student.auth_user)
                if prof.email_notifications:
                    subject = f'ACDC: نسبة حضور {student.name} {pct:.1f}%'
                    send_mail(
                        subject,
                        f"عزيزي {student.name}،\n\nنسبة حضورك الحالية {pct:.1f}%.\n"
                        f"الحد الأدنى المطلوب 75%.\n\nنظام SHAMEL",
                        getattr(settings, 'EMAIL_HOST_USER', 'noreply@acdc.edu'),
                        [student.university_email],
                        fail_silently=True,
                    )
            except Exception:
                pass


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_classroom_status, IntervalTrigger(minutes=1),
                      id='classroom_status', replace_existing=True)
    scheduler.add_job(sync_offline_cache, IntervalTrigger(minutes=2),
                      id='offline_sync', replace_existing=True)
    scheduler.add_job(check_attendance_compliance, CronTrigger(hour=8, minute=0),
                      id='attendance_compliance', replace_existing=True)
    scheduler.start()
