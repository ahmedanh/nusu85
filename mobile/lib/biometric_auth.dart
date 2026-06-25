import 'dart:convert';
import 'dart:typed_data';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'api.dart';

/// Face-based quick login against the central SHAMEL database.
///
/// Replaces the old local_auth (OS fingerprint/face) flow.
/// No biometric data is stored locally — every match goes through the server.
class FaceLoginSheet extends StatefulWidget {
  const FaceLoginSheet({super.key});

  /// Opens a bottom sheet and returns the API result map on success,
  /// or null if the user dismissed / an error occurred.
  static Future<Map<String, dynamic>?> show(BuildContext context) {
    return showModalBottomSheet<Map<String, dynamic>>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (_) => const FaceLoginSheet(),
    );
  }

  @override
  State<FaceLoginSheet> createState() => _FaceLoginSheetState();
}

class _FaceLoginSheetState extends State<FaceLoginSheet> {
  CameraController? _ctrl;
  List<CameraDescription> _cameras = [];
  bool _ready = false;
  bool _scanning = false;
  String? _status;
  bool _failed = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  @override
  void dispose() {
    _ctrl?.dispose();
    super.dispose();
  }

  Future<void> _initCamera() async {
    try {
      _cameras = await availableCameras();
      if (_cameras.isEmpty) {
        setState(() => _status = 'لا توجد كاميرا متاحة');
        return;
      }
      // Prefer front camera
      final cam = _cameras.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.front,
        orElse: () => _cameras.first,
      );
      _ctrl = CameraController(cam, ResolutionPreset.medium,
          enableAudio: false, imageFormatGroup: ImageFormatGroup.jpeg);
      await _ctrl!.initialize();
      if (!mounted) return;
      setState(() => _ready = true);
      // Auto-scan after 1.5 s warm-up
      Future.delayed(const Duration(milliseconds: 1500), _scan);
    } catch (e) {
      setState(() => _status = 'تعذّر تشغيل الكاميرا');
    }
  }

  Future<void> _scan() async {
    if (!mounted || _scanning || !_ready || _ctrl == null) return;
    setState(() { _scanning = true; _status = null; _failed = false; });

    try {
      final xFile = await _ctrl!.takePicture();
      final bytes = await xFile.readAsBytes();
      final b64 = base64Encode(bytes);

      final res = await Api.postJson('/api/v1/auth/face-login', {'image': b64});

      if (!mounted) return;

      if (res['ok'] == true) {
        // Save token and return result to caller
        if (res['token'] != null) {
          await Api.saveTokenPublic(res['token'] as String);
        }
        Navigator.of(context).pop(res);
      } else {
        final code = res['code'] as String? ?? '';
        final msg  = res['message'] as String? ?? 'لم يتم التعرف';
        if (code == 'face_not_registered') {
          // Terminal error — don't retry
          setState(() { _status = msg; _failed = true; _scanning = false; });
        } else {
          // Transient — retry automatically
          setState(() { _scanning = false; });
          await Future.delayed(const Duration(milliseconds: 2000));
          _scan();
        }
      }
    } catch (e) {
      if (!mounted) return;
      setState(() { _scanning = false; });
      await Future.delayed(const Duration(milliseconds: 2000));
      if (!_failed) _scan();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: EdgeInsets.only(
          bottom: MediaQuery.of(context).viewInsets.bottom + 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(width: 40, height: 4,
              margin: const EdgeInsets.only(top: 12, bottom: 16),
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2))),

          const Text('تسجيل الدخول بالوجه',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w800)),
          const SizedBox(height: 4),
          Text('ضع وجهك أمام الكاميرا',
              style: TextStyle(fontSize: 13, color: Colors.grey.shade600)),
          const SizedBox(height: 16),

          // Camera preview
          SizedBox(
            width: 220, height: 220,
            child: ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: _ready && _ctrl != null
                  ? CameraPreview(_ctrl!)
                  : Container(
                      color: Colors.black87,
                      child: const Center(
                          child: CircularProgressIndicator(color: Colors.white))),
            ),
          ),

          const SizedBox(height: 16),

          // Status
          if (_status != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Text(_status!,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                      color: _failed ? Colors.red.shade700 : Colors.grey.shade700,
                      fontSize: 13, fontWeight: FontWeight.w600)),
            )
          else if (_scanning)
            Row(mainAxisAlignment: MainAxisAlignment.center, children: [
              SizedBox(width: 14, height: 14,
                  child: CircularProgressIndicator(strokeWidth: 2,
                      color: Theme.of(context).colorScheme.primary)),
              const SizedBox(width: 8),
              const Text('جارٍ المسح...', style: TextStyle(fontSize: 13)),
            ])
          else
            Text('جارٍ الاستعداد...', style: TextStyle(
                color: Colors.grey.shade500, fontSize: 13)),

          const SizedBox(height: 16),

          // Retry / Cancel buttons
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => Navigator.of(context).pop(null),
                  child: const Text('إلغاء'),
                ),
              ),
              if (_failed) ...[
                const SizedBox(width: 12),
                Expanded(
                  child: ElevatedButton(
                    onPressed: () {
                      setState(() { _failed = false; _status = null; });
                      _scan();
                    },
                    child: const Text('إعادة المحاولة'),
                  ),
                ),
              ],
            ]),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }
}
