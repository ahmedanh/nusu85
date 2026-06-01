import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../api.dart';
import '../auth.dart';
import '../theme.dart';
import '../widgets.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});
  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  bool _loading = true;
  String? _error;
  Map<String, dynamic> _data = {};

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.dashboard();
      if (r['ok'] == true) {
        _data = (r['data'] ?? {}) as Map<String, dynamic>;
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  List<Widget> _cards(String role) {
    String s(dynamic v) => '${v ?? 0}';
    switch (role) {
      case 'admin':
      case 'coordinator':
        return [
          StatCard(label: 'الطلاب', value: s(_data['students']), icon: Icons.school_outlined, accent: ShamelColors.roleStudent),
          StatCard(label: 'الأساتذة', value: s(_data['teachers']), icon: Icons.groups_outlined, accent: ShamelColors.roleTeacher),
          StatCard(label: 'المواد', value: s(_data['courses']), icon: Icons.menu_book_outlined, accent: ShamelColors.gold),
          StatCard(label: 'القاعات', value: s(_data['classrooms']), icon: Icons.meeting_room_outlined, accent: ShamelColors.primary),
          StatCard(label: 'جلسات نشطة', value: s(_data['active_sessions']), icon: Icons.sensors, accent: ShamelColors.success),
          StatCard(label: 'حضور اليوم', value: s(_data['attendance_today']), icon: Icons.how_to_reg_outlined, accent: ShamelColors.roleCoordinator),
        ];
      case 'teacher':
        return [
          StatCard(label: 'موادي', value: s(_data['my_courses']), icon: Icons.menu_book_outlined, accent: ShamelColors.gold),
          StatCard(label: 'جلساتي', value: s(_data['my_sessions']), icon: Icons.event_note_outlined, accent: ShamelColors.roleTeacher),
          StatCard(label: 'جلسات نشطة', value: s(_data['active_sessions']), icon: Icons.sensors, accent: ShamelColors.success),
        ];
      case 'student':
        return [
          StatCard(label: 'نسبة الحضور', value: '${_data['attendance_pct'] ?? 0}%', icon: Icons.percent, accent: ShamelColors.success),
          StatCard(label: 'حاضر', value: s(_data['present']), icon: Icons.check_circle_outline, accent: ShamelColors.roleStudent),
          StatCard(label: 'إجمالي السجلات', value: s(_data['total_records']), icon: Icons.list_alt_outlined, accent: ShamelColors.primary),
        ];
      default:
        return [];
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    if (_loading || _error != null) {
      return LoadingOrError(loading: _loading, error: _error, onRetry: _load);
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [ShamelColors.navy, ShamelColors.primaryContainer],
                begin: Alignment.topRight, end: Alignment.bottomLeft,
              ),
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('أهلاً، ${auth.name}',
                  style: const TextStyle(color: Colors.white, fontSize: 20, fontWeight: FontWeight.w800)),
              const SizedBox(height: 4),
              Text(ShamelTheme.roleLabel(auth.role),
                  style: const TextStyle(color: ShamelColors.goldLight, fontSize: 13, fontWeight: FontWeight.w600)),
            ]),
          ),
          const SizedBox(height: 20),
          const SectionTitle('نظرة عامة'),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            childAspectRatio: 1.55,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            children: _cards(auth.role),
          ),
        ],
      ),
    );
  }
}
