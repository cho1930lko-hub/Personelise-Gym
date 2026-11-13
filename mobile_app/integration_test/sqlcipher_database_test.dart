import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:path/path.dart' as p;
import 'package:personelise_gym/data/local/local_database.dart';
import 'package:personelise_gym/data/local/secure_database_key_store.dart';
import 'package:sqflite_sqlcipher/sqflite.dart';

class _MemoryKeyStore implements SecureKeyValueStore {
  _MemoryKeyStore(this.key);

  final String key;

  @override
  Future<String?> read(String name) async => key;

  @override
  Future<void> write(String name, String value) async {}
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('SQLCipher persists data with correct key and rejects wrong key',
      (tester) async {
    final dbDirectory = await getDatabasesPath();
    final path = p.join(
      dbDirectory,
      'personelise_sqlcipher_${DateTime.now().microsecondsSinceEpoch}.db',
    );

    const correctKey = 'integration-test-key-256-bit-material';
    final first = LocalDatabase(
      databasePath: path,
      keyProvider: SecureDatabaseKeyProvider(
        store: _MemoryKeyStore(correctKey),
      ),
    );

    await first.upsertProfile(
      userId: 'sqlcipher-user',
      displayName: 'Encrypted User',
      heightCm: 172,
    );
    await first.close();

    final reopened = LocalDatabase(
      databasePath: path,
      keyProvider: SecureDatabaseKeyProvider(
        store: _MemoryKeyStore(correctKey),
      ),
    );
    final profile = await reopened.database.then(
      (db) => db.query(
        'profiles',
        where: 'user_id = ?',
        whereArgs: ['sqlcipher-user'],
        limit: 1,
      ),
    );
    expect(profile, hasLength(1));
    expect(profile.single['display_name'], 'Encrypted User');
    await reopened.close();

    final wrongKey = LocalDatabase(
      databasePath: path,
      keyProvider: SecureDatabaseKeyProvider(
        store: _MemoryKeyStore('definitely-the-wrong-key'),
      ),
    );
    await expectLater(
      wrongKey.database,
      throwsA(anything),
    );
    await wrongKey.close();
    await deleteDatabase(path);
  });

  testWidgets('Android secure storage returns a stable database key',
      (tester) async {
    final provider = SecureDatabaseKeyProvider(
      store: FlutterSecureKeyValueStore(),
    );
    final firstKey = await provider.getOrCreateKey();
    final secondKey = await provider.getOrCreateKey();

    expect(firstKey, isNotEmpty);
    expect(secondKey, firstKey);
  });
}
