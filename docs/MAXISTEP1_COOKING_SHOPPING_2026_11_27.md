# Cooking Anime — Maxi-step 1 implementation contract

- Product scope: guided cooking, structured shopping and restrained visual polish. All 162 recipe IDs, authoring, runtime locale packs, image files and review status remain untouched.
- Guided cooking: step-ID progress stored locally per recipe, in-app active-step timer using an absolute wall-clock deadline, pause/reset and resume after reopening. Timer completion is shown via foreground UI only. It is not a background notification or safety-critical alarm.
- During the cooking screen the app enables screen-on with `wakelock_plus` and releases it on exit/background. This screen-on lock does not keep the app executing in background.
- Shopping: import canonical ingredient quantities scaled to 1–99 servings into user-owned state, preserving recipe catalog. Aggregate only exact normalized localized ingredient labels and matching units when both quantities are numeric; manual/unknown quantities do not aggregate; no automatic unit conversion.
- Category: conservative classification using canonical Italian ingredient IDs, configurable individually, five groups. Legacy shopping JSON fields remain optional.
- Visual reference: Design-App/RXN animated circular progress bar, independently adapted to app colors and reduced-motion behavior; UIV-002 gradient pill retained as a future reference, not copied into a consumer without an app-specific need.
- Validation: source/catalog parity, Python tests, generated localizations in six languages, Flutter analyze/test, Web build, Android ARM64, emulator smoke on exact PR HEAD. Real device, store and payment signoff remain separate.
- Editorial translations and artwork #153/#155 are separate tickets and are explicitly excluded from this feature work.
