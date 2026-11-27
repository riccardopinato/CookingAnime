class CookingSession {
  const CookingSession({
    required this.stepId,
    this.completedStepIds = const [],
    this.timerStepId,
    this.remainingSeconds,
    this.deadlineEpochMs,
  });

  final String stepId;
  final List<String> completedStepIds;
  final String? timerStepId;
  final int? remainingSeconds;
  final int? deadlineEpochMs;

  int? remainingAt(int nowEpochMs) {
    final remaining = remainingSeconds;
    if (remaining == null) return null;
    if (deadlineEpochMs == null) return remaining;
    final left = ((deadlineEpochMs! - nowEpochMs) / 1000).ceil();
    return left.clamp(0, remaining).toInt();
  }

  Map<String, dynamic> toJson() => {
    'stepId': stepId,
    'completedStepIds': completedStepIds,
    if (timerStepId != null) 'timerStepId': timerStepId,
    if (remainingSeconds != null) 'remainingSeconds': remainingSeconds,
    if (deadlineEpochMs != null) 'deadlineEpochMs': deadlineEpochMs,
  };

  factory CookingSession.fromJson(Map<String, dynamic> json) {
    final completed = json['completedStepIds'];
    return CookingSession(
      stepId: json['stepId'] is String ? json['stepId'] as String : '',
      completedStepIds: completed is List
          ? completed.whereType<String>().toList(growable: false)
          : const [],
      timerStepId: json['timerStepId'] as String?,
      remainingSeconds: (json['remainingSeconds'] as num?)?.toInt(),
      deadlineEpochMs: (json['deadlineEpochMs'] as num?)?.toInt(),
    );
  }
}
