# Recupero PR #7 Utrecht — 7 novembre 2026

Il ramo esistente `feat/utrecht-expansion` integra main `ff618eb4d6b8d0cf28d9e2fac187989c1019e219`, inclusi ownership PR #11, riconciliazione PR #12, Provincial Factory v1 PR #13 e ultima raccolta automatica. Nessuna nuova PR, provincia, ricerca provinciale o raccolta massiva. Nessun merge della PR o deployment.

## Conflitti e integrità

Il workflow [#42391091905](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42391091905) è concluso: test, 16 shard e publish tutti `success`.

Risolti individualmente nove JSON: catalogo, coverage globale e company coverage, tre report provinciali, discovery queue, integration queue e country research progress. Merge per identità stabile dei record, con priorità agli aggiornamenti concorrenti di main. Le osservazioni pubblicate, incluse le prove di verifica annidate, sono unità coerenti: i 310 record di main sono conservati identici, senza ricomporre prove vecchie e nuove. Aggiunti i record esclusivi Utrecht. Conservati identici anche i 1.833 rapporti fonte pubblicati, `employer-collection.json` e le ownership review. Contatori e code derivate sono rigenerati dagli input uniti. I conteggi delle fonti descrivono osservazioni raccolte in momenti diversi, non una nuova esecuzione completa.

Nei due conflitti frontend sono conservati sia `provincialJobs` e il relativo test Utrecht, sia `completeRecentInventory` e i test di lingua/KPI provenienti da main. Le correzioni backend #11/#12 e il codice Factory restano attivi; sono mantenute anche le verifiche Utrecht di titolo, requisition, form e chiusura Watson e il selettore Domino’s opt-in.

L’audit deterministico [audit_utrecht_recovery.py](../scripts/audit_utrecht_recovery.py) verifica: zero ID persi fra i 310 pubblicati e i 321 originali; 322 record uniti; geografia Utrecht identica, 26 comuni e 104 località uniche; stessi 51 datori ricercati; datori/fonti main e sedi fuori Utrecht conservati; stessi ID verificati per Fryslân, Groningen e Drenthe. Risultati in [utrecht-recovery-integrity.json](utrecht-recovery-integrity.json).

Il checkout originale Flevoland non è stato modificato. Sono confrontati gli hash dei 34 file locali modificati o non tracciati; il recupero usa il clone Utrecht già presente nel workspace.

## Sei candidature ricontrollate, quattro stage verificati

Controlli del 7 novembre 2026 fra le 16:40 e le 16:43 UTC (17:40–17:43 Zurigo), senza invii. Prove correnti, hash delle risposte e collegamenti sono in [utrecht-recovery-vacancies.json](utrecht-recovery-vacancies.json). Nessuna prova è stata sostituita con una semplice risposta HTTP 200.

| Datore / stage | Esito attuale | Inizio pubblicato | Lingua di lavoro |
| --- | --- | --- | --- |
| Remia — HR Stagiair(e), Den Dolder | Verificato, form candidato della stessa vacancy | Febbraio 2027, almeno quattro mesi | Requisito esplicito non accertato |
| Berenschot — Advies & Onderzoek, Utrecht | Verificato, form della stessa vacancy; link ATS accertato sulla pagina ufficiale | Non specificato | Requisito esplicito non accertato |
| AS Watson — HR Business Partner Kruidvat, Renswoude | Verificato, form renderizzato con titolo e requisition corrispondenti | Febbraio 2027, almeno cinque mesi | Requisito esplicito non accertato |
| AS Watson — Employer Branding en Recruitment, Renswoude | Verificato, form renderizzato con titolo e requisition corrispondenti | Febbraio 2027, circa cinque mesi | Requisito esplicito non accertato |
| Trunkrs — HR Stagiair, Woerden | Non verificato: canale attivo, intake corrente/futuro non confermato | 1 settembre 2026, passato | Olandese **e** inglese richiesti |
| Domino’s — Meewerkstage HR, Nieuwegein | Non verificato: istruzioni email presenti, anno/intake non confermato | Settembre senza anno | Olandese richiesto |

Tutti e sei gli annunci sono in olandese; la lingua dell’annuncio non prova un requisito lavorativo. Per nessuno è documentata la sufficienza del solo inglese. La policy v2 resta invariata, inclusa la freschezza di 48 ore. Il catalogo riporta separatamente le date di intake e la UI le mostra; per Trunkrs e Domino’s la motivazione di revisione resta visibile anche nelle raccolte successive. Due voci `needs-verification` nel registro delle revisioni impediscono la ripromozione automatica sulla sola base di un modulo attivo; un test esegue il vero `finalize` con nuove prove tecniche simulate e controlla l’esito non verificato.

La configurazione Berenschot originaria non autorizzava l’host della vacancy Recruitee già documentata. Il link ufficiale alla stessa candidatura è stato ricontrollato ed è stato aggiunto il solo host `berenschot.recruitee.com`, sia alla fonte sia all’override Utrecht. Non sono state allargate indiscriminatamente le allowlist.

## Factory e checkpoint

Riepilogo offline in [utrecht-recovery-factory.txt](utrecht-recovery-factory.txt): 51 datori identificati/configurati, due inventari completi e recenti; stati 2 completi, 35 parziali, 10 incompleti, 2 bloccati e 2 falliti. Quattro stage verificati. Nessuna nuova richiesta di rete dal riepilogo. Lo zero dei candidati handoff riguarda la sola coda Factory: non elimina le opportunità non verificate del catalogo o il percorso studenti generico nel report provinciale.

`checkpoint --resume` rifiuta lo stato mancante/obsoleto con exit 2. Dopo la creazione di un checkpoint, il cambiamento dei dati di verifica lo invalida realmente; rigenerato il checkpoint, `--resume` lo riusa correttamente. Il commit cambia nuovamente l’identità del checkpoint e richiede rigenerazione. I checkpoint locali non vengono pubblicati né scambiati per una ripresa del crawler.

## Validazione e limiti

- 219 test Python e 21 frontend superati.
- Valutazione: 64 casi, zero falsi positivi e zero falsi negativi nel campione.
- Test mirati: daily integrity 8, ownership 9, riconciliazione Ennatuurlijk 9, tutti superati; inclusi anche nella suite completa.
- Catalogo, registry e geografia validati; audit di conservazione superato; `git diff --check` pulito.
- Build statica riuscita. Chromium: quattro province a 1280 e 390 px, filtri e righe comunali, nessun errore di pagina o overflow; [risultati](utrecht-recovery-ui.json).

Le 49 anomalie di raccolta della Factory restano visibili; completezza geografica e presenza aziendale non equivalgono a inventario completo di vacancy. I sei controlli puntuali non aggiornano artificialmente la completezza delle fonti. Disponibilità e prove hanno durata limitata; Trunkrs e Domino’s richiedono una nuova evidenza esplicita sull’intake e revisione manuale prima di rimuovere il blocco. La CI sul commit della PR viene verificata e riportata nella descrizione GitHub; nessuna pubblicazione di produzione è eseguita.
