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

class LoadingOrError extends StatelessWidget {
  final bool loading;
  final String? error;
  final VoidCallback? onRetry;
  const LoadingOrError({super.key, required this.loading, this.error, this.onRetry});
  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Padding(
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
