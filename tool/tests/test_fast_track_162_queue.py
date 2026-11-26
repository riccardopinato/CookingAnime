"""Regression coverage for non-certifying Fast Track inventory and work lanes."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tool"
sys.path.insert(0, str(TOOL))
spec = importlib.util.spec_from_file_location("fast_track_162_queue", TOOL / "fast_track_162_queue.py")
queue = importlib.util.module_from_spec(spec)
spec.loader.exec_module(queue)


class TestFastTrack162Queue(unittest.TestCase):
    def test_batches_are_disjoint_and_deterministic(self):
        rows = [{"id": f"recipe_{i:06d}"} for i in range(162, 0, -1)]
        batches = queue.partition(rows, 100)
        self.assertEqual([b["count"] for b in batches], [100, 62])
        ids = [rid for b in batches for rid in b["ids"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(batches, queue.partition(rows, 100))

    def test_overlap_and_invalid_batch_fail(self):
        with self.assertRaises(ValueError):
            queue.partition([{"id": "same"}, {"id": "same"}], 100)
        with self.assertRaises(ValueError):
            queue.partition([], 0)

    def test_full_real_catalog_remains_review_not_certified(self):
        report = queue.build(ROOT)
        self.assertEqual(report["countCanonicalIds"], 162)
        self.assertEqual(report["totalLocaleRecordsExpected"], 972)
        self.assertEqual(report["structurallyInspectedTranslationPairs"], 810)
        self.assertEqual([b["count"] for b in report["batches"]], [100, 62])
        self.assertEqual(report["semanticallyReviewedByAI"], 0)
        self.assertEqual(report["semanticallyCertifiedPairs"], 0)
        self.assertEqual(report["semanticCertification"], "NOT_CERTIFIED")
        self.assertTrue(all(row["semanticStatus"] == "REVIEW_REQUIRED"
                            for row in report["recipes"]))
        self.assertEqual(report["contentFingerprint"], queue.build(ROOT)["contentFingerprint"])


if __name__ == "__main__":
    unittest.main()
