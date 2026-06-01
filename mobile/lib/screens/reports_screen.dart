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
  bool _loading = true;
  String? _error;
  Map<String, dynamic> _d = {};

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.reportsSummary();
      if (r['ok'] == true) {
        _d = r;
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
    final pct = (_d['avg_attendance'] ?? 0).toDouble();
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const SectionTitle('ملخّص الحضور'),
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: const Color(0xFFE8EAED)),
            ),
            child: Column(children: [
              SizedBox(
                width: 140, height: 140,
                child: Stack(alignment: Alignment.center, children: [
                  SizedBox(
                    width: 140, height: 140,
                    child: CircularProgressIndicator(
                      value: pct / 100,
                      strokeWidth: 12,
                      backgroundColor: ShamelColors.surfaceContainer,
                      valueColor: AlwaysStoppedAnimation(
                          pct >= 75 ? ShamelColors.success : (pct >= 50 ? ShamelColors.warning : ShamelColors.error)),
                    ),
                  ),
                  Column(mainAxisSize: MainAxisSize.min, children: [
                    Text('${pct.toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: ShamelColors.primary)),
                    const Text('متوسط الحضور', style: TextStyle(fontSize: 11, color: ShamelColors.secondary)),
                  ]),
                ]),
              ),
            ]),
          ),
          const SizedBox(height: 16),
          Row(children: [
            Expanded(child: StatCard(label: 'إجمالي السجلات', value: '${_d['total_records'] ?? 0}', icon: Icons.list_alt, accent: ShamelColors.primary)),
            const SizedBox(width: 12),
            Expanded(child: StatCard(label: 'حاضر', value: '${_d['present'] ?? 0}', icon: Icons.check_circle_outline, accent: ShamelColors.success)),
          ]),
          const SizedBox(height: 12),
          StatCard(label: 'حضور اليوم', value: '${_d['today'] ?? 0}', icon: Icons.today_outlined, accent: ShamelColors.roleCoordinator),
        ],
      ),
    );
  }
}
