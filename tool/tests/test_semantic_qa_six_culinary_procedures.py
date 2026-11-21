"""Offline regression for Cooking Anime PR #67 six-recipe source/runtime parity.

This structural test is not an AI semantic review or chef certification.
"""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
RECIPE_NUMBERS = (53, 57, 60, 67, 72, 79)
LOCALES = ("en", "it", "es", "fr", "de", "pt")


def read_json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SixCulinaryRecipesRuntimeParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = {
            record["id"]: record
            for record in read_json("assets/catalog/recipes.json")["recipes"]
        }
        cls.locales = {
            locale: read_json(f"assets/catalog/locales/{locale}.json")["recipes"]
            for locale in LOCALES
        }

    def test_all_six_recipes_match_authoring_exactly(self):
        for number in RECIPE_NUMBERS:
            rid = f"recipe_{number:06d}"
            with self.subTest(recipe=rid):
                source = read_json(f"authoring/recipes/{rid}.json")
                canonical = self.canonical[rid]
                self.assertEqual(source["id"], rid)
                self.assertEqual(source["status"], "published")
                self.assertEqual(source["contentVersion"], canonical["contentVersion"])
                self.assertEqual(set(source["locales"]), set(LOCALES))
                self.assertIsNone(source["imageAssetId"])
                self.assertIsNone(canonical["imageAsset"])
                for field in ("id", "status", "inspirationTitle", "animeReferences",
                              "prepMinutes", "cookMinutes", "servings", "difficulty",
                              "contentOrigin", "sourceNote", "ingredients", "steps"):
                    self.assertEqual(canonical[field], source[field], (rid, field))
                ingredient_ids = {ingredient["id"] for ingredient in source["ingredients"]}
                step_ids = {step["id"] for step in source["steps"]}
                for locale in LOCALES:
                    with self.subTest(recipe=rid, locale=locale):
                        expected = source["locales"][locale]
                        actual = self.locales[locale][rid]
                        self.assertEqual(actual["title"], expected["title"])
                        self.assertEqual(actual["description"], expected["description"])
                        self.assertEqual(actual["animeContext"], expected["animeContext"])
                        self.assertEqual(actual["ingredientTexts"], expected["ingredients"])
                        self.assertEqual(actual["stepTexts"], expected["steps"])
                        self.assertEqual(set(expected["ingredients"]), ingredient_ids)
                        self.assertEqual(set(expected["steps"]), step_ids)
                        self.assertTrue(expected["description"].strip())
                        self.assertTrue(all(text.strip() for text in expected["steps"].values()))


if __name__ == "__main__":
    unittest.main()
