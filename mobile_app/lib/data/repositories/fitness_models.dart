import 'dart:convert';

class FitnessProfile {
  const FitnessProfile({
    required this.userId,
    required this.displayName,
    this.heightCm,
    this.currentWeightKg,
    this.goalWeightKg,
    required this.createdAt,
    required this.updatedAt,
  });

  final String userId;
  final String displayName;
  final double? heightCm;
  final double? currentWeightKg;
  final double? goalWeightKg;
  final DateTime createdAt;
  final DateTime updatedAt;

  factory FitnessProfile.fromMap(Map<String, Object?> map) => FitnessProfile(
        userId: map['user_id']! as String,
        displayName: map['display_name']! as String,
        heightCm: (map['height_cm'] as num?)?.toDouble(),
        currentWeightKg: (map['current_weight_kg'] as num?)?.toDouble(),
        goalWeightKg: (map['goal_weight_kg'] as num?)?.toDouble(),
        createdAt: DateTime.parse(map['created_at']! as String),
        updatedAt: DateTime.parse(map['updated_at']! as String),
      );
}

class WorkoutSet {
  const WorkoutSet({required this.weightKg, required this.reps});

  final double weightKg;
  final int reps;

  Map<String, num> toMap() => {'weight_kg': weightKg, 'reps': reps};

  factory WorkoutSet.fromMap(Map<String, dynamic> map) => WorkoutSet(
        weightKg: (map['weight_kg'] as num).toDouble(),
        reps: (map['reps'] as num).toInt(),
      );
}

class WorkoutLog {
  const WorkoutLog({
    required this.recordId,
    required this.userId,
    required this.workoutDate,
    required this.muscleGroup,
    required this.exerciseName,
    required this.sets,
    this.notes = '',
    required this.createdAt,
    required this.updatedAt,
    this.syncStatus = 'pending',
  });

  final String recordId;
  final String userId;
  final DateTime workoutDate;
  final String muscleGroup;
  final String exerciseName;
  final List<WorkoutSet> sets;
  final String notes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String syncStatus;

  factory WorkoutLog.fromMap(Map<String, Object?> map) {
    final rawSets = jsonDecode(map['sets_json']! as String) as List<dynamic>;
    return WorkoutLog(
      recordId: map['record_id']! as String,
      userId: map['user_id']! as String,
      workoutDate: DateTime.parse(map['workout_date']! as String),
      muscleGroup: map['muscle_group']! as String,
      exerciseName: map['exercise_name']! as String,
      sets: rawSets
          .map((item) => WorkoutSet.fromMap(item as Map<String, dynamic>))
          .toList(growable: false),
      notes: map['notes'] as String? ?? '',
      createdAt: DateTime.parse(map['created_at']! as String),
      updatedAt: DateTime.parse(map['updated_at']! as String),
      syncStatus: map['sync_status'] as String? ?? 'pending',
    );
  }
}

class BodyStat {
  const BodyStat({
    required this.recordId,
    required this.userId,
    required this.measuredAt,
    required this.weightKg,
    required this.heightCm,
    this.notes = '',
    required this.createdAt,
    required this.updatedAt,
    this.syncStatus = 'pending',
  });

  final String recordId;
  final String userId;
  final DateTime measuredAt;
  final double weightKg;
  final double heightCm;
  final String notes;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String syncStatus;

  factory BodyStat.fromMap(Map<String, Object?> map) => BodyStat(
        recordId: map['record_id']! as String,
        userId: map['user_id']! as String,
        measuredAt: DateTime.parse(map['measured_at']! as String),
        weightKg: (map['weight_kg']! as num).toDouble(),
        heightCm: (map['height_cm']! as num).toDouble(),
        notes: map['notes'] as String? ?? '',
        createdAt: DateTime.parse(map['created_at']! as String),
        updatedAt: DateTime.parse(map['updated_at']! as String),
        syncStatus: map['sync_status'] as String? ?? 'pending',
      );
}

class WeeklyTracker {
  const WeeklyTracker({
    required this.recordId,
    required this.userId,
    required this.weekStart,
    required this.targetDays,
    required this.completedDays,
    required this.updatedAt,
    this.syncStatus = 'pending',
  });

  final String recordId;
  final String userId;
  final DateTime weekStart;
  final int targetDays;
  final List<int> completedDays;
  final DateTime updatedAt;
  final String syncStatus;

  factory WeeklyTracker.fromMap(Map<String, Object?> map) =>
      WeeklyTracker(
        recordId: map['record_id']! as String,
        userId: map['user_id']! as String,
        weekStart: DateTime.parse(map['week_start']! as String),
        targetDays: map['target_days']! as int,
        completedDays: (jsonDecode(
          map['completed_days_json']! as String,
        ) as List<dynamic>).cast<int>(),
        updatedAt: DateTime.parse(map['updated_at']! as String),
        syncStatus: map['sync_status'] as String? ?? 'pending',
      );
}

class ExerciseChecklistItem {
  const ExerciseChecklistItem({
    required this.userId,
    required this.exerciseId,
    required this.isChecked,
    required this.updatedAt,
    this.syncStatus = 'pending',
  });

  final String userId;
  final String exerciseId;
  final bool isChecked;
  final DateTime updatedAt;
  final String syncStatus;

  factory ExerciseChecklistItem.fromMap(Map<String, Object?> map) =>
      ExerciseChecklistItem(
        userId: map['user_id']! as String,
        exerciseId: map['exercise_id']! as String,
        isChecked: (map['is_checked']! as int) == 1,
        updatedAt: DateTime.parse(map['updated_at']! as String),
        syncStatus: map['sync_status'] as String? ?? 'pending',
      );
}

class UserSettings {
  const UserSettings({
    required this.userId,
    required this.values,
    required this.updatedAt,
    this.syncStatus = 'pending',
  });

  final String userId;
  final Map<String, Object?> values;
  final DateTime updatedAt;
  final String syncStatus;

  factory UserSettings.fromMap(Map<String, Object?> map) => UserSettings(
        userId: map['user_id']! as String,
        values: (jsonDecode(map['settings_json']! as String)
                as Map<String, dynamic>)
            .cast<String, Object?>(),
        updatedAt: DateTime.parse(map['updated_at']! as String),
        syncStatus: map['sync_status'] as String? ?? 'pending',
      );
}
