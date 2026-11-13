import 'dart:convert';
import 'dart:math';

import 'package:flutter_secure_storage/flutter_secure_storage.dart';

abstract interface class SecureKeyValueStore {
  Future<String?> read(String key);
  Future<void> write(String key, String value);
}

class FlutterSecureKeyValueStore implements SecureKeyValueStore {
  FlutterSecureKeyValueStore({FlutterSecureStorage? storage})
      : _storage = storage ??
            const FlutterSecureStorage(
              aOptions: AndroidOptions(resetOnError: false),
            );

  final FlutterSecureStorage _storage;

  @override
  Future<String?> read(String key) => _storage.read(key: key);

  @override
  Future<void> write(String key, String value) =>
      _storage.write(key: key, value: value);
}

/// Creates one random SQLCipher key and keeps it in Android Keystore-backed
/// secure storage. Storage failures are deliberately propagated: the app must
/// never silently replace a lost key and make an existing database unreadable.
class SecureDatabaseKeyProvider {
  SecureDatabaseKeyProvider({required SecureKeyValueStore store})
      : _store = store;

  static const databaseKeyStorageName = 'personelise_sqlcipher_database_key_v1';
  static const _keyByteLength = 32;

  final SecureKeyValueStore _store;
  Future<String>? _inFlight;

  Future<String> getOrCreateKey() {
    final active = _inFlight;
    if (active != null) return active;

    final request = _loadOrCreateKey();
    _inFlight = request;
    return request.whenComplete(() {
      if (identical(_inFlight, request)) _inFlight = null;
    });
  }

  Future<String> _loadOrCreateKey() async {
    final existing = await _store.read(databaseKeyStorageName);
    if (existing != null && existing.isNotEmpty) return existing;

    final random = Random.secure();
    final bytes = List<int>.generate(
      _keyByteLength,
      (_) => random.nextInt(256),
      growable: false,
    );
    final generated = base64UrlEncode(bytes).replaceAll('=', '');

    await _store.write(databaseKeyStorageName, generated);
    final persisted = await _store.read(databaseKeyStorageName);
    if (persisted != generated) {
      throw StateError('Database encryption key could not be verified in secure storage.');
    }
    return generated;
  }
}
