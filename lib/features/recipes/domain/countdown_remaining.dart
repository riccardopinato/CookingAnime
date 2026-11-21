/// Computes remaining seconds from elapsed monotonic time rather than tick count.
/// When the OS suspends callbacks in background, time still elapses.
int remainingAfterElapsed({
  required int secondsAtStart,
  required Duration elapsed,
}) {
  if (secondsAtStart <= 0) return 0;
  final ms = secondsAtStart * 1000 - elapsed.inMilliseconds;
  return ms <= 0 ? 0 : (ms + 999) ~/ 1000;
}
