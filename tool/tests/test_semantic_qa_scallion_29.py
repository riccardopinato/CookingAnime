"""Zero-API editorial safety checks: the Italian cipollotto is not onion or chives.

This is a bounded, inspectable linguistic invariant, NOT an AI meaning
certification, food-safety certification or human translator signoff.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
IDS = (55, 61, 63, 66, 71, 73, 75, 76, 78, 82, 83, 90, 92, 98, 100,
       108, 112, 114, 118, 123, 130, 131, 133, 134, 138, 147, 149, 151, 156)
PATTERNS = {
    "en": re.compile(r"\b(?:spring onions?|scallions?|green onions?)\b", re.I),
    "es": re.compile(r"\bcebolletas?\b", re.I),
    "fr": re.compile(r"(?:\bcébettes?\b|\bciboules?\b|\boignons?\s+nouveaux?\b)", re.I),
    "de": re.compile(r"\b(?:Frühlingszwiebeln?|Lauchzwiebeln?)\b", re.I),
    "pt": re.compile(r"\b(?:cebolas?\s+de\s+rama|cebolinhas?)\b", re.I),
}
LOCALES = ("it", "en", "es", "fr", "de", "pt")


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class SourceBoundIngredientFidelityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lexicon = load("tool/semantic_qa_scallion_lexicon.json")
        cls.runtime = {
            locale: load(f"assets/catalog/locales/{locale}.json")["recipes"]
            for locale in LOCALES
        }
        cls.canonical = {
            rec["id"]: rec for rec in load("assets/catalog/recipes.json")["recipes"]
        }

    def test_canonical_scope_and_provenance(self):
        self.assertEqual(self.lexicon["canonicalLocale"], "it")
        self.assertEqual(set(self.lexicon["targetLocales"]), set(PATTERNS))
        self.assertEqual(len(self.lexicon["terminology"]), 16)
        self.assertEqual(len(IDS), 29)

    def test_29_source_records_and_six_runtime_packs_are_consistent(self):
        for number in IDS:
            rid = f"recipe_{number:06d}"
            with self.subTest(recipe=rid):
                source = load(f"authoring/recipes/{rid}.json")
                self.assertEqual(source["id"], rid)
                self.assertEqual(source["status"], "published")
                asset_id = source.get("imageAssetId")
                expected_asset = f"assets/recipe_artwork/{rid}.jpg" if asset_id else None
                self.assertEqual(asset_id, f"{rid}_artwork" if expected_asset else None)
                self.assertEqual(self.canonical[rid]["imageAsset"], expected_asset)
                self.assertEqual(self.canonical[rid]["contentVersion"],
                                 source["contentVersion"])
                self.assertEqual(set(source["locales"]), set(LOCALES))
                for locale in LOCALES:
                    expected = source["locales"][locale]
                    actual = self.runtime[locale][rid]
                    self.assertEqual(actual["description"], expected["description"])
                    self.assertEqual(actual["ingredientTexts"],
                                     expected["ingredients"])
                    self.assertEqual(actual["stepTexts"], expected["steps"])
                    for key, it in source["locales"]["it"]["ingredients"].items():
                        mapping = self.lexicon["terminology"].get(it["name"])
                        if mapping and locale != "it":
                            self.assertEqual(expected["ingredients"][key]["name"],
                                             mapping[locale])
                    if locale == "it":
                        continue
                    for key, it_step in source["locales"]["it"]["steps"].items():
                        if "cipollott" not in it_step.casefold():
                            continue
                        localized = expected["steps"][key]
                        self.assertRegex(localized, PATTERNS[locale])

    def test_tsukemen_seven_steps_and_original_ingredients_preserved(self):
        rid = "recipe_000083"
        src = load(f"authoring/recipes/{rid}.json")
        source_ids = [v["id"] for v in src["ingredients"]]
        source_amounts = [(v.get("quantity"), v.get("unit")) for v in
                          src["ingredients"]]
        self.assertEqual(source_ids,
                         [v["id"] for v in self.canonical[rid]["ingredients"]])
        self.assertEqual(source_amounts,
                         [(v.get("quantity"), v.get("unit")) for v in
                          self.canonical[rid]["ingredients"]])
        for locale in LOCALES:
            texts = src["locales"][locale]
            self.assertEqual(len(texts["steps"]), 7)
            self.assertIn("katsuobushi", texts["description"].casefold())
            self.assertIn("katsuobushi",
                          texts["ingredients"]["polvere_di_pesce"]["name"].casefold())
            self.assertIn("5", texts["steps"]["step_3"])
            self.assertIn("6", texts["steps"]["step_3"])
        for locale in LOCALES[1:]:
            desc = src["locales"][locale]["description"].casefold()
            for stale in ("intingolo", "intingol", "traço e condimentos",
                          "tore glaze", "salsa tar", "pobre katsuobushi",
                          "poor katsuobushi", "fish powder (poor"):
                self.assertNotIn(stale, desc)

if __name__ == "__main__":
    unittest.main()
