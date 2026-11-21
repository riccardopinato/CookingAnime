# Cooking Anime — Fast Track Wave 77 (21 November 2026)

## Scope and evidence boundary

This is an incremental source-bound editorial correction, **not** a blanket
semantic certification of 77 recipes or 385 translations. The 112 canonical
recipes 051–162 are reconciled with the merged PR #66 (29 recipe IDs) and
merged PR #67 (6 other recipe IDs). The 35 IDs are explicitly excluded in
`tool/fast_track_wave77_corrections.json`. The disjoint remaining scope is
77 IDs (51–162 minus those 35).

## Completed in this PR

- Inspect all 77 remaining IDs using IT source steps versus five runtime
  language packs and high-confidence lexical anomaly witnesses.
- Correct **66 specific preparation-step translations**, bound to the
  corresponding Italian source, in **28 distinct canonical recipes**.
- Distribution: EN **4**, ES **27**, FR **4**, DE **27**, PT **4**.
- Each touched recipe advances `contentVersion` exactly once.
- Preserve Italian source wording, titles, descriptions, anime references,
  ingredient IDs and quantities, methods and step IDs, timers, status,
  catalog version, user-owned state and artwork references.
- Update `assets/catalog/recipes.json` and five changed locale packages
  from the authoring records; Italian runtime package remains unchanged.
- Add a permanent mapping of the edited passages and a regression test
  checking all six locale packages for 28 touched records.

Representative source-bound repairs include Spanish `apuñala` for
"thread onto a skewer", German `springen` for "stir-fry", German
`im Badezimmer` for a bain-marie, and English `skip` for "stir-fry".

## Deliberately not claimed

- **49 of the 77** remain without a correction in this wave; absence of
  detected lexical warnings does not establish complete contextual accuracy.
- The **28 edited recipes** are source-parity checked but not independently
  AI-semantic certified across every instruction or professionally kitchen-tested.
- All translations outside the 66 edited step fields are unchanged, including
  any remaining linguistic or culinary deficiencies.
- No paid AI APIs, live source publishing, user-state migration, artwork update
  or production-store release is involved.

## Acceptance gates

```bash
python3 tool/compile_recipe_catalog.py --check
python3 -m unittest discover -s tool/tests -p 'test_fast_track_wave77.py' -v
python3 -m unittest discover -s tool/tests -p 'test_*.py'
python3 tool/validate_recipe_catalog.py
```

Normal exact-head Development, Semantic QA offline, inventory and R1 CI
should pass before merge. CI success is structural/tool evidence, not
independent culinary or language certification.
