"""
0017_hnsw_trgm_indexes
~~~~~~~~~~~~~~~~~~~~~~
Creates HNSW vector similarity indexes (for fast face-match queries) and a
pg_trgm GIN index on student names (for fast ILIKE / trigram searches).

These indexes cannot be expressed as Django Meta.indexes because they use
PostgreSQL-specific index methods (hnsw, gin with gin_trgm_ops) that the
ORM does not support natively.  We use RunSQL with reverse operations so
`migrate --run-syncdb` and `migrate zero` work correctly.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0016_phase7_and_indexes"),
    ]

    operations = [
        # Enable pg_trgm extension (safe to run if already installed)
        migrations.RunSQL(
            sql="CREATE EXTENSION IF NOT EXISTS pg_trgm;",
            reverse_sql="",   # do not drop the extension on rollback
        ),

        # HNSW index on student face embeddings (vector_l2_ops)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS student_embedding_hnsw_idx
              ON attendance_studentfaceembedding
              USING hnsw (embedding vector_l2_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS student_embedding_hnsw_idx;",
        ),

        # HNSW index on teacher face embeddings (vector_l2_ops)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS teacher_embedding_hnsw_idx
              ON attendance_teacherfaceembedding
              USING hnsw (face_vector vector_l2_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS teacher_embedding_hnsw_idx;",
        ),

        # GIN trigram index on student names (speeds up ILIKE / pg_trgm similarity)
        migrations.RunSQL(
            sql="""
            CREATE INDEX IF NOT EXISTS student_name_trgm_idx
              ON attendance_student
              USING gin (name gin_trgm_ops);
            """,
            reverse_sql="DROP INDEX IF EXISTS student_name_trgm_idx;",
        ),
    ]
