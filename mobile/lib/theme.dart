import 'package:flutter/material.dart';

/// SHAMEL design tokens — high-contrast academic palette (light + dark).
class ShamelColors {
  // ── Light mode ──────────────────────────────────────────────────────────
  static const primary           = Color(0xFF1E3A8A); // academic blue
  static const primaryContainer  = Color(0xFF1B2B5E);
  static const navy              = Color(0xFF1E3A8A);
  static const gold              = Color(0xFFF59E0B); // amber accent
  static const goldLight         = Color(0xFFFBBF24);
  static const secondary         = Color(0xFF475569); // sub-text
  static const secondaryContainer= Color(0xFFE2E8F0);
  static const surface           = Color(0xFFF8FAFC); // page background
  static const surfaceContainer  = Color(0xFFEEF2F7);
  static const onSurface         = Color(0xFF0F172A); // headings
  static const onSurfaceVariant  = Color(0xFF475569);
  static const outline           = Color(0xFF64748B);
  static const outlineVariant    = Color(0xFFCBD5E1);
  static const error             = Color(0xFFEF4444);
  static const errorContainer    = Color(0xFFFEE2E2);
  static const success           = Color(0xFF10B981);
  static const warning           = Color(0xFFF59E0B);

  // ── Dark mode ───────────────────────────────────────────────────────────
  static const dPrimary          = Color(0xFF60A5FA); // readable on dark
  static const dGold             = Color(0xFFFBBF24);
  static const dBackground       = Color(0xFF0F172A); // near-black navy
  static const dSurface          = Color(0xFF1E293B); // cards
  static const dOnSurface        = Color(0xFFF8FAFC); // headings
  static const dOnSurfaceVariant = Color(0xFF94A3B8); // sub-text
  static const dSuccess          = Color(0xFF34D399);
  static const dError            = Color(0xFFF87171);

  // role accent colors (badges)
  static const roleAdmin       = Color(0xFFEF4444);
  static const roleTeacher     = Color(0xFF3B82F6);
  static const roleStudent     = Color(0xFF10B981);
  static const roleCoordinator = Color(0xFF8B5CF6);
  static const roleGate        = Color(0xFF64748B);
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

  /// Dark theme using the high-contrast dark palette.
  static ThemeData dark() {
    final base = ThemeData.dark(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: ShamelColors.dBackground,
      colorScheme: ColorScheme.fromSeed(
        brightness: Brightness.dark,
        seedColor: ShamelColors.dPrimary,
        primary: ShamelColors.dPrimary,
        secondary: ShamelColors.dGold,
        surface: ShamelColors.dSurface,
        error: ShamelColors.dError,
      ),
      cardTheme: CardThemeData(
        color: ShamelColors.dSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFF334155)),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: ShamelColors.dBackground,
        foregroundColor: ShamelColors.dOnSurface,
        elevation: 0,
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: ShamelColors.dSurface,
        selectedItemColor: ShamelColors.dPrimary,
        unselectedItemColor: ShamelColors.dOnSurfaceVariant,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
      ),
    );
  }
}
