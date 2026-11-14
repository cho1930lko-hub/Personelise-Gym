import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/data/local/secure_database_key_store.dart';

class _MemorySecureStore implements SecureKeyValueStore {
  final Map<String, String> values = {};

  @override
  Future<String?> read(String key) async => values[key];

  @override
  Future<void> write(String key, String value) async {
    values[key] = value;
  }

  @override
  Future<void> delete(String key) async {
    values.remove(key);
  }
}

void main() {
  test('creates a cryptographically random 256-bit database key', () async {
    final store = _MemorySecureStore();
    final provider = SecureDatabaseKeyProvider(store: store);

    final key = await provider.getOrCreateKey();
    final decoded = base64Url.decode(base64Url.normalize(key));

    expect(decoded, hasLength(32));
    expect(store.values[SecureDatabaseKeyProvider.databaseKeyStorageName], key);
  });

  test('reuses the existing key after provider recreation', () async {
    final store = _MemorySecureStore();
    final firstProvider = SecureDatabaseKeyProvider(store: store);
    final firstKey = await firstProvider.getOrCreateKey();

    final secondProvider = SecureDatabaseKeyProvider(store: store);
    final secondKey = await secondProvider.getOrCreateKey();

    expect(secondKey, firstKey);
    expect(store.values, hasLength(1));
  });

  test('does not replace a stored key with a new key', () async {
    final store = _MemorySecureStore();
    store.values[SecureDatabaseKeyProvider.databaseKeyStorageName] =
        'existing-key-value';

    final provider = SecureDatabaseKeyProvider(store: store);

    expect(await provider.getOrCreateKey(), 'existing-key-value');
    expect(store.values.values, ['existing-key-value']);
  });
}
