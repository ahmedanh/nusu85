import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'dart:convert';
import 'api.dart';

class UpdateChecker {
  /// Call once after login. Shows update dialog if newer version available.
  static Future<void> checkAndPrompt(BuildContext context) async {
    try {
      final info = await PackageInfo.fromPlatform();
      final currentCode = int.tryParse(info.buildNumber) ?? 1;

      final r = await http
          .get(Uri.parse('${Api.baseUrl}/api/v1/app/version'))
          .timeout(const Duration(seconds: 8));
      if (r.statusCode != 200) return;

      final data = jsonDecode(r.body) as Map<String, dynamic>;
      final serverCode = (data['version_code'] as int?) ?? 1;
      if (serverCode <= currentCode) return;

      if (!context.mounted) return;
      _showUpdateDialog(
        context,
        versionName: data['version_name'] as String? ?? '',
        notes: data['notes'] as String? ?? '',
        apkUrl: data['apk_url'] as String? ?? '',
      );
    } catch (_) {
      // Silent fail — update check is non-critical
    }
  }

  static void _showUpdateDialog(
    BuildContext context, {
    required String versionName,
    required String notes,
    required String apkUrl,
  }) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => _UpdateDialog(
        versionName: versionName,
        notes: notes,
        apkUrl: apkUrl,
      ),
    );
  }
}

class _UpdateDialog extends StatefulWidget {
  final String versionName;
  final String notes;
  final String apkUrl;

  const _UpdateDialog({
    required this.versionName,
    required this.notes,
    required this.apkUrl,
  });

  @override
  State<_UpdateDialog> createState() => _UpdateDialogState();
}

class _UpdateDialogState extends State<_UpdateDialog> {
  double _progress = 0;
  bool _downloading = false;
  bool _readyToInstall = false;
  String? _error;
  String? _apkPath;

  Future<void> _download() async {
    setState(() {
      _downloading = true;
      _readyToInstall = false;
      _error = null;
      _progress = 0;
    });

    try {
      final dir = await getTemporaryDirectory();
      final apkDir = Directory('${dir.path}/apk_downloads');
      await apkDir.create(recursive: true);
      final apkFile = File('${apkDir.path}/shamel-update.apk');

      // Delete old APK if exists
      if (await apkFile.exists()) await apkFile.delete();

      final client = http.Client();
      try {
        final request = http.Request('GET', Uri.parse(widget.apkUrl));
        final response = await client.send(request)
            .timeout(const Duration(minutes: 5));

        final total = response.contentLength ?? 0;
        int received = 0;

        final sink = apkFile.openWrite();
        await for (final chunk in response.stream) {
          sink.add(chunk);
          received += chunk.length;
          if (total > 0 && mounted) {
            setState(() => _progress = received / total);
          }
        }
        await sink.close();
      } finally {
        client.close();
      }

      if (!mounted) return;
      setState(() {
        _progress = 1.0;
        _apkPath = apkFile.path;
        _readyToInstall = true;
        _downloading = false;
      });

      // Auto-trigger install immediately
      await _install();
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = 'فشل التنزيل — جرب تحديث يدوي';
        _downloading = false;
      });
    }
  }

  /// Install the downloaded APK.
  /// Strategy: try in-app install first; fall back to browser download.
  Future<void> _install() async {
    if (_apkPath == null) return;
    final file = File(_apkPath!);
    if (!await file.exists()) {
      _openInBrowser();
      return;
    }

    // Try to launch the APK file via the system installer.
    // On Android 8+ this requires "install unknown apps" permission.
    // We launch a chooser intent via url_launcher as a content URI.
    final uri = Uri.file(_apkPath!);
    bool launched = false;
    try {
      if (await canLaunchUrl(uri)) {
        launched = await launchUrl(uri, mode: LaunchMode.externalApplication);
      }
    } catch (_) {}

    if (!launched) {
      // Fallback: open browser to download (always works, browser handles install)
      _openInBrowser();
    }
  }

  void _openInBrowser() {
    final uri = Uri.parse(widget.apkUrl);
    launchUrl(uri, mode: LaunchMode.externalApplication);
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final cs = Theme.of(context).colorScheme;
    return AlertDialog(
      backgroundColor: cs.surface,
      title: Row(children: [
        Icon(Icons.system_update, color: cs.primary),
        const SizedBox(width: 8),
        Text('تحديث جديد متاح', style: TextStyle(color: cs.onSurface)),
      ]),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('الإصدار ${widget.versionName}',
              style: TextStyle(
                  fontWeight: FontWeight.bold, color: cs.onSurface)),
          if (widget.notes.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(widget.notes,
                style: TextStyle(color: cs.onSurfaceVariant, fontSize: 13)),
          ],
          if (_downloading) ...[
            const SizedBox(height: 16),
            LinearProgressIndicator(value: _progress > 0 ? _progress : null),
            const SizedBox(height: 4),
            Text(
              _progress > 0
                  ? 'جارٍ التنزيل ${(_progress * 100).toStringAsFixed(0)}%'
                  : 'جارٍ التنزيل...',
              style: TextStyle(fontSize: 12, color: cs.onSurfaceVariant),
            ),
          ],
          if (_readyToInstall && !_downloading) ...[
            const SizedBox(height: 12),
            Row(children: [
              Icon(Icons.check_circle, color: Colors.green.shade600, size: 18),
              const SizedBox(width: 6),
              Text('تم التنزيل — سيبدأ التثبيت الآن',
                  style: TextStyle(
                      color: Colors.green.shade700,
                      fontSize: 12, fontWeight: FontWeight.w600)),
            ]),
          ],
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!,
                style: const TextStyle(color: Colors.red, fontSize: 12)),
            const SizedBox(height: 4),
            Text('اضغط "تنزيل من المتصفح" لتحديث يدوي',
                style: TextStyle(fontSize: 11, color: cs.onSurfaceVariant)),
          ],
        ],
      ),
      actions: [
        if (!_downloading)
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text('لاحقاً', style: TextStyle(color: cs.onSurfaceVariant)),
          ),
        if (_error != null)
          ElevatedButton.icon(
            onPressed: _openInBrowser,
            icon: const Icon(Icons.open_in_browser, size: 16),
            label: const Text('تنزيل من المتصفح'),
          )
        else if (!_downloading)
          ElevatedButton.icon(
            onPressed: _readyToInstall ? _install : _download,
            icon: Icon(_readyToInstall ? Icons.install_mobile : Icons.download,
                size: 16),
            label: Text(_readyToInstall ? 'تثبيت' : 'تحديث الآن'),
          ),
      ],
    );
  }
}
