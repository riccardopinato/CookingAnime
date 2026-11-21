# Cooking Anime — Final49 source-locked Fast Track (21 November 2026)

## Branch and scope

This tranche reconciles **all 49** recipe IDs remaining after PR #66
(29 canonical recipes), PR #67 (6), and PR #68 (28 further recipes).
The bounded source-of-truth list is the 77-ID scope in
`tool/fast_track_wave77_corrections.json` minus its 28 fixed IDs.

The five committed, immutable-review input documents are:

- `tool/final49/review_group_01.json` — IDs 51–77, 10 reviewed
- `tool/final49/review_group_02.json` — IDs 80–99, 10 reviewed
- `tool/final49/review_group_03.json` — IDs 101–119, 10 reviewed
- `tool/final49/review_group_04.json` — IDs 122–143, 10 reviewed
- `tool/final49/review_group_05.json` — IDs 145–161, 9 reviewed

The manifests hold source-bound editorial interventions, not machine-certified
evidence of translation accuracy for every untouched sentence.

## Outcomes

- **49 / 49 inventoried and reviewed** against Italian method and translated
  runtime packages.
- **46 / 49** canonical authoring records edited; the three **51, 56, 153**
  already had focused prior corrections and have **no new edit**.
- **463** localized instruction updates: **IT 5, EN 18, ES 116,
  FR 20, DE 184, PT 120**, plus **one English ingredient name**.
- Exactly one `contentVersion` bump for each of the 46 edited recipes;
  canonical recipe IDs, quantities, units, ingredient/step identities,
  timers, servings, difficulty, artwork and anime references remain unchanged.
- Generated `assets/catalog/recipes.json` plus **all six** locale assets
  synchronized to the modified canonical `authoring/recipes/*.json`.
- The permanent `test_fast_track_final49.py` regression suite validates
  all 49 × 6 source/runtime records and exact edits.

Representative material fixes:
- recipe 80: all five translations now agree with the Italian
  **cleaned/eviscerated Pacific saury** preparation rather than
  contradicting its safety instruction;
- recipe 84: chicken method now explicitly checks at least **74 °C**
  centre temperature in all six languages;
- recipe 110: five translations avoid instructing users to process
  **raw offal** when the Italian recipe explicitly requires
  cleaned and precooked offal;
- recipe 136: German method correctly applies the miso glaze to
  **tofu**, not aubergines;
- recipe 142: English, Spanish, French, German and Portuguese
  describe mixing until **no dry lumps remain**;
- recipe 101: erroneous German auto-translation of **onigiri**
  corrected, including a seriously inappropriate word;
- recipes 52, 59, 65, 68, 69, 74, 77, 87, 93, 95, 96, 113,
  125, 126, 140, 143, 152, 155 and 161: preparation verbs
  and objects reviewed and corrected directly against Italian.

## Evidence boundaries and remaining risk

This is a **source-locked semantic correction wave**, not proof of complete
professional culinary certification, all-text linguistic certification,
independent accuracy of anime appearances, or physical cook testing. The
offline CI Semantic QA job is structural/heuristic; its green result
must not be promoted to an independent LLM or chef review. Untouched
recipe fields and untranslated anomalies may still exist. The review
manifests distinguish reviewed records from records with actual edits.

The existing 162-recipe catalog is not renumbered, no user data or
database migration is involved, and no paid translation/AI API is used.

## Reproducibility and gates

```bash
python3 tool/compile_recipe_catalog.py --check
python3 -m unittest discover -s tool/tests -p 'test_fast_track_final49.py' -v
python3 -m unittest discover -s tool/tests -p 'test_*.py'
flutter analyze
flutter test
```

Require exact-head GitHub Development checks, offline Semantic QA,
Fast Track inventory and R1 checks to pass before merge.
