#!/usr/bin/env python3
"""Cooking Anime: source-locked *structural* full catalog audit, not semantic certification."""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("it", "en", "es", "fr", "de", "pt")
NUMBER = re.compile(r"(?<![\w])\d+(?:[.,]\d+)?")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def anchors(value: str):
    # Advisory only: words such as 'four' may legitimately replace numerals.
    return sorted(match.group().replace(",", ".") for match in NUMBER.finditer(value))


def run(root: Path = ROOT):
    catalog = load(root / "assets/catalog/recipes.json")
    recipes = catalog["recipes"]
    packs = {l: load(root / f"assets/catalog/locales/{l}.json") for l in LOCALES}
    authors = sorted((root / "authoring/recipes").glob("recipe_*.json"))
    errors = []
    warnings = []
    if len(recipes) != 162 or len(authors) != 162:
        errors.append({"code": "CATALOG_SIZE", "source": len(authors), "runtime": len(recipes)})
    by_id = {r["id"]: r for r in recipes}
    if len(by_id) != len(recipes):
        errors.append({"code": "DUPLICATE_RECIPE"})
    if any(len(p["recipes"]) != 162 for p in packs.values()):
        errors.append({"code": "LOCALE_PACK_COUNT"})
    field_checks = 0
    step_count = 0
    ingredient_count = 0
    step_timer_count = 0
    for path in authors:
        r = load(path)
        rid = r["id"]
        if rid != path.stem or rid not in by_id:
            errors.append({"code": "SOURCE_ID_MISMATCH", "id": rid})
            continue
        runtime = by_id[rid]
        if r["status"] != "published" or r["contentVersion"] != runtime["contentVersion"]:
            errors.append({"code": "PUBLISH_VERSION", "id": rid})
        for key in ("ingredients", "steps", "animeReferences", "prepMinutes",
                    "cookMinutes", "servings", "difficulty", "status"):
            field_checks += 1
            if r[key] != runtime[key]:
                errors.append({"code": "CANONICAL_DRIFT", "id": rid, "field": key})
        ing = {entry["id"] for entry in r["ingredients"]}
        steps = {entry["id"] for entry in r["steps"]}
        ingredient_count += len(ing)
        step_count += len(steps)
        step_timer_count += sum(entry.get("timerSeconds") is not None for entry in r["steps"])
        for entry in r["steps"]:
            if entry.get("timerSeconds") is not None:
                # May be rest/marinade time, not active cooking: REVIEW only.
                if entry["timerSeconds"] > 60 * (r["prepMinutes"] + r["cookMinutes"]):
                    warnings.append({"code": "STEP_TIMER_EXCEEDS_TOTAL", "id": rid,
                                     "step": entry["id"], "seconds": entry["timerSeconds"],
                                     "metaMinutes": r["prepMinutes"] + r["cookMinutes"]})
        for locale in LOCALES:
            live = packs[locale]["recipes"].get(rid)
            source = r["locales"].get(locale)
            if not live or not source:
                errors.append({"code": "MISSING_LOCALE", "id": rid, "locale": locale})
                continue
            for sourceKey, targetKey in (("title", "title"),
                                         ("description", "description"),
                                         ("animeContext", "animeContext"),
                                         ("ingredients", "ingredientTexts"),
                                         ("steps", "stepTexts")):
                field_checks += 1
                if source[sourceKey] != live[targetKey]:
                    errors.append({"code": "LOCALE_SOURCE_RUNTIME_DRIFT", "id": rid,
                                   "locale": locale, "field": sourceKey})
            if set(live["ingredientTexts"]) != ing or set(live["stepTexts"]) != steps:
                errors.append({"code": "LOCALE_KEY_MISMATCH", "id": rid, "locale": locale})
            for key in ("title", "description", "animeContext"):
                field_checks += 1
                if not live[key].strip():
                    errors.append({"code": "EMPTY_LOCALE_PROSE", "id": rid,
                                   "locale": locale, "field": key})
            for key in ing:
                field_checks += 1
                if not live["ingredientTexts"][key]["name"].strip():
                    errors.append({"code": "EMPTY_INGREDIENT", "id": rid, "locale": locale,
                                   "field": key})
            for key in steps:
                field_checks += 1
                if not live["stepTexts"][key].strip():
                    errors.append({"code": "EMPTY_STEP", "id": rid, "locale": locale,
                                   "field": key})
            if locale != "it":
                original = packs["it"]["recipes"].get(rid)
                if original:
                    for key in steps:
                        a = original["stepTexts"][key]
                        b = live["stepTexts"][key]
                        if anchors(a) != anchors(b):
                            warnings.append({"code": "NUMERIC_ANCHOR_REVIEW", "id": rid,
                                             "locale": locale, "step": key,
                                             "sourceAnchors": anchors(a),
                                             "targetAnchors": anchors(b)})
    en = load(root / "lib/l10n/app_en.arb")
    baseline = {k for k in en if not k.startswith("@")}
    ui_keys = {}
    for locale in LOCALES:
        ui = load(root / f"lib/l10n/app_{locale}.arb")
        keys = {k for k in ui if not k.startswith("@")}
        ui_keys[locale] = len(keys)
        if keys != baseline:
            errors.append({"code": "UI_ARB_KEY_MISMATCH", "locale": locale,
                           "missing": sorted(baseline - keys),
                           "extra": sorted(keys - baseline)})
    return {
        "report": "COOKING_162_FULL_STRUCTURAL_QA",
        "source": "authoring/recipes",
        "sourceRecipes": len(authors),
        "canonicalRuntimeRecipes": len(recipes),
        "localeCounts": {l: len(packs[l]["recipes"]) for l in LOCALES},
        "uiArbKeys": ui_keys,
        "sourceSteps": step_count,
        "sourceIngredients": ingredient_count,
        "stepTimers": step_timer_count,
        "structuralFieldChecks": field_checks,
        "blockingErrors": errors,
        "reviewWarnings": warnings,
        "warningCounts": dict(sorted(Counter(w["code"] for w in warnings).items())),
        "editorialCertification": "NOT_CERTIFIED",
        "physicalDeviceVerification": "NOT_VERIFIED",
        "mode": "READ_ONLY_OFFLINE",
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = run()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: report[k] for k in (
        "sourceRecipes", "localeCounts", "uiArbKeys", "structuralFieldChecks",
        "warningCounts", "editorialCertification")}, ensure_ascii=False))
    if report["blockingErrors"]:
        print(f"STRUCTURAL FAIL: {len(report['blockingErrors'])} blocking errors")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
