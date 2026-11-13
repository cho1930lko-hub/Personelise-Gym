import 'dart:convert';

import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';
import 'package:uuid/uuid.dart';

class LocalDatabase {
  LocalDatabase({this.databasePath});

  final String? databasePath;
  static const _databaseName = 'personelise_gym.db';
  static const _databaseVersion = 1;
  static const _uuid = Uuid();

  Database? _instance;

  Future<Database> get database async {
    if (_instance != null) return _instance!;
    final path = databasePath ?? p.join(await getDatabasesPath(), _databaseName);
    _instance = await openDatabase(
      path,
      version: _databaseVersion,
      onConfigure: (db) async {
        await db.execute('PRAGMA foreign_keys = ON');
      },
      onCreate: _createSchema,
    );
    return _instance!;
  }

  Future<void> _createSchema(Database db, int version) async {
    await db.execute('''
      CREATE TABLE profiles (
        user_id TEXT PRIMARY KEY,
        display_name TEXT NOT NULL,
        height_cm REAL,
        current_weight_kg REAL,
        goal_weight_kg REAL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');

    await db.execute('''
      CREATE TABLE workout_logs (
        record_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        workout_date TEXT NOT NULL,
        muscle_group TEXT NOT NULL,
        exercise_name TEXT NOT NULL,
        sets_json TEXT NOT NULL,
        notes TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE body_stats (
        record_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        measured_at TEXT NOT NULL,
        weight_kg REAL NOT NULL,
        height_cm REAL NOT NULL,
        notes TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE weekly_tracker (
        record_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        week_start TEXT NOT NULL,
        target_days INTEGER NOT NULL,
        completed_days_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        UNIQUE(user_id, week_start),
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE exercise_checklist (
        user_id TEXT NOT NULL,
        exercise_id TEXT NOT NULL,
        is_checked INTEGER NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        PRIMARY KEY(user_id, exercise_id),
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE user_settings (
        user_id TEXT PRIMARY KEY,
        settings_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'pending',
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute('''
      CREATE TABLE sync_queue (
        queue_id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        record_id TEXT NOT NULL,
        operation TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        attempt_count INTEGER NOT NULL DEFAULT 0,
        last_error TEXT NOT NULL DEFAULT '',
        FOREIGN KEY (user_id) REFERENCES profiles(user_id) ON DELETE CASCADE
      )
    ''');

    await db.execute(
      'CREATE INDEX idx_workout_user_date ON workout_logs(user_id, workout_date)',
    );
    await db.execute(
      'CREATE INDEX idx_body_stats_user_date ON body_stats(user_id, measured_at)',
    );
    await db.execute(
      'CREATE INDEX idx_sync_queue_user_created ON sync_queue(user_id, created_at)',
    );
  }

  Future<void> upsertProfile({
    required String userId,
    required String displayName,
    double? heightCm,
    double? currentWeightKg,
    double? goalWeightKg,
  }) async {
    final db = await database;
    final now = DateTime.now().toUtc().toIso8601String();
    await db.transaction((txn) async {
      final existing = await txn.query(
        'profiles',
        columns: ['user_id'],
        where: 'user_id = ?',
        whereArgs: [userId],
        limit: 1,
      );
      final values = <String, Object?>{
        'display_name': displayName.trim(),
        'height_cm': heightCm,
        'current_weight_kg': currentWeightKg,
        'goal_weight_kg': goalWeightKg,
        'updated_at': now,
      };

      if (existing.isEmpty) {
        await txn.insert('profiles', {
          'user_id': userId,
          ...values,
          'created_at': now,
        });
      } else {
        await txn.update(
          'profiles',
          values,
          where: 'user_id = ?',
          whereArgs: [userId],
        );
      }
    });
  }

  Future<String> addWorkoutLog({
    required String userId,
    required DateTime workoutDate,
    required String muscleGroup,
    required String exerciseName,
    required List<Map<String, num>> sets,
    String notes = '',
  }) async {
    final db = await database;
    final recordId = _uuid.v4();
    final now = DateTime.now().toUtc().toIso8601String();
    final payload = <String, Object?>{
      'record_id': recordId,
      'user_id': userId,
      'workout_date': workoutDate.toUtc().toIso8601String(),
      'muscle_group': muscleGroup,
      'exercise_name': exerciseName,
      'sets': sets,
      'notes': notes,
      'created_at': now,
      'updated_at': now,
    };

    await db.transaction((txn) async {
      await txn.insert('workout_logs', {
        'record_id': recordId,
        'user_id': userId,
        'workout_date': payload['workout_date'],
        'muscle_group': muscleGroup,
        'exercise_name': exerciseName,
        'sets_json': jsonEncode(sets),
        'notes': notes,
        'created_at': now,
        'updated_at': now,
        'sync_status': 'pending',
      });
      await txn.insert('sync_queue', {
        'queue_id': _uuid.v4(),
        'user_id': userId,
        'entity_type': 'workout_log',
        'record_id': recordId,
        'operation': 'upsert',
        'payload_json': jsonEncode(payload),
        'created_at': now,
      });
    });
    return recordId;
  }

  Future<List<Map<String, Object?>>> getWorkoutLogs(String userId) async {
    final db = await database;
    return db.query(
      'workout_logs',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'workout_date DESC',
    );
  }

  Future<List<Map<String, Object?>>> getPendingSyncItems(String userId) async {
    final db = await database;
    return db.query(
      'sync_queue',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'created_at ASC',
    );
  }

  Future<void> close() async {
    await _instance?.close();
    _instance = null;
  }
}
