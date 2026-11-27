from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from artwork_style_gate import check_review, validate  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
POLICY = {
    "guideVersion": "CA-ART-v1",
    "referenceIds": [f"recipe_{n:06d}" for n in (5, 20, 25, 35, 45, 50)],
    "minimumReferencesPerReview": 3,
}


def example(payload=b"actual jpeg"):
    return {
        "recipeId": "recipe_000101",
        "styleReview": {
            "status": "approved",
            "guideVersion": "CA-ART-v1",
            "reviewedContentVersion": 3,
            "referenceIds": POLICY["referenceIds"][:3],
            "imageSha256": hashlib.sha256(payload).hexdigest(),
            "reviewedAt": "2026-11-27",
            "note": "Food identity and 2D anime style visually checked against real guide references.",
        },
    }


class TestArtworkStyleGate(unittest.TestCase):
    def test_existing_catalog_is_not_retroactively_failed(self):
        self.assertEqual(validate(ROOT), [])

    def test_source_bound_style_review_passes(self):
        self.assertEqual(check_review(example(), POLICY, source=b"actual jpeg", content_version=3), [])

    def test_missing_style_review_is_blocked(self):
        self.assertIn("missing styleReview", " ".join(
            check_review({"recipeId": "recipe_000101"}, POLICY, source=b"test", content_version=1)
        ))

    def test_changed_bytes_and_wrong_reference_are_blocked(self):
        record = example()
        record["styleReview"]["referenceIds"] = ["recipe_000099"]
        result = check_review(record, POLICY, source=b"changed jpeg", content_version=3)
        self.assertTrue(any("referenceIds" in e for e in result))
        self.assertTrue(any("imageSha256" in e for e in result))

    def test_stale_content_version_is_blocked(self):
        result = check_review(example(), POLICY, source=b"actual jpeg", content_version=4)
        self.assertTrue(any("reviewedContentVersion" in e for e in result))


if __name__ == "__main__":
    unittest.main()
