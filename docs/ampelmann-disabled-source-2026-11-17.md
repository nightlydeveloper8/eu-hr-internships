# People Placement — Ampelmann source pronta ma DISABILITATA (17 novembre 2026)

## Evidenza e configurazione preparata

La [PR #60](https://github.com/nightlydeveloper8/eu-hr-internships/pull/60) contiene il nuovo adapter **Recruitee public XML** opt-in, con prova `process_source() → finalize()` effettuata due volte **il 17/11 nello stesso giorno** nella [run #44147104809](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44147104809): **1 stage HR policy v2** nello staging (Ampelmann Delft, `Internship People & Organisation`, posting **2822573**), **9 GET / 1.887.074 byte / 12,841 secondi-fonte**, stesso ID catalogo nei due cicli, 363 ID storici preservati, nessuna chiusura per assenza. **Non è una verifica di produzione**.

Su questo branch, **derivato dalla HEAD PR #60**, predisposti e materialmente scritti nel registro del branch:
- Azienda `ampelmann-operations-b-v` — Ampelmann Operations B.V., URL aziendale ufficiale career `https://careers.ampelmann.nl/`, evidenza posizione e sede **Delft, NL**; paese verificato dalla vacancy, nessun dato sul numero dipendenti inventato
- Fonte `recruitee-ampelmann-nl` — `enabled=false`, `adapter=recruitee`, `feed_format=recruitee-public-xml`, `application_check=recruitee-linked`, feed esatto `/api/feeds/offers.xml`, host solo `careers.ampelmann.nl`, limite 16 HTTP/70 s, ownership revisionata
- `collection_activation_hold=true` sull'azienda, nuovo gate nel `collector.daily.provision()`: se un'azienda è in hold, **nessun crawler `auto-*`** viene creato, e un'eventuale fonte attiva accidentalmente causa `ValueError` (fail closed). Per attivare servono due modifiche simultanee, togliere hold e abilitare quella stessa fonte specifica, **con autorizzazione distinta**.

## Prova automatica

[Run #44173740699](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44173740699) — workflow temporaneo branch-only **success**: 5 regressioni offline superate, dry-run `would_add_companies=1`, `would_add_sources=1`, `enabled=false`, `auto_provisioned=0`; applicazione nel solo branch `--apply`, `python -m collector.daily provision`, `python -m collector.pipeline --validate` superati. Commit su branch isolato **`69ebbd8`** dei soli `data/companies.json` e `data/sources.json`; dati preesistenti preservati. La prova stampa **1.897 aziende / 1.894 collector attivi** sul branch: +1 azienda registrata **non significa** +1 fonte attiva o candidatura in produzione. Nessun GET/PATCH/POST verso Ampelmann nel provisioning.

## Gate aperti e distinzione ambienti

1. Rilettura bounded del feed e modulo su **data diversa dal 17 novembre** e confronto same-ID, robots e costo, senza POST
2. PR #60 non ancora mergiata; review della modifica specifica, CI e allineamento tra PR principali e branch derivato
3. Merge separato della fonte configurata **disabled** solo previa autorizzazione specifica, senza attivazione
4. Solo dopo autorizzazione distinta al rollout, rimuovere hold e `enabled=true`; verificare primo ciclo ordinario, catalogo dati e Cloudflare, stesso ID e assenza regressioni

**Nessun merge né rollout eseguito qui.** L'azienda è preparata nel branch, non nel registro `main`; lo stage dimostrato solo in staging non aumenta i verified pubblici. Workflow temporaneo rimosso dal branch dopo il test.

## Correzione delle regressioni nella CI completa

La CI completa della PR aveva individuato due incompatibilità con il nuovo concetto di azienda deliberatamente disabilitata: un test presupponeva una regione NUTS per ogni workplace NL, un altro un collector attivo per ogni azienda, senza eccezioni. Dati sistemati sul solo record Ampelmann con **NL36 Zuid-Holland e NL362 Delft en Westland** (codici presenti in `data/geography.json`); il secondo test ora richiede esattamente un collector attivo per tutti gli altri datori e zero per un'azienda in `collection_activation_hold`, con source disabilitata realmente associata. Nessuna promozione di stage o eliminazione di test. [Run di correzione #44175253219](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44175253219) success: 5 + 29 + 17 test mirati, `collector.daily provision` e `collector.pipeline --validate`; l'aggiornamento `data/companies.json` è rimasto nel branch. La CI completa della HEAD finale va letta separatamente, senza attribuire automaticamente il successo del preflight all'intera suite.
