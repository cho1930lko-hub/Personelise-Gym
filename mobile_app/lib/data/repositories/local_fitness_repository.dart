import 'dart:convert';

import 'package:sqflite_sqlcipher/sqflite.dart';
import 'package:uuid/uuid.dart';

import '../local/local_database.dart';
import 'fitness_models.dart';
import 'fitness_repository.dart';

class LocalFitnessRepository implements FitnessRepository {
  LocalFitnessRepository(this._localDatabase);

  final LocalDatabase _localDatabase;
  static const _uuid = Uuid();

  String _now() => DateTime.now().toUtc().toIso8601String();

  Future<void> _queue(
    DatabaseExecutor executor, {
    required String userId,
    required String entityType,
    required String recordId,
    required String operation,
    required Map<String, Object?> payload,
  }) async {
    await executor.insert('sync_queue', {
      'queue_id': _uuid.v4(),
      'user_id': userId,
      'entity_type': entityType,
      'record_id': recordId,
      'operation': operation,
      'payload_json': jsonEncode(payload),
      'created_at': _now(),
    });
  }

  Future<void> _upsert(
    DatabaseExecutor executor,
    String table,
    Map<String, Object?> values, {
    required String where,
    required List<Object?> whereArgs,
  }) async {
    final existing = await executor.query(
      table,
      columns: ['rowid'],
      where: where,
      whereArgs: whereArgs,
      limit: 1,
    );
    if (existing.isEmpty) {
      await executor.insert(table, values);
    } else {
      await executor.update(table, values, where: where, whereArgs: whereArgs);
    }
  }

  @override
  Future<void> saveProfile(FitnessProfile profile) async {
    final db = await _localDatabase.database;
    await db.transaction((txn) async {
      final values = <String, Object?>{
        'user_id': profile.userId,
        'display_name': profile.displayName.trim(),
        'height_cm': profile.heightCm,
        'current_weight_kg': profile.currentWeightKg,
        'goal_weight_kg': profile.goalWeightKg,
        'created_at': profile.createdAt.toUtc().toIso8601String(),
        'updated_at': profile.updatedAt.toUtc().toIso8601String(),
      };
      await _upsert(txn, 'profiles', values,
          where: 'user_id = ?', whereArgs: [profile.userId]);
    });
  }

  @override
  Future<FitnessProfile?> getProfile(String userId) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'profiles',
      where: 'user_id = ?',
      whereArgs: [userId],
      limit: 1,
    );
    return rows.isEmpty ? null : FitnessProfile.fromMap(rows.single);
  }

  @override
  Future<void> saveWorkout(WorkoutLog workout) async {
    final db = await _localDatabase.database;
    final now = _now();
    final workoutDate = workout.workoutDate.toUtc().toIso8601String();
    final sets = workout.sets.map((item) => item.toMap()).toList();
    final payload = <String, Object?>{
      'record_id': workout.recordId,
      'user_id': workout.userId,
      'workout_date': workoutDate,
      'muscle_group': workout.muscleGroup,
      'exercise_name': workout.exerciseName,
      'sets': sets,
      'notes': workout.notes,
      'updated_at': now,
    };

    await db.transaction((txn) async {
      final values = <String, Object?>{
        'record_id': workout.recordId,
        'user_id': workout.userId,
        'workout_date': workoutDate,
        'muscle_group': workout.muscleGroup,
        'exercise_name': workout.exerciseName,
        'sets_json': jsonEncode(sets),
        'notes': workout.notes,
        'created_at': workout.createdAt.toUtc().toIso8601String(),
        'updated_at': now,
        'sync_status': 'pending',
      };
      await _upsert(txn, 'workout_logs', values,
          where: 'record_id = ? AND user_id = ?',
          whereArgs: [workout.recordId, workout.userId]);
      await _queue(
        txn,
        userId: workout.userId,
        entityType: 'workout_log',
        recordId: workout.recordId,
        operation: 'upsert',
        payload: payload,
      );
    });
  }

  @override
  Future<List<WorkoutLog>> getWorkoutLogs(String userId) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'workout_logs',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'workout_date DESC',
    );
    return rows.map(WorkoutLog.fromMap).toList(growable: false);
  }

  @override
  Future<void> deleteWorkout(String userId, String recordId) async {
    final db = await _localDatabase.database;
    await db.transaction((txn) async {
      final deleted = await txn.delete(
        'workout_logs',
        where: 'record_id = ? AND user_id = ?',
        whereArgs: [recordId, userId],
      );
      if (deleted > 0) {
        await _queue(
          txn,
          userId: userId,
          entityType: 'workout_log',
          recordId: recordId,
          operation: 'delete',
          payload: {'record_id': recordId, 'user_id': userId},
        );
      }
    });
  }

  @override
  Future<void> saveBodyStat(BodyStat bodyStat) async {
    final db = await _localDatabase.database;
    final now = _now();
    final payload = <String, Object?>{
      'record_id': bodyStat.recordId,
      'user_id': bodyStat.userId,
      'measured_at': bodyStat.measuredAt.toUtc().toIso8601String(),
      'weight_kg': bodyStat.weightKg,
      'height_cm': bodyStat.heightCm,
      'notes': bodyStat.notes,
      'updated_at': now,
    };
    await db.transaction((txn) async {
      final values = <String, Object?>{
        ...payload,
        'created_at': bodyStat.createdAt.toUtc().toIso8601String(),
        'sync_status': 'pending',
      };
      await _upsert(txn, 'body_stats', values,
          where: 'record_id = ? AND user_id = ?',
          whereArgs: [bodyStat.recordId, bodyStat.userId]);
      await _queue(
        txn,
        userId: bodyStat.userId,
        entityType: 'body_stat',
        recordId: bodyStat.recordId,
        operation: 'upsert',
        payload: payload,
      );
    });
  }

  @override
  Future<List<BodyStat>> getBodyStats(String userId) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'body_stats',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'measured_at DESC',
    );
    return rows.map(BodyStat.fromMap).toList(growable: false);
  }

  @override
  Future<void> deleteBodyStat(String userId, String recordId) async {
    final db = await _localDatabase.database;
    await db.transaction((txn) async {
      final deleted = await txn.delete(
        'body_stats',
        where: 'record_id = ? AND user_id = ?',
        whereArgs: [recordId, userId],
      );
      if (deleted > 0) {
        await _queue(
          txn,
          userId: userId,
          entityType: 'body_stat',
          recordId: recordId,
          operation: 'delete',
          payload: {'record_id': recordId, 'user_id': userId},
        );
      }
    });
  }

  @override
  Future<void> saveWeeklyTracker(WeeklyTracker tracker) async {
    final db = await _localDatabase.database;
    final payload = <String, Object?>{
      'record_id': tracker.recordId,
      'user_id': tracker.userId,
      'week_start': tracker.weekStart.toUtc().toIso8601String(),
      'target_days': tracker.targetDays,
      'completed_days': tracker.completedDays,
      'updated_at': _now(),
    };
    await db.transaction((txn) async {
      final values = <String, Object?>{
        'record_id': tracker.recordId,
        'user_id': tracker.userId,
        'week_start': tracker.weekStart.toUtc().toIso8601String(),
        'target_days': tracker.targetDays,
        'completed_days_json': jsonEncode(tracker.completedDays),
        'updated_at': _now(),
        'sync_status': 'pending',
      };
      await _upsert(txn, 'weekly_tracker', values,
          where: 'user_id = ? AND week_start = ?',
          whereArgs: [
            tracker.userId,
            tracker.weekStart.toUtc().toIso8601String(),
          ]);
      await _queue(
        txn,
        userId: tracker.userId,
        entityType: 'weekly_tracker',
        recordId: tracker.recordId,
        operation: 'upsert',
        payload: payload,
      );
    });
  }

  @override
  Future<WeeklyTracker?> getWeeklyTracker(
    String userId,
    DateTime weekStart,
  ) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'weekly_tracker',
      where: 'user_id = ? AND week_start = ?',
      whereArgs: [userId, weekStart.toUtc().toIso8601String()],
      limit: 1,
    );
    return rows.isEmpty ? null : WeeklyTracker.fromMap(rows.single);
  }

  @override
  Future<void> saveChecklistItem(ExerciseChecklistItem item) async {
    final db = await _localDatabase.database;
    final payload = <String, Object?>{
      'user_id': item.userId,
      'exercise_id': item.exerciseId,
      'is_checked': item.isChecked,
      'updated_at': _now(),
    };
    await db.transaction((txn) async {
      final values = <String, Object?>{
        'user_id': item.userId,
        'exercise_id': item.exerciseId,
        'is_checked': item.isChecked ? 1 : 0,
        'updated_at': _now(),
        'sync_status': 'pending',
      };
      await _upsert(txn, 'exercise_checklist', values,
          where: 'user_id = ? AND exercise_id = ?',
          whereArgs: [item.userId, item.exerciseId]);
      await _queue(
        txn,
        userId: item.userId,
        entityType: 'exercise_checklist',
        recordId: item.exerciseId,
        operation: 'upsert',
        payload: payload,
      );
    });
  }

  @override
  Future<List<ExerciseChecklistItem>> getChecklist(String userId) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'exercise_checklist',
      where: 'user_id = ?',
      whereArgs: [userId],
      orderBy: 'exercise_id ASC',
    );
    return rows.map(ExerciseChecklistItem.fromMap).toList(growable: false);
  }

  @override
  Future<void> saveSettings(UserSettings settings) async {
    final db = await _localDatabase.database;
    final payload = <String, Object?>{
      'user_id': settings.userId,
      'settings': settings.values,
      'updated_at': _now(),
    };
    await db.transaction((txn) async {
      final values = <String, Object?>{
        'user_id': settings.userId,
        'settings_json': jsonEncode(settings.values),
        'updated_at': _now(),
        'sync_status': 'pending',
      };
      await _upsert(txn, 'user_settings', values,
          where: 'user_id = ?', whereArgs: [settings.userId]);
      await _queue(
        txn,
        userId: settings.userId,
        entityType: 'user_settings',
        recordId: settings.userId,
        operation: 'upsert',
        payload: payload,
      );
    });
  }

  @override
  Future<UserSettings?> getSettings(String userId) async {
    final db = await _localDatabase.database;
    final rows = await db.query(
      'user_settings',
      where: 'user_id = ?',
      whereArgs: [userId],
      limit: 1,
    );
    return rows.isEmpty ? null : UserSettings.fromMap(rows.single);
  }
}
