// SHAMEL gRPC Face Service client for Flutter.
//
// Usage:
//   final client = ShamelGrpcClient(host: '10.0.2.2', port: 50051);
//   await client.connect();
//   final result = await client.scanGate(imageBytes, authToken: token);
//   client.close();
//
// Proto stubs must be generated before use:
//   dart pub global activate protoc_plugin
//   protoc --dart_out=grpc:lib/grpc_generated -I../proto ../proto/face_service.proto
//
// Until stubs are generated, the HTTP fallback in api.dart remains active.

import 'dart:typed_data';

// Stub classes mirroring the proto — replace with generated code after running protoc.
// ignore_for_file: non_constant_identifier_names

class BoundingBox {
  final double x1, y1, x2, y2;
  const BoundingBox(this.x1, this.y1, this.x2, this.y2);
}

class PersonInfo {
  final String name;
  final String type; // "student" | "teacher"
  final bool allowed;
  final String denyReason;
  final bool cooldown;
  final String studentCode;
  final String phone;
  final bool registered;
  final bool feesPaid;

  const PersonInfo({
    required this.name,
    required this.type,
    required this.allowed,
    this.denyReason = '',
    this.cooldown = false,
    this.studentCode = '',
    this.phone = '',
    this.registered = true,
    this.feesPaid = true,
  });
}

class FaceResult {
  final bool matched;
  final BoundingBox? bbox;
  final PersonInfo? person;
  const FaceResult({required this.matched, this.bbox, this.person});
}

class GateScanResponse {
  final bool ok;
  final bool detected;
  final String error;
  final List<FaceResult> results;
  final int frameWidth;
  final int frameHeight;

  const GateScanResponse({
    required this.ok,
    this.detected = false,
    this.error = '',
    this.results = const [],
    this.frameWidth = 0,
    this.frameHeight = 0,
  });
}

class LoginResponse {
  final bool success;
  final String name;
  final String redirectUrl;
  final String error;
  final String sessionKey; // auth token for Flutter
  const LoginResponse({
    required this.success,
    this.name = '',
    this.redirectUrl = '',
    this.error = '',
    this.sessionKey = '',
  });
}

class EnrollResponse {
  final bool success;
  final String error;
  final int angleIndex;
  const EnrollResponse({required this.success, this.error = '', this.angleIndex = 0});
}

class HealthResponse {
  final bool engineAvailable;
  final String engineName;
  final int studentEmbeddings;
  final int teacherEmbeddings;
  final int dimMismatchCount;
  final String engineDim;

  const HealthResponse({
    required this.engineAvailable,
    this.engineName = '',
    this.studentEmbeddings = 0,
    this.teacherEmbeddings = 0,
    this.dimMismatchCount = 0,
    this.engineDim = '512',
  });
}

/// Thin wrapper around the SHAMEL gRPC face service.
/// Replace the stub implementations below with generated gRPC calls
/// after running `protoc --dart_out=grpc:lib/grpc_generated`.
class ShamelGrpcClient {
  final String host;
  final int port;
  bool _connected = false;

  ShamelGrpcClient({required this.host, this.port = 50051});

  Future<void> connect() async {
    // TODO: initialize grpc.ClientChannel after proto stubs are generated
    // _channel = grpc.ClientChannel(host, port: port, ...);
    // _stub = FaceServiceClient(_channel);
    _connected = true;
  }

  void close() {
    _connected = false;
    // _channel?.shutdown();
  }

  bool get isConnected => _connected;

  /// Gate scan — match face against all enrolled persons
  Future<GateScanResponse> scanGate(
    Uint8List imageBytes, {
    required String authToken,
  }) async {
    _assertConnected();
    // TODO: replace with generated stub call:
    // final req = FrameRequest()..imageData = imageBytes ..authToken = authToken;
    // final resp = await _stub.scanGate(req);
    // return _mapGateResponse(resp);
    throw UnimplementedError(
      'Run protoc to generate Dart stubs from proto/face_service.proto, '
      'then replace this stub with real gRPC calls.',
    );
  }

  /// Face login — returns auth token on success
  Future<LoginResponse> loginFace(Uint8List imageBytes) async {
    _assertConnected();
    throw UnimplementedError('Generate Dart stubs from proto/face_service.proto');
  }

  /// Enroll a face angle
  Future<EnrollResponse> enrollFace(
    Uint8List imageBytes, {
    required String authToken,
    required String personType,
    required int personId,
    int angleIndex = 0,
  }) async {
    _assertConnected();
    throw UnimplementedError('Generate Dart stubs from proto/face_service.proto');
  }

  /// Health check — returns engine status + DB embedding audit
  Future<HealthResponse> healthCheck() async {
    _assertConnected();
    throw UnimplementedError('Generate Dart stubs from proto/face_service.proto');
  }

  void _assertConnected() {
    if (!_connected) throw StateError('Call connect() first');
  }
}

/// Generate stubs by running from the project root:
///
///   dart pub global activate protoc_plugin
///   protoc \
///     --dart_out=grpc:mobile/lib/grpc_generated \
///     -I proto \
///     proto/face_service.proto
///
/// Then replace the stub bodies in this file with:
///
///   import 'grpc_generated/face_service.pbgrpc.dart';
///   import 'grpc_generated/face_service.pb.dart';
