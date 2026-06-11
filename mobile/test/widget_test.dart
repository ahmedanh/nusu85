// Root smoke test — re-exports sub-suites for `flutter test` discovery.
// Run all: flutter test
// Run unit only: flutter test test/unit/
// Run widget only: flutter test test/widget/
export 'unit/api_exceptions_test.dart';
export 'unit/local_db_test.dart';
export 'widget/login_screen_test.dart';
export 'widget/widgets_test.dart';
