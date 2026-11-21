import 'dart:async';

import 'package:flutter/material.dart';

import '../../../../core/theme/app_design_tokens.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/countdown_remaining.dart';

class CookingTimerWidget extends StatefulWidget {
  const CookingTimerWidget({
    super.key,
    required this.minutes,
  });

  final int minutes;

  @override
  State<CookingTimerWidget> createState() => _CookingTimerWidgetState();
}

class _CookingTimerWidgetState extends State<CookingTimerWidget>
    with SingleTickerProviderStateMixin, WidgetsBindingObserver {
  Timer? _timer;
  final Stopwatch _intervalClock = Stopwatch();
  late int _remainingAtStart;
  late int _totalSeconds;
  late int _remainingSeconds;
  late final AnimationController _pulseController;
  bool _running = false;
  bool _finishing = false;

  bool get _reduceMotion =>
      MediaQuery.maybeOf(context)?.disableAnimations ?? false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _resetValues();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 950),
    );
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncPulse();
  }

  @override
  void didUpdateWidget(covariant CookingTimerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.minutes != widget.minutes) {
      _timer?.cancel();
      _resetValues();
      _syncPulse();
    }
  }

  void _resetValues() {
    _intervalClock
      ..stop()
      ..reset();
    _totalSeconds = widget.minutes * 60;
    _remainingAtStart = _totalSeconds;
    _remainingSeconds = _totalSeconds;
    _running = false;
    _finishing = false;
  }

  void _syncPulse() {
    if (_reduceMotion || !_running) {
      _pulseController
        ..stop()
        ..value = 0;
      return;
    }

    if (!_pulseController.isAnimating) {
      _pulseController.repeat(reverse: true);
    }
  }

  void _start() {
    if (_remainingSeconds <= 0 || _running) return;
    _remainingAtStart = _remainingSeconds;
    _intervalClock
      ..reset()
      ..start();
    setState(() => _running = true);
    _syncPulse();
    // UI callbacks may stop in Android background. Elapsed time is monotonic.
    _timer = Timer.periodic(const Duration(milliseconds: 250), (_) => _refresh());
  }

  void _refresh() {
    if (!mounted || !_running) return;
    final remaining = remainingAfterElapsed(
      secondsAtStart: _remainingAtStart,
      elapsed: _intervalClock.elapsed,
    );
    if (remaining == _remainingSeconds) return;
    if (remaining == 0) {
      _timer?.cancel();
      _intervalClock.stop();
      setState(() {
        _remainingSeconds = 0;
        _running = false;
      });
      _syncPulse();
      unawaited(_finishTimer());
      return;
    }
    setState(() => _remainingSeconds = remaining);
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) _refresh();
  }

  void _pause() {
    _refresh();
    _timer?.cancel();
    _intervalClock.stop();
    if (_running) setState(() => _running = false);
    _syncPulse();
  }

  void _reset() {
    _timer?.cancel();
    setState(_resetValues);
    _syncPulse();
  }

  Future<void> _finishTimer() async {
    _pulseController.stop();

    if (!_reduceMotion && mounted) {
      setState(() => _finishing = true);
      _pulseController.value = 0;
      await _pulseController.animateTo(
        1,
        duration: const Duration(milliseconds: 160),
        curve: Curves.easeOutBack,
      );
      await _pulseController.animateBack(
        0,
        duration: const Duration(milliseconds: 180),
        curve: Curves.easeInOutCubic,
      );
      if (mounted) {
        setState(() => _finishing = false);
      }
    } else {
      _pulseController.value = 0;
    }

    if (mounted) {
      await _showFinishedDialog();
    }
  }

  Future<void> _showFinishedDialog() async {
    final l10n = AppLocalizations.of(context)!;
    await showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: Text(l10n.timerDoneTitle),
        content: Text(l10n.timerDoneBody),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(),
            child: Text(MaterialLocalizations.of(dialogContext).okButtonLabel),
          ),
        ],
      ),
    );
  }

  String get _formattedTime {
    final minutes = _remainingSeconds ~/ 60;
    final seconds = _remainingSeconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:'
        '${seconds.toString().padLeft(2, '0')}';
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _timer?.cancel();
    _intervalClock.stop();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final progress = _totalSeconds == 0
        ? 0.0
        : _remainingSeconds / _totalSeconds;
    final reduceMotion = _reduceMotion;

    return Container(
      padding: const EdgeInsets.all(AppSpacing.large),
      decoration: BoxDecoration(
        color: colors.primary.withValues(alpha: 0.09),
        borderRadius: BorderRadius.circular(AppRadii.container),
        border: Border.all(
          color: colors.primary.withValues(alpha: 0.18),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: colors.primary.withValues(alpha: 0.13),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: AnimatedBuilder(
                  animation: _pulseController,
                  child: Icon(
                    Icons.timer_outlined,
                    color: colors.primary,
                  ),
                  builder: (context, child) {
                    if (reduceMotion) {
                      return child!;
                    }
                    final amplitude = _finishing ? 0.14 : 0.045;
                    return Transform.scale(
                      scale: 1 + (_pulseController.value * amplitude),
                      child: child,
                    );
                  },
                ),
              ),
              const SizedBox(width: AppSpacing.small),
              Expanded(
                child: Text(
                  l10n.timerTitle,
                  style: theme.textTheme.titleLarge,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppSpacing.large),
          Text(
            _formattedTime,
            style: theme.textTheme.displayMedium?.copyWith(
              fontFamily: null,
              fontWeight: FontWeight.w800,
              color: colors.onSurface,
            ),
          ),
          const SizedBox(height: AppSpacing.medium),
          ClipRRect(
            borderRadius: BorderRadius.circular(AppRadii.pill),
            child: TweenAnimationBuilder<double>(
              tween: Tween<double>(begin: 0, end: progress),
              duration: reduceMotion
                  ? Duration.zero
                  : const Duration(milliseconds: 360),
              curve: Curves.easeOutCubic,
              builder: (context, value, _) {
                return LinearProgressIndicator(
                  value: value,
                  minHeight: 9,
                  backgroundColor:
                      colors.surface.withValues(alpha: 0.72),
                  color: colors.primary,
                );
              },
            ),
          ),
          const SizedBox(height: AppSpacing.large),
          Wrap(
            spacing: AppSpacing.small,
            runSpacing: AppSpacing.small,
            children: [
              FilledButton.icon(
                onPressed: _running ? null : _start,
                icon: const Icon(Icons.play_arrow_rounded),
                label: Text(l10n.timerStart),
              ),
              OutlinedButton.icon(
                onPressed: _running ? _pause : null,
                icon: const Icon(Icons.pause_rounded),
                label: Text(l10n.timerPause),
              ),
              TextButton.icon(
                onPressed: _reset,
                icon: const Icon(Icons.refresh_rounded),
                label: Text(l10n.timerReset),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
