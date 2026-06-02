import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';
import 'theme.dart';
import 'theme_controller.dart';
import 'auth.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthState()..bootstrap()),
        ChangeNotifierProvider(create: (_) => ThemeController()..load()),
      ],
      child: const ShamelApp(),
    ),
  );
}

class ShamelApp extends StatelessWidget {
  const ShamelApp({super.key});

  @override
  Widget build(BuildContext context) {
    final themeCtl = context.watch<ThemeController>();
    return MaterialApp(
      title: 'SHAMEL',
      debugShowCheckedModeBanner: false,
      theme: ShamelTheme.light(),
      darkTheme: ShamelTheme.dark(),
      themeMode: themeCtl.mode,
      locale: const Locale('ar'),
      supportedLocales: const [Locale('ar'), Locale('en')],
      localizationsDelegates: const [
        GlobalMaterialLocalizations.delegate,
        GlobalWidgetsLocalizations.delegate,
        GlobalCupertinoLocalizations.delegate,
      ],
      builder: (context, child) => Directionality(
        textDirection: TextDirection.rtl,
        child: child!,
      ),
      home: const _Root(),
    );
  }
}

class _Root extends StatelessWidget {
  const _Root();

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    if (auth.loading) {
      return const Scaffold(
        backgroundColor: ShamelColors.primary,
        body: Center(child: CircularProgressIndicator(color: ShamelColors.gold)),
      );
    }
    return auth.user == null ? const LoginScreen() : const HomeScreen();
  }
}
