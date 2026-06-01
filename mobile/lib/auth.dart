import 'package:flutter/foundation.dart';
import 'api.dart';

/// Holds the authenticated user + role across the app.
class AuthState extends ChangeNotifier {
  Map<String, dynamic>? user;
  bool loading = true;

  String get role => (user?['role'] ?? 'student') as String;
  String get name => (user?['name'] ?? 'مستخدم') as String;

  bool serverReachable = true;

  /// Called at startup: discover a reachable server, restore token, fetch profile.
  Future<void> bootstrap() async {
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
      } catch (_) {
        // offline but token present — keep logged-in shell, screens handle errors
      }
    }
    loading = false;
    notifyListeners();
  }

  Future<String?> login(String username, String password) async {
    // Re-discover if the previous probe failed (server may have come up).
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
    } catch (e) {
      // Try one more discovery pass before giving up.
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
      return 'تعذّر الوصول للخادم — تأكد أن خادم SHAMEL يعمل على الكمبيوتر '
          '(المنفذ 9000 أو 8000)';
    }
  }

  Future<void> logout() async {
    await Api.clearToken();
    user = null;
    notifyListeners();
  }
}
