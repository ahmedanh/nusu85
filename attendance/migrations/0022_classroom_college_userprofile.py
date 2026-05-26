from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0021_merge_0018_systemconfig_0020_performance_indexes_v2'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # Add college FK to Classroom (safe — column doesn't exist yet)
        migrations.AddField(
            model_name='classroom',
            name='college',
            field=models.ForeignKey(
                blank=True,
                help_text='اترك فارغاً للقاعات المشتركة بين الكليات',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='attendance.college',
            ),
        ),
        # Register UserProfile in Django's migration state (table already exists on VPS)
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='UserProfile',
                    fields=[
                        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                        ('show_phone_to_peers', models.BooleanField(default=True)),
                        ('show_email_to_peers', models.BooleanField(default=True)),
                        ('show_attendance_to_coordinator', models.BooleanField(default=True)),
                        ('email_notifications', models.BooleanField(default=True)),
                        ('attendance_alerts', models.BooleanField(default=True)),
                        ('ticket_updates', models.BooleanField(default=True)),
                        ('weekly_summary', models.BooleanField(default=False)),
                        ('require_face_login', models.BooleanField(default=False)),
                        ('last_password_change', models.DateTimeField(blank=True, null=True)),
                        ('user', models.OneToOneField(
                            on_delete=django.db.models.deletion.CASCADE,
                            related_name='profile',
                            to=settings.AUTH_USER_MODEL,
                        )),
                    ],
                    options={
                        'db_table': 'attendance_userprofile',
                    },
                ),
            ],
            database_operations=[],  # Table already exists — skip DB creation
        ),
    ]
