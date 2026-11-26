# Cooking Anime — riconciliazione PR / Fast Track (26 novembre 2026)

## Baseline verificata
- `main` = `8ea641ecb0ecf3083b9366989d85c9bbc6fee9a3` (24/11/2026).
- Factory = `842dfa073451ec247308ccb4afb8ead5349bcbd4`, Master v27, Golden Index v31.
- Catalogo pubblico: 162 ID; 6 locale; asset originali già approvati: 50/162.
- PR aperte effettive: #65, #44, #11. Nessun merge/disabilitazione automatica proposto da questo audit.

## Stato reale e azione

| PR | Stato reale | Evidenza | Decisione operativa |
|---|---|---|---|
| [#65](https://github.com/riccardopinato/In-Cucina-con-gli-Anime/pull/65) | OPEN, non-Draft, `mergeable_state=dirty`, head `758c33b5` | 39 file, fra cui 28 ricette e cataloghi; sovrapposta a #66–#71 già su `main`. | **EXTRACT/RECONCILE**, NON rebase cieco, NON merge. Diff campo-per-campo dalla sorgente corrente; cherry-pick solo dei fix ancora mancanti, incrementare versioni una volta e rigenerare runtime. Quando provenienza comprovata, chiusura della vecchia PR come superseded. |
| [#44](https://github.com/riccardopinato/In-Cucina-con-gli-Anime/pull/44) | OPEN/Draft, 122-record review dossier storico (112 ricette + 10 componenti) | Non modifica runtime. Piano di review qualificata universalmente obbligatoria storico, incompatibile con l'attuale Fast Track proporzionata per ricette ordinarie. | **DOCUMENTATION REVIEW / SUPERSEDE CANDIDATE**. Conservare lead verificati su sicurezza alimentare; non mantenere 122 sign-off come blocco universale. Non attribuire certificazione inesistente. |
| [#11](https://github.com/riccardopinato/In-Cucina-con-gli-Anime/pull/11) | OPEN, billing lifetime `remove_ads_lifetime` | PurchaseGateway, restore, provider verifier fail-closed, prova sandbox non fornita; confini economici differenziati. | **KEEP BLOCKED** fino al test vero su Google Play. Non integrare nel lotto editoriale né abilitare billing prima della verifica. |

## Campionamento PR #65 vs authoring corrente
Confronto effettivamente eseguito su tre ricette, versioni 5/5, 5/5 e 6/6 fra `main` e head della #65:
- `recipe_000055`: 7 campi localizzati divergenti (ingredienti e passaggi in più lingue).
- `recipe_000083`: **54** campi divergenti (Tsukemen: descrizioni, ingredienti e passaggi in varie lingue); contenuti **non equivalenti per definizione**, da confrontare in contesto prima di scegliere.
- `recipe_000134`: 6 campi divergenti, principalmente passi EN/ES/FR/DE/PT.

**Conseguenza:** versioni numeriche uguali non dimostrano identità editoriale. Sono stati confrontati **3/28 record**, non 28/28. Non dichiarare la #65 interamente recuperata o superata. Non applicare merge automatico.

## Regola per lo step successivo
1. Inventario degli **ID e dei campi divergenti** per tutte le 28 ricette della #65 sul `main` attuale.
2. Per ciascuna differenza distinguere `already-fixed`, `new-valid-fix`, `regression`, `needs-context`.
3. Risolvere le sole differenze realmente utili su un branch ricette in ownership esclusiva, senza riscrivere 162 ricette inutilmente; rigenerare catalogo, exact-head CI.
4. Chiudere #65 soltanto dopo verifica/trasferimento del residuo, #44 soltanto dopo salvataggio dei rischi specifici; lasciare #11 indipendente per la release.

## Guardrail
Stato del source tree e QA editoriale sono separati da certificazione semantica IA, prova culinaria fisica, acquisto sandbox e pubblicazione Play. Le PR tecniche, le CI e un report verde non certificano fatti esterni.