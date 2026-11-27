import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../../../../core/theme/app_design_tokens.dart';
import '../../../../l10n/app_localizations.dart';
import '../../domain/cooking_session.dart';
import '../../domain/recipe.dart';

/// Guided, offline-only recipe view. Timers use absolute deadlines so
/// returning from background never silently extends a cooking duration.
/// No system alarms or background notifications are promised by this screen.
class CookingModeScreen extends StatefulWidget {
  const CookingModeScreen({super.key, required this.recipe});
  final Recipe recipe;

  @override
  State<CookingModeScreen> createState() => _CookingModeScreenState();
}

class _CookingModeScreenState extends State<CookingModeScreen>
    with WidgetsBindingObserver {
  SharedPreferences? _prefs;
  String? _currentStepId;
  final Set<String> _completed = {};
  String? _timerStepId;
  int? _remainingSeconds;
  int? _deadlineEpochMs;
  Timer? _ticker;
  bool _ready = false;
  bool _timerNoticeShown = false;

  String get _storageKey => 'cooking_progress_v1_${widget.recipe.id}';
  int get _now => DateTime.now().millisecondsSinceEpoch;
  int get _stepIndex {
    final index = widget.recipe.steps.indexWhere((s) => s.id == _currentStepId);
    return index < 0 ? 0 : index;
  }

  int? get _effectiveRemaining {
    final remaining = _remainingSeconds;
    if (remaining == null) return null;
    if (_deadlineEpochMs == null) return remaining;
    return ((_deadlineEpochMs! - _now) / 1000).ceil().clamp(0, remaining);
  }

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    _currentStepId = widget.recipe.steps.first.id;
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    if (!mounted) return;
    final saved = prefs.getString(_storageKey);
    CookingSession? session;
    if (saved != null) {
      try {
        final decoded = jsonDecode(saved);
        if (decoded is Map<String, dynamic>) {
          session = CookingSession.fromJson(decoded);
        }
      } on FormatException {
        // Ignore invalid local state; never mutate recipe content.
      } on TypeError {
        // Previous/corrupt state cannot crash cooking navigation.
      }
    }
    final validIds = widget.recipe.steps.map((s) => s.id).toSet();
    setState(() {
      _prefs = prefs;
      if (session != null) {
        if (validIds.contains(session.stepId)) {
          _currentStepId = session.stepId;
        }
        _completed
          ..clear()
          ..addAll(session.completedStepIds.where(validIds.contains));
        if (validIds.contains(session.timerStepId) &&
            session.remainingSeconds != null &&
            session.remainingSeconds! >= 0) {
          _timerStepId = session.timerStepId;
          _remainingSeconds = session.remainingSeconds;
          _deadlineEpochMs = session.deadlineEpochMs;
        }
      }
      _ready = true;
    });
    _armTicker();
  }

  void _save() {
    final prefs = _prefs;
    if (prefs == null) return;
    final payload = CookingSession(
      stepId: _currentStepId ?? widget.recipe.steps.first.id,
      completedStepIds: _completed.toList(growable: false),
      timerStepId: _timerStepId,
      remainingSeconds: _effectiveRemaining,
      deadlineEpochMs: _deadlineEpochMs,
    );
    unawaited(prefs.setString(_storageKey, jsonEncode(payload.toJson())));
  }

  void _armTicker() {
    _ticker?.cancel();
    if (_deadlineEpochMs == null) return;
    _tick();
    if (_deadlineEpochMs != null) {
      _ticker = Timer.periodic(const Duration(seconds: 1), (_) => _tick());
    }
  }

  void _tick() {
    if (!mounted) return;
    final remaining = _effectiveRemaining;
    setState(() {});
    if (remaining == 0) {
      _ticker?.cancel();
      _deadlineEpochMs = null;
      _remainingSeconds = 0;
      _save();
      if (!_timerNoticeShown) {
        _timerNoticeShown = true;
        final l10n = AppLocalizations.of(context)!;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(l10n.timerDoneBody)),
        );
      }
    }
  }

  void _setStep(int index) {
    if (index < 0 || index >= widget.recipe.steps.length) return;
    setState(() => _currentStepId = widget.recipe.steps[index].id);
    _save();
  }

  void _toggleCompleted() {
    final id = widget.recipe.steps[_stepIndex].id;
    setState(() {
      if (!_completed.remove(id)) _completed.add(id);
    });
    _save();
  }

  void _startTimer(RecipeStep step) {
    final duration = step.timerSeconds;
    if (duration == null || duration <= 0) return;
    final remaining = _timerStepId == step.id
        ? (_effectiveRemaining ?? duration)
        : duration;
    if (_timerStepId != null &&
        _timerStepId != step.id &&
        (_effectiveRemaining ?? 0) > 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(AppLocalizations.of(context)!.cookingTimerAlreadyRunning)),
      );
      return;
    }
    setState(() {
      _timerStepId = step.id;
      _remainingSeconds = remaining;
      _deadlineEpochMs = _now + remaining * 1000;
      _timerNoticeShown = false;
    });
    _save();
    _armTicker();
  }

  void _pauseTimer() {
    final remaining = _effectiveRemaining;
    _ticker?.cancel();
    setState(() {
      _remainingSeconds = remaining;
      _deadlineEpochMs = null;
    });
    _save();
  }

  void _resetTimer() {
    _ticker?.cancel();
    setState(() {
      _timerStepId = null;
      _remainingSeconds = null;
      _deadlineEpochMs = null;
      _timerNoticeShown = false;
    });
    _save();
  }

  Future<void> _resetProgress() async {
    setState(() {
      _completed.clear();
      _currentStepId = widget.recipe.steps.first.id;
    });
    _resetTimer();
    _save();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed && mounted) _tick();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _ticker?.cancel();
    _save();
    super.dispose();
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final rest = seconds % 60;
    return '${minutes.toString().padLeft(2, '0')}:${rest.toString().padLeft(2, '0')}';
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final theme = Theme.of(context);
    final colors = theme.colorScheme;
    final steps = widget.recipe.steps;
    final index = _stepIndex;
    final step = steps[index];
    final progress = _completed.length / steps.length;
    final reduceMotion = MediaQuery.maybeOf(context)?.disableAnimations ?? false;
    final activeStepIndex = steps.indexWhere((s) => s.id == _timerStepId);
    final remaining = _effectiveRemaining;

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.cookingModeLaunch),
        actions: [
          IconButton(
            tooltip: l10n.cookingResetProgress,
            onPressed: _ready ? _resetProgress : null,
            icon: const Icon(Icons.restart_alt_rounded),
          ),
        ],
      ),
      body: !_ready
          ? const Center(child: CircularProgressIndicator())
          : Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 760),
                child: ListView(
                  padding: const EdgeInsets.fromLTRB(20, 12, 20, 40),
                  children: [
                    Text(widget.recipe.title,
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.w800)),
                    const SizedBox(height: AppSpacing.large),
                    Container(
                      padding: const EdgeInsets.all(AppSpacing.medium),
                      decoration: BoxDecoration(
                        color: colors.primaryContainer.withValues(alpha: .44),
                        borderRadius: BorderRadius.circular(AppRadii.container),
                      ),
                      child: Row(
                        children: [
                          Semantics(
                            label: l10n.cookingProgressLabel,
                            value: '${_completed.length}/${steps.length}',
                            child: SizedBox.square(
                              dimension: 72,
                              // Design-App reference: RXN animated circular progress,
                              // adapted to app tokens and reduced-motion behavior.
                              child: TweenAnimationBuilder<double>(
                                tween: Tween<double>(end: progress),
                                duration: reduceMotion ? Duration.zero : AppMotion.standard,
                                builder: (context, value, _) => Stack(
                                  alignment: Alignment.center,
                                  children: [
                                    CircularProgressIndicator(
                                      value: value,
                                      strokeWidth: 7,
                                      strokeCap: StrokeCap.round,
                                      backgroundColor: colors.surface,
                                    ),
                                    Text('${(value * 100).round()}%',
                                      style: theme.textTheme.labelLarge),
                                  ],
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(width: AppSpacing.medium),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(l10n.cookingProgressLabel,
                                  style: theme.textTheme.titleMedium),
                                Text('${_completed.length} / ${steps.length}',
                                  style: theme.textTheme.bodyLarge),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: AppSpacing.large),
                    Container(
                      padding: const EdgeInsets.all(AppSpacing.large),
                      decoration: BoxDecoration(
                        color: colors.surfaceContainerLow,
                        borderRadius: BorderRadius.circular(AppRadii.hero),
                        border: Border.all(color: colors.outlineVariant),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('${l10n.cookingStepLabel} ${index + 1} / ${steps.length}',
                            style: theme.textTheme.labelLarge?.copyWith(
                              color: colors.primary, fontWeight: FontWeight.w800)),
                          const SizedBox(height: AppSpacing.large),
                          SelectableText(step.text,
                            style: theme.textTheme.headlineSmall?.copyWith(
                              fontSize: 24, height: 1.45)),
                          const SizedBox(height: AppSpacing.large),
                          FilledButton.tonalIcon(
                            onPressed: _toggleCompleted,
                            icon: Icon(_completed.contains(step.id)
                                ? Icons.check_circle_rounded
                                : Icons.radio_button_unchecked_rounded),
                            label: Text(_completed.contains(step.id)
                                ? l10n.cookingMarkedDone
                                : l10n.cookingMarkDone),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: AppSpacing.medium),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: index == 0 ? null : () => _setStep(index - 1),
                            icon: const Icon(Icons.chevron_left_rounded),
                            label: Text(l10n.cookingPrevious),
                          ),
                        ),
                        const SizedBox(width: AppSpacing.small),
                        Expanded(
                          child: FilledButton.icon(
                            onPressed: index == steps.length - 1
                                ? null : () => _setStep(index + 1),
                            icon: const Icon(Icons.chevron_right_rounded),
                            label: Text(l10n.cookingNext),
                          ),
                        ),
                      ],
                    ),
                    if (step.timerSeconds != null && step.timerSeconds! > 0 ||
                        _timerStepId != null) ...[
                      const SizedBox(height: AppSpacing.large),
                      Container(
                        padding: const EdgeInsets.all(AppSpacing.medium),
                        decoration: BoxDecoration(
                          color: colors.secondaryContainer.withValues(alpha: .40),
                          borderRadius: BorderRadius.circular(AppRadii.container),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(l10n.timerTitle, style: theme.textTheme.titleMedium),
                            if (activeStepIndex >= 0)
                              Text('${l10n.cookingStepLabel} ${activeStepIndex + 1}'),
                            Text(_formatTime(
                                remaining ?? step.timerSeconds ?? 0),
                              style: theme.textTheme.displayMedium?.copyWith(
                                fontWeight: FontWeight.w800)),
                            Wrap(
                              spacing: 8,
                              children: [
                                FilledButton.tonalIcon(
                                  onPressed: step.timerSeconds == null || step.timerSeconds! <= 0
                                      ? null
                                      : () => _startTimer(step),
                                  icon: const Icon(Icons.play_arrow_rounded),
                                  label: Text(l10n.timerStart),
                                ),
                                OutlinedButton.icon(
                                  onPressed: _deadlineEpochMs == null ? null : _pauseTimer,
                                  icon: const Icon(Icons.pause_rounded),
                                  label: Text(l10n.timerPause),
                                ),
                                TextButton.icon(
                                  onPressed: _timerStepId == null ? null : _resetTimer,
                                  icon: const Icon(Icons.refresh_rounded),
                                  label: Text(l10n.timerReset),
                                ),
                              ],
                            ),
                            Text(l10n.cookingTimerForegroundNotice,
                              style: theme.textTheme.bodySmall?.copyWith(
                                color: colors.onSurfaceVariant)),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: AppSpacing.large),
                    ExpansionTile(
                      title: Text(l10n.ingredientsTitle),
                      children: [
                        for (final ingredient in widget.recipe.ingredients)
                          ListTile(title: Text(ingredient.displayText)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
