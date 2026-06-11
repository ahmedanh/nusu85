import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shamel/auth.dart';
import 'package:shamel/theme.dart';
import 'package:shamel/screens/login_screen.dart';

// Minimal AuthState stub — no network calls.
class _FakeAuth extends ChangeNotifier implements AuthState {
  @override Map<String, dynamic>? user;
  @override bool loading = false;
  @override bool serverReachable = true;
  @override bool sessionExpired = false;
  @override String get role => 'student';
  @override String get name => 'مستخدم';
  @override bool get isLoggedIn => user != null;

  @override Future<void> bootstrap() async {}
  @override void _onSessionExpired() {}
  @override Future<String?> login(String u, String p) async => null;
  @override Future<String?> loginBiometric() async => null;
  @override Future<void> logout() async {}
}

Widget _wrap(Widget child, {AuthState? auth}) => MaterialApp(
      theme: ShamelTheme.light(),
      darkTheme: ShamelTheme.dark(),
      home: ChangeNotifierProvider<AuthState>.value(
        value: auth ?? _FakeAuth(),
        child: child,
      ),
    );

void main() {
  group('LoginScreen', () {
    testWidgets('renders username + password fields', (tester) async {
      await tester.pumpWidget(_wrap(const LoginScreen()));
      expect(find.byType(TextFormField), findsNWidgets(2));
      expect(find.text('تسجيل الدخول'), findsOneWidget);
    });

    testWidgets('shows validation error on empty submit', (tester) async {
      await tester.pumpWidget(_wrap(const LoginScreen()));
      await tester.tap(find.widgetWithText(ElevatedButton, 'تسجيل الدخول'));
      await tester.pump();
      expect(find.text('اسم المستخدم مطلوب'), findsOneWidget);
      expect(find.text('كلمة المرور مطلوبة'), findsOneWidget);
    });

    testWidgets('shows password-too-short validation', (tester) async {
      await tester.pumpWidget(_wrap(const LoginScreen()));
      await tester.enterText(
          find.widgetWithText(TextFormField, 'أدخل اسم المستخدم'), 'admin');
      await tester.enterText(
          find.widgetWithText(TextFormField, 'أدخل كلمة المرور'), '123');
      await tester.pump();
      expect(find.text('كلمة المرور قصيرة جداً (6 أحرف على الأقل)'),
          findsOneWidget);
    });

    testWidgets('session-expired banner appears when sessionExpired=true',
        (tester) async {
      final auth = _FakeAuth()..sessionExpired = true;
      await tester.pumpWidget(_wrap(const LoginScreen(), auth: auth));
      expect(find.text('انتهت صلاحية جلستك — يرجى تسجيل الدخول مجدداً'),
          findsOneWidget);
    });

    testWidgets('server-unreachable indicator shows correct text',
        (tester) async {
      final auth = _FakeAuth()..serverReachable = false;
      await tester.pumpWidget(_wrap(const LoginScreen(), auth: auth));
      expect(find.textContaining('الخادم غير متاح'), findsOneWidget);
    });
  });
}
