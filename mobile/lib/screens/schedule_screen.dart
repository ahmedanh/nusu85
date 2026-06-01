import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});
  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  bool _loading = true;
  String? _error;
  List _rows = [];

  static const _dayAr = {
    'Saturday': 'السبت', 'Sunday': 'الأحد', 'Monday': 'الإثنين',
    'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة',
  };

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.schedule();
      if (r['ok'] == true) {
        _rows = (r['schedule'] ?? []) as List;
      } else {
        _error = 'تعذّر التحميل';
      }
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading || _error != null) {
      return LoadingOrError(loading: _loading, error: _error, onRetry: _load);
    }
    if (_rows.isEmpty) {
      return const Center(
        child: Padding(padding: EdgeInsets.all(40),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Icon(Icons.event_busy, size: 48, color: ShamelColors.outline),
            SizedBox(height: 12),
            Text('لا توجد محاضرات مجدولة', style: TextStyle(color: ShamelColors.secondary)),
          ])),
      );
    }
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _rows.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (_, i) {
          final r = _rows[i] as Map;
          return Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: const Color(0xFFE8EAED)),
            ),
            child: Row(children: [
              Container(
                width: 4, height: 48,
                decoration: BoxDecoration(color: ShamelColors.gold, borderRadius: BorderRadius.circular(4)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('${r['course'] ?? '—'}',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: ShamelColors.primary)),
                  const SizedBox(height: 4),
                  Text('${r['teacher'] ?? ''}  •  ${r['classroom'] ?? ''}',
                      style: const TextStyle(color: ShamelColors.secondary, fontSize: 12)),
                ]),
              ),
              Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                Text(_dayAr[r['day']] ?? '${r['day'] ?? ''}',
                    style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12, color: ShamelColors.primaryContainer)),
                const SizedBox(height: 4),
                Text('${_fmt(r['start'])} - ${_fmt(r['end'])}',
                    style: const TextStyle(color: ShamelColors.outline, fontSize: 11)),
              ]),
            ]),
          );
        },
      ),
    );
  }

  String _fmt(dynamic t) {
    final s = '$t';
    return s.length >= 5 ? s.substring(0, 5) : s;
  }
}
