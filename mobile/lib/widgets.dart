import 'package:flutter/material.dart';
import 'theme.dart';

/// Reusable stat card — mirrors the web dashboard metric cards.
class StatCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color? accent;
  const StatCard({super.key, required this.label, required this.value, required this.icon, this.accent});

  @override
  Widget build(BuildContext context) {
    final c = accent ?? ShamelColors.primary;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE8EAED)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            padding: const EdgeInsets.all(7),
            decoration: BoxDecoration(color: c.withValues(alpha: 0.1), borderRadius: BorderRadius.circular(10)),
            child: Icon(icon, color: c, size: 18),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(value, style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: c, height: 1.1)),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 11, color: ShamelColors.secondary, fontWeight: FontWeight.w600)),
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
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 12, top: 4),
        child: Text(title, style: const TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: ShamelColors.primary)),
      );
}

/// Animated shimmer wrapper — sweeps a highlight band across grey
/// placeholder boxes. No external package; uses a ShaderMask.
class Shimmer extends StatefulWidget {
  final Widget child;
  const Shimmer({super.key, required this.child});
  @override
  State<Shimmer> createState() => _ShimmerState();
}

class _ShimmerState extends State<Shimmer> with SingleTickerProviderStateMixin {
  late final AnimationController _c =
      AnimationController(vsync: this, duration: const Duration(milliseconds: 1300))..repeat();
  @override
  void dispose() {
    _c.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final dark = Theme.of(context).brightness == Brightness.dark;
    final base = dark ? const Color(0xFF1E293B) : const Color(0xFFE9EEF5);
    final hi = dark ? const Color(0xFF334155) : const Color(0xFFF6F9FC);
    return AnimatedBuilder(
      animation: _c,
      child: widget.child,
      builder: (context, child) => ShaderMask(
        blendMode: BlendMode.srcATop,
        shaderCallback: (rect) => LinearGradient(
          colors: [base, hi, base],
          stops: const [0.25, 0.5, 0.75],
          begin: Alignment(-1.0 - 2.0 * _c.value, 0),
          end: Alignment(1.0 - 2.0 * _c.value, 0),
          tileMode: TileMode.clamp,
        ).createShader(rect),
        child: child,
      ),
    );
  }
}

/// A single grey placeholder block.
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
        color: dark ? const Color(0xFF1E293B) : const Color(0xFFE9EEF5),
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}

/// Shimmering placeholder list — mirrors the card rows used across the app.
/// Drop-in replacement for a CircularProgressIndicator while data loads.
class SkeletonList extends StatelessWidget {
  final int count;
  const SkeletonList({super.key, this.count = 7});
  @override
  Widget build(BuildContext context) {
    return Shimmer(
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        physics: const NeverScrollableScrollPhysics(),
        itemCount: count,
        itemBuilder: (_, __) => Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0x14000000)),
          ),
          child: Row(children: const [
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

class LoadingOrError extends StatelessWidget {
  final bool loading;
  final String? error;
  final VoidCallback? onRetry;
  final bool skeleton;
  const LoadingOrError({super.key, required this.loading, this.error, this.onRetry, this.skeleton = true});
  @override
  Widget build(BuildContext context) {
    if (loading) {
      return skeleton
          ? const SkeletonList()
          : const Padding(
              padding: EdgeInsets.all(40),
              child: Center(child: CircularProgressIndicator(color: ShamelColors.gold)),
            );
    }
    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(children: [
        const Icon(Icons.cloud_off, size: 48, color: ShamelColors.outline),
        const SizedBox(height: 12),
        Text(error ?? 'تعذّر تحميل البيانات', textAlign: TextAlign.center,
            style: const TextStyle(color: ShamelColors.secondary)),
        if (onRetry != null) ...[
          const SizedBox(height: 12),
          OutlinedButton.icon(onPressed: onRetry, icon: const Icon(Icons.refresh), label: const Text('إعادة المحاولة')),
        ],
      ]),
    );
  }
}
