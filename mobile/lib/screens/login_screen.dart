import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme.dart';
import '../auth.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey   = GlobalKey<FormState>();
  final _user      = TextEditingController();
  final _pass      = TextEditingController();
  bool  _obscure   = true;
  bool  _busy      = false;
  String? _error;

  @override
  void dispose() {
    _user.dispose();
    _pass.dispose();
    super.dispose();
  }

  // ── Validators ───────────────────────────────────────────────────────────

  String? _validateUsername(String? v) {
    v = v?.trim() ?? '';
    if (v.isEmpty)   return 'اسم المستخدم مطلوب';
    if (v.length < 3) return 'اسم المستخدم قصير جداً (3 أحرف على الأقل)';
    // Only alphanumeric + underscore + hyphen
    if (!RegExp(r'^[a-zA-Z0-9_\-@\.]+$').hasMatch(v)) {
      return 'اسم المستخدم يحتوي على أحرف غير مسموح بها';
    }
    return null;
  }

  String? _validatePassword(String? v) {
    v = v ?? '';
    if (v.isEmpty)   return 'كلمة المرور مطلوبة';
    if (v.length < 6) return 'كلمة المرور قصيرة جداً (6 أحرف على الأقل)';
    return null;
  }

  // ── Submit ────────────────────────────────────────────────────────────────

  Future<void> _submit() async {
    // Clear global error before re-validating
    setState(() => _error = null);
    if (!_formKey.currentState!.validate()) return;

    setState(() => _busy = true);
    final err = await context.read<AuthState>().login(
      _user.text.trim(),
      _pass.text,
    );
    if (!mounted) return;
    setState(() { _busy = false; _error = err; });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final expired = auth.sessionExpired;

    return Scaffold(
      backgroundColor: ShamelColors.primary,
      resizeToAvoidBottomInset: true,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsets.only(
              left: 24, right: 24, top: 24,
              bottom: MediaQuery.of(context).viewInsets.bottom + 24,
            ),
            child: Container(
              constraints: const BoxConstraints(maxWidth: 420),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
              decoration: BoxDecoration(
                color: Theme.of(context).brightness == Brightness.dark
                    ? const Color(0xFF1E293B)
                    : Colors.white,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    // Brand emblem
                    Container(
                      width: 72, height: 72,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [ShamelColors.navy, ShamelColors.primaryContainer],
                          begin: Alignment.topLeft, end: Alignment.bottomRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: const Icon(Icons.shield_outlined, color: ShamelColors.gold, size: 38),
                    ),
                    const SizedBox(height: 8),
                    Container(width: 90, height: 3, color: ShamelColors.gold),
                    const SizedBox(height: 20),
                    const Text('مرحباً بعودتك',
                        style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800,
                            color: ShamelColors.primary)),
                    const SizedBox(height: 6),
                    const Text('سجّل الدخول للوصول إلى بوابتك الأكاديمية',
                        style: TextStyle(color: ShamelColors.secondary, fontSize: 13)),
                    const SizedBox(height: 24),

                    // Session-expired banner
                    if (expired) ...[
                      _AlertBanner(
                        icon: Icons.lock_clock,
                        color: ShamelColors.warning,
                        text: 'انتهت صلاحية جلستك — يرجى تسجيل الدخول مجدداً',
                      ),
                      const SizedBox(height: 12),
                    ],

                    // API error banner
                    if (_error != null) ...[
                      _AlertBanner(
                        icon: Icons.error_outline,
                        color: ShamelColors.error,
                        text: _error!,
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Username field
                    const Align(
                      alignment: Alignment.centerRight,
                      child: Text('اسم المستخدم',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                              color: ShamelColors.secondary, letterSpacing: 0.5)),
                    ),
                    const SizedBox(height: 6),
                    TextFormField(
                      controller: _user,
                      textDirection: TextDirection.ltr,
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                      validator: _validateUsername,
                      decoration: const InputDecoration(
                        hintText: 'أدخل اسم المستخدم',
                        prefixIcon: Icon(Icons.person_outline, size: 18),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Password field
                    const Align(
                      alignment: Alignment.centerRight,
                      child: Text('كلمة المرور',
                          style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                              color: ShamelColors.secondary, letterSpacing: 0.5)),
                    ),
                    const SizedBox(height: 6),
                    TextFormField(
                      controller: _pass,
                      obscureText: _obscure,
                      textDirection: TextDirection.ltr,
                      autovalidateMode: AutovalidateMode.onUserInteraction,
                      validator: _validatePassword,
                      onFieldSubmitted: (_) => _submit(),
                      decoration: InputDecoration(
                        hintText: 'أدخل كلمة المرور',
                        prefixIcon: const Icon(Icons.lock_outline, size: 18),
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscure ? Icons.visibility_off : Icons.visibility,
                            color: ShamelColors.gold, size: 20,
                          ),
                          onPressed: () => setState(() => _obscure = !_obscure),
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _busy ? null : _submit,
                        child: _busy
                            ? const SizedBox(height: 20, width: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2, color: Colors.white))
                            : const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                Icon(Icons.login, size: 18),
                                SizedBox(width: 8),
                                Text('تسجيل الدخول'),
                              ]),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Icon(
                        Icons.circle,
                        color: auth.serverReachable ? ShamelColors.success : ShamelColors.error,
                        size: 8,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        auth.serverReachable
                            ? 'النظام متصل  •  SHAMEL v4.2'
                            : 'الخادم غير متاح — يعمل بوضع محدود',
                        style: const TextStyle(color: ShamelColors.outline, fontSize: 11),
                      ),
                    ]),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _AlertBanner extends StatelessWidget {
  final IconData icon;
  final Color    color;
  final String   text;
  const _AlertBanner({required this.icon, required this.color, required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.10),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.30)),
      ),
      child: Row(children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(width: 8),
        Expanded(child: Text(text,
            style: TextStyle(color: color, fontSize: 13, fontWeight: FontWeight.w600))),
      ]),
    );
  }
}
