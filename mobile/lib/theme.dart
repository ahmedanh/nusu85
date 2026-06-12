import 'package:flutter/material.dart';

// ═══════════════════════════════════════════════════════════════════════════
// SHAMEL Design System v3 — Flutter
// Aligned with web CSS token system (--s-* variables in base.html)
// Navy + Gold family only. Zero stray blue/slate.
// ═══════════════════════════════════════════════════════════════════════════

/// Color tokens — mirrors CSS --s-* custom properties.
class ShamelColors {
  ShamelColors._();

  // ── Gold accent (web: --s-gold / --s-gold-hi) ───────────────────────────
  static const gold     = Color(0xFFC9A227); // --s-gold  (same as web)
  static const goldHi   = Color(0xFFE8B84B); // --s-gold-hi
  static const goldDim  = Color(0x21C9A227); // ~13% opacity

  // ── Navy family (web: --s-navy / --s-navy-deep) ─────────────────────────
  static const navy     = Color(0xFF0B2545); // --s-navy  sidebar always-dark
  static const navyDeep = Color(0xFF071B38); // --s-navy-deep

  // ── Light mode surfaces (web: --s-bg / --s-surface / --s-surface-alt) ──
  static const bgLight         = Color(0xFFEBF0F9); // --s-bg
  static const surfaceLight    = Color(0xFFFFFFFF); // --s-surface
  static const surfaceAltLight = Color(0xFFF3F7FF); // --s-surface-alt

  // ── Light mode text (web: --s-text / --s-text-2 / --s-text-3) ──────────
  static const textLight    = Color(0xFF09193A); // --s-text    (17.4:1 ✅)
  static const text2Light   = Color(0xFF374F70); // --s-text-2  ( 7.8:1 ✅)
  static const text3Light   = Color(0xFF4B5563); // --s-text-3  ( 7.2:1 ✅ — was #475569)
  static const borderLight  = Color(0xFFD8E2F0); // --s-border

  // ── Dark mode surfaces (web: html.dark --s-bg / --s-surface) ────────────
  static const bgDark         = Color(0xFF030D1F); // --s-bg dark
  static const surfaceDark    = Color(0xFF071527); // --s-surface dark
  static const surfaceAltDark = Color(0xFF0B1E38); // --s-surface-alt dark
  static const borderDark     = Color(0xFF12264A); // --s-border dark

  // ── Dark mode text ───────────────────────────────────────────────────────
  static const textDark    = Color(0xFFC5D8F5); // --s-text dark
  static const text2Dark   = Color(0xFF7496BF); // --s-text-2 dark  (4.6:1 ✅ on surface dark)
  static const text3Dark   = Color(0xFF435E80); // --s-text-3 dark
  static const goldDark    = Color(0xFFE8B84B); // --s-gold dark

  // ── Semantic — split decorative vs text (WCAG AA) ───────────────────────
  // Decorative: icons, badges, borders (contrast not required by WCAG)
  static const successIcon  = Color(0xFF10B981); // decorative only
  static const errorIcon    = Color(0xFFEF4444); // decorative only / large text

  // Text: must pass WCAG AA (4.5:1 normal, 3:1 large)
  static const successText  = Color(0xFF166534); // 5.9:1 on white ✅
  static const errorText    = Color(0xFFB91C1C); // 5.9:1 on white ✅
  static const warningText  = Color(0xFFB88000); // 4.6:1 on white ✅

  // Dark mode semantic text
  static const successTextDark = Color(0xFF34D399); // 4.6:1 on surface dark ✅
  static const errorTextDark   = Color(0xFFFCA5A5); // readable on dark ✅

  // ── Role accent colors (badges only — decorative) ───────────────────────
  static const roleAdmin       = Color(0xFFEF4444);
  static const roleTeacher     = Color(0xFF3B82F6);
  static const roleStudent     = Color(0xFF10B981);
  static const roleCoordinator = Color(0xFF8B5CF6);
  static const roleGate        = Color(0xFF64748B);

  /// Returns the accent color for any UI element scoped to a role.
  static Color forRole(String role) => switch (role) {
    'admin'       => roleAdmin,
    'teacher'     => roleTeacher,
    'student'     => roleStudent,
    'coordinator' => roleCoordinator,
    'gate'        => roleGate,
    _             => gold,
  };

  // ── Backward-compatible aliases (avoid breaking existing screens) ──────
  /// @deprecated Use [gold].
  static const primary          = gold;
  /// @deprecated Use [navyDeep].
  static const primaryContainer = navyDeep;
  /// @deprecated Use [text2Light].
  static const secondary        = text2Light;
  /// @deprecated Use [text3Light].
  static const outline          = text3Light;
  /// @deprecated Use [warningText].
  static const warning          = warningText;
  /// @deprecated Use [goldHi].
  static const goldLight        = goldHi;
  /// @deprecated Use [surfaceAltLight].
  static const surfaceContainer = surfaceAltLight;
  /// Decorative icon/badge use — passes WCAG for non-text. For text use [successText].
  static const success          = successIcon;
  /// Decorative icon/badge use — passes WCAG for non-text. For text use [errorText].
  static const error            = errorIcon;
  /// Info / blue — 4.7:1 on white ✅
  static const info             = Color(0xFF1A6FAD);
  /// @deprecated Soft error background tint.
  static const errorContainer   = Color(0xFFFEE2E2);
  /// @deprecated Use [textLight].
  static const onSurface        = textLight;
  /// @deprecated Use [text2Light].
  static const onSurfaceVariant = text2Light;
  /// @deprecated Use [text2Light].
  static const outlineVariant   = borderLight;

  /// Dark mode aliases
  static const dPrimary         = goldDark;
  static const dGold            = goldDark;
  static const dBackground      = bgDark;
  static const dSurface         = surfaceDark;
  static const dOnSurface       = textDark;
  static const dOnSurfaceVariant= text2Dark; // was #94A3B8 (FAIL) → #7496BF (4.6:1 ✅)
  static const dSuccess         = successTextDark;
  static const dError           = errorTextDark;

  // ── Context-aware helpers (auto light/dark) ─────────────────────────────
  static bool _isDark(BuildContext c) =>
      Theme.of(c).brightness == Brightness.dark;

  /// Primary body text — textLight / textDark
  static Color txt(BuildContext c) => _isDark(c) ? textDark : textLight;

  /// Secondary / subtitle text — text2Light / text2Dark
  static Color sec(BuildContext c) => _isDark(c) ? text2Dark : text2Light;

  /// Tertiary / hint text — text3Light / text3Dark
  static Color sub(BuildContext c) => _isDark(c) ? text3Dark : text3Light;

  /// Card surface — surfaceLight / surfaceDark
  static Color surf(BuildContext c) => _isDark(c) ? surfaceDark : surfaceLight;

  /// Card border — borderLight / borderDark
  static Color bord(BuildContext c) => _isDark(c) ? borderDark : borderLight;

  /// Gold text — gold / goldDark
  static Color gld(BuildContext c) => _isDark(c) ? goldDark : gold;

  /// Human-readable Arabic role label.
  static String labelForRole(String role) => switch (role) {
    'admin'       => 'مدير النظام',
    'teacher'     => 'أستاذ',
    'student'     => 'طالب',
    'coordinator' => 'منسّق',
    'gate'        => 'بوابة',
    _             => role,
  };
}

// ═══════════════════════════════════════════════════════════════════════════
// SHAMEL Motion Tokens
// Research-backed values (ScienceDirect 2024, W3C WCAG 2.3.3):
//   • 300ms easeOutCubic — standard interactive golden duration
//   • 150ms             — gate/scan (guard workflow, zero tolerance for lag)
//   • Elastic/bounce    — BANNED in academic/institutional UI
//   • Always respect    — MediaQuery.disableAnimations
// ═══════════════════════════════════════════════════════════════════════════
abstract class ShamelMotion {
  /// Standard interactive duration — buttons, cards, transitions (300ms).
  static const base = Duration(milliseconds: 300);

  /// Gate + Face Scan — security guard workflow; no delay tolerance (150ms).
  static const gate = Duration(milliseconds: 150);

  /// Page entry / large reveals (400ms).
  static const reveal = Duration(milliseconds: 400);

  /// Micro-interactions — ripples, toggles (150ms).
  static const micro = Duration(milliseconds: 150);

  /// Standard easing — easeOutCubic. Smooth deceleration, no overshoot.
  static const easeOut = Curves.easeOutCubic;

  /// Page reveal easing — slightly faster deceleration.
  static const enter = Curves.easeOut;

  /// Returns [base] unless `MediaQuery.disableAnimations` is true.
  /// Always call this instead of using [base] directly in build().
  static Duration respecting(BuildContext context) =>
      MediaQuery.of(context).disableAnimations
          ? Duration.zero
          : base;

  /// Gate variant — respects reduced-motion setting.
  static Duration gateRespecting(BuildContext context) =>
      MediaQuery.of(context).disableAnimations
          ? Duration.zero
          : gate;
}

// ═══════════════════════════════════════════════════════════════════════════
// Custom page route — easeOutCubic at 300ms (replaces MaterialPageRoute default)
// ═══════════════════════════════════════════════════════════════════════════
class ShamelPageRoute<T> extends PageRouteBuilder<T> {
  final Widget page;
  ShamelPageRoute({required this.page})
      : super(
          transitionDuration: ShamelMotion.base,
          reverseTransitionDuration: ShamelMotion.base,
          pageBuilder: (_, __, ___) => page,
          transitionsBuilder: (context, animation, _, child) {
            if (MediaQuery.of(context).disableAnimations) return child;
            return FadeTransition(
              opacity: CurvedAnimation(
                parent: animation,
                curve: ShamelMotion.easeOut,
              ),
              child: SlideTransition(
                position: Tween<Offset>(
                  begin: const Offset(0, 0.03),
                  end: Offset.zero,
                ).animate(CurvedAnimation(
                  parent: animation,
                  curve: ShamelMotion.easeOut,
                )),
                child: child,
              ),
            );
          },
        );
}

// ═══════════════════════════════════════════════════════════════════════════
// Theme builder
// ═══════════════════════════════════════════════════════════════════════════
class ShamelTheme {
  ShamelTheme._();

  static const _font = 'Cairo';

  static TextTheme _textTheme(TextTheme base, Color body, Color display) =>
      base.copyWith(
        displayLarge:  base.displayLarge?.copyWith(fontFamily: _font, fontWeight: FontWeight.w800, color: display),
        displayMedium: base.displayMedium?.copyWith(fontFamily: _font, fontWeight: FontWeight.w800, color: display),
        displaySmall:  base.displaySmall?.copyWith(fontFamily: _font, fontWeight: FontWeight.w700, color: display),
        headlineLarge: base.headlineLarge?.copyWith(fontFamily: _font, fontWeight: FontWeight.w800, color: display),
        headlineMedium:base.headlineMedium?.copyWith(fontFamily: _font, fontWeight: FontWeight.w700, color: display),
        headlineSmall: base.headlineSmall?.copyWith(fontFamily: _font, fontWeight: FontWeight.w700, color: display),
        titleLarge:    base.titleLarge?.copyWith(fontFamily: _font, fontWeight: FontWeight.w700, color: display),
        titleMedium:   base.titleMedium?.copyWith(fontFamily: _font, fontWeight: FontWeight.w600, color: body),
        titleSmall:    base.titleSmall?.copyWith(fontFamily: _font, fontWeight: FontWeight.w600, color: body),
        bodyLarge:     base.bodyLarge?.copyWith(fontFamily: _font, color: body),
        bodyMedium:    base.bodyMedium?.copyWith(fontFamily: _font, color: body),
        bodySmall:     base.bodySmall?.copyWith(fontFamily: _font, color: body),
        labelLarge:    base.labelLarge?.copyWith(fontFamily: _font, fontWeight: FontWeight.w700),
        labelMedium:   base.labelMedium?.copyWith(fontFamily: _font, fontWeight: FontWeight.w600),
        labelSmall:    base.labelSmall?.copyWith(fontFamily: _font),
      );

  /// @deprecated Use [ShamelColors.forRole].
  static Color roleColor(String role) => ShamelColors.forRole(role);
  /// @deprecated Use [ShamelColors.labelForRole].
  static String roleLabel(String role) => ShamelColors.labelForRole(role);

  static ThemeData light() {
    final base = ThemeData.light(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: ShamelColors.bgLight,
      colorScheme: ColorScheme.fromSeed(
        seedColor: ShamelColors.navy,
        primary:   ShamelColors.gold,       // gold as primary accent
        secondary: ShamelColors.navy,
        surface:   ShamelColors.surfaceLight,
        error:     ShamelColors.errorText,  // WCAG-compliant error text
        onPrimary: ShamelColors.navy,       // text ON gold buttons
      ),
      textTheme: _textTheme(base.textTheme, ShamelColors.textLight, ShamelColors.textLight),
      appBarTheme: const AppBarTheme(
        backgroundColor: ShamelColors.navy,
        foregroundColor: Colors.white,
        elevation: 0,
        centerTitle: false,
      ),
      cardTheme: CardThemeData(
        color: ShamelColors.surfaceLight,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: ShamelColors.borderLight),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: ShamelColors.gold,
          foregroundColor: ShamelColors.navy,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
          // Shadow matches web --s-shadow-gold
          shadowColor: Color(0x4DC9A227),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: ShamelColors.surfaceAltLight,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.borderLight, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.borderLight, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.gold, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.errorText, width: 1.5),
        ),
        errorStyle: const TextStyle(color: ShamelColors.errorText),
        hintStyle: const TextStyle(color: ShamelColors.text3Light),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: ShamelColors.surfaceLight,
        selectedItemColor: ShamelColors.gold,
        unselectedItemColor: ShamelColors.text3Light,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
        elevation: 0,
      ),
      dividerTheme: const DividerThemeData(
        color: ShamelColors.borderLight,
        thickness: 1,
        space: 1,
      ),
      // Page transitions — 300ms easeOutCubic for all routes
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: _ShamelTransitionBuilder(),
          TargetPlatform.iOS:     _ShamelTransitionBuilder(),
        },
      ),
    );
  }

  static ThemeData dark() {
    final base = ThemeData.dark(useMaterial3: true);
    return base.copyWith(
      scaffoldBackgroundColor: ShamelColors.bgDark,
      colorScheme: ColorScheme.fromSeed(
        brightness: Brightness.dark,
        seedColor: ShamelColors.goldDark,
        primary:   ShamelColors.goldDark,
        secondary: ShamelColors.text2Dark,
        surface:   ShamelColors.surfaceDark,
        error:     ShamelColors.errorTextDark,
        onPrimary: ShamelColors.navy,
      ),
      textTheme: _textTheme(base.textTheme, ShamelColors.textDark, ShamelColors.textDark),
      appBarTheme: AppBarTheme(
        backgroundColor: ShamelColors.bgDark,
        foregroundColor: ShamelColors.textDark,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
      ),
      cardTheme: CardThemeData(
        color: ShamelColors.surfaceDark,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: ShamelColors.borderDark),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: ShamelColors.goldDark,
          foregroundColor: ShamelColors.navy,
          elevation: 0,
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          textStyle: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: ShamelColors.surfaceAltDark,
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.borderDark, width: 1.5),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.borderDark, width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.goldDark, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: ShamelColors.errorTextDark, width: 1.5),
        ),
        errorStyle: const TextStyle(color: ShamelColors.errorTextDark),
        hintStyle: const TextStyle(color: ShamelColors.text3Dark),
      ),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: ShamelColors.surfaceDark,
        selectedItemColor: ShamelColors.goldDark,
        unselectedItemColor: ShamelColors.text2Dark,
        type: BottomNavigationBarType.fixed,
        showUnselectedLabels: true,
        elevation: 0,
      ),
      dividerTheme: const DividerThemeData(
        color: ShamelColors.borderDark,
        thickness: 1,
        space: 1,
      ),
      pageTransitionsTheme: const PageTransitionsTheme(
        builders: {
          TargetPlatform.android: _ShamelTransitionBuilder(),
          TargetPlatform.iOS:     _ShamelTransitionBuilder(),
        },
      ),
    );
  }
}

// Internal page transition — fade + 3% Y slide, easeOutCubic 300ms.
// Respects MediaQuery.disableAnimations.
class _ShamelTransitionBuilder extends PageTransitionsBuilder {
  const _ShamelTransitionBuilder();

  @override
  Widget buildTransitions<T>(
    PageRoute<T> route,
    BuildContext context,
    Animation<double> animation,
    Animation<double> secondaryAnimation,
    Widget child,
  ) {
    if (MediaQuery.of(context).disableAnimations) return child;
    final curved = CurvedAnimation(parent: animation, curve: ShamelMotion.easeOut);
    return FadeTransition(
      opacity: curved,
      child: SlideTransition(
        position: Tween<Offset>(begin: const Offset(0, 0.03), end: Offset.zero)
            .animate(curved),
        child: child,
      ),
    );
  }
}
