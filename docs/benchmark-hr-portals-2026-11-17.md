# People Placement — benchmark dei portali stage HR (17 novembre 2026)

## Verifica ufficiale reale: Ampelmann e valutazione PepsiCo (17 novembre, secondo intervento)

### Ampelmann — outcome *incomplete*, non `verified`

Eseguito **GitHub Actions GET-only** su branch isolato `pilot/ampelmann-readonly-20261117`, con `BudgetClient` reale, controllo robots, host ristretto al **solo** `careers.ampelmann.nl`, limite **6 richieste/48 secondi per ciclo**, senza POST, browser, login o dati di candidati. Workflow temporaneo **rimosso** dopo il test, nessun merge/rollout.

- Primo [run #44143996768](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44143996768): 2 HTTP, **305.445 B**, **2,059 s**, interrotto da **errore del nostro script** (`canonical_url()` riservata a URL di vacancy usata per homepage); non indicava un blocco del sito. Corretto nel workflow isolato.
- Secondo [run #44144200129](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44144200129): **3 HTTP, 603.229 B, 2,855 s**. La richiesta robots è stata superata, homepage ufficiale corrente **include esattamente** `/o/internship-people-organisation-1`; titolo `Internship People & Organisation` corrispondente e **ID strutturato 2822573**. Il controllo `applicant_form(body,strict=True)` non ha dimostrato il modulo abilitato nell'HTML iniziale. Nessuna visita dinamica autorizzata o seconda prova positiva: **policy v2 incomplete**, **0 stage importati**.
- **Costo complessivo dei due tentativi**: **5 GET**, **908.674 byte**, **4,914 s-fonte cumulati**; 0 rendering/POST. Non presentare il risultato come "due cicli verificati": il primo è un errore tecnico del preflight, il secondo è un unico ciclo incompleto.
- Il lettore web mostra input e pulsante `Send` nella pagina aziendale (scadenza dichiarata 24/11/2026), ma la resa del lettore **non sostituisce** HTML statico, controllo app URL same-ID né prove del collector. Non inventare `/c/new` o tenant API. La documentazione ufficiale [Recruitee Careers API](https://docs.recruitee.com/reference/authentication-1) conferma un gate di autenticazione via token per le chiamate API; l'XML feed segue regole separate. Non aggirare né usare API di terzi a pagamento.
- **Passo tecnico incompleto:** determinare un URL di applicazione effettivamente **pubblicato dall'ATS/da una sua sorgente pubblica autorizzata**, oppure un modulo statico same-ID; altrimenti lasciare `unverified`. Un'eventuale prova dinamica richiede gate distinto per sorgente, non estensione implicita di `pilot-v1` ad Ampelmann.

### PepsiCo — due ID ufficiali, ma accesso automatizzato non attestato

- [480557, People & Culture Intern, Zaandam](https://www.pepsicojobs.com/main/jobs/480557?lang=en-us); [479166, Soda Stream HR Intern, Tilburg](https://www.pepsicojobs.com/main/jobs/479166?lang=en-us). Due **ID di posizione** e luoghi distinti, non due copie dello stesso annuncio.
- Il motore web indicizza le due pagine aziendali, ma la lettura **`robots.txt` via web reader e l'apertura diretta delle pagine hanno dato HTTP 403**. Questa risposta non dimostra che gli annunci siano chiusi; impedisce di certificare le regole di accesso tramite questo ambiente. **0 GET BudgetClient PepsiCo, 0 form same-ID, 0 nuovi stage verified**; nessun tentativo di aggirare blocchi/alterare User-Agent o ricostruire API non autorizzate.
- Individuata una terza pista aziendale [481204 — First Gen: HR Intern Benelux, Utrecht](https://www.pepsicojobs.com/main/jobs/481204?lang=en-US), **solo discovery**. Non inclusa nei 9 gap già quantificati e non aggiunta alla raccolta.
- Prima di proporre un adapter PepsiCo è necessario un **preflight robots accessibile** da percorso ordinario autorizzato, seguito da inventario completo e same-ID application. Se l'accesso resta 403, stop.

### Risorse gratuite e costi operativi

[GitHub Actions Billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions) indica che i **runner standard** sono gratuiti per repository pubblici; la repo è documentata pubblica e il workflow di prova usa `ubuntu-latest`. [Cloudflare Pages Free](https://developers.cloudflare.com/pages/platform/limits/) prevede **500 build mensili**. **Nessuna fatturazione/account balance è stato letto**: si tratta di compatibilità con condizioni gratuite, non certificazione di fattura personale pari a 0 €. La vera criticità qui è la resa del monitoraggio, non una spesa dimostrata.

### Francia, Belgio, Germania: baseline concreta, non previsione

Su `data/catalog.json` main `ab51981`, selezionando solo `internship_type=internship` e paese principale:

| Paese | Record stage HR | Open/verified | Unverified | Closed | Pattern già noti |
|---|---:|---:|---:|---:|---|
| **Francia** | 46 | 5 | 37 | 4 | 11 unverified SmartRecruiters; 2 Ashby |
| **Belgio** | 4 | 3 | 1 | 0 | 1 SmartRecruiters da verificare |
| **Germania** | 28 | 0 | 26 | 2 | 2 Personio senza form abilitato dimostrato |

**64 record unverified** in FR/BE/DE sono un *backlog*, non 64 stage aperti né 64 nuovi stage potenziali necessariamente recuperabili. Alcuni sono su host vietati, scaduti o con identity mismatch. Priorità: **pattern SmartRecruiters FR/BE** con ownership/same-ID e regole accesso consentite; in DE indagare il gate Personio (non promuovere pulsanti disabled) e identificare feed ufficiali aggiuntivi. Non esiste base attendibile per dire che i connettori NL produrrebbero +X stage su questi paesi.

### Frequenza e risparmio possibile

Nel ciclo ordinario precedente le **1.832 fonti senza match HR** hanno consumato **34.192 richieste (94,52%)**, **3.765.755.480 byte (90,54%)** e **3.187 rendering (96,99%)**. Non modificata la cadenza: un solo giorno non prova assenza persistente. Proposta di misura **14 giorni**, e solo dopo una **simulazione offline** della politica: fonte con HR recente o verifica critica → giornaliera; fonti sistematicamente senza match → intervallo conservativo da sperimentare con canary, monitorando vacancy perse, latenza e costo. Non promettere **zero** perdite se si eseguono meno controlli; un nuovo stage può aprirsi e chiudersi tra due visite.

**Esito netto di questo intervento:** 1 fonte ufficiale Ampelmann con inventory+identity confermati ma form statico non dimostrato, 2 PepsiCo con pagine indicizzate ma accesso corrente non accertabile, **0 nuovi HR verified**. Nessun catalogo, registry, crawler ordinario, workflow di produzione o modello di costi modificati.

## Decisione e limite
**Aggiornamento della seconda tranche:** **12 lead** HR/affini da **due** portali, **9 vacancy ID assenti** nel catalogo baseline (di cui uno misto HR/amministrazione da classificare), **2 corrispondenze unverified/ambigue** e **1 vacancy Unilever già open/verified**. **11** pagine ufficiali lette nel web, **1** URL ufficiale storico JDE non riletto. Nessuna di queste 12 attività ha creato nuove vacancy verificate. La prima tranche di 7 lead resta documentata sotto, con i suoi conteggi autonomi.

**Risultato primo lotto:** in un campione mirato di **7 annunci HR NL da Magnet.me**, **5 datori/annunci non risultano nel catalogo main** cercando datore e titolo, **2 hanno corrispondenze già non verificate** (Philips, JDE Peet's). **Sei** dispongono di una pagina ufficiale specifica leggibile nella ricognizione web odierna; per **JDE** il collegamento ufficiale proviene dal catalogo preesistente ma non è stato nuovamente letto. **Una** (Ampelmann) mostra nel contenuto HTML pubblico i campi del form di candidatura. **Zero nuove candidature policy v2**: non sono stati eseguiti preflight BudgetClient/robots/host, staging, due cicli o publish per questo benchmark.

**Riferimento verificato:** `data/catalog.json` main, `updated_at=2026-11-17T08:07:40.055449+00:00`, blob `40f655ca915de1f921ec688b4e7f98ade46cbbc0`: **363 ID**, **28 stage HR open/verified**, **1 working student open/verified**, **307 unverified**, **27 closed**. Gli stage verificati sono in **NL 18, BE 3, FR 5, ES 1, PT 1**. Nessuna delle dodici piste modifica questo numero.

Il file strutturato [benchmark-hr-portals-2026-11-17.json](benchmark-hr-portals-2026-11-17.json) conserva identificativi e link. Campione intenzionale, due portali (Magnet.me e JobTeaser) e solo NL: **non** stimare quota di mercato UE27, duplicazioni globali, freschezza o tasso di conversione reale dei concorrenti da questi 12 casi.

## Portali osservati e limiti del confronto

| Portale | Segnale utile | Limite prima di usare il portale come fonte |
|---|---|---|
| [Magnet.me — HR NL](https://magnet.me/en/internships/netherlands/human-resources) | Pagine specifiche, datore e luogo; 7 piste tracciate in questo lotto | Annuncio su aggregatore ≠ candidatura ancora aperta; non automatizzare il prelievo senza controllo di termini e robots |
| [iAgora — HR Europa](https://www.iagora.com/work/en/internships/hr/europe) | Ricerca HR per area europea e filtri linguistici | Conteggi riportati dal sito non sono opportunità uniche/candidabili, alcuni datori non nominati |
| [Stageplaza — HR/HRM](https://stageplaza.nl/stage/hr-hrm/) | Catalogo specializzato negli stage olandesi | Le quantità in pagina non misurano la disponibilità su sito aziendale |
| [JobTeaser](https://www.jobteaser.com/en/) | Annunci HR europei con requisiti accademici, spesso dati azienda | Accesso e modalità candidatura variano; confrontare sempre la pagina ufficiale |
| [Welcome to the Jungle](https://www.welcometothejungle.com/en/jobs) | Pagine di internship/People Operations di aziende europee | Possibile pagina editoriale o ATS terzo, nessun automatico `verified` |

Non effettuati scraping, esportazioni o importazione del contenuto dei concorrenti nel catalogo. Il benchmark consiste in letture web limitate di annunci individuati e pagine **ufficiali**. Prima di costruire discovery automatica da aggregatori verificare condizioni d'uso, robots.txt, provenienza e licenze; preferire inventari dei datori e feed pubblici esplicitamente autorizzati.

## Campione verificato sulle pagine aziendali, ma non secondo policy v2

| Priorità | Datore / vacancy / ID | Riscontro ufficiale | Stato nel catalogo / motivo residuo |
|---|---|---|---|
| **1** | [Ampelmann — Internship People & Organisation](https://careers.ampelmann.nl/o/internship-people-organisation-1), Delft | Scheda HR, sede, scadenza 24/11/2026, form visibile (nome, email, CV, domande); **inglese richiesto, olandese plus** | **Non trovata**; migliore candidata a un preflight ufficiale controllato e a un adapter riutilizzabile, senza promozione anticipata |
| **2** | [Henkel — HRBP Intern](https://www.henkel.com/careers/find-your-job-apply/2273404-2273404), Amsterdam/Utrecht, job ID 26101817 | Pagina ufficiale e link al sistema Henkel Cornerstone; **inglese richiesto, olandese preferito** | **Non trovata**; manca attestazione modulo sullo stesso ID, non usare email di contatto per candidarsi |
| **3** | [Stryker — Human Resources Intern](https://careers.stryker.com/human-resources-intern/job/CA0F9085968EB37DDF81736932C396BF), Amsterdam, R576472 | Annuncio aziendale con link `Apply Now` a [Workday stesso ID](https://stryker.wd1.myworkdayjobs.com/StrykerCareers/job/Amsterdam-Netherlands/Human-Resources-Intern_R576472-1) | **Non trovata**; Workday aperto dal lettore ma non mostra modulo leggibile, niente `verified` |
| **4** | [ASML — Early career Events / Talent Engagement](https://www.asml.com/en/careers/find-your-job/hr--business-administration-internship-early-career-events-programs-and-talent-engagement-j00355639), Veldhoven, J-00355639 | Annuncio ufficiale, internship non-thesis da febbraio 2027, **inglese eccellente** | **Non trovata**; candidatura non attestata con prova specifica |
| **5** | [Hunkemöller — HR Global Projects & Recruitment](https://jobs.hunkemoller.com/en/vacancies/internship-hr-global-projects-and-recruitment-hilversum-jr78931), Hilversum, JR78931 | Scheda aziendale con CTA `Apply`; **olandese fluente obbligatorio** | **Non trovata**; modulo non attestato, priorità minore per studenti solo anglofoni |
| **6** | [Philips — Internship HR](https://www.careers.philips.com/global/en/job/594564/Intern-Manufacturing-People-Partnering), Drachten, 594564 | Vacancy ufficiale, inizio febbraio 2027, **olandese + inglese** | **Già nel catalogo, ID `903efc58fb2fabb24b59`**; `unverified`: nessuna application entry specifica stabilita |
| **7** | [JDE Peet's — Internship Talent Acquisition](https://careers-nl.jdepeets.com/job-posting-detail?id=744000158015131&return_url=%2Fjob-search%2F), NL | URL aziendale già registrata, **non accessibile al lettore web in questa sessione**; il concorrente mostra un titolo affine | **Possibile sovrapposizione**, ID `8b5138f67090ed0cd3b4` unverified (form non stabilito); esiste anche mirror storico `ba254a8016887ae59fee` quarantinato per ownership. **Non** contare due offerte né dichiarare la stessa ID senza nuova verifica |

Fonte di scoperta per i 7 lead: [Magnet.me](https://magnet.me/en/internships/netherlands/human-resources); URL individuali nella coda JSON. Osservazione puntuale il **17/11/2026**; le risposte del lettore web **non** sostituiscono controlli GET/robots, inventario completo, same-vacancy, identità del datore, host autorizzati, durata e candidatura aperta in collector.


## Secondo lotto: ulteriori cinque opportunità ufficiali e riconciliazione degli ID

| Origine | Vacanza / ID ufficiale | Stato in baseline main | Limite |
|---|---|---|---|
| [Magnet.me](https://magnet.me/en/opportunity/1109983/intern---hr---business-administration-support) | [ING — HR & Business Administration Support](https://careers.ing.com/en/job/amsterdam/intern-hr-and-business-administration-support/3121/46858366848), **REQ-10124598**, Amsterdam | **ID assente** | Supporto misto HR, eventi e operations: **pertinenza accademica da confermare**; CTA non è form verified |
| [Magnet.me](https://magnet.me/en/opportunity/1109849/people---culture--hr--intern) | [IKEA — People & Culture (HR) Intern](https://jobs.ikea.com/nl/banen/delft/people-and-culture-hr-intern/24107/103162004976), **103162004976**, Delft | **ID assente**: IKEA è presente con due vacancy **diverse** a Groningen (ID 102900957200 e 102759645920), non duplicare per datore | Anche l'annuncio specifico Delft necessita inventario/form policy v2 |
| [Magnet.me](https://magnet.me/en/opportunity/1108832/first-gen--people---culture-intern) | [PepsiCo — First Gen: People & Culture Intern](https://www.pepsicojobs.com/main/jobs/480557?lang=en-us), **480557**, Zaandam | **ID assente** | Form di candidatura non verificato |
| [JobTeaser](https://www.jobteaser.com/nl/job-offers/ba610404-1da7-47d2-99be-f7cf32b1a7c4-pepsico-soda-stream-hr-intern) | [PepsiCo/SodaStream — HR Intern](https://www.pepsicojobs.com/main/jobs/479166?lang=en-US), **479166**, Tilburg | **ID assente**, e **distinto** da PepsiCo Zaandam | Form di candidatura non verificato |
| [Magnet.me](https://magnet.me/en/opportunity/1104787/internship--27--human-resources) | [Unilever — Internship '27: Human Resources](https://careers.unilever.com/en/job/rotterdam/internship-27-human-resources/34155/101567836896), **R-1189147**, Rotterdam | **Già open/verified**, ID `12e4d5cc93dc6e0323bb`; **0 nuove** | Riscontro positivo di deduplica: non conteggiare nuovamente |

**Risultato complessivo non rappresentativo:** **12 lead**, **9 ID assenti**, **2 già unverified/possibile overlap**, **1 già verified**, **11 pagine ufficiali leggibili**, **1 link catalogo non riletto**, **0 nuove candidature policy v2**. Due ruoli PepsiCo rappresentano due vacancy, non due aziende. Nessun annuncio è stato inserito nella raccolta ordinaria. Per misurare una vera conversione `new_verified / leads` occorre completare i gate per tutti i lead eleggibili: **0 stage verificati in questa analisi non significa 0% di candidabilità dei concorrenti**.

## Risposte operative alle tre domande

### 1. Quanti nuovi stage possiamo scoprire?

Il campione mirato prova **9 gap di singola vacancy**, non una previsione dei volumi potenziali sull'UE27. Un gap è una vacancy presente su pagina ufficiale ma assente nel catalogo per URL/identificativo; **non equivale a un nuovo stage verificato**. Il lavoro sui portali va trattato come ricerca di segnali, **mai** come mirroring automatico non autorizzato. iAgora pubblicizza [48 internship HR nei Paesi Bassi](https://www.iagora.com/work/en/internships/hr/netherlands) e Stageplaza [487 HR stage](https://stageplaza.nl/stage/hr-hrm/), ma questi totali non sono stati deduplicati, filtrati per attualità, identità azienda, lingua o candidabilità e non diventano KPI People Placement. **Il benchmark per country e portale resta incompleto**; non si può extrapolare 9/12 al resto dell'UE.

### 2. Quali ATS meritano l'automazione riutilizzabile?

**Connettori già presenti in `collector/adapters.py`:** `greenhouse`, `lever`, `recruitee`, `personio-xml`, `ashby`, `smartrecruiters`. Le documentazioni ufficiali confermano canali di sola lettura: [Greenhouse Job Board API](https://docs.greenhouse.io/job-board), [Lever Postings API](https://github.com/lever/postings-api), [Recruitee Careers Site](https://support.recruitee.com/en/articles/8213076-faq-api), [Personio XML](https://developer.personio.de/docs/retrieving-open-job-positions), [Ashby public postings](https://developers.ashbyhq.com/docs/public-job-posting-api). **API tecnicamente disponibile ≠ autorizzazione per qualsiasi host/tenant**: ogni fonte deve rispettare robots, allowlist, termini e policy v2; alcuni endpoint Ashby/SmartRecruiters e altri host possono risultare 401/403.

| Priorità | Riutilizzo | Rischio / azione |
|---|---|---|
| **A** | Greenhouse, Lever; Recruitee e Personio per feed con tenant validato | Inventario strutturato spesso economico; **verifica dell'applicazione specifica** ancora necessaria. Priorità al nuovo caso [Ampelmann su dominio careers](https://careers.ampelmann.nl/o/internship-people-organisation-1): il formato suggerisce Recruitee, **tenant e API da verificare**, non derivare automaticamente un URL |
| **B** | Ashby, SmartRecruiters; altri ATS con API documentata e accessibile | Solo dove i controlli host/robots consentono lettura; nessun 401/403 bypass, title/applicant-ID mismatch o form presunto |
| **C** | Workday (Stryker), Cornerstone (Henkel), career pages aziendali (IKEA/ING/ASML/PepsiCo) | Priorità di costo minore per il primo ciclo: candidatura spesso dinamica o multi-host; non codificare una singola vacancy e non inventare API generica |

**Importante:** il ramo [PR #56](https://github.com/nightlydeveloper8/eu-hr-internships/pull/56) contiene già l'adapter autorizzazione-separata JobTech→ATS ufficiale, con 1 caso Jobandtalent positivo **in staging**. Evitare duplicare quel connettore nel benchmark.

### 3. Qual è il rendimento per euro e per ora?

Le metriche attualmente disponibili permettono **costo fisico per ciclo**, non costo monetario certo e nemmeno rendimento marginale della raccolta ordinaria:

| Osservazione verificata | Richieste / byte / tempo | Delta stage HR policy v2 verificati in produzione |
|---|---|---:|
| Raccolta 16/11, [rapporto in stato progetto](stato-progetto.md) | **36.174 HTTP**, **4.159.256.878 byte**, **3.286 rendering**, **43.410,44 s-fonte cumulati** (= **12,06 ore-fonte**, non wall-clock) | **0 nuovi ID/stage** nel ciclo confrontato |
| Pilota JobTech→Jobandtalent su [Action #44086636248](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44086636248) | **10 GET**, **723.606 byte**, **13,467 s-fonte**, 0 rendering | **+1 stage in sola staging**; **0 in produzione** |
| Questo benchmark con due portali | **0 richieste BudgetClient**, 0 rendering/POST; **ricerche web esterne non conteggiate** nel budget collector | **0**; 9 gap ufficiali sono opportunità da verificare |

**Concentrazione di costo senza resa HR osservata nello stesso ciclo:** le **1.832 fonti prive di match HR** hanno usato **34.192/36.174 HTTP (94,5%)**, **3.765.755.480/4.159.256.878 byte (90,5%)** e **3.187/3.286 rendering (97,0%)**. Sono dati *di un singolo giorno*, **non** prova che tali fonti non produrranno internship HR nei prossimi giorni. La priorità economica è misurare su **più giorni** il rendimento per fonte e valutare poi frequenze differenziate/conservatrici, non disabilitare subito il 96% dei datori. Non sottrarre agli stage HR verificati già esistenti i costi di mantenimento e ri-verifica senza un confronto coerente.

Un costo `€/nuovo internship verified` **non è calcolabile** senza dati di fatturazione/consumo GitHub Actions e Cloudflare e con **0 nuovi stage** nel ciclo principale. Non dividere 36.174 per il **totale esistente 28**: quello misura un costo grossolano per stock, non il costo marginale di acquisizione. Analogamente, non dividere uno stage di staging per 13,467 secondi e presentarlo come throughput orario sostenibile: n=1 e durata non wall-clock.

**Contratto della prossima misura automatizzabile:** per ogni fonte e `run_id` registrare `official_leads`, `distinct_official_ids`, `same_id_application_v2`, `new_verified_catalog_ids`, `reverified_existing_ids`, `http_requests`, `response_bytes`, `renderings`, `wall_clock_seconds`, `source_seconds`, `actions_billable_minutes` e, quando disponibili, i costi monetari reali. Calcolare solo sui dati osservati `new_verified / wall_clock_hours` e `actual_eur / new_verified`; con denominatore 0 riportare **non calcolabile**, non 0 €/stage. Confrontare almeno **due cicli su giorni diversi**, preservando ID e non chiudendo per inventario parziale.

**Conclusione operativa:** prima provare il gate di Ampelmann con adapter riutilizzabile e inventario ufficiale; poi sfruttare i due ID PepsiCo tramite un unico canale aziendale se consentito; per IKEA e ING distinguere i nuovi job ID da offerte esistenti. Nessuna attivazione automatica, aumento di allowlist o merge derivano da questo benchmark.

## Misura, classificazione e beneficio reale (primo lotto)

- **7 lead**, **6 pagine ufficiali specifiche lette oggi** e **1 URL ufficiale storico nel catalogo non riletto (JDE)**, **5 non presenti per datore+titolo nella baseline**, **2 già presenti come `unverified` / possibili match**, **1 form pubblico visibile**, **0 stage policy v2 promossi**.
- Costo di **questa modifica al progetto**: **0 GET BudgetClient, 0 rendering, 0 byte collector, 0 POST**, nessun nuovo monitoraggio quotidiano, nessuna candidatura. Sono state usate ricerche/aperture web esterne al collector; il loro costo monetario non è misurato. Non attribuire risparmi o rendimento di produzione a questo report.
- **Beneficio effettivo:** backlog riproducibile di gap nel catalogo, con URL ufficiali, ID, classificazione linguistica e ordine di adattamento. La copertura **non è aumentata** su `main`.
- **Non** usare portali terzi come `source_type=universal-employer` o come proprietà del datore: rischio già osservato sul mirror storico JDE/Tilburg. Separare sempre discovery dalla lettura ATS ufficiale, con dedup per identità della vacancy.

## Lavoro successivo orientato al risultato

1. **Ampelmann:** controllare termini/robots dell'host e ATS, source ownership, inventario, form sullo stesso ID in un unico preflight BudgetClient *bounded*; poi due cicli di staging con contatori richieste/byte/tempo e zero POST. Se passa, proporre fonte **disabled** in PR dedicata, senza attivazione in produzione. Non è ancora un `verified`.
2. **Henkel e Stryker:** preferire la soluzione riutilizzabile per Cornerstone/Workday e controllo della pagina candidatura specifica, non eccezioni per URL individuali. Non aggiungere nuovi host alla allowlist senza review; rispettare auth/CAPTCHA/429 e budget.
3. **ASML e Hunkemöller:** distinguere pagina HR da candidatura completa, dare precedenza a requisiti linguistici che ammettono inglese; nessun abbassamento di policy v2.
4. **Philips/JDE:** aprire diagnosi della causa strutturale di application entry già nota, senza duplicare record e senza riaprire il mirror di terzi.
5. Per misurare il valore comparato, costruire **campioni replicabili in più paesi e più portali** solo se accesso consentito; il vero KPI è `nuovi stage HR distinti e verificati / HTTP, byte, secondi e manutenzione`, non il numero dichiarato dai portali.

**Confini:** documentazione e dati di benchmark su branch separato, nessuna fonte, catalogo o workflow modificati; nessun merge/rollout, scheduler o produzione. Riesaminare il materiale insieme alle PR #56 (feed nazionali) e alla Issue #18 (miglioramento resa), evitando lavoro ATS duplicato.
