"""Regression checks for Tori Tsukune locale fidelity and food-safety copy."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[2]
RID = "recipe_000153"
LOCALES = ("it", "en", "es", "fr", "de", "pt")

def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))

class TsukuneQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.author = load(f"authoring/recipes/{RID}.json")
        cls.canonical = next(x for x in load("assets/catalog/recipes.json")["recipes"]
                             if x["id"] == RID)

    def test_version_and_ingredient_identity(self):
        self.assertGreaterEqual(self.author["contentVersion"], 6)
        self.assertEqual(self.canonical["contentVersion"], self.author["contentVersion"])
        self.assertEqual(
            [(x["id"],x["quantity"],x["unit"]) for x in self.canonical["ingredients"]],
            [(x["id"],x["quantity"],x["unit"]) for x in self.author["ingredients"]])
        self.assertIsNone(self.author["imageAssetId"])

    def test_all_six_locales_match_authoring(self):
        terms = {"it": "cipollotti", "en": "spring onions", "es": "cebolletas",
                 "fr": "cébettes", "de": "Frühlingszwiebeln",
                 "pt": "cebolas de rama"}
        for locale in LOCALES:
            with self.subTest(locale=locale):
                loc = self.author["locales"][locale]
                runtime = load(f"assets/catalog/locales/{locale}.json")["recipes"][RID]
                self.assertEqual(runtime["description"], loc["description"])
                self.assertEqual(runtime["ingredientTexts"], loc["ingredients"])
                self.assertEqual(runtime["stepTexts"], loc["steps"])
                self.assertIn(terms[locale].lower(),
                    loc["ingredients"]["cipollotto_tritati_finemente"]["name"].lower())
                self.assertIn("74", loc["description"])
                self.assertIn("74", loc["steps"]["step_6"])
                self.assertRegex(loc["description"].lower(), r"past[eé]ur")
                self.assertRegex(loc["steps"]["step_6"].lower(), r"past[eé]ur")
                self.assertNotIn("intingol", loc["description"].lower())
                self.assertNotIn("esmalte rasgado", loc["description"].lower())
                self.assertNotIn("intillo-eisel", loc["description"].lower())

if __name__ == "__main__":
    unittest.main()
