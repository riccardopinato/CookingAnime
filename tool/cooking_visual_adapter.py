#!/usr/bin/env python3
"""Cooking Anime domain adapter for reusable Visual Batch Engine.

This planning-only adapter skips current version-bound approved artworks.
It does not generate images, approve assets, or issue network requests.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from visual_batch_engine import plan_items, reference_profile

ROOT = Path(__file__).resolve().parents[1]
PILOT_IDS = (51, 53, 56, 57, 60, 63, 74, 83, 86, 108, 134, 162)

# Explicitly witnessed from the Italian authoring titles and ingredients:
# these are visual intentions, not a model-generated proof of plate fidelity.
VISUAL_FACTS = {
    51: (["shio ramen in a bowl with clear salt-seasoned broth", "ramen noodles",
          "chashu pork, seasoned bamboo shoots, marinated egg and nori"],
         ["opaque tonkotsu broth", "unrelated curry or fried rice"]),
    53: (["ebi tendon: golden shrimp tempura over a bowl of white rice",
          "crisp light tempura batter, tentsuyu glaze"],
         ["uncooked shrimp", "fried chicken instead of shrimp"]),
    56: (["chirashizushi: broad sushi-rice platter with separate colorful toppings",
          "fish, cooked shrimp, thin vegetables and egg strips"],
         ["sushi rolls", "ramen soup"]),
    57: (["kurogoma dango: small round Japanese rice dumplings",
          "recognizable dark roasted black sesame coating"],
         ["chocolate truffles", "squid-ink spaghetti"]),
    60: (["Japanese castella sponge cake", "golden rectangular cake slices with airy fine crumb"],
         ["frosted layer cake", "pancakes or bread loaf"]),
    63: (["tenshinhan: fluffy crab omelette over a mound of steamed rice",
          "glossy sweet-and-sour sauce"],
         ["flat okonomiyaki", "shrimp tempura"]),
    74: (["oden stew in a bowl of clear broth",
          "distinct daikon slices, cooked eggs and assorted oden pieces"],
         ["ramen noodles", "spicy curry soup"]),
    83: (["tsukemen dipping noodles: thick chilled noodles on a plate",
          "concentrated steaming dipping broth in a separate bowl",
          "chashu, marinated egg and nori arranged beside the noodles"],
         ["noodles submerged in a single ramen soup", "solid sauce without dipping broth"]),
    86: (["tall airy Japanese souffle pancakes in a soft stack",
          "thick cloudlike rounded pancake layers"],
         ["thin crepes", "regular flat American pancakes"]),
    108: (["tonkotsu ramen with dense creamy opaque pork broth",
           "ramen noodles and chashu in a deep ramen bowl"],
          ["clear salt-only shio broth", "pasta with cream sauce"]),
    134: (["shirasu don: a rice bowl with many tiny whitebait fish",
           "a recognizably small fish garnish and egg as described by the recipe"],
          ["giant prawns", "sardine steaks", "vegetarian vegetable bowl"]),
    162: (["pale citrus yuzu sorbet served cold as a frozen dessert",
           "light airy scoops in a small serving cup"],
          ["cheesecake", "orange soup", "large whole fruits replacing sorbet"]),
}

STYLE = (
    "Create ONE original premium anime-inspired FOOD illustration, consistent "
    "with the approved Cooking Anime 1-50 culinary art collection. "
    "Close food-first framing, warm appetizing light, painterly highlights, "
    "delicious glossy textures, crisp readable silhouette, minimal background, "
    "balanced plate geometry, restrained editorial Japanese-contemporary feel. "
    "Match overall art direction, not any protected animation studio or character."
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build(root: Path = ROOT, *, pilot_only: bool = True) -> dict:
    manifest = load_json(root / "authoring/assets/manifest.json")
    approved = [asset for asset in manifest["assets"]
                if asset.get("semanticReview", {}).get("status") == "approved"]
    refs = sorted(asset["path"] for asset in approved
                  if asset["recipeId"].split("_")[-1].isdigit()
                  and 1 <= int(asset["recipeId"].split("_")[-1]) <= 50)
    if len(refs) != 50 or len(set(refs)) != 50:
        raise ValueError(f"expected exactly 50 approved, distinct reference assets, found {len(refs)}")
    adapter = {
        "adapterId": "cooking_anime_v1",
        "referencePaths": refs,
        "assetPolicy": manifest["policy"],
        "styleDirective": STYLE,
        "variantsPerRecipe": 2,
    }
    profile = reference_profile(root, adapter)
    targets = PILOT_IDS if pilot_only else tuple(range(51, 163))
    integrated_in_catalog = {
        a["recipeId"] for a in manifest["assets"]
        if 51 <= int(a["recipeId"].split("_")[-1]) <= 162
        and a["semanticReview"]["status"] == "approved"
    }
    skipped_integrated = []
    specs = []
    for number in targets:
        recipe_id = f"recipe_{number:06d}"
        recipe = load_json(root / f"authoring/recipes/{recipe_id}.json")
        if recipe["id"] != recipe_id or recipe.get("status") != "published":
            raise ValueError(f"invalid canonical recipe: {recipe_id}")
        if recipe.get("imageAssetId") is not None:
            asset = next((a for a in manifest["assets"]
                          if a["id"] == recipe["imageAssetId"]
                          and a["recipeId"] == recipe_id), None)
            if (asset is None or asset["semanticReview"]["status"] != "approved"
                    or asset["semanticReview"]["reviewedContentVersion"]
                       != recipe["contentVersion"]):
                raise ValueError(f"stale/missing approved artwork: {recipe_id}")
            skipped_integrated.append(recipe_id)
            continue
        localized = recipe["locales"]["it"]
        visual = VISUAL_FACTS.get(number)
        if visual:
            positive, negative = visual
        else:
            positive = [
                f"the exact finished dish from its Italian canonical title: {localized['title']}",
                "composition to be confirmed against ingredient and step-level source facts",
            ]
            negative = [
                "a visually similar but different dish",
                "any garnish or hero component that contradicts canonical ingredients",
            ]
        specs.append({
            "id": recipe_id,
            "title": localized["title"],
            "contentVersion": recipe["contentVersion"],
            "ingredientNames": [
                localized["ingredients"][entry["id"]]["name"]
                for entry in recipe["ingredients"]
            ],
            "visualFacts": {"positive": positive, "negative": negative},
            "domainReview": "SOURCE_GROUNDED_PILOT" if visual else "REQUIRES_DOMAIN_REVIEW",
            "sourceStepCount": len(recipe["steps"]),
        })
    output = plan_items(adapter, profile, specs)
    output["domain"] = "food_recipe"
    output["assetPolicy"] = adapter["assetPolicy"]
    output["styleProfile"] = profile
    output["pilotIds"] = [f"recipe_{n:06d}" for n in PILOT_IDS]
    output["skippedAlreadyIntegrated"] = skipped_integrated
    output["catalogAlreadyIntegrated"] = len(integrated_in_catalog)
    output["requiresDomainReview"] = sum(
        x["domainReview"] == "REQUIRES_DOMAIN_REVIEW" for x in specs
    )
    output["sourceBoundFacts"] = {spec["id"]: spec["visualFacts"] for spec in specs}
    output["claims"] = {
        "styleReferenceFilesVerified": len(refs),
        "semanticImageRecognition": "NOT_RUN",
        "imageGeneration": "NOT_RUN",
        "imagesIntegrated": len(integrated_in_catalog),
        "copyright": "original imagery only; no existing anime stills or characters",
    }
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--all", action="store_true", help="Plan 112 recipes, no generation")
    parser.add_argument("--output", type=Path, default=ROOT / "build/visual_batch/cooking_pilot.json")
    args = parser.parse_args()
    result = build(args.root, pilot_only=not args.all)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "referenceCount": result["styleProfile"]["referenceCount"],
        "requests": result["count"],
        "domainReviewNeeded": result["requiresDomainReview"],
        "imagesGenerated": result["imagesGenerated"],
        "imagesIntegrated": result["claims"]["imagesIntegrated"],
        "output": str(args.output),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
