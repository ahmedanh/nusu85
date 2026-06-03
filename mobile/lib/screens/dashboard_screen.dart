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

  // Coordinator-specific KPIs (academic focus, college-scoped)
  int _pendingExcuses = 0;
  String _collegeName = '';

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.dashboard();
      if (r['ok'] == true) {
        _data = (r['data'] ?? {}) as Map<String, dynamic>;
        _collegeName = '${_data['college_name'] ?? ''}';
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
      final role = (_data['role'] ?? '') as String;

      if (role == 'admin') {
        // Admin: global infra metrics (rooms + system tickets)
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
        } catch (_) {}
      } else if (role == 'coordinator') {
        // Coordinator: academic KPIs scoped to their college
        try {
          final ex = await Api.getJson('/api/v1/excuses');
          if (ex['ok'] == true) {
            _pendingExcuses = ((ex['excuses'] ?? []) as List)
                .where((e) => '${(e as Map)['status']}' == 'pending').length;
          }
          final tk = await Api.getJson('/api/v1/tickets');
          if (tk['ok'] == true) {
            _openTickets = ((tk['tickets'] ?? []) as List)
                .where((t) => '${(t as Map)['status']}'.toLowerCase().contains('open')).length;
          }
        } catch (_) {}
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
        // Global infrastructure view
        return [
          StatCard(label: 'الطلاب (كل الجامعة)', value: s(_data['students']), icon: Icons.school_outlined, accent: ShamelColors.roleStudent),
          StatCard(label: 'الأساتذة', value: s(_data['teachers']), icon: Icons.groups_outlined, accent: ShamelColors.roleTeacher),
          StatCard(label: 'المواد', value: s(_data['courses']), icon: Icons.menu_book_outlined, accent: ShamelColors.gold),
          StatCard(label: 'القاعات', value: s(_data['classrooms']), icon: Icons.meeting_room_outlined, accent: ShamelColors.primary),
          StatCard(label: 'جلسات نشطة', value: s(_data['active_sessions']), icon: Icons.sensors, accent: ShamelColors.success),
          StatCard(label: 'حضور اليوم', value: s(_data['attendance_today']), icon: Icons.how_to_reg_outlined, accent: ShamelColors.roleCoordinator),
        ];
      case 'coordinator':
        // Academic KPIs scoped to coordinator's college
        return [
          StatCard(label: 'طلاب الكلية', value: s(_data['students']), icon: Icons.school_outlined, accent: ShamelColors.roleStudent),
          StatCard(label: 'أساتذة الكلية', value: s(_data['teachers']), icon: Icons.groups_outlined, accent: ShamelColors.roleTeacher),
          StatCard(label: 'المواد', value: s(_data['courses']), icon: Icons.menu_book_outlined, accent: ShamelColors.gold),
          StatCard(label: 'حضور اليوم', value: s(_data['attendance_today']), icon: Icons.how_to_reg_outlined, accent: ShamelColors.success),
          StatCard(label: 'أعذار معلقة', value: '$_pendingExcuses', icon: Icons.medical_services_outlined, accent: ShamelColors.warning),
          StatCard(label: 'تذاكر مفتوحة', value: '$_openTickets', icon: Icons.support_agent_outlined, accent: ShamelColors.error),
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
          // ── Role-specific extras ───────────────────────────────────
          if (auth.role == 'admin') ...[
            const SizedBox(height: 24),
            const SectionTitle('إجراءات سريعة'),
            _quickActionsAdmin(context),
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
          ] else if (auth.role == 'coordinator') ...[
            // College header banner
            if (_collegeName.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: ShamelColors.roleCoordinator.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: ShamelColors.roleCoordinator.withValues(alpha: 0.3)),
                ),
                child: Row(children: [
                  const Icon(Icons.account_balance_outlined, color: ShamelColors.roleCoordinator, size: 18),
                  const SizedBox(width: 8),
                  Text(_collegeName, style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.roleCoordinator)),
                ]),
              ),
            ],
            const SizedBox(height: 24),
            const SectionTitle('الإجراءات الأكاديمية'),
            _quickActionsCoordinator(context),
            // Pending excuses alert
            if (_pendingExcuses > 0) ...[
              const SizedBox(height: 16),
              _alertCard(
                icon: Icons.medical_services_outlined,
                color: ShamelColors.warning,
                title: 'أعذار طبية تنتظر الموافقة',
                count: _pendingExcuses,
              ),
            ],
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

  Widget _buildQuickGrid(List<(String, IconData, Color)> items) {
    return GridView.count(
      crossAxisCount: 2, shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      childAspectRatio: 2.8, crossAxisSpacing: 12, mainAxisSpacing: 12,
      children: items.map((it) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 14),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFE8EAED)),
        ),
        child: Row(children: [
          Icon(it.$2, color: it.$3, size: 20),
          const SizedBox(width: 10),
          Expanded(child: Text(it.$1,
              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: ShamelColors.primary))),
        ]),
      )).toList(),
    );
  }

  /// Admin quick actions — infrastructure / system focus
  Widget _quickActionsAdmin(BuildContext context) => _buildQuickGrid([
    ('مسح الوجه',     Icons.center_focus_strong_outlined, ShamelColors.gold),
    ('سجلات البوابة', Icons.sensor_door_outlined,         ShamelColors.roleGate),
    ('التقارير',      Icons.bar_chart_outlined,            ShamelColors.roleTeacher),
    ('سجل التدقيق',   Icons.manage_search_outlined,       ShamelColors.roleCoordinator),
  ]);

  /// Coordinator quick actions — academic / college-scoped focus
  Widget _quickActionsCoordinator(BuildContext context) => _buildQuickGrid([
    ('الأعذار الطبية', Icons.medical_services_outlined, ShamelColors.warning),
    ('الامتحانات',     Icons.event_note_outlined,        ShamelColors.gold),
    ('إدخال الدرجات', Icons.grade_outlined,              ShamelColors.roleTeacher),
    ('التقارير',       Icons.bar_chart_outlined,          ShamelColors.roleCoordinator),
  ]);

  Widget _alertCard({required IconData icon, required Color color, required String title, required int count}) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: color.withValues(alpha: 0.35)),
      ),
      child: Row(children: [
        Icon(icon, color: color, size: 22),
        const SizedBox(width: 12),
        Expanded(child: Text(title,
            style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 13))),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
          decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(20)),
          child: Text('$count', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 13)),
        ),
      ]),
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
