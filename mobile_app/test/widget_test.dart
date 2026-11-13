import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/app/personelise_app.dart';

void main() {
  testWidgets('app shell renders navigation destinations', (tester) async {
    await tester.pumpWidget(const PersoneliseApp());

    expect(find.text('Your fitness'), findsOneWidget);
    expect(find.text('Home'), findsOneWidget);
    expect(find.text('Workout'), findsOneWidget);
    expect(find.text('Progress'), findsOneWidget);
    expect(find.text('Profile'), findsOneWidget);
  });

  testWidgets('bottom navigation changes section', (tester) async {
    await tester.pumpWidget(const PersoneliseApp());

    await tester.tap(find.text('Workout'));
    await tester.pumpAndSettle();

    expect(find.text('Workout'), findsWidgets);
    expect(find.text('This section will be added in its development phase.'),
        findsOneWidget);
  });
}
