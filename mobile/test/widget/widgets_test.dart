import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shamel/theme.dart';
import 'package:shamel/widgets.dart';

Widget _m(Widget child) => MaterialApp(
      theme: ShamelTheme.light(),
      home: Scaffold(body: child),
    );

void main() {
  group('StatCard', () {
    testWidgets('renders label and value', (tester) async {
      await tester.pumpWidget(_m(const StatCard(
        label: 'الطلاب', value: '120', icon: Icons.school_outlined)));
      expect(find.text('الطلاب'), findsOneWidget);
      expect(find.text('120'),    findsOneWidget);
    });
  });

  group('LoadingOrError', () {
    testWidgets('shows SkeletonList when loading=true + skeleton=true',
        (tester) async {
      await tester.pumpWidget(
          _m(const LoadingOrError(loading: true, skeleton: true)));
      expect(find.byType(SkeletonList), findsOneWidget);
    });

    testWidgets('shows CircularProgressIndicator when skeleton=false',
        (tester) async {
      await tester.pumpWidget(
          _m(const LoadingOrError(loading: true, skeleton: false)));
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('shows error text and retry button', (tester) async {
      var retried = false;
      await tester.pumpWidget(_m(LoadingOrError(
        loading: false,
        error: 'فشل التحميل',
        onRetry: () => retried = true,
      )));
      expect(find.text('فشل التحميل'),    findsOneWidget);
      expect(find.text('إعادة المحاولة'), findsOneWidget);
      await tester.tap(find.text('إعادة المحاولة'));
      expect(retried, isTrue);
    });
  });

  group('SkeletonGrid', () {
    testWidgets('renders without overflow', (tester) async {
      await tester.pumpWidget(_m(const SingleChildScrollView(
          child: SkeletonGrid(count: 4))));
      expect(tester.takeException(), isNull);
    });
  });
}
