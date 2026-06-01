import 'package:flutter/foundation.dart';
import 'api.dart';

/// Holds the authenticated user + role across the app.
class AuthState extends ChangeNotifier {
  Map<String, dynamic>? user;
  bool loading = true;

  String get role => (user?['role'] ?? 'student') as String;
  String get name => (user?['name'] ?? 'مستخدم') as String;

  /// Called at startup: restore token, fetch profile.
  Future<void> bootstrap() async {
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
    try {
      final r = await Api.login(username, password);
      if (r['ok'] == true) {
        user = r['user'] as Map<String, dynamic>;
        notifyListeners();
        return null; // success
      }
      return (r['message'] ?? 'فشل تسجيل الدخول') as String;
    } catch (e) {
      return 'تعذّر الاتصال بالخادم — تحقق من الشبكة';
    }
  }

  Future<void> logout() async {
    await Api.clearToken();
    user = null;
    notifyListeners();
  }
}
