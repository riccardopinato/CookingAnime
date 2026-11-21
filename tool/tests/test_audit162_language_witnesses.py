"""Pinned Cooking Anime linguistic witness regression; NOT full semantic certification."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
EXPECTED = {
  "recipe_000004": {
    "de": {
      "steps": [
        "cook_first_side"
      ],
      "ingredients": []
    },
    "es": {
      "steps": [
        "cook_first_side"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "cook_first_side"
      ],
      "ingredients": []
    },
    "pt": {
      "steps": [
        "cook_first_side"
      ],
      "ingredients": []
    }
  },
  "recipe_000023": {
    "de": {
      "steps": [
        "first_fry"
      ],
      "ingredients": []
    }
  },
  "recipe_000039": {
    "es": {
      "steps": [
        "prep_berries"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "prep_berries"
      ],
      "ingredients": []
    },
    "de": {
      "steps": [
        "prep_berries"
      ],
      "ingredients": []
    },
    "pt": {
      "steps": [
        "prep_berries"
      ],
      "ingredients": []
    }
  },
  "recipe_000041": {
    "es": {
      "steps": [
        "cook_covered"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "cook_covered"
      ],
      "ingredients": []
    },
    "de": {
      "steps": [
        "cook_covered"
      ],
      "ingredients": []
    },
    "pt": {
      "steps": [
        "cook_covered"
      ],
      "ingredients": []
    }
  },
  "recipe_000043": {
    "es": {
      "steps": [
        "warm_tofu"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "warm_tofu"
      ],
      "ingredients": []
    },
    "de": {
      "steps": [
        "warm_tofu"
      ],
      "ingredients": []
    },
    "pt": {
      "steps": [
        "warm_tofu"
      ],
      "ingredients": []
    }
  },
  "recipe_000080": {
    "en": {
      "steps": [
        "step_2",
        "step_4",
        "step_6",
        "step_8"
      ],
      "ingredients": []
    },
    "es": {
      "steps": [
        "step_5",
        "step_6",
        "step_7"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "step_2"
      ],
      "ingredients": [
        "fettine_di_limone_o_sudachi"
      ]
    },
    "de": {
      "steps": [
        "step_5",
        "step_6",
        "step_7"
      ],
      "ingredients": [
        "fettine_di_limone_o_sudachi"
      ]
    },
    "pt": {
      "steps": [
        "step_2"
      ],
      "ingredients": []
    }
  },
  "recipe_000111": {
    "en": {
      "steps": [
        "step_1"
      ],
      "ingredients": []
    }
  },
  "recipe_000136": {
    "en": {
      "steps": [
        "step_6"
      ],
      "ingredients": []
    },
    "es": {
      "steps": [
        "step_6"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "step_6"
      ],
      "ingredients": []
    }
  },
  "recipe_000029": {
    "de": {
      "steps": [
        "cook_tonkatsu"
      ],
      "ingredients": []
    }
  },
  "recipe_000030": {
    "es": {
      "steps": [
        "prep_filling"
      ],
      "ingredients": []
    },
    "fr": {
      "steps": [
        "prep_filling"
      ],
      "ingredients": []
    },
    "de": {
      "steps": [
        "prep_filling"
      ],
      "ingredients": []
    },
    "pt": {
      "steps": [
        "prep_filling"
      ],
      "ingredients": []
    }
  }
}
FORBIDDEN = {
    ("recipe_000080", "en", "step_2"): "Insert the skin",
    ("recipe_000080", "fr", "fettine_di_limone_o_sudachi"): "Coquilles",
    ("recipe_000080", "de", "fettine_di_limone_o_sudachi"): "Fenchel",
    ("recipe_000111", "en", "step_1"): "insert the skin",
}

class TestWitnesses(unittest.TestCase):
    def test_all_patched_fields_match_runtime(self):
        for rid, locales in EXPECTED.items():
            source = json.loads((ROOT / "authoring" / "recipes" / (rid+".json")).read_text(encoding="utf-8"))
            for locale, contents in locales.items():
                pack = json.loads((ROOT / "assets" / "catalog" / "locales" / (locale+".json")).read_text(encoding="utf-8"))["recipes"][rid]
                for key in contents["steps"]:
                    value = source["locales"][locale]["steps"][key]
                    self.assertEqual(value, pack["stepTexts"][key]); self.assertTrue(value.strip())
                    if (rid, locale, key) in FORBIDDEN:
                        self.assertNotIn(FORBIDDEN[rid, locale, key].lower(), value.lower())
                for key in contents["ingredients"]:
                    value = source["locales"][locale]["ingredients"][key]["name"]
                    self.assertEqual(value, pack["ingredientTexts"][key]["name"])
                    if (rid, locale, key) in FORBIDDEN:
                        self.assertNotIn(FORBIDDEN[rid, locale, key].lower(), value.lower())

    def test_changed_versions_match_canonical(self):
        all_recipes = json.loads((ROOT / "assets" / "catalog" / "recipes.json").read_text(encoding="utf-8"))["recipes"]
        canonical = {row["id"]: row for row in all_recipes}
        for rid in EXPECTED:
            source = json.loads((ROOT / "authoring" / "recipes" / (rid+".json")).read_text(encoding="utf-8"))
            self.assertEqual(source["contentVersion"], canonical[rid]["contentVersion"])

if __name__ == "__main__": unittest.main()
