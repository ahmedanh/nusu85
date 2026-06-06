from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0026_qa_indexes_constraints'),
    ]

    operations = [
        # Index on session FK — speeds up all lecture_scan queries
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['session'], name='attendance_session_idx'),
        ),
        migrations.AddIndex(
            model_name='aiattendancelog',
            index=models.Index(fields=['session', 'status'], name='attendance_session_status_idx'),
        ),
        # Unique: one record per student per session (prevents duplicate on manual re-submit)
        migrations.AddConstraint(
            model_name='aiattendancelog',
            constraint=models.UniqueConstraint(
                fields=['student', 'session'],
                condition=models.Q(session__isnull=False),
                name='unique_student_per_session',
            ),
        ),
    ]
