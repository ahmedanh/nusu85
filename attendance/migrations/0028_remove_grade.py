from django.db import migrations


class Migration(migrations.Migration):
    """
    Grade table was created via raw SQL in 0023 (sqlite_compat_columns),
    so it never existed in Django's migration state. We drop it from the DB
    only, with no state change needed.
    """

    dependencies = [
        ('attendance', '0027_lecture_attendance_constraints'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS attendance_grade;",
            reverse_sql="",  # no rollback — feature removed intentionally
        ),
    ]
