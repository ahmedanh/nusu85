"""Simulate a school day — run with: python simulate_day.py"""
import os, sys, django, datetime, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'acdc_config.settings')
django.setup()

from django.db import connection
from attendance.models import Schedule, Course, Teacher

today_en = datetime.datetime.now().strftime('%A')
now      = datetime.datetime.now().time()
print(f'Today: {today_en}   Now: {now}')

# ── Ensure classrooms exist ───────────────────────────────────────────────────
room_data = [
    ('قاعة A-101', 50, 'Lecture'), ('قاعة A-102', 40, 'Lecture'),
    ('قاعة A-201', 60, 'Lecture'), ('قاعة B-101', 35, 'Lecture'),
    ('قاعة B-102', 45, 'Lecture'), ('قاعة B-201', 55, 'Lecture'),
    ('قاعة C-101', 30, 'Lecture'), ('قاعة C-202', 70, 'Lecture'),
    ('مختبر الحاسوب', 25, 'Lab'), ('مختبر الكيمياء', 20, 'Lab'),
    ('القاعة الكبرى', 120, 'Lecture'), ('قاعة D-101', 40, 'Lecture'),
]

with connection.cursor() as cur:
    for rname, cap, rtype in room_data:
        try:
            cur.execute(
                "INSERT INTO attendance_classroom"
                " (name, location, capacity, is_occupied, is_busy, classroom_type)"
                " SELECT %s, %s, %s, false, false, %s"
                " WHERE NOT EXISTS (SELECT 1 FROM attendance_classroom WHERE name=%s)",
                [rname, 'المبنى الرئيسي', cap, rtype, rname]
            )
        except Exception as e:
            print('  Room error:', rname, e)

    cur.execute("SELECT id, name FROM attendance_classroom ORDER BY id")
    rooms = cur.fetchall()

print(f'Rooms in DB: {len(rooms)}')

teachers = list(Teacher.objects.all()[:15])
courses  = list(Course.objects.all()[:30])
if not teachers or not courses:
    print('ERROR: No teachers/courses')
    sys.exit(1)

# ── Build time slots — include current hour so rooms show as busy NOW ─────────
now_h = datetime.datetime.now().hour
now_m = datetime.datetime.now().minute

def hm(h, m=0):
    return datetime.time(h, m)

# Standard daily slots
slots = [
    (hm(8),  hm(10)),
    (hm(10), hm(12)),
    (hm(12,30), hm(14,30)),
    (hm(14,30), hm(16,30)),
    (hm(16,30), hm(18)),
]
# Add a slot that covers NOW so some rooms show busy
current_slot = (hm(now_h - 1 if now_h > 0 else 0), hm(now_h + 1 if now_h < 23 else 23, 59))
slots.append(current_slot)

# ── Delete today's existing schedules ─────────────────────────────────────────
room_ids = [r[0] for r in rooms]
with connection.cursor() as cur:
    for rid in room_ids:
        cur.execute(
            "DELETE FROM attendance_schedule WHERE day_of_week=%s AND classroom_id=%s",
            [today_en, rid]
        )
print('Cleared old schedules')

# ── Insert new schedules ──────────────────────────────────────────────────────
created = 0
for i, (rid, rname) in enumerate(rooms):
    n_slots = random.randint(3, 5)
    chosen  = random.sample(slots, k=min(n_slots, len(slots)))
    # Make 70% of rooms have the current slot (so they appear busy now)
    if i % 10 < 7 and current_slot not in chosen:
        if len(chosen) >= n_slots:
            chosen[-1] = current_slot
        else:
            chosen.append(current_slot)
    for start_t, end_t in chosen:
        teacher = teachers[i % len(teachers)]
        course  = courses[(i * 3 + slots.index((start_t, end_t)) if (start_t, end_t) in slots else i*2) % len(courses)]
        try:
            with connection.cursor() as cur:
                cur.execute(
                    "INSERT INTO attendance_schedule"
                    " (day_of_week, start_time, end_time, classroom_id, course_id,"
                    "  teacher_id, batch, semester, total_lectures_required)"
                    " VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    [today_en, start_t, end_t, rid, course.id,
                     teacher.pk, '', '1', 28]
                )
            created += 1
        except Exception as e:
            print(f'  Sched err {rname}:', str(e)[:80])

print(f'Created {created} schedules')

# ── Count active now ──────────────────────────────────────────────────────────
with connection.cursor() as cur:
    cur.execute(
        "SELECT COUNT(*) FROM attendance_schedule"
        " WHERE day_of_week=%s AND start_time<=%s AND end_time>=%s",
        [today_en, now, now]
    )
    active_count = cur.fetchone()[0]

print(f'Active NOW: {active_count} of {len(rooms)} rooms busy  ✓')
print('Simulation complete!')
