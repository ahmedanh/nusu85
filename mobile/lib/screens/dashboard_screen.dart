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
  List _rooms = [];
  int _busyRooms = 0, _freeRooms = 0;
  int _openTickets = 0;

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
      // Mirror the web Chancellor panel: room status + open tickets.
      final role = (_data['role'] ?? '') as String;
      if (role == 'admin' || role == 'coordinator') {
        try {
          final rs = await Api.getJson('/api/v1/classrooms/status');
          if (rs['ok'] == true) {
            _rooms = (rs['classrooms'] ?? []) as List;
            _busyRooms = (rs['busy'] ?? 0) as int;
            _freeRooms = (rs['free'] ?? 0) as int;
          }
          final tk = await Api.getJson('/api/v1/tickets');
          if (tk['ok'] == true) {
            _openTickets = ((tk['tickets'] ?? []) as List)
                .where((t) => '${(t as Map)['status']}'.toLowerCase().contains('open')).length;
          }
        } catch (_) {/* keep dashboard usable if these fail */}
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
          // ── Chancellor-panel parity: admin/coordinator extras ──
          if (auth.role == 'admin' || auth.role == 'coordinator') ...[
            const SizedBox(height: 24),
            const SectionTitle('إجراءات سريعة'),
            _quickActions(context),
            if (_rooms.isNotEmpty) ...[
              const SizedBox(height: 24),
              Row(children: [
                const SectionTitle('حالة القاعات'),
                const Spacer(),
                _pill('متاحة $_freeRooms', ShamelColors.success),
                const SizedBox(width: 6),
                _pill('مشغولة $_busyRooms', ShamelColors.error),
              ]),
              _roomStatus(),
            ],
            const SizedBox(height: 24),
            _openTicketsCard(),
          ],
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  Widget _pill(String text, Color c) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(color: c.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(20)),
        child: Text(text, style: TextStyle(color: c, fontSize: 11, fontWeight: FontWeight.w700)),
      );

  Widget _quickActions(BuildContext context) {
    final items = [
      ('تقرير الطلاب', Icons.person_search_outlined, ShamelColors.roleStudent, 2),  // → Reports tab
      ('المسح', Icons.center_focus_strong_outlined, ShamelColors.gold, 1),          // → Scan tab
      ('التقارير', Icons.bar_chart_outlined, ShamelColors.roleTeacher, 2),
      ('الإشعارات', Icons.notifications_outlined, ShamelColors.roleCoordinator, 3),
    ];
    return GridView.count(
      crossAxisCount: 2, shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 2.8, crossAxisSpacing: 12, mainAxisSpacing: 12,
      children: items.map((it) => InkWell(
        borderRadius: BorderRadius.circular(14),
        onTap: () {/* tabs are managed by HomeScreen; users use bottom nav */},
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14),
          decoration: BoxDecoration(
            color: Colors.white, borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFFE8EAED)),
          ),
          child: Row(children: [
            Icon(it.$2, color: it.$3, size: 20),
            const SizedBox(width: 10),
            Expanded(child: Text(it.$1, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: ShamelColors.primary))),
          ]),
        ),
      )).toList(),
    );
  }

  Widget _roomStatus() {
    final show = _rooms.take(6).toList();
    return Column(children: show.map((r) {
      final m = r as Map;
      final busy = m['is_busy'] == true;
      return Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white, borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE8EAED)),
        ),
        child: Row(children: [
          Icon(Icons.meeting_room_outlined, size: 18, color: busy ? ShamelColors.error : ShamelColors.success),
          const SizedBox(width: 10),
          Expanded(child: Text('${m['name'] ?? ''}', style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: ShamelColors.primary))),
          _pill(busy ? 'مشغولة' : 'متاحة', busy ? ShamelColors.error : ShamelColors.success),
        ]),
      );
    }).toList());
  }

  Widget _openTicketsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8EAED)),
      ),
      child: Row(children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(color: ShamelColors.warning.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(12)),
          child: const Icon(Icons.support_agent_outlined, color: ShamelColors.warning),
        ),
        const SizedBox(width: 12),
        const Expanded(child: Text('التذاكر المفتوحة', style: TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary))),
        Text('$_openTickets', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: ShamelColors.warning)),
      ]),
    );
  }
}
