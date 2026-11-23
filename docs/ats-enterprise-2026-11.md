# Scoperta ATS enterprise — 23 novembre 2026

Estensione di [#134](https://github.com/nightlydeveloper8/eu-hr-internships/pull/134) e del [dossier ATS iniziale](ats-tenant-discovery-2026-11.md). Ipotesi: gli stage HR si concentrano presso i grandi datori. Le chiavi delle bacheche descrivono la piattaforma e il sito carriere. La dimensione del datore richiede evidenza indipendente.

## Aggiornamento — nuova regola di accesso, 23 novembre 2026

Questa revisione applica la [regola del maintainer](../AGENTS.md#4-fonti-e-raccolta-dati). Il silenzio dei termini non esclude un canale. Ogni ammissione si limita al percorso pubblico verificato e ogni tenant deve superare il preflight robots. La fase 1 precedente resta una fotografia storica.

| Piattaforma | Decisione | Condizione decisiva e prova del 23 novembre |
|---|---|---|
| Workday | Ammesso per sitemap e dettagli consentiti | Robots 200 su [Damen](https://damen.wd3.myworkdayjobs.com/robots.txt) e [Huhtamaki](https://huhtamaki.wd103.myworkdayjobs.com/robots.txt) in due controlli distanziati di almeno 60 s, dopo i 429 precedenti. Entrambi dichiarano sitemap; i risultati del campione confermano letture pubbliche. Esclusi i singoli host con 429 persistente. [Documentazione siti esterni](https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/career-sites/san1394588983205.html) · [Termini Workday](https://www.workday.com/en-us/legal/site-terms.html) |
| Oracle Recruiting Cloud | Incerto | Robots 404 sull’[host iniziale](https://ejwl.fa.us2.oraclecloud.com/robots.txt) e su quattro host campionati. Formato candidato [Recruiting CE](https://docs.oracle.com/en/cloud/saas/human-resources/farws/api-recruiting-ce-job-requisitions.html); la condizione robots resta non dimostrata. |
| iCIMS | Ammesso per sitemap e dettagli consentiti | Tutti e quattro gli host del preflight aggiuntivo hanno robots 200 e una sitemap. [Esempio Bridgewater](https://careers-bridgewater.icims.com/robots.txt) · [Termini iCIMS](https://www.icims.com/legal/terms-of-use/) · [Campi JobPosting documentati](https://developer-community.icims.com/platform/services/standard-xml-feed-job-boards). |
| Cornerstone | Ammesso per il dettaglio JSON-LD dove confermato | [OHB](https://career-ohb.csod.com/robots.txt) robots 200 con crawl delay 10 s. Un dettaglio pubblico same-host rende un JobPosting in 2 GET, 22.050 byte, 10,167 s. I [termini Cornerstone](https://www.cornerstoneondemand.com/terms-of-use/) vietano i bot su cornerstoneondemand.com, distinto dal tenant CSOD. |
| Taleo | Incerto | Robots 404 su [TTEC](https://ttec.taleo.net/robots.txt), [Chicago](https://chicago.taleo.net/robots.txt) e su altri quattro host campionati. La condizione robots resta non dimostrata. |
| Avature | Ammesso per le sitemap careers consentite | Robots 200 con sitemap pubbliche su [AMS](https://amswh.avature.net/robots.txt) e [Bloomberg](https://bloomberg.avature.net/robots.txt). Confermate in staging le sottositemap localizzate e alcune pagine anonime con JobPosting. [Termini Avature](https://www.avature.net/terms-of-use/) · [Termini Bloomberg](https://www.bloomberg.com/notices/tos/). |
| SAP SuccessFactors | Incerto; career5 escluso | [career5](https://career5.successfactors.eu/robots.txt) vieta il percorso. Otto host Jobs2web hanno robots 200 senza sitemap dichiarata. Un dettaglio pubblico per host risponde 200, tutti e otto senza JobPosting rilevabile. JSON pubblico alternativo non dimostrato. [Documentazione SAP](https://help.sap.com/docs/successfactors-recruiting/setting-up-and-maintaining-sap-successfactors-recruiting/site-configuration-in-career-site-builder-settings). |
| Phenom | Non ammesso sul sito proprietario; clienti incerti | [Robots careers.phenom.com](https://careers.phenom.com/robots.txt) 200 e sitemap dichiarate. I [termini Phenom §§1 e 4](https://www.phenom.com/terms--conditions) includono i sottodomini propri e vietano espressamente crawler e bot; distinguono le installazioni dei clienti, da verificare separatamente. |
| Welcome to the Jungle | Non ammesso | [Condizioni](https://www.welcometothejungle.com/fr/pages/terms) vietano espressamente l’estrazione automatizzata. Esclusione confermata. |

Lo script di staging usa GET pubblici, host esatto, nessun redirect, user agent di People Placement e robots HTTP 200. Minimo di 2 s tra richieste sullo stesso host o più se lo richiede il crawl delay. Budget per tentativo di 7 GET, 55 s, 2 MB per risposta e fino a tre dettagli. Per le sitemap, legge un solo ramo figlio in presenza di un indice. Per Cornerstone cerca fino a tre URL storici di dettaglio entro il board, poi misura il markup dal vivo. I lotti registrano errori e blocchi. Per Workday è stato ripetuto il preflight per i primi 429; i 429 ripetuti fermano l’host. I due host di controllo hanno un intervallo di almeno 60 s. La stessa attesa per ciascun host del successivo campione non è dimostrata dai log iniziali. Lo script finale registra Retry-After e impone un’attesa minima di 60 s a partire dalla fine del giro precedente. I token di navigazione, i login e le candidature restano fuori dallo scope.

| ATS | Ammessi / campione | Pagine lette | Tenant con sede UE/CH/GB | Segnali HR IT / ES / totale | GET / byte / s-fonte | Stima tenant con segnale (IC 95%) |
|---|---:|---:|---:|---|---|---|
| Workday | 40 / 100 | 79 | 7 | 0 / 0 / 0 | 278 / 5.233.962 / 346.142 | 0 [0–163] |
| iCIMS | 68 / 100 | 96 | 3 | 0 / 0 / 0 | 304 / 4.907.982 / 1122.442 | 0 [0–82] |
| Avature | 42 / 48 | 50 | 0 | 0 / 0 / 0 | 243 / 7.747.381 / 385.299 | 0 [0–0] censimento |
| Cornerstone | 8 / 100 | 109 | 0 | 0 / 0 / 0 | 209 / 736.744 / 1145.780 | 0 [0–31] |

Sono stati estratti 348 tenant, con 158 percorsi ammessi e 334 pagine di dettaglio lette. Il campione ha richiesto 1.034 GET, 18.626.069 byte di corpi riusciti e 2.999,663 s-fonte cumulati, inclusi i ritentativi. Non è un tempo a muro. Costo per stage **non dimostrato** perché il protocollo non ha rilevato segnali HR. I controlli di formato Jobs2web e OHB sono separati, con 18 GET, 527.970 byte e 32,753 s cumulati incluse le ricerche di URL nel colonnare.

Le quote operative contano tenant nuovi con almeno un segnale rilevato dallo stesso protocollo limitato. L’intervallo Wilson al 95% serve a quantificare la rarità delle rilevazioni, con conteggio esatto per i 48 tentativi del censimento Avature. Fallimenti e pagine non campionate riducono la capacità di rilevare segnali. Il totale degli stage nella popolazione e la verifica v2 restano **non dimostrati**. Per confronto, #134 iniziale ha letto 1.032 feed, con 477 tenant con posting europei, 13 segnali HR (IT 0, ES 0) e circa 166 GET per segnale. Il campione enterprise legge fino a tre dettagli per bacheca; i due protocolli hanno sensibilità diversa.

### Percorso JSON-LD su 100 tenant ammessi

Sottocampione casuale riproducibile dai 158 tenant ammessi, seed `2026-11-23-jsonld`. 56 tenant hanno prodotto pagine di dettaglio. **123/153 pagine** espongono un singolo JobPosting leggibile. Titolo 115/123, sede europea riconoscibile 10/123, data 115/123, link di candidatura esplicito 0/123. Tutti e quattro i campi 0/123.

La sede misura un paese UE27, CH o GB riconosciuto dalle località strutturate del posting. Il link di candidatura richiede un target esplicito nello stesso host. Il solo `url` in schema.org identifica la scheda e `directApply` è un indicatore, quindi non si contano come target. I body sono elaborati in memoria; in staging si salvano soltanto metriche per tenant e campo. Per riprodurre usare lo script `scripts/ats_enterprise_yield.py --provider <ats>` dopo l’enumerazione; i report sono in `.staging/ats-enterprise/`. L’opzione `--summary` ricalcola le tabelle a partire dai lotti completati.

Priorità aggiornata per un adattatore in staging dopo revisione del disegno di campionamento: Workday e iCIMS (3–5 giorni ciascuno), Avature (2–4 giorni), Cornerstone (3–5 giorni). La priorità riflette formato riproducibile e potenziale di copertura; la classifica per costo per stage verificato resta **non dimostrata**.

## Prima valutazione di accesso — storico

Sono stati controllati i robots di host rappresentativi e il perimetro dei termini applicabili prima del campione. Le decisioni sono per il protocollo richiesto, con 100 tenant per piattaforma. Una sitemap del singolo datore è evidenza di un formato pubblicato, mentre l’accesso agli altri tenant richiede un controllo proprio. I risultati robots e gli inventari grezzi sono in `.staging/ats-enterprise/`.

| Piattaforma | Esito | Robots osservato | Formato e termini |
|---|---|---|---|
| Workday | Incerto | 429 su [Damen](https://damen.wd3.myworkdayjobs.com/robots.txt) e [Huhtamaki](https://huhtamaki.wd103.myworkdayjobs.com/robots.txt); stop su entrambi | Workday documenta siti pubblici esterni e report Find Jobs. Endpoint JSON usato dalle pagine, accesso automatizzato ai tenant e termini applicabili allo stesso endpoint **non dimostrato**. [Documentazione](https://doc.workday.com/admin-guide/en-us/human-capital-management/recruiting/career-sites/san1394588983205.html) · [Termini del sito Workday](https://www.workday.com/en-us/legal/site-terms.html) |
| SAP SuccessFactors | Incerto; non ammesso su career5 | [career5](https://career5.successfactors.eu/robots.txt) restituisce 200 e vieta `/` e i percorsi con company, con eccezione `/login`. [jobs.sap.com](https://jobs.sap.com/robots.txt) restituisce 403 | Career Site Builder è documentato. Feed, sitemap o JSON-LD idonei e termini operativi sugli altri tenant **non dimostrato**. [SAP Help](https://help.sap.com/docs/successfactors-recruiting/setting-up-and-maintaining-sap-successfactors-recruiting/site-configuration-in-career-site-builder-settings) · [Termini SAP](https://www.sap.com/about/legal/terms-of-use.html) |
| Oracle Recruiting Cloud | Incerto | [Host Oracle Cloud campione](https://ejwl.fa.us2.oraclecloud.com/robots.txt) restituisce 404 | Oracle documenta Recruiting CE Job Requisitions. Accesso anonimo ammesso sul tenant e applicabilità dei termini al feed **non dimostrato**. [API Oracle](https://docs.oracle.com/en/cloud/saas/human-resources/farws/api-recruiting-ce-job-requisitions.html) · [Termini sito Oracle](https://www.oracle.com/legal/terms.html) |
| Taleo | Incerto | 404 su [Chicago](https://chicago.taleo.net/robots.txt) e [TTEC](https://ttec.taleo.net/robots.txt); errore di trasporto sull’host Oracle Taleo provato | Career Section esterna documentata. Termini di raccolta e formato strutturato senza autenticazione **non dimostrato**; il contratto software non stabilisce i termini dei siti dei datori. [Career Section](https://docs.oracle.com/en/cloud/saas/taleo-enterprise/20d/otrcg/implementing-recruiting.pdf) · [Accordo software](https://www.oracle.com/us/corporate/contracts/taleo/taleo-pm-general-terms-conditions-1840909.pdf) |
| Avature | Incerto | [Bloomberg](https://bloomberg.avature.net/robots.txt) pubblica regole per `/careers` e la sitemap XML `/careers/sitemap_index.xml`; altri host provati hanno dato errore di trasporto | Sitemap dichiarata, contenuto non letto. Scope dei termini del datore e metadati delle vacancy nell’XML **non dimostrato**. [Termini sito Avature](https://www.avature.net/terms-of-use/) · [Privacy recruiting Baker McKenzie](https://www.bakermckenzie.com/en/avature-privacy-policy) |
| Cornerstone / CSOD | Incerto | [OHB](https://career-ohb.csod.com/robots.txt) restituisce 200 con crawl delay di 10 s | I termini vietano l’accesso automatizzato a cornerstoneondemand.com. Termini del distinto host CSOD OHB e formato pubblico leggibile **non dimostrato**. [Termini Cornerstone](https://www.cornerstoneondemand.com/terms-of-use/) |
| iCIMS | Incerto | [Medpace](https://jobs-medpace.icims.com/robots.txt) restituisce 404 | iCIMS documenta mappature JSON-LD e un feed XML per job board. Feed anonimo e termini per il campione **non dimostrato**. [Specifiche feed](https://developer-community.icims.com/platform/services/standard-xml-feed-job-boards) · [Termini sito iCIMS](https://www.icims.com/legal/terms-of-use/) |
| Phenom | Incerto | [Host storico](https://careers.phenompeople.com/robots.txt) reindirizza al [robots del sito corrente](https://careers.phenom.com/robots.txt), 200 con regole specifiche e segnale `ai-input=no` | Career site documentato; formato strutturato anonimo e condizioni trasferibili ai domini dei clienti **non dimostrato**. [Prodotto](https://www.phenom.com/use-cases/attract-engage-candidates-career-site-personalization) · [Termini sito Phenom](https://www.phenom.com/terms--conditions) |
| Welcome to the Jungle | Non ammesso | [www](https://www.welcometothejungle.com/robots.txt) e [app](https://app.welcometothejungle.com/robots.txt) restituiscono 200 e dichiarano sitemap | Le condizioni vietano espressamente scraping e copia automatizzata di contenuti e profili, con eccezione circoscritta agli operatori di motori di ricerca pubblici. Nessuna ulteriore interrogazione in questo studio. [Condizioni, obblighi degli utenti](https://www.welcometothejungle.com/fr/pages/terms) |

Preflight robots: 17 tentativi GET, 4.568 byte di corpi riusciti letti e 6,409 s cumulati. I corpi degli errori e le consultazioni dei termini tramite ricerca web non sono inclusi. La fase non ha richiesto sitemap, dettagli, feed o endpoint di candidatura.

## Fase 1 — Indice colonnare

Union dei tre crawl più recenti, `CC-MAIN-2026-43`, `CC-MAIN-2026-39`, `CC-MAIN-2026-34`. Lo script `scripts/ats_enterprise_discovery.py` riutilizza i footer già acquisiti da #134, legge solo gli intervalli SURT pertinenti e conserva chiavi deduplicate dalle catture HTTP 200. Usa DuckDB solo in staging. L’export è in `.staging/ats-enterprise/inventory.json`. Per riprodurre, eseguire `.staging/ats-duckdb/bin/python scripts/ats_enterprise_discovery.py` dalla radice dopo aver preparato la venv descritta nel dossier principale. [Metodo, limiti e termini di Common Crawl](ats-tenant-discovery-2026-11.md#enumerazione-e-confronto-con-il-registro)

| Piattaforma | Prefissi SURT | Chiavi di bacheca | Regola |
|---|---|---:|---|
| Workday | `com,myworkdayjobs,`, `com,myworkdaysite,` | 4.399 | Host e sito carriere; locale scartato. Sul secondo dominio, host e `/recruiting/<tenant>/<site>` |
| SuccessFactors | `eu,successfactors,`, `com,successfactors,`, `com,jobs2web,` | 8 | Host e percorso career con selettore `company` per istanze condivise; host su Jobs2web. Tutte le otto osservazioni sono su Jobs2web |
| Oracle Recruiting Cloud | `com,oraclecloud,` | 1.562 | Host e ID sito nella route Candidate Experience |
| Taleo | `net,taleo,` | 533 | Host e ID Career Section. Forme TBE e domini personalizzati fuori campione |
| Avature | `net,avature,` | 48 | Host con route carriera, incluse varianti con locale |
| Cornerstone | `com,csod,` | 829 | Host e ID sito ATS ove presente |
| iCIMS | `com,icims,` | 2.194 | Host con route jobs o careerportal |
| Phenom | `com,phenompeople,`, `com,phenom,` | 1 | Host con route job/career. I domini brandizzati dei datori possono sfuggire interamente |
| Welcome to the Jungle | Fase esclusa | non dimostrato | Il conteggio storico #134 è 2.247; resta storico |
| **Totale** | | **9.574** | Bacheche osservate entro queste regole, con possibili alias |

Passaggio finale con cache dei footer: 129 GET, 30 HEAD, 46.983.357 byte, 6,601 s a muro, zero errori nelle query. Il primo passaggio diagnostico, prima del filtro delle route tecniche Taleo, aveva lo stesso traffico e 8,287 s a muro. Il conteggio delle bacheche non misura gruppi aziendali, sedi, occupazione in UE o opportunità attive. Il recall per domini personalizzati, in particolare Phenom e SuccessFactors, è **non dimostrato**.

## Prima valutazione di resa — storico

| Campione | Tenant letti | Tenant con posting europei | Stage HR IT / ES | Prova e costo |
|---|---:|---:|---|---|
| Enterprise e Welcome to the Jungle | 0 | non dimostrato | non dimostrato / non dimostrato | 0 GET e 0 byte agli annunci; livello v2, costo per stage e stima con intervallo non dimostrati |
| Cinque ATS di #134 | 1.032 feed letti | 477 | 0 / 0 osservati | 13 segnali da feed, 2.163 GET, 304.889.247 byte e 1.426,645 s-fonte nel campione finale; circa 166 GET per segnale |

Il gate d’accesso non ha ammesso alcun campione. Zero letture non fornisce un denominatore di resa. Per un futuro campione ammesso, estrarre 100 chiavi per piattaforma senza reinserimento (censimento se meno), registrare esclusioni e duplicati, usare il classificatore corrente e mantenere solo le sedi UE27, CH o GB dimostrate dal posting. Budget proposto di 12 GET e 60 s per tenant, seriale sullo stesso host con crawl delay, stop su 429. Contare segnali e candidature v2 separatamente. Stimare separatamente la quota di tenant con almeno un segnale e il totale dei segnali, con intervalli per campionamento di tenant e non risposta esplicita. Per testare la concentrazione per taglia occorre stratificare anche per dimensione documentata del datore, geografia e copertura degli inventari. L’ipotesi sulle grandi aziende resta **non dimostrata**.

## Proposta iniziale — storico

La classifica per stage stimati per costo è **non dimostrata**. Questo ordine riguarda la validazione tecnica dopo un esito d’accesso positivo. Le durate sono stime di sviluppo e test per un adattatore circoscritto, escluse la revisione di accesso e la verifica v2.

| Ordine di verifica | Piattaforma | Motivo e lavoro stimato |
|---:|---|---|
| 1 | Avature | Sitemap esplicita su un host. Validare la struttura e il costo di un GET per annuncio con JSON-LD, 2–4 gg |
| 2 | iCIMS | Schema dei campi documentato. Verificare se esiste un feed anonimo ammesso sul campione, 2–4 gg |
| 3 | Oracle Recruiting Cloud | Definizione endpoint disponibile. Condizioni, inventario e paginazione, 3–5 gg |
| 4 | Workday | Più chiavi osservate, robots con 429 sui due host testati. Validare canale pubblico ammesso, paginazione e alias, 4–6 gg |
| 5 | Cornerstone, Taleo | Scope per sito, formati e possibili varianti dei percorsi, 3–5 gg ciascuno |
| 6 | SuccessFactors, Phenom | Prima misurare recall sui domini personalizzati e trovare host accessibili, 4–6 gg ciascuno |
| — | Welcome to the Jungle | Escluso dal protocollo di estrazione |

La PR conserva registri, collector, file del bot e workflow. Le misure sono di ricerca in staging.
