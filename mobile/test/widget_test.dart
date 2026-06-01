import 'package:flutter_test/flutter_test.dart';
import 'package:shamel/main.dart';

void main() {
  testWidgets('SHAMEL app boots', (WidgetTester tester) async {
    await tester.pumpWidget(const ShamelApp());
    expect(find.byType(ShamelApp), findsOneWidget);
  });
}
