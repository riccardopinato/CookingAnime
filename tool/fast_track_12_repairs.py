#!/usr/bin/env python3
"""Source-bounded Fast Track errata for the 12 remaining Cooking Anime recipes.

This is a direct, inspectable patch set, not a blind machine translation.
Every safety addition is localized explicitly to all six app languages.
The frozen F3K/F3L review-draft source packs remain untouched; runtime
authoring stores the corrected accepted version.
"""
from __future__ import annotations

LOCALES = ("it", "en", "es", "fr", "de", "pt")
IDS = (51, 56, 59, 80, 96, 110, 117, 133, 149, 150, 153, 156)
# Approved guidance: USDA FSIS poultry 74C, FDA shellfish and raw seafood,
# FDA pasteurized eggs, UK FSA rice cooling/reheating, EU sanma species name.
REFERENCES = {
    "poultry": "https://ask.fsis.usda.gov/article/What-is-a-safe-internal-temperature-for-cooking-meat-and-poultry",
    "shellfish": "https://www.fda.gov/food/buy-store-serve-safe-food/selecting-and-serving-fresh-and-frozen-seafood-safely",
    "egg": "https://www.fda.gov/food/retail-food-industryregulatory-assistance-training/assuring-safety-eggs-and-menu-and-deli-items-made-raw-shell-eggs",
    "rice": "https://www.gov.uk/government/publications/home-food-fact-checker/home-food-fact-checker",
    "sanma": "https://fish-commercial-names.ec.europa.eu/fish-names/species/cololabis-saira_es",
}
# Add only recipe-specific actionable instructions; preserve all source steps.
SAFETY = {
  51: {
    "it": "Usa inizialmente solo mezzo cucchiaino di sale fino, assaggia il brodo prima di servirlo e regola eventualmente a piccole dosi: dashi, chashu e condimenti sono già sapidi.",
    "en": "Start with only half a teaspoon of fine salt. Taste the broth before serving and adjust sparingly; dashi, chashu and seasonings already contain salt.",
    "es": "Empieza con solo media cucharadita de sal fina. Prueba el caldo antes de servirlo y ajusta poco a poco: el dashi, el chashu y los condimentos ya aportan sal.",
    "fr": "Commencez avec seulement une demi-cuillère à café de sel fin. Goûtez le bouillon avant de servir et rectifiez par petites touches : dashi et garnitures sont déjà salés.",
    "de": "Zunächst nur einen halben Teelöffel feines Salz verwenden. Die Brühe vor dem Servieren abschmecken und vorsichtig nachsalzen: Dashi und Beläge sind bereits salzig.",
    "pt": "Comece com apenas meia colher de chá de sal fino. Prove o caldo antes de servir e ajuste aos poucos: o dashi, o chashu e os temperos já contêm sal.",
  },
  56: {
    "it": "Usa salmone e tonno espressamente forniti come idonei al consumo crudo, rispettando le indicazioni del fornitore su abbattimento e refrigerazione; tienili al freddo e assembla solo al momento del servizio. L'aspetto fresco non dimostra la sicurezza del pesce.",
    "en": "Use salmon and tuna expressly supplied as suitable for raw consumption, following the supplier's freezing and refrigeration guidance. Keep chilled and assemble just before serving; a fresh appearance does not establish safety.",
    "es": "Utiliza salmón y atún expresamente aptos para consumo crudo y sigue las indicaciones del proveedor sobre congelación y refrigeración. Consérvalos fríos hasta servir: el aspecto fresco no garantiza su seguridad.",
    "fr": "Utilisez du saumon et du thon expressément adaptés à la consommation crue, en suivant les consignes du fournisseur sur la congélation et le maintien au froid. Assemblez juste avant de servir : l'aspect frais ne garantit pas l'innocuité.",
    "de": "Nur Lachs und Thunfisch verwenden, die vom Lieferanten ausdrücklich für den Rohverzehr freigegeben sind; dessen Vorgaben zum Gefrieren und Kühlen einhalten. Bis zum Anrichten kalt lagern: frisches Aussehen ist kein Sicherheitsnachweis.",
    "pt": "Utilize salmão e atum expressamente adequados ao consumo cru, seguindo as instruções do fornecedor sobre congelação e refrigeração. Mantenha-os frios até servir: o aspeto fresco não garante segurança.",
  },
  59: {
    "it": "Usa vongole vive provenienti da filiera controllata, scarta i gusci rotti e quelle che non si chiudono al tocco prima della cottura; scarta tutte le vongole rimaste chiuse dopo una cottura adeguata.",
    "en": "Use live clams from a reliable supplier. Discard broken shells and clams that do not close when tapped before cooking; discard any clams that remain closed after thorough cooking.",
    "es": "Utiliza almejas vivas de un proveedor fiable. Desecha las conchas rotas y las almejas que no se cierren al tocarlas antes de cocinarlas; desecha también las que queden cerradas tras la cocción.",
    "fr": "Utilisez des palourdes vivantes provenant d'un fournisseur fiable. Jetez celles dont la coquille est cassée ou qui ne se referment pas au toucher avant cuisson, puis celles qui restent fermées après une cuisson complète.",
    "de": "Lebende Venusmuscheln von einem zuverlässigen Anbieter verwenden. Beschädigte Muscheln und solche, die sich bei Berührung nicht schließen, vor dem Garen aussortieren; Muscheln, die nach gründlichem Garen geschlossen bleiben, wegwerfen.",
    "pt": "Utilize amêijoas vivas de fornecedor fiável. Rejeite conchas partidas e amêijoas que não fechem ao toque antes da cozedura; deite fora as que permaneçam fechadas após uma cozedura adequada.",
  },
  80: {
    "it": "Il sanma è la costardella del Pacifico (Cololabis saira), non il luccio di mare. Per la preparazione domestica usa pesce acquistato pulito/eviscerato oppure fallo pulire dal pescivendolo; cuocilo completamente e verifica il centro del pesce.",
    "en": "Sanma is Pacific saury (Cololabis saira), not pike. For home cooking buy cleaned and gutted fish or have the fishmonger prepare it; cook the fish thoroughly and check the thickest part.",
    "es": "El sanma es paparda del Pacífico (Cololabis saira), no lucio. Para cocinarlo en casa compra pescado limpio y eviscerado o pide que lo preparen en la pescadería; comprueba la cocción en la parte más gruesa.",
    "fr": "Le sanma est le balaou du Pacifique (Cololabis saira), pas un brochet. Pour une préparation domestique, prenez du poisson nettoyé et vidé ou faites-le préparer par le poissonnier ; vérifiez la cuisson dans la partie la plus épaisse.",
    "de": "Sanma ist Pazifischer Makrelenhecht (Cololabis saira), kein Hecht. Für die Zubereitung zu Hause ausgenommenen, gesäuberten Fisch kaufen oder beim Fischhändler ausnehmen lassen; die Garung an der dicksten Stelle prüfen.",
    "pt": "O sanma é agulhão-do-Japão (Cololabis saira), não lúcio. Para preparar em casa, utilize peixe limpo e eviscerado ou peça ao peixeiro que o prepare; verifique a cozedura na parte mais espessa.",
  },
  96: {
    "it": "Prima della cottura elimina le vongole rotte e quelle vive che non si chiudono al tocco; dopo la cottura scarta tutte quelle rimaste chiuse. Conserva refrigerato il liquido filtrato se non lo usi subito.",
    "en": "Before cooking, discard clams with broken shells and live clams that do not close when tapped; after cooking discard any that remain closed. Refrigerate the strained liquid if not using it immediately.",
    "es": "Antes de cocerlas, desecha las almejas con conchas rotas o que no se cierren al tocarlas; después, desecha las que sigan cerradas. Refrigera el líquido colado si no lo usas enseguida.",
    "fr": "Avant cuisson, jetez les palourdes cassées ou qui ne se referment pas au toucher ; après cuisson, jetez celles qui restent fermées. Réfrigérez le jus filtré s'il n'est pas utilisé immédiatement.",
    "de": "Vor dem Garen beschädigte Muscheln und solche aussortieren, die sich bei Berührung nicht schließen. Nach dem Garen geschlossen gebliebene Muscheln wegwerfen. Abgesiebten Sud sofort verwenden oder kühlen.",
    "pt": "Antes da cozedura, deite fora amêijoas com conchas partidas ou que não fechem ao toque; depois, rejeite as que permaneçam fechadas. Refrigere o caldo coado se não o utilizar logo.",
  },
  110: {
    "it": "Per questa ricetta usa soltanto trippa/frattaglie vendute già pulite e precotte, seguendo le istruzioni del produttore. I 10–15 minuti sono un riscaldamento finale, NON bastano per rendere sicure frattaglie crude; se sono crude occorre prima una cottura completa specifica per il taglio.",
    "en": "Use only tripe/offal sold already cleaned and precooked, following the producer's directions. The 10–15 minutes are for final heating, NOT sufficient to cook raw offal safely; raw offal requires its own complete cooking beforehand.",
    "es": "Utiliza solo callos o vísceras ya limpios y precocidos, siguiendo las instrucciones del fabricante. Los 10–15 minutos son un calentamiento final, NO bastan para cocinar vísceras crudas; estas necesitan cocción completa previa.",
    "fr": "Utilisez uniquement des tripes ou abats vendus déjà nettoyés et précuits, conformément aux consignes du fabricant. Les 10 à 15 minutes servent au réchauffage final et ne suffisent PAS pour cuire des abats crus.",
    "de": "Nur bereits gereinigte und vorgegarte Kutteln/Innereien nach Herstellerangaben verwenden. Die 10–15 Minuten dienen lediglich zum abschließenden Erhitzen und reichen NICHT zum sicheren Garen roher Innereien.",
    "pt": "Utilize apenas tripas ou miudezas já limpas e pré-cozidas, seguindo as indicações do produtor. Os 10–15 minutos são para aquecer no final, NÃO chegam para cozinhar miudezas cruas; estas exigem cozedura completa prévia.",
  },
  117: {
    "it": "Controlla i bocconcini di pollo con un termometro alimentare: la temperatura al cuore deve raggiungere almeno 74 °C. La doratura esterna o il tempo di frittura non garantiscono da soli la cottura.",
    "en": "Check the chicken pieces with a food thermometer: the centre must reach at least 74°C (165°F). A golden crust or frying time alone does not guarantee doneness.",
    "es": "Comprueba los trozos de pollo con un termómetro de cocina: el centro debe alcanzar al menos 74 °C. El dorado exterior o el tiempo de fritura por sí solos no garantizan la cocción.",
    "fr": "Vérifiez les morceaux de poulet avec un thermomètre alimentaire : ils doivent atteindre au moins 74 °C à cœur. La couleur dorée et le temps de friture ne suffisent pas à garantir la cuisson.",
    "de": "Hähnchenstücke mit einem Lebensmittelthermometer kontrollieren: Die Kerntemperatur muss mindestens 74 °C erreichen. Bräunung und Frittierzeit allein beweisen keine vollständige Garung.",
    "pt": "Verifique os pedaços de frango com um termómetro alimentar: o centro deve atingir pelo menos 74 °C. A cor dourada e o tempo de fritura, por si só, não garantem a cozedura.",
  },
  133: {
    "it": "Prima di affettare il rotolo di pollo, verifica con un termometro che il centro abbia raggiunto almeno 74 °C; prolunga la cottura se necessario. Usa spago da cucina, non spaghetti alimentari.",
    "en": "Before slicing the rolled chicken, verify with a food thermometer that the centre has reached at least 74°C (165°F); cook longer if necessary. Tie with kitchen twine, not edible spaghetti.",
    "es": "Antes de cortar el pollo enrollado, comprueba con un termómetro que el centro alcance al menos 74 °C; prolonga la cocción si hace falta. Ata con hilo de cocina, no con espaguetis.",
    "fr": "Avant de trancher le poulet roulé, vérifiez au thermomètre que le centre a atteint au moins 74 °C ; prolongez la cuisson si nécessaire. Ficelez avec de la ficelle de cuisine.",
    "de": "Vor dem Aufschneiden des Hähnchenrollbratens mit einem Thermometer mindestens 74 °C Kerntemperatur prüfen; nötigenfalls länger garen. Küchengarn statt Spaghetti verwenden.",
    "pt": "Antes de fatiar o rolo de frango, confirme com um termómetro que o centro atingiu pelo menos 74 °C; prolongue a cozedura se necessário. Ate com fio de cozinha.",
  },
  149: {
    "it": "Usa riso cotto raffreddato rapidamente in uno strato sottile, idealmente entro un'ora, poi refrigerato e consumato entro 24 ore. Non lasciare il riso a temperatura ambiente; riscaldalo una sola volta finché è ben fumante in ogni parte.",
    "en": "Use cooked rice cooled rapidly in a shallow layer, ideally within one hour, then refrigerated and used within 24 hours. Do not leave rice at room temperature; reheat only once until steaming hot throughout.",
    "es": "Utiliza arroz cocido enfriado rápidamente en una capa fina, idealmente en una hora, refrigerado y consumido en 24 horas. No lo dejes a temperatura ambiente y recaliéntalo una sola vez hasta que esté muy caliente por completo.",
    "fr": "Utilisez du riz cuit refroidi rapidement en couche fine, idéalement en une heure, puis réfrigéré et consommé sous 24 heures. Ne le laissez pas à température ambiante et ne le réchauffez qu'une fois, jusqu'à ce qu'il soit brûlant à cœur.",
    "de": "Gekochten Reis in einer flachen Schicht schnell, idealerweise innerhalb einer Stunde, abkühlen, dann kühlen und binnen 24 Stunden verwenden. Nicht bei Raumtemperatur stehen lassen; nur einmal vollständig dampfend heiß aufwärmen.",
    "pt": "Use arroz cozido arrefecido rapidamente numa camada fina, idealmente numa hora, depois refrigerado e consumido em 24 horas. Não o deixe à temperatura ambiente; reaqueça apenas uma vez até ficar bem quente em toda a porção.",
  },
  150: {
    "it": "Per una preparazione domestica prudente controlla con un termometro che il petto d'anatra raggiunga almeno 74 °C al cuore prima del servizio; i minuti indicati sono solo orientativi. Il breve passaggio nel brodo non sostituisce la verifica della temperatura.",
    "en": "For a conservative home preparation, use a food thermometer to check that duck breast reaches at least 74°C (165°F) at the centre before serving; timings are indicative. Brief simmering in broth does not replace this check.",
    "es": "Para una preparación doméstica prudente, comprueba con un termómetro que el centro de la pechuga de pato llegue al menos a 74 °C antes de servir. Los tiempos son orientativos y un hervor breve en el caldo no sustituye esta comprobación.",
    "fr": "Pour une préparation domestique prudente, vérifiez avec un thermomètre que le magret de canard atteint au moins 74 °C à cœur avant de servir. Les durées sont indicatives ; le bref passage dans le bouillon ne remplace pas ce contrôle.",
    "de": "Für eine vorsichtige Zubereitung zu Hause die Entenbrust vor dem Servieren mit einem Thermometer auf mindestens 74 °C Kerntemperatur prüfen. Zeitangaben sind Richtwerte; kurzes Ziehen in Brühe ersetzt diese Kontrolle nicht.",
    "pt": "Para uma preparação doméstica prudente, confirme com um termómetro que o peito de pato atinge pelo menos 74 °C no centro antes de servir. Os tempos são indicativos; a passagem breve pelo caldo não substitui a medição.",
  },
  153: {
    "it": "Cuoci le polpette di pollo fino ad almeno 74 °C al cuore, misurati con un termometro. Per la salsa da intingere usa esclusivamente tuorlo pastorizzato idoneo al consumo senza cottura; non usare un tuorlo fresco crudo non pastorizzato.",
    "en": "Cook the chicken meatballs to at least 74°C (165°F) at the centre, measured with a food thermometer. For dipping use only pasteurized egg yolk suitable for eating without cooking; never use unpasteurized raw yolk.",
    "es": "Cocina las albóndigas de pollo hasta al menos 74 °C en el centro, comprobados con termómetro. Para mojar utiliza solo yema pasteurizada apta para consumo sin cocción; no uses yema cruda sin pasteurizar.",
    "fr": "Faites cuire les boulettes de poulet à au moins 74 °C à cœur, mesurés au thermomètre. Pour tremper les brochettes, utilisez uniquement du jaune d'œuf pasteurisé adapté à la consommation sans cuisson, jamais un jaune cru non pasteurisé.",
    "de": "Hähnchenbällchen mit einem Thermometer auf mindestens 74 °C Kerntemperatur garen. Zum Dippen nur pasteurisiertes, für den Rohverzehr geeignetes Eigelb verwenden, niemals rohes unpasteurisiertes Eigelb.",
    "pt": "Cozinhe as almôndegas de frango até pelo menos 74 °C no centro, medidos com um termómetro. Para molhar, use apenas gema pasteurizada adequada ao consumo sem cozedura, nunca gema crua não pasteurizada.",
  },
  156: {
    "it": "Usa vongole vive e spurgate da fornitore affidabile. Elimina quelle con guscio rotto o che non si chiudono al tocco prima di cuocerle; scarta quelle rimaste chiuse dopo una cottura adeguata. Non usare il liquido di molluschi scartati.",
    "en": "Use live, purged clams from a reliable supplier. Discard broken shells and clams that do not close when tapped before cooking, and discard any remaining closed after thorough cooking. Do not use liquid from discarded clams.",
    "es": "Utiliza almejas vivas y depuradas de un proveedor fiable. Desecha las conchas rotas o que no se cierren al tocarlas y, tras cocinarlas bien, las que sigan cerradas. No uses líquido de almejas desechadas.",
    "fr": "Utilisez des palourdes vivantes et dégorgées d'un fournisseur fiable. Jetez celles dont la coquille est cassée ou ne se referme pas au toucher, puis celles qui restent fermées après cuisson complète. N'utilisez pas le jus des palourdes jetées.",
    "de": "Lebende, gereinigte Venusmuscheln von einem zuverlässigen Anbieter verwenden. Beschädigte Muscheln oder solche, die sich bei Berührung nicht schließen, aussortieren; nach gründlichem Garen geschlossene Muscheln wegwerfen. Deren Flüssigkeit nicht verwenden.",
    "pt": "Use amêijoas vivas e depuradas de fornecedor fiável. Deite fora as que têm conchas partidas ou não fecham ao toque e, depois de bem cozidas, as que permaneçam fechadas. Não aproveite o líquido das amêijoas rejeitadas.",
  },
}

TITLES_80 = {
    "it": "Sanma no Shioyaki (Costardella del Pacifico alla griglia con daikon)",
    "en": "Sanma no Shioyaki — grilled Pacific saury with daikon",
    "es": "Sanma no Shioyaki — paparda del Pacífico a la parrilla con daikon",
    "fr": "Sanma no Shioyaki — balaou du Pacifique grillé au daikon",
    "de": "Sanma no Shioyaki — gegrillter Pazifischer Makrelenhecht mit Daikon",
    "pt": "Sanma no Shioyaki — agulhão-do-Japão grelhado com daikon",
}
INGREDIENTS_80 = {
    "it": "costardella del Pacifico (Cololabis saira, sanma) intera, pulita ed eviscerata",
    "en": "whole Pacific saury (Cololabis saira), cleaned and gutted",
    "es": "paparda del Pacífico (Cololabis saira) entera, limpia y eviscerada",
    "fr": "balaou du Pacifique (Cololabis saira) entier, nettoyé et vidé",
    "de": "ganzer Pazifischer Makrelenhecht (Cololabis saira), gesäubert und ausgenommen",
    "pt": "agulhão-do-Japão (Cololabis saira) inteiro, limpo e eviscerado",
}
# Explicit observed false friends: corrections apply only to the specified
# recipe/locale/field, never as unrestricted global string substitutions.
LEXICAL = {
    (56, "en"): {"Shrimp cooked in shell": "peeled cooked shrimp", "fresh salmon for sashimi in cubes": "salmon suitable for sashimi, diced"},
    (56, "fr"): {"striscioles d'alga nori": "fines lanières de nori"},
    (56, "es"): {"grietas de algas nori": "tiras de alga nori"},
    (56, "pt"): {"Camarão cozido em casca": "camarão cozido e descascado"},
    (59, "en"): {"unwrap the remaining ones closed": "discard those that remain closed", "Fresh clams (sprinkled in salted water)": "fresh clams, already purged"},
    (59, "fr"): {"oubliez celles qui restent fermées": "jetez celles qui restent fermées", "palourdes fraîches (purée dans l'eau salée)": "palourdes fraîches préalablement dégorgées"},
    (59, "pt"): {"desembrulhar os restantes fechados": "deite fora as que permanecerem fechadas"},
    (59, "es"): {"descargue las que quedan cerradas": "desecha las que permanezcan cerradas"},
    (96, "en"): {"until the potatoes are kept": "until the potatoes are tender"},
    (96, "pt"): {"até que as batatas sejam mantidas": "até as batatas estarem tenras"},
    (133, "es"): {"espagueti de cocina": "hilo de cocina"},
    (133, "de"): {"Kochspaghetti": "Küchengarn"},
    (133, "en"): {"golden discs": "even slices"},
    (150, "en"): {"chest of chess duck": "duck breast in a crosshatch pattern"},
    (150, "es"): {"pecho de pato de ajedrez": "pechuga de pato en forma de cuadrícula"},
    (150, "fr"): {"poitrine de canard à échiquier": "peau du magret en croisillons"},
    (150, "pt"): {"peito do pato de xadrez": "peito de pato em padrão cruzado", "toques de porco": "pedaços de alho-francês"},
    (150, "de"): {"Berühre die Haut der Entenbrust in ein Schachbrett": "Die Haut der Entenbrust kreuzweise einschneiden"},
    (153, "en"): {"Chicken millstone": "ground chicken", "mischioose": "sticky"},
    (153, "es"): {"Triturado de pollo": "pollo picado", "muérdago": "viscoso"},
    (153, "fr"): {"moulu de poulet": "poulet haché", "texture soit silencieuse": "consistance sirupeuse"},
    (153, "de"): {"Hühnchenmühle": "Hähnchenhackfleisch", "Spennella": "Bestreichen"},
    (153, "pt"): {"Pedra de molho de galinha": "frango picado", "mischioose": "pegajosa"},
    (156, "pt"): {"suco de mosquito": "caldo das amêijoas", "moluscos, verdadeiras, torcidas": "amêijoas depuradas"},
    (156, "en"): {"clams, true, sprained": "purged clams"},
    (156, "fr"): {"beurre de girofle": "beurre", "aspirez": "égouttez"},
}


def _replace(text: str, mapping: dict[str, str]) -> str:
    for before, after in mapping.items():
        text = text.replace(before, after)
    return text


def repair(recipe: dict) -> dict:
    """Mutate a reconstructed authoring recipe: locale-complete, risk-targeted."""
    rid = int(recipe["id"].split("_")[-1])
    if rid not in IDS:
        return recipe
    src_steps = recipe["steps"]
    assert len(src_steps) >= 6
    if rid == 51:
        target = next(x for x in recipe["ingredients"] if x["id"] == "sale_marino_fine")
        target["quantity"], target["unit"] = 0.5, "tsp"
    if rid == 110:
        # Preserve the meat identity; qualify mandatory precooking.
        recipe["locales"]["it"]["ingredients"][
            recipe["ingredients"][0]["id"]
        ]["name"] = "trippa o frattaglie già pulite e precotte"
    if rid == 153:
        for loc, label in {
            "it": "uovo pastorizzato (albume nell'impasto, tuorlo pastorizzato per servire)",
            "en": "pasteurized egg (white in the mixture, pasteurized yolk for dipping)",
            "es": "huevo pasteurizado (clara en la mezcla y yema para mojar)",
            "fr": "œuf pasteurisé (blanc dans la préparation, jaune pasteurisé pour tremper)",
            "de": "pasteurisiertes Ei (Eiweiß in der Masse, pasteurisiertes Eigelb zum Dippen)",
            "pt": "ovo pasteurizado (clara na mistura, gema pasteurizada para molhar)",
        }.items():
            egg_id = next(x["id"] for x in recipe["ingredients"] if x["id"].startswith("uovo"))
            recipe["locales"][loc]["ingredients"][egg_id]["name"] = label

    for loc in LOCALES:
        p = recipe["locales"][loc]
        if rid == 80:
            p["title"] = TITLES_80[loc]
            p["ingredients"][recipe["ingredients"][0]["id"]]["name"] = INGREDIENTS_80[loc]
        if rid == 51:
            salt = p["ingredients"]["sale_marino_fine"]
            salt["note"] = {
                "it": "0,5 cucchiaino iniziale: aggiusta solo dopo aver assaggiato il brodo",
                "en": "Start with ½ tsp; adjust only after tasting the broth",
                "es": "Empieza con ½ cucharadita; ajusta tras probar el caldo",
                "fr": "Commencez par ½ cuillère à café ; rectifiez après dégustation",
                "de": "Mit ½ TL beginnen; erst nach dem Abschmecken nachsalzen",
                "pt": "Comece com ½ colher de chá; ajuste depois de provar",
            }[loc]
        mapping = LEXICAL.get((rid, loc), {})
        for entry in p["ingredients"].values():
            entry["name"] = _replace(entry["name"], mapping)
        p["description"] = _replace(p["description"], mapping)
        for sid, prose in p["steps"].items():
            p["steps"][sid] = _replace(prose, mapping)
        # Safety notes are appended to the relevant actual process step,
        # rather than to metadata that the runtime could hide.
        step_target = {
            51: "step_1", 56: "step_5", 59: "step_6", 80: "step_1",
            96: "step_1", 110: "step_1", 117: "step_5", 133: "step_4",
            149: "step_1", 150: "step_7", 153: "step_6", 156: "step_2",
        }[rid]
        assert step_target in p["steps"], (rid, loc, step_target)
        p["steps"][step_target] = p["steps"][step_target].rstrip(". ") + ". " + SAFETY[rid][loc]
        if rid == 80 and loc == "it":
            p["steps"]["step_1"] = (
                "Utilizza sanma già pulito ed eviscerato dal pescivendolo. " + SAFETY[rid]["it"]
            )
        if rid == 153 and loc == "it":
            p["steps"]["step_6"] = (
                "Servi gli spiedini glassati con il tuorlo pastorizzato "
                "idoneo al consumo senza cottura, per intingerli. " + SAFETY[rid]["it"]
            )
        if rid == 110 and loc == "it":
            p["steps"]["step_1"] = (
                "Utilizza trippa già pulita e precotta; tagliala in bocconi "
                "regolari senza ricontaminarla con utensili usati per alimenti crudi. "
                + SAFETY[rid]["it"]
            )
    recipe["editorialVerification"]["culinaryStatus"] = "corrected"
    recipe["editorialVerification"]["culinaryNote"] = (
        "Fast Track 12/12: original recipe reconciled to full procedure and "
        "localized risk-specific corrections for IT/EN/ES/FR/DE/PT; "
        "FDA/FSIS/FSA and EU species evidence recorded in tool/fast_track_12_repairs.py."
    )
    return recipe
