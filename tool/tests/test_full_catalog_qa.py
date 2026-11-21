"""Full live catalog structural matrix: no semantic or hardware certification."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "tool/full_catalog_qa.py"
spec = importlib.util.spec_from_file_location("full_catalog_qa", PATH)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class TestFullCatalog(unittest.TestCase):
    def test_exact_runtime_source_and_ui_parity(self):
        out = qa.run(ROOT)
        self.assertEqual(out["sourceRecipes"], 162)
        self.assertEqual(out["canonicalRuntimeRecipes"], 162)
        self.assertEqual(set(out["localeCounts"].values()), {162})
        self.assertEqual(len(set(out["uiArbKeys"].values())), 1)
        self.assertGreater(min(out["uiArbKeys"].values()), 0)
        self.assertRegex(out["inputFingerprint"], r"^[0-9a-f]{64}$")
        self.assertEqual(out["inputFingerprint"], qa.run(ROOT)["inputFingerprint"])
        self.assertEqual(out["blockingErrors"], [])
        self.assertEqual(out["editorialCertification"], "NOT_CERTIFIED")
        self.assertEqual(out["physicalDeviceVerification"], "NOT_VERIFIED")

    def test_numeric_heuristic_must_not_silently_certify(self):
        self.assertEqual(qa.anchors("2 minuti, 74 °C"), ["2", "74"])
        self.assertEqual(qa.anchors("two minutes, 74 °C"), ["74"])
        output = qa.run(ROOT)
        self.assertTrue(any(w["code"] == "NUMERIC_ANCHOR_REVIEW"
                            for w in output["reviewWarnings"]))
        self.assertTrue(any(w["code"] == "STEP_TIMER_EXCEEDS_TOTAL"
                            for w in output["reviewWarnings"]))


if __name__ == "__main__":
    unittest.main()
