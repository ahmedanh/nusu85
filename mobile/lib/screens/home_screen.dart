import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme.dart';
import '../auth.dart';
import 'dashboard_screen.dart';
import 'schedule_screen.dart';
import 'reports_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'scan_screen.dart';

/// Role-based shell with a Bottom Navigation Bar (native mobile idiom,
/// replacing the web sidebar).
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _index = 0;

  List<_Tab> _tabsFor(String role) {
    final dash = _Tab('الرئيسية', Icons.dashboard_outlined, const DashboardScreen());
    final sched = _Tab('الجدول', Icons.calendar_month_outlined, const ScheduleScreen());
    final notifs = _Tab('الإشعارات', Icons.notifications_outlined, const NotificationsScreen());
    final profile = _Tab('حسابي', Icons.person_outline, const ProfileScreen());
    final reports = _Tab('التقارير', Icons.bar_chart_outlined, const ReportsScreen());
    final scan = _Tab('المسح', Icons.center_focus_strong_outlined, const ScanScreen());

    switch (role) {
      case 'admin':
      case 'coordinator':
        return [dash, scan, reports, notifs, profile];
      case 'teacher':
        return [dash, sched, scan, notifs, profile];
      case 'student':
        return [dash, sched, reports, notifs, profile];
      case 'gate':
        return [dash, scan, notifs, profile];
      default:
        return [dash, notifs, profile];
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final role = auth.role;
    final tabs = _tabsFor(role);
    if (_index >= tabs.length) _index = 0;

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 16,
        title: Row(children: [
          const Icon(Icons.shield_outlined, color: ShamelColors.gold, size: 22),
          const SizedBox(width: 8),
          const Text('SHAMEL', style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 1)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: ShamelTheme.roleColor(role),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(ShamelTheme.roleLabel(role),
                style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w700)),
          ),
        ]),
      ),
      body: IndexedStack(
        index: _index,
        children: tabs.map((t) => t.screen).toList(),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: tabs
            .map((t) => BottomNavigationBarItem(icon: Icon(t.icon), label: t.label))
            .toList(),
      ),
    );
  }
}

class _Tab {
  final String label;
  final IconData icon;
  final Widget screen;
  _Tab(this.label, this.icon, this.screen);
}
