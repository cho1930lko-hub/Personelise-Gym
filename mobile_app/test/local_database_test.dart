import 'package:flutter_test/flutter_test.dart';
import 'package:personelise_gym/data/local/local_database.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  late LocalDatabase localDatabase;

  setUp(() {
    localDatabase = LocalDatabase(databasePath: inMemoryDatabasePath);
  });

  tearDown(() async {
    await localDatabase.close();
  });

  test('workout records and sync queue are isolated by user ID', () async {
    await localDatabase.upsertProfile(userId: 'user-a', displayName: 'Person A');
    await localDatabase.upsertProfile(userId: 'user-b', displayName: 'Person B');

    await localDatabase.addWorkoutLog(
      userId: 'user-a',
      workoutDate: DateTime.utc(2026, 11, 13),
      muscleGroup: 'Chest',
      exerciseName: 'Bench Press',
      sets: [
        {'weight_kg': 40, 'reps': 10},
        {'weight_kg': 45, 'reps': 8},
      ],
    );

    final userAWorkouts = await localDatabase.getWorkoutLogs('user-a');
    final userBWorkouts = await localDatabase.getWorkoutLogs('user-b');
    final userASync = await localDatabase.getPendingSyncItems('user-a');
    final userBSync = await localDatabase.getPendingSyncItems('user-b');

    expect(userAWorkouts, hasLength(1));
    expect(userBWorkouts, isEmpty);
    expect(userASync, hasLength(1));
    expect(userBSync, isEmpty);
  });

  test('workout insert and sync queue write are atomic', () async {
    await localDatabase.upsertProfile(userId: 'user-a', displayName: 'Person A');

    await localDatabase.addWorkoutLog(
      userId: 'user-a',
      workoutDate: DateTime.utc(2026, 11, 13),
      muscleGroup: 'Back',
      exerciseName: 'Lat Pulldown',
      sets: [
        {'weight_kg': 35, 'reps': 12},
      ],
    );

    final logs = await localDatabase.getWorkoutLogs('user-a');
    final queue = await localDatabase.getPendingSyncItems('user-a');

    expect(logs, hasLength(1));
    expect(queue, hasLength(1));
    expect(queue.single['record_id'], logs.single['record_id']);
  });
  test('updating a profile does not delete its existing workouts', () async {
    await localDatabase.upsertProfile(userId: 'user-a', displayName: 'Person A');
    await localDatabase.addWorkoutLog(
      userId: 'user-a',
      workoutDate: DateTime.utc(2026, 11, 13),
      muscleGroup: 'Legs',
      exerciseName: 'Squat',
      sets: [
        {'weight_kg': 50, 'reps': 8},
      ],
    );

    await localDatabase.upsertProfile(
      userId: 'user-a',
      displayName: 'Person A Updated',
      heightCm: 172,
    );

    final logs = await localDatabase.getWorkoutLogs('user-a');
    expect(logs, hasLength(1));
    expect(logs.single['exercise_name'], 'Squat');
  });

}
