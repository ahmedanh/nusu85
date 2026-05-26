import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'acdc_config.settings'
django.setup()

from django.db import connection

sql = """
CREATE TABLE IF NOT EXISTS attendance_gatelog (
    id SERIAL PRIMARY KEY,
    person_name VARCHAR(200) NOT NULL DEFAULT '',
    status VARCHAR(10) NOT NULL DEFAULT 'Unknown',
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    student_id INTEGER,
    teacher_id INTEGER,
    camera_id INTEGER,
    snapshot VARCHAR(100)
);
"""
with connection.cursor() as c:
    c.execute(sql)
print("attendance_gatelog table created or already exists.")
