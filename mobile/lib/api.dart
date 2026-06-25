import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'local_db.dart';

// ── Storage key constants (no magic strings) ─────────────────────────────────
abstract class _K {
  static const token       = 'shamel_token';
  static const schedule    = 'cache:schedule';
  static const session     = 'cache:active_session';
  static const attLogs     = 'cache:attendance_logs';
  static const userProfile = 'cache:user_profile';
}

// ── Typed exceptions ─────────────────────────────────────────────────────────
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  ApiException(this.message, {this.statusCode});
  @override String toString() => message;
}

class AuthException extends ApiException {
  AuthException([String msg = 'انتهت صلاحية الجلسة — يرجى تسجيل الدخول مجدداً'])
      : super(msg, statusCode: 401);
}

class PermissionException extends ApiException {
  PermissionException([String msg = 'ليس لديك صلاحية الوصول لهذا المورد'])
      : super(msg, statusCode: 403);
}

class NotFoundException extends ApiException {
  NotFoundException([String msg = 'البيانات المطلوبة غير موجودة'])
      : super(msg, statusCode: 404);
}

/// SHAMEL API client — talks to the Django /api/v1 JSON endpoints.
class Api {
  // ── Server discovery ────────────────────────────────────────────────────────
  static const _serverOverride = String.fromEnvironment('SHAMEL_SERVER');

  static String baseUrl = _serverOverride.isNotEmpty && _serverOverride != 'local'
      ? _serverOverride
      : 'https://shamel.sd';

  static List<String> get _candidates {
    if (_serverOverride == 'local') {
      return [
        'http://10.0.2.2:9000',
        'http://10.0.2.2:8000',
        'http://127.0.0.1:9000',
        'http://127.0.0.1:8000',
      ];
    }
    if (_serverOverride.isNotEmpty) return [_serverOverride];
    return [
      'https://shamel.sd',
      'http://10.0.2.2:9000',
      'http://10.0.2.2:8000',
      'http://127.0.0.1:9000',
      'http://127.0.0.1:8000',
    ];
  }

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
      } catch (_) {}
    }
    return false;
  }

  // ── Token / auth ─────────────────────────────────────────────────────────────
  static const _storage = FlutterSecureStorage();
  static String? _token;

  /// Called by AuthState on init so 401 responses trigger auto-logout everywhere.
  static void Function()? onUnauthorized;

  static Future<void> loadToken() async {
    _token = await _storage.read(key: _K.token);
  }

  static Future<void> _saveToken(String t) async {
    _token = t;
    await _storage.write(key: _K.token, value: t);
  }

  static Future<void> clearToken() async {
    _token = null;
    await _storage.delete(key: _K.token);
  }

  /// Public surface used by FaceLoginSheet after a successful face-login API call.
  static Future<void> saveTokenPublic(String t) => _saveToken(t);

  static bool get isLoggedIn => _token != null;

  static Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_token != null) 'Authorization': 'Bearer $_token',
      };

  static Uri _u(String path) => Uri.parse('$baseUrl$path');

  // ── Core HTTP helpers ─────────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> _handleResponse(http.Response r) async {
    switch (r.statusCode) {
      case 200:
      case 201:
        break;
      case 401:
        await clearToken();
        onUnauthorized?.call();
        throw AuthException();
      case 403:
        throw PermissionException();
      case 404:
        throw NotFoundException();
      case 500:
      case 502:
      case 503:
        throw ApiException('خطأ في الخادم (${r.statusCode}) — حاول مجدداً لاحقاً',
            statusCode: r.statusCode);
      default:
        throw ApiException('خطأ HTTP ${r.statusCode}', statusCode: r.statusCode);
    }
    try {
      return jsonDecode(r.body) as Map<String, dynamic>;
    } catch (_) {
      throw ApiException('استجابة غير صالحة من الخادم');
    }
  }

  static Future<Map<String, dynamic>> _get(String path) async {
    try {
      final r = await http
          .get(_u(path), headers: _headers)
          .timeout(const Duration(seconds: 15));
      return _handleResponse(r);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw ApiException('انتهت مهلة الطلب — تحقق من اتصالك بالإنترنت');
    } catch (e) {
      throw ApiException('تعذّر الاتصال بالخادم: ${e.toString()}');
    }
  }

  static Future<Map<String, dynamic>> _post(String path, Map body) async {
    try {
      final r = await http
          .post(_u(path), headers: _headers, body: jsonEncode(body))
          .timeout(const Duration(seconds: 30));
      return _handleResponse(r);
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw ApiException('انتهت مهلة الطلب — تحقق من اتصالك بالإنترنت');
    } catch (e) {
      throw ApiException('تعذّر الاتصال بالخادم: ${e.toString()}');
    }
  }

  // ── Auth endpoints ─────────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final r = await http
          .post(_u('/api/v1/auth/login'),
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode({'username': username.trim(), 'password': password}))
          .timeout(const Duration(seconds: 15));
      // Login 401 = bad credentials, not session expiry — handle separately
      if (r.statusCode == 401) {
        return {'ok': false, 'message': 'اسم المستخدم أو كلمة المرور غير صحيحة'};
      }
      final data = await _handleResponse(r);
      if (data['ok'] == true && data['token'] != null) {
        await _saveToken(data['token'] as String);
      }
      return data;
    } on ApiException {
      rethrow;
    } on TimeoutException {
      throw ApiException('انتهت مهلة تسجيل الدخول — تحقق من اتصالك');
    } catch (e) {
      throw ApiException('تعذّر الاتصال بالخادم');
    }
  }

  // ── Connectivity ──────────────────────────────────────────────────────────

  static Future<bool> ping() async {
    try {
      final r = await http
          .get(_u('/api/v1/health'))
          .timeout(const Duration(seconds: 3));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Standard endpoints ─────────────────────────────────────────────────────

  static Future<Map<String, dynamic>> me() async {
    final data = await _get('/api/v1/me');
    // Cache profile for offline bootstrap
    if (data['ok'] == true && data['user'] != null) {
      await LocalDb.cacheSet(_K.userProfile, jsonEncode(data['user']));
    }
    return data;
  }

  /// Returns cached user profile if offline, null if no cache.
  static Future<Map<String, dynamic>?> cachedProfile() async {
    final raw = await LocalDb.cacheGet(_K.userProfile,
        maxAge: const Duration(days: 30));
    if (raw == null) return null;
    try {
      return jsonDecode(raw) as Map<String, dynamic>;
    } catch (_) {
      return null;
    }
  }
  static Future<Map<String, dynamic>> dashboard()      => _get('/api/v1/dashboard');
  static Future<Map<String, dynamic>> schedule()       => _get('/api/v1/schedule');
  static Future<Map<String, dynamic>> reportsSummary() => _get('/api/v1/reports/summary');
  static Future<Map<String, dynamic>> notifications()  => _get('/api/v1/notifications');
  static Future<Map<String, dynamic>> markNotificationsRead() =>
      _post('/api/v1/notifications/read', {});

  /// Generic authenticated GET / POST for extended section endpoints.
  static Future<Map<String, dynamic>> getJson(String path) => _get(path);
  static Future<Map<String, dynamic>> postJson(String path, Map body) => _post(path, body);

  static Future<Map<String, dynamic>> scan(String imageB64, {int? scheduleId}) =>
      _post('/api/v1/scan', {
        'image': imageB64,
        if (scheduleId != null) 'schedule_id': scheduleId,
      });

  // ── Offline-aware lecture attendance ───────────────────────────────────────

  static Future<Map<String, dynamic>> activeSession() async {
    try {
      final data = await _get('/api/v1/sessions/active');
      if (data['ok'] == true) {
        await LocalDb.cacheSet(_K.session, jsonEncode(data));
      }
      return data;
    } catch (e) {
      if (e is AuthException || e is PermissionException) rethrow;
      final cached = await LocalDb.cacheGet(_K.session);
      if (cached != null) {
        final data = jsonDecode(cached) as Map<String, dynamic>;
        data['from_cache'] = true;
        return data;
      }
      return {'ok': false, 'error': 'offline', 'session': null, 'enrolled': []};
    }
  }

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
        // fall through to offline queue
      }
    }
    await LocalDb.enqueue(
      sessionId: sessionId,
      studentId: studentId,
      status: status,
      method: method,
    );
    return {'ok': true, 'queued': true};
  }

  /// Cached schedule — stale-while-revalidate.
  static Future<Map<String, dynamic>> scheduleCached() async {
    try {
      final data = await _get('/api/v1/schedule');
      await LocalDb.cacheSet(_K.schedule, jsonEncode(data));
      return data;
    } catch (e) {
      if (e is AuthException || e is PermissionException) rethrow;
      final cached = await LocalDb.cacheGet(_K.schedule,
          maxAge: const Duration(days: 7));
      if (cached != null) {
        final data = jsonDecode(cached) as Map<String, dynamic>;
        data['from_cache'] = true;
        return data;
      }
      return {'ok': false, 'error': 'offline', 'schedule': []};
    }
  }

  /// Cached attendance logs with optional filters.
  static Future<Map<String, dynamic>> attendanceLogsCached({
    String? dateFrom,
    String? dateTo,
    String? status,
    String? courseId,
  }) async {
    final params = <String, String>{};
    if (dateFrom != null) params['date_from'] = dateFrom;
    if (dateTo   != null) params['date_to']   = dateTo;
    if (status   != null && status.isNotEmpty) params['status'] = status;
    if (courseId != null && courseId.isNotEmpty) params['course_id'] = courseId;

    final query = params.isNotEmpty
        ? '?${params.entries.map((e) => '${e.key}=${Uri.encodeComponent(e.value)}').join('&')}'
        : '';
    final path = '/api/v1/attendance-logs$query';

    try {
      final data = await _get(path);
      // Only cache unfiltered results for offline fallback
      if (params.isEmpty && data['ok'] == true) {
        await LocalDb.cacheSet(_K.attLogs, jsonEncode(data));
      }
      return data;
    } catch (e) {
      if (e is AuthException || e is PermissionException) rethrow;
      if (params.isEmpty) {
        final cached = await LocalDb.cacheGet(_K.attLogs,
            maxAge: const Duration(hours: 1));
        if (cached != null) {
          final data = jsonDecode(cached) as Map<String, dynamic>;
          data['from_cache'] = true;
          return data;
        }
      }
      throw ApiException('تعذّر تحميل سجلات الحضور — تحقق من اتصالك');
    }
  }

  /// Sync pending offline records. Returns count synced.
  static Future<int> syncOfflineQueue() async {
    final pending = await LocalDb.pendingCount();
    if (pending == 0) return 0;
    await LocalDb.syncAll((records) => postJson(
        '/api/v1/lecture-attendance/sync', {'records': records}));
    return pending;
  }

  static Future<int> pendingCount() => LocalDb.pendingCount();
}
