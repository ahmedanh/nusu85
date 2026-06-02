import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../auth.dart';
import '../theme.dart';
import '../theme_controller.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final u = auth.user ?? {};
    final role = auth.role;

    Widget row(String label, dynamic value) {
      if (value == null || '$value'.isEmpty) return const SizedBox.shrink();
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(children: [
          Text(label, style: const TextStyle(color: ShamelColors.secondary, fontSize: 13)),
          const Spacer(),
          Text('$value', style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary, fontSize: 14)),
        ]),
      );
    }

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const SizedBox(height: 8),
        Center(child: Column(children: [
          Container(
            width: 88, height: 88,
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [ShamelColors.navy, ShamelColors.primaryContainer]),
              shape: BoxShape.circle,
            ),
            child: Center(
              child: Text(
                (auth.name.isNotEmpty ? auth.name[0] : '?'),
                style: const TextStyle(color: ShamelColors.gold, fontSize: 36, fontWeight: FontWeight.w800),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(auth.name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w800, color: ShamelColors.primary)),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(color: ShamelTheme.roleColor(role), borderRadius: BorderRadius.circular(20)),
            child: Text(ShamelTheme.roleLabel(role),
                style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700)),
          ),
        ])),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE8EAED)),
          ),
          child: Column(children: [
            row('اسم المستخدم', u['username']),
            const Divider(height: 1),
            row('البريد الإلكتروني', u['email']),
            if (u['student_code'] != null) ...[const Divider(height: 1), row('الرقم الجامعي', u['student_code'])],
            if (u['teacher_id'] != null) ...[const Divider(height: 1), row('رقم الأستاذ', u['teacher_id'])],
            if (u['degree'] != null) ...[const Divider(height: 1), row('الدرجة العلمية', u['degree'])],
            if (u['department'] != null) ...[const Divider(height: 1), row('القسم', u['department'])],
            if (u['college'] != null) ...[const Divider(height: 1), row('الكلية', u['college'])],
            if (u['batch'] != null) ...[const Divider(height: 1), row('الدفعة', u['batch'])],
          ]),
        ),
        const SizedBox(height: 16),
        // ── Dark mode toggle ──
        Builder(builder: (ctx) {
          final tc = ctx.watch<ThemeController>();
          return Container(
            decoration: BoxDecoration(
              color: Theme.of(ctx).cardColor,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE8EAED)),
            ),
            child: SwitchListTile(
              value: tc.isDark,
              onChanged: (_) => ctx.read<ThemeController>().toggle(),
              activeThumbColor: ShamelColors.gold,
              secondary: Icon(tc.isDark ? Icons.dark_mode : Icons.light_mode,
                  color: tc.isDark ? ShamelColors.goldLight : ShamelColors.gold),
              title: const Text('الوضع الداكن', style: TextStyle(fontWeight: FontWeight.w700)),
            ),
          );
        }),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            style: OutlinedButton.styleFrom(
              foregroundColor: ShamelColors.error,
              side: const BorderSide(color: ShamelColors.error),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            onPressed: () => context.read<AuthState>().logout(),
            icon: const Icon(Icons.logout),
            label: const Text('تسجيل الخروج', style: TextStyle(fontWeight: FontWeight.w700)),
          ),
        ),
        const SizedBox(height: 16),
        const Center(child: Text('SHAMEL v4.2  •  تطبيق أصلي', style: TextStyle(color: ShamelColors.outline, fontSize: 11))),
      ],
    );
  }
}
