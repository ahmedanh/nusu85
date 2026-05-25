import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'acdc_config.settings'
django.setup()
from django.db import connection
with connection.cursor() as cur:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='attendance_classroom' ORDER BY ordinal_position")
    print('Classroom cols:', [r[0] for r in cur.fetchall()])
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name='attendance_schedule' ORDER BY ordinal_position")
    print('Schedule cols:', [r[0] for r in cur.fetchall()])
