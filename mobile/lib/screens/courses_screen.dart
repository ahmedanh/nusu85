import 'dart:async';
import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';
import 'create_screens.dart';

/// Courses list with college-scope toggle for student role.
class CoursesScreen extends StatefulWidget {
  /// When true: defaults to "mine" scope (student's college only) + no add FAB.
  final bool studentMode;
  const CoursesScreen({super.key, this.studentMode = false});

  @override
  State<CoursesScreen> createState() => _CoursesScreenState();
}

class _CoursesScreenState extends State<CoursesScreen> {
  static const _pageSize = 50;

  bool   _loading     = true;
  bool   _loadingMore = false;
  String? _error;
  List   _items       = [];
  int    _total       = 0;
  int    _page        = 1;
  bool   _hasMore     = false;
  String _q           = '';
  // 'mine' = college-scoped, 'all' = entire university
  String _scope       = 'mine';

  final _ctrl = TextEditingController();
  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    _scope = widget.studentMode ? 'mine' : 'all';
    _load();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _ctrl.dispose();
    super.dispose();
  }

  String _buildPath(int page) {
    final params = <String>[
      'scope=$_scope',
      'page=$page',
      'page_size=$_pageSize',
    ];
    if (_q.isNotEmpty) params.add('q=${Uri.encodeComponent(_q)}');
    return '/api/v1/courses?${params.join('&')}';
  }

  Future<void> _load({bool reset = true}) async {
    if (reset) setState(() { _loading = true; _error = null; _page = 1; _items = []; });
    try {
      final r = await Api.getJson(_buildPath(_page));
      if (!mounted) return;
      if (r['ok'] == true) {
        final fetched = (r['courses'] ?? []) as List;
        _total = (r['total'] ?? fetched.length) as int;
        _items = reset ? fetched : [..._items, ...fetched];
        _hasMore = _items.length < _total;
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
    } catch (_) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() { _loading = false; _loadingMore = false; });
  }

  Future<void> _loadMore() async {
    if (_loadingMore || !_hasMore) return;
    setState(() { _loadingMore = true; _page++; });
    await _load(reset: false);
  }

  void _onSearch(String v) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 320), () {
      if (_q == v.trim()) return;
      _q = v.trim();
      _load();
    });
  }

  void _setScope(String s) {
    if (_scope == s) return;
    setState(() => _scope = s);
    _load();
  }

  @override
  Widget build(BuildContext context) {
    final dark   = Theme.of(context).brightness == Brightness.dark;
    final cardBg = dark ? ShamelColors.surfaceDark : Colors.white;
    final border = dark ? ShamelColors.borderDark  : const Color(0xFFE8EAED);

    return Scaffold(
      appBar: AppBar(
        title: const Text('المواد الدراسية',
            style: TextStyle(fontWeight: FontWeight.w800)),
      ),
      floatingActionButton: widget.studentMode
          ? null
          : FloatingActionButton(
              backgroundColor: ShamelColors.gold,
              foregroundColor: Colors.white,
              onPressed: () => Navigator.push(
                  context, ShamelPageRoute(page: const CreateCourseScreen())),
              child: const Icon(Icons.add),
            ),
      body: Column(children: [

        // ── Search ─────────────────────────────────────────────────────────
        Padding(
          padding: const EdgeInsets.fromLTRB(12, 12, 12, 0),
          child: TextField(
            controller: _ctrl,
            onChanged: _onSearch,
            decoration: InputDecoration(
              hintText: 'بحث في المواد…',
              prefixIcon: const Icon(Icons.search, size: 20),
              suffixIcon: _q.isNotEmpty
                  ? IconButton(
                      icon: const Icon(Icons.clear, size: 18),
                      onPressed: () { _ctrl.clear(); _q = ''; _load(); })
                  : null,
            ),
          ),
        ),

        // ── Scope toggle (only shown in student mode) ───────────────────────
        if (widget.studentMode)
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 10, 12, 0),
            child: Row(children: [
              _ScopeChip(
                label: 'مواد كليتي',
                icon: Icons.school_outlined,
                selected: _scope == 'mine',
                onTap: () => _setScope('mine'),
              ),
              const SizedBox(width: 8),
              _ScopeChip(
                label: 'جميع المواد',
                icon: Icons.public,
                selected: _scope == 'all',
                onTap: () => _setScope('all'),
              ),
            ]),
          ),

        // ── Count row ──────────────────────────────────────────────────────
        if (!_loading && _error == null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            child: Row(children: [
              Icon(Icons.menu_book_outlined, size: 14, color: ShamelColors.gold),
              const SizedBox(width: 6),
              Text(
                'عرض ${_items.length} من $_total مادة',
                style: const TextStyle(
                    color: ShamelColors.secondary,
                    fontSize: 12, fontWeight: FontWeight.w700),
              ),
            ]),
          ),

        // ── List ───────────────────────────────────────────────────────────
        Expanded(
          child: _loading
              ? const LoadingOrError(loading: true)
              : _error != null
                  ? LoadingOrError(loading: false, error: _error, onRetry: _load)
                  : _items.isEmpty
                      ? Center(
                          child: Column(mainAxisSize: MainAxisSize.min, children: [
                            Icon(Icons.menu_book_outlined,
                                size: 48, color: ShamelColors.gold.withValues(alpha: 0.4)),
                            const SizedBox(height: 12),
                            Text(
                              _q.isNotEmpty
                                  ? 'لا توجد نتائج لـ "$_q"'
                                  : 'لا توجد مواد',
                              style: const TextStyle(color: ShamelColors.secondary),
                            ),
                          ]),
                        )
                      : RefreshIndicator(
                          onRefresh: _load,
                          child: ListView.separated(
                            padding: const EdgeInsets.all(12),
                            itemCount: _items.length + (_hasMore ? 1 : 0),
                            separatorBuilder: (_, __) => const SizedBox(height: 8),
                            itemBuilder: (ctx, i) {
                              if (i == _items.length) {
                                return _loadingMore
                                    ? const Center(
                                        child: Padding(
                                          padding: EdgeInsets.all(12),
                                          child: CircularProgressIndicator(strokeWidth: 2),
                                        ))
                                    : TextButton.icon(
                                        onPressed: _loadMore,
                                        icon: const Icon(Icons.expand_more),
                                        label: Text(
                                          'تحميل المزيد (${_total - _items.length} متبقي)',
                                          style: const TextStyle(color: ShamelColors.gold),
                                        ),
                                      );
                              }
                              final m = _items[i] as Map;
                              return Container(
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: cardBg,
                                  borderRadius: BorderRadius.circular(14),
                                  border: Border.all(color: border),
                                ),
                                child: Row(children: [
                                  Container(
                                    padding: const EdgeInsets.all(8),
                                    decoration: BoxDecoration(
                                      color: ShamelColors.gold.withValues(alpha: 0.12),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: const Icon(Icons.menu_book_outlined,
                                        color: ShamelColors.gold, size: 18),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: [
                                        Text('${m['title'] ?? ''}',
                                            maxLines: 1,
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(
                                                fontWeight: FontWeight.w700,
                                                fontSize: 14,
                                                color: ShamelColors.primary)),
                                        const SizedBox(height: 2),
                                        Text(
                                          '${m['code'] ?? ''} • ${m['department'] ?? ''}',
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(
                                              color: ShamelColors.secondary,
                                              fontSize: 12),
                                        ),
                                      ],
                                    ),
                                  ),
                                  Text('${m['hours'] ?? ''} س',
                                      style: const TextStyle(
                                          fontWeight: FontWeight.w800,
                                          fontSize: 12,
                                          color: ShamelColors.gold)),
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

class _ScopeChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;
  const _ScopeChip({
    required this.label, required this.icon,
    required this.selected, required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
        decoration: BoxDecoration(
          color: selected
              ? ShamelColors.gold
              : ShamelColors.gold.withValues(alpha: 0.10),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
            color: selected
                ? ShamelColors.gold
                : ShamelColors.gold.withValues(alpha: 0.30),
          ),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 15,
              color: selected ? Colors.white : ShamelColors.gold),
          const SizedBox(width: 6),
          Text(label,
              style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: selected ? Colors.white : ShamelColors.gold)),
        ]),
      ),
    );
  }
}
