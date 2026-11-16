# Lotto 07 — Cipro, Grecia, Croazia e Malta

**Data:** 16 novembre 2026. **Risultato:** 8 indizi esaminati, 3 schede HR su siti ufficiali da verificare, **0 nuovi stage policy v2 verified**, **0 fonti attivate**. Le tre schede non equivalgono ancora a tre candidature verificabili. Evidenza completa nel [JSON del lotto](batch-07-review-2026-11-16.json).

**Baseline:** ultima raccolta documentata del 16 novembre 16:51:25 UTC, 362 annunci, **28 stage verified in cinque paesi + 1 working student DE**. PR #48 integrata su main nel commit bea9c85 e validazione #43915251768 riuscita. Nessun nuovo ciclo o deploy attribuibile a questo lotto.

## Priorità da verificare

| Paese | Offerta e collegamento ufficiale | Gate ancora mancante |
| --- | --- | --- |
| **Cipro** | [Brainstorm Hospitality — HR Intern](https://careers.fridays.com.cy/jobs/7649525-hr-intern) a Larnaca, ID **7649525**. [Inventario datore](https://careers.fridays.com.cy/) coerente, stage retribuito. | La CTA apre un modulo dinamico che nel lettore mostra **Loading application form**; campi visibili e invio abilitato **non dimostrati**. Robots e inventario non letti da BudgetClient. |
| **Grecia** | [iKnowHow S.A. — HR Intern (Talent Acquisition)](https://apply.workable.com/ikh/j/3F368EAC02), Neo Psychiko, ID **3F368EAC02**, inglese richiesto, iscrizione idonea a istituto greco richiesta. [Carriere aziendali](https://www.iknowhow.com/careers/) rimanda esattamente al [tenant Workable](https://apply.workable.com/ikh/); l'[informativa societaria](https://www.iknowhow.com/privacy-policy/) conferma Workable. | Prova ufficiale datore→ATS **confermata**; robots, feed completo, stessi ID/CTA e modulo candidato anonimo non attestati dal collector. |
| **Malta** | [Marriott / Westin Dragonara — Human Resources Intern](https://careers.marriott.com/human-resources-intern-the-westin-dragonara-resort/job/P1-7345932-0), St Julian's, ID **26132701**, presente anche nell'[inventario Westin](https://careers.marriott.com/brands/westin/jobs/page/52). CTA Oracle conserva l'ID nell'URL finale. Indennità lorda €835/mese, almeno 5–6 mesi. | Robots Marriott/Oracle non verificati; [CTA Oracle](https://ejwl.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/26132701/apply/email?posting_type=1) restituisce nessun modulo leggibile nel lettore web. Nessuna autenticazione tentata. |

La priorità di pilot è Brainstorm (singolo job nell'inventario corrente), poi iKnowHow (identità datore→Workable accertata), poi Marriott (correlazione ID accertata, form Oracle sconosciuto). **Non** dichiarare candidabile una posizione soltanto per la CTA o per un HTTP 200.

## Esclusioni e limiti

- **Croazia:** la [vecchia pagina Rimac People Operations Intern](https://careers.rimac-group.com/position/people-operations-intern/) è tuttora pubblica, ma non figura tra le **124 vacancy dell'[inventario Rimac attuale](https://careers.rimac-group.com/)**. Gli altri HR sono ruoli permanenti; la vecchia pagina richiede **inglese e croato**. Non dichiarare l'annuncio aperto né chiuso senza prova di chiusura esplicita, ma non ammetterlo.
- **Croazia:** l'[avviso PLIVA AskHR](https://www.sczg.unizg.hr/poslovi/studentski-posao-u-odjelu-ljudskih-potencijala) scadeva il **9 novembre 2026** ed è un lavoro studentesco, non stage.
- **Malta:** per Xara Collection le pubblicazioni Hosco/LinkedIn indicano HR Intern, ma la [lista aziendale](https://xaracollection.com/xara-collection-vacancies/) contiene **HR Executive** e non lo stage; non confondere i due ruoli. Hilton HR Trainee marzo 2027 è documentato solo da siti terzi, senza identità ATS ufficiale precisa: non ammissibile.
- **Cipro:** il [board Stoiximan](https://apply.workable.com/stoiximan/?not_found=true) menziona HR Intern in materiale promozionale, ma dichiara **zero posizioni aperte in Corporate Functions**; non contarlo come stage live.

## Preflight reale con il client del progetto — 16 novembre, 17:29 UTC

Dopo la ricerca web è stata eseguita **una singola prova GET-only** con il vero `collector.runtime.BudgetClient` su un ramo pilota separato, con `robots=True`, redirect limitati agli host pubblici già identificati, **12 richieste e 45 secondi-fonte massimo** per datore. GitHub Actions [#43918927512](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43918927512) **success**. Evidenze grezze riproducibili, inclusi SHA256 dei corpi letti, nel [JSON del preflight](batch-07-live-preflight-2026-11-16.json).

| Fonte | Richieste logiche totali, inclusi robots | Byte letti | Secondi-fonte | HTTP delle pagine | Form candidato HTML visibile |
| --- | ---: | ---: | ---: | --- | --- |
| Brainstorm CY | **3** | 100.676 | 1,965 | 200 inventario; 200 vacancy | **No** |
| iKnowHow GR | **3** | 15.300 | 1,072 | 200 board; 200 vacancy | **No** |
| Marriott MT | **5** | 1.240.277 | 2,366 | 200 board; 200 vacancy; 200 Oracle | **No** |
| **Totale** | **11** | **1.356.253** | **5,403** | Nessun HTTP 429 | **0 su 3** |

La guardia `robots.txt` del client ha **consentito le URL richieste**: non significa che tutte le sezioni degli host siano autorizzate. Il probe **non conserva contenuto/status delle singole risposte robots** e quindi non si possono attestare direttive precise. Non sono stati usati browser, renderer, autenticazione, POST, invio o CAPTCHA. **Nessuna fonte è stata attivata né nel ramo principale né nel workflow giornaliero.**

**Qualità delle prove:** Brainstorm restituisce nel corpo dell'inventario il titolo HR Intern e sulla scheda lo stesso titolo/ID; il form resta non visibile. iKnowHow restituisce HTTP 200 e il testo del ruolo sulla singola pagina, ma la pagina board viene letta come HTML shell senza titolo HR nel testo estratto; inventario completo **non dimostrato**. Marriott restituisce la scheda HR con titolo e la destinazione Oracle con ID 26132701, ma quest'ultima è una shell senza campi candidati nel DOM statico; anche il listing Westin non contiene il titolo HR nel testo estratto dal client. Non sono perciò tre verifiche policy v2 riuscite.

**Beneficio reale:** confermato l'accesso robots-guarded e la lettura limitata delle tre schede; **0 nuove candidature verificate**, **0 fonti abilitate**, **0 richieste quotidiane aggiunte**. Il costo misurato di questa attività è **11 GET logici e 1,36 MB di corpi letti** con **5,403 s-fonte**; il costo aggiuntivo del monitoraggio ordinario resta **zero** perché non c'è rollout. Le ricerche web sono state svolte separatamente e non sono metriche del BudgetClient. Nessuna prova di produzione ottenuta per questi nuovi canali.

## Prossimo punto incompleto

1. **Dopo il preflight GET già riuscito:** individuare un modo ufficiale, riutilizzabile e consentito di ottenere il modulo anonimo abilitato per Brainstorm Teamtailor e iKnowHow Workable, senza rendere più permissiva la policy v2; verificare completezza del board Workable.
2. **Marriott MT → Oracle:** host e ID del percorso verificati in GET, ma solo shell HTML: lasciare unverified finché il modulo anonimo non è osservabile senza login o rendering non autorizzato.
3. **Croazia:** sostituire Rimac non attuale con un nuovo inventario HR student ufficiale realmente aperto. Non promuovere annunci chiusi o lavori studenteschi a stage.
4. Solo dopo le prove policy v2 predisporre bundle atomico/rollout specifico e misurare due cicli. Lotto 08 AT/DE/DK/FI/PL/SE già pianificato, **non schedulato**.

Questa PR cambia **solo documentazione** e il checkpoint globale; non altera registry, collector, catalogo, workflow o policy v2. Il workflow pilota GET-only vive su un ramo separato non integrato e non è una schedulazione quotidiana. PR #41 e #46 restano draft non pronti.
