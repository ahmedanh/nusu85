import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../theme.dart';
import '../auth.dart';
import '../api.dart';
import '../update_checker.dart';
import 'dashboard_screen.dart';
import 'schedule_screen.dart';
import 'reports_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'menu_drawer.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int  _index       = 0;
  bool _isOnline    = true;
  int  _pendingSync = 0;

  StreamSubscription<List<ConnectivityResult>>? _connSub;
  Timer? _syncTimer;

  // ── Lifecycle ─────────────────────────────────────────────────────────────

  @override
  void initState() {
    super.initState();

    // Post-frame: update check + connectivity
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (mounted) UpdateChecker.checkAndPrompt(context);
      await _checkConnectivity();
      await _refreshPendingCount();
    });

    // Watch connectivity changes
    _connSub = Connectivity()
        .onConnectivityChanged
        .listen((results) async {
      final online = results.any((r) => r != ConnectivityResult.none);
      if (!mounted) return;
      setState(() => _isOnline = online);
      if (online) {
        // Auto-sync when coming back online
        await _syncOffline();
      }
    });

    // Poll pending count every 30s
    _syncTimer = Timer.periodic(const Duration(seconds: 30), (_) async {
      if (mounted) await _refreshPendingCount();
    });
  }

  @override
  void dispose() {
    _connSub?.cancel();
    _syncTimer?.cancel();
    super.dispose();
  }

  Future<void> _checkConnectivity() async {
    final results = await Connectivity().checkConnectivity();
    if (!mounted) return;
    setState(() => _isOnline = results.any((r) => r != ConnectivityResult.none));
  }

  Future<void> _refreshPendingCount() async {
    final count = await Api.pendingCount();
    if (!mounted) return;
    setState(() => _pendingSync = count);
  }

  Future<void> _syncOffline() async {
    if (_pendingSync == 0) return;
    try {
      final synced = await Api.syncOfflineQueue();
      if (synced > 0 && mounted) {
        await _refreshPendingCount();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('تمت مزامنة $synced سجل حضور بنجاح'),
            backgroundColor: ShamelColors.success,
            behavior: SnackBarBehavior.floating,
          ));
        }
      }
    } catch (_) {}
  }

  // ── Tabs by role ──────────────────────────────────────────────────────────

  List<_Tab> _tabsFor(String role) {
    final dash    = _Tab('الرئيسية',   Icons.dashboard_outlined,      const DashboardScreen());
    final sched   = _Tab('الجدول',     Icons.calendar_month_outlined,  const ScheduleScreen());
    final notifs  = _Tab('الإشعارات', Icons.notifications_outlined,   const NotificationsScreen());
    final profile = _Tab('حسابي',      Icons.person_outline,           const ProfileScreen());
    final reports = _Tab('التقارير',   Icons.bar_chart_outlined,       const ReportsScreen());

    switch (role) {
      case 'admin':
      case 'coordinator':
        return [dash, reports, notifs, profile];
      case 'teacher':
        return [dash, sched, notifs, profile];
      case 'student':
        return [dash, sched, reports, notifs, profile];
      case 'gate':
        return [dash, notifs, profile];
      default:
        return [dash, notifs, profile];
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    final auth  = context.watch<AuthState>();
    final role  = auth.role;
    final tabs  = _tabsFor(role);
    if (_index >= tabs.length) _index = 0;

    return Scaffold(
      drawer: const MenuDrawer(),
      appBar: AppBar(
        titleSpacing: 8,
        title: Row(children: [
          const Icon(Icons.shield_outlined, color: ShamelColors.gold, size: 22),
          const SizedBox(width: 8),
          const Text('SHAMEL',
              style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: 1)),
          const Spacer(),
          // Pending sync badge
          if (_pendingSync > 0)
            Padding(
              padding: const EdgeInsets.only(left: 8),
              child: Tooltip(
                message: '$_pendingSync سجل حضور في انتظار المزامنة',
                child: GestureDetector(
                  onTap: _isOnline ? _syncOffline : null,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: ShamelColors.warning.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                          color: ShamelColors.warning.withValues(alpha: 0.40)),
                    ),
                    child: Row(mainAxisSize: MainAxisSize.min, children: [
                      const Icon(Icons.sync, size: 13, color: ShamelColors.warning),
                      const SizedBox(width: 4),
                      Text('$_pendingSync',
                          style: const TextStyle(
                              color: ShamelColors.warning,
                              fontSize: 12, fontWeight: FontWeight.w800)),
                    ]),
                  ),
                ),
              ),
            ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: ShamelTheme.roleColor(role),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(ShamelTheme.roleLabel(role),
                style: const TextStyle(
                    color: Colors.white, fontSize: 11,
                    fontWeight: FontWeight.w700)),
          ),
        ]),
      ),
      body: Column(children: [
        // ── Offline banner ────────────────────────────────────────────────
        AnimatedSwitcher(
          duration: const Duration(milliseconds: 300),
          child: !_isOnline
              ? _OfflineBanner(pendingSync: _pendingSync)
              : _pendingSync > 0
                  ? _SyncBanner(
                      pendingSync: _pendingSync,
                      onSync: _syncOffline,
                    )
                  : const SizedBox.shrink(),
        ),

        // ── Tab content ───────────────────────────────────────────────────
        Expanded(
          child: IndexedStack(
            index: _index,
            children: tabs.map((t) => t.screen).toList(),
          ),
        ),
      ]),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: tabs
            .map((t) => BottomNavigationBarItem(
                  icon: Icon(t.icon),
                  label: t.label,
                ))
            .toList(),
      ),
    );
  }
}

// ── Sub-widgets ───────────────────────────────────────────────────────────────

class _OfflineBanner extends StatelessWidget {
  final int pendingSync;
  const _OfflineBanner({required this.pendingSync});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: ShamelColors.error.withValues(alpha: 0.10),
      child: Row(children: [
        const Icon(Icons.wifi_off, size: 16, color: ShamelColors.error),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            pendingSync > 0
                ? 'أنت غير متصل — $pendingSync سجل في انتظار المزامنة'
                : 'أنت غير متصل — يتم عرض البيانات المحفوظة',
            style: const TextStyle(
                color: ShamelColors.error,
                fontSize: 12, fontWeight: FontWeight.w600),
          ),
        ),
      ]),
    );
  }
}

class _SyncBanner extends StatelessWidget {
  final int pendingSync;
  final VoidCallback onSync;
  const _SyncBanner({required this.pendingSync, required this.onSync});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      color: ShamelColors.warning.withValues(alpha: 0.08),
      child: Row(children: [
        const Icon(Icons.cloud_upload_outlined,
            size: 15, color: ShamelColors.warning),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            '$pendingSync سجل حضور في انتظار المزامنة',
            style: const TextStyle(
                color: ShamelColors.warning,
                fontSize: 12, fontWeight: FontWeight.w600),
          ),
        ),
        TextButton(
          onPressed: onSync,
          style: TextButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 8),
              minimumSize: const Size(0, 28)),
          child: const Text('مزامنة الآن',
              style: TextStyle(
                  color: ShamelColors.warning,
                  fontSize: 12, fontWeight: FontWeight.w800)),
        ),
      ]),
    );
  }
}

class _Tab {
  final String   label;
  final IconData icon;
  final Widget   screen;
  _Tab(this.label, this.icon, this.screen);
}
