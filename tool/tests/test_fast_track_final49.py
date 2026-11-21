"""Final49 review regression: 49 IDs, 46 source-bound corrected recipes, six runtime packs.

This test checks source/runtime structural and exact-field consistency. It is NOT
independent language-model semantic, professional culinary, or image certification.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ("it", "en", "es", "fr", "de", "pt")
EXPECTED_COUNTS = {"it": 5, "en": 19, "es": 118, "fr": 21, "de": 185, "pt": 123}


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class Final49FastTrackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.groups = [
            load(f"tool/final49/review_group_0{n}.json") for n in range(1, 6)
        ]
        cls.previous = load("tool/fast_track_wave77_corrections.json")
        cls.canonical = {x["id"]: x for x in load("assets/catalog/recipes.json")["recipes"]}
        cls.packs = {
            locale: load(f"assets/catalog/locales/{locale}.json")["recipes"]
            for locale in LOCALES
        }
        cls.fixes = {
            rid: changes
            for group in cls.groups
            for rid, changes in group["fixes"].items()
        }
        cls.ingredient_fixes = {
            rid: changes
            for group in cls.groups
            for rid, changes in group.get("ingredientFixes", {}).items()
        }

    def test_all_remaining_49_accounted_for(self):
        groups = self.groups
        ids = [number for group in groups for number in group["reviewedIds"]]
        self.assertEqual(len(ids), 49)
        self.assertEqual(len(set(ids)), 49)
        previously_fixed = {
            int(rid.split("_")[-1]) for rid in self.previous["fixes"]
        }
        self.assertEqual(
            set(ids),
            set(self.previous["scopeIds"]) - previously_fixed,
        )
        changed = {int(rid.split("_")[-1]) for rid in self.fixes}
        self.assertEqual(len(changed), 46)
        self.assertEqual(set(ids) - changed, {51, 56, 153})
        self.assertEqual(len(self.ingredient_fixes), 3)
        self.assertEqual(set(self.ingredient_fixes), {"recipe_000065", "recipe_000088", "recipe_000142"})

    def test_every_exact_source_locked_fix_is_in_runtime(self):
        locale_counts = dict.fromkeys(LOCALES, 0)
        for rid, locale_fixes in self.fixes.items():
            source = load(f"authoring/recipes/{rid}.json")
            for locale, steps in locale_fixes.items():
                self.assertIn(locale, LOCALES)
                for step_id, corrected in steps.items():
                    with self.subTest(recipe=rid, locale=locale, step=step_id):
                        self.assertTrue(corrected.strip())
                        self.assertIn(step_id, source["locales"]["it"]["steps"])
                        self.assertEqual(source["locales"][locale]["steps"][step_id], corrected)
                        self.assertEqual(self.packs[locale][rid]["stepTexts"][step_id], corrected)
                        locale_counts[locale] += 1
        self.assertEqual(locale_counts, EXPECTED_COUNTS)
        self.assertEqual(sum(locale_counts.values()), 471)
        for rid, changes in self.ingredient_fixes.items():
            source = load(f"authoring/recipes/{rid}.json")
            for locale, names in changes.items():
                for ingredient_id, replacement in names.items():
                    self.assertIn(ingredient_id, source["locales"]["it"]["ingredients"])
                    self.assertEqual(
                        source["locales"][locale]["ingredients"][ingredient_id]["name"],
                        replacement["name"],
                    )
                    self.assertEqual(
                        self.packs[locale][rid]["ingredientTexts"][ingredient_id]["name"],
                        replacement["name"],
                    )

    def test_every_reviewed_recipe_six_packs_and_metadata_parity(self):
        ids = [
            f"recipe_{number:06d}"
            for group in self.groups
            for number in group["reviewedIds"]
        ]
        for rid in ids:
            with self.subTest(recipe=rid):
                source = load(f"authoring/recipes/{rid}.json")
                record = self.canonical[rid]
                self.assertEqual(source["id"], rid)
                self.assertEqual(source["status"], "published")
                self.assertIsNone(source.get("imageAssetId"))
                self.assertEqual(record["id"], rid)
                self.assertEqual(record["contentVersion"], source["contentVersion"])
                for field in (
                    "status", "inspirationTitle", "animeReferences", "servings",
                    "difficulty", "prepMinutes", "cookMinutes", "ingredients", "steps",
                    "sourceNote", "contentOrigin",
                ):
                    self.assertEqual(record[field], source[field], (rid, field))
                for locale in LOCALES:
                    with self.subTest(recipe=rid, locale=locale):
                        expected = source["locales"][locale]
                        actual = self.packs[locale][rid]
                        self.assertEqual(actual["title"], expected["title"])
                        self.assertEqual(actual["description"], expected["description"])
                        self.assertEqual(actual["animeContext"], expected["animeContext"])
                        self.assertEqual(actual["ingredientTexts"], expected["ingredients"])
                        self.assertEqual(actual["stepTexts"], expected["steps"])
                        self.assertEqual(
                            set(actual["stepTexts"]),
                            {step["id"] for step in source["steps"]},
                        )
                        self.assertEqual(
                            set(actual["ingredientTexts"]),
                            {ingredient["id"] for ingredient in source["ingredients"]},
                        )

    def test_safety_and_semantic_specific_witnesses(self):
        sanma = load("authoring/recipes/recipe_000080.json")
        self.assertIn("eviscerato", sanma["locales"]["it"]["steps"]["step_1"])
        for locale in ("en", "es", "fr", "de", "pt"):
            self.assertEqual(
                sanma["locales"][locale]["steps"]["step_1"],
                self.fixes["recipe_000080"][locale]["step_1"],
            )
        chicken = load("authoring/recipes/recipe_000084.json")
        for locale in LOCALES:
            self.assertIn("74", chicken["locales"][locale]["steps"]["step_7"])
        tofu = load("authoring/recipes/recipe_000136.json")
        self.assertIn("Tofu", tofu["locales"]["de"]["steps"]["step_6"])
        self.assertNotIn("Auberginen", tofu["locales"]["de"]["steps"]["step_6"])
        matcha = load("authoring/recipes/recipe_000142.json")
        self.assertIn("no dry lumps remain", matcha["locales"]["en"]["steps"]["step_2"])
        offal = load("authoring/recipes/recipe_000110.json")
        for locale in LOCALES:
            self.assertTrue(offal["locales"][locale]["steps"]["step_1"])


if __name__ == "__main__":
    unittest.main()
