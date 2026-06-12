import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

Widget _kv(BuildContext context, String k, dynamic v) {
  if (v == null || '$v'.isEmpty) return const SizedBox.shrink();
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 9),
    child: Row(children: [
      Text(k, style: TextStyle(color: ShamelColors.sec(context), fontSize: 13)),
      const Spacer(),
      Flexible(child: Text('$v', textAlign: TextAlign.left,
          style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary, fontSize: 14))),
    ]),
  );
}

class _DetailScaffold extends StatelessWidget {
  final String title;
  final Future<Map<String, dynamic>> future;
  final String dataKey;
  final List<Widget> Function(Map d) body;
  const _DetailScaffold({required this.title, required this.future, required this.dataKey, required this.body});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title, style: const TextStyle(fontWeight: FontWeight.w800))),
      body: FutureBuilder<Map<String, dynamic>>(
        future: future,
        builder: (ctx, snap) {
          if (!snap.hasData) return const LoadingOrError(loading: true);
          final r = snap.data!;
          if (r['ok'] != true) return LoadingOrError(loading: false, error: '${r['message'] ?? 'تعذّر التحميل'}');
          final d = (r[dataKey] ?? {}) as Map;
          return ListView(padding: const EdgeInsets.all(16), children: body(Map<String, dynamic>.from(d)));
        },
      ),
    );
  }
}

class TeacherDetailScreen extends StatelessWidget {
  final int teacherId;
  const TeacherDetailScreen({super.key, required this.teacherId});
  @override
  Widget build(BuildContext context) => _DetailScaffold(
        title: 'ملف الأستاذ', dataKey: 'teacher',
        future: Api.getJson('/api/v1/teachers/$teacherId'),
        body: (d) => [
          _Header(name: '${d['name']}', sub: '${d['degree'] ?? ''}', accent: ShamelColors.roleTeacher),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: StatCard(label: 'الجلسات', value: '${d['sessions'] ?? 0}', icon: Icons.event_note, accent: ShamelColors.roleTeacher)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'المواد', value: '${d['courses'] ?? 0}', icon: Icons.menu_book, accent: ShamelColors.gold)),
          ]),
          const SizedBox(height: 16),
          _Card(children: [
            _kv(context, 'التخصص', d['major']), _kv(context, 'القسم', d['department']),
            _kv(context, 'الكلية', d['college']), _kv(context, 'البريد', d['email']),
            _kv(context, 'الهاتف', d['phone']),
            _kv(context, 'دخول البوابة', d['allowed_entry'] == true ? 'مسموح' : 'موقوف'),
          ]),
        ],
      );
}

class StudentDetailScreen extends StatelessWidget {
  final int studentId;
  const StudentDetailScreen({super.key, required this.studentId});
  @override
  Widget build(BuildContext context) => _DetailScaffold(
        title: 'ملف الطالب', dataKey: 'student',
        future: Api.getJson('/api/v1/students/$studentId'),
        body: (d) => [
          _Header(name: '${d['name']}', sub: '${d['code'] ?? ''}', accent: ShamelColors.roleStudent),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: StatCard(label: 'نسبة الحضور', value: '${d['attendance_pct'] ?? 0}%', icon: Icons.percent, accent: ShamelColors.success)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'حاضر', value: '${d['present'] ?? 0}', icon: Icons.check_circle_outline, accent: ShamelColors.roleStudent)),
          ]),
          const SizedBox(height: 16),
          _Card(children: [
            _kv(context, 'الرقم الجامعي', d['code']), _kv(context, 'القسم', d['department']),
            _kv(context, 'الدفعة', d['batch']), _kv(context, 'البريد', d['email']), _kv(context, 'الهاتف', d['phone']),
            _kv(context, 'إجمالي السجلات', d['total_records']),
          ]),
        ],
      );
}

class _Header extends StatelessWidget {
  final String name, sub;
  final Color accent;
  const _Header({required this.name, required this.sub, required this.accent});
  @override
  Widget build(BuildContext context) => Row(children: [
        Container(
          width: 64, height: 64,
          decoration: BoxDecoration(color: accent.withValues(alpha: 0.15), shape: BoxShape.circle),
          child: Center(child: Text(name.isNotEmpty ? name[0] : '?',
              style: TextStyle(color: accent, fontSize: 28, fontWeight: FontWeight.w800))),
        ),
        const SizedBox(width: 14),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(name, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: ShamelColors.primary)),
          if (sub.isNotEmpty) Text(sub, style: TextStyle(color: ShamelColors.sec(context), fontSize: 13)),
        ])),
      ]);
}

class _Card extends StatelessWidget {
  final List<Widget> children;
  const _Card({required this.children});
  @override
  Widget build(BuildContext context) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 16),
        decoration: BoxDecoration(
          color: ShamelColors.surf(context), borderRadius: BorderRadius.circular(16),
          border: Border.all(color: ShamelColors.bord(context)),
        ),
        child: Column(children: children),
      );
}

// ── Ticket detail (view subject/body/status + admin reply) ─────────────────
class TicketDetailScreen extends StatelessWidget {
  final int ticketId;
  const TicketDetailScreen({super.key, required this.ticketId});

  Color _statusColor(String s) {
    final l = s.toLowerCase();
    if (l.contains('open')) return ShamelColors.warning;
    if (l.contains('closed') || l.contains('resolved')) return ShamelColors.success;
    return ShamelColors.roleTeacher;
  }

  @override
  Widget build(BuildContext context) => _DetailScaffold(
        title: 'تفاصيل البلاغ', dataKey: 'ticket',
        future: Api.getJson('/api/v1/tickets/$ticketId'),
        body: (d) {
          final status = '${d['status'] ?? ''}';
          return [
            Row(children: [
              Expanded(child: Text('${d['subject'] ?? ''}',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w800, color: ShamelColors.primary))),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(color: _statusColor(status).withValues(alpha: 0.12), borderRadius: BorderRadius.circular(20)),
                child: Text(status, style: TextStyle(color: _statusColor(status), fontSize: 12, fontWeight: FontWeight.w700)),
              ),
            ]),
            const SizedBox(height: 6),
            Text('${d['user'] ?? ''} • أولوية: ${d['priority'] ?? ''}',
                style: TextStyle(color: ShamelColors.sec(context), fontSize: 12)),
            const SizedBox(height: 16),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: ShamelColors.surf(context), borderRadius: BorderRadius.circular(14),
                border: Border.all(color: ShamelColors.bord(context)),
              ),
              child: Text('${d['body'] ?? ''}', style: TextStyle(color: ShamelColors.txt(context), height: 1.5)),
            ),
            if ('${d['reply'] ?? ''}'.isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text('رد الإدارة', style: TextStyle(fontWeight: FontWeight.w800, color: ShamelColors.primary)),
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: ShamelColors.success.withValues(alpha: 0.06),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: ShamelColors.success.withValues(alpha: 0.3)),
                ),
                child: Text('${d['reply']}', style: TextStyle(color: ShamelColors.txt(context), height: 1.5)),
              ),
            ],
          ];
        },
      );
}

// ── Global search ────────────────────────────────────────────────────────
class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});
  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  Map<String, dynamic> _res = {};
  bool _loading = false;

  Future<void> _search(String q) async {
    if (q.trim().length < 2) return;
    setState(() => _loading = true);
    try {
      _res = await Api.getJson('/api/v1/search?q=${Uri.encodeComponent(q.trim())}');
    } catch (_) {}
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    List sec(String k) => (_res[k] ?? []) as List;
    return Scaffold(
      appBar: AppBar(title: const Text('البحث الشامل', style: TextStyle(fontWeight: FontWeight.w800))),
      body: Column(children: [
        Padding(
          padding: const EdgeInsets.all(12),
          child: TextField(
            autofocus: true,
            decoration: const InputDecoration(hintText: 'ابحث عن طالب أو أستاذ أو مادة…', prefixIcon: Icon(Icons.search)),
            onSubmitted: _search,
          ),
        ),
        if (_loading) const LinearProgressIndicator(color: ShamelColors.gold),
        Expanded(child: ListView(padding: const EdgeInsets.all(12), children: [
          if (sec('students').isNotEmpty) const SectionTitle('الطلاب'),
          ...sec('students').map((s) => _row(Icons.school_outlined, ShamelColors.roleStudent, '${s['name']}', '${s['code']}')),
          if (sec('teachers').isNotEmpty) const SectionTitle('الأساتذة'),
          ...sec('teachers').map((t) => _row(Icons.groups_outlined, ShamelColors.roleTeacher, '${t['name']}', '')),
          if (sec('courses').isNotEmpty) const SectionTitle('المواد'),
          ...sec('courses').map((c) => _row(Icons.menu_book_outlined, ShamelColors.gold, '${c['title']}', '${c['code']}')),
        ])),
      ]),
    );
  }

  Widget _row(IconData ic, Color c, String t, String s) => Container(
        margin: const EdgeInsets.only(bottom: 8),
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(color: ShamelColors.surf(context), borderRadius: BorderRadius.circular(12), border: Border.all(color: ShamelColors.bord(context))),
        child: Row(children: [
          Icon(ic, color: c, size: 18), const SizedBox(width: 12),
          Expanded(child: Text(t, style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary))),
          if (s.isNotEmpty) Text(s, style: TextStyle(color: ShamelColors.sec(context), fontSize: 12)),
        ]),
      );
}

// ── Settings ─────────────────────────────────────────────────────────────
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الإعدادات', style: TextStyle(fontWeight: FontWeight.w800))),
      body: FutureBuilder<Map<String, dynamic>>(
        future: Api.getJson('/api/v1/settings'),
        builder: (ctx, snap) {
          if (!snap.hasData) return const LoadingOrError(loading: true);
          final s = (snap.data!['settings'] ?? {}) as Map;
          return ListView(padding: const EdgeInsets.all(16), children: [
            _Card(children: [
              _kv(context, 'الإصدار', s['version']),
              _kv(context, 'محرك التعرف على الوجه', s['face_engine']),
              _kv(context, 'الدور', ShamelTheme.roleLabel('${s['role']}')),
              _kv(context, 'عنوان الخادم', Api.baseUrl),
            ]),
          ]);
        },
      ),
    );
  }
}
