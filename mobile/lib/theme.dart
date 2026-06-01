import 'package:flutter/material.dart';

/// SHAMEL design tokens — mirrored exactly from the web system's Tailwind config.
class ShamelColors {
  static const primary           = Color(0xFF051125); // deep navy
  static const primaryContainer  = Color(0xFF1B263B);
  static const navy              = Color(0xFF0B2545);
  static const gold              = Color(0xFFCBA135); // brand gold accent
  static const goldLight         = Color(0xFFE3C766);
  static const secondary         = Color(0xFF5A5E69);
  static const secondaryContainer= Color(0xFFDCDFEC);
  static const surface           = Color(0xFFF8F9FA);
  static const surfaceContainer  = Color(0xFFEDEEEF);
  static const onSurface         = Color(0xFF191C1D);
  static const onSurfaceVariant  = Color(0xFF45474D);
  static const outline           = Color(0xFF75777D);
  static const outlineVariant    = Color(0xFFC5C6CD);
  static const error             = Color(0xFFBA1A1A);
  static const errorContainer    = Color(0xFFFFDAD6);
  static const success           = Color(0xFF15803D);
  static const warning           = Color(0xFFB45309);

  // role accent colors (match web role badges)
  static const roleAdmin       = Color(0xFFDC3232);
  static const roleTeacher     = Color(0xFF3296DC);
  static const roleStudent     = Color(0xFF32B464);
  static const roleCoordinator = Color(0xFFB464DC);
  static const roleGate        = Color(0xFF787878);
}

class ShamelTheme {
  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: ShamelColors.surface,
      colorScheme: ColorScheme.fromSeed(
        seedColor: ShamelColors.navy,
        primary: ShamelColors.primary,
        secondary: ShamelColors.gold,
        surface: Colors.white,
        error: ShamelColors.error,
      ),
      textTheme: base.textTheme.apply(
        bodyColor: ShamelColors.onSurface,
        displayColor: ShamelColors.primary,
        fontFamily: 'Roboto',
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: ShamelColors.primary,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFFE8EAED)),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: ShamelColors.primary,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: const Color(0xFFEEF1F6),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.gold, width: 1.5),
        ),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: ShamelColors.primary,
        unselectedItemColor: ShamelColors.outline,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
      ),
    );
  }

  static Color roleColor(String role) {
    switch (role) {
      case 'admin': return ShamelColors.roleAdmin;
      case 'teacher': return ShamelColors.roleTeacher;
      case 'student': return ShamelColors.roleStudent;
      case 'coordinator': return ShamelColors.roleCoordinator;
      case 'gate': return ShamelColors.roleGate;
      default: return ShamelColors.primary;
    }
  }

  static String roleLabel(String role) {
    switch (role) {
      case 'admin': return 'مدير النظام';
      case 'teacher': return 'أستاذ';
      case 'student': return 'طالب';
      case 'coordinator': return 'منسّق';
      case 'gate': return 'بوابة';
      default: return role;
    }
  }
}
