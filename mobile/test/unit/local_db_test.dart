import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:shamel/local_db.dart';

void main() {
  setUpAll(() {
    // Use in-memory FFI database for tests (no Android device needed).
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  tearDown(() async {
    // Reset singleton so each test starts fresh.
    LocalDb.resetForTest();
  });

  group('LocalDb — attendance queue', () {
    test('enqueue increases pendingCount', () async {
      expect(await LocalDb.pendingCount(), 0);
      await LocalDb.enqueue(sessionId: 1, studentId: 42);
      expect(await LocalDb.pendingCount(), 1);
    });

    test('markSynced reduces pendingCount', () async {
      final id = await LocalDb.enqueue(sessionId: 1, studentId: 10);
      expect(await LocalDb.pendingCount(), 1);
      await LocalDb.markSynced([id]);
      expect(await LocalDb.pendingCount(), 0);
    });

    test('pendingRecords returns unsynced only', () async {
      await LocalDb.enqueue(sessionId: 1, studentId: 1);
      await LocalDb.enqueue(sessionId: 1, studentId: 2);
      final pending = await LocalDb.pendingRecords();
      expect(pending.length, 2);
      await LocalDb.markSynced([pending.first['id'] as int]);
      final still = await LocalDb.pendingRecords();
      expect(still.length, 1);
    });

    test('syncAll calls syncer with records then marks them synced', () async {
      await LocalDb.enqueue(sessionId: 5, studentId: 99, status: 'Late');
      final captured = <Map<String, dynamic>>[];
      await LocalDb.syncAll((records) async {
        captured.addAll(records.cast());
      });
      expect(captured.length, 1);
      expect(captured.first['student_id'], 99);
      expect(await LocalDb.pendingCount(), 0);
    });

    test('syncAll is no-op when queue empty', () async {
      var called = false;
      await LocalDb.syncAll((_) async { called = true; });
      expect(called, isFalse);
    });
  });

  group('LocalDb — KV cache', () {
    test('cacheSet and cacheGet round-trip', () async {
      await LocalDb.cacheSet('test_key', '{"ok":true}');
      final v = await LocalDb.cacheGet('test_key');
      expect(v, '{"ok":true}');
    });

    test('cacheGet returns null for unknown key', () async {
      final v = await LocalDb.cacheGet('nonexistent');
      expect(v, isNull);
    });

    test('cacheGet returns null for stale entry', () async {
      await LocalDb.cacheSet('stale', 'data');
      // Override: max age of 0 → always stale
      final v = await LocalDb.cacheGet('stale',
          maxAge: Duration.zero);
      expect(v, isNull);
    });

    test('cacheClear removes entry', () async {
      await LocalDb.cacheSet('del_me', 'value');
      await LocalDb.cacheClear('del_me');
      final v = await LocalDb.cacheGet('del_me');
      expect(v, isNull);
    });
  });
}
