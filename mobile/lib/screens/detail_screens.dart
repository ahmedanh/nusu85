import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

Widget _kv(String k, dynamic v) {
  if (v == null || '$v'.isEmpty) return const SizedBox.shrink();
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 9),
    child: Row(children: [
      Text(k, style: const TextStyle(color: ShamelColors.secondary, fontSize: 13)),
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
            _kv('التخصص', d['major']), _kv('القسم', d['department']),
            _kv('الكلية', d['college']), _kv('البريد', d['email']),
            _kv('الهاتف', d['phone']),
            _kv('دخول البوابة', d['allowed_entry'] == true ? 'مسموح' : 'موقوف'),
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
            _kv('الرقم الجامعي', d['code']), _kv('القسم', d['department']),
            _kv('الدفعة', d['batch']), _kv('البريد', d['email']), _kv('الهاتف', d['phone']),
            _kv('إجمالي السجلات', d['total_records']),
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
          if (sub.isNotEmpty) Text(sub, style: const TextStyle(color: ShamelColors.secondary, fontSize: 13)),
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
          color: Colors.white, borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFE8EAED)),
        ),
        child: Column(children: children),
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
        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12), border: Border.all(color: const Color(0xFFE8EAED))),
        child: Row(children: [
          Icon(ic, color: c, size: 18), const SizedBox(width: 12),
          Expanded(child: Text(t, style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary))),
          if (s.isNotEmpty) Text(s, style: const TextStyle(color: ShamelColors.secondary, fontSize: 12)),
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
              _kv('الإصدار', s['version']),
              _kv('محرك التعرف على الوجه', s['face_engine']),
              _kv('الدور', ShamelTheme.roleLabel('${s['role']}')),
              _kv('عنوان الخادم', Api.baseUrl),
            ]),
          ]);
        },
      ),
    );
  }
}
