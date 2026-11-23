# Scoperta ATS enterprise — 23 novembre 2026

Estensione di [#134](https://github.com/nightlydeveloper8/eu-hr-internships/pull/134) e del [dossier ATS iniziale](ats-tenant-discovery-2026-11.md). Ipotesi: gli stage HR si concentrano presso i grandi datori. Le chiavi delle bacheche descrivono la piattaforma e il sito carriere. La dimensione del datore richiede evidenza indipendente.

## Fase 0 — Accesso rivisto il 23 novembre 2026

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

## Fase 2 — Resa

| Campione | Tenant letti | Tenant con posting europei | Stage HR IT / ES | Prova e costo |
|---|---:|---:|---|---|
| Enterprise e Welcome to the Jungle | 0 | non dimostrato | non dimostrato / non dimostrato | 0 GET e 0 byte agli annunci; livello v2, costo per stage e stima con intervallo non dimostrati |
| Cinque ATS di #134 | 1.032 feed letti | 477 | 0 / 0 osservati | 13 segnali da feed, 2.163 GET, 304.889.247 byte e 1.426,645 s-fonte nel campione finale; circa 166 GET per segnale |

Il gate d’accesso non ha ammesso alcun campione. Zero letture non fornisce un denominatore di resa. Per un futuro campione ammesso, estrarre 100 chiavi per piattaforma senza reinserimento (censimento se meno), registrare esclusioni e duplicati, usare il classificatore corrente e mantenere solo le sedi UE27, CH o GB dimostrate dal posting. Budget proposto di 12 GET e 60 s per tenant, seriale sullo stesso host con crawl delay, stop su 429. Contare segnali e candidature v2 separatamente. Stimare separatamente la quota di tenant con almeno un segnale e il totale dei segnali, con intervalli per campionamento di tenant e non risposta esplicita. Per testare la concentrazione per taglia occorre stratificare anche per dimensione documentata del datore, geografia e copertura degli inventari. L’ipotesi sulle grandi aziende resta **non dimostrata**.

## Fase 3 — Proposta

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
