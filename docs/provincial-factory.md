# Provincial Factory v1 — operatore

Implementazione offline della Issue #8. Base: `main` `118d3a9` (ultima raccolta del 7 novembre 2026), con PR #11 e #12 integrate e Issue #10 chiusa. Nessuna nuova ricerca geografica, richiesta HTTP, modifica al catalogo o servizio esterno.

## Ricognizione e riuso

- `import_province_geography.py` importa la geografia; `integrate_province.py` integra **righe già revisionate** e riusa registro e provisioning.
- `collect_province.py`, `collector.daily` e `collect.yml` raccolgono e verificano le fonti. Audit provinciali e `company_coverage.py` conservano copertura e prove. Nessuna riscrittura o modifica alla CI.
- `collector.provinces.coverage()` produce già un report per comune e datore, con opportunità verificate tramite `verified_job()`. La Factory riusa identità del registro, policy v2 e diagnostica dei blocchi; legge i file grezzi invece di fidarsi della data di generazione di un report derivato.
- Mancavano riepilogo operativo delimitato, checkpoint del workflow con invalidazione e import handoff senza promozione. La Factory aggiunge solo questi tre comandi. Le liste nel codice di `generate_all`, `collect_province.py` e UI test restano un miglioramento futuro; la Factory accetta una geografia provinciale esistente senza una nuova lista.
- PR #7 Utrecht: aperta, head `299d330`, base precedente `3ec0afd`; GitHub segnala `mergeable=false`. Nessuna modifica o riallineamento. Il checkout Flevoland con modifiche non committate è preservato; lavoro isolato in un altro worktree.

## Comandi

Dalla radice del repository, Python standard library, nessun pacchetto aggiuntivo:

```sh
python3 scripts/provincial_factory.py summary drenthe
python3 scripts/provincial_factory.py summary drenthe --source auto-scania
python3 scripts/provincial_factory.py checkpoint drenthe
python3 scripts/provincial_factory.py checkpoint drenthe --resume
python3 scripts/provincial_factory.py handoff drenthe --input docs/examples/handoff-drenthe.json
```

L'ultimo comando è una **demo sintetica**, conserva un candidato inventato soltanto nella coda locale. Per uso reale, sostituire il file con i candidati da revisionare. Dopo l'import un checkpoint precedente diventa obsoleto: eseguire nuovamente `checkpoint drenthe`.

Ogni comando accetta `--at 2026-11-07T14:30:00+00:00` per riprodurre un'analisi storica; ometterlo per una decisione operativa corrente. Una data storica non certifica freschezza attuale. Timestamp senza fuso sono rifiutati; timestamp futuri o mancanti nelle prove non contano come recenti.

Esempio sintetico dell'esperimento, allo stesso istante sui dati già pubblicati:

```text
Employers: identified 34; configured 34; complete/recent 3
Sources: configured 34; complete/recent 3; stale/invalid/missing timestamp 0
complete=3; partial=17; incomplete=9; blocked=5; failed=0; not-attempted=0
Verified HR internships: 2
```

Il riepilogo completo di esempio è in `examples/provincial-factory-drenthe.txt`: 30 righe, 1.177 byte, senza contenuti delle vacancy. Stdout standard è limitato a 60 comuni e 10 anomalie (meno di 100 righe); `--source` aggiunge due righe con stato, timestamp e puntatore alla prova, senza stamparla. I totali comunali possono sovrapporsi; quelli provinciali contano datori distinti.

## Semantica dei contatori

- **Identificato**: datore già nel registro con ricerca provinciale; non è un censimento esaustivo.
- **Configurato**: almeno una fonte abilitata. Fonte assente/disabilitata non conta.
- **Completo e recente**: tutte le fonti abilitate del datore hanno `status=ok`, `complete=true`, nessun `inventory_complete=false`, timestamp valido non futuro entro 48 ore. La completezza è quella dell'inventario osservato nel perimetro della fonte, non di tutti i posti del gruppo o della provincia.
- **Partial**: raccolta non completa con record ispezionati. **Incomplete**: nessuna completezza stabilita e nessun record ispezionato, inclusa discovery incompleta. **Blocked**: blocco esplicito o errore robots/accesso; **failed**: altro fallimento; **not-attempted**: rapporto assente. Lo stato resta distinto dalla freschezza: un vecchio inventario completo resta storico ma non conta fra i completi recenti.
- **Stage HR verificato**: `internship`, regione provinciale, datore/fonte associato e `verified_job()` della policy esistente (aperto, candidatura verificata policy v2 entro 48 ore). Sono richieste entrambe le condizioni indipendenti: verifica entro 48 ore e deadline `valid_through` non superata. Una deadline con orario resta valida all’istante esatto indicato ed è esclusa subito dopo; una data senza orario resta valida per tutta la giornata UTC indicata (anche se `--at` usa un altro fuso), fino alle 00:00 UTC del giorno successivo escluse. Una deadline assente non aggiunge un vincolo; una deadline malformata esclude il record dai conteggi. Working-student esclusi. Nessuna inferenza sulla sufficienza dell'inglese; le evidenze linguistiche restano nel catalogo.
- Anomalie: configurazione mancante, blocchi, fallimenti, date scadute/invalide, incompletezza e fonti disabilitate. Dettagli completi in `data/coverage.json`, registro, geografia e catalogo originali.

## Checkpoint del workflow

File locale: `.staging/factory/<provincia>/checkpoint.json`; storico in `checkpoints/<sha256>.json`. La directory è già gitignored: copiarla esplicitamente se serve un handoff fra macchine. Un aggiornamento usa sostituzione atomica; lo storico conserva le precedenti versioni. Usare un operatore alla volta.

Schema v1 generato dallo script: provincia, fase `offline-review`, commit Git, hash SHA-256 del codice Python in `collector/` e `scripts/` e dei requirements, hash dei cinque input letti e della coda handoff, timestamp di creazione e delle fonti osservate, attività residue, ID degli stage verificati, prossimo comando. Non contiene descrizioni delle vacancy, nomi dei candidati o dati personali. “Fonti elaborate” significa rapporti preesistenti letti offline, non nuove raccolte eseguite.

A ogni invocazione vengono ricalcolati stato e freschezza; codice e input sono controllati anche prima/dopo la lettura. Cambi di commit, codice, dati, coda, schema, integrità del checkpoint, scadenza di una verifica, superamento di `valid_through` o età del checkpoint di 48 ore ne impediscono il riuso. Il passaggio della deadline modifica gli ID verificati nello stato ricalcolato e invalida il checkpoint anche senza modifiche ai file e prima delle 48 ore dalla creazione. `--resume` lo rifiuta con exit code 2; il comando senza `--resume` lo rigenera.

- `checkpoint` riusa byte identici se ancora valido; altrimenti genera e archivia uno stato nuovo.
- `checkpoint --resume` valida soltanto uno stato esistente: se mancante/obsoleto termina con exit code 2. Non esegue il prossimo comando, né istruzioni salvate o ricevute da terzi.
- Il prossimo comando è un riepilogo riproducibile dell'attuale provincia. Le attività residue richiedono ancora decisioni e verifiche dell'operatore.

Questo è un **checkpoint del workflow provinciale**. La Factory **non implementa la ripresa di un crawler a metà**. Eventuali cache/checkpoint interni dei raccoglitori restano gestiti dalla pipeline preesistente, senza nuove garanzie di ripresa.

## Handoff ChatGPT → Codex

Schema: `provincial-factory-handoff.schema.json`; esempio: `examples/handoff-drenthe.json`. Oggetto con `schema_version: 1` e array `candidates`. Campi obbligatori esatti:

| Campo | Regola |
| --- | --- |
| `employer` | Testo della proposta, non identità accertata |
| `official_career_url` | URL HTTPS proposto, ufficialità da dimostrare |
| `municipality` | Nome esatto nella geografia provinciale |
| `evidence_url` | URL HTTPS della prova dichiarata, può riferirsi a un'Issue |
| `observed_at` | ISO 8601 con fuso, non futuro |
| `confidence` | Numero finito 0–1, non una prova |
| `review_status` | Dichiarazione esterna, mai autorizzazione |

Il validatore runtime applica lo schema senza dipendenze e aggiunge controllo di comune, fuso/data futura, credenziali negli URL e caratteri di controllo. Campi extra, incluso `command`, sono rifiutati. Un lotto invalido non cambia la coda. Il JSON Schema è documentazione interoperabile; questi controlli contestuali sono nello script.

Import in `.staging/factory/<provincia>/handoff.json`: ID deterministico sul candidato, deduplicazione delle proposte identiche, `review_status=pending`, `trust=unverified-external-data`; lo stato dichiarato è conservato come `claimed_review_status`, anche se dice `verified`. I candidati validi non verificati restano nella coda. Testi e URL non vengono eseguiti, scaricati o stampati nel riepilogo. Non copiare il testo di Issue/commenti nella shell o trattarlo come istruzioni; il commento pubblico della Issue #8 non ha determinato installazioni o scarti automatici.

Il JSON della [Issue #9](https://github.com/nightlydeveloper8/eu-hr-internships/issues/9) **non è direttamente compatibile** con questo handoff. Serve una conversione esplicita: separare datori e opportunità, racchiudere i candidati nel wrapper `schema_version`/`candidates`, selezionare i sette campi previsti e conservare gli ID/provenienza e le informazioni aggiuntive in un documento di ricerca separato. In particolare `observed_at` nella Issue contiene solo una data e `confidence` contiene etichette testuali: non inventare un orario/fuso né tradurre arbitrariamente un’etichetta in un punteggio. Se mancano prove per quei campi, lasciare la conversione in sospeso e richiedere le informazioni documentate; una futura nuova osservazione va registrata con il suo timestamp reale. L’import richiede inoltre una geografia provinciale già presente in `data/<provincia>-geography.json`, con i comuni corrispondenti: questa correzione non importa geografia, non converte né integra Flevoland e non modifica la Issue #9.

Revisione ancora manuale: controllare identità del datore, presenza/comune, ufficialità e ownership dei canali ATS, perimetro e restrizioni; preparare le righe revisionate per l'integrazione esistente. Il formato handoff non è accettato da `integrate_employers` come riga già revisionata. Per le vacancy servono raccolta e verifica specifica della candidatura secondo la policy esistente; **nessun percorso automatico dalla coda al catalogo**. Questa v1 non aggiunge un comando di approvazione né una nuova ricerca di datori.

## Verifica e limiti misurati

```sh
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 -c "from collector.pipeline import ROOT,read; from collector.company_registry import validate_registry; assert validate_registry(read(ROOT/'data/companies.json',[]),read(ROOT/'data/geography.json',{}),read(ROOT/'data/sources.json',[]))"
python3 scripts/build.py
```

211 test Python (18 della Factory, inclusi 6 nuovi test per deadline/freschezza), 20 frontend, 64 casi di classificazione senza errori; registro/catalogo validi e build riuscita. Nel desktop Node non era nel PATH: usato `/Users/dennis/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node` per lo stesso comando frontend.

Un test di PR #12 falliva anche sul checkout esportato di `main` `118d3a9`: equiparava la prima fixture sintetica alla nuova raccolta reale, ora aperta e con lingua aggiornata. Corretto soltanto il test per confrontare le due esecuzioni identiche della fixture del giorno 7; restano attivi gli assert di policy, ID, candidature, assenze, chiusure e idempotenza. Nessuna modifica alla pipeline di riconciliazione.

`provincial-factory-experiment.json` registra il confronto locale sullo stesso lotto di 34 rapporti: vecchio `coverage()['summary']` (1 riga/546 byte) e nuovo riepilogo (30 righe/1.177 byte), con tempi mediani di cinque esecuzioni. Il nuovo output è più informativo, non più corto del vecchio contatore aggregato. Il vecchio timing usa oggetti precaricati, il nuovo include letture file: non è un benchmark comparabile del crawler. Le richieste nuove sono zero in entrambi i casi; richieste e somma dei tempi della raccolta salvata sono riportate separatamente, non come durata wall-clock. Controlli CLI reali: ripetibilità, checkpoint identico, invalidazione dopo import/scadenza, handoff idempotente e hash invariati di **tutti** i file `data/*.json`.

Quota Codex non misurata: nessun risparmio percentuale dichiarato. Restano manuali ricerca preliminare, revisione delle proposte, configurazione di fonti, decisioni sulle anomalie e verifiche live necessarie. Possibili lotti futuri: registro unico delle province nei comandi esistenti e selezione mirata delle fonti da ricontrollare, senza cambiare gli standard di qualità.

## Regressione P2: deadline e checkpoint

Fixture offline: verifica `2026-11-07T15:00:00Z`, deadline `2026-11-07T15:30:00Z`, valutazione `2026-11-07T15:31:00Z`. Prima della correzione: ID verificati `['j1']`, CLI `checkpoint --resume` exit 0/`reused`. Dopo: ID verificati `[]`, `--resume` exit 2/obsoleto, comando senza `--resume` `created` con ID `[]`. Hash dei file dati della fixture identici prima e dopo il passaggio della deadline.

Test mirati riproducibili: `python3 -m unittest discover -s tests -p test_provincial_factory.py -v`. I casi `timestamp_deadline_*` e `date_only_deadline_*` controllano deadline con orario, istante esatto, giorno UTC inclusivo, fusi diversi e invalidazione/rigenerazione via CLI. I casi `verification_freshness_*` mantengono separata la scadenza delle 48 ore della verifica (anche con una deadline futura); il precedente test `vacancy_expiry_*` è stato rinominato per rendere esplicita questa distinzione. Pipeline di raccolta e policy condivisa restano invariate.
