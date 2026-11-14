import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/app/personelise_app.dart';

void main() {
  testWidgets('auth screen does not offer local demo access when backend is unconfigured', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: AuthScreen(
        apiConfigured: false,
        isSignup: false,
        busy: false,
        error: null,
        onModeChanged: (_) {},
        onSubmit: ({
          required String email,
          required String password,
          required String displayName,
        }) async {},
      ),
    ));

    expect(find.text('Personelise Gym'), findsOneWidget);
    expect(find.textContaining('Account service is not configured yet.'), findsOneWidget);
    expect(find.text('Create account'), findsNothing);
    expect(find.text('Sign in'), findsNothing);
  });

  testWidgets('authentication screen exposes sign-in mode when configured', (tester) async {
    await tester.pumpWidget(MaterialApp(
      home: AuthScreen(
        apiConfigured: true,
        isSignup: false,
        busy: false,
        error: null,
        onModeChanged: (_) {},
        onSubmit: ({
          required String email,
          required String password,
          required String displayName,
        }) async {},
      ),
    ));

    expect(find.text('Sign in'), findsOneWidget);
    expect(find.text('New here? Create an account'), findsOneWidget);
  });
}
