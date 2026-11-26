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
        self.assertEqual(output["count"], 12)
        self.assertEqual(len({x["id"] for x in output["requests"]}), 12)
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
        self.assertEqual(output["count"], 112)
        self.assertEqual(output["imagesGenerated"], 0)
        self.assertEqual(output["imagesApproved"], 0)
        self.assertEqual(output["requiresDomainReview"], 100)
        self.assertEqual(output["claims"]["imagesIntegrated"], 0)

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
