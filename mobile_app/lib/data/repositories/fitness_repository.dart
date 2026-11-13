import 'fitness_models.dart';

abstract interface class FitnessRepository {
  Future<void> saveProfile(FitnessProfile profile);
  Future<FitnessProfile?> getProfile(String userId);

  Future<void> saveWorkout(WorkoutLog workout);
  Future<List<WorkoutLog>> getWorkoutLogs(String userId);
  Future<void> deleteWorkout(String userId, String recordId);

  Future<void> saveBodyStat(BodyStat bodyStat);
  Future<List<BodyStat>> getBodyStats(String userId);
  Future<void> deleteBodyStat(String userId, String recordId);

  Future<void> saveWeeklyTracker(WeeklyTracker tracker);
  Future<WeeklyTracker?> getWeeklyTracker(String userId, DateTime weekStart);

  Future<void> saveChecklistItem(ExerciseChecklistItem item);
  Future<List<ExerciseChecklistItem>> getChecklist(String userId);

  Future<void> saveSettings(UserSettings settings);
  Future<UserSettings?> getSettings(String userId);
}
