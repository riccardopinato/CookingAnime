# CookingAnime — Artwork Style Guide v1

**Canonical for new and replacement artwork; adopted 2026-11-27.** The visual source of truth is the *actual* approved JPEG corpus `assets/recipe_artwork/recipe_000001.jpg` through `recipe_000050.jpg`. A prompt or an example from elsewhere does not outrank these files.

## Visual identity

- **Food first:** one recognizable completed recipe, filling most of the picture, understandable in a small app card.
- **Hand-painted 2D anime food illustration:** clear drawn edges, controlled cel shading and simplified but convincing ingredient shapes. No photoreal photography, smooth 3D surfaces, plastic-like sauce, excessive specular glare or extreme depth-of-field.
- **Warm, natural illumination:** appetizing late-afternoon/kitchen light, plausible cast shadows, controlled saturation and highlights. No blanket orange filter.
- **Restrained settings:** illustrated table, café or kitchen can support the dish, but avoid elaborate photographic interiors, landscapes and repeated identical bowls. Proportions and food identity dominate scenery.
- **Specific food texture:** crisp coatings, rice grains, noodle thickness and broth clarity as required by the canonical recipe; not arbitrary toppings.
- **Variation:** distinct dish, camera position and vessel per recipe. Neither one standard bowl nor an exact duplicate of a reference frame is allowed.
- **Originality:** do not copy characters, stills, logos or identifiable modern anime franchises.

## Reference anchors within the first 50

| File | Focus |
| --- | --- |
| `recipe_000005.jpg` | clearly drawn rice and minimal environment |
| `recipe_000020.jpg` | expressive, simple cel-shaded confectionery |
| `recipe_000025.jpg` | separate readable noodle/ingredient groups |
| `recipe_000035.jpg` | simplified outlines and restrained background |
| `recipe_000045.jpg` | crisp illustrated frying texture |
| `recipe_000050.jpg` | richer dessert scene within anime illustration vocabulary |

These examples bound a *range*, not one uniform density: the original 1–50 also contain more detailed drawings (e.g. 002, 029, 050). Reference at least three source JPEGs relevant to each dish.

## Required workflow and acceptance

1. Read `authoring/recipes/recipe_NNNNNN.json`, preferably the original Italian `locales.it`, including ingredients, preparation, finished temperature and specific variant.
2. Build positive food facts **and** negative constraints for each ID. Exact recipe identity outranks pretty composition.
3. Examine at least three approved 1–50 files appropriate to the dish, not internet photographs or an assumed image style.
4. Generate **one individual native-resolution image per recipe**. A cropped contact sheet is not equivalent to individual high-resolution art.
5. Inspect actual generated pixels for dish identity, garnishes, temperature, cooked state, anatomy and 2D style. Reject material errors. A tool call or asset filename alone is not visual review evidence.
6. Optimize JPEG to F3E: short edge >=720 px, long edge <=960 px, target <=130 KiB, hard limit <=140 KiB. Check the optimized output again.
7. For **new artworks 101+**, record a `styleReview` record in `authoring/assets/manifest.json`: `status: "approved"`, `guideVersion: "CA-ART-v1"`, `reviewedContentVersion`, at least three `referenceIds` from the anchors, `imageSha256` for the *actual committed JPEG*, `reviewedAt` and a specific `note`. The CI style gate checks this evidence; it **does not claim to evaluate image pixels autonomously**.
8. For replacement assets 001–100, include equivalent style evidence after actual visual review. The legacy catalogue is exempt from retrospective mandatory metadata; known rework exceptions are documented in `authoring/artwork/rework_queue_20261127.json`.
9. Follow the normal authoring, F3E validation, generated-catalog, PR and exact-head CI workflow before merge.

## Current per-recipe corrections

**080:** `Cololabis saira` (Pacific saury, sanma), elongated silvery fish with *short pointed beak* and slightly protruding lower jaw, not long needlefish bill; whole grilled fish with daikon and citrus. Reference: Smithsonian Tropical Research Institute species 5256 and NOAA/AFSC species morphology.

**081:** Tamago Sando must be a fully assembled crustless shokupan sandwich, visible egg-mayo filling and neat half-egg cross-section.

**083:** Tsukemen noodles are **cold**; only the separate concentrated dipping broth is hot and may steam.

**091–100:** Re-render using the 1–50 *hand-painted 2D* visual vocabulary; avoid photographic food, overpowering window scenery, repeated blue floral bowls and excessive hyper-gloss. **099 P0:** boiled white dango with *smooth koshian* red-bean paste and dusting of kinako; not textured whole-bean `tsubuan`.

## Evidence limits

A style/semantic metadata check only verifies that a declaration exists and is bound to the recipe and exact file bytes. Actual dish recognition and stylistic approval require inspected pixels and cannot be inferred from a clean CI job. An image-generation service error yields **zero newly corrected images**, not a pass.

## Operational rework command (historical approvals are not enough)

```bash
python3 tool/cooking_visual_adapter.py --rework-only --output build/visual_batch/rework_20261127.json
python3 tool/build_recipe_artwork_queue.py --rework-only --output build/authoring/rework_20261127.json
```

Both commands output **13 ID-specific work requests**, including previously approved assets. Their output is **PLANNED_NOT_GENERATED**, not artwork, visual approval or a merge. `--missing-only` now additionally includes flagged rework IDs; mark an item resolved in the source rework queue only after the actual corrected image has passed pixel review and landed in main.
