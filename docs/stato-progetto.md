# Stato di ripresa — People Placement

## 15 novembre 2026 — correzione parsing e checkpoint, audit rendimento

Base main `a70117cee3697bcf61238a1999e32baa916dca9a`, checkout isolato
`fix-verification-null-20261115/`. WIP storico e PR delle altre sessioni preservati.
Questa sezione prevale sui vecchi prossimi passi sotto.

- Ripresa dall'incarico approvato. I quattro motivi `sequence item ... NoneType`
  di DAF/BD/Belsimpel sono osservazioni del 6–7 novembre; il verificatore è già
  corretto dalla PR #19. Corretta la precedente priorità: non sono quattro errori
  prodotti oggi. Nessuna promozione o modifica manuale del catalogo.
- Confrontate due raccolte ordinarie già concluse (14 e 15 novembre, main
  `a33e530`/`a70117c`): 19 → 19 internship HR verified freschi; 340 → 341 ID,
  nessun ID perso. Nel catalogo attuale 299 unverified e 23 closed. Ultimo
  run [#43688692857](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43688692857)
  riuscito con 18 job; publish GitHub non equivale a verifica Cloudflare.
- Tilburg: 108 record su host esterni al registro della fonte; 99 osservazioni
  del 7 novembre, inclusi i 71 vecchi motivi di budget. Non sono 71 errori odierni.
  Oggi zero record estratti da 70 pagine. Nessuna riassegnazione massiva o chiusura
  per assenza. Audit riproducibile in `docs/collection-priority-audit-2026-11-15.json`
  e `scripts/audit_collection_backlog.py` (offline, zero HTTP).
- Riprodotti e corretti in `collector/universal.py`: attributi HTML opzionali con
  valore None e checkpoint che riattivano host esterni nonostante scope
  `reviewed-hosts`. Filtrati seed/coda/record; risposta rediretta fuori scope non
  autorizza il dominio. Il trasporto esistente resta responsabile dei redirect HTTP;
  il nuovo controllo sulla destinazione è successivo alla risposta.
- Proposta restrizione DAF al dominio già revisionato `www.daf.com`, con lo scope
  esistente. Il report odierno mostrava deriva Randstad, 86 richieste / 100,46 s /
  2.332 URL pendenti e zero record. Nessun host o budget aggiunto. Attivazione non
  avvenuta: dipende da eventuale merge autorizzato, che non è stato eseguito.
- Validazione: 291 test Python con 3.12.16, 24 frontend, 64 esempi senza errori,
  generazione coverage e build riusciti. Quattro regressioni nuove, inclusi due cicli
  e canale esterno esplicitamente revisionato. Scenario sintetico: 3 → 2 letture
  nel primo ciclo, stesso record HR interno; nessun risparmio live rivendicato.
- Solo diagnostica live circoscritta: DAF root 200, pagina Tilburg problematica 403;
  4 richieste conteggiate compresi robots, 25,108 s, 123.021 byte; zero rendering,
  candidature o raccolte complete. Nessun retry del 403. Prove nel rapporto
  `docs/career-scope-diagnosis-2026-11-15.md` e JSON associato. Nuovi verified: **0**.
- Consegna sul branch `fix/career-scope-checkpoints-20261115`, senza merge,
  ampliamento rollout o cambio al gate Dynamic ATS. CI remota da verificare sulla PR.

**Primo punto indipendente successivo:** riconciliazione Overijssel, già avviata
recuperando i checkpoint storici. 171 schede nominali e piste in 25 comuni non sono
aziende uniche né copertura completa. De Nieuwe Zaak, WEBO e altri lead con stage
storici richiedono identità e prova ufficiale corrente; Elis, Wagenborg e Countus
hanno corrispondenze nel registro da riusare/verificare. Lotto geografico separato
da questa correzione, senza inventare i dettagli mancanti di OVI-05–17.
Dopo eventuale merge autorizzato misurare il primo ciclo ordinario DAF/Tilburg;
nessun controllo AI futuro aggiunto e nessuna raccolta completa manuale.

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
