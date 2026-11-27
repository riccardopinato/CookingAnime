import 'package:flutter_test/flutter_test.dart';
import 'package:animekitchen/features/recipes/domain/cooking_session.dart';

void main() {
  test('session persists stable step IDs and completed state', () {
    const session = CookingSession(
      stepId: 'wash_rice', completedStepIds: ['wash_rice'],
      timerStepId: 'boil', remainingSeconds: 180, deadlineEpochMs: 200000,
    );
    final decoded = CookingSession.fromJson(session.toJson());
    expect(decoded.stepId, 'wash_rice');
    expect(decoded.completedStepIds, ['wash_rice']);
    expect(decoded.timerStepId, 'boil');
    expect(decoded.remainingAt(50000), 150);
    expect(decoded.remainingAt(210000), 0);
  });

  test('paused timers retain the remaining seconds', () {
    const session = CookingSession(
      stepId: 'one', remainingSeconds: 42, timerStepId: 'one',
    );
    expect(session.remainingAt(90000000), 42);
  });

  test('historic/corrupt progress never invents steps', () {
    final session = CookingSession.fromJson({
      'stepId': '', 'completedStepIds': ['step_1', 42, null],
    });
    expect(session.completedStepIds, ['step_1']);
    expect(session.remainingAt(0), isNull);
  });
}
