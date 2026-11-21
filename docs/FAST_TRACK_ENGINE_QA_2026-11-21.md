# Cooking Anime — Fast Track evidence hardening (2026-11-21)

Pinned shared authoring engines at App-Factory-Core d90c274cd33a9e727e070aa9fa45a506c2ae13c5.
Language Engine 1.1 recognizes safe written cardinals and C/F equivalents,
separates unit mismatches, rejects stale drafts and checks that an imported
Semantic QA report covers the exact same source data SHA256 and all 810 pairs.

The Cooking Anime CI performs a fail-closed cross-check after both engines run:
same input fingerprint, 162 canonical recipes, 810 translation pairs, zero
provider calls from Language Engine, and NOT_CERTIFIED editorial status.

The local structural scanner now emits its own deterministic fingerprint from
canonical authoring files, generated locale/runtime packs and six UI ARB files.
It still reports numeric differences and suspicious step timers for human
review. Its tests no longer freeze the UI translation-key count to 73, so adding
valid new localized UI strings does not make the checker itself stale.

No source recipe text, quantity, imagery, app behavior or external API changed.
Full linguistic and professional culinary sign-off remain distinct from runtime
emulator / build / publication gates.
