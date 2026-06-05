"""
0024_fix_schedule_nullable_fields

Reconciles attendance_schedule DB state with the Django model:
  1. teacher_id: make nullable (model says null=True, DB had NOT NULL)
  2. total_lectures_required: add to model state (column already in DB from raw SQL)

Safe on PostgreSQL and SQLite.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0023_sqlite_compat_columns'),
    ]

    operations = [
        # 1. Make teacher nullable — matches model FK(null=True, blank=True)
        migrations.AlterField(
            model_name='schedule',
            name='teacher',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='attendance.teacher',
            ),
        ),
        # 2. Register total_lectures_required in migration state.
        #    Column already exists on PostgreSQL (added via raw SQL).
        #    Use SeparateDatabaseAndState so Django's state knows about the
        #    field without trying to re-create the column.
        migrations.SeparateDatabaseAndState(
            database_operations=[],   # no-op: column already exists
            state_operations=[
                migrations.AddField(
                    model_name='schedule',
                    name='total_lectures_required',
                    field=models.IntegerField(default=28),
                    preserve_default=True,
                ),
            ],
        ),
    ]
