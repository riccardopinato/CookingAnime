"""Regression: valid English culinary verbs are not Italian leakage."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fast_track_recipe_inventory import ITALIAN_LEAK

class ItalianLeakTests(unittest.TestCase):
    def test_marinate_is_valid_english(self):
        self.assertIsNone(ITALIAN_LEAK.search(
            "Marinate the tuna for one or two minutes in soy sauce."))
        self.assertIsNone(ITALIAN_LEAK.search(
            "Let the chicken marinate for at least twenty minutes."))

    def test_genuine_italian_leaks_still_flagged(self):
        self.assertIsNotNone(ITALIAN_LEAK.search(
            "Mix the butter until ammorbidito."))
        self.assertIsNotNone(ITALIAN_LEAK.search(
            "Add sale marino fine."))

if __name__ == "__main__":
    unittest.main()
