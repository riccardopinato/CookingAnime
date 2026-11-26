# Visual Batch Engine v0.1 — Cooking Anime pilota (26 novembre 2026)

**Stato:** implementazione iniziale su branch, NON Golden certificata, NON generazione immagini, NON integrazione runtime.

## Componenti realmente aggiunti
- `tool/visual_batch_engine.py`: core portabile Python stdlib, input dominio neutro, ID/fingerprint, profilo riferimenti verificati su file JPEG reali, parsing dimensioni JPEG, rendering prompt, verifica dimensioni/peso e evidenza visuale fail-closed.
- `tool/cooking_visual_adapter.py`: adapter Cooking Anime, sole ricette authoring canoniche; **50 artwork approvati** come riferimenti di versione, stile testuale F3D/F3E, policy 140 KiB / 720–960 px, prompt alimentati da titoli e ingredienti italiani. Nessun nuovo SDK nell'APK.
- `tool/tests/test_visual_batch_engine.py`: test sul corpus reale 50 asset, 12 richieste pilot, 112 richieste globali e guardrail dei risultati falsamente approvati.

## Come riprodurre
```sh
python3 tool/cooking_visual_adapter.py --output build/visual_batch/pilot.json
python3 tool/cooking_visual_adapter.py --all --output build/visual_batch/112_planned.json
python3 -m unittest tool.tests.test_visual_batch_engine
```

**Il primo comando prepara 12 richieste, non 12 immagini.** Il secondo produce 112 richieste, non genera immagini. Ogni richiesta conserva fingerprint della ricetta, della specifica e dei 50 riferimenti, per impedire promozioni dopo modifiche alle ricette.

## Pilota rappresentativo (12 ricette)
| ID | Piatto | Distingue dal piatto visivamente simile |
|---|---|---|
| 051 | Shio ramen | Brodo chiaro, non tonkotsu |
| 053 | Ebi tendon | Tempura di gamberi sul riso |
| 056 | Chirashizushi | Riso sushi guarnito, non maki |
| 057 | Kurogoma dango | Dango al sesamo nero, non cioccolatini |
| 060 | Castella | Pan di Spagna giapponese, non pan cake |
| 063 | Tenshinhan | Omelette di granchio sul riso con salsa |
| 074 | Oden | Stufato chiaro con componenti separati, non ramen |
| 083 | Tsukemen | Noodles freddi e brodo da intingolo in ciotole **separate** |
| 086 | Soufflé pancake | Alto e soffice, non crepe |
| 108 | Tonkotsu ramen | Brodo denso e opaco, non shio |
| 134 | Shirasu don | Bianchetti minuti, non gamberoni |
| 162 | Yuzu sorbet | Sorbetto agrumato, non torta |

## Requisiti per portarlo in produzione
1. **Input**: app adapter schema, ID, source fingerprint, fatti visivi positivi e negativi, riferimenti di stile approvati, limiti asset, diritti.
2. **GeneratorPort**: provider di generazione immagini per batch con numero varianti, budget, rate-limit e idempotenza. Attualmente NON COLLEGATO. Niente API a pagamento o credenziali aggiunte.
3. **VisionPort**: riconoscimento visivo reale dell'asset candidato (oggetti/ingredienti/forma/piatto) e confronto delle immagini campione per stile; un controllo solo testuale non equivale al VisionPort. Evidenza con `candidateSha256`, `requestFingerprint`, `styleReferenceFingerprint`, `mode=ACTUAL_IMAGE_REVIEW`, `foodIdentityPass`, `stylePass` e motivi delle anomalie. Nella v0.1 NON COLLEGATO.
4. **Gate tecnico**: un solo JPEG per ricetta, massimo 140 KiB, min lato corto 720 px, max lato lungo 960 px, asset originale e fonte/diritti verificati. Il motore verifica questi valori senza Pillow.
5. **Review**: anche il `VISUAL_CANDIDATE_PASS_NOT_APPROVED` necessita di approvazione editoriale/rights secondo la policy dell'app e aggiornamento del manifest; un prompt non è un'immagine, una generazione non è approvazione.
6. **Batching**: su 112 ricette, prima 12 campioni e correzione del protocollo, poi 20/40/restante; richieste disgiunte e merge unico del manifest dopo validazione. Le altre 100 hanno `REQUIRES_DOMAIN_REVIEW` finché non si producono fatti visivi specifici.

## Riutilizzo cross-app
Il core non importa lo schema Cooking Anime. I consumer futuri (World Days, Art Drift, app fotografiche) sostituiscono l'adapter, i criteri visivi e i diritti, **non** il motore. Il riuso in un secondo consumer e la visual QA reale sono prerequisiti per valutare promozione a Donor/Golden App Factory. Non trasferire per errore le euristiche gastronomiche in altre app.

## Limiti verificabili
- `reference_profile` confronta *file reali*, dimensioni e digest, ma **non apprende da solo uno stile visivo**; il direttivo grafico è editoriale. Similarità stilistica/riconoscimento richiedono VisionPort.
- Il core non genera immagini, non richiama modelli cloud e non fa reverse engineering di opere protette.
- L'immagine candidata si può promuovere soltanto dopo riconoscimento reale, verifica manuale e protezione da versioni stale. Non ridurre i guardrail per automatizzare le 112.
