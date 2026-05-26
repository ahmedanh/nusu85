# -*- coding: utf-8 -*-
"""
SHAMEL Email Utilities — no-reply email helpers for all roles.
All sending is fail_silently=True so email failures never crash the app.
"""

from django.core.mail import EmailMessage
from django.conf import settings

NOREPLY = 'SHAMEL System <noreply@shamel.edu.sd>'

BRAND_COLOR   = '#0B2545'
ACCENT_COLOR  = '#C9A227'

_BASE_HTML = """
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
<meta charset="UTF-8"/>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; direction: rtl; }}
  .wrapper {{ max-width: 600px; margin: 30px auto; background: #fff; border-radius: 12px;
              box-shadow: 0 2px 16px rgba(11,37,69,.10); overflow: hidden; }}
  .header {{ background: {brand}; padding: 28px 32px 20px; text-align: center; }}
  .header h1 {{ color: {accent}; font-size: 22px; margin: 0 0 4px; letter-spacing: .5px; }}
  .header p  {{ color: #a8bcd6; font-size: 12px; margin: 0; }}
  .body  {{ padding: 28px 32px; color: #222; line-height: 1.7; font-size: 15px; }}
  .body h2 {{ color: {brand}; font-size: 17px; margin-bottom: 8px; }}
  .highlight {{ background: #f0f4fa; border-right: 4px solid {accent}; padding: 12px 16px;
                border-radius: 6px; margin: 16px 0; font-size: 14px; }}
  .btn {{ display: inline-block; background: {brand}; color: #fff; padding: 10px 24px;
          border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 16px; }}
  .footer {{ background: #f0f4fa; padding: 14px 32px; font-size: 11px; color: #888; text-align: center; }}
</style>
</head>
<body>
<div class="wrapper">
  <div class="header">
    <h1>&#x1F393; نظام SHAMEL</h1>
    <p>منظومة إدارة الحضور الذكي — الجامعة</p>
  </div>
  <div class="body">
    {content}
  </div>
  <div class="footer">
    هذا البريد مُرسَل تلقائيًا من نظام SHAMEL — لا تردّ على هذه الرسالة.<br/>
    SHAMEL Attendance System &copy; 2025 — noreply@shamel.edu.sd
  </div>
</div>
</body>
</html>
""".format(brand=BRAND_COLOR, accent=ACCENT_COLOR, content='{content}')


def _render_email(content_html):
    return _BASE_HTML.replace('{content}', content_html)


def send_system_email(to_email, subject, html_body, attachments=None):
    """Send a styled no-reply HTML email. Returns True on success."""
    if not to_email:
        return False
    try:
        msg = EmailMessage(
            subject=f'[SHAMEL] {subject}',
            body=html_body,
            from_email=NOREPLY,
            to=[to_email],
        )
        msg.content_subtype = 'html'
        if attachments:
            for name, data, mime in attachments:
                msg.attach(name, data, mime)
        msg.send(fail_silently=True)
        return True
    except Exception:
        return False


# ── Role-specific helpers ────────────────────────────────────────────────────

def notify_teacher_assignment(teacher, schedule):
    """Email teacher when assigned to a course schedule."""
    if not getattr(teacher, 'email', None):
        return False
    day_ar = {
        'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الاثنين',
        'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء',
        'Thursday': 'الخميس', 'Friday': 'الجمعة',
    }.get(schedule.day_of_week, schedule.day_of_week)

    course_title = schedule.course.title if schedule.course else '—'
    start = schedule.start_time.strftime('%I:%M %p') if schedule.start_time else '—'
    end   = schedule.end_time.strftime('%I:%M %p') if schedule.end_time else '—'

    content = f"""
    <h2>تم تعيينك في مادة جديدة</h2>
    <p>أستاذنا الكريم <strong>{teacher.name}</strong>،</p>
    <p>يسعدنا إبلاغك بأنه تم تعيينك للتدريس في الحصة الدراسية التالية:</p>
    <div class="highlight">
      <strong>المادة:</strong> {course_title}<br/>
      <strong>اليوم:</strong> {day_ar}<br/>
      <strong>الوقت:</strong> {start} – {end}<br/>
      <strong>الفصل الدراسي:</strong> {schedule.semester or '—'}
    </div>
    <p>يرجى الاطلاع على الجدول الدراسي الكامل عبر بوابة SHAMEL.</p>
    """
    return send_system_email(
        teacher.email,
        f'تعيين جديد — {course_title}',
        _render_email(content),
    )


def notify_student_attendance_warning(student, pct):
    """Email student when attendance is approaching or below 75%."""
    if not getattr(student, 'email', None):
        return False
    level = 'تحذير حضور' if pct >= 75 else 'إنذار حضور — دون الحد المسموح'
    color = '#e67e22' if pct >= 75 else '#e74c3c'
    content = f"""
    <h2>{level}</h2>
    <p>الطالب/ة العزيز/ة <strong>{student.name}</strong>،</p>
    <p>نودّ تنبيهك إلى أن نسبة حضورك الحالية:</p>
    <div class="highlight" style="border-color:{color};">
      <strong>نسبة الحضور:</strong> <span style="color:{color};font-size:20px;font-weight:bold;">{pct:.1f}%</span>
    </div>
    <p>
      {'الحد الأدنى المطلوب للحضور هو <strong>75%</strong>. نسبتك تقترب من هذا الحد — يُرجى الانتظام في الحضور.' if pct >= 75
       else 'نسبة حضورك دون الحد المسموح به (<strong>75%</strong>). قد يؤثر ذلك على أهليتك للامتحانات. تواصل مع المنسق فورًا.'}
    </p>
    """
    return send_system_email(
        student.email,
        level,
        _render_email(content),
    )


def notify_student_ineligible(student):
    """Email student when they become ineligible for entry."""
    if not getattr(student, 'email', None):
        return False
    content = f"""
    <h2>تنبيه: تم إيقاف أهليتك للدخول</h2>
    <p>الطالب/ة <strong>{student.name}</strong>،</p>
    <p>نُعلمك بأنه <strong>تم إيقاف أهليتك للدخول إلى الحرم الجامعي</strong> في نظام SHAMEL.</p>
    <div class="highlight" style="border-color:#e74c3c;">
      <strong>الرمز الطلابي:</strong> {getattr(student, 'student_code', '—')}<br/>
      <strong>الكلية:</strong> {student.college.college_name if student.college else '—'}
    </div>
    <p>للاستفسار أو تقديم طلب مراجعة، يرجى التواصل مع منسق كليتك.</p>
    """
    return send_system_email(
        student.email,
        'إيقاف أهلية الدخول',
        _render_email(content),
    )


def notify_admin_new_report(admin_email, report_name, generated_by):
    """Email admin when a report is exported."""
    if not admin_email:
        return False
    from django.utils import timezone as tz
    now = tz.now().strftime('%Y-%m-%d %H:%M')
    content = f"""
    <h2>تقرير جديد تم إنشاؤه</h2>
    <p>تم إنشاء التقرير التالي وتصديره من نظام SHAMEL:</p>
    <div class="highlight">
      <strong>اسم التقرير:</strong> {report_name}<br/>
      <strong>أُنشئ بواسطة:</strong> {generated_by}<br/>
      <strong>الوقت:</strong> {now}
    </div>
    <p>يمكنك الاطلاع على التقرير عبر بوابة SHAMEL.</p>
    """
    return send_system_email(
        admin_email,
        f'تقرير جديد — {report_name}',
        _render_email(content),
    )


def notify_coordinator_new_report(coordinator_email, report_name, generated_by):
    """Email coordinator when a report is exported."""
    return notify_admin_new_report(coordinator_email, report_name, generated_by)
