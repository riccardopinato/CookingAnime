#!/usr/bin/env python3
"""Fail-closed *metadata* gate for new CookingAnime artwork (not computer vision)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY = Path("authoring/artwork/style_policy.json")
MANIFEST = Path("authoring/assets/manifest.json")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
ID = re.compile(r"recipe_(\d{6})\Z")


def check_review(asset: dict, policy: dict, *, source: bytes, content_version: int) -> list[str]:
    """Bind an explicit visual editorial decision to *exact* JPEG bytes."""
    rid = str(asset["recipeId"])
    review = asset.get("styleReview")
    if not isinstance(review, dict):
        return [f"{rid}: missing styleReview for a new/replacement artwork"]
    errors = []
    if review.get("status") != "approved":
        errors.append(f"{rid}: styleReview.status must be approved")
    if review.get("guideVersion") != policy["guideVersion"]:
        errors.append(f"{rid}: styleReview.guideVersion is stale")
    if review.get("reviewedContentVersion") != content_version:
        errors.append(f"{rid}: styleReview.reviewedContentVersion is stale")
    refs = review.get("referenceIds")
    valid_refs = set(policy["referenceIds"])
    if (not isinstance(refs, list) or len(set(str(v) for v in refs)) < policy["minimumReferencesPerReview"]
            or any(not isinstance(v, str) or v not in valid_refs for v in refs)):
        errors.append(f"{rid}: styleReview.referenceIds need at least three real guide anchors")
    sha = review.get("imageSha256")
    if not isinstance(sha, str) or HEX64.fullmatch(sha) is None or sha != hashlib.sha256(source).hexdigest():
        errors.append(f"{rid}: styleReview.imageSha256 does not match the committed bytes")
    if not isinstance(review.get("reviewedAt"), str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", review["reviewedAt"]) is None:
        errors.append(f"{rid}: styleReview.reviewedAt must be YYYY-MM-DD")
    if not isinstance(review.get("note"), str) or len(review["note"].strip()) < 25:
        errors.append(f"{rid}: styleReview.note must document the visual check specifically")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    policy = json.loads((root / POLICY).read_text(encoding="utf-8"))
    if policy.get("schemaVersion") != 1 or policy.get("guideVersion") != "CA-ART-v1":
        return ["artwork style policy is not version 1"]
    if not (root / policy["guidePath"]).is_file():
        errors.append("missing canonical artwork style guide")
    for ref in policy["referenceIds"]:
        if not (root / "assets/recipe_artwork" / (ref + ".jpg")).is_file():
            errors.append(f"missing first-50 style anchor: {ref}")
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        rid = str(asset.get("recipeId", ""))
        match = ID.fullmatch(rid)
        if not match:
            continue  # Main authoring validator diagnoses invalid IDs.
        number = int(match.group(1))
        if number < policy["enforceFromRecipeNumber"] and "styleReview" not in asset:
            continue  # Grandfather existing 001–100 without silently re-certifying.
        image = root / str(asset["path"])
        recipe = root / "authoring/recipes" / (rid + ".json")
        if not image.is_file() or not recipe.is_file():
            errors.append(f"{rid}: source artwork or canonical recipe missing")
            continue
        version = json.loads(recipe.read_text(encoding="utf-8"))["contentVersion"]
        errors.extend(check_review(asset, policy, source=image.read_bytes(), content_version=version))
    return errors


if __name__ == "__main__":
    failures = validate()
    for failure in failures:
        print("ARTWORK STYLE GATE:", failure, file=sys.stderr)
    print(f"Artwork style metadata gate: {'FAILED' if failures else 'PASS'} (no pixel recognition)")
    raise SystemExit(bool(failures))
