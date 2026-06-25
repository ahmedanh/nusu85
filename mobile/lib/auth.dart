import 'package:flutter/foundation.dart';
import 'api.dart';

/// Holds the authenticated user + role across the app.
class AuthState extends ChangeNotifier {
  Map<String, dynamic>? user;
  bool loading       = true;
  bool serverReachable = true;
  bool sessionExpired  = false; // set true when 401 received mid-session

  String get role => (user?['role'] ?? 'student') as String;
  String get name => (user?['name'] ?? 'مستخدم') as String;
  bool   get isLoggedIn => user != null;

  /// Called at startup: discover server, restore token, fetch profile.
  /// Also registers the 401 callback so any future 401 auto-logs out.
  Future<void> bootstrap() async {
    Api.onUnauthorized = _onSessionExpired;

    serverReachable = await Api.discover();
    await Api.loadToken();

    if (Api.isLoggedIn) {
      try {
        final r = await Api.me();
        if (r['ok'] == true) {
          user = r['user'] as Map<String, dynamic>;
        } else {
          await Api.clearToken();
        }
      } on AuthException {
        // Token was invalid — clear it
        await Api.clearToken();
      } catch (_) {
        // Offline — try cached profile so user stays logged in
        final cached = await Api.cachedProfile();
        if (cached != null) {
          user = cached;
        }
        // If no cache either, user must re-login when back online
      }
    }
    loading = false;
    notifyListeners();
  }

  /// Called automatically by Api when a 401 is received on any request.
  void _onSessionExpired() {
    if (user == null) return; // already logged out
    user = null;
    sessionExpired = true;
    notifyListeners();
  }

  Future<String?> login(String username, String password) async {
    sessionExpired = false;
    if (!serverReachable) {
      serverReachable = await Api.discover();
    }
    try {
      final r = await Api.login(username, password);
      if (r['ok'] == true) {
        user = r['user'] as Map<String, dynamic>;
        notifyListeners();
        return null; // success
      }
      return (r['message'] ?? 'فشل تسجيل الدخول') as String;
    } on ApiException catch (e) {
      // Rediscover and retry once
      if (await Api.discover()) {
        try {
          final r = await Api.login(username, password);
          if (r['ok'] == true) {
            user = r['user'] as Map<String, dynamic>;
            notifyListeners();
            return null;
          }
          return (r['message'] ?? 'فشل تسجيل الدخول') as String;
        } catch (_) {}
      }
      return e.message;
    }
  }

  /// Biometric login: token already exists — just re-validate via /me.
  Future<String?> loginBiometric() async {
    sessionExpired = false;
    try {
      final r = await Api.me();
      if (r['ok'] == true) {
        user = r['user'] as Map<String, dynamic>;
        notifyListeners();
        return null;
      }
      return 'انتهت صلاحية الجلسة — أعد تسجيل الدخول بكلمة المرور';
    } on AuthException {
      return 'انتهت صلاحية الجلسة — أعد تسجيل الدخول بكلمة المرور';
    } on ApiException catch (e) {
      return e.message;
    }
  }

  Future<void> logout() async {
    await Api.clearToken();
    user = null;
    sessionExpired = false;
    notifyListeners();
  }
}
