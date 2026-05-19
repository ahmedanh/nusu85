import sqlite3
import os
from django.conf import settings

CACHE_PATH = os.path.join(settings.BASE_DIR, 'edge_cache.db')

def init_edge_cache():
    conn = sqlite3.connect(CACHE_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS offline_attendance
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         student_name TEXT, schedule_id INTEGER,
         confidence REAL, status TEXT,
         timestamp TEXT, synced INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def log_to_cache(student_name: str, schedule_id: int, confidence: float, status: str):
    try:
        init_edge_cache()
        from datetime import datetime
        conn = sqlite3.connect(CACHE_PATH)
        conn.execute(
            "INSERT INTO offline_attendance (student_name,schedule_id,confidence,status,timestamp) VALUES (?,?,?,?,?)",
            (student_name, schedule_id, confidence, status, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def is_server_reachable() -> bool:
    try:
        from django.db import connection
        connection.ensure_connection()
        return True
    except Exception:
        return False
