"""Regression witnesses from the 2026-11-26 full 162x6 runtime scan."""
from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LOCALES = ("it", "en", "es", "fr", "de", "pt")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestNovember26Witnesses(unittest.TestCase):
    def test_source_runtime_parity_and_versions(self):
        canon = {r["id"]: r for r in load(ROOT / "assets/catalog/recipes.json")["recipes"]}
        packs = {locale: load(ROOT / f"assets/catalog/locales/{locale}.json")["recipes"]
                 for locale in LOCALES}
        for number in (51, 123, 162):
            rid = f"recipe_{number:06d}"
            author = load(ROOT / f"authoring/recipes/{rid}.json")
            self.assertEqual(canon[rid]["contentVersion"], author["contentVersion"])
            for locale in LOCALES:
                record = packs[locale][rid]
                source = author["locales"][locale]
                self.assertEqual(record["description"], source["description"])
                self.assertEqual(record["stepTexts"], source["steps"])
                self.assertEqual(record["ingredientTexts"], source["ingredients"])

    def test_shio_ramen_herb_matches_canonical_ingredient(self):
        a = load(ROOT / "authoring/recipes/recipe_000051.json")
        expected = {"it": "erba cipollina", "en": "chives", "es": "cebollino",
                    "fr": "ciboulette", "de": "Schnittlauch", "pt": "cebolinho"}
        for locale, name in expected.items():
            with self.subTest(locale=locale):
                self.assertIn(name.casefold(), a["locales"][locale]["description"].casefold())

    def test_zosui_rice_not_replaced_by_beans_or_other_false_friends(self):
        a = load(ROOT / "authoring/recipes/recipe_000123.json")
        self.assertEqual(len(a["steps"]), 7)
        for locale in LOCALES:
            text = " ".join([a["locales"][locale]["description"],
                             *a["locales"][locale]["steps"].values()]).casefold()
            for wrong in ("fucked", "fodido", "feijões", "beans", "écollez",
                          "cochez", "mit draht", "emborrachen", "los granos se desvanecen"):
                self.assertNotIn(wrong, text, (locale, wrong))

    def test_yuzu_egg_safety_and_instruction(self):
        a = load(ROOT / "authoring/recipes/recipe_000162.json")
        self.assertIn("pasteurized", a["locales"]["en"]["description"])
        self.assertIn("cooled syrup", a["locales"]["en"]["steps"]["step_3"])
        self.assertNotIn("Embed Yuzu", a["locales"]["en"]["steps"]["step_3"])


if __name__ == "__main__":
    unittest.main()
