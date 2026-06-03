"""
0017_hnsw_trgm_indexes
~~~~~~~~~~~~~~~~~~~~~~
Creates HNSW vector similarity indexes and pg_trgm GIN indexes.
PostgreSQL-only — silently skipped on SQLite.
"""
from django.db import migrations


def run_pg_only(sql):
    """Return a RunPython operation that executes raw SQL only on PostgreSQL."""
    def forward(apps, schema_editor):
        if schema_editor.connection.vendor != 'postgresql':
            return
        schema_editor.execute(sql)
    return migrations.RunPython(forward, migrations.RunPython.noop)


class Migration(migrations.Migration):

    dependencies = [
        ("attendance", "0016_phase7_and_indexes"),
    ]

    operations = [
        run_pg_only("CREATE EXTENSION IF NOT EXISTS pg_trgm;"),
        run_pg_only("""
            CREATE INDEX IF NOT EXISTS student_embedding_hnsw_idx
              ON attendance_studentfaceembedding
              USING hnsw (embedding vector_l2_ops);
        """),
        run_pg_only("""
            CREATE INDEX IF NOT EXISTS teacher_embedding_hnsw_idx
              ON attendance_teacherfaceembedding
              USING hnsw (face_vector vector_l2_ops);
        """),
        run_pg_only("""
            CREATE INDEX IF NOT EXISTS student_name_trgm_idx
              ON attendance_student
              USING gin (name gin_trgm_ops);
        """),
    ]
