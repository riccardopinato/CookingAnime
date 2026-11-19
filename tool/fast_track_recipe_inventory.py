#!/usr/bin/env python3
"""Read-only Fast Track inventory of existing Cooking Anime recipe translations.

A record is not accepted merely because its schema says "published".
This checks obvious template text and Italian leakage; it does not certify cuisine,
copyright, anime appearances or food safety. No new recipe IDs are generated.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

LOCALES = ("it", "en", "es", "fr", "de", "pt")
FIRST_PENDING, LAST_PENDING = 51, 162
# These are existing runtime phrases, not language-model guesses.
BOILERPLATE = {
    "en": ("prepare the broth or seasoning base first", "prepare the filling or main ingredient", "cook the main component"),
    "es": ("prepara todos los componentes de la receta antes de aplicar calor", "cocina el elemento principal"),
    "fr": ("préparez tous les éléments de la recette avant de", "faites cuire l'élément principal"),
    "de": ("bereite alle zutaten vor", "gare die hauptzutat"),
    "pt": ("prepare todos os componentes da receita antes de", "cozinhe o elemento principal"),
}
# Narrow lexical witnesses of Italian text embedded in non-Italian translations.
ITALIAN_LEAK = re.compile(
    r"\b(?:tiepido|ammorbidito|tritata|marinate|giapponese denso|in polvere|"
    r"erba cipollina|sale marino fine|alga kelp salata)\b", re.IGNORECASE
)

def inventory(root: Path) -> dict:
    packs = {}
    for locale in LOCALES:
        data = json.loads((root / "assets/catalog/locales" / f"{locale}.json").read_text(encoding="utf-8"))
        if data.get("locale") != locale or not isinstance(data.get("recipes"), dict):
            raise ValueError(f"Invalid locale pack: {locale}")
        packs[locale] = data["recipes"]
    canonical = json.loads((root / "assets/catalog/recipes.json").read_text(encoding="utf-8"))["recipes"]
    ids = {entry["id"] for entry in canonical}
    pending = [f"recipe_{number:06d}" for number in range(FIRST_PENDING, LAST_PENDING + 1)]
    if not set(pending).issubset(ids):
        raise ValueError("Existing canonical recipe range 51-162 is incomplete")
    rows = []
    for recipe_id in pending:
        issues = []
        for locale in LOCALES:
            entry = packs[locale].get(recipe_id)
            if not isinstance(entry, dict):
                issues.append({"locale": locale, "kind": "missing_locale_record"})
                continue
            if not entry.get("title") or not entry.get("description"):
                issues.append({"locale": locale, "kind": "missing_editorial_copy"})
            ingredients = entry.get("ingredientTexts", {})
            steps = entry.get("stepTexts", {})
            if not ingredients or not steps:
                issues.append({"locale": locale, "kind": "missing_method_or_ingredients"})
                continue
            text = " ".join(str(v) for v in steps.values()).casefold()
            if any(phrase in text for phrase in BOILERPLATE.get(locale, ())):
                issues.append({"locale": locale, "kind": "generic_non_specific_method"})
            if locale != "it":
                ingredient_text = " ".join(str(v.get("name", "")) for v in ingredients.values() if isinstance(v, dict))
                if ITALIAN_LEAK.search(ingredient_text + " " + text):
                    issues.append({"locale": locale, "kind": "italian_lexical_leak"})
        rows.append({"id": recipe_id, "status": "NEEDS_AI_REVIEW" if issues else "CANDIDATE_FOR_CONTEXTUAL_REVIEW", "issues": issues})
    by_kind = {}
    for row in rows:
        for item in row["issues"]:
            key = item["locale"] + ":" + item["kind"]
            by_kind[key] = by_kind.get(key, 0) + 1
    return {
        "scope": {"first": pending[0], "last": pending[-1], "recipes": len(rows), "locales": list(LOCALES)},
        "status": "TRIAGE_ONLY_NO_EDITORIAL_CERTIFICATION",
        "needs_ai_review": sum(row["status"] == "NEEDS_AI_REVIEW" for row in rows),
        "contextual_review_candidates": sum(row["status"] == "CANDIDATE_FOR_CONTEXTUAL_REVIEW" for row in rows),
        "issue_counts": dict(sorted(by_kind.items())),
        "recipes": rows,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    report = inventory(args.root)
    result = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result, encoding="utf-8")
    else:
        print(result, end="")

if __name__ == "__main__":
    main()
