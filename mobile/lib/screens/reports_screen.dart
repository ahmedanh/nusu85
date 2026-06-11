import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

class ReportsScreen extends StatefulWidget {
  const ReportsScreen({super.key});
  @override
  State<ReportsScreen> createState() => _ReportsScreenState();
}

class _ReportsScreenState extends State<ReportsScreen> {
  bool   _loading = true;
  String? _error;
  Map<String, dynamic> _d = {};
  DateTime? _from;
  DateTime? _to;

  @override
  void initState() { super.initState(); _load(); }

  String _fmt(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2,'0')}-${d.day.toString().padLeft(2,'0')}';

  String _fmtAr(DateTime d) =>
      '${d.day}/${d.month}/${d.year}';

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final params = <String, String>{};
      if (_from != null) params['date_from'] = _fmt(_from!);
      if (_to   != null) params['date_to']   = _fmt(_to!);
      final query = params.isEmpty ? '' :
          '?${params.entries.map((e) => '${e.key}=${e.value}').join('&')}';
      final r = await Api.getJson('/api/v1/reports/summary$query');
      if (!mounted) return;
      if (r['ok'] == true) {
        _d = r;
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
    } on AuthException catch (e) {
      _error = e.message;
    } on ApiException catch (e) {
      _error = e.message;
    } catch (_) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  Future<void> _pickDate(bool isFrom) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: (isFrom ? _from : _to) ?? now,
      firstDate: DateTime(now.year - 2),
      lastDate: now,
    );
    if (picked == null || !mounted) return;
    setState(() => isFrom ? _from = picked : _to = picked);
    _load();
  }

  void _clearDates() {
    setState(() { _from = null; _to = null; });
    _load();
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const LoadingOrError(loading: true, skeleton: false);
    if (_error != null) {
      return LoadingOrError(loading: false, error: _error, onRetry: _load);
    }

    final pct     = (_d['avg_attendance'] ?? 0).toDouble();
    final present = (_d['present']       ?? 0) as int;
    final total   = (_d['total_records'] ?? 0) as int;
    final absent  = total - present;
    final today   = (_d['today']         ?? 0) as int;

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [

          // ── Date range filter ───────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Theme.of(context).brightness == Brightness.dark
                  ? ShamelColors.surfaceDark : Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                  color: Theme.of(context).brightness == Brightness.dark
                      ? ShamelColors.borderDark : ShamelColors.borderLight),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  const Icon(Icons.date_range_outlined,
                      size: 16, color: ShamelColors.gold),
                  const SizedBox(width: 6),
                  const Text('نطاق التاريخ',
                      style: TextStyle(
                          fontWeight: FontWeight.w700, fontSize: 13,
                          color: ShamelColors.secondary)),
                  const Spacer(),
                  if (_from != null || _to != null)
                    TextButton(
                      onPressed: _clearDates,
                      style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 6),
                          minimumSize: const Size(0, 28)),
                      child: const Text('مسح',
                          style: TextStyle(
                              color: ShamelColors.gold, fontSize: 12)),
                    ),
                ]),
                const SizedBox(height: 10),
                Row(children: [
                  Expanded(child: _DateBtn(
                    label: _from != null ? _fmtAr(_from!) : 'من تاريخ',
                    active: _from != null,
                    onTap: () => _pickDate(true),
                  )),
                  const SizedBox(width: 10),
                  Expanded(child: _DateBtn(
                    label: _to != null ? _fmtAr(_to!) : 'إلى تاريخ',
                    active: _to != null,
                    onTap: () => _pickDate(false),
                  )),
                ]),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // ── Attendance ring ─────────────────────────────────────────────
          const SectionTitle('ملخّص الحضور'),
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).brightness == Brightness.dark
                  ? ShamelColors.surfaceDark : Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(
                  color: Theme.of(context).brightness == Brightness.dark
                      ? ShamelColors.borderDark : ShamelColors.borderLight),
            ),
            child: Column(children: [
              SizedBox(
                width: 150, height: 150,
                child: Stack(alignment: Alignment.center, children: [
                  SizedBox(
                    width: 150, height: 150,
                    child: CircularProgressIndicator(
                      value: pct / 100,
                      strokeWidth: 14,
                      backgroundColor: ShamelColors.surfaceContainer,
                      valueColor: AlwaysStoppedAnimation(
                          pct >= 75 ? ShamelColors.success
                              : (pct >= 50 ? ShamelColors.warning
                                  : ShamelColors.error)),
                    ),
                  ),
                  Column(mainAxisSize: MainAxisSize.min, children: [
                    Text('${pct.toStringAsFixed(1)}%',
                        style: const TextStyle(
                            fontSize: 30, fontWeight: FontWeight.w800,
                            color: ShamelColors.primary)),
                    const Text('متوسط الحضور',
                        style: TextStyle(
                            fontSize: 11, color: ShamelColors.secondary)),
                  ]),
                ]),
              ),
            ]),
          ),
          const SizedBox(height: 16),

          // ── Stats grid ───────────────────────────────────────────────────
          Row(children: [
            Expanded(child: StatCard(
                label: 'إجمالي السجلات', value: '$total',
                icon: Icons.list_alt, accent: ShamelColors.primary)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(
                label: 'حاضر', value: '$present',
                icon: Icons.check_circle_outline, accent: ShamelColors.success)),
          ]),
          const SizedBox(height: 12),
          Row(children: [
            Expanded(child: StatCard(
                label: 'غائب', value: '$absent',
                icon: Icons.cancel_outlined, accent: ShamelColors.error)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(
                label: 'حضور اليوم', value: '$today',
                icon: Icons.today_outlined, accent: ShamelColors.gold)),
          ]),
          const SizedBox(height: 16),

          // ── Per-course breakdown (if API returns it) ──────────────────
          if (_d['courses'] != null) ...[
            const SectionTitle('تفصيل حسب المقرر'),
            ...(_d['courses'] as List).map((c) {
              final m = c as Map;
              final cp = (m['attendance_pct'] ?? 0).toDouble();
              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 12),
                  decoration: BoxDecoration(
                    color: Theme.of(context).brightness == Brightness.dark
                        ? ShamelColors.surfaceDark : Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                        color: Theme.of(context).brightness == Brightness.dark
                            ? ShamelColors.borderDark : ShamelColors.borderLight),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('${m['course'] ?? m['name'] ?? ''}',
                          style: const TextStyle(
                              fontWeight: FontWeight.w700,
                              color: ShamelColors.primary)),
                      const SizedBox(height: 8),
                      Row(children: [
                        Expanded(child: ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: cp / 100,
                            minHeight: 6,
                            backgroundColor: ShamelColors.surfaceContainer,
                            valueColor: AlwaysStoppedAnimation(
                                cp >= 75 ? ShamelColors.success
                                    : (cp >= 50 ? ShamelColors.warning
                                        : ShamelColors.error)),
                          ),
                        )),
                        const SizedBox(width: 10),
                        Text('${cp.toStringAsFixed(0)}%',
                            style: TextStyle(
                                fontWeight: FontWeight.w800, fontSize: 12,
                                color: cp >= 75 ? ShamelColors.success
                                    : (cp >= 50 ? ShamelColors.warning
                                        : ShamelColors.error))),
                      ]),
                    ],
                  ),
                ),
              );
            }),
          ],
        ],
      ),
    );
  }
}

class _DateBtn extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;
  const _DateBtn({required this.label, required this.active, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
        decoration: BoxDecoration(
          color: active
              ? ShamelColors.gold.withValues(alpha: 0.10)
              : ShamelColors.surfaceContainer.withValues(alpha: 0.5),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
              color: active
                  ? ShamelColors.gold.withValues(alpha: 0.40)
                  : ShamelColors.outline.withValues(alpha: 0.20)),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.calendar_today_outlined,
              size: 14,
              color: active ? ShamelColors.gold : ShamelColors.outline),
          const SizedBox(width: 6),
          Flexible(child: Text(label,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                  fontSize: 12, fontWeight: FontWeight.w600,
                  color: active ? ShamelColors.gold : ShamelColors.outline))),
        ]),
      ),
    );
  }
}
