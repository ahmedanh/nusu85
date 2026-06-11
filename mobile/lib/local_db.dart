import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// SQLite local database for offline support.
/// Tables:
///   attendance_queue  — pending attendance records to sync
///   schedule_cache    — last-fetched teacher schedule (JSON blob)
///   session_cache     — last-fetched active session (JSON blob)
class LocalDb {
  static Database? _db;

  static Future<Database> get db async {
    _db ??= await _open();
    return _db!;
  }

  static Future<Database> _open() async {
    final path = join(await getDatabasesPath(), 'shamel_offline.db');
    return openDatabase(
      path,
      version: 1,
      onCreate: (db, _) async {
        await db.execute('''
          CREATE TABLE attendance_queue (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id  INTEGER NOT NULL,
            student_id  INTEGER NOT NULL,
            status      TEXT    NOT NULL DEFAULT 'Present',
            method      TEXT    NOT NULL DEFAULT 'manual',
            timestamp   TEXT    NOT NULL,
            synced      INTEGER NOT NULL DEFAULT 0
          )
        ''');
        await db.execute('''
          CREATE TABLE kv_cache (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            saved_at TEXT NOT NULL
          )
        ''');
      },
    );
  }

  // ── Attendance queue ────────────────────────────────────────────────

  static Future<int> enqueue({
    required int sessionId,
    required int studentId,
    String status = 'Present',
    String method = 'manual',
  }) async {
    final d = await db;
    return d.insert('attendance_queue', {
      'session_id': sessionId,
      'student_id': studentId,
      'status': status,
      'method': method,
      'timestamp': DateTime.now().toIso8601String(),
      'synced': 0,
    });
  }

  static Future<List<Map<String, dynamic>>> pendingRecords() async {
    final d = await db;
    return d.query('attendance_queue', where: 'synced = 0');
  }

  static Future<void> markSynced(List<int> ids) async {
    if (ids.isEmpty) return;
    final d = await db;
    final placeholders = ids.map((_) => '?').join(',');
    await d.rawUpdate(
      'UPDATE attendance_queue SET synced = 1 WHERE id IN ($placeholders)',
      ids,
    );
  }

  /// Calls [syncer] with all pending records, then marks them synced.
  static Future<void> syncAll(
      Future<dynamic> Function(List<Map<String, dynamic>> records) syncer) async {
    final records = await pendingRecords();
    if (records.isEmpty) return;
    await syncer(records);
    final ids = records.map((r) => r['id'] as int).toList();
    await markSynced(ids);
  }

  static Future<int> pendingCount() async {
    final d = await db;
    final r = await d.rawQuery(
        'SELECT COUNT(*) as c FROM attendance_queue WHERE synced = 0');
    return (r.first['c'] as int?) ?? 0;
  }

  // ── KV cache (schedule, active session JSON) ─────────────────────

  static Future<void> cacheSet(String key, String json) async {
    final d = await db;
    await d.insert(
      'kv_cache',
      {'key': key, 'value': json, 'saved_at': DateTime.now().toIso8601String()},
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  static Future<String?> cacheGet(String key,
      {Duration maxAge = const Duration(hours: 6)}) async {
    final d = await db;
    final rows = await d.query('kv_cache', where: 'key = ?', whereArgs: [key]);
    if (rows.isEmpty) return null;
    final savedAt = DateTime.tryParse(rows.first['saved_at'] as String? ?? '');
    if (savedAt != null &&
        DateTime.now().difference(savedAt) > maxAge) {
      return null; // stale
    }
    return rows.first['value'] as String?;
  }

  static Future<void> cacheClear(String key) async {
    final d = await db;
    await d.delete('kv_cache', where: 'key = ?', whereArgs: [key]);
  }
}
