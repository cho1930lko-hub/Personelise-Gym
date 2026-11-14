import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:personelise_gym/data/auth/auth_api_client.dart';
import 'package:personelise_gym/data/auth/auth_session.dart';
import 'package:personelise_gym/data/auth/secure_session_store.dart';
import 'package:personelise_gym/data/local/secure_database_key_store.dart';

class _MemorySecureStore implements SecureKeyValueStore {
  final values = <String, String>{};

  @override
  Future<String?> read(String key) async => values[key];

  @override
  Future<void> write(String key, String value) async => values[key] = value;

  @override
  Future<void> delete(String key) async => values.remove(key);
}

void main() {
  final futureExpiry = DateTime.utc(2035, 1, 1);

  AuthSession session({DateTime? expiresAt}) => AuthSession(
        accessToken: 'signed-token',
        userId: 'account-a',
        email: 'a@example.test',
        expiresAt: expiresAt ?? futureExpiry,
      );

  test('session JSON round-trips without losing account identity', () {
    final original = session();
    final decoded = AuthSession.fromJson(original.toJson());

    expect(decoded.accessToken, original.accessToken);
    expect(decoded.userId, original.userId);
    expect(decoded.email, original.email);
    expect(decoded.expiresAt, original.expiresAt);
  });

  test('invalid session payload is rejected', () {
    expect(
      () => AuthSession.fromJson({'access_token': '', 'user_id': 'x'}),
      throwsFormatException,
    );
  });

  test('secure session store saves, reads, and deletes session', () async {
    final backing = _MemorySecureStore();
    final store = SecureSessionStore(store: backing);
    await store.save(session());

    expect((await store.read())?.userId, 'account-a');
    await store.clear();
    expect(await store.read(), isNull);
    expect(backing.values, isEmpty);
  });

  test('expired and malformed sessions are cleared on read', () async {
    final backing = _MemorySecureStore();
    final store = SecureSessionStore(store: backing);
    await store.save(session(expiresAt: DateTime.utc(2020)));
    expect(await store.read(), isNull);
    expect(backing.values, isEmpty);

    backing.values[SecureSessionStore.storageKey] = '{broken';
    expect(await store.read(), isNull);
    expect(backing.values, isEmpty);
  });

  test('login sends action-based request and parses server session', () async {
    late http.Request captured;
    final client = AuthApiClient(
      baseUri: Uri.parse('https://script.google.com/macros/s/test/exec'),
      client: MockClient((request) async {
        captured = request;
        return http.Response(jsonEncode(session().toJson()), 200);
      }),
    );

    final result = await client.signIn(
      email: ' A@Example.Test ',
      password: 'correct horse battery staple',
    );
    final body = jsonDecode(captured.body) as Map<String, dynamic>;

    expect(captured.method, 'POST');
    expect(body['action'], 'login');
    expect(body['email'], 'a@example.test');
    expect(body['password'], 'correct horse battery staple');
    expect(result.userId, 'account-a');
  });

  test('profile uses POST body token and never trusts a user id argument', () async {
    late http.Request captured;
    final client = AuthApiClient(
      baseUri: Uri.parse('https://script.google.com/macros/s/test/exec'),
      client: MockClient((request) async {
        captured = request;
        return http.Response(jsonEncode({'user_id': 'account-a'}), 200);
      }),
    );

    final result = await client.getProfile(session());
    final body = jsonDecode(captured.body) as Map<String, dynamic>;

    expect(captured.method, 'POST');
    expect(body['action'], 'profile');
    expect(body['access_token'], 'signed-token');
    expect(body.containsKey('user_id'), isFalse);
    expect(result['user_id'], 'account-a');
  });

  test('API error response is surfaced without accepting a session', () async {
    final client = AuthApiClient(
      baseUri: Uri.parse('https://script.google.com/macros/s/test/exec'),
      client: MockClient((_) async =>
          http.Response(jsonEncode({'error': 'Invalid credentials'}), 401)),
    );

    await expectLater(
      client.signIn(email: 'a@example.test', password: 'wrong'),
      throwsA(isA<AuthApiException>().having(
        (error) => error.statusCode,
        'statusCode',
        401,
      )),
    );
  });
}
