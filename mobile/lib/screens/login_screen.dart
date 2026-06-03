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
  final _user = TextEditingController();
  final _pass = TextEditingController();
  bool _obscure = true;
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _user.dispose();
    _pass.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() { _busy = true; _error = null; });
    final err = await context.read<AuthState>().login(_user.text.trim(), _pass.text);
    if (!mounted) return;
    setState(() { _busy = false; _error = err; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ShamelColors.primary,
      resizeToAvoidBottomInset: true,  // keyboard pushes content up (fixes black screen)
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: EdgeInsets.only(
              left: 24, right: 24, top: 24,
              bottom: MediaQuery.of(context).viewInsets.bottom + 24, // extra pad above keyboard
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
                      style: TextStyle(fontSize: 26, fontWeight: FontWeight.w800, color: ShamelColors.primary)),
                  const SizedBox(height: 6),
                  const Text('سجّل الدخول للوصول إلى بوابتك الأكاديمية',
                      style: TextStyle(color: ShamelColors.secondary, fontSize: 13)),
                  const SizedBox(height: 24),

                  if (_error != null) ...[
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: ShamelColors.errorContainer,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(children: [
                        const Icon(Icons.error_outline, color: ShamelColors.error, size: 18),
                        const SizedBox(width: 8),
                        Expanded(child: Text(_error!,
                            style: const TextStyle(color: ShamelColors.error, fontSize: 13, fontWeight: FontWeight.w600))),
                      ]),
                    ),
                    const SizedBox(height: 16),
                  ],

                  const Align(
                    alignment: Alignment.centerRight,
                    child: Text('اسم المستخدم أو البريد',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: ShamelColors.secondary, letterSpacing: 0.5)),
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _user,
                    textDirection: TextDirection.ltr,
                    decoration: const InputDecoration(hintText: 'أدخل اسم المستخدم'),
                  ),
                  const SizedBox(height: 16),
                  const Align(
                    alignment: Alignment.centerRight,
                    child: Text('كلمة المرور',
                        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700, color: ShamelColors.secondary, letterSpacing: 0.5)),
                  ),
                  const SizedBox(height: 6),
                  TextField(
                    controller: _pass,
                    obscureText: _obscure,
                    textDirection: TextDirection.ltr,
                    onSubmitted: (_) => _submit(),
                    decoration: InputDecoration(
                      hintText: 'أدخل كلمة المرور',
                      suffixIcon: IconButton(
                        icon: Icon(_obscure ? Icons.visibility_off : Icons.visibility,
                            color: ShamelColors.gold, size: 20),
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
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                              Icon(Icons.login, size: 18),
                              SizedBox(width: 8),
                              Text('تسجيل الدخول'),
                            ]),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                    Icon(Icons.circle, color: ShamelColors.success, size: 8),
                    SizedBox(width: 6),
                    Text('النظام متصل  •  SHAMEL v4.2',
                        style: TextStyle(color: ShamelColors.outline, fontSize: 11)),
                  ]),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
