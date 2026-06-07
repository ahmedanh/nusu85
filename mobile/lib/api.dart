import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'local_db.dart';

/// SHAMEL API client — talks to the Django /api/v1 JSON endpoints.
///
/// Base URL note:
///  - Android emulator reaches the host machine at 10.0.2.2
///  - A physical phone would use the LAN IP / public domain (shamel.sd)
class Api {
  // 10.0.2.2 = host loopback from the Android emulator.
  // Both Daphne (:9000) and the Django dev server (:8000) serve /api/v1.
  // The app auto-discovers whichever is reachable so testing never breaks
  // just because one server is down.
  static String baseUrl = 'https://shamel.sd';

  /// Candidate hosts tried in order during discovery.
  /// Production server is tried first — if internet is available it wins instantly.
  static const List<String> _candidates = [
    'https://shamel.sd',       // production — tried first, no local Django needed
    'http://10.0.2.2:9000',   // emulator → host Daphne (fallback)
    'http://10.0.2.2:8000',   // emulator → host Django dev server
    'http://127.0.0.1:9000',
    'http://127.0.0.1:8000',
  ];

  /// Probe candidate hosts and lock onto the first reachable one.
  /// Returns true if a server was found.
  static Future<bool> discover() async {
    for (final base in _candidates) {
      try {
        final r = await http
            .get(Uri.parse('$base/api/v1/health'))
            .timeout(const Duration(seconds: 3));
        if (r.statusCode == 200) {
          baseUrl = base;
          return true;
        }
      } catch (_) {
        // try next candidate
      }
    }
    return false;
  }

  static const _storage = FlutterSecureStorage();
  static String? _token;

  static Future<void> loadToken() async {
    _token = await _storage.read(key: 'shamel_token');
  }

  static Future<void> _saveToken(String t) async {
    _token = t;
    await _storage.write(key: 'shamel_token', value: t);
  }

  static Future<void> clearToken() async {
    _token = null;
    await _storage.delete(key: 'shamel_token');
  }

  static bool get isLoggedIn => _token != null;

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  static Uri _u(String path) => Uri.parse('$baseUrl$path');

  /// Returns {ok, user, token?} — throws ApiException on transport failure.
  static Future<Map<String, dynamic>> login(String username, String password) async {
    final r = await http
        .post(_u('/api/v1/auth/login'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'username': username, 'password': password}))
        .timeout(const Duration(seconds: 15));
    final data = jsonDecode(r.body) as Map<String, dynamic>;
    if (data['ok'] == true && data['token'] != null) {
      await _saveToken(data['token']);
    }
    return data;
  }

  static Future<Map<String, dynamic>> _get(String path) async {
    final r = await http.get(_u(path), headers: _headers).timeout(const Duration(seconds: 15));
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> _post(String path, Map body) async {
    final r = await http
        .post(_u(path), headers: _headers, body: jsonEncode(body))
        .timeout(const Duration(seconds: 30));
    return jsonDecode(r.body) as Map<String, dynamic>;
  }

  static Future<Map<String, dynamic>> me() => _get('/api/v1/me');
  static Future<Map<String, dynamic>> dashboard() => _get('/api/v1/dashboard');
  static Future<Map<String, dynamic>> schedule() => _get('/api/v1/schedule');
  static Future<Map<String, dynamic>> reportsSummary() => _get('/api/v1/reports/summary');
  static Future<Map<String, dynamic>> notifications() => _get('/api/v1/notifications');
  static Future<Map<String, dynamic>> markNotificationsRead() =>
      _post('/api/v1/notifications/read', {});

  /// Generic authenticated GET / POST for the extended section endpoints.
  static Future<Map<String, dynamic>> getJson(String path) => _get(path);
  static Future<Map<String, dynamic>> postJson(String path, Map body) => _post(path, body);

  /// Submit a base64 JPEG for face scan. Optional schedule_id to log attendance.
  static Future<Map<String, dynamic>> scan(String imageB64, {int? scheduleId}) =>
      _post('/api/v1/scan', {
        'image': imageB64,
        if (scheduleId != null) 'schedule_id': scheduleId,
      });

  /// Connectivity probe (server-reachable, not just navigator.onLine analogue).
  static Future<bool> ping() async {
    try {
      final r = await http.get(_u('/api/v1/health')).timeout(const Duration(seconds: 5));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Offline-aware lecture attendance ──────────────────────────────────────

  /// Returns active session + enrolled students.
  /// Falls back to cached data if server unreachable.
  static Future<Map<String, dynamic>> activeSession() async {
    try {
      final data = await _get('/api/v1/sessions/active');
      if (data['ok'] == true) {
        await LocalDb.cacheSet('active_session', jsonEncode(data));
      }
      return data;
    } catch (_) {
      final cached = await LocalDb.cacheGet('active_session');
      if (cached != null) {
        final data = jsonDecode(cached) as Map<String, dynamic>;
        data['from_cache'] = true;
        return data;
      }
      return {'ok': false, 'error': 'offline', 'session': null, 'enrolled': []};
    }
  }

  /// Mark a student present — online → direct API, offline → sqflite queue.
  /// Returns {'ok': true, 'queued': false} online or {'ok': true, 'queued': true} offline.
  static Future<Map<String, dynamic>> markAttendance({
    required int sessionId,
    required int studentId,
    String status = 'Present',
    String method = 'manual',
  }) async {
    final online = await ping();
    if (online) {
      try {
        return await postJson('/api/v1/lecture-attendance/sync', {
          'records': [{
            'session_id': sessionId,
            'student_id': studentId,
            'status': status,
            'method': method,
            'timestamp': DateTime.now().toIso8601String(),
          }],
        });
      } catch (_) {
        // fall through to queue
      }
    }
    // Offline — save locally
    await LocalDb.enqueue(
      sessionId: sessionId,
      studentId: studentId,
      status: status,
      method: method,
    );
    return {'ok': true, 'queued': true};
  }

  /// Cached teacher schedule — returns stale data if offline.
  static Future<Map<String, dynamic>> scheduleCached() async {
    try {
      final data = await _get('/api/v1/schedule');
      await LocalDb.cacheSet('schedule', jsonEncode(data));
      return data;
    } catch (_) {
      final cached = await LocalDb.cacheGet('schedule',
          maxAge: const Duration(days: 7));
      if (cached != null) {
        final data = jsonDecode(cached) as Map<String, dynamic>;
        data['from_cache'] = true;
        return data;
      }
      return {'ok': false, 'error': 'offline', 'schedule': []};
    }
  }
}
