"""Visual Batch Engine contract: no fabricated generation or vision evidence."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tool"))
import visual_batch_engine as engine

spec = importlib.util.spec_from_file_location(
    "cooking_visual_adapter", ROOT / "tool/cooking_visual_adapter.py")
adapter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)


class TestVisualBatchEngine(unittest.TestCase):
    def test_reference_corpus_and_disjoint_pilot(self):
        output = adapter.build(ROOT)
        self.assertEqual(output["styleProfile"]["referenceCount"], 50)
        self.assertRegex(output["styleProfile"]["referenceFingerprint"], r"^[0-9a-f]{64}$")
        expected_missing = [n for n in adapter.PILOT_IDS
                            if adapter.load_json(ROOT / f"authoring/recipes/recipe_{n:06d}.json")
                               ["imageAssetId"] is None]
        self.assertEqual(output["count"], len(expected_missing))
        self.assertEqual(len({x["id"] for x in output["requests"]}), len(expected_missing))
        self.assertTrue(all(51 <= int(x["id"].split("_")[-1]) <= 162
                            for x in output["requests"]))
        self.assertEqual(output["imagesGenerated"], 0)
        self.assertEqual(output["imagesApproved"], 0)
        self.assertEqual(output["claims"]["semanticImageRecognition"], "NOT_RUN")
        self.assertEqual(output["requiresDomainReview"], 0)
        self.assertEqual(output["referenceFingerprint"],
                         adapter.build(ROOT)["referenceFingerprint"])

    def test_all_missing_are_planned_not_published(self):
        output = adapter.build(ROOT, pilot_only=False)
        still_missing = [n for n in range(51, 163)
                         if adapter.load_json(ROOT / f"authoring/recipes/recipe_{n:06d}.json")
                            ["imageAssetId"] is None]
        self.assertEqual(output["count"], len(still_missing))
        self.assertEqual(output["imagesGenerated"], 0)
        self.assertEqual(output["imagesApproved"], 0)
        self.assertEqual(output["requiresDomainReview"],
                         sum(n not in adapter.VISUAL_FACTS for n in still_missing))
        self.assertEqual(output["claims"]["imagesIntegrated"], 112 - len(still_missing))

    def test_resolved_rework_is_no_longer_queued(self):
        # The 13 visual issues from 27 Nov were replaced and SHA-reviewed.
        # A rework-only batch must now be empty, rather than replay old tasks.
        plan = adapter.build(ROOT, rework_only=True)
        self.assertEqual(plan["count"], 0)
        self.assertEqual(plan["imagesGenerated"], 0)
        self.assertEqual(plan["imagesApproved"], 0)
        self.assertEqual(plan["reworkIds"], [])
        self.assertEqual(plan["requests"], [])
        source = json.loads(
            (ROOT / "authoring/artwork/rework_queue_20261127.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(len(source["items"]), 13)
        self.assertTrue(all(
            item["status"] == "REPLACED_AND_VISUALLY_REVIEWED"
            for item in source["items"]
        ))

    def test_reject_duplicate_and_unreviewable_item(self):
        config = {"adapterId": "test", "styleDirective": "original art"}
        profile = {"referenceFingerprint": "a" * 64}
        spec = {"id": "x", "title": "Dish", "contentVersion": 1,
                "visualFacts": {"positive": ["rice"], "negative": ["no soup"]}}
        with self.assertRaises(ValueError):
            engine.plan_items(config, profile, [spec, spec])
        with self.assertRaises(ValueError):
            engine.plan_items(config, profile, [{"id": "y", "title": "y",
                                                 "contentVersion": 1, "visualFacts": {}}])

    def test_missing_and_false_evidence_are_not_accepted(self):
        req = {"id": "recipe_000051", "requestFingerprint": "1" * 64,
               "styleReferenceFingerprint": "2" * 64}
        policy = {"hardMaxBytes": 143360, "minShortEdge": 720, "maxLongEdge": 960}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "no-file.jpg"
            self.assertEqual(engine.review_candidate(path, req, policy)["state"],
                             "NOT_GENERATED")
            # Syntactically valid SOF frame; no source/trust claim is made.
            payload = bytes.fromhex("FFD8 FFC0 0011 08 02D0 03C0 03 01 11 00 02 11 00 03 11 00 FFD9")
            path.write_bytes(payload)
            self.assertEqual(engine.jpeg_geometry(payload), (960, 720))
            self.assertEqual(engine.review_candidate(path, req, policy)["state"],
                             "NEEDS_VISION_REVIEW")
            evidence = {"candidateSha256": "incorrect",
                        "requestFingerprint": req["requestFingerprint"],
                        "styleReferenceFingerprint": req["styleReferenceFingerprint"],
                        "mode": "ACTUAL_IMAGE_REVIEW", "foodIdentityPass": True, "stylePass": True}
            self.assertEqual(engine.review_candidate(path, req, policy, evidence)["state"],
                             "REJECT_STALE_VISION_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
