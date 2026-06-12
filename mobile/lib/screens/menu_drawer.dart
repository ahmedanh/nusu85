import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme.dart';
import '../auth.dart';
import '../sections.dart';

/// Full-system navigation drawer — lists every section available to the
/// current role (grouped), so the native app surfaces all web features.
class MenuDrawer extends StatelessWidget {
  const MenuDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final role = auth.role;
    final groups = sectionsFor(role);

    return Drawer(
      child: SafeArea(
        child: Column(children: [
          // header
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                colors: [ShamelColors.navy, ShamelColors.primaryContainer],
                begin: Alignment.topRight, end: Alignment.bottomLeft,
              ),
            ),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Row(children: [
                const Icon(Icons.shield_outlined, color: ShamelColors.gold, size: 26),
                const SizedBox(width: 8),
                const Text('SHAMEL', style: TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800, letterSpacing: 1)),
              ]),
              const SizedBox(height: 12),
              Text(auth.name, style: const TextStyle(color: Colors.white, fontSize: 15, fontWeight: FontWeight.w700)),
              Text(ShamelTheme.roleLabel(role), style: const TextStyle(color: ShamelColors.goldLight, fontSize: 12)),
            ]),
          ),
          Expanded(
            child: ListView(
              padding: EdgeInsets.zero,
              children: [
                for (final g in groups) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(20, 16, 20, 6),
                    child: Text(g.title, style: TextStyle(
                        color: ShamelColors.sub(context), fontSize: 11, fontWeight: FontWeight.w800, letterSpacing: 1)),
                  ),
                  for (final s in g.items)
                    ListTile(
                      dense: true,
                      leading: Icon(s.icon, color: ShamelColors.primaryContainer, size: 22),
                      title: Text(s.label, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                      onTap: () {
                        Navigator.pop(context);
                        Navigator.push(context, MaterialPageRoute(builder: (_) => s.build()));
                      },
                    ),
                ],
                const Divider(height: 24),
                ListTile(
                  leading: const Icon(Icons.logout, color: ShamelColors.error),
                  title: const Text('تسجيل الخروج', style: TextStyle(color: ShamelColors.error, fontWeight: FontWeight.w700)),
                  onTap: () { Navigator.pop(context); context.read<AuthState>().logout(); },
                ),
              ],
            ),
          ),
          Padding(
            padding: EdgeInsets.all(12),
            child: Text('SHAMEL v4.2 • تطبيق أصلي', style: TextStyle(color: ShamelColors.sub(context), fontSize: 11)),
          ),
        ]),
      ),
    );
  }
}
