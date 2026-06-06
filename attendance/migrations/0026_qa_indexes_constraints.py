import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """
    QA audit fixes:
    - Registers session FK in ORM state (column exists via 0023 raw SQL)
    - DB indexes on AIAttendanceLog, GateLog, Notification
    - UniqueConstraint (partial) on AIAttendanceLog(student, schedule) where session is null
    - Adds 'Excused' as a valid status choice for AIAttendanceLog
    """

    dependencies = [
        ('attendance', '0025_fix_embedding_dim_512'),
    ]

    operations = [
        # Register session FK in ORM state — column already in DB via 0023 RunSQL
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.AddField(
                    model_name='aiattendancelog',
                    name='session',
                    field=models.ForeignKey(
                        'attendance.LectureSession',
                        blank=True, null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                    ),
                ),
            ],
            database_operations=[],  # column already exists
        ),

        # AIAttendanceLog: add Excused status
        migrations.AlterField(
            model_name='aiattendancelog',
            name='status',
            field=models.CharField(
                choices=[
                    ('Present', 'Present'),
                    ('Absent', 'Absent'),
                    ('Late', 'Late'),
                    ('Excused', 'Excused'),
                ],
                default='Present',
                max_length=10,
            ),
        ),

        # Indexes
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['timestamp'], name='ail_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['status'], name='ail_status_idx'),
        ),
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['student', 'status'], name='ail_student_status_idx'),
        ),
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['schedule', 'status'], name='ail_schedule_status_idx'),
        ),
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['student', 'timestamp'], name='ail_student_ts_idx'),
        ),

        # Partial unique constraint: student+schedule unique only when session is null
        migrations.AddConstraint(
            model_name='aiattendancelog',
            constraint=models.UniqueConstraint(
                condition=models.Q(session__isnull=True),
                fields=['student', 'schedule'],
                name='unique_student_schedule_nosession',
            ),
        ),

        # GateLog + Notification raw indexes
        migrations.RunSQL(
            sql=[
                "CREATE INDEX IF NOT EXISTS gatelog_ts_idx ON attendance_gatelog(timestamp);",
                "CREATE INDEX IF NOT EXISTS gatelog_status_idx ON attendance_gatelog(status);",
                "CREATE INDEX IF NOT EXISTS gatelog_student_ts_idx ON attendance_gatelog(student_id, timestamp);",
                "CREATE INDEX IF NOT EXISTS notif_user_read_idx ON attendance_notification(user_id, is_read);",
            ],
            reverse_sql=[
                "DROP INDEX IF EXISTS gatelog_ts_idx;",
                "DROP INDEX IF EXISTS gatelog_status_idx;",
                "DROP INDEX IF EXISTS gatelog_student_ts_idx;",
                "DROP INDEX IF EXISTS notif_user_read_idx;",
            ],
        ),
    ]
