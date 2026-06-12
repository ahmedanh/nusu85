import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  bool _loading = true;
  String? _error;
  List _rows = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.notifications();
      if (r['ok'] == true) {
        _rows = (r['notifications'] ?? []) as List;
      } else {
        _error = 'تعذّر التحميل';
      }
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  Color _levelColor(String lvl) {
    switch (lvl) {
      case 'error': return ShamelColors.error;
      case 'warning': return ShamelColors.warning;
      case 'success': return ShamelColors.success;
      default: return ShamelColors.roleTeacher;
    }
  }

  IconData _levelIcon(String lvl) {
    switch (lvl) {
      case 'error': return Icons.error_outline;
      case 'warning': return Icons.warning_amber_outlined;
      case 'success': return Icons.check_circle_outline;
      default: return Icons.info_outline;
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading || _error != null) {
      return LoadingOrError(loading: _loading, error: _error, onRetry: _load);
    }
    if (_rows.isEmpty) {
      return Center(
        child: Padding(padding: EdgeInsets.all(40),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Icon(Icons.notifications_none, size: 48, color: ShamelColors.sub(context)),
            SizedBox(height: 12),
            Text('لا توجد إشعارات', style: TextStyle(color: ShamelColors.sec(context))),
          ])),
      );
    }
    return Column(children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
        child: Row(children: [
          const Spacer(),
          TextButton.icon(
            onPressed: () async {
              await Api.markNotificationsRead();
              _load();
            },
            icon: const Icon(Icons.done_all, size: 18),
            label: const Text('تعليم الكل كمقروء'),
          ),
        ]),
      ),
      Expanded(
        child: RefreshIndicator(
          onRefresh: _load,
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: _rows.length,
            separatorBuilder: (_, __) => const SizedBox(height: 10),
            itemBuilder: (_, i) {
              final n = _rows[i] as Map;
              final lvl = '${n['level'] ?? 'info'}';
              final read = n['is_read'] == true;
              return Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: read ? ShamelColors.surf(context) : _levelColor(lvl).withValues(alpha: 0.05),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: read ? ShamelColors.bord(context) : _levelColor(lvl).withValues(alpha: 0.3)),
                ),
                child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Icon(_levelIcon(lvl), color: _levelColor(lvl), size: 22),
                  const SizedBox(width: 12),
                  Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    if ('${n['title'] ?? ''}'.isNotEmpty)
                      Text('${n['title']}', style: const TextStyle(fontWeight: FontWeight.w700, color: ShamelColors.primary, fontSize: 14)),
                    Text('${n['body'] ?? ''}', style: TextStyle(color: ShamelColors.sec(context), fontSize: 13)),
                  ])),
                ]),
              );
            },
          ),
        ),
      ),
    ]);
  }
}
