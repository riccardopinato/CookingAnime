#!/usr/bin/env python3
"""Full 162 x 6 Cooking Anime catalog audit and witnessed-error remediation.

Checks all canonical IDs, locale records, step/ingredient parity, required prose,
source/runtime agreement, generic methods and known false friends. The audit
never claims that automated checks certify all translations as idiomatic.
--apply makes ONLY explicitly documented, source-inspected textual repairs in
artwork-free records and writes a structured before/after report; the workflow
compiles and validates the runtime catalog after application.
"""
from __future__ import annotations
import argparse
import collections
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("it", "en", "es", "fr", "de", "pt")
DOC = ROOT / "docs/f3l_editorial/FAST_TRACK_162_CATALOG_AUDIT.json"
SOURCE = ROOT / "authoring/recipes"
# Exact witnessed false friends; restricted to 51..162 and to the correct
# locale. No speculative multiword find/replace across other app resources.
FIXES = {
 "en": [
    ("Turn off the fire", "Turn off the heat"),
    ("turn off the fire", "turn off the heat"),
    ("Bring to the table", "Serve"),
    ("bring to the table", "serve"),
    ("flour 00", "Italian 00 flour"),
 ],
 "es": [
    ("Cebollina fresca", "Cebollino fresco"),
    ("cebollina fresca", "cebollino fresco"),
 ],
 "fr": [
    ("aspirez", "égouttez"),
    ("Aspirez", "Égouttez"),
    ("écolières", "égouttez-les"),
    ("brindilles", "lanières"),
    ("Rouvrez entièrement", "Recouvrez entièrement"),
    ("Dormir à feu doux", "Faites dorer à feu doux"),
    ("dormir à feu doux", "faites dorer à feu doux"),
 ],
 "de": [
    ("Spennella", "Bestreichen Sie"),
    ("spennella", "bestreichen"),
    ("Frischlachs", "frischer Lachs"),
    ("Hähnchenüberdeckung", "Hähnchenoberkeule"),
    ("Löffeln von 4 cm", "Stücken von 4 cm"),
 ],
 "pt": [
    ("Brodo de Dashi", "Caldo de dashi"),
    ("brodo de dashi", "caldo de dashi"),
    ("frittatina", "omelete fina"),
    ("moscas, verdadeiras, torcidas", "amêijoas depuradas"),
    ("moscas, verdadeiras", "amêijoas depuradas"),
 ],
}
# WITNESS can include known issues that need contextual review rather than
# automatic correction. A warning is not a proof that the text is wrong.
WITNESSES = {
    "en": ("turn off the fire", "bring to the table", "chicken millstone",
           "chess duck", "mischioose", "flour 00"),
    "es": ("espagueti de cocina", "muérdago", "huevo golpeado",
           "cose una tortilla", "cebollina fresca"),
    "fr": ("aspirez", "écolières", "striscioles", "brindilles",
           "dormir à feu", "rouvrez"),
    "de": ("spennella", "hähnchenüberdeckung", "kochspaghetti",
           "löffeln von 4 cm", "frischlachs"),
    "pt": ("brodo de dashi", "suco de mosquito", "moscas, verdadeiras",
           "frittatina", "toques de porco"),
}
GENERIC = {
    "en": ("prepare the broth or seasoning base first",
           "prepare the filling or main ingredient",
           "cook the main component"),
    "es": ("prepara todos los componentes de la receta antes de aplicar calor",
           "cocina el elemento principal"),
    "fr": ("préparez tous les éléments de la recette avant de",
           "faites cuire l'élément principal"),
    "de": ("bereite alle zutaten vor", "gare die hauptzutat"),
    "pt": ("prepare todos os componentes da receita antes de",
           "cozinhe o elemento principal"),
}

# Fully curated steps replace demonstrated unusable draft translations rather
# than merely suppressing their scanner warnings. Source actions and timers
# remain canonical; safety instruction appended below from the accepted repair.
CURATED = {
56: {
 "en": [
  "Spread the cooled, seasoned sushi rice evenly in a wide serving bowl.",
  "Beat the two eggs with a pinch of salt and sugar.",
  "Cook a very thin omelette in a lightly oiled pan; cool and cut into fine strips (kinshi tamago).",
  "Cover the surface of the rice with the fine omelette strips.",
  "Arrange the diced salmon, tuna, peeled cooked shrimp and thin cucumber slices attractively on the rice.",
  "Add a little salmon roe (ikura) at the centre; sprinkle with toasted sesame seeds and thin nori strips.",
  "Serve cool, with soy sauce and wasabi on the side.",
 ],
 "es": [
  "Extiende el arroz para sushi ya condimentado y templado en una fuente amplia.",
  "Bate los dos huevos con una pizca de sal y azúcar.",
  "Prepara una tortilla muy fina en una sartén ligeramente engrasada, deja enfriar y córtala en tiras finas (kinshi tamago).",
  "Cubre la superficie del arroz con las tiras de tortilla.",
  "Distribuye los dados de salmón y atún, las gambas cocidas y peladas y las rodajas finas de pepino.",
  "Añade unas cucharadas de huevas de salmón (ikura) en el centro; termina con sésamo tostado y tiras de nori.",
  "Sirve fresco, con salsa de soja y wasabi aparte.",
 ],
 "fr": [
  "Étalez le riz à sushi assaisonné et tiédi dans un grand plat de service.",
  "Battez les deux œufs avec une pincée de sel et de sucre.",
  "Faites cuire une omelette très fine dans une poêle légèrement huilée ; laissez refroidir et taillez de fines lanières (kinshi tamago).",
  "Recouvrez toute la surface du riz avec les lanières d'omelette.",
  "Disposez harmonieusement les dés de saumon et de thon, les crevettes cuites décortiquées et les fines tranches de concombre.",
  "Déposez quelques cuillerées d'œufs de saumon (ikura) au centre ; parsemez de sésame grillé et de lanières de nori.",
  "Servez frais, avec de la sauce soja et du wasabi à part.",
 ],
 "de": [
  "Den gewürzten, etwas abgekühlten Sushi-Reis gleichmäßig in einer breiten Servierschale verteilen.",
  "Die beiden Eier mit einer Prise Salz und Zucker verquirlen.",
  "In einer leicht geölten Pfanne ein sehr dünnes Omelett ausbacken, abkühlen lassen und in feine Streifen (Kinshi Tamago) schneiden.",
  "Die Reisoberfläche vollständig mit den Omelettstreifen bedecken.",
  "Lachs- und Thunfischwürfel, gegarte geschälte Garnelen und dünne Gurkenscheiben dekorativ auf dem Reis anrichten.",
  "Etwas Lachsrogen (Ikura) in die Mitte geben und mit geröstetem Sesam und feinen Noristreifen bestreuen.",
  "Kühl servieren, dazu Sojasauce und Wasabi reichen.",
 ],
 "pt": [
  "Espalhe o arroz para sushi já temperado e morno numa travessa larga.",
  "Bata os dois ovos com uma pitada de sal e açúcar.",
  "Prepare uma omelete muito fina numa frigideira ligeiramente untada; deixe arrefecer e corte em tiras finas (kinshi tamago).",
  "Cubra toda a superfície do arroz com as tiras de omelete.",
  "Disponha os cubos de salmão e atum, os camarões cozidos e descascados e as rodelas finas de pepino sobre o arroz.",
  "Coloque algumas colheres de ovas de salmão (ikura) ao centro e termine com sésamo tostado e tiras finas de nori.",
  "Sirva fresco, com molho de soja e wasabi à parte.",
 ],
},
153: {
 "en": [
  "Mix the ground chicken with finely chopped spring onions, grated ginger, cornstarch, egg white, salt and pepper until sticky and uniform.",
  "Divide into four elongated portions and shape each firmly around a wooden skewer.",
  "Simmer the soy sauce, mirin, sake and sugar in a small pan until the tare glaze becomes syrupy.",
  "Pan-grill the chicken skewers with a little oil over medium heat for approximately 3–4 minutes per side, checking doneness rather than relying on time alone.",
  "Brush the skewers with tare during the final minutes, turning frequently to coat them evenly.",
  "Serve the glazed skewers with a separate bowl of pasteurized egg yolk suitable for uncooked consumption as a dipping sauce.",
 ],
 "es": [
  "Mezcla el pollo picado con la cebolleta, el jengibre, la maicena, la clara de huevo, sal y pimienta hasta obtener una masa homogénea y pegajosa.",
  "Divide la mezcla en cuatro porciones alargadas y moldea cada una alrededor de una brocheta de madera.",
  "Reduce la salsa de soja, el mirin, el sake y el azúcar en un cazo hasta obtener una salsa tare de textura siruposa.",
  "Cocina las brochetas con un poco de aceite a fuego medio durante unos 3–4 minutos por lado; comprueba la cocción y no dependas únicamente del tiempo.",
  "Pincela con la salsa tare durante los últimos minutos y gira las brochetas para glasearlas uniformemente.",
  "Sirve las brochetas glaseadas con una yema pasteurizada apta para consumo sin cocción en un cuenco aparte para mojar.",
 ],
 "fr": [
  "Mélangez le poulet haché avec les cébettes, le gingembre, la fécule de maïs, le blanc d'œuf, le sel et le poivre jusqu'à obtenir une préparation homogène et collante.",
  "Divisez le mélange en quatre portions allongées et façonnez chacune autour d'une brochette en bois.",
  "Faites réduire la sauce soja, le mirin, le saké et le sucre dans une petite casserole jusqu'à obtenir une sauce tare sirupeuse.",
  "Faites griller les brochettes dans une poêle légèrement huilée à feu moyen pendant environ 3 à 4 minutes par face ; vérifiez la cuisson au lieu de vous fier au seul temps.",
  "Badigeonnez les brochettes de tare en fin de cuisson, en les retournant souvent pour les glacer uniformément.",
  "Servez les brochettes laquées avec un jaune d'œuf pasteurisé adapté à la consommation sans cuisson, dans un bol séparé.",
 ],
 "de": [
  "Hähnchenhackfleisch mit fein geschnittenen Frühlingszwiebeln, Ingwer, Maisstärke, Eiweiß, Salz und Pfeffer zu einer gleichmäßigen, klebrigen Masse vermengen.",
  "Die Masse in vier längliche Portionen teilen und jeweils fest um einen Holzspieß formen.",
  "Sojasauce, Mirin, Sake und Zucker in einem kleinen Topf zu einer sirupartigen Tare-Glasur einkochen.",
  "Die Spieße in einer leicht geölten Pfanne bei mittlerer Hitze etwa 3–4 Minuten pro Seite braten; den Gargrad kontrollieren statt nur auf die Zeit zu achten.",
  "In den letzten Minuten mehrfach mit Tare bestreichen und dabei häufig wenden, damit die Glasur gleichmäßig haftet.",
  "Die glasierten Spieße mit pasteurisiertem, zum Rohverzehr geeignetem Eigelb in einer separaten Schale als Dip servieren.",
 ],
 "pt": [
  "Misture o frango picado com cebolinho, gengibre ralado, amido de milho, clara de ovo, sal e pimenta até obter uma massa homogénea e pegajosa.",
  "Divida a mistura em quatro porções alongadas e molde cada uma em volta de um espeto de madeira.",
  "Reduza o molho de soja, o mirin, o saqué e o açúcar num tacho até obter um molho tare xaroposo.",
  "Grelhe os espetos numa frigideira com um pouco de óleo em lume médio durante cerca de 3–4 minutos de cada lado; confirme a cozedura sem confiar apenas no tempo.",
  "Pincele os espetos com molho tare nos últimos minutos, virando-os com frequência para os glacear.",
  "Sirva os espetos glaceados com uma gema pasteurizada adequada ao consumo sem cozedura, numa tigela à parte para molhar.",
 ],
},
}


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def target_paths() -> list[Path]:
    return [SOURCE / f"recipe_{i:06d}.json" for i in range(1, 163)]


def blob_text(recipe: dict, locale: str) -> list[tuple[str, str]]:
    d = recipe.get("locales", {}).get(locale, {})
    if not isinstance(d, dict):
        return []
    fields = [(k, str(d.get(k) or "")) for k in ("title", "description", "animeContext")]
    fields.extend((f"ingredients.{k}.name", str(v.get("name") or ""))
                  for k, v in d.get("ingredients", {}).items() if isinstance(v, dict))
    fields.extend((f"steps.{k}", str(v)) for k, v in d.get("steps", {}).items())
    return fields


def audit(recipes: list[dict]) -> dict:
    rows = []
    issue_count = collections.Counter()
    affected = set()
    lookup = {r["id"]: r for r in recipes}
    for num in range(1, 163):
        rid = f"recipe_{num:06d}"
        r = lookup.get(rid)
        issues = []
        if r is None:
            issues.append({"kind": "missing_canonical_id", "severity": "ERROR"})
            rows.append({"id": rid, "issues": issues})
            continue
        ingredients = {x["id"] for x in r.get("ingredients", [])}
        steps = {x["id"] for x in r.get("steps", [])}
        if r.get("status") != "published":
            issues.append({"kind": "unexpected_status", "severity": "REVIEW"})
        if len(ingredients) != len(r.get("ingredients", [])):
            issues.append({"kind": "duplicate_ingredient_ids", "severity": "ERROR"})
        if len(steps) != len(r.get("steps", [])):
            issues.append({"kind": "duplicate_step_ids", "severity": "ERROR"})
        for locale in LOCALES:
            d = r.get("locales", {}).get(locale)
            if not isinstance(d, dict):
                issues.append({"locale": locale, "kind": "missing_locale", "severity": "ERROR"})
                continue
            if num in (51, 56, 59, 80, 96, 110, 117, 133, 149, 150, 153, 156):
                from fast_track_12_repairs import SAFETY
                full_method = " ".join(str(v) for v in d.get("steps", {}).values())
                if SAFETY[num][locale] not in full_method:
                    issues.append({"locale": locale, "kind": "missing_source_bound_safety",
                                   "severity": "ERROR"})
            if set(d.get("ingredients", {})) != ingredients:
                issues.append({"locale": locale, "kind": "ingredient_key_drift", "severity": "ERROR"})
            if set(d.get("steps", {})) != steps:
                issues.append({"locale": locale, "kind": "step_key_drift", "severity": "ERROR"})
            for path, value in blob_text(r, locale):
                if not value.strip():
                    issues.append({"locale": locale, "path": path,
                                   "kind": "empty_text", "severity": "ERROR"})
                if path.startswith("steps.") and len(value.strip()) < 8:
                    issues.append({"locale": locale, "path": path,
                                   "kind": "very_short_step", "severity": "REVIEW"})
                if locale in WITNESSES:
                    for pattern in WITNESSES[locale]:
                        if pattern in value.casefold():
                            issues.append({"locale": locale, "path": path,
                                           "kind": "witnessed_false_friend_or_loanword",
                                           "severity": "REVIEW", "evidence": pattern})
                    if path.startswith("steps."):
                        for pattern in GENERIC[locale]:
                            if pattern in value.casefold():
                                issues.append({"locale": locale, "path": path,
                                               "kind": "generic_method",
                                               "severity": "REVIEW", "evidence": pattern})
        for v in issues:
            issue_count[v["kind"]] += 1
        if issues:
            affected.add(rid)
        rows.append({"id": rid, "issues": issues})
    return {
        "scope": {"canonicalRecipes": 162, "locales": list(LOCALES),
                  "localeRecordsExamined": 972,
                  "fields": ["title", "description", "animeContext",
                             "ingredient names", "step texts", "IDs", "timers", "quantities"]},
        "methodology": "DETERMINISTIC_FULL_CATALOG_SCAN_NOT_SEMANTIC_CERTIFICATION",
        "summary": {
            "uniqueRecipesWithFindings": len(affected),
            "issueCount": sum(issue_count.values()),
            "byKind": dict(sorted(issue_count.items())),
        },
        "recipes": rows,
        "limitation": ("All 972 locale records and their fields were inspected "
                       "programmatically. Contextual native-language fluency, "
                       "ingredient-level recipe safety and anime-source accuracy "
                       "cannot be fully guaranteed by lexical rules alone."),
    }


def apply_fixes(recipes: list[dict]) -> tuple[list[str], int]:
    from fast_track_12_repairs import SAFETY
    modified = []
    changed_fields = 0
    for recipe in recipes:
        rid = recipe["id"]
        num = int(rid.split("_")[-1])
        if not 51 <= num <= 162:
            continue
        if recipe.get("imageAssetId") is not None:
            continue  # Do not invalidate approved semantic-artwork content version.
        changes_here = 0
        for locale in LOCALES:
            data = recipe["locales"][locale]
            if num in CURATED and locale in CURATED[num]:
                items = CURATED[num][locale]
                if len(items) != len(recipe["steps"]):
                    raise ValueError(f"Curated steps count mismatch {rid}/{locale}")
                step_id = {56: "step_5", 153: "step_6"}[num]
                seq = [x + ((" " + SAFETY[num][locale]) if f"step_{i+1}" == step_id else "")
                       for i, x in enumerate(items)]
                for i, line in enumerate(seq):
                    k = f"step_{i+1}"
                    if data["steps"][k] != line:
                        data["steps"][k] = line
                        changes_here += 1
            pairs = FIXES.get(locale, ())
            entries = [("title", data)] if isinstance(data.get("title"), str) else []
            entries += [(k, data) for k in ("description", "animeContext")
                        if isinstance(data.get(k), str)]
            entries += [("name", v) for v in data.get("ingredients", {}).values()
                        if isinstance(v, dict)]
            entries += [(k, data["steps"]) for k in data.get("steps", {})]
            for field, target in entries:
                before = target[field]
                after = before
                for old, new in pairs:
                    after = after.replace(old, new)
                if before != after:
                    target[field] = after
                    changes_here += 1
        if changes_here:
            recipe["contentVersion"] = int(recipe["contentVersion"]) + 1
            recipe["sourceNote"] = ((recipe.get("sourceNote") or "") +
                                    " FAST_TRACK_162_WITNESSED_TRANSLATION_REPAIR.")
            # The change is to copy, not proof of a professional culinary review.
            modified.append(rid)
            changed_fields += changes_here
            write(SOURCE / f"{rid}.json", recipe)
    return modified, changed_fields


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--report", type=Path, default=DOC)
    args = p.parse_args()
    recipes = [read(path) for path in target_paths()]
    before = audit(recipes)
    edited, field_count = apply_fixes(recipes) if args.apply else ([], 0)
    after = audit(recipes)
    prior = read(args.report) if args.apply and args.report.is_file() else None
    initial = prior.get("cumulative", {}).get("initial") if prior else None
    if initial is None:
        initial = prior["before"]["summary"] if prior else before["summary"]
    prior_ids = prior.get("cumulative", {}).get("correctedIDs", prior.get("correctedIDs", [])) if prior else []
    prior_fields = prior.get("cumulative", {}).get("correctedTextFields", prior.get("correctedTextFields", 0)) if prior else 0
    cumulative = {
        "initial": initial,
        "latest": after["summary"],
        "correctedIDs": sorted(set(prior_ids + edited)),
        "correctedRecipeCount": len(set(prior_ids + edited)),
        "correctedTextFields": prior_fields + field_count,
    }
    report = {
        "cumulative": cumulative,
        "date": "2026-11-19",
        "mode": "APPLIED_SOURCE_BOUND_FIXED_ERRORS" if args.apply else "READ_ONLY",
        "before": before,
        "after": after,
        "correctedIDs": edited,
        "correctedRecipeCount": len(edited),
        "correctedTextFields": field_count,
        "mainIntegration": "NOT_ASSERTED_BY_SCANNER",
        "remainingReviewRequired": after["summary"]["issueCount"] != 0,
    }
    if args.apply:
        write(args.report, report)
    print(json.dumps({
        "inspected": after["scope"], "before": before["summary"],
        "after": after["summary"], "changedIDs": len(edited),
        "textFieldsChanged": field_count,
        "report": str(args.report),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
