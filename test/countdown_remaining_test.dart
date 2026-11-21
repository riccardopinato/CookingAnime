import 'package:flutter_test/flutter_test.dart';
import 'package:animekitchen/features/recipes/domain/countdown_remaining.dart';

void main() {
  test('elapsed time survives a long gap between UI callbacks', () {
    expect(remainingAfterElapsed(secondsAtStart: 120, elapsed: Duration.zero), 120);
    expect(remainingAfterElapsed(secondsAtStart: 120, elapsed: const Duration(milliseconds: 1001)), 119);
    expect(remainingAfterElapsed(secondsAtStart: 120, elapsed: const Duration(seconds: 90)), 30);
    expect(remainingAfterElapsed(secondsAtStart: 120, elapsed: const Duration(seconds: 200)), 0);
  });
  test('countdown clamps to zero and rounds subsecond progress upward', () {
    expect(remainingAfterElapsed(secondsAtStart: -2, elapsed: Duration.zero), 0);
    expect(remainingAfterElapsed(secondsAtStart: 2, elapsed: const Duration(milliseconds: 1999)), 1);
    expect(remainingAfterElapsed(secondsAtStart: 2, elapsed: const Duration(seconds: 2)), 0);
  });
}
