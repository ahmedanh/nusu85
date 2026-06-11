import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:open_file/open_file.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
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
  String? _error;

  Future<void> _download() async {
    setState(() {
      _downloading = true;
      _error = null;
      _progress = 0;
    });

    try {
      final dir = await getTemporaryDirectory();
      final apkDir = Directory('${dir.path}/apk_downloads');
      await apkDir.create(recursive: true);
      final apkFile = File('${apkDir.path}/shamel-update.apk');

      final client = http.Client();
      final request = http.Request('GET', Uri.parse(widget.apkUrl));
      final response = await client.send(request);

      final total = response.contentLength ?? 0;
      int received = 0;

      final sink = apkFile.openWrite();
      await for (final chunk in response.stream) {
        sink.add(chunk);
        received += chunk.length;
        if (total > 0) {
          setState(() => _progress = received / total);
        }
      }
      await sink.close();
      client.close();

      setState(() => _progress = 1.0);
      await OpenFile.open(apkFile.path);
    } catch (e) {
      setState(() {
        _error = 'فشل التنزيل: $e';
        _downloading = false;
      });
    }
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
          if (_error != null) ...[
            const SizedBox(height: 8),
            Text(_error!,
                style: const TextStyle(color: Colors.red, fontSize: 12)),
          ],
        ],
      ),
      actions: _downloading && _error == null
          ? []
          : [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: Text('لاحقاً', style: TextStyle(color: cs.onSurfaceVariant)),
              ),
              ElevatedButton.icon(
                onPressed: _downloading ? null : _download,
                icon: const Icon(Icons.download),
                label: Text(_error != null ? 'إعادة المحاولة' : 'تحديث الآن'),
              ),
            ],
    );
  }
}
