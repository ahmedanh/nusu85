import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

/// Attendance logs with status colour coding + confidence.
class AttendanceLogsScreen extends StatefulWidget {
  const AttendanceLogsScreen({super.key});
  @override
  State<AttendanceLogsScreen> createState() => _AttendanceLogsScreenState();
}

class _AttendanceLogsScreenState extends State<AttendanceLogsScreen> {
  bool _loading = true;
  String? _error;
  List _rows = [];
  int _total = 0;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.getJson('/api/v1/attendance-logs');
      if (r['ok'] == true) {
        _rows = (r['logs'] ?? []) as List;
        _total = (r['total'] ?? _rows.length) as int;
      } else {
        _error = 'تعذّر التحميل';
      }
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  Color _statusColor(String s) {
    final l = s.toLowerCase();
    if (l.contains('present') || l.contains('حاضر')) return ShamelColors.success;
    if (l.contains('flag') || l.contains('late')) return ShamelColors.warning;
    return ShamelColors.error;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('سجلات الحضور', style: TextStyle(fontWeight: FontWeight.w800))),
      body: (_loading || _error != null)
          ? LoadingOrError(loading: _loading, error: _error, onRetry: _load)
          : Column(children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(children: [
                  const Icon(Icons.fact_check_outlined, size: 16, color: ShamelColors.primary),
                  const SizedBox(width: 6),
                  Text('$_total سجل', style: const TextStyle(color: ShamelColors.secondary, fontWeight: FontWeight.w700, fontSize: 12)),
                ]),
              ),
              Expanded(
                child: RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.separated(
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: _rows.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (_, i) {
                      final l = _rows[i] as Map;
                      final st = '${l['status'] ?? ''}';
                      final conf = l['confidence'];
                      return Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white, borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFFE8EAED)),
                        ),
                        child: Row(children: [
                          Container(width: 4, height: 40,
                              decoration: BoxDecoration(color: _statusColor(st), borderRadius: BorderRadius.circular(4))),
                          const SizedBox(width: 12),
                          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            Text('${l['student'] ?? '—'}', style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary)),
                            Text('${l['course'] ?? ''}', maxLines: 1, overflow: TextOverflow.ellipsis,
                                style: const TextStyle(color: ShamelColors.secondary, fontSize: 12)),
                          ])),
                          Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(color: _statusColor(st).withValues(alpha: 0.12), borderRadius: BorderRadius.circular(8)),
                              child: Text(st, style: TextStyle(color: _statusColor(st), fontSize: 11, fontWeight: FontWeight.w700)),
                            ),
                            if (conf != null)
                              Padding(padding: const EdgeInsets.only(top: 4),
                                  child: Text('${(conf is num ? (conf * 100).toStringAsFixed(0) : conf)}%',
                                      style: const TextStyle(color: ShamelColors.outline, fontSize: 11))),
                          ]),
                        ]),
                      );
                    },
                  ),
                ),
              ),
            ]),
    );
  }
}
