import 'package:flutter_test/flutter_test.dart';
import 'package:shamel/api.dart';

void main() {
  group('ApiException hierarchy', () {
    test('ApiException carries message and statusCode', () {
      final e = ApiException('خطأ في الخادم', statusCode: 500);
      expect(e.message, 'خطأ في الخادم');
      expect(e.statusCode, 500);
    });

    test('AuthException is ApiException (401)', () {
      final e = AuthException();
      expect(e, isA<ApiException>());
      expect(e.statusCode, 401);
    });

    test('PermissionException is ApiException (403)', () {
      final e = PermissionException();
      expect(e, isA<ApiException>());
      expect(e.statusCode, 403);
    });

    test('NotFoundException is ApiException (404)', () {
      final e = NotFoundException();
      expect(e, isA<ApiException>());
      expect(e.statusCode, 404);
    });

    test('AuthException caught as ApiException', () {
      void throws() => throw AuthException();
      expect(throws, throwsA(isA<ApiException>()));
    });

    test('PermissionException caught as ApiException', () {
      void throws() => throw PermissionException();
      expect(throws, throwsA(isA<ApiException>()));
    });
  });
}
