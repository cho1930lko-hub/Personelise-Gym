import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/data/local/local_database.dart';
import 'package:personelise_gym/data/local/secure_database_key_store.dart';
import 'package:personelise_gym/data/repositories/fitness_models.dart';
import 'package:personelise_gym/data/repositories/local_fitness_repository.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

class _MemorySecureStore implements SecureKeyValueStore {
  final Map<String, String> values = {};

  @override
  Future<String?> read(String key) async => values[key];

  @override
  Future<void> write(String key, String value) async {
    values[key] = value;
  }
}

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  late LocalDatabase database;
  late LocalFitnessRepository repository;

  setUp(() {
    database = LocalDatabase(
      databasePath: inMemoryDatabasePath,
      keyProvider: SecureDatabaseKeyProvider(store: _MemorySecureStore()),
      databaseOpener: ({
        required path,
        required password,
        required version,
        required onConfigure,
        required onCreate,
      }) =>
          databaseFactoryFfi.openDatabase(
        path,
        options: OpenDatabaseOptions(
          version: version,
          onConfigure: onConfigure,
          onCreate: onCreate,
        ),
      ),
    );
    repository = LocalFitnessRepository(database);
  });

  tearDown(() async => database.close());

  DateTime get now => DateTime.utc(2026, 11, 13);

  Future<void> createProfile(String userId) async {
    await repository.saveProfile(FitnessProfile(
      userId: userId,
      displayName: userId,
      heightCm: 170,
      createdAt: now,
      updatedAt: now,
    ));
  }

  test('typed workout CRUD is isolated by user and queued atomically', () async {
    await createProfile('user-a');
    await createProfile('user-b');

    final workout = WorkoutLog(
      recordId: 'workout-a1',
      userId: 'user-a',
      workoutDate: now,
      muscleGroup: 'Chest',
      exerciseName: 'Bench Press',
      sets: const [
        WorkoutSet(weightKg: 40, reps: 10),
        WorkoutSet(weightKg: 45, reps: 8),
      ],
      createdAt: now,
      updatedAt: now,
    );
    await repository.saveWorkout(workout);

    final userA = await repository.getWorkoutLogs('user-a');
    final userB = await repository.getWorkoutLogs('user-b');
    expect(userA, hasLength(1));
    expect(userA.single.sets[1].weightKg, 45);
    expect(userB, isEmpty);

    await repository.deleteWorkout('user-b', 'workout-a1');
    expect(await repository.getWorkoutLogs('user-a'), hasLength(1));

    await repository.deleteWorkout('user-a', 'workout-a1');
    expect(await repository.getWorkoutLogs('user-a'), isEmpty);

    final pending = await database.getPendingSyncItems('user-a');
    expect(pending, hasLength(2));
    expect(pending.last['operation'], 'delete');
  });

  test('typed body stats and settings round trip per user', () async {
    await createProfile('user-a');
    await createProfile('user-b');

    await repository.saveBodyStat(BodyStat(
      recordId: 'body-a1',
      userId: 'user-a',
      measuredAt: now,
      weightKg: 72.5,
      heightCm: 172,
      createdAt: now,
      updatedAt: now,
    ));
    await repository.saveSettings(UserSettings(
      userId: 'user-a',
      values: const {'theme': 'dark', 'weight_unit': 'kg'},
      updatedAt: now,
    ));

    final statsA = await repository.getBodyStats('user-a');
    final statsB = await repository.getBodyStats('user-b');
    expect(statsA.single.weightKg, 72.5);
    expect(statsB, isEmpty);

    final settings = await repository.getSettings('user-a');
    expect(settings?.values['theme'], 'dark');
    expect(await repository.getSettings('user-b'), isNull);

    await repository.deleteBodyStat('user-a', 'body-a1');
    expect(await repository.getBodyStats('user-a'), isEmpty);
  });

  test('weekly tracker and exercise checklist round trip', () async {
    await createProfile('user-a');

    await repository.saveWeeklyTracker(WeeklyTracker(
      recordId: 'week-a1',
      userId: 'user-a',
      weekStart: now,
      targetDays: 4,
      completedDays: const [1, 3],
      updatedAt: now,
    ));
    await repository.saveChecklistItem(ExerciseChecklistItem(
      userId: 'user-a',
      exerciseId: 'bench-press',
      isChecked: true,
      updatedAt: now,
    ));

    final tracker = await repository.getWeeklyTracker('user-a', now);
    final checklist = await repository.getChecklist('user-a');
    expect(tracker?.targetDays, 4);
    expect(tracker?.completedDays, [1, 3]);
    expect(checklist.single.isChecked, isTrue);
  });
}
