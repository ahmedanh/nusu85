"""
0023_sqlite_compat_columns
~~~~~~~~~~~~~~~~~~~~~~~~~~
Adds columns that exist in the Django model but were never migrated to SQLite
because the original migrations relied on PostgreSQL-specific extensions
(pgvector, pg_trgm) or RunSQL statements that only ran on PostgreSQL.

Safe to run on PostgreSQL too — uses IF NOT EXISTS where possible via RunPython.
"""
from django.db import migrations


SQLITE_COLUMNS = [
    # table, column, sql_type, nullable
    ('attendance_college',    'name',          'VARCHAR(200)',  True),
    # Department has a created_at from an old migration — give it a default
    ('attendance_department', 'college_id',    'INTEGER',       True),
    ('attendance_teacher',    'college_id',    'INTEGER',       True),
    ('attendance_teacher',    'university_email', 'VARCHAR(200)', True),
    ('attendance_teacher',    'phone_number',  'VARCHAR(20)',   True),
    ('attendance_teacher',    'auth_user_id',  'INTEGER',       True),
    ('attendance_student',    'college_id',    'INTEGER',       True),
    ('attendance_student',    'year_of_study', 'INTEGER',       True),
    ('attendance_student',    'attendance_percentage', 'REAL',  True),
    ('attendance_student',    'auth_user_id',  'INTEGER',       True),
    ('attendance_course',     'college_id',    'INTEGER',       True),
    ('attendance_course',     'credit_hours',  'INTEGER',       True),
    ('attendance_aiattendancelog', 'session_id', 'INTEGER',     True),
    ('attendance_aiattendancelog', 'method',    'VARCHAR(20)',   True),
    ('attendance_aiattendancelog', 'is_manual', 'INTEGER',      True),
    ('attendance_lecturesession',  'duration_minutes', 'INTEGER', True),
    ('attendance_lecturesession',  'actual_end_time', 'DATETIME', True),
    ('attendance_lecturesession',  'opened_by_id', 'INTEGER',   True),
    ('attendance_camerasource',    'is_gate',   'INTEGER',      True),
    ('attendance_notification',    'title',     'VARCHAR(200)', True),
    ('attendance_notification',    'body',      'TEXT',         True),
    ('attendance_notification',    'level',     'VARCHAR(20)',  True),
]

MISSING_TABLES = {
    'attendance_supportticket': '''
        CREATE TABLE IF NOT EXISTS attendance_supportticket (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            subject TEXT NOT NULL DEFAULT "",
            body TEXT NOT NULL DEFAULT "",
            status VARCHAR(20) NOT NULL DEFAULT "open",
            priority VARCHAR(10) NOT NULL DEFAULT "medium",
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            admin_reply TEXT DEFAULT ""
        )
    ''',
    'attendance_grade': '''
        CREATE TABLE IF NOT EXISTS attendance_grade (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            course_id INTEGER,
            score REAL DEFAULT 0,
            grade VARCHAR(5) DEFAULT "",
            semester VARCHAR(20) DEFAULT "",
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''',
    'attendance_auditlog': '''
        CREATE TABLE IF NOT EXISTS attendance_auditlog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action VARCHAR(50) DEFAULT "",
            target_model VARCHAR(100) DEFAULT "",
            target_id INTEGER DEFAULT 0,
            description TEXT DEFAULT "",
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address VARCHAR(45) DEFAULT ""
        )
    ''',
    'attendance_systemconfig': '''
        CREATE TABLE IF NOT EXISTS attendance_systemconfig (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) UNIQUE NOT NULL DEFAULT "",
            value TEXT DEFAULT "",
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''',
}


def add_sqlite_columns(apps, schema_editor):
    if schema_editor.connection.vendor != 'sqlite':
        return

    import sqlite3 as _sqlite3
    db_path = schema_editor.connection.settings_dict['NAME']
    conn = _sqlite3.connect(str(db_path))
    conn.execute('PRAGMA foreign_keys=OFF')

    # Fix Department.created_at — it has NOT NULL but no default in old migration
    try:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS attendance_department_fix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL DEFAULT "",
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                college_id INTEGER
            );
            INSERT OR IGNORE INTO attendance_department_fix(id,name,created_at,college_id)
                SELECT id,name,COALESCE(created_at,CURRENT_TIMESTAMP),college_id
                FROM attendance_department;
            DROP TABLE attendance_department;
            ALTER TABLE attendance_department_fix RENAME TO attendance_department;
        ''')
    except Exception:
        pass  # already fixed or table doesn't exist yet

    # Create missing tables
    for _table, sql in MISSING_TABLES.items():
        conn.execute(sql)

    # Add missing columns
    for table, col, dtype, nullable in SQLITE_COLUMNS:
        existing = {r[1] for r in conn.execute(f'PRAGMA table_info({table})').fetchall()}
        if col not in existing:
            null_clause = '' if nullable else 'NOT NULL'
            default_clause = 'DEFAULT NULL' if nullable else 'DEFAULT 0'
            try:
                conn.execute(f'ALTER TABLE {table} ADD COLUMN {col} {dtype} {null_clause} {default_clause}')
            except Exception:
                pass  # already exists or table doesn't exist

    conn.commit()
    conn.close()


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0022_classroom_college_userprofile'),
    ]

    operations = [
        migrations.RunPython(add_sqlite_columns, migrations.RunPython.noop),
    ]
