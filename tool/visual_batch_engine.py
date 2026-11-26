#!/usr/bin/env python3
"""Portable, domain-neutral Visual Batch Engine v0.1.

It prepares deterministic source/style-grounded requests, fingerprints real
reference images and gates JPEG deliverables. It does NOT generate images or
pretend to run semantic vision without an explicitly connected provider.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def fingerprint(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def jpeg_geometry(payload: bytes) -> tuple[int, int]:
    """Parse baseline/progressive JPEG SOF dimensions without new dependencies."""
    if not payload.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG")
    i = 2
    frames = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
              0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
    while i < len(payload):
        if payload[i] != 0xFF:
            i += 1
            continue
        while i < len(payload) and payload[i] == 0xFF:
            i += 1
        if i >= len(payload):
            break
        marker = payload[i]
        i += 1
        if marker in (0x00, 0x01, 0xD8):
            continue
        if marker in (0xD9, 0xDA):
            break
        if 0xD0 <= marker <= 0xD7:
            continue
        if i + 2 > len(payload):
            break
        length = int.from_bytes(payload[i:i + 2], "big")
        if length < 2 or i + length > len(payload):
            break
        if marker in frames and length >= 7:
            height = int.from_bytes(payload[i + 3:i + 5], "big")
            width = int.from_bytes(payload[i + 5:i + 7], "big")
            if width <= 0 or height <= 0:
                break
            return width, height
        i += length
    raise ValueError("JPEG geometry unavailable")


def inspect_image(path: Path, policy: dict) -> dict:
    data = path.read_bytes()
    width, height = jpeg_geometry(data)
    violations = []
    if len(data) > policy["hardMaxBytes"]:
        violations.append("MAX_BYTES")
    if min(width, height) < policy["minShortEdge"]:
        violations.append("MIN_SHORT_EDGE")
    if max(width, height) > policy["maxLongEdge"]:
        violations.append("MAX_LONG_EDGE")
    return {
        "sha256": hashlib.sha256(data).hexdigest(),
        "width": width,
        "height": height,
        "bytes": len(data),
        "technicalViolations": violations,
    }


def reference_profile(root: Path, adapter: dict) -> dict:
    """Ground the profile in actual image bytes; prose is adapter-authored."""
    files = []
    for relpath in adapter["referencePaths"]:
        safe_path = Path(relpath)
        if safe_path.is_absolute() or ".." in safe_path.parts:
            raise ValueError("reference path escapes repository")
        path = root / safe_path
        if not path.is_file():
            raise ValueError(f"missing style reference: {relpath}")
        probe = inspect_image(path, adapter["assetPolicy"])
        if probe["technicalViolations"]:
            raise ValueError(f"reference is not valid per policy: {relpath}")
        files.append({"path": relpath, **probe})
    if not files:
        raise ValueError("empty reference set")
    return {
        "adapterId": adapter["adapterId"],
        "referenceCount": len(files),
        "references": files,
        "referenceFingerprint": fingerprint(files),
        "styleDirective": adapter["styleDirective"],
        # Byte and geometric verification is NOT image semantic/style analysis.
        "styleAssessment": "EDITORIAL_DIRECTIVE_WITH_BYTE_VERIFIED_REFERENCES",
        "visualRecognitionPerformed": False,
    }


def plan_items(adapter: dict, profile: dict, items: list[dict]) -> dict:
    """Prepare provider-independent batch requests. ID-level ownership."""
    seen = set()
    requests = []
    for item in sorted(items, key=lambda v: v["id"]):
        rid = item["id"]
        if rid in seen:
            raise ValueError(f"duplicate asset request id {rid}")
        seen.add(rid)
        facts = item["visualFacts"]
        if not facts.get("positive") or not facts.get("negative"):
            raise ValueError(f"{rid} lacks positive/negative visual constraints")
        item_hash = fingerprint(item)
        prompt = "\n".join([
            adapter["styleDirective"],
            f"Artwork subject: {item['title']}.",
            "REQUIRED VISIBLE FACTS: " + "; ".join(facts["positive"]),
            "MUST NOT DEPICT: " + "; ".join(facts["negative"]),
            "Context only (not a demand to depict every ingredient): " +
                "; ".join(item.get("ingredientNames", [])[:16]),
            "Visual emphasis: food-only, no characters, no anime frames, no logos, no text.",
            "One coherent dish per image. No invented crucial garnishes or substitutions.",
        ])
        requests.append({
            "id": rid,
            "contentVersion": item["contentVersion"],
            "itemFingerprint": item_hash,
            "styleReferenceFingerprint": profile["referenceFingerprint"],
            "requestFingerprint": fingerprint([item_hash, profile["referenceFingerprint"], prompt]),
            "prompt": prompt,
            "requestedVariants": adapter.get("variantsPerRecipe", 2),
            "targetFileStem": rid,
            "workflowStatus": "PLANNED_NOT_GENERATED",
            "visionReviewStatus": "NOT_PERFORMED",
            "providerStatus": "UNCONNECTED",
        })
    return {
        "schemaVersion": 1,
        "engine": "visual_batch_engine",
        "adapterId": adapter["adapterId"],
        "referenceFingerprint": profile["referenceFingerprint"],
        "count": len(requests),
        "requests": requests,
        "imagesGenerated": 0,
        "imagesVisionVerified": 0,
        "imagesApproved": 0,
        "providerCalls": 0,
    }


def review_candidate(path: Path, request: dict, policy: dict,
                     vision_evidence: dict | None = None) -> dict:
    """Strict technical inspection + optional source-bound external vision evidence.

    A vision result cannot silently publish an asset: a separate human/authorized
    asset-review decision is still required by each app's asset policy.
    """
    if not path.exists():
        return {"state": "NOT_GENERATED", "id": request["id"]}
    try:
        probe = inspect_image(path, policy)
    except (OSError, ValueError) as exc:
        return {"state": "REJECT_TECHNICAL", "id": request["id"], "reason": str(exc)}
    if probe["technicalViolations"]:
        return {"state": "REJECT_TECHNICAL", "id": request["id"], **probe}
    if vision_evidence is None:
        return {"state": "NEEDS_VISION_REVIEW", "id": request["id"], **probe}
    for key, expected in (
        ("candidateSha256", probe["sha256"]),
        ("requestFingerprint", request["requestFingerprint"]),
        ("styleReferenceFingerprint", request["styleReferenceFingerprint"]),
    ):
        if vision_evidence.get(key) != expected:
            return {"state": "REJECT_STALE_VISION_EVIDENCE", "id": request["id"], **probe}
    if vision_evidence.get("mode") != "ACTUAL_IMAGE_REVIEW":
        return {"state": "NEEDS_VISION_REVIEW", "id": request["id"], **probe}
    if vision_evidence.get("criticalMismatch") or not vision_evidence.get("foodIdentityPass") or not vision_evidence.get("stylePass"):
        return {"state": "REJECT_VISUAL", "id": request["id"], **probe}
    return {"state": "VISUAL_CANDIDATE_PASS_NOT_APPROVED", "id": request["id"], **probe}
