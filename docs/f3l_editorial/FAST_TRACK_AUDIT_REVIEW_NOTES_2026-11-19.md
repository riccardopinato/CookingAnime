# Cooking Anime — Fast Track: 162 ricette, 6 lingue, audit e correzioni

**Data:** 2026-11-19. **Perimetro canonico:** `recipe_000001`–`recipe_000162`. **Lingue:** IT, EN, ES, FR, DE, PT (972 record localizzati). **Nuove ricette:** 0.

## Reconciliations
- Previous PR #57: 96 complete source-locked recipe methods promoted to runtime.
- Previous PR #58: 4 additional dishes with raw-food and pasteurization safeguards.
- PR #59: all 12 remaining risk-specific HOLD corrected, detailed locale methods materialized and merged on `main`. Zero outstanding inventory HOLD from the original 112 backlog.
- This PR: cross-catalog scan of ALL 162 IDs and six locale records, with inspectable before/after results in `docs/f3l_editorial/FAST_TRACK_162_CATALOG_AUDIT.json`. It corrected **153 text fields across 55 distinct recipe IDs**, including all five translated procedures for Chirashizushi (#56) and Tori Tsukune (#153), plus observed source-specific false friends.

## Scope of audit
The deterministic scanner reads all 162 authoring recipe files, all six locale records for every recipe, their editorial copy, ingredient labels, step instructions, canonical identifiers, units, timer alignment and known filler/false-friend patterns. It counts *only* proven structural/lexical anomalies and preserves per-ID evidence. Artwork-related recipes `000001`–`000050` are scanned but their content is NOT auto-mutated because changing `contentVersion` would invalidate artwork semantic-review seals.

The witnessed heuristic count moved **51 → 0** after repairs, with additional separate false-friend sampling performed in follow-up passes. An empty set of witnessed errors is **NOT a full natural-language, semantic or culinary certification**. In particular, a recipe can be grammatical but mistranslate a specific technique; external bilingual scrutiny of every sentence has not been asserted. No fabricated professional reviewer signatures.

## Safety checks
Twelve historically held recipes require the six-language, source-bound safety guidance in `tool/fast_track_12_repairs.py`; the new audit verifies those excerpts remain present. Guidance sources:
- Poultry/duck 74 °C: https://ask.fsis.usda.gov/article/What-is-a-safe-internal-temperature-for-cooking-meat-and-poultry
- Shellfish and fish sourcing: https://www.fda.gov/food/buy-store-serve-safe-food/selecting-and-serving-fresh-and-frozen-seafood-safely
- Pasteurized eggs: https://www.fda.gov/food/retail-food-industryregulatory-assistance-training/assuring-safety-eggs-and-menu-and-deli-items-made-raw-shell-eggs
- Cooked rice quick chilling: https://www.gov.uk/government/publications/home-food-fact-checker/home-food-fact-checker
- Sanma as *Cololabis saira*: https://fish-commercial-names.ec.europa.eu/fish-names/species/cololabis-saira_es

## Technical acceptance
- Source/compiled runtime must be synchronized: `python3 tool/compile_recipe_catalog.py --check`.
- Validate runtime schema and deduplication: `python3 tool/validate_recipe_catalog.py`.
- Flutter analyze/test, Web release and Android ARM64 build are gated separately by the repository's PR CI; no green claim until exact-head checks succeed.
- On merge, verify latest `main` and distinguish structural coverage from semantic correctness.
