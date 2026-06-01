import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

/// Generic list screen — renders any /api/v1 list endpoint. One reusable
/// widget covers courses, classrooms, departments, teachers, students,
/// tickets, attendance-logs, gate-logs, audit-log, exams, etc.
class ResourceListScreen extends StatefulWidget {
  final String title;
  final String endpoint;        // e.g. /api/v1/courses
  final String listKey;         // e.g. 'courses'
  final IconData icon;
  final Color accent;
  final bool searchable;
  final String Function(Map item) titleOf;
  final String Function(Map item)? subtitleOf;
  final String Function(Map item)? trailingOf;
  final void Function(BuildContext, Map item)? onTap;
  final Widget? fab;

  const ResourceListScreen({
    super.key,
    required this.title,
    required this.endpoint,
    required this.listKey,
    required this.icon,
    required this.accent,
    required this.titleOf,
    this.subtitleOf,
    this.trailingOf,
    this.onTap,
    this.searchable = false,
    this.fab,
  });

  @override
  State<ResourceListScreen> createState() => _ResourceListScreenState();
}

class _ResourceListScreenState extends State<ResourceListScreen> {
  bool _loading = true;
  String? _error;
  List _items = [];
  int _total = 0;
  String _q = '';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final sep = widget.endpoint.contains('?') ? '&' : '?';
      final path = _q.isEmpty ? widget.endpoint : '${widget.endpoint}${sep}q=${Uri.encodeComponent(_q)}';
      final r = await Api.getJson(path);
      if (r['ok'] == true) {
        _items = (r[widget.listKey] ?? []) as List;
        _total = (r['total'] ?? _items.length) as int;
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title, style: const TextStyle(fontWeight: FontWeight.w800)),
      ),
      floatingActionButton: widget.fab,
      body: Column(children: [
        if (widget.searchable)
          Padding(
            padding: const EdgeInsets.all(12),
            child: TextField(
              decoration: InputDecoration(
                hintText: 'بحث في ${widget.title}…',
                prefixIcon: const Icon(Icons.search, color: ShamelColors.outline),
              ),
              onSubmitted: (v) { _q = v.trim(); _load(); },
            ),
          ),
        if (!_loading && _error == null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(children: [
              Icon(widget.icon, size: 16, color: widget.accent),
              const SizedBox(width: 6),
              Text('$_total عنصر', style: const TextStyle(color: ShamelColors.secondary, fontSize: 12, fontWeight: FontWeight.w700)),
            ]),
          ),
        Expanded(
          child: (_loading || _error != null)
              ? LoadingOrError(loading: _loading, error: _error, onRetry: _load)
              : _items.isEmpty
                  ? Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
                      Icon(widget.icon, size: 48, color: ShamelColors.outline),
                      const SizedBox(height: 12),
                      const Text('لا توجد بيانات', style: TextStyle(color: ShamelColors.secondary)),
                    ]))
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        padding: const EdgeInsets.all(12),
                        itemCount: _items.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (_, i) {
                          final it = _items[i] as Map;
                          return InkWell(
                            onTap: widget.onTap == null ? null : () => widget.onTap!(context, it),
                            borderRadius: BorderRadius.circular(14),
                            child: Container(
                              padding: const EdgeInsets.all(14),
                              decoration: BoxDecoration(
                                color: Colors.white,
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(color: const Color(0xFFE8EAED)),
                              ),
                              child: Row(children: [
                                Container(
                                  padding: const EdgeInsets.all(8),
                                  decoration: BoxDecoration(color: widget.accent.withValues(alpha: 0.12), borderRadius: BorderRadius.circular(10)),
                                  child: Icon(widget.icon, color: widget.accent, size: 18),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                                  Text(widget.titleOf(it), maxLines: 1, overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: ShamelColors.primary)),
                                  if (widget.subtitleOf != null && widget.subtitleOf!(it).isNotEmpty) ...[
                                    const SizedBox(height: 2),
                                    Text(widget.subtitleOf!(it), maxLines: 1, overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(color: ShamelColors.secondary, fontSize: 12)),
                                  ],
                                ])),
                                if (widget.trailingOf != null)
                                  Text(widget.trailingOf!(it),
                                      style: TextStyle(fontWeight: FontWeight.w800, fontSize: 12, color: widget.accent)),
                                if (widget.onTap != null)
                                  const Icon(Icons.chevron_left, color: ShamelColors.outline),
                              ]),
                            ),
                          );
                        },
                      ),
                    ),
        ),
      ]),
    );
  }
}
