# Timer QA checkpoint — Cooking Anime (2026-11-21)

Replaced the aggregate cooking timer's count-of-periodic-callbacks with
a monotonic `Stopwatch` based elapsed-time calculation. `WidgetsBindingObserver`
refreshes the remaining seconds on resume; pause stores precise remaining
seconds, reset cancels running state. A pure calculation has deterministic tests.

**Limits:** timer still lives only while the Flutter process survives and the
detail page remains mounted. It does **not** schedule system notifications,
persist across process termination, start each recipe-step timer, or qualify as
an Android system alarm. Hardware acceptance (screen off / background / resume)
is still required and is separate from Flutter tests.
