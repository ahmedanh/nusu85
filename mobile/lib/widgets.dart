import 'package:flutter/material.dart';
import 'theme.dart';

/// KPI stat card — mirrors web dashboard metric cards.
class StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? accent;
  const StatCard({super.key, required this.label, required this.value, required this.icon, this.accent});

  @override
  Widget build(BuildContext context) {
    final dark  = Theme.of(context).brightness == Brightness.dark;
    final c     = accent ?? ShamelColors.gold;
    final bg    = dark ? ShamelColors.surfaceDark : ShamelColors.surfaceLight;
    final bdr   = dark ? ShamelColors.borderDark  : ShamelColors.borderLight;
    final lbl   = dark ? ShamelColors.text3Dark   : ShamelColors.text3Light;

    return AnimatedContainer(
      duration: ShamelMotion.base,
      curve: ShamelMotion.easeOut,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: bdr),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            padding: const EdgeInsets.all(7),
            decoration: BoxDecoration(
              color: c.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: c, size: 18),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(value,
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: c, height: 1.1)),
              Text(label,
                  maxLines: 1, overflow: TextOverflow.ellipsis,
                  style: TextStyle(fontSize: 11, color: lbl, fontWeight: FontWeight.w600)),
            ],
          ),
        ],
      ),
    );
  }
}

class SectionTitle extends StatelessWidget {
  final String title;
  const SectionTitle(this.title, {super.key});
  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Padding(
      padding: const EdgeInsets.only(bottom: 12, top: 4),
      child: Text(title,
          style: TextStyle(
            fontSize: 17,
            fontWeight: FontWeight.w800,
            color: dark ? ShamelColors.goldDark : ShamelColors.navy,
          )),
    );
  }
}

/// Shimmer skeleton — respects reduced-motion via MediaQuery.
class Shimmer extends StatefulWidget {
  final Widget child;
  const Shimmer({super.key, required this.child});
  @override
  State<Shimmer> createState() => _ShimmerState();
}

class _ShimmerState extends State<Shimmer> with SingleTickerProviderStateMixin {
  late final AnimationController _c;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // Respect reduced-motion: freeze the shimmer at start position.
    final disable = MediaQuery.of(context).disableAnimations;
    _c = AnimationController(
      vsync: this,
      duration: disable ? Duration.zero : const Duration(milliseconds: 1600),
    );
    if (!disable) _c.repeat();
  }

  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    // Use navy tokens, not slate
    final base = dark ? ShamelColors.surfaceAltDark : const Color(0xFFE8EEF7);
    final hi   = dark ? ShamelColors.surfaceDark    : const Color(0xFFF5F8FF);

    return AnimatedBuilder(
      animation: _c,
      child: widget.child,
      builder: (_, child) => ShaderMask(
        blendMode: BlendMode.srcATop,
        shaderCallback: (rect) => LinearGradient(
          colors: [base, hi, base],
          stops: const [0.25, 0.5, 0.75],
          begin: Alignment(-1.0 - 2.0 * _c.value, 0),
          end:   Alignment( 1.0 - 2.0 * _c.value, 0),
          tileMode: TileMode.clamp,
        ).createShader(rect),
        child: child,
      ),
    );
  }
}

/// Single grey placeholder block.
class SkeletonBox extends StatelessWidget {
  final double? width;
  final double height;
  final double radius;
  const SkeletonBox({super.key, this.width, this.height = 12, this.radius = 8});

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: dark ? ShamelColors.surfaceAltDark : const Color(0xFFE8EEF7),
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}

/// Shimmer placeholder list — replaces CircularProgressIndicator.
class SkeletonList extends StatelessWidget {
  final int count;
  const SkeletonList({super.key, this.count = 7});

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bdr  = dark ? ShamelColors.borderDark : ShamelColors.borderLight;
    final bg   = dark ? ShamelColors.surfaceDark : ShamelColors.surfaceLight;

    return Shimmer(
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        physics: const NeverScrollableScrollPhysics(),
        shrinkWrap: true,
        itemCount: count,
        itemBuilder: (_, __) => Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: bdr),
          ),
          child: const Row(children: [
            SkeletonBox(width: 38, height: 38, radius: 12),
            SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  SkeletonBox(width: 170, height: 12),
                  SizedBox(height: 8),
                  SkeletonBox(width: 110, height: 10),
                ],
              ),
            ),
          ]),
        ),
      ),
    );
  }
}

/// Shimmer 2-column card grid — for dashboard skeleton.
class SkeletonGrid extends StatelessWidget {
  final int count;
  const SkeletonGrid({super.key, this.count = 6});

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final bg   = dark ? ShamelColors.surfaceDark   : ShamelColors.surfaceLight;
    final bdr  = dark ? ShamelColors.borderDark    : ShamelColors.borderLight;
    return Shimmer(
      child: GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        childAspectRatio: 1.55,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
        children: List.generate(count, (_) => Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: bg,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: bdr),
          ),
          child: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              SkeletonBox(width: 34, height: 34, radius: 10),
              Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                SkeletonBox(width: 60, height: 18),
                SizedBox(height: 6),
                SkeletonBox(width: 90, height: 10),
              ]),
            ],
          ),
        )),
      ),
    );
  }
}

class LoadingOrError extends StatelessWidget {
  final bool loading;
  final String? error;
  final VoidCallback? onRetry;
  final bool skeleton;
  const LoadingOrError({super.key, required this.loading, this.error, this.onRetry, this.skeleton = true});

  @override
  Widget build(BuildContext context) {
    final dark  = Theme.of(context).brightness == Brightness.dark;
    final muted = dark ? ShamelColors.text3Dark : ShamelColors.text3Light;
    final gold  = dark ? ShamelColors.goldDark  : ShamelColors.gold;

    if (loading) {
      return skeleton
          ? const SkeletonList()
          : Padding(
              padding: const EdgeInsets.all(40),
              child: Center(child: CircularProgressIndicator(color: gold)),
            );
    }
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(children: [
        Icon(Icons.cloud_off, size: 48, color: muted),
        const SizedBox(height: 12),
        Text(error ?? 'تعذّر تحميل البيانات',
            textAlign: TextAlign.center,
            style: TextStyle(color: muted)),
        if (onRetry != null) ...[
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: onRetry,
            icon: Icon(Icons.refresh, color: gold),
            label: Text('إعادة المحاولة', style: TextStyle(color: gold)),
            style: OutlinedButton.styleFrom(side: BorderSide(color: gold)),
          ),
        ],
      ]),
    );
  }
}
