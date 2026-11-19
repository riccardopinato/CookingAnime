#!/usr/bin/env python3
"""Cooking Anime Semantic QA adapter unit tests (no API, no repo mutations)."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "semantic_qa_adapter.py"
spec = importlib.util.spec_from_file_location("cooking_semantic_adapter", SCRIPT)
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class AdapterTests(unittest.TestCase):
    def make_root(self, base: Path):
        folder = base / "authoring/recipes"
        folder.mkdir(parents=True)
        for i in range(1, 163):
            rid = f"recipe_{i:06d}"
            text = {"title": f"Ricetta {i}", "description": "Cottura completa.",
                    "animeContext": "", "ingredients": {"a": {"name": "pollo"}},
                    "steps": {"step_1": "Cuoci fino al centro."}}
            locale = {l: dict(text) for l in ("it", "en", "es", "fr", "de", "pt")}
            recipe = {"id": rid, "status": "published", "contentVersion": 1,
                      "locales": locale,
                      "ingredients": [{"id": "a", "quantity": 100, "unit": "g"}],
                      "steps": [{"id": "step_1", "timerSeconds": 0}]}
            (folder / f"{rid}.json").write_text(json.dumps(recipe),encoding="utf-8")
    def test_all_162_unique_source_bound(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.make_root(root)
            data=adapter.collect(root)
            self.assertEqual(len(data["records"]),162)
            self.assertEqual(data["sourceLocale"],"it")
            self.assertEqual(len(data["targetLocales"]),5)
            self.assertEqual(data["records"][0]["context"]["ingredients"][0]["quantity"],100)
            self.assertEqual(data["records"][-1]["id"],"recipe_000162")
    def test_localized_ingredient_notes_are_semantically_visible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.make_root(root)
            path=root/"authoring/recipes/recipe_000128.json"
            source=json.loads(path.read_text(encoding="utf-8"))
            source["locales"]["it"]["ingredients"]["a"]["note"]="Circa 160 g per persona."
            source["locales"]["en"]["ingredients"]["a"]["note"]="About 160 g per person."
            path.write_text(json.dumps(source),encoding="utf-8")
            data=adapter.collect(root)
            row=data["records"][127]
            self.assertIn("160 g",row["source"]["ingredients"]["a"]["note"])
            self.assertIn("160 g",row["translations"]["en"]["ingredients"]["a"]["note"])
    def test_mismatch_detected_and_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            self.make_root(root)
            (root/"authoring/recipes/recipe_000162.json").unlink()
            with self.assertRaises(ValueError):
                adapter.collect(root)
    def test_report_completeness_and_certification(self):
        report={"adapter":"cooking_anime","recordCount":162,
                "comparisonCount":810,"certification":"NOT_CERTIFIED",
                "results":[{"id":"recipe_000001","locale":"en","state":"OFFLINE_REVIEW_REQUIRED"}]}
        summary=adapter.verify_report(report)
        self.assertEqual(summary["blockingStructuralHolds"],0)
        report["certification"]="CERTIFIED"
        with self.assertRaises(ValueError):adapter.verify_report(report)

if __name__=="__main__":unittest.main()
