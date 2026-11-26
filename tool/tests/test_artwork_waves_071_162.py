"""Image-backed 71+ waves must preserve exact stable IDs and version-bound manifest."""
import json
from pathlib import Path
import unittest
import sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"tool"))
from recipe_authoring_lib import _jpeg_dimensions

def load(p): return json.loads(p.read_text(encoding="utf-8"))

class TestAutoArtworkWaves(unittest.TestCase):
    def test_exact_source_manifest_runtime_for_every_integrated_wave_asset(self):
        manifest=load(ROOT/"authoring/assets/manifest.json")
        assets={a["recipeId"]:a for a in manifest["assets"]}
        recipes={r["id"]:r for r in load(ROOT/"assets/catalog/recipes.json")["recipes"]}
        self.assertGreaterEqual(len(assets),80)
        latest=max(int(id.rsplit("_",1)[-1]) for id in assets)
        for n in range(71,latest+1):
            id=f"recipe_{n:06d}"
            with self.subTest(id=id):
                self.assertIn(id,assets)
                original=load(ROOT/f"authoring/recipes/{id}.json")
                asset=assets[id]
                rel=f"assets/recipe_artwork/{id}.jpg"
                self.assertEqual(original["imageAssetId"],id+"_artwork")
                self.assertEqual(recipes[id]["imageAsset"],rel)
                self.assertEqual(asset["id"],id+"_artwork")
                self.assertEqual(asset["path"],rel)
                self.assertEqual(asset["rights"],"original")
                self.assertEqual(asset["semanticReview"]["status"],"approved")
                self.assertEqual(asset["semanticReview"]["reviewedContentVersion"],original["contentVersion"])
                file=ROOT/rel
                self.assertTrue(file.is_file())
                self.assertLessEqual(file.stat().st_size,133120)
                wh=_jpeg_dimensions(file)
                self.assertGreaterEqual(min(wh),720)
                self.assertLessEqual(max(wh),960)
