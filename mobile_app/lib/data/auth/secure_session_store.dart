import 'dart:convert';

import '../local/secure_database_key_store.dart';
import 'auth_session.dart';

class SecureSessionStore {
  SecureSessionStore({required SecureKeyValueStore store}) : _store = store;

  static const storageKey = 'personelise_auth_session_v1';
  final SecureKeyValueStore _store;

  Future<void> save(AuthSession session) async {
    await _store.write(storageKey, jsonEncode(session.toJson()));
  }

  Future<AuthSession?> read() async {
    final raw = await _store.read(storageKey);
    if (raw == null || raw.isEmpty) return null;
    try {
      final decoded = jsonDecode(raw);
      if (decoded is! Map<String, dynamic>) {
        throw const FormatException('Invalid stored session.');
      }
      final session = AuthSession.fromJson(decoded);
      if (session.isExpired) {
        await clear();
        return null;
      }
      return session;
    } on FormatException {
      await clear();
      return null;
    }
  }

  Future<void> clear() => _store.write(storageKey, '');
}
