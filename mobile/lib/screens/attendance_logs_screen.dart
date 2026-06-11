import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../api.dart';
import '../theme.dart';
import '../widgets.dart';

class AttendanceLogsScreen extends StatefulWidget {
  const AttendanceLogsScreen({super.key});
  @override
  State<AttendanceLogsScreen> createState() => _AttendanceLogsScreenState();
}

class _AttendanceLogsScreenState extends State<AttendanceLogsScreen> {
  bool   _loading   = true;
  String? _error;
  List   _rows      = [];
  int    _total     = 0;
  bool   _fromCache = false;

  // Filters
  DateTime? _from;
  DateTime? _to;
  String    _status    = '';   // '' = all
  String    _courseId  = '';

  final _statusOptions = const [
    ('', 'الكل'),
    ('Present', 'حاضر'),
    ('Absent',  'غائب'),
    ('Late',    'متأخر'),
    ('Excused', 'معذور'),
  ];

  bool get _hasFilters => _from != null || _to != null ||
      _status.isNotEmpty || _courseId.isNotEmpty;

  static const _prefFrom     = 'att_filter_from';
  static const _prefTo       = 'att_filter_to';
  static const _prefStatus   = 'att_filter_status';

  @override
  void initState() { super.initState(); _restoreFilters(); }

  Future<void> _restoreFilters() async {
    final p = await SharedPreferences.getInstance();
    final from   = p.getString(_prefFrom);
    final to     = p.getString(_prefTo);
    final status = p.getString(_prefStatus) ?? '';
    setState(() {
      _from   = from   != null ? DateTime.tryParse(from)   : null;
      _to     = to     != null ? DateTime.tryParse(to)     : null;
      _status = status;
    });
    _load();
  }

  Future<void> _saveFilters() async {
    final p = await SharedPreferences.getInstance();
    if (_from != null) {
      await p.setString(_prefFrom, _from!.toIso8601String());
    } else {
      await p.remove(_prefFrom);
    }
    if (_to != null) {
      await p.setString(_prefTo, _to!.toIso8601String());
    } else {
      await p.remove(_prefTo);
    }
    await p.setString(_prefStatus, _status);
  }

  Future<void> _load() async {
    setState(() { _loading = true; _error = null; });
    try {
      final r = await Api.attendanceLogsCached(
        dateFrom: _from != null ? _fmt(_from!) : null,
        dateTo:   _to   != null ? _fmt(_to!)   : null,
        status:   _status.isNotEmpty   ? _status   : null,
        courseId: _courseId.isNotEmpty ? _courseId : null,
      );
      if (!mounted) return;
      if (r['ok'] == true) {
        _rows      = (r['logs']  ?? []) as List;
        _total     = (r['total'] ?? _rows.length) as int;
        _fromCache = r['from_cache'] == true;
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

  void _clearFilters() {
    setState(() {
      _from = null; _to = null;
      _status = ''; _courseId = '';
    });
    _saveFilters();
    _load();
  }

  String _fmt(DateTime d) =>
      '${d.year}-${d.month.toString().padLeft(2,'0')}-${d.day.toString().padLeft(2,'0')}';

  Future<void> _pickDate(bool isFrom) async {
    final now = DateTime.now();
    final picked = await showDatePicker(
      context: context,
      initialDate: (isFrom ? _from : _to) ?? now,
      firstDate: DateTime(now.year - 2),
      lastDate: now,
      locale: const Locale('ar'),
    );
    if (picked == null || !mounted) return;
    setState(() { isFrom ? _from = picked : _to = picked; });
    _saveFilters();
    _load();
  }

  Color _statusColor(String s) {
    final l = s.toLowerCase();
    if (l.contains('present') || l.contains('حاضر'))  return ShamelColors.success;
    if (l.contains('late')    || l.contains('متأخر'))  return ShamelColors.warning;
    if (l.contains('excused') || l.contains('معذور'))  return ShamelColors.info;
    return ShamelColors.error;
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = dark ? ShamelColors.surfaceDark : Colors.white;
    final bdr    = dark ? ShamelColors.borderDark  : const Color(0xFFE8EAED);

    return Scaffold(
      appBar: AppBar(
        title: const Text('سجلات الحضور',
            style: TextStyle(fontWeight: FontWeight.w800)),
        actions: [
          if (_hasFilters)
            TextButton.icon(
              onPressed: _clearFilters,
              icon: const Icon(Icons.filter_alt_off, size: 18),
              label: const Text('مسح'),
            ),
          IconButton(
            icon: Badge(
              isLabelVisible: _hasFilters,
              child: const Icon(Icons.filter_list),
            ),
            tooltip: 'تصفية',
            onPressed: _showFilterSheet,
          ),
        ],
      ),
      body: Column(children: [

        // ── Filter summary chips ─────────────────────────────────────────
        if (_hasFilters)
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            child: Row(children: [
              if (_from != null)
                _FilterChip(
                    label: 'من: ${_fmt(_from!)}',
                    onDelete: () { setState(() => _from = null); _load(); }),
              if (_to != null)
                _FilterChip(
                    label: 'إلى: ${_fmt(_to!)}',
                    onDelete: () { setState(() => _to = null); _load(); }),
              if (_status.isNotEmpty)
                _FilterChip(
                    label: _statusOptions
                        .firstWhere((e) => e.$1 == _status,
                            orElse: () => (_status, _status))
                        .$2,
                    onDelete: () { setState(() => _status = ''); _load(); }),
            ]),
          ),

        // ── Count + cache badge ──────────────────────────────────────────
        if (!_loading && _error == null)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
            child: Row(children: [
              const Icon(Icons.fact_check_outlined,
                  size: 15, color: ShamelColors.primary),
              const SizedBox(width: 6),
              Text('${_rows.length} من $_total سجل',
                  style: const TextStyle(
                      color: ShamelColors.secondary,
                      fontWeight: FontWeight.w700, fontSize: 12)),
              if (_fromCache) ...[
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: ShamelColors.warning.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Text('بيانات محفوظة',
                      style: TextStyle(
                          color: ShamelColors.warning,
                          fontSize: 10, fontWeight: FontWeight.w700)),
                ),
              ],
            ]),
          ),

        // ── Body ─────────────────────────────────────────────────────────
        Expanded(
          child: (_loading || _error != null)
              ? LoadingOrError(loading: _loading, error: _error, onRetry: _load)
              : _rows.isEmpty
                  ? Center(
                      child: Column(mainAxisSize: MainAxisSize.min, children: [
                        const Icon(Icons.fact_check_outlined,
                            size: 48, color: ShamelColors.outline),
                        const SizedBox(height: 12),
                        Text(
                          _hasFilters
                              ? 'لا توجد سجلات تطابق الفلتر المحدد'
                              : 'لا توجد سجلات حضور بعد',
                          style: const TextStyle(
                              color: ShamelColors.secondary,
                              fontWeight: FontWeight.w600),
                        ),
                        if (_hasFilters) ...[
                          const SizedBox(height: 10),
                          OutlinedButton(
                            onPressed: _clearFilters,
                            child: const Text('مسح الفلاتر'),
                          ),
                        ],
                      ]),
                    )
                  : RefreshIndicator(
                      onRefresh: _load,
                      child: ListView.separated(
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        itemCount: _rows.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 8),
                        itemBuilder: (_, i) {
                          final l  = _rows[i] as Map;
                          final st = '${l['status'] ?? ''}';
                          final conf = l['confidence'];
                          final date = '${l['date'] ?? l['timestamp'] ?? ''}';
                          return Semantics(
                            label: '${l['student']} — $st',
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: cardBg,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: bdr),
                              ),
                              child: Row(children: [
                                Container(
                                  width: 4, height: 48,
                                  decoration: BoxDecoration(
                                    color: _statusColor(st),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                ),
                                const SizedBox(width: 12),
                                Expanded(child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text('${l['student'] ?? '—'}',
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w700,
                                            color: ShamelColors.primary)),
                                    Text('${l['course'] ?? ''}',
                                        maxLines: 1,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                            color: ShamelColors.secondary,
                                            fontSize: 12)),
                                    if (date.isNotEmpty)
                                      Text(date,
                                          style: const TextStyle(
                                              color: ShamelColors.outline,
                                              fontSize: 11)),
                                  ],
                                )),
                                Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                        horizontal: 8, vertical: 3),
                                    decoration: BoxDecoration(
                                      color: _statusColor(st).withValues(alpha: 0.12),
                                      borderRadius: BorderRadius.circular(8),
                                    ),
                                    child: Text(st,
                                        style: TextStyle(
                                            color: _statusColor(st),
                                            fontSize: 11,
                                            fontWeight: FontWeight.w700)),
                                  ),
                                  if (conf != null)
                                    Padding(
                                      padding: const EdgeInsets.only(top: 4),
                                      child: Text(
                                        '${(conf is num ? (conf * 100).toStringAsFixed(0) : conf)}%',
                                        style: const TextStyle(
                                            color: ShamelColors.outline,
                                            fontSize: 11),
                                      ),
                                    ),
                                ]),
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

  // ── Filter bottom sheet ────────────────────────────────────────────────────

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => Padding(
          padding: EdgeInsets.only(
              left: 20, right: 20, top: 16,
              bottom: MediaQuery.of(ctx).viewInsets.bottom + 20),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Container(
              width: 40, height: 4,
              decoration: BoxDecoration(
                color: ShamelColors.outline.withValues(alpha: 0.4),
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(height: 16),
            const Text('تصفية السجلات',
                style: TextStyle(
                    fontSize: 17, fontWeight: FontWeight.w800,
                    color: ShamelColors.primary)),
            const SizedBox(height: 20),

            // Date from
            _DateRow(
              label: 'من تاريخ',
              value: _from != null ? _fmt(_from!) : null,
              onPick: () async {
                await _pickDate(true);
                setSheetState(() {});
              },
              onClear: _from != null ? () {
                setState(() => _from = null);
                setSheetState(() {});
                _load();
              } : null,
            ),
            const SizedBox(height: 12),

            // Date to
            _DateRow(
              label: 'إلى تاريخ',
              value: _to != null ? _fmt(_to!) : null,
              onPick: () async {
                await _pickDate(false);
                setSheetState(() {});
              },
              onClear: _to != null ? () {
                setState(() => _to = null);
                setSheetState(() {});
                _load();
              } : null,
            ),
            const SizedBox(height: 16),

            // Status
            const Align(
              alignment: Alignment.centerRight,
              child: Text('الحالة',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                      color: ShamelColors.secondary)),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8, runSpacing: 8,
              children: _statusOptions.map((opt) {
                final selected = _status == opt.$1;
                return ChoiceChip(
                  label: Text(opt.$2),
                  selected: selected,
                  onSelected: (_) {
                    setState(() => _status = opt.$1);
                    setSheetState(() {});
                    _saveFilters();
                    _load();
                  },
                  selectedColor: ShamelColors.gold.withValues(alpha: 0.20),
                  labelStyle: TextStyle(
                      fontWeight: FontWeight.w700,
                      color: selected ? ShamelColors.gold : ShamelColors.secondary),
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            Row(children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () {
                    Navigator.pop(ctx);
                    _clearFilters();
                  },
                  child: const Text('مسح الكل'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('تطبيق'),
                ),
              ),
            ]),
          ]),
        ),
      ),
    );
  }
}

// ── Helper widgets ────────────────────────────────────────────────────────────

class _FilterChip extends StatelessWidget {
  final String label;
  final VoidCallback onDelete;
  const _FilterChip({required this.label, required this.onDelete});
  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(left: 6),
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: ShamelColors.gold.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: ShamelColors.gold.withValues(alpha: 0.3)),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        Text(label,
            style: const TextStyle(
                color: ShamelColors.gold, fontSize: 12,
                fontWeight: FontWeight.w700)),
        const SizedBox(width: 4),
        GestureDetector(
          onTap: onDelete,
          child: const Icon(Icons.close, size: 14, color: ShamelColors.gold),
        ),
      ]),
    );
  }
}

class _DateRow extends StatelessWidget {
  final String label;
  final String? value;
  final VoidCallback onPick;
  final VoidCallback? onClear;
  const _DateRow({required this.label, this.value,
      required this.onPick, this.onClear});
  @override
  Widget build(BuildContext context) {
    return Row(children: [
      Expanded(
        child: Text(label,
            style: const TextStyle(
                fontSize: 13, fontWeight: FontWeight.w600,
                color: ShamelColors.secondary)),
      ),
      GestureDetector(
        onTap: onPick,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: ShamelColors.gold.withValues(alpha: 0.08),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(
                color: value != null
                    ? ShamelColors.gold.withValues(alpha: 0.4)
                    : ShamelColors.outline.withValues(alpha: 0.3)),
          ),
          child: Row(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.calendar_today_outlined,
                size: 15, color: ShamelColors.gold),
            const SizedBox(width: 6),
            Text(value ?? 'اختر تاريخاً',
                style: TextStyle(
                    color: value != null ? ShamelColors.gold : ShamelColors.outline,
                    fontSize: 13, fontWeight: FontWeight.w600)),
          ]),
        ),
      ),
      if (onClear != null)
        IconButton(
          icon: const Icon(Icons.clear, size: 16, color: ShamelColors.outline),
          onPressed: onClear,
          padding: EdgeInsets.zero,
          constraints: const BoxConstraints(minWidth: 32, minHeight: 32),
        ),
    ]);
  }
}

