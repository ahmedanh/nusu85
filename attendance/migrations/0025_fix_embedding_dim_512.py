from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0024_fix_schedule_nullable_fields'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE attendance_studentfaceembedding ALTER COLUMN embedding TYPE vector(512) USING embedding::text::vector(512);",
                "ALTER TABLE attendance_teacherfaceembedding ALTER COLUMN face_vector TYPE vector(512) USING face_vector::text::vector(512);",
            ],
            reverse_sql=[
                "ALTER TABLE attendance_studentfaceembedding ALTER COLUMN embedding TYPE vector(384) USING embedding::text::vector(384);",
                "ALTER TABLE attendance_teacherfaceembedding ALTER COLUMN face_vector TYPE vector(384) USING face_vector::text::vector(384);",
            ],
        ),
    ]
