#!/usr/bin/env python3
"""Cooking Anime -> App Factory Semantic QA v1 adapter (READ-ONLY).

Source of truth: authoring/recipes/recipe_*.json, not generated assets.
English/Spanish/French/German/Portuguese compare against Italian master.
Only public editorial recipe text may be sent to a remote provider, and only
with explicit separate opt-in in the central engine. No source mutation here.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "build/semantic_qa/cooking_anime_input.json"
LOCALES = ("en", "es", "fr", "de", "pt")

def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def text_fields(content: dict) -> dict:
    if not isinstance(content, dict):
        raise ValueError("Missing locale payload")
    return {
        "title": content.get("title") or "",
        "description": content.get("description") or "",
        "animeContext": content.get("animeContext") or "",
        "ingredients": {
            k: v.get("name") or ""
            for k, v in sorted(content.get("ingredients", {}).items())
        },
        "steps": dict(sorted(content.get("steps", {}).items())),
    }

def collect(root: Path = ROOT) -> dict:
    paths = sorted((root / "authoring/recipes").glob("recipe_*.json"))
    if len(paths) != 162:
        raise ValueError(f"Expected 162 canonical authoring recipes; found {len(paths)}")
    records = []
    seen = set()
    for path in paths:
        recipe = load(path)
        rid = recipe.get("id")
        if not isinstance(rid, str) or rid in seen or path.stem != rid:
            raise ValueError(f"Duplicate/mismatched canonical recipe: {path}")
        seen.add(rid)
        if recipe.get("status") != "published":
            raise ValueError(f"Unpublished recipe in canonical catalog: {rid}")
        locales = recipe.get("locales", {})
        source = text_fields(locales["it"])
        translations = {lang: text_fields(locales[lang]) for lang in LOCALES
                        if isinstance(locales.get(lang), dict)}
        records.append({
            "id": rid,
            "source": source,
            "translations": translations,
            "protectedTerms": [],
            "sourceRefs": [],
            "context": {
                "contentVersion": recipe.get("contentVersion"),
                "servings": recipe.get("servings"),
                "prepMinutes": recipe.get("prepMinutes"),
                "cookMinutes": recipe.get("cookMinutes"),
                "ingredients": [
                    {"id": x.get("id"), "quantity": x.get("quantity"),
                     "unit": x.get("unit")} for x in recipe["ingredients"]
                ],
                "timers": [
                    {"id": x.get("id"), "timerSeconds": x.get("timerSeconds")}
                    for x in recipe["steps"]
                ],
                "animeReferences": recipe.get("animeReferences", []),
            },
        })
    return {
        "schemaVersion": 1,
        "adapter": "cooking_anime",
        "privacy": "PUBLIC_EDITORIAL",
        "sourceLocale": "it",
        "targetLocales": list(LOCALES),
        "domainRubric": (
            "Cooking Anime. Verify source-bound ingredient identities and "
            "quantities, execution order, verbs and their objects, refrigeration, "
            "raw fish or eggs, shellfish rejection, time and temperature, food "
            "safety instructions, allergen terms, and anime attribution. "
            "Never invent professional chef certification or missing facts."
        ),
        "records": records,
    }

def verify_report(report: dict, count: int = 162) -> dict:
    if report.get("adapter") != "cooking_anime":
        raise ValueError("Wrong adapter report")
    if report.get("recordCount") != count or report.get("comparisonCount") != count*5:
        raise ValueError("Not all 162 x 5 translation comparisons were inspected")
    if report.get("certification") != "NOT_CERTIFIED":
        raise ValueError("Report overclaims semantic certification")
    found = [x for x in report.get("results", []) if x["state"] == "HOLD"]
    return {"totalRecipes": count, "translations": count*5,
            "blockingStructuralHolds": len(found),
            "unresolvedHolds": [{"id": x["id"], "locale": x["locale"]}
                                for x in found]}

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, default=INPUT)
    p.add_argument("--verify-report", type=Path)
    args = p.parse_args()
    if args.verify_report:
        summary = verify_report(load(args.verify_report))
        print(json.dumps(summary, ensure_ascii=False))
        return 2 if summary["blockingStructuralHolds"] else 0
    result = collect()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+"\n",
                           encoding="utf-8")
    print(json.dumps({"adapter": "cooking_anime", "records": len(result["records"]),
                      "translations": len(result["records"])*5}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
