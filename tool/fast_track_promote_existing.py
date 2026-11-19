#!/usr/bin/env python3
"""Materialize existing F3K/F3L six-locale recipe content, never invent new IDs.

Fast Track execution: structural source-lock and known-risk HOLD are not
a professional culinary/language certification. Run --check for a non-writing
reconciliation or --apply to update authoring/runtime and the ledger.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from f3l_translation_gate import digest, inspect

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("en", "es", "fr", "de", "pt")
HOLD = {
    51: "Salt amount 1.5 tbsp in 500 ml broth requires correction before publishing updated method",
    56: "Raw seafood sourcing and cold-chain handling",
    59: "Shellfish handling and cooking guidance",
    80: "Japanese sanma species/common-name ambiguity",
    96: "Shellfish handling and cooking guidance",
    110: "Offal cleaning, doneness and handling",
    117: "Poultry/egg preparation safety",
    133: "Poultry/egg preparation safety",
    149: "Cooked-rice rapid cooling and reheating safeguards",
    150: "Poultry/duck doneness and handling",
    153: "Raw dipping yolk suitability",
    156: "Clam handling and cooking guidance",
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def translate(source: dict, candidate: dict, locale: str) -> dict:
    ingredients = [dict(x) for x in candidate["ingredients"]]
    steps = [dict(x) for x in candidate["steps"]]
    # Source-witnessed semantic repairs, not generic machine substitution.
    if source["id"] == "recipe_000052":
        if locale == "en":
            ingredients[6]["name"] = (
                "Cold, thick Japanese curry (with potatoes, carrots and minced meat)"
            )
            ingredients[1]["name"] = "dry baker's yeast"
            steps[12]["instruction"] = "Drain on paper towels and serve hot."
        elif locale == "pt":
            ingredients[6]["name"] = (
                "Caril japonês espesso e bem frio (com batata, cenoura e carne picada)"
            )
    return {
        "title": candidate["title"],
        "description": candidate["description"],
        "animeContext": candidate["animeContext"],
        "ingredients": {
            x["id"].rstrip("_"): {"name": x["name"], "note": x.get("note")}
            for x in ingredients
        },
        "steps": {x["id"]: x["instruction"] for x in steps},
    }


def italian(source: dict, former: dict) -> dict:
    return {
        "title": source["title"],
        "description": source["description"],
        "animeContext": former["animeContext"],
        "ingredients": {
            x["id"].rstrip("_"): {"name": x["name"], "note": x.get("note")}
            for x in source["ingredients"]
        },
        "steps": {x["id"]: x["instruction"] for x in source["steps"]},
    }


def reconstruct(existing: dict, source: dict, candidates: dict) -> dict:
    if existing["id"] != source["id"] or existing["status"] != "published":
        raise ValueError("Unexpected identity or status")
    if existing.get("imageAssetId") is not None:
        raise ValueError("Artwork present: contentVersion requires semantic asset review")
    new = dict(existing)
    new["sourceNote"] = (existing.get("sourceNote") or "") + " F3K_F3L_SOURCE_LOCKED_FAST_TRACK_20261119."
    new["contentVersion"] = max(
        existing["contentVersion"] + 1, source["targetContentVersion"]
    )
    new["servings"] = source["servings"]
    new["difficulty"] = source["difficulty"]
    new["prepMinutes"] = source["times"]["prepMinutes"]
    new["cookMinutes"] = source["times"]["sourceCookMinutes"]
    new["ingredients"] = [
        {"id": x["id"].rstrip("_"), "quantity": x["quantity"], "unit": x["unit"]}
        for x in source["ingredients"]
    ]
    new["steps"] = [
        {"id": x["id"], "timerSeconds": x["timerSeconds"]}
        for x in source["steps"]
    ]
    new["animeReferences"] = [
        {
            "workTitle": x["workTitle"],
            "relation": x["relation"],
            "season": x.get("season"),
            "episode": x.get("episode"),
            "chapter": x.get("chapter"),
        }
        for x in source["animeReview"]["references"]
    ]
    verify = dict(new["editorialVerification"])
    verify["culinaryStatus"] = "corrected"
    verify["culinaryNote"] = (
        "AI-assisted Fast Track: detailed Italian method and source-locked "
        "locale candidates were reconciled with matching ingredient IDs, "
        "quantities, step IDs and timers. This is not a professional or "
        "physical cooking certification."
    )
    verify["animeStatus"] = (
        "verified" if any(
            x["relation"] == "verified_appearance"
            for x in new["animeReferences"]
        ) else "unverified"
    )
    verify["animeNote"] = (
        "Associations derive from the source review; 'inspired' never "
        "claims a verified on-screen recipe."
    )
    new["editorialVerification"] = verify
    new["locales"] = {
        **existing["locales"],
        "it": italian(source, existing["locales"]["it"]),
        **{
            locale: translate(source, candidates[locale], locale)
            for locale in LOCALES
        },
    }
    return new


def main() -> int:
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true")
    action.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    source = read(ROOT / "authoring/f3k_it_hardening_51_162.json")
    packs = {
        l: read(
            ROOT / "authoring/f3l_review_drafts" /
            f"f3l_{l}_51_162_review_draft.json"
        ) for l in LOCALES
    }
    for locale in LOCALES:
        errors = inspect(source, packs[locale])
        if errors:
            raise SystemExit(
                f"{locale}: source-locked structural errors: {errors[:12]}"
            )
    source_by_id = {x["id"]: x for x in source["recipes"]}
    targets = [
        f"recipe_{n:06d}" for n in range(51, 163) if n not in HOLD
    ]
    if len(targets) != 100 or len(source_by_id) != 112:
        raise SystemExit("Unexpected target count or source identity")
    translations = {
        l: {r["id"]: r for r in packs[l]["recipes"]}
        for l in LOCALES
    }
    changed = []
    source_steps = 0
    locale_methods = 0
    for rid in targets:
        path = ROOT / "authoring/recipes" / f"{rid}.json"
        old = read(path)
        src = source_by_id[rid]
        if old["contentVersion"] >= src["targetContentVersion"] and len(
            old["steps"]
        ) == len(src["steps"]):
            # Already imported: safe to re-run without increasing versions.
            continue
        locales = {l: translations[l][rid] for l in LOCALES}
        new = reconstruct(old, src, locales)
        if len(new["steps"]) != len(src["steps"]):
            raise SystemExit(f"{rid}: lost method steps")
        if args.apply:
            write(path, new)
        changed.append(rid)
        source_steps += len(src["steps"])
        locale_methods += sum(
            len(new["locales"][l]["steps"]) for l in ("it", *LOCALES)
        )
    report = {
        "scope": {"from": "recipe_000051", "to": "recipe_000162", "existing": 112},
        "phase": "FAST_TRACK_CANDIDATE_NOT_LANGUAGE_OR_SAFETY_CERTIFIED",
        "promotedRecipeIds": targets,
        "eligibleCount": len(targets),
        "newChangesThisExecution": len(changed),
        "italianDetailedStepsInChangedRecords": source_steps,
        "allLocaleMethodStepsInChangedRecords": locale_methods,
        "hold": {
            f"recipe_{n:06d}": reason for n, reason in sorted(HOLD.items())
        },
        "holdCount": len(HOLD),
        "batches": [
            {"from": "recipe_000051", "to": "recipe_000150", "size": 100},
            {"from": "recipe_000151", "to": "recipe_000162", "size": 12},
        ],
        "caution": (
            "Source-locked multilingual staging improves methods but does not "
            "prove complete contextual translation accuracy. The HOLD group "
            "keeps concrete food-safety and factual risks out of this update. "
            "Run compiler, QA, tests and exact-head CI before any merge."
        ),
    }
    if args.apply:
        # Import includes compiled runtime assets, not just authoring sources.
        # CI invokes compile_recipe_catalog.py immediately after this step.
        write(ROOT / "docs/f3l_editorial/FAST_TRACK_PROMOTION_2026-11-19.json",
              report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
