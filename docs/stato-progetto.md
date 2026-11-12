# Stato di ripresa — People Placement

## 12 novembre 2026 — estensione pilota BE/IE: nuove directory con siti aziendali, non ancora autorizzate per scraping

- Recuperati checkpoint main `e7056c3351d06bedaa1f0d4a8e443f5a6e424a78`, PR #33 (draft) e PR #34 (draft); nessun merge.
- Verificate tramite visualizzazione web due pagine pubbliche che **contengono collegamenti aziendali reali**: Hogeschool PXL (`https://www.pxl.be/bedrijven-en-organisaties/jobevent/deelnemende-bedrijven/`), e Tech Industry Alliance Member Listing 2026 (`https://techindustryalliance.ie/members/`). Le precedenti liste VTK/DCU contenevano soprattutto nomi e restano materiale secondario.
- Nel campione limitato di **8 link per paese**, nessuna delle 16 imprese coincide per nome normalizzato o dominio con il registro da 1.882 aziende. Sono soltanto **16 lead in revisione**: dimensione, unicita' per gruppo, proprieta', sedi, ATS, stage HR e lingue non dimostrati. Nessun nuovo stage verified o datore operativo attestato. Evidenze: `docs/eu-discovery-web-evidence.json` con URL di origine e identificatori.
- Aggiunto alla PR #34 un parser conservativo `employer-table` con marcatore di sezione esplicito, lettura riga nome+link HTTPS e test sintetici BE/IE per evitare falsi positivi di menu/nav. Le prove sul nuovo parser NON costituiscono replay dei documenti HTML reali.
- **Accesso automatico non approvato:** l'accesso a robots.txt dei due host non e' riuscito tramite gli strumenti disponibili; condizioni del sito da controllare. Seed BE/IE inseriti con `access_reviewed=false`, nessun live run del collector, zero richieste di raccolta GitHub aggiunte, nessun cron/deploy/attivazione. Nessuna modifica a `data/companies.json`, `data/sources.json`, catalogo, policy v2, freschezza, host allowlist o Dynamic ATS #23.
- I costi/benefici del nuovo ciclo quotidiano restano da misurare **dopo** review robots/termini ed un piccolo run autorizzato: requests, seconds, rendering, lead realmente nuovi ed eventuali stage verified. Il piano 70/20/10 e' un'ipotesi di budget, non applicata ai workflow.
- Seguono CI Python/frontend/build per il commit finale PR, verifica di due cicli offline, e revisione prima di qualsiasi merge. Non confondere CI verde con produzione verificata.


## 12 novembre 2026 — secondo intervento EU discovery, indipendente dalla PR #33

- Obiettivo: acquisire incrementalmente nuove aziende da directory/fiere universitarie ufficiali e verificabili, senza ricominciare la mappatura geografica, senza integrare automaticamente ATS o aumentare il budget del collector. La PR #33 resta in bozza e non e' prerequisito per il codice di questa branch.
- Baseline main `e7056c3351d06bedaa1f0d4a8e443f5a6e424a78`, catalogo 12 novembre 20:21 UTC: **335 record, 20 open/verified HR internships, 303 unverified, 12 closed**, update partial. Aziende tentate 1.882, solo 56 collected e 31 verified-empty, 514 partial, 990 discovery-incomplete, 291 blocked/failed. Evidenza storica, non nuova verifica live.
- Script storico `scripts/map_employers.py`: gia' acquisisce aziende dalle fiere Fontys, IKOM (DE), PhDTalent (FR), ma lo script storico verifica siti aziendali su piu' host e scrive direttamente `data/companies.json`. Il nuovo passaggio isola la sola acquisizione candidati da un singolo directory host, senza seguire link di aziende nuove o scrivere ai registri.
- Modulo `collector/eu_directory_discovery.py` e CLI `scripts/eu_directory_discovery.py`: parser riutilizzati da directory gia' conosciute, parser configurabile a link di espositori esplicitamente marcati, dedup per nome e dominio contro registro e fra paesi, accodamento con provenienza e prima/ultima osservazione, conservazione candidati in caso di sorgente assente, quote per seed (max 100) e dimensione del body (max 1 MB).
- Il live richiede il flag esplicito e `access_reviewed=true` per ogni seed; Client di raccolta con robots, GET-only, host identico anche nei redirect, max 6 richieste e 20 s per directory; nessuna scansione degli host aziendali o ATS. Config iniziale DE/FR in stato non autorizzato; BE/IE hanno pagine universitarie esplorative ma nessun feed ATS dimostrato e nessun parser live approvato.
- Il risultato e' un **registro di indizi** e non annunci HR: 0 nuovi verified attestati, 0 nuove fonti abilitate, 0 crawl di produzione e 0 costi nuovi di raccolta in questa PR. Le prove con due aziende sintetiche BE/IE servono solo a dimostrare deduplica, identita' e idempotenza, non un risultato live. Non attribuire posti di lavoro dal paese della directory.
- Regressioni: URL HTTPS, host/redirect/robots gate, cap budget, casi di source assente, due cicli deterministici, nessun effetto su catalogo/policy v2, pipeline e registri. **CI PR #34 superata**: run #43306446272 e #43306529615 completati; 294 test Python, 24 frontend, valutazione su 64 esempi e build verdi. Durata test Python ~48,3 s sul run ispezionato; spesa monetaria non misurata.
- Confronto delle **472 aziende** nello snapshot storico `docs/employer-mapping-audit.json` con il registro attuale: 233 DE, 97 FR, 142 NL, **tutte gia' registrate**, quindi 0 nuovi datori da questo snapshot. Non si tratta di una nuova raccolta o di aumento verified. Il prototipo non e' un nuovo cron e non ha effettuato requests live.
- Follow-up necessario: validazione legale/tecnica di almeno una fonte BE e IE che pubblica **link verso siti employer-owned** e non soltanto nomi; cattura live circoscritta e autorizzata, approvazione ATS e integrazione con i cicli quotidiani in una PR distinta. Prioritizzare budget in base al numero di opportunita' verified per costo, non al numero di aziende.
- **Nessun merge, attivazione, schedule aggiuntivo, modifica alla produzione, aumento del Dynamic ATS pilot-v1 o nuova raccolta completa.**


## 12 novembre 2026, sera — PR per vista verified e allarme zero verificati

- Main di riferimento: `48c7e44923466f7719bdd071ab86a62de9ca58e3`. PR #30 merged, raccolta automatica post-merge [#43249156225](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43249156225) riuscita (test, 16 shard, publish). Catalogo del 12 novembre 15:47 UTC: **332 record, 21 open/verified (tutti internship HR), 299 unverified, 12 closed**, secondo policy v2 e limite di freschezza frontend di 48 ore, calcolati alle 19:49 UTC. Questi conteggi non sostituiscono il controllo del deployment Cloudflare.
- Difetto UI della PR #30: quando l'ultimo catalogo risultava stale e zero verified, la homepage cambiava `filters.unverified=true`; `urlState()` aggiungeva `?unverified=true`, che rimaneva anche dopo il ripristino. In questo stato 300+ record potevano sembrare opportunita' confermate, nonostante il testo di avviso.
- Correzione proposta: default **sempre verified-only** all'apertura e al reset, anche durante incidenti; i record storici si consultano solo scegliendo esplicitamente **Explore unverified leads** o **Include unverified**. Il parametro di stato `unverified` non e' piu' scritto o letto dalla query (incluse vecchie URL di emergenza), per cui non persiste dopo reload; altri filtri URL restano condivisibili. Banner e badge `Verification incomplete` restano visibili dove pertinenti.
- Allarme implementato in due punti **solo dopo un merge autorizzato**: il job giornaliero `publish` e il monitor GitHub Actions `stale.yml` (gia' schedulato una volta al giorno, 12:47 UTC). Creano/aggiornano la stessa Issue bot `[monitor] Zero currently verified HR internships` quando `opportunityCounts().verifiedInternships===0`, e la chiudono automaticamente quando torna positivo. Riusa la funzione di verifica policy v2 del frontend; nessuna nuova API, scansione o dipendenza. Notifiche email dipendono dalle impostazioni GitHub dell'utente, non vengono inviate dall'app.
- Test di regressione: vincolo 48h, policy v2, ruoli fuori categoria, record chiusi, stato verified-only predefinito e filtro unverified non persistente. Mantenuti catalogo e dati intatti, host/policy/robots/budget invariati; PR separata, **nessun merge, deploy o run manuale**. Dopo il merge autorizzato verificare CI, una esecuzione programmata/manuale approvata del monitor, creazione/chiusura Issue su dati controllati, il sito live e il numero di stage realmente verificati; il frontend puo' restare a zero legittimamente se non vi sono prove fresche.
- Beneficio: eliminato il passaggio automatico 21 verified → 320 risultati apparentemente aperti; costo runtime frontend nullo, nessuna richiesta extra, riutilizzo dei due workflow esistenti. I costi monetari GitHub non sono direttamente misurati in questa PR.

## 12 novembre 2026 — emergenza: zero annunci visibili e raccolta ferma

- Il run giornaliero [#43175350542](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43175350542) fallisce su **tutti i 16 shard** prima della raccolta. Log shard 0: Playwright Python `1.60.0` installato, ma `python -m playwright install --with-deps chromium` rifiuta Ubuntu 26.04 con `Playwright does not support chromium on ubuntu26.04-x64`. La fase publish non riceve alcun shard. La precedente correzione intake PR #25 e' gia' in main; il test iniziale di oggi e' verde, quindi e' un secondo problema indipendente.
- Catalogo `main` (SHA dati `3706bf28a0c7792c3c3bd4582a983cfa6534a800`): ultimo update **10 novembre 07:28 UTC**, 327 record, 22 open/verified storici, 298 unverified, 7 closed. L'ultima verifica dei 22 risale alle 07:18 UTC del 10 novembre: il controllo frontend `verifiedJob()` ha una soglia di 48 ore e dunque alle 15:23 UTC del 12 novembre **zero annunci soddisfano la verifica fresca**, senza che il catalogo sia vuoto. I 320 record non chiusi non sono automaticamente offerte ancora aperte.
- Correzione proposta in questa branch: fissare il runner del solo job `collect` a `ubuntu-24.04`, compatibile con Playwright 1.60.0; nessuna nuova dipendenza, host, fonte o budget. Nessuna raccolta manuale.
- Degradazione trasparente della UI quando l'ultimo catalogo e' stantio e non restano verifiche fresche: vista iniziale su **Include unverified**, con banner che indica esplicitamente l'assenza di candidature fresche e che si tratta di indizi storici, mai di vacancy confermate. Le preferenze URL esplicite restano rispettate; non cambia la funzione `verifiedJob`, la soglia 48h o policy v2. Regressione con orologio fisso e casi non-stale, verificato, chiuso e vuoto.
- Verifiche richieste: CI Python/frontend/classificazione/build; dopo un **merge espressamente autorizzato** eseguire il job giornaliero ordinario, controllare 16 shard, publish e aggiornamento catalogo, poi deployment Pages e UI live con timestamp e numero effettivamente verificato. In questa PR nessun merge, nessuna attivazione di produzione e nessuna verifica live di candidabilita' dichiarata.
- Costi previsti: nessuna nuova chiamata esterna dalla sola UI, runner esistente a 16 shard; monitorare richieste, durata e eventuali browser rendering del primo ciclo riuscito. Le sole correzioni non producono nuove candidature.

## 11 novembre 2026 — correzione del test che blocca la raccolta

Obiettivo permanente: più stage HR distinti e candidabili da fonti ufficiali,
aggiornati ogni giorno; prima copertura dei Paesi Bassi, poi dell'Europa.

- Main di riferimento: `0e73e9a7b26d7c674110beb50697fd29a8e2fdf1`.
- [Raccolta automatica fallita](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42978923468)
  dell'11 novembre alle 08:21 Bruxelles: il test intake imponeva 324 record,
  mentre la raccolta ordinaria precedente aveva portato il catalogo a 327.
  Collect e publish saltati; errore riprodotto offline con Python 3.12.
- [Ultima raccolta riuscita](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42774047883):
  10 novembre, 18 job riusciti. Catalogo aggiornato alle 08:28 Bruxelles:
  327 ID univoci, 22 open, 298 unverified, 7 closed; tutti i 324 ID precedenti
  conservati. Sono stati storici, non nuove verifiche live dell'11 novembre.
- Correzione limitata a `tests/test_intake.py`: eliminato il conteggio storico
  fisso, mantenuti controlli su identità, campi, ownership, policy e review blocks;
  aggiunta regressione con un record sintetico in più e replay alla data del catalogo.
  Nessuna modifica a collector, catalogo, workflow, host, budget o gate ATS.
- Lavoro isolato dal checkout storico con WIP. Accesso Git dalla shell non
  disponibile; file aggiornati recuperati tramite connessione GitHub e confrontati
  con i blob di main prima della consegna. Nessuna raccolta completa manuale.
- Validazione con Python 3.12: 287 test Python (inclusi 12 intake), 21 frontend,
  64 esempi di classificazione senza errori, validazione catalogo e build riusciti.
  Tutti i blob locali di main coincidono con quelli remoti salvo il test modificato.
  CI riportata nella PR; non confondere test con nuove opportunità.
- Consegna tramite PR circoscritta, senza merge o rollout. La produzione resta
  bloccata dal vecchio test finché la correzione non viene integrata.

Prossimo passo: revisionare e integrare la PR solo con autorizzazione specifica,
poi verificare il successivo ciclo automatico (nessun controllo futuro AI configurato).
Completare quindi le evidenze su beneficio e costi Dynamic ATS della Issue #23;
la Issue #18 resta il lavoro di miglioramento della copertura. PR #20 Drenthe
separata, non integrata. Per la mappatura riprendere i checkpoint territoriali
senza dichiarare completa una provincia sulla base dei soli datori censiti.
