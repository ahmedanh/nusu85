import 'dart:async';
import 'package:flutter/material.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

/// Generic paginated list — covers courses, classrooms, departments, teachers,
/// students, tickets, attendance-logs, gate-logs, audit-log, exams, etc.
class ResourceListScreen extends StatefulWidget {
  final String title;
  final String endpoint;       // e.g. /api/v1/courses
  final String listKey;        // e.g. 'courses'
  final IconData icon;
  final Color accent;
  final bool searchable;
  final String Function(Map item) titleOf;
  final String Function(Map item)? subtitleOf;
  final String Function(Map item)? trailingOf;
  final void Function(BuildContext, Map item)? onTap;
  final Widget? fab;
  /// Human-readable hint for the empty-state message.
  final String emptyHint;
  /// Supported sort fields, e.g. [('الاسم', 'name'), ('التاريخ', 'date')].
  /// Empty list = no sort UI shown.
  final List<(String label, String value)> sortOptions;

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
    this.emptyHint = '',
    this.sortOptions = const [],
  });

  @override
  State<ResourceListScreen> createState() => _ResourceListScreenState();
}

class _ResourceListScreenState extends State<ResourceListScreen> {
  static const _pageSize = 25;

  bool   _loading    = true;
  bool   _loadingMore = false;
  String? _error;
  List   _items      = [];
  int    _total      = 0;
  int    _page       = 1;
  bool   _hasMore    = false;
  String _q          = '';
  bool   _fromCache  = false;
  String _sort       = '';      // sort field value; '' = default
  bool   _sortAsc    = true;

  final _searchCtrl = TextEditingController();
  Timer? _debounce;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _debounce?.cancel();
    _searchCtrl.dispose();
    super.dispose();
  }

  // ── Data loading ─────────────────────────────────────────────────────────

  Future<void> _load({bool reset = true}) async {
    if (reset) {
      setState(() { _loading = true; _error = null; _page = 1; _items = []; });
    }
    try {
      final path = _buildPath(_page);
      final r = await Api.getJson(path);
      if (!mounted) return;
      if (r['ok'] == true) {
        final fetched = (r[widget.listKey] ?? []) as List;
        _total     = (r['total'] ?? fetched.length) as int;
        _fromCache = r['from_cache'] == true;
        if (reset) {
          _items   = fetched;
        } else {
          _items   = [..._items, ...fetched];
        }
        _hasMore = _items.length < _total;
      } else {
        _error = (r['message'] ?? 'تعذّر التحميل') as String;
      }
    } on AuthException catch (e) {
      _error = e.message;
    } on PermissionException catch (e) {
      _error = e.message;
    } on ApiException catch (e) {
      _error = e.message;
    } catch (e) {
      _error = 'تعذّر الاتصال بالخادم';
    }
    if (mounted) setState(() { _loading = false; _loadingMore = false; });
  }

  Future<void> _loadMore() async {
    if (_loadingMore || !_hasMore) return;
    setState(() { _loadingMore = true; _page++; });
    await _load(reset: false);
  }

  String _buildPath(int page) {
    final sep = widget.endpoint.contains('?') ? '&' : '?';
    var path = widget.endpoint;
    final params = <String>[];
    if (_q.isNotEmpty)     params.add('q=${Uri.encodeComponent(_q)}');
    if (_sort.isNotEmpty)  params.add('sort=${_sort}&order=${_sortAsc ? 'asc' : 'desc'}');
    params.add('page=$page');
    params.add('page_size=$_pageSize');
    return path + sep + params.join('&');
  }

  // ── Search with debounce ─────────────────────────────────────────────────

  void _onSearchChanged(String v) {
    _debounce?.cancel();
    _debounce = Timer(const Duration(milliseconds: 320), () {
      if (_q == v.trim()) return;
      _q = v.trim();
      _load();
    });
  }

  void _clearSearch() {
    _searchCtrl.clear();
    if (_q.isEmpty) return;
    _q = '';
    _load();
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = dark ? ShamelColors.surfaceDark : Colors.white;
    final border = dark ? ShamelColors.borderDark  : ShamelColors.bord(context);

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title,
            style: const TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          if (widget.sortOptions.isNotEmpty) ...[
            // Direction toggle
            Semantics(
              label: _sortAsc ? 'ترتيب تصاعدي' : 'ترتيب تنازلي',
              button: true,
              child: IconButton(
                icon: Icon(
                    _sortAsc ? Icons.arrow_upward : Icons.arrow_downward,
                    size: 18),
                tooltip: _sortAsc ? 'تصاعدي' : 'تنازلي',
                onPressed: () {
                  setState(() => _sortAsc = !_sortAsc);
                  _load();
                },
              ),
            ),
            // Sort field dropdown
            PopupMenuButton<String>(
              tooltip: 'ترتيب حسب',
              icon: Badge(
                isLabelVisible: _sort.isNotEmpty,
                child: const Icon(Icons.sort),
              ),
              onSelected: (v) {
                setState(() => _sort = _sort == v ? '' : v);
                _load();
              },
              itemBuilder: (_) => widget.sortOptions.map((opt) {
                final selected = _sort == opt.$2;
                return PopupMenuItem<String>(
                  value: opt.$2,
                  child: Row(children: [
                    Expanded(child: Text(opt.$1,
                        style: TextStyle(
                            fontWeight: FontWeight.w600,
                            color: selected
                                ? ShamelColors.gold
                                : ShamelColors.primary))),
                    if (selected)
                      const Icon(Icons.check, size: 16, color: ShamelColors.gold),
                  ]),
                );
              }).toList(),
            ),
          ],
        ],
      ),
      floatingActionButton: widget.fab,
      body: Column(children: [

        // ── Search bar ────────────────────────────────────────────────────
        if (widget.searchable)
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 4),
            child: TextField(
              controller: _searchCtrl,
              onChanged: _onSearchChanged,
              onSubmitted: (v) { _q = v.trim(); _load(); },
              decoration: InputDecoration(
                hintText: 'بحث في ${widget.title}…',
                prefixIcon: const Icon(Icons.search, size: 20),
                suffixIcon: _q.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 18),
                        onPressed: _clearSearch,
                      )
                    : null,
              ),
            ),
          ),

        // ── Cache notice + count ───────────────────────────────────────────
        if (!_loading && _error == null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            child: Row(children: [
              Icon(widget.icon, size: 15, color: widget.accent),
              const SizedBox(width: 6),
              Text(
                _q.isEmpty
                    ? 'عرض ${_items.length} من $_total عنصر'
                    : 'نتائج البحث: ${_items.length} من $_total',
                style: TextStyle(
                    color: ShamelColors.sec(context), fontSize: 12,
                    fontWeight: FontWeight.w700),
              ),
              if (_fromCache) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: ShamelColors.warning.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Text('بيانات محفوظة',
                      style: TextStyle(color: ShamelColors.warning,
                          fontSize: 10, fontWeight: FontWeight.w700)),
                ),
              ],
            ]),
          ),

        // ── Body ─────────────────────────────────────────────────────────
        Expanded(
          child: _loading
              ? const LoadingOrError(loading: true)
              : _error != null
                  ? LoadingOrError(loading: false, error: _error, onRetry: _load)
                  : _items.isEmpty
                      ? _EmptyState(
                          icon: widget.icon,
                          accent: widget.accent,
                          isSearch: _q.isNotEmpty,
                          query: _q,
                          hint: widget.emptyHint,
                          onClear: _q.isNotEmpty ? _clearSearch : null,
                        )
                      : RefreshIndicator(
                          onRefresh: _load,
                          child: ListView.separated(
                            padding: const EdgeInsets.all(12),
                            itemCount: _items.length + (_hasMore ? 1 : 0),
                            separatorBuilder: (_, __) => const SizedBox(height: 8),
                            itemBuilder: (ctx, i) {
                              // Load-more footer
                              if (i == _items.length) {
                                return _LoadMoreButton(
                                  loading: _loadingMore,
                                  remaining: _total - _items.length,
                                  onPressed: _loadMore,
                                  accent: widget.accent,
                                );
                              }
                              final it = _items[i] as Map;
                              return _ItemCard(
                                item: it,
                                widget: widget,
                                cardBg: cardBg,
                                border: border,
                              );
                            },
                          ),
                        ),
        ),
      ]),
    );
  }
}

// ── Sub-widgets ───────────────────────────────────────────────────────────────

class _ItemCard extends StatelessWidget {
  final Map item;
  final ResourceListScreen widget;
  final Color cardBg;
  final Color border;
  const _ItemCard({required this.item, required this.widget,
      required this.cardBg, required this.border});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: widget.titleOf(item),
      button: widget.onTap != null,
      child: InkWell(
        onTap: widget.onTap == null ? null : () => widget.onTap!(context, item),
        borderRadius: BorderRadius.circular(14),
        child: Container(
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
                color: widget.accent.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(widget.icon, color: widget.accent, size: 18),
            ),
            const SizedBox(width: 12),
            Expanded(child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.titleOf(item),
                    maxLines: 1, overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontWeight: FontWeight.w700,
                        fontSize: 14, color: ShamelColors.txt(context))),
                if (widget.subtitleOf != null &&
                    widget.subtitleOf!(item).isNotEmpty) ...[
                  const SizedBox(height: 2),
                  Text(widget.subtitleOf!(item),
                      maxLines: 1, overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                          color: ShamelColors.sec(context), fontSize: 12)),
                ],
              ],
            )),
            if (widget.trailingOf != null)
              Text(widget.trailingOf!(item),
                  style: TextStyle(fontWeight: FontWeight.w800,
                      fontSize: 12, color: widget.accent)),
            if (widget.onTap != null)
              Icon(Icons.chevron_left, color: ShamelColors.sub(context)),
          ]),
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  final IconData icon;
  final Color accent;
  final bool isSearch;
  final String query;
  final String hint;
  final VoidCallback? onClear;
  const _EmptyState({
    required this.icon, required this.accent, required this.isSearch,
    required this.query, required this.hint, this.onClear,
  });

  @override
  Widget build(BuildContext context) {
    final title = isSearch
        ? 'لا توجد نتائج لـ "$query"'
        : (hint.isNotEmpty ? hint : 'لا توجد بيانات بعد');
    final sub = isSearch
        ? 'جرّب كلمة بحث أخرى'
        : 'ستظهر البيانات هنا عند إضافتها';

    return Center(
      child: Column(mainAxisSize: MainAxisSize.min, children: [
        Container(
          width: 64, height: 64,
          decoration: BoxDecoration(
            color: accent.withValues(alpha: 0.10),
            borderRadius: BorderRadius.circular(18),
          ),
          child: Icon(icon, color: accent, size: 30),
        ),
        const SizedBox(height: 12),
        Text(title,
            style: const TextStyle(
                fontWeight: FontWeight.w700, color: ShamelColors.primary,
                fontSize: 15)),
        const SizedBox(height: 6),
        Text(sub,
            style: TextStyle(
                color: ShamelColors.sec(context), fontSize: 13)),
        if (onClear != null) ...[
          const SizedBox(height: 14),
          OutlinedButton.icon(
            onPressed: onClear,
            icon: const Icon(Icons.clear, size: 16),
            label: const Text('مسح البحث'),
          ),
        ],
      ]),
    );
  }
}

class _LoadMoreButton extends StatelessWidget {
  final bool loading;
  final int remaining;
  final VoidCallback onPressed;
  final Color accent;
  const _LoadMoreButton({
    required this.loading, required this.remaining,
    required this.onPressed, required this.accent,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Center(
        child: loading
            ? const SizedBox(
                height: 28, width: 28,
                child: CircularProgressIndicator(strokeWidth: 2.5))
            : TextButton.icon(
                onPressed: onPressed,
                icon: Icon(Icons.expand_more, color: accent),
                label: Text(
                  'تحميل المزيد ($remaining متبقي)',
                  style: TextStyle(color: accent, fontWeight: FontWeight.w700),
                ),
              ),
      ),
    );
  }
}
