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
LEGACY_BASELINE = Path("authoring/artwork/legacy_asset_baseline_20261127.json")
HEX64 = re.compile(r"[a-f0-9]{64}\Z")
HEX40 = re.compile(r"[a-f0-9]{40}\Z")
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


def git_blob_sha1(source: bytes) -> str:
    """Hash Git blob header plus content, not the content alone."""
    header = b"blob " + str(len(source)).encode("ascii") + b"\0"
    return hashlib.sha1(header + source).hexdigest()


def legacy_unmodified(source: bytes, stored_git_blob_sha1: str) -> bool:
    return bool(HEX40.fullmatch(stored_git_blob_sha1)) and git_blob_sha1(source) == stored_git_blob_sha1


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
    baseline = json.loads((root / LEGACY_BASELINE).read_text(encoding="utf-8"))
    originals = baseline.get("gitBlobSha1", {})
    if (baseline.get("schemaVersion") != 1
            or baseline.get("sourceMainCommit") != "ed900dcbcdc2460eab872c36c04135184d7adee6"
            or len(originals) != 100
            or any(not isinstance(v, str) or not HEX40.fullmatch(v) for v in originals.values())):
        return ["invalid or altered legacy artwork baseline"]
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    for asset in manifest.get("assets", []):
        rid = str(asset.get("recipeId", ""))
        match = ID.fullmatch(rid)
        if not match:
            continue  # Main authoring validator diagnoses invalid IDs.
        number = int(match.group(1))
        image = root / str(asset["path"])
        recipe = root / "authoring/recipes" / (rid + ".json")
        if number < policy["enforceFromRecipeNumber"] and "styleReview" not in asset:
            if not image.is_file():
                errors.append(f"{rid}: missing legacy artwork")
                continue
            original_sha = originals.get(rid)
            if not isinstance(original_sha, str) or not legacy_unmodified(image.read_bytes(), original_sha):
                errors.append(f"{rid}: legacy artwork changed; exact-byte styleReview required")
            continue
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
