import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:local_auth/local_auth.dart';

/// Thin wrapper around local_auth.
/// Biometric login stores the last-used token and re-uses it.
/// If the token is stale the API will 401 → normal session-expiry flow kicks in.
class BiometricAuth {
  static final _auth    = LocalAuthentication();
  static const _storage = FlutterSecureStorage();
  static const _bioKey  = 'shamel_bio_enabled';

  // ── Capability ────────────────────────────────────────────────────────

  /// Returns true if device supports biometric AND at least one is enrolled.
  static Future<bool> isAvailable() async {
    try {
      final capable  = await _auth.canCheckBiometrics;
      final enrolled = await _auth.isDeviceSupported();
      if (!capable || !enrolled) return false;
      final bios = await _auth.getAvailableBiometrics();
      return bios.isNotEmpty;
    } catch (_) {
      return false;
    }
  }

  // ── User opt-in / opt-out ─────────────────────────────────────────────

  static Future<bool> isEnabled() async {
    final v = await _storage.read(key: _bioKey);
    return v == 'true';
  }

  static Future<void> setEnabled(bool value) =>
      _storage.write(key: _bioKey, value: value ? 'true' : 'false');

  /// Called after successful password login: enables biometric for next time.
  static Future<void> enableAfterLogin() async {
    if (await isAvailable()) await setEnabled(true);
  }

  /// Wipe biometric preference (on logout / token clear).
  static Future<void> disable() => setEnabled(false);

  // ── Authenticate ──────────────────────────────────────────────────────

  /// Prompts OS biometric dialog.
  /// Returns true if authenticated, false if cancelled or failed.
  static Future<bool> authenticate() async {
    try {
      return await _auth.authenticate(
        localizedReason: 'سجّل دخولك إلى شامل بصمةً أو بالتعرف على الوجه',
        options: const AuthenticationOptions(
          biometricOnly: false,   // allow PIN fallback
          stickyAuth: true,       // don't cancel when app goes background
        ),
      );
    } catch (_) {
      return false;
    }
  }
}
