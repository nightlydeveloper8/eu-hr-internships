# Stato di ripresa — People Placement




## 16 novembre 2026 — lotto DE/DK/PL/FI verificato, nessuna nuova fonte ammissibile

**Quattro indizi → zero nuove fonti attivabili, zero nuovi stage aggiunti.**
Ramo `review/eu27-de-dk-pl-fi-20261116`, base main `876794a`.
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
