import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// SHAMEL API client — talks to the Django /api/v1 JSON endpoints.
///
/// Base URL note:
///  - Android emulator reaches the host machine at 10.0.2.2
///  - A physical phone would use the LAN IP / public domain (shamel.sd)
class Api {
  // 10.0.2.2 = host loopback from the Android emulator. Daphne runs on :9000.
  static String baseUrl = 'http://10.0.2.2:9000';

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
}
