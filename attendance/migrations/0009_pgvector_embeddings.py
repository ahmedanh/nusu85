from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [('attendance', '0008_teacher_user_nullable')]

    operations = [
        migrations.RunSQL(
            "CREATE EXTENSION IF NOT EXISTS vector;",
            "DROP EXTENSION IF EXISTS vector;",
        ),
        migrations.RunSQL(
            "ALTER TABLE attendance_studentfaceembedding ALTER COLUMN embedding TYPE vector(384) USING embedding::vector(384);",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "ALTER TABLE attendance_teacherfaceembedding ALTER COLUMN face_vector TYPE vector(384) USING face_vector::vector(384);",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS student_embedding_hnsw ON attendance_studentfaceembedding USING hnsw (embedding vector_l2_ops);",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS teacher_embedding_hnsw ON attendance_teacherfaceembedding USING hnsw (face_vector vector_l2_ops);",
            migrations.RunSQL.noop,
        ),
    ]
