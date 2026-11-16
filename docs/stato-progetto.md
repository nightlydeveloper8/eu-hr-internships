# Stato di ripresa — People Placement

## 16 novembre 2026 — lotto 07 CY/GR/HR/MT, GET pilot misurato senza fonti attive

**Risultato reale:** 8 indizi esaminati in 4 paesi, tre vacancy HR di fonte ufficiale con identità precisa ma **0 nuove candidature verified policy v2** e **0 nuove fonti enabled**. Baseline di produzione invariata nell'ultimo catalogo letto: **362 record, 28 stage HR open/verified in 5 paesi, 1 working student DE** (16 novembre 16:51:25 UTC). Nessun rollout né aggiornamento del catalogo da questo lotto.

**Piste prioritarie e prove:** Brainstorm Hospitality **CY** HR Intern Larnaca, Teamtailor ID **7649525**, inventario aziendale corrente e pagina specifica; form dinamico non leggibile in HTML statico. iKnowHow **GR** HR Intern (Talent Acquisition), Workable ID **3F368EAC02**, collegamento corporate→tenant esatto; form HTML statico assente e feed del board non stabilito. Marriott Westin **MT** HR Intern, ID **26132701**, listing aziendale e CTA Oracle con job ID conservato, ma l'HTML della pagina Oracle non mostra campi per candidarsi. Requisiti iKnowHow inglese fluente e iscrizione a istituto greco, Marriott stage 5–6 mesi/€835 lordi mensili. **Croazia:** Rimac People Operations Intern non appare nel board attuale nonostante la pagina vecchia; PLIVA AskHR scaduta il 9 novembre ed è working student, non stage. Xara MT HR Intern solo su mirror, Hilton MT solo fonte terza, Stoiximan CY programma HR senza vacancy corporate attuale: nessuno ammesso.

**Preflight GET reale e limitato:** su ramo separato di GitHub Actions, [run #43918927512](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43918927512) **success**. Client originale BudgetClient con controllo robots attivo e allowlist redirect esatta. **11 richieste logiche totali**, di cui Brainstorm 3, iKnowHow 3, Marriott/Oracle 5; **1.356.253 byte letti** e **5,403 secondi-fonte cumulati**, **0 rendering, 0 HTTP 429**. Le 3 vacancy hanno HTTP 200, ma **nessuna pagina ha mostrato campi e submit anonimi abilitati**. La guardia robots ha consentito *queste URL*; il dump non registra direttive/status dei robots, né prova accesso all'intero sito. L'ambiente locale aveva DNS non disponibile, perciò la prova è stata eseguita sul runner; solo GET, niente login, CAPTCHA, POST o candidature. Nessuna fonte attivata: **incremento richieste quotidiane 0**, costo effettivo del singolo test 11 GET e 1,36 MB, costo monetario non misurato.

Prove in [BATCH-07-REVIEW.md](eu27-expansion/BATCH-07-REVIEW.md), [JSON indizi](eu27-expansion/batch-07-review-2026-11-16.json) e [JSON del probe live](eu27-expansion/batch-07-live-preflight-2026-11-16.json); il workflow pilota NON è su main, non è programmato come raccolta quotidiana. Modificati solo documenti e stato, PR dell'attività da verificare CI/merge. Le PR #41 e #46 restano draft indipendenti e non ready.

**Primo punto incompleto:** individuare per Teamtailor/Workable un percorso ufficiale e riutilizzabile verso il vero modulo anonimo senza abilitare indiscriminatamente renderer o variare policy v2; Oracle resta blocked/unverified quanto a form. In HR trovare una vacancy corrente sostitutiva. **Prossimo lotto 08: AT/DE/DK/FI/PL/SE**. Non dichiarare mappatura completa dei quattro paesi.


## 16 novembre 2026 — lotto 06 (EE/LV/LT/BG/IT/HU/SI/SK), audit UE27 senza rollout

**Baseline dopo PR #47:** workflow #43909444414 (raccolta) e #43909444577 (validazione) riusciti. Catalogo main 16 novembre 16:51:25 UTC: **362 annunci, 28 stage HR verified in cinque paesi, 1 working student DE, 306 unverified, 27 closed**. PR #47 squash merge 5364825: fix host 429 e messaggi filled. Nessun nuovo stage verificato attribuibile al lotto 06.

**Ricognizione lotto 06:** 8 paesi, 10 indizi, 9 datori, **0 nuove fonti abilitate / 0 nuove candidature policy v2**. Piste ancora non ammesse: DIGI MEDIA LV (ruolo HR e form visibile sulla pagina aziendale), Girteka LT (stage HR ma candidatura /talentcommunity incompleta), CCEP BG (People Services 2027, inglese e tedesco, form non stabilito), Heritage IT (due HR stage nel board Greenhouse corrente, ID 4945490101/4945390101, moduli presenti ma manca link dal sito corporate al tenant esatto). Altre cinque evidenze: Gameloft BG candidatura expired; Bolt EE scadenza esterna passata; Betsson HU ruolo non presente nel board corrente; Danfoss SI rimosso; Adient SK working student e non stage.

Prove in [BATCH-06-REVIEW.md](eu27-expansion/BATCH-06-REVIEW.md) e [JSON](eu27-expansion/batch-06-review-2026-11-16.json). [Piano EU27](eu27-expansion/EU27-MAPPING-PLAN.md) assegna i 27 paesi ai lotti 06–10 senza sovrapposizioni, ma pianificare non equivale a mappare. Nuovo script audit offline dei 27 paesi e test con filtro v2/freschezza, nessuna nuova esecuzione programmata. Nessuna copertura nazionale dichiarata completa.

**Costi:** 0 nuove richieste collector, 0 rendering e 0 carico quotidiano aggiuntivo perché nessuna fonte attivata. Ricerca web svolta, ma byte/durata/richieste web non misurate come costi collector. Accesso HTTPS diretto al preflight bloccato da DNS e robots dei canali prioritari non disponibili al tool: nessuna prova completa di inventario/candidatura.

**Primo punto incompleto:** preflight limitato con BudgetClient e robots su DIGI MEDIA LV e Heritage IT (una fonte, due posizioni), poi Girteka LT se il link arriva a modulo stesso annuncio. Misurare richieste, secondi, byte, deduplica e ripetibilità su due cicli. Review CI della PR audit e procedere col lotto 07 CY/GR/HR/MT senza promuovere indizi bloccati.

## 16 novembre 2026 — lotto 04 attivo e produzione verificata

**Risultato reale: 26 → 28 stage HR verificati, più 1 working student in Germania.** Tre nuove fonti ufficiali attive: Hotel TwentySeven (stage NL, Amsterdam), Bundl (stage BE, Antwerp) e Franklin Institute (posizione mista DE, München, conteggiata working student). Nessuna candidatura inviata, nessuna raccolta completa manuale, nessun gate Dynamic ATS o schedule ampliato.

L'utente ha autorizzato prossimo lotto e squash and merge autonomi del lavoro pronto: **PR #44 merged `464d87c` e PR #45 merged `8ab36e9`**. CI PR45 head `f406f16`: 413 Python, 26 Node, 64 esempi, coverage e build; run #43901346530/#43901406534 e dopo merge #43901780674 riusciti. PR #41 resta draft non pronta e non viene integrata. Autorizzazione agli squash pronti da mantenere senza richiederla nuovamente.

**Primo ciclo ordinario dopo #45: [#43901780885](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43901780885), tutti i 18 job riusciti.** Dati main `d764bececa798a089893754afde022dff9a2f90e`, catalogo 16:08:16 UTC: **356 → 361 record, tutti i 356 ID precedenti conservati**, tre nuove candidature verificate; due altre aggiunte automatiche TNG/Yobbers restano unverified. Tutte le vecchie opportunità verificate conservate. Cloudflare Pages riuscito sullo stesso commit dati; GET pubblico 200 alle 16:09:32 UTC, 888.716 byte identici alla pubblicazione, hash nel rapporto. Il ciclo #44 #43898333473 era riuscito con 26 stage invariati; BSH inglese ora documented, sufficienza da solo unknown.

Costi di produzione delle tre fonti: **15 richieste logiche / 8,84 secondi-fonte / 3.768.689 byte / zero rendering**. Ciascuna usa 5 richieste, entro massimo 12/45 s, solo il proprio host Recruitee. Inventari 24+6+11 offerte, un match verificato ciascuno; completezza solo del feed restituito, closure_complete=false. Nuove aziende/fonti applicate atomicamente. Correzione riutilizzabile del client: documenti HTML, API JSON esplicito, robots testo semplice; identità bot, host, robots e budget preservati. Nessun catalogo promosso manualmente.

Bundl richiede inglese+olandese; Franklin tedesco+inglese nel testo, costrutto non ancora estratto; Hotel lingua unknown. Nessuna offerta dichiarata English-only, nessuna dimensione PMI inferita. Opportunità verificate per paese: NL 18 stage, FR 5, BE 3, ES 1, PT 1; DE 1 working student e 0 stage. **UE27 ancora incompleta**, non presentare sei paesi con qualche opportunità come sei mappature complete. Quadro dei 27 paesi in [COUNTRY-OUTCOMES.md](eu27-expansion/COUNTRY-OUTCOMES.md).

Ricerca/ammissione lotto 04: 52 richieste/26,114 s/11.849.666 byte, nove query web, zero rendering (include letture CMS errate e asset JS Social Hub da circa 4,7 MB, escluso dal monitoraggio). Kickmaker 403 intermedio, Zero Motorcycles e Social Hub ownership incompleta, Settels inizio febbraio 2026 e controllo datore fallito: nessuno attivato.

Lotto successivo preparato durante il ciclo: CZ/RO/SE/IE, 27 richieste/14,721 s/1.222.790 byte e 14 query, zero nuove fonti/verified. Manifesto CZ: corporate→tenant esatto confermato, 8 link, stage non retribuito ceco+inglese; modulo non stabilito, cinque URL distinti 429. Nessun ulteriore accesso oggi; il lettore generico continua altri URL dopo primo 429, difetto da correggere prima di ammettere questo canale. Singola offerta Continental RO esplicitamente chiusa; Fidelity IE 404, nessun retry; Electrolux SE JR81378 con sede strutturata Stockholm, candidatura/inventario incompleti. Non contare questi indizi come stage candidabili.

Prove: [rapporto di produzione](eu27-expansion/batch-04-first-production-cycle-2026-11-16.json), [review lotto 04](eu27-expansion/BATCH-04-REVIEW.md), preflight lotto 05 e `next-structural-priorities-2026-11-16.json`. **Primo punto incompleto:** verificare inventario/candidatura Electrolux SE e cercare sostituti ufficiali per le due offerte RO/IE non disponibili, senza ripetere i blocchi del giorno. In parallelo diagnosi della causa comune dei link senza identificativo partendo dai 13 record L'Oréal: sono record unverified, non 13 recuperi promessi; totale 36 di quel motivo nel catalogo di baseline. Nessun nuovo controllo AI futuro configurato.

## 16 novembre 2026 — lotto DE/DK/PL/FI verificato, nessuna nuova fonte ammissibile

**Quattro indizi → zero nuove fonti attivabili, zero nuovi stage aggiunti.**
Consegna nella [PR #44](https://github.com/nightlydeveloper8/eu-hr-internships/pull/44),
ramo `review/eu27-de-dk-pl-fi-20261116`, base main `876794a`.
Rapporto [BATCH-03-REVIEW.md](eu27-expansion/BATCH-03-REVIEW.md) e
[evidenze JSON](eu27-expansion/batch-03-review-2026-11-16.json).

Constructor: 28 posizioni nel feed, uno stage HR a Bremen, ID 4772353101,
modulo stesso titolo/ID visibile abilitato. Marchio e sito coerenti, ma nessun
collegamento ufficiale azienda→tenant esatto stabilito nelle pagine consentite.
Careers usa l'endpoint pubblicato `/api/v2/jobs`, vietato da robots: contenuto
non scaricato. Proposta incompleta fuori runtime in
`batch-03-constructor-pending-proposal.json`; non integrare sulla sola prova del
modulo o del backlink ATS→azienda. Limite di 12 richieste raggiunto; stop su questo caso.

FirstMind: 38 posizioni nel feed, Global Talent Intern assente, zero HR studenti
classificati; non è un errore attuale del filtro e non si promuovono ruoli sales.
Saint-Gobain: scheda HTTP 403 dopo robots 404, nessun retry; inventario e
candidatura sconosciuti, datore già censito. Barona: JobPosting 116361 a Tampere,
collegamento corporate→Barona Careers confermato; pagina “Sign in and Apply”,
nessuna candidatura anonima stabilita e nessun login. Inglese e finlandese
elencati, non una proposta di lavoro con solo inglese.

Preparati due miglioramenti riutilizzabili: forme polacche Stażysta/Stażystka
riconosciute, “staż pracy” distinto dall'esperienza richiesta in ruoli permanenti;
“Inglés nivel B2” riconosciuto con esclusione di corsi/CV e gestione di
opzionalità/negazione. Replay BSH: requisito inglese unknown → documented,
**inglese sufficiente da solo resta unknown**, nessuna disponibilità o timestamp
rinnovati. La lingua del CV e i corsi Constructor restano esclusi.

**407 test Python, 26 Node, 64 esempi e build passati**, 12 nuove regressioni.
Costo verifica: **22 richieste logiche, 10,940 secondi-fonte cumulati,
1.962.584 byte, zero rendering**, più cinque query web. Budget per datore 12/45 s
rispettato. Catalogo/registri/workflow invariati, nessun gate/host di produzione
esteso, nessun merge o attivazione; baseline **26 stage verificati** preservata.

**Primo punto incompleto:** review della PR con i filtri corretti; eventuale
merge richiede autorizzazione specifica. Nuovo lotto con collegamento pubblico
datore→ATS e candidatura anonima controllati in anticipo. Constructor resta
incompleta per ownership; non spendere una nuova sessione soltanto sui blocchi
di questo lotto e non aggirare 403/API vietate/sign-in.

## 16 novembre 2026 — BSH attiva, primo ciclo e pubblicazione verificati

**Risultato reale: 25 → 26 stage HR aperti e verificati (+1 distinto), primo
stage verificato in Spagna.** PR [#43](https://github.com/nightlydeveloper8/eu-hr-internships/pull/43)
integrata con squash su autorizzazione specifica dell'utente: head attivazione
`d0903bd01f75617aeb3453adcb5234b958f55119`, merge
`e101e7415b08c14b543a259053f1e67719310b5e`. CI e preview verdi, nessuna review
bloccante; 395 test Python, 26 Node e build superati.

Azienda `bsh-electrodomesticos-espana` e fonte `index-bsh-es` aggiunte insieme:
1.892 → 1.893 aziende, 1.936 → 1.937 sorgenti. Fonte abilitata su main,
unico host `jobs.bsh-group.de`, budget 10 richieste/75 s, crawl-delay 10 s;
provisioner idempotente. Nessun altro gate, host di produzione o schedule esteso.
Rollback: revert congiunto di azienda e fonte; disabilitare solo la fonte
lasciando l'azienda attiverebbe il fallback generico.

Raccolta ordinaria avviata automaticamente dal merge, evento push:
[run 43878488280](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43878488280),
**18 job riusciti**, publish `946ebb7911641301defebd6e2d4d403210ead018`.
Catalogo del 16 novembre 14:56:56 ora svizzera (13:56:56 UTC): **352 → 355 ID**,
tutti i 352 precedenti preservati, nessun precedente stato modificato.
Un nuovo stage verificato: BSH, Prácticas Recursos Humanos - Formación,
Zaragoza, ID 46112. Gli altri due nuovi record (FITZ traineeship e Rohde & Schwarz
working student) restano **unverified** e non aumentano le opportunità disponibili.
Conteggio frontend confermato: **26 verifiedInternships**, zero altri tipi verificati.

BSH nel ciclo: 15 posizioni effettive, una corrispondenza HR con prova live
policy v2, inventario completo nello scope revisionato, nessun errore;
**5 richieste logiche, 61,16 secondi-fonte, 109.503 byte**, budget rispettati.
Zero rendering nel percorso BSH; non è il tempo a muro dell'intero workflow.
Chiusure per assenza ancora disabilitate; un solo ciclo ordinario non prova
il refresh seguente o disponibilità futura. Annuncio spagnolo, inglese B2
documentato manualmente; la frase B2 non è ancora riconosciuta dall'estrattore,
solo inglese non stabilito: nessun tag forzato.

Cloudflare Pages success sul commit dati `946ebb7`, deployment
`f093bcb5-b3be-4c5c-82ec-b2967fa7a32b`. Catalogo pubblico GET HTTP 200 e identico
byte per byte al file Git: pubblicazione e distribuzione effettivamente verificate.
Nessuna modifica manuale del catalogo, importazione di replay, workflow_dispatch,
raccolta completa manuale o nuova automazione AI. La pianificazione quotidiana
preesistente resta invariata (06:17 UTC, 07:17 ora svizzera in questa data).
Report: [bsh-first-production-cycle-2026-11-16.json](eu27-expansion/bsh-first-production-cycle-2026-11-16.json);
autorizzazione/baseline/rollback: [bsh-activation-2026-11-16.json](eu27-expansion/bsh-activation-2026-11-16.json).

Stage verificati osservati: NL 17, FR 5, BE 2, PT 1, ES 1. Sono cinque paesi con
opportunità recenti, non cinque mappature nazionali complete; gli zeri negli
altri paesi non provano mercati vuoti. Durante l'attesa preparati quattro indizi
ufficiali per DE/DK/PL/FI in
[next-uncovered-country-leads-2026-11-16.json](eu27-expansion/next-uncovered-country-leads-2026-11-16.json),
8 query di ricerca, zero feed letti o nuove fonti attivate. Saint-Gobain è già
censita e richiede un nuovo canale-paese, non una nuova azienda.

**Primo punto incompleto:** verificare in lotto identità, inventario, candidatura
e lingue dei nuovi canali DE/DK/PL/FI, priorità agli indizi HR espliciti già
compatibili col classificatore. FirstMind richiede prova delle mansioni HR,
Saint-Gobain review della forma polacca Stażysta/Stażystka. Mantenere fuori
runtime le proposte fino a nuova autorizzazione specifica. Il secondo ciclo BSH
compete alla raccolta ordinaria; nessun controllo AI futuro promesso.

## 16 novembre 2026 — lotto IT/ES/PT/AT verificato, BSH preparata senza rollout

**Otto indizi → una nuova integrazione ammissibile (BSH Spagna), una candidatura già in produzione (Emma), sei indizi non ammissibili.** Consegna nella [PR #43](https://github.com/nightlydeveloper8/eu-hr-internships/pull/43),
ramo `review/eu27-it-es-pt-at-20261116`, base main `2e68639182be2bda95cc2c9bf87b1d065c6ffc57`.
Rapporto [BATCH-02-REVIEW.md](eu27-expansion/BATCH-02-REVIEW.md), evidenze e costi
[batch-02-review-2026-11-16.json](eu27-expansion/batch-02-review-2026-11-16.json).

BSH: collegamento ufficiale datore→portale, 15 posizioni effettive coincidenti
con il conteggio pubblicato, due candidature spontanee escluse. Uno stage HR
Formación a Zaragoza, ID 46112; modulo dello stesso ID/titolo visibile abilitato.
**Pilota singola fonte riuscito: 5 richieste, 60,682 secondi, 109.503 byte,
zero rendering/errori**, budget 10/75 rispettato; crawl-delay 10 s e redirect
rispettati. Beneficio potenziale +1; **zero nuovi annunci pubblicati**.
Annuncio spagnolo, inglese B2 documentato; solo inglese non stabilito e frase B2
non ancora riconosciuta dall'estrattore automatico delle lingue, senza tag forzati.

Correzioni riutilizzabili: prefisso spagnolo Prácticas nel filtro; scope esatto e
conteggio degli elenchi, titoli completi opt-in prima di aprire le schede;
`publication-linked` verifica CTA osservata, identità e modulo dello stesso ID.
**395 test Python, 26 Node, 64 esempi e build superati**, 11 nuove regressioni,
due cicli offline con ID conservati. Fixture non sono nuove prove live.
Dopo il pilota corretta l'etichetta di report sui titoli: comportamento di rete
invariato. Bundle [batch-02-integration-bundle.json](eu27-expansion/batch-02-integration-bundle.json)
fuori runtime, fonte disabilitata: nessun registry/catalogo/workflow modificato,
nessun merge, gate o host di produzione esteso. Inserire azienda e fonte attiva
insieme solo dopo autorizzazione specifica, evitando fallback generici.

Altri esiti: Ginori/Kering e ENGIE bloccati da robots sul percorso di candidatura;
Gucci rimanda al listone (non dichiarato chiuso); Société Générale reindirizza
via JavaScript al login Taleo (nessuna autenticazione); Revolution Event ha XML
con 8 posizioni e una HR ma submit disabilitato/cf-turnstile e paese office non
risolto dal connettore; Unit4 429 su robots, nessun retry; Emma già verificata,
nessun doppione o nuova richiesta. **Costo totale lotto e pilota: 39 richieste
logiche, 115,265 secondi-fonte cumulati, zero rendering**, più tre query web.
Produzione resta baseline 352 record / 25 stage verificati del ciclo precedente.

**Primo punto incompleto:** review della PR, eventuale attivazione specificamente
autorizzata e primo ciclo ordinario BSH; nessuna raccolta completa manuale o
nuova automazione. Proseguire la ricerca di canali accessibili nei paesi non
coperti senza concentrare la sessione sui blocchi tecnici di questo lotto.

## 16 novembre 2026 — cinque fonti attive, primo ciclo e sito verificati

**Risultato reale: 20 → 25 stage HR aperti e verificati (+5 distinti, +25%).**
PR [#42](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42) integrata
con squash su autorizzazione specifica dell'utente: head `bb2dfbd`, merge
`87e3c56fa0daac6e5badccabde713e2210a3f1a2`. CI e preview verdi, nessuna review
bloccante. 384 test Python, 26 Node e build superati.

Aggiunti insieme cinque datori e cinque sorgenti Recruitee abilitate:
Monsterscore e SKYTREE (NL), Ibexa (BE), Gérard Bertrand e SAS LOOK UP SPACE (FR).
Quest'ultimo è diritto sociale a supporto HR: sottotipo esplicito.
Registro 1.887 → 1.892 datori, 1.931 → 1.936 sorgenti; provision idempotente.
Ogni sorgente usa soltanto il tenant esatto revisionato, `recruitee-linked`,
12 richieste/45 s. Nessun altro host, gate Dynamic ATS o schedule esteso.
Rollback: revert congiunto delle cinque aggiunte aziende/fonti; disabilitare le
sole fonti lasciando i datori genererebbe fallback generici via provisioner.

Il merge ha avviato il workflow esistente, evento push, senza workflow_dispatch:
[run 43857890201](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43857890201),
**18 job riusciti**, pubblicazione automatica `00b211644fb3fb8194b4b65b555b7ee22d243b97`.
Catalogo 16 novembre 11:41:24 UTC: **347 → 352 ID**, tutti i 347 precedenti
preservati, cinque nuove candidature con prova live policy v2. I due cambiamenti
su record precedenti sono unverified → closed, senza riduzione dei 20 verified.
Conteggio della logica frontend confermato: 25 verifiedInternships.

Costo incrementale delle cinque fonti nel ciclo: **25 richieste (5 ciascuna),
16,1 secondi-fonte cumulati, 5.052.141 byte**, nessun errore; budget rispettati.
Non è la durata a muro dell'intero workflow né un costo monetario misurato.
Inventari completi; `closure_complete=false` resta esplicito: questo primo ciclo
non dimostra ancora il refresh successivo o il comportamento di chiusura live.
Rapporto: `docs/eu27-expansion/first-production-cycle-2026-11-16.json`;
autorizzazione/configurazione: `activation-2026-11-16.json`.

**Produzione verificata:** Cloudflare Pages success sul commit dati `00b2116`,
deployment `04844850-2805-45e9-977c-beb80a2b6a63`. GET del catalogo pubblico
HTTP 200, timestamp e 352 record corrispondenti, confronto byte per byte identico
al file su Git. Nessuna modifica manuale del catalogo o importazione di replay.
La raccolta quotidiana preesistente rimane schedulata alle 06:17 UTC.
Nessuna nuova automazione AI configurata.

**Limiti e primo punto incompleto:** il successo di questi cinque canali non
rende completa la copertura UE27. Il report generale conserva 321 datori
blocked-or-failed, 514 partial e 964 discovery-incomplete; non sono inventari vuoti.
Restano 24 proposte del primo lotto non ammissibili. Per espandere i paesi,
preparati otto indizi ufficiali in IT/ES/PT/AT in
`next-country-leads-2026-11-16.json`: ancora da rivedere, nessuna fonte attivata.
Deduplicare Kering/Ginori/Gucci come gruppo; Emma è già monitorata; ENGIE ES
richiede review di host diverso dall'attuale fonte italiana. Prossimo intervento:
verificare in un lotto datore→ATS, accesso, inventario e candidature dei nuovi
canali IT/ES/PT/AT. Ulteriore rollout richiede autorizzazione specifica.
Il secondo ciclo live delle cinque fonti compete alla pianificazione ordinaria;
nessuna promessa di controllo AI automatico successivo.

## 16 novembre 2026 — verifica delle 29 proposte, cinque integrazioni ammissibili

Richiesta esplicita: verificare datore→ATS, feed, inventario e candidature delle
29 proposte, preparando l'integrazione senza merge o attivazioni. La PR #42 è
ancora aperta allo head `7d5940b`; questo lavoro ne completa il contenuto.

- **29 feed tentati, 21 inventari letti, 366 posizioni e 20 ruoli HR per studenti
  classificati.** Quattro fonti hanno risposto 429, senza retry. Tre XML Personio
  404; Hotel Beveren pubblica URL su un host diverso non approvato e rimane
  escluso. Le otto letture non stabilite non sono inventari vuoti.
- **Cinque stage distinti con prova live completa del pilota:** Monsterscore
  (HRM, Amsterdam NL), SKYTREE (HR & People Operations, Amsterdam NL), Ibexa
  (Human Resources, Louvain-la-Neuve BE), Gérard Bertrand (SIRH, Narbonne FR),
  SAS LOOK UP SPACE (diritto sociale a supporto HR, Toulouse FR).
  Per ognuno: collegamento ufficiale del datore al tenant esatto, feed letto,
  ID/titolo/datore corrispondenti e candidatura con campi visibili abilitati.
  Non equivalgono a cinque annunci già pubblicati sul sito.
- Correzione riutilizzabile **opt-in** `application_check=recruitee-linked`:
  conserva l'entry di candidatura realmente pubblicata nel feed, senza inventare
  `/c/new`; verifica ID/titolo/datore sulle due pagine, percorso, host, redirect,
  chiusure/scadenze e modulo visibile. Evita di prendere per prova il form nella
  scheda nascosta della vacancy. Connettori Recruitee già registrati invariati.
- Bundle fuori dal runtime: `docs/eu27-expansion/reviewed-integration-bundle.json`,
  cinque aziende/fonti disabilitate, metadati e prove. **Non aggiungere da sole
  aziende con fonti disabilitate:** `daily.provision` attiverebbe crawler generici.
  L'eventuale attivazione richiede integrazione congiunta nel medesimo commit e
  autorizzazione specifica. Nessun registry, catalogo o workflow modificato.
- Verifica offline su risposte salvate con il codice finale: due cicli
  **347 → 352 ID e 20 → 25 open/verified**, tutti gli ID precedenti conservati,
  idempotenza confermata. È una simulazione, non un conteggio di produzione e
  non rinnova le evidenze live. Il futuro collector dovrà rileggere tutto live;
  nessuno snapshot di questo pilota viene importato nel catalogo.
- Costo totale delle fasi: **165 richieste logiche**, 83,071 secondi-fonte,
  24,570 secondi a muro cumulati dei processi, zero rendering; massimo osservato
  10 richieste per datore su budget 12/45 secondi. Ulteriori 16 query web e
  7 aperture/find per la ricerca di pagine ufficiali; costi monetari non misurati.
- Restano **24 proposte non ammissibili**, con motivi nel report `REVIEW.md`:
  accesso/feed, identità societaria/pubblicatore, applicazione o classificazione.
  Altares e Toreon non mostrano nel feed lo stage HR indicizzato; non è una prova
  generale di chiusura. threon HRIS richiede review del filtro. Dimensioni/gruppi
  non qualificati come PMI; lingue e intake sconosciuti rimangono tali.

Consegna nella [PR #42](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42),
con estensione opt-in e bundle disabilitato. **384 test Python 3.12, 26 Node,
64 esempi di classificazione e build superati**; dieci nuove regressioni sul
percorso Recruitee e due cicli con ID preservati. CI sul nuovo head da verificare.

**Primo punto incompleto:** review della modifica e del bundle dei cinque datori,
poi integrazione/attivazione solo con autorizzazione specifica. Dopo attivazione,
misurare il primo ciclo ordinario reale (cinque prove pilota non garantiscono
cinque nuove vacancy ancora aperte in quel ciclo). Avanzare in modo indipendente
su fonti dei paesi successivi, senza ritentare qui i quattro 429 né avviare una
raccolta completa manuale. Nessuna nuova automazione o schedulazione configurata.

## 16 novembre 2026 — coda UE27 e primo lotto di espansione preparati

Ripresa del lavoro locale interrotto sul ramo `plan/eu27-expansion-20261115`,
checkout isolato `fix-jde-20261115`. Base aggiornata al main `e99f263` senza
sovrascrivere il lavoro delle altre sessioni. Il catalogo delle 09:06 UTC ha
347 record e 20 open/verified; nessun aumento attribuito a questa preparazione.
La PR #40 è merged; #18/#23 restano aperte e non limitano la ricerca UE27
richiesta esplicitamente dall'utente. NL resta prioritario senza attendere la
mappatura completa delle 12 province per ricercare nel resto dell'UE.

- Generatore offline riproducibile e coda per **27 paesi**, 1.926 identità di
  ricerca, 2.202 attività su canali. Riutilizza registro, esiti recenti, catalogo
  e scansioni esistenti. Le 39 nuove identità web sono da rivedere per gruppo e
  dimensioni: non sono aziende giuridicamente uniche accertate o fonti attive.
- **Primo lotto: 37 attività**, NL 11, BE 10, DE 11, FR 3, IE 2: 34 nuovi canali
  candidati e 3 conversioni di crawler generici (2-CNNCT, Gemeente Achtkarspelen,
  VTG GmbH Ingenieurbüro). Non è stato raggiunto l'obiettivo iniziale di 50:
  connettori dedicati già attivi, vecchi recuperi, identità condivise e prove
  contraddittorie sono esclusi, senza riempire il lotto con lavoro duplicato.
- **29 bozze per adattatori già disponibili**, tutte disabilitate nel solo
  documento `batch-01.json`; nessun file di produzione le carica. Restano da
  dimostrare collegamento datore/tenant, identità del gruppo, accesso del feed,
  completezza dell'inventario, sede e candidatura policy v2. Dimensioni non
  qualificate per tutte le 37 attività: quota PMI della strategia non dimostrata.
- Preflight live limitato a una pagina già osservata per canale supportato:
  **33 datori, 34 tentativi** (Zero Motorcycles ha poi una nuova URL vacancy
  osservata, distinta dalla precedente URL solo candidatura), **64 richieste
  logiche, 7.137.457 byte, 34,168 secondi-fonte, 16,583 secondi a muro cumulati**
  dei due processi, zero rendering. Robots e redirect sul solo host esatto
  rispettati; nessuna candidatura, API inventory o raccolta completa.
- **28 pagine con titolo corrispondente**, non 28 candidature verificate.
  DocMedico 404; JD Sports FR restituisce board Netherlands; Theodo timeout;
  Hospitality Recruiters redirect fuori scope, non seguito. Fidelity già
  contraddetta da apertura 404 resta fuori dal lotto. eXtra Shop richiede
  revisione del titolo e distinzione alternance/stage. Nessun aggiramento.
- Ricerca web complessiva delle due sessioni: 40 query e 6 aperture; costi
  monetari non misurati. **Nuove fonti attivate 0, nuove candidature verificate 0**.
  Report: `docs/eu27-expansion/README.md`, `queue.json`, `batch-01.json`, manifest
  degli indizi e due preflight con URL, date, hash e costi.

Validazione: **374 test Python 3.12 e 26 test Node superati**, 64 esempi di
classificazione senza errori, build riuscita; rigenerazione deterministica,
nessuna modifica a catalogo, registry, workflow o codice di produzione.
La coda completa è conservata anche compressa, oltre alla versione leggibile locale.

[PR #42 aperta](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42),
commit codice `f5864f87f951071d1cac285f4a89250148776ed5`. CI/preview avviate
automaticamente, esito ancora da verificare. Nessun merge o attivazione.

**Primo punto incompleto:** review e pilota circoscritto delle 29 proposte di
adattatore (priorità alle 28 con titolo live corrispondente), partendo dal legame
ufficiale datore→tenant e dal feed completo. Preparare l'integrazione soltanto
per canali con prove sufficienti, in un lotto; nessun merge/rollout implicito.
Per gli altri 22 paesi esiste la coda nazionale, non una nuova mappatura live.
Nessuna automazione di ricerca AI o nuova schedulazione configurata.

## Ripresa — verifica integrazione JDE

Verificata via API GitHub la PR #40: squash merge completato il 15 novembre 2026,
21:14:18 UTC, commit `216ea7300e5d666d6e78a0a1d2ba732d5109d502`.
La correzione di identità è quindi su main; i dettagli sotto descrivono la diagnosi
precedente al merge. Beneficio dimostrato dalla diagnosi: **0 nuove candidature**;
il target JDE restituiva JSON senza modulo. Nessuna PR duplicata, nuovo merge o
rollout in questa ripresa. Verifica della candidatura JDE e beneficio della raccolta
dopo merge ancora non attestati. Il runtime locale è disconnesso; stato aggiornato
tramite GitHub preservando il contenuto delle altre sessioni.

## 15 novembre 2026 — identità JDE e confronto Center Parcs/Landal

Ripresa dal primo punto incompleto sul main remoto `b51a602`. Checkout isolato
`fix-jde-20261115`, ramo `fix/jde-application-evidence-20261115`; preservato il
checkout principale e il lavoro delle altre sessioni.

- **Modifica proposta, non integrata:** riconoscimento conservativo dello stesso
  posting SmartRecruiters fra `job-posting-detail?id=` e prefisso numerico della
  CTA osservata. Nessun ID inferito dalla sola CTA; query ripetute, ID discordanti,
  host simili e ID nel tracking non bastano. Controlli titolo, host, redirect,
  chiusura e modulo restano obbligatori. Nessuna configurazione host/gate cambiata.
- **JDE: 0 nuove candidature verificate**, un solo record con tre URL osservate.
  Lettura live ufficiale e target ATS con robots: il target restituisce JSON della
  vacancy, non un modulo. Replay reale prima/dopo: errore d'identità risolto,
  successivo errore `Application page does not identify the same vacancy` mantenuto.
  Nessun aggiornamento del catalogo o timestamp di verifica da replay.
- Confronto live circoscritto: Center Parcs ha titolo/JobPosting della stessa
  vacancy e pulsante JavaScript `Solliciteren`, ma nessun href/modulo statico;
  Landal pubblica `JR104108`, mentre la CTA Workday osservata contiene `JR104108-1`.
  Nessuna promozione o presunzione di equivalenza della variante.
- Costi complessivi della diagnosi: **9 richieste / 17,505 secondi-fonte /
  0 rendering**, inclusi robots; JDE 5/4,685 s, Center Parcs 2/11,487 s,
  Landal 2/1,333 s. La correzione aggiunge una lettura del target nel replay;
  non dimostra un risparmio né nuove opportunità in produzione.
- Report riproducibile: `docs/jde-application-identity-2026-11-15.json`, due
  risposte reali compresse con SHA-256 e sei test nuovi, incluso replay in due cicli
  senza mutazione del record. Corretto anche il test WEBO che assumeva uno stage
  ancora assente dal catalogo: verifica ora inserimento e refresh/idempotenza.

Validazione locale: **362 test Python 3.12 e 26 Node superati**, 64 esempi di
classificazione senza errori, coverage e build riusciti. I file di copertura
rigenerati solo nel timestamp sono stati esclusi dal diff.

[PR #40 aperta](https://github.com/nightlydeveloper8/eu-hr-internships/pull/40),
commit codice `1f223d046368e3edc3f50087e7b448e36658f261`. CI GitHub e preview
avviate automaticamente, esito ancora da verificare. Nessun merge o attivazione.

**Primo punto incompleto:** diagnosi riutilizzabile del flusso DigitalRecruiters
Center Parcs attivato dal pulsante osservato, con letture non-submit e scope/budget
esistenti. Per JDE serve una prova ufficiale di candidatura oltre al JSON; per
Landal restano identità della variante Workday e modulo. Non ampliare rollout,
non avviare raccolte complete. Catalogo/produzione invariati; confronto pubblico
Cloudflare e Issue #18/#23 restano aperti. Nessun controllo AI futuro configurato.

## 15 novembre 2026 — esito della prima raccolta dopo #39

Ripreso il primo punto incompleto senza avviare raccolte manuali.
[Raccolta #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
conclusa con successo alle 20:20 ora svizzera: test, 16 shard e publish riusciti.
Commit dati `1ad28a9cae8076d9181974fa4ea07940e263a93d`.

- Catalogo: **345 → 346 ID; 19 → 20 open/verified; 303 unverified e 23 closed invariati**.
  Tutti i vecchi ID conservati e nessun cambio di status sui record precedenti.
  Le 20 verifiche aperte hanno checked_at del 15 novembre, fra 19:07:47 e 19:08:08 UTC.
- **WEBO — Stage HRM, Rijssen**: nuovo ID `538388e73bc1c0592ab5`,
  candidatura ufficiale via email documentata dal collector live, policy v2,
  `official-vacancy-email-instructions`; inizio febbraio 2027, lingua di lavoro
  sconosciuta. Nessuna email o candidatura inviata. È una nuova opportunità verificata,
  già presente come vecchia scheda aggregatore unverified: non due opportunità distinte.
  Fonte parziale: 11 richieste, 23,17 s, zero rendering. Gli errori su open application
  e working student non invalidano la prova della vacancy HR né rendono completo l'inventario.
- Cinque fonti nuove, costo complessivo **50 richieste / 71,73 secondi-fonte**:
  WEBO 11/23,17 s → 1 HR verificato; Attero 30/35,85 s → 0 HR osservati,
  lettura parziale (una scheda senza JobPosting); Intergas 2/1,21 s → inventario
  14 offerte, 0 HR; SW 2/1,63 s → inventario 39 offerte, 0 HR;
  Reestmond 5/9,87 s → discovery incompleta, non prova di zero offerte.
  Questi tempi non sono tempo a muro né costo monetario.
- Drenthe: 40/40 tentati, 27 con dimensione qualificata, 2 stage verificati totali
  (1 presso datori qualificati). Stati: 21 partial, 10 discovery-incomplete,
  5 blocked-or-failed, 4 collected. Provincia ancora incompleta.
- Totale monitoraggio: 1.887 datori tentati; 57 collected, 31 verified-empty,
  513 partial, 977 discovery-incomplete, 309 blocked-or-failed.
- Cloudflare check-run `132927454054`: **success sul commit dati esatto 1ad28a9**,
  deployment `a2442ea2-8a3b-4496-a134-1497fe0fdad6`.
  Il success del deployment è attestato; confronto del catalogo servito ancora
  incompleto: precedente accesso HTTP 403 e tentativo browser corrente in timeout.
- Dynamic ATS: Bentacera, OPACK e Achmea restano unverified. Nessuna nuova prova
  di beneficio di produzione per #23; #18/#23 rimangono aperte. Gate e rollout invariati.
- Nessuna PR aperta all'avvio della ripresa. Nessun nuovo merge, ampliamento host,
  rollout, modifica al catalogo o workflow manuale in questa attività.

**Primo punto incompleto aggiornato:** diagnosi riutilizzabile dei link ufficiali
di candidatura sui canali NL già letti, partendo da JDE: tre URL osservate nella raccolta condividono
lo stesso posting ID `744000158015131` e falliscono `Application link lacks a matching vacancy identifier`;
non sono tre opportunità distinte. Confrontare poi Center Parcs e Landal, preservando
policy v2, robots e host autorizzati. Prove live circoscritte solo quando utili;
nessuna raccolta completa manuale. Proseguire la copertura comunale NL tramite fonti
ufficiali accessibili; CBS, Groothuis e Wikidata restano esclusi finché bloccati.
Il confronto del sito servito resta una verifica indipendente da completare.
Nessun controllo AI futuro configurato.

## 15 novembre 2026 — integrazione autorizzata delle PR pronte

L'utente ha autorizzato esplicitamente squash and merge di tutto il lavoro pronto.
Non chiedere di nuovo l'autorizzazione per completare questa integrazione.

- **PR #38 già merged**, squash `adf4c69dd1d47cc7f940a98421796940c818d7f3`.
  Verificati head esatto, CI/preview verdi e assenza di review bloccanti prima del merge.
- **PR #39 merged con squash**, `3a2830f558af8c3e58b1ec7673dbfd7df294fbef`.
  Include le modifiche pronte #20, #27, #28, #32, #33, #34, #35, #36, #37 e WEBO;
  il checkpoint #26 è superato dallo stato corrente. Le dieci vecchie PR sono
  chiuse come consolidate/superate, non come singoli merge; rami e prove preservati.
  Nessuna PR aperta resta al controllo finale. Checkout `merge-ready-20261115`.
- Due conflitti di codice risolti conservando sia i limiti host/checkpoint #38 sia
  titoli storici, telemetria e publisher ufficiali scoped delle #27/#28. Allarme
  testato anche avviando i test fuori dalla root, senza modificare gli script live.
- **356 test Python (3.12), 26 Node, 64 esempi, coverage e build riusciti.**
  La #28 aveva vecchie CI cancellate: non è stata assunta pronta sulla sola preview;
  il suo codice è incluso nella verifica combinata completa.
- Registro integrato: 1.887 datori e 1.931 fonti, cinque datori/fonti nuovi
  (Attero, Intergas, Reestmond, SW Vastgoedverbetering e WEBO). Le altre modifiche
  estendono o correggono identità/sedi e canali di datori già censiti.
- Tutti i 345 ID del catalogo corrente conservati, senza variazioni di status,
  identità o verifiche. Unica associazione aggiornata: Landal Nooitgedacht → NL13,
  derivata dalla sede ufficiale Drenthe già revisionata. Nessun snapshot storico
  di catalogo o coverage generale sovrascrive quello attuale.
- WEBO Stage HRM: 1 nuova candidatura verificabile nel pilota live del 15 novembre
  (3 richieste / 34,533 s), nessun invio. Fonte quotidiana configurata su main, parziale, host
  esatto e budget 80 richieste/120 s. Prima raccolta su main ancora da verificare;
  l'incremento effettivo di stage in produzione non è ancora attestato.
- Drenthe: lotto parziale di 40 datori, 27 qualificati nella ricerca del 14 novembre;
  non provincia completa. Overijssel: WEBO primo canale proposto; CBS 406 rispettato,
  municipality code ignoto. Le 171 vecchie schede OVI non sono aziende uniche.
- Directory/ATS discovery #33/#34 restano code offline, seed live disabilitati;
  #35 audit DIM conferma mantenimento storico, non nuove vacancy; #36 documenta un
  pilota Wikidata bloccato. Nessuna query o fonte live avviata per questi moduli.
- Gate Dynamic ATS `pilot-v1`, allowlist del pilota e schedule invariati. Nessuna
  raccolta completa manuale, email, candidatura o automazione AI aggiunta.

**Stato finale dell'integrazione:** CI prima del merge #43750190939/#43750185407
riuscita sullo head esatto `061426e`; CI dopo merge #43750497438 riuscita.
[Raccolta automatica #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
avviata dal merge #39, ancora in corso all'ultimo controllo. Nessun workflow
manuale avviato e nessun controllo AI futuro configurato.

La precedente raccolta dopo #38, #43748284250, è riuscita: test, 16 shard e
publish tutti verdi, commit dati `19c4258`. Catalogo 18:55 UTC: 345 ID, 19 open,
303 unverified, 23 closed. Prima/dopo #38: 341 → 345 record ma 19 → 19 verified;
nessun nuovo verified attribuito al fix. DAF: richieste 86 → 75, durata
100,46 → 86,13 s, pending 2.332 → 57, solo host www.daf.com. Inventario ancora
parziale: il risparmio osservato non prova completezza né nuove candidature.

**Punto di ripresa precedente (completato sopra):** leggere l'esito del run #43750497445, verificare
publish, nuovi ID, freschezza e opportunità WEBO; misurare costi e canali Drenthe.
Non dichiarare un incremento di produzione prima di quel risultato. Il controllo
pubblico del catalogo Cloudflare ha restituito HTTP 403: deployment/contenuto
servito non attestati dal runtime, distinzione conservata rispetto a GitHub.
Issue #18 e #23 restano aperte finché tutti i criteri di produzione non sono provati.
Le vecchie modifiche locali WEBO sono già incluse: non creare una PR duplicata
partendo dal checkout storico. Dettagli in docs/integration-2026-11-15.md.

## 16 novembre 2026 — pilota Marquardt/SLB/TikTok e fix strutturali 429/filled (PR tecnica)

La review ufficiale delle tre schede e CTA produce **0 nuove candidature verified**: Marquardt RO ha vacancy HR Sibiu e CTA Mingle ma modulo non stabilito; SLB RO mostra configurazione Eightfold `disableLoggedOutApply: true`/`recaptchaEnabled: true`, senza applicazione anonima dimostrata; TikTok IE A187616 ha CTA verso ID corrispondente, ma il redirect finale non è leggibile dal tool e il datore era già nella coda precedente. **robots, inventari completi e moduli validi non attestati**; nessuna fonte ammissibile, nessun nuovo contatore di produzione. Baseline documentata invariata: **28 stage verificati + 1 working student**, 361 record; nessuna attivazione o raccolta completa.

Correzioni **proposte su ramo separato, non integrate**: `collector/runtime.py` applica uno stop nello stesso processo dopo primo HTTP 429 per host (no ulteriori chiamate di rete a quel host; altri host continuano). `collector/applications.py` riconosce “job ... has been filled” di Electrolux `JR81378` anche in presenza di JSON-LD obsoleto. Test offline per 429 multipli, client separati, redirect, robots, 503 non-bloccante, chiusura con JobPosting residuo. Esiti CI e merge da verificare, zero modifica registri/workflow, zero rollout.

Costo produzione aggiuntivo **0**. Il pilota web non dispone di conteggio HTTP/tempo/byte del collector: non equipararlo al preflight documentato (27 richieste, 14,721 secondi-fonte). Con ipotetico massimo 8 richieste/45 secondi per ciascuna di tre fonti, tetto condizionale 24 richieste e 135 secondi-fonte **solo dopo ammissione**, non misurazione live. Dettagli, evidenze e prossimi blocchi: [BATCH-05-PILOT-AND-429-FIX.md](eu27-expansion/BATCH-05-PILOT-AND-429-FIX.md).

**Primo punto incompleto:** controllare CI della PR tecnica; pilota client HTTPS/robots su Marquardt/SLB/TikTok e same-vacancy form anonimo, senza CAPTCHA/login. Non attivare i tre canali finché un percorso non supera policy v2; se nessuno passa, cercare fonti sostitutive.

