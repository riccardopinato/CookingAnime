# Cooking Anime — Fast Track IA, backlog già esistente (19 novembre 2026)

## Ambito

Completare **solo** `recipe_000051`–`recipe_000162` (112 ricette) nelle sei lingue del catalogo (`it/en/es/fr/de/pt`). Non creare nuovi ID, non ampliare il ricettario finché queste non sono completate.

Baseline repository: `main@fb4c8cf5d7b0e8de0ada7649a1ef8b7e981ed465`.
Baseline Factory: `App-Factory-Core@b630a210e3121b0255bbad5de7b408d2c67c6298`, Master v27, sezione «CONTENT EDITORIALE A BASSO RISCHIO — FAST TRACK».

## Inventario reale

- 162 ID nel runtime e 162 entry per ciascuna delle sei lingue; 112 appartengono al backlog 51–162.
- I campi `status: published` nel vecchio authoring **non** provano la qualità editoriale.
- Le traduzioni runtime del backlog contengono metodi generici non fedeli alla preparazione italiana e lessico misto. Esempio verificato: `recipe_000052` EN presenta un metodo di frittura generico al posto della preparazione specifica con lievitazione, ripieno e panatura; EN/ES conservano parole come «ammorbidito».
- Esistono cinque pacchetti `authoring/f3l_review_drafts` di 112 candidati ciascuno, con interventi di correzione pregressi. Sono **input editoriali**, non testi da importare indiscriminatamente: la documentazione dichiara una sola ricetta (`000051`) completamente rivista in tutte le cinque lingue; altre correzioni sono parziali.
- I dieci componenti riutilizzabili richiedono coerenza con ingredienti e preparazioni.

## Nuova regola di lavoro

Il Master Fast Track sostituisce i vecchi obblighi **universali** di chef, traduttori professionisti e firma umana su ogni record. Non elimina controllo di completezza, preparabilità, plausibilità dei tempi, quantità, allergeni e rischio alimentare, anime-reference claims, copyright e deduplica.

Per ogni ID: confrontare italiano canonico, cinque pacchetti candidati, runtime attuale e componenti; correggere davvero le istruzioni in tutte le lingue, mantenendo quantità/tempi coerenti; registrare eventuali anomalie specifiche come HOLD, senza bloccare gli altri ID; poi aggiornare authoring, compilati, verifiche e CI sul medesimo commit. Il contenuto solo revisionato con IA **non** va chiamato «certificato da professionisti».

**Il precedente gate '0 human-reviewed = zero pubblicazione' non va più usato come divieto automatico.** Restano indipendenti i gate tecnici per build/release, copyright e i problemi effettivi di sicurezza alimentare.

## Esecuzione e controllo

```bash
python3 tool/fast_track_recipe_inventory.py --output build/fast-track-recipes.json
python3 tool/compile_recipe_catalog.py --check
python3 tool/validate_recipe_catalog.py
```

L'inventario è read-only e volutamente prudente: un esito senza segnalazioni lessicali **non** equivale a ricetta già verificata o pronta per il merge. Dopo ogni lotto aggiornare quattro numeri distinti: ID integrati davvero dopo revisione, ID già presenti nel runtime ma da correggere, ID in HOLD motivato, ID restanti.

## Stato di questa PR

**Impostazione e inventario dei difetti**, non completamento delle 112 ricette. Questa modifica non promuove draft, non falsifica sign-off e non dichiara traduzioni corrette prima della revisione effettiva.
