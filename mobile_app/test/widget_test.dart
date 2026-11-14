import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/app/personelise_app.dart';

void main() {
  testWidgets('app asks for backend configuration instead of creating a demo account', (tester) async {
    await tester.pumpWidget(const PersoneliseApp());
    await tester.pumpAndSettle();

    expect(find.text('Personelise Gym'), findsOneWidget);
    expect(find.textContaining('Account service is not configured yet.'), findsOneWidget);
    expect(find.text('Create account'), findsNothing);
  });

  testWidgets('authentication screen exposes sign-in and signup modes when configured', (tester) async {
    var signupMode = false;
    await tester.pumpWidget(MaterialApp(
      home: AuthScreen(
        apiConfigured: true,
        isSignup: signupMode,
        busy: false,
        error: null,
        onModeChanged: (value) => signupMode = value,
        onSubmit: ({
          required email,
          required password,
          required displayName,
        }) async {},
      ),
    ));

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('New here? Create an account'), findsOneWidget);
  });
}
