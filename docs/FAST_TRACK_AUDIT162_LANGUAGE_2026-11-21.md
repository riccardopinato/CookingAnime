# Cooking Anime — correction of re-audit witnesses (2026-11-21)

Source pinned: `4b5ae932aeb60bc42643b85e49d1fe27b70c2294`. Rechecked all 162 published recipe IDs / all six locale catalogs; 162 records per locale. This change corrects **40 source-bound translated text fields in 10 recipes** across EN, ES, FR, DE and PT. It is not a complete independent semantic certification of all 810 source/target comparisons.

### Witnesses fixed
- Missing quantitative anchors: 5 mm Dorayaki ring; 1.5–2 cm Tonkatsu cutlet (also the long German method); 4–5 mm strawberry slices for Strawberry Shortcake; 1.5–2 cm Tonkatsu cutlet; 25 g Ichigo Daifuku anko; 20–22 cm omelette pan; 1–1.5 cm tofu cubes.
- Sanma: translated cutting/drying/serving verbs and German/French lemon/sudachi names; English mackerel scoring in recipe 111; clearer miso glaze instructions for tofu recipe 136.
- IDs, anime references, portions, canonical quantities, per-step timers, preparation/cooking minutes, images, and statuses unchanged. Bump exactly one `contentVersion` for each of the 8 edited recipes. Runtime locale packs updated consistently.

### Verification boundary
New regression tests assert exact authoring/runtime parity and witnessed wording. The core Semantic QA still runs OFFLINE_ONLY and requires independent contextual review; CI PASS does not prove culinary or full-linguistic certification. Device tests, timing discrepancies and full translation QA are independent follow-up gates.
