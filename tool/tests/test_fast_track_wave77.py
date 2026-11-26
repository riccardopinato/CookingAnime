"""Wave77 Cooking Anime regression: source-locked, offline, and version-safe.

28 touched records, 66 localized instruction corrections within a disjoint 77-ID
wave. This tests structural and exact-text parity, not culinary certification.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ("it", "en", "es", "fr", "de", "pt")
TRANSLATIONS = ("en", "es", "fr", "de", "pt")


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class FastTrackWave77Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = load("tool/fast_track_wave77_corrections.json")
        cls.canonical = {r["id"]: r for r in load("assets/catalog/recipes.json")["recipes"]}
        cls.packs = {
            locale: load(f"assets/catalog/locales/{locale}.json")["recipes"]
            for locale in LOCALES
        }

    def test_wave_inventory_disjoint_and_explicit(self):
        plan = self.plan
        self.assertEqual(plan["sourceLocale"], "it")
        self.assertEqual(set(plan["supportedLocales"]), set(LOCALES))
        self.assertEqual(plan["scopeRange"], [51, 162])
        excluded = set(plan["excludedAlreadyRepaired"])
        expected_scope = {n for n in range(51, 163) if n not in excluded}
        self.assertEqual(len(excluded), 35)
        self.assertEqual(len(expected_scope), 77)
        self.assertEqual(set(plan["scopeIds"]), expected_scope)
        fixes = plan["fixes"]
        self.assertEqual(len(fixes), 28)
        self.assertTrue(all(int(rid.split("_")[-1]) in expected_scope for rid in fixes))
        counts = {locale: 0 for locale in TRANSLATIONS}
        for recipe in fixes.values():
            self.assertTrue(set(recipe).issubset(TRANSLATIONS))
            for locale, steps in recipe.items():
                counts[locale] += len(steps)
        self.assertEqual(counts, {"en": 4, "es": 27, "fr": 4, "de": 27, "pt": 4})
        self.assertEqual(sum(counts.values()), 66)

    def test_all_28_authoring_records_equal_six_runtime_packages(self):
        for rid, fixes in self.plan["fixes"].items():
            with self.subTest(recipe=rid):
                source = load(f"authoring/recipes/{rid}.json")
                canon = self.canonical[rid]
                self.assertEqual(source["id"], rid)
                self.assertEqual(source["status"], "published")
                asset_id = source.get("imageAssetId")
                expected_asset = f"assets/recipe_artwork/{rid}.jpg" if asset_id else None
                self.assertEqual(asset_id, f"{rid}_artwork" if expected_asset else None)
                self.assertEqual(canon["imageAsset"], expected_asset)
                self.assertEqual(canon["contentVersion"], source["contentVersion"])
                self.assertEqual(set(source["locales"]), set(LOCALES))
                for field in ("status", "id", "inspirationTitle", "animeReferences",
                              "prepMinutes", "cookMinutes", "servings", "difficulty",
                              "contentOrigin", "sourceNote", "ingredients", "steps"):
                    self.assertEqual(canon[field], source[field], (rid, field))
                ingredient_ids = {item["id"] for item in source["ingredients"]}
                step_ids = {step["id"] for step in source["steps"]}
                for locale in LOCALES:
                    with self.subTest(recipe=rid, locale=locale):
                        actual = self.packs[locale][rid]
                        expected = source["locales"][locale]
                        self.assertEqual(actual["title"], expected["title"])
                        self.assertEqual(actual["description"], expected["description"])
                        self.assertEqual(actual["animeContext"], expected["animeContext"])
                        self.assertEqual(actual["ingredientTexts"], expected["ingredients"])
                        self.assertEqual(actual["stepTexts"], expected["steps"])
                        self.assertEqual(set(expected["ingredients"]), ingredient_ids)
                        self.assertEqual(set(expected["steps"]), step_ids)
                        self.assertTrue(expected["description"].strip())
                        self.assertTrue(all(v.strip() for v in expected["steps"].values()))
                        for step_id, text in fixes.get(locale, {}).items():
                            self.assertEqual(expected["steps"][step_id], text)
                            self.assertEqual(actual["stepTexts"][step_id], text)


if __name__ == "__main__":
    unittest.main()
