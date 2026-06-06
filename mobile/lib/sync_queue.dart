import 'dart:async';
import 'dart:convert';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'local_db.dart';
import 'api.dart';

/// Watches connectivity and syncs pending offline attendance records
/// to the server whenever the network becomes available.
///
/// Usage — call once at app start:
///   SyncQueue.start();
///
/// To manually trigger (e.g. after manual entry):
///   SyncQueue.syncNow();
class SyncQueue {
  SyncQueue._();

  static StreamSubscription? _sub;
  static bool _running = false;

  static void start() {
    _sub?.cancel();
    _sub = Connectivity().onConnectivityChanged.listen((results) {
      final hasNet = results.any((r) => r != ConnectivityResult.none);
      if (hasNet) syncNow();
    });
    // Also try immediately on start
    syncNow();
  }

  static void stop() {
    _sub?.cancel();
    _sub = null;
  }

  /// Push all pending records. Idempotent — server uses get_or_create.
  static Future<SyncResult> syncNow() async {
    if (_running) return SyncResult(0, 0);
    _running = true;
    try {
      final pending = await LocalDb.pendingRecords();
      if (pending.isEmpty) return SyncResult(0, 0);

      // Check reachability
      final alive = await Api.ping();
      if (!alive) return SyncResult(0, pending.length);

      // Build payload
      final records = pending.map((r) => {
        'session_id': r['session_id'],
        'student_id': r['student_id'],
        'status': r['status'],
        'method': r['method'],
        'timestamp': r['timestamp'],
      }).toList();

      final res = await Api.postJson(
        '/api/v1/lecture-attendance/sync',
        {'records': records},
      );

      if (res['ok'] == true) {
        final ids = pending.map((r) => r['id'] as int).toList();
        await LocalDb.markSynced(ids);
        return SyncResult(res['saved'] as int? ?? 0, res['skipped'] as int? ?? 0);
      }
      return SyncResult(0, pending.length);
    } catch (_) {
      return SyncResult(0, 0);
    } finally {
      _running = false;
    }
  }
}

class SyncResult {
  final int saved;
  final int skipped;
  const SyncResult(this.saved, this.skipped);
}
