#!/usr/bin/env python3
"""Fast Track 162x6 work queue. No AI/provider calls or inferred certification.

Reuses the current full_catalog_qa and semantic_qa_adapter. Read-only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from full_catalog_qa import run as structural_qa
from semantic_qa_adapter import collect as semantic_source

ROOT = Path(__file__).resolve().parents[1]


def sha256_json(value: object) -> str:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def partition(rows: list[dict], batch_size: int = 100) -> list[dict]:
    if batch_size < 1:
        raise ValueError("batch size must be positive")
    if len(set(row["id"] for row in rows)) != len(rows):
        raise ValueError("overlapping recipe IDs")
    ordered = sorted(rows, key=lambda r: r["id"])
    return [
        {
            "batch": n // batch_size + 1,
            "count": len(part),
            "ids": [r["id"] for r in part],
            "fingerprint": sha256_json(part),
        }
        for n in range(0, len(ordered), batch_size)
        for part in [ordered[n:n + batch_size]]
    ]


def build(root: Path = ROOT, batch_size: int = 100) -> dict:
    structural = structural_qa(root)
    semantic_input = semantic_source(root)
    records = semantic_input["records"]
    errors = defaultdict(list)
    warnings = defaultdict(list)
    for item in structural["blockingErrors"]:
        errors[item.get("id", "__global__")].append(item)
    for item in structural["reviewWarnings"]:
        warnings[item.get("id", "__global__")].append(item)
    rows = []
    for record in records:
        recipe_id = record["id"]
        locales = set(record["translations"])
        missing = sorted(set(semantic_input["targetLocales"]) - locales)
        item_errors = errors[recipe_id] + [{"code": "MISSING_TRANSLATION", "locale": l} for l in missing]
        item_warnings = warnings[recipe_id]
        rows.append({
            "id": recipe_id,
            "contentVersion": record["context"]["contentVersion"],
            "sourceFingerprint": sha256_json(record),
            "localesPresent": sorted(["it", *locales]),
            "translationPairsPresent": len(locales),
            "structuralStatus": "HOLD" if item_errors else "PASS",
            "semanticStatus": "REVIEW_REQUIRED",
            "issues": item_errors,
            "reviewSignals": item_warnings,
            "reviewPriority": "P0" if item_errors else ("P1" if item_warnings else "P2"),
        })
    batches = partition(rows, batch_size)
    statuses = dict(sorted(Counter(row["structuralStatus"] for row in rows).items()))
    return {
        "schemaVersion": 1,
        "report": "COOKING_ANIME_FAST_TRACK_162X6_QUEUE",
        "mode": "OFFLINE_STRUCTURAL_TRIAGE_ONLY",
        "source": "authoring/recipes",
        "inputFingerprint": structural["inputFingerprint"],
        "contentFingerprint": sha256_json(rows),
        "countCanonicalIds": len(rows),
        "localeCountIncludingItalian": 6,
        "totalLocaleRecordsExpected": 6 * len(rows),
        "structurallyInspectedTranslationPairs": sum(r["translationPairsPresent"] for r in rows),
        "semanticallyReviewedByAI": 0,
        "semanticallyCertifiedPairs": 0,
        "semanticCertification": "NOT_CERTIFIED",
        "structuralStatusCounts": statuses,
        "warningCounts": structural["warningCounts"],
        "globalBlockingErrors": errors["__global__"],
        "batches": batches,
        "recipes": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "build/fast_track/queue.json")
    parser.add_argument("--batch-size", type=int, default=100)
    args = parser.parse_args()
    result = build(args.root, args.batch_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "recipes": result["countCanonicalIds"],
        "batches": [b["count"] for b in result["batches"]],
        "statuses": result["structuralStatusCounts"],
        "reviewWarnings": result["warningCounts"],
        "semanticCertification": result["semanticCertification"],
        "output": str(args.output),
    }, ensure_ascii=False))
    return 2 if result["globalBlockingErrors"] or result["structuralStatusCounts"].get("HOLD", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
