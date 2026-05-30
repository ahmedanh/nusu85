import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'acdc_config.settings'
django.setup()
from django.db import connection
with connection.cursor() as c:
    c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='attendance_userprofile' ORDER BY ordinal_position")
    for row in c.fetchall():
        print(row)
print("---classroom---")
with connection.cursor() as c:
    c.execute("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='attendance_classroom' ORDER BY ordinal_position")
    for row in c.fetchall():
        print(row)
