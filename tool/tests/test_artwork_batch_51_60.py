"""Artwork batch 51-60: exact authoring/asset/runtime wiring and F3E budget."""
from __future__ import annotations
import json
from pathlib import Path
import unittest
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tool"))
from recipe_authoring_lib import _jpeg_dimensions

ASSET_ROOT = ROOT / "assets/recipe_artwork"
MANIFEST = ROOT / "authoring/assets/manifest.json"
RUNTIME = ROOT / "assets/catalog/recipes.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


class TestArtworkBatch51To60(unittest.TestCase):
    def test_every_recipe_has_exact_current_approved_asset(self):
        manifest = read_json(MANIFEST)
        registry = {a["recipeId"]: a for a in manifest["assets"]}
        runtime = {r["id"]: r for r in read_json(RUNTIME)["recipes"]}
        self.assertGreaterEqual(len(registry), 60)
        for n in range(51, 61):
            recipe_id = f"recipe_{n:06d}"
            author = read_json(ROOT / f"authoring/recipes/{recipe_id}.json")
            asset = registry[recipe_id]
            relpath = f"assets/recipe_artwork/{recipe_id}.jpg"
            with self.subTest(recipe=recipe_id):
                self.assertEqual(author["id"], recipe_id)
                self.assertEqual(author["status"], "published")
                self.assertEqual(author["imageAssetId"], recipe_id + "_artwork")
                self.assertEqual(runtime[recipe_id]["imageAsset"], relpath)
                self.assertEqual(asset["id"], recipe_id + "_artwork")
                self.assertEqual(asset["path"], relpath)
                self.assertEqual(asset["rights"], "original")
                self.assertEqual(asset["semanticReview"]["status"], "approved")
                self.assertEqual(asset["semanticReview"]["reviewedContentVersion"],
                                 author["contentVersion"])
                image_file = ROOT / relpath
                self.assertTrue(image_file.is_file())
                self.assertLessEqual(image_file.stat().st_size, 133120)
                dimensions = _jpeg_dimensions(image_file)
                self.assertIsNotNone(dimensions)
                self.assertGreaterEqual(min(dimensions), 720)
                self.assertLessEqual(max(dimensions), 960)


if __name__ == "__main__":
    unittest.main()
