import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import '../api.dart';
import '../theme.dart';

class ScanScreen extends StatefulWidget {
  const ScanScreen({super.key});
  @override
  State<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends State<ScanScreen> {
  CameraController? _controller;
  bool _initializing = true;
  bool _busy = false;
  String? _camError;
  String? _result;
  bool _resultOk = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  Future<void> _initCamera() async {
    try {
      final cams = await availableCameras();
      if (cams.isEmpty) {
        setState(() { _camError = 'لا توجد كاميرا متاحة'; _initializing = false; });
        return;
      }
      // prefer front camera for face scan
      final cam = cams.firstWhere(
        (c) => c.lensDirection == CameraLensDirection.front,
        orElse: () => cams.first,
      );
      final ctrl = CameraController(cam, ResolutionPreset.medium, enableAudio: false);
      await ctrl.initialize();
      if (!mounted) return;
      setState(() { _controller = ctrl; _initializing = false; });
    } catch (e) {
      setState(() { _camError = 'تعذّر تشغيل الكاميرا: السماح بالإذن مطلوب'; _initializing = false; });
    }
  }

  Future<void> _capture() async {
    if (_controller == null || _busy) return;
    setState(() { _busy = true; _result = null; });
    try {
      final shot = await _controller!.takePicture();
      final bytes = await shot.readAsBytes();
      final b64 = base64Encode(bytes);
      final r = await Api.scan(b64);
      if (!mounted) return;
      if (r['ok'] == true) {
        _resultOk = true;
        _result = 'تم التعرف: ${r['matched']}  (${((r['confidence'] ?? 0) * 100).toStringAsFixed(0)}%)';
      } else {
        _resultOk = false;
        _result = (r['message'] ?? 'لم يتم التعرف') as String;
      }
    } catch (e) {
      _resultOk = false;
      _result = 'تعذّر المسح — حاول مجدداً';
    }
    if (mounted) setState(() => _busy = false);
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: ShamelColors.primary,
      child: Column(children: [
        const SizedBox(height: 16),
        const Text('محطة المسح', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w800)),
        const Text('وجّه الكاميرا نحو الوجه', style: TextStyle(color: ShamelColors.goldLight, fontSize: 12)),
        const SizedBox(height: 16),
        Expanded(
          child: Center(
            child: _initializing
                ? const CircularProgressIndicator(color: ShamelColors.gold)
                : _camError != null
                    ? Padding(
                        padding: const EdgeInsets.all(24),
                        child: Column(mainAxisSize: MainAxisSize.min, children: [
                          const Icon(Icons.videocam_off, color: ShamelColors.outline, size: 48),
                          const SizedBox(height: 12),
                          Text(_camError!, textAlign: TextAlign.center,
                              style: const TextStyle(color: Colors.white70)),
                          const SizedBox(height: 12),
                          OutlinedButton(onPressed: () { setState(() => _initializing = true); _initCamera(); },
                              child: const Text('إعادة المحاولة', style: TextStyle(color: ShamelColors.gold))),
                        ]),
                      )
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(20),
                        child: AspectRatio(
                          aspectRatio: _controller!.value.aspectRatio,
                          child: Stack(fit: StackFit.expand, children: [
                            CameraPreview(_controller!),
                            // scanner frame overlay
                            Center(
                              child: Container(
                                width: 220, height: 260,
                                decoration: BoxDecoration(
                                  border: Border.all(color: ShamelColors.gold, width: 2),
                                  borderRadius: BorderRadius.circular(16),
                                ),
                              ),
                            ),
                          ]),
                        ),
                      ),
          ),
        ),
        if (_result != null)
          Container(
            margin: const EdgeInsets.all(16),
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: (_resultOk ? ShamelColors.success : ShamelColors.error).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _resultOk ? ShamelColors.success : ShamelColors.error),
            ),
            child: Row(children: [
              Icon(_resultOk ? Icons.check_circle : Icons.error_outline,
                  color: _resultOk ? ShamelColors.success : ShamelColors.error),
              const SizedBox(width: 10),
              Expanded(child: Text(_result!, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600))),
            ]),
          ),
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 24),
          child: SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              style: ElevatedButton.styleFrom(
                backgroundColor: ShamelColors.gold,
                foregroundColor: ShamelColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              onPressed: (_controller == null || _busy) ? null : _capture,
              child: _busy
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: ShamelColors.primary))
                  : const Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                      Icon(Icons.center_focus_strong), SizedBox(width: 8),
                      Text('مسح الآن', style: TextStyle(fontWeight: FontWeight.w800)),
                    ]),
            ),
          ),
        ),
      ]),
    );
  }
}
