# Jobandtalent SE — esito pilota live e proposta di integrazione controllata

**Data:** 17 novembre 2026. **Stato:** review tecnica in PR #56, non merged, **fonte non abilitata**. Nessuna candidatura inviata.

## Prova reale, un solo workflow opt-in

- [GitHub Actions #44072892358](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44072892358), commit pilota `439f1837`, job `one-company-two-cycles` **success**, [artifact `jobandtalent-single-pilot-20261117`](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44072892358#artifacts).
- Feed: JobTech SE `31558200`, 3 query limitate a 10 risultati ciascuna, 30 righe osservate con 2 candidati HR stage distinti; 4 richieste / **324.019 B**. La sola posizione di Jobandtalent è passata alla verifica ATS.
- Datore `Jobandtalent Sweden AB`, sede **Malmö**, ATS Teamtailor `jobb.jobandtalent.com`, ID ATS **8503489**. Le due prove live confermano titolo/sede, inventario ufficiale `/sitemap`, identità dell'azienda sulla pagina legal/privacy pubblicata sullo stesso host, stessa candidatura e form abilitato.
- **Ciclo ATS 1:** 6 richieste / **399.581 B** / **6,114 s**, dossier `policy-v2-evidence-passed-staging-only`, un nuovo ID rispetto ai 363 record di `main`, nessun ID storico perso o duplicato, `closure_eligible=0`.
- **Ciclo ATS 2:** 5 richieste / **399.303 B** / **3,475 s**, nuovo dossier **nuovamente live e positivo**, stesso ID storico e prima scoperta, **0 nuovi ID**, nessuna chiusura o duplicazione.
- **Totale osservato del pilota:** **15 HTTP, 1.122.903 B, 19,692 s wall-clock**, **0 rendering**, **0 POST**, **0 invio candidatura**, **0 scritture catalogo produzione**. Dati di contatto/curricula non acquisiti.
- Catalogo di partenza `main` `ab51981` = **363 ID, 28 internship HR verified**, 1 working student verified a parte; simulazione in directory temporanea = **364 ID, 29 internship HR verified**. **Guadagno reale in produzione: 0**. La simulazione di 2 cicli nello stesso workflow non prova la stabilità su 2 giorni distinti.
- Codice `scripts/pilot_jobandtalent_two_cycles.py` con prove offline `tests/test_jobandtalent_live_pilot.py`; [Validate application #44072388736](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44072388736) e [#44072397525](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44072397525) **success**. Previsti rifiuti automatici su datore non confermato o feed campionato privo dell'ID.
- Un primo tentativo di *definizione YAML* del workflow one-off non era valido: [#44072781509](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44072781509) è fallito con **0 job e 0 letture**. Corretto e lanciato **un solo pilota ATS effettivo**. Il workflow temporaneo è stato **eliminato** dal ramo pilota al commit `b87cb482` per impedire ripetizioni accidentali. Il ramo pilota separato non è una PR di produzione.

## Contratto d'integrazione riutilizzabile — proposta, non attivazione

**Fonte proposta:** `staging-jobandtalent-se` inizialmente `enabled: false` e `staging_only: true`, `ownership_scope: reviewed-hosts`, `require_employer_identity: true`, host esclusivo `jobb.jobandtalent.com`, inventario verificato `https://jobb.jobandtalent.com/sitemap`. Il codice corrente non aggiunge questo record a `data/sources.json` né a `data/companies.json`.

**Passo tecnico mancante:** collegare `official_feed_staging.staging_part()` al normale `process_source()`/job `collect` con un adapter parametrico e prova ATS per ogni ciclo. `finalize()` è stato esercitato davvero in staging, ma una prova su directory temporanea **non** è un produttore quotidiano. I controlli in ingresso devono preservare la coppia **JobTech-ID 31558200 ≠ ATS-ID 8503489**, la proprietà del datore, titolo, sede, referral on-host, inventario e form; nessun record viene promosso se mancano prove fresche secondo policy v2.

**Deduplicazione e chiusure:** riutilizzare ID stabile per ATS e alias ufficiali solo con prova individuale, rifiutare mirror ambigui, preservare `first_discovered_at`. L'inventario puntuale di una sola posizione **non può** causare chiusure per assenza, `closure_eligible=[]`; evidenza di `closed` solo dal modulo/pagina ufficiale della specifica vacancy.

**Budget iniziale condizionale:** almeno un dossier ATS su una posizione in un singolo ciclo; limite conservativo e host allowlist, gestione immediata 429/access denied e cache rispettosa. Il pilota di due letture è costato 11 richieste ATS / 798.884 B, ma il budget effettivo del ciclo ordinario va misurato prima di aumentare frequenza o fonti. Condividere, se ammesso, la lettura JobTech tra candidati; non rilanciare la ricerca multipla per ogni azienda.

**Gate prima del rollout (richiede autorizzazione specifica):** CI e test regressione; nuovo preflight read-only su ramo isolato e confronto con catalogo completo; source registrata ma disabled; piano di rollback e monitoraggio qualità; prima raccolta limitata con metriche richieste/byte/tempo/ID; conferma della produzione dopo un ciclo effettivamente pubblicato e verifica Cloudflare distinta. Nessun merge o source enable automatico da questa nota.

## Risposte alle tre domande

1. **Secondo ciclo e duplicazione:** nel secondo *ciclo live dello stesso workflow* un unico ID è stato mantenuto; **0 candidature aggiuntive duplicate**. Restano da verificare i giorni separati.
2. **Riutilizzo per altri ATS:** `staging_part()` e `finalize()` sono riutilizzabili come contratto, ma `ats_parent()` e fallback dell'applicazione oggi riconoscono solo il percorso Teamtailor revisionato. Nuovi ATS richiedono un adapter con legame datore→tenant, ID e form specifici, test negativi e robots; nessuna approvazione indiscriminata.
3. **Altro feed pubblico UE27:** CZ MPSV (delta 61 righe, 0 HR stage) e LV NVA (150 righe, 11 segnali HR, 0 HR internship) non dimostrano ancora resa positiva; LT ha dataset promettente ma accesso a metadata/distribuzioni HTTP 429, quindi **0 righe live**. Nessuna fonte nazionale alternativa è ancora migliore di JobTech secondo la metrica *stage HR verified per costo*. Ulteriore campionamento solo consentito, per segnali realmente candidabili.

**Prossimo passo:** progettare il nuovo adapter parametrico con fonte disabled e test dinamici *senza attivazione*, poi una decisione separata sull'eventuale merge, sul pilot di raccolta ordinaria e sull'attivazione della fonte.
