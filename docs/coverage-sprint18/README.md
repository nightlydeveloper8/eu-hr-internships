# Coverage Improvement Sprint #18 — primo lotto

Issue: https://github.com/nightlydeveloper8/eu-hr-internships/issues/18 · base `main` **6d97637**.

## Risultato misurato

**Una candidatura ufficiale in più verificabile automaticamente**, già presente nel catalogo: [HRBP Intern – February 2027, Hunter Douglas](https://job-boards.greenhouse.io/talentprograms/jobs/8073628003), Rotterdam. Nessun nuovo annuncio HR scoperto.

| Misura | Prima | Dopo |
|---|---:|---:|
| Aziende preselezionate / diagnosticate live | 25 / 8 | 25 / 8 |
| Candidature note confrontate sullo stesso snapshot | 8 | 8 |
| Verificate policy v2 nel campione | 0 | 1 |
| Ancora senza prova di candidatura | 8 | 7 |
| Candidate-to-verified | 0% | 12,5% |
| Catalogo completo **nel replay**: open / unverified / closed | 23 / 300 / 1 | 24 / 299 / 1 |
| Copertura aziendale completa dimostrata nel lotto | 0 | 1 |

Baseline del lotto: `partial=8`, `blocked-or-failed=0`, `discovery-incomplete=0`, `collected=0`, `verified-empty=0`. Il replay dell'inventario Greenhouse completo porta **Hunter Douglas da partial a collected**: 16 elementi pubblicati, 13 vacancy dopo l'esclusione di 3 programmi generici con `internal_job_id=null`, una candidatura HR. Per le altre sette aziende abbiamo diagnosticato una vacancy, senza rieseguire l'intero inventario: nessun aggiornamento di copertura completa o closure per assenza è rivendicato. Nessuna candidatura del campione è dichiarata chiusa sulla sola base di 404/redirect.

Il catalogo di produzione, le fonti e le aziende **non sono modificati**. Il delta globale +1 è ottenuto con `process_source` e `finalize` su risposte ufficiali archiviate, con codice prima/dopo e catalogo storico identici; gli snapshot di test non vengono usati dal collector notturno per rinnovare verifiche. La verifica è stata inoltre **confermata live alle 22:58 UTC del 7 novembre 2026** rileggendo inventario e form ufficiali con il codice corretto (manifest `confirmation/result.json`, 4 chiamate residue). La successiva raccolta ordinaria dovrà acquisire nuove prove live.

## Selezione riproducibile

Join per ID esistenti tra aziende, fonti attive, catalogo, employer-collection e integration queue; controlli sui report company-coverage e sulle code discovery/channel. La presenza NL è una **candidatura geografica dell'azienda**, non prova che ciascuna vacancy sia in NL. La provincia è riportata solo quando presente nei workplaces registrati; non viene inferita.

Si escludono blocchi già documentati (robots, 403/406/429, CAPTCHA), host non approvati, aggregatori/portali condivisi con ownership da chiarire, canali email e fonti già fallite. Esclusioni dettagliate in `shortlist.json`; tra queste Rijksoverheid/CJIB, Rijkswaterstaat, IKEA, Scania, SThree, SmartRecruiters e Tilburg University. Non sono state interrogate.

Punteggio euristico, non probabilità statistica: +100 errore `NoneType` nei form, +40 candidatura non riconosciuta, +20 almeno un candidato unverified, +10 singolo adapter, +10 nessuna URL pendente, +10 al massimo 10 pagine nel run precedente. Ordinamento per punteggio decrescente, pagine crescenti, ID. Si privilegiano errori riproducibili e riuso con costo osservato basso; le ragioni e le componenti del punteggio sono nel JSON. Gli importi delle richieste non stimano vacancy ancora sconosciute.

Le prime otto aziende costituiscono il lotto. Le altre 17 restano coda ordinata: nessuna lettura live o modifica ai loro dati. “HR” include stage, working student e traineeship già classificati; non rappresenta nuove offerte.

| # | Azienda | Provincia registrata | Score | Stato | HR noti | Pagine / pendenti precedenti |
|---:|---|---|---:|---|---:|---:|
| 1 | **Kenonz** | NL12 | 150 | partial | 1 | 9 / 0 |
| 2 | **DAF Trucks** | non registrata | 130 | partial | 2 | 20 / 2270 |
| 3 | **BAS Group** | NL41 | 90 | partial | 1 | 0 / 0 |
| 4 | **Danone** | NL32, NL35 | 90 | partial | 10 | 0 / 0 |
| 5 | **Hunter Douglas – Talent Programs** | NL36 | 90 | partial | 1 | 0 / 0 |
| 6 | **Sijperda Verhuur** | NL12 | 90 | partial | 1 | 0 / 0 |
| 7 | **HB RTS** | NL35 | 90 | partial | 2 | 1 / 0 |
| 8 | **NNCZ** | NL13 | 90 | partial | 1 | 1 / 0 |
| 9 | Center Parcs | NL13 | 90 | partial | 2 | 2 / 0 |
| 10 | Philips | NL12 | 80 | partial | 1 | 8 / 110 |
| 11 | Econvert Water & Energy B.V. | NL12 | 80 | discovery-incomplete | 4 | 16 / 0 |
| 12 | Bentacera | NL12 | 80 | partial | 1 | 23 / 0 |
| 13 | Elevation Group B.V. | non registrata | 80 | discovery-incomplete | 1 | 27 / 0 |
| 14 | Oosterwolde Plastic Industrie B.V. | NL12 | 80 | partial | 1 | 30 / 0 |
| 15 | Politie Nederland | NL12 | 70 | partial | 1 | 27 / 12 |
| 16 | Manpower | NL12 | 70 | partial | 1 | 30 / 3403 |
| 17 | Randstad Groep Nederland | NL12 | 70 | partial | 1 | 70 / 602 |
| 18 | Technicum | NL12 | 70 | partial | 2 | 70 / 1048 |
| 19 | Royal A-ware | NL12, NL35 | 50 | partial | 2 | 0 / 0 |
| 20 | DeFabrique Holding | NL35 | 50 | partial | 1 | 1 / 0 |
| 21 | AXS logistiek | non registrata | 50 | partial | 1 | 8 / 0 |
| 22 | Yobbers | NL12 | 40 | partial | 1 | 9 / 562 |
| 23 | Centraal Beheer Achmea | NL12 | 40 | partial | 1 | 64 / 0 |
| 24 | Unilever | NL36 | 30 | partial | 1 | 0 / 0 |
| 25 | AS Watson Benelux | NL35 | 30 | partial | 2 | 1 / 0 |

## Correzione riutilizzabile

Un'unica causa strutturale: **lettura incompleta della semantica dei form** in `applicant_form`.

- Gli attributi HTML senza valore (`novalidate`, `required`) sono rappresentati come `None`: concatenarli provocava `TypeError`. Ora si leggono solo valori testuali degli attributi del form.
- I form ATS moderni associano i controlli a `id`, `autocomplete` e `aria-label`, pur omettendo `name`. Ora questi attributi concorrono al riconoscimento di email, nome/CV, sempre nello stesso form con submit abilitato.

La policy rimane v2: richiesta corrente, host approvato, URL e titolo della stessa vacancy, controllo deadline, form candidato effettivo e submit disponibile. Nessun URL, titolo, ID o stato verified è codificato per una vacancy particolare. Restano invariati ownership, alias, intake, date, cache e review block Trunkrs/Domino's e VAR/Meerpaal.

## Diagnosi live circoscritta

Budget: massimo 8 chiamate logiche e 45 secondi per fase/azienda; nessun browser, form inviato, login o servizio a pagamento. In totale **26 chiamate logiche Client.request**, incluse robots.txt, per 8 aziende. I redirect HTTP interni a urllib non sono contati separatamente. Le durate sotto includono robots quando annidate nella lettura principale; non sono benchmark del collector completo. Provenienza, URL finali, timestamp UTC, eventi e SHA-256 dei body sono nei manifest `tests/fixtures/sprint18/*/capture.json`. I body sono compressi senza timestamp gzip.

| Azienda | Chiamate | Secondi osservati | Esito dopo il fix / residuo |
|---|---:|---:|---|

| bas-group | 4 | 3.565 | CTA a frammento presente, form non esposto nel documento; resta unverified. Lettura del frammento acquisita prima di escludere duplicati nello script. |
| daf-trucks | 2 | 1.69 | Redirect alla pagina generale Vacancies; identità non dimostrata. Nessuna chiusura o promozione. |
| danone | 2 | 1.442 | 404 sulla vacancy già nota; resta senza prova, nessuna ricerca manuale sostitutiva. |
| hb-rts | 2 | 0.699 | Form newsletter/search, nessun form candidato: correttamente esclusi. |
| hunter-douglas-talent-programs | 8 | 4.083 | Form candidato nella stessa vacancy, email/nome/CV identificati da id; verified. Inventario pubblico completo. |
| kenonz | 4 | 1.891 | Eliminato TypeError; CTA con Job ID corrispondente, ma destinazione generica Apply senza form/titolo specifico: resta unverified. |
| nncz | 2 | 1.118 | Titolo corretto, nessuna candidatura disponibile nella risposta HTML. |
| sijperda-verhuur | 2 | 0.604 | CTA JavaScript a pulsante, nessun form HTML: resta unverified; nessun endpoint indovinato. |

Hunter Douglas pubblica “Proficient in English (additional languages are a plus)”: inglese esplicitamente richiesto, **sufficienza dell'inglese non confermata** dal classificatore. Febbraio 2027 nel titolo non viene trasformato in intake confermato. Gli altri requisiti espliciti già registrati sono nella shortlist JSON, senza inferenze dalla lingua dell'annuncio.

## Riproduzione e test

```sh
python3 scripts/coverage_sprint18.py          # ranking sui dati della base
python3 scripts/replay_sprint18.py            # confronto offline su snapshot storici
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 scripts/company_coverage.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

Solo per una nuova acquisizione autorizzata, in una copia senza capture preesistenti: `coverage_sprint18.py --capture`, `--capture-linked`, `--capture-inventory`, quindi `--confirm-live` per la sola fonte riuscita; lo script rifiuta la sovrascrittura silenziosa degli snapshot principali. Non usare il replay come raccolta live.

Risultati locali: **252 test Python** (9 nuovi), **21 frontend**, classificazione **64 esempi / zero falsi positivi e negativi**, registry/coverage **1.882 aziende tutte monitorate**, catalogo valido, build statica riuscita. Il runtime Node incluso nell'app è stato usato perché Node non era nel PATH. I timestamp generati dalle validazioni di coverage sono stati ripristinati: nessun aggiornamento dati estraneo nella PR.

I nuovi test coprono fixture ATS ufficiali, attributi booleani, controlli senza name, form separati/newsletter/disabled, inventario troncato rispetto al totale (nessuna falsa completezza di pagina), titolo/redirect/deadline errati, challenge e cache insufficiente. Due raccolte successive dell'inventario reale danno lo stesso risultato; due finalize mantengono ID, ownership, prima scoperta e tutti gli open esistenti. I sette fallimenti restano fallimenti. Il catalogo storico compresso rende l'esperimento indipendente dagli aggiornamenti notturni. La suite esistente copre inoltre paginazione, alias, dati legacy, intake e review block.

## Residui

- Le 17 aziende dalla posizione 9 alla 25 rimangono seconda tranche; i costi e motivi nel JSON guidano il prossimo lotto.
- Nel lotto attuale, valutare solo automatismi di lettura autorizzata per moduli JS e inventari; le nuove evidenze 404/redirect di Danone/DAF riducono la priorità di ripetere quelle URL. Kenonz non ottiene verified sulla sola query con ID. Nessuna ricerca manuale, email o CAPTCHA richiesto.
- Nessuna nuova provincia, raccolta massiva, merge o deployment. La modifica entra nel percorso notturno esistente dopo review/merge; nessuna gestione manuale delle singole vacancy è introdotta.
