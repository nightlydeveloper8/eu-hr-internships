# Copertura per paese e acquisizione degli stage HR

## Stato al 20 novembre 2026

Il [catalogo `7c5ce80`](https://github.com/nightlydeveloper8/eu-hr-internships/blob/7c5ce8037f9bdca7fd869d57668c9f420f40edc0/data/catalog.json) ha **39 stage con candidatura diretta, in 6 dei 27 paesi UE**. Dei 21 a zero, cinque hanno schede di stage attive su EURES o JobTech e sedici non ne hanno neppure una in catalogo. Tredici dei 21 non hanno datori con monitoraggio nazionale documentato nel rapporto di ricerca. Includendo la Svizzera, EURES ha **384** schede attive senza candidatura verificata nel catalogo; JobTech ne ha **5**. Nei Paesi Bassi sono 230 delle 354 schede EURES nell'UE. I conteggi escludono working student e traineeship.

EURES è l'unica ricerca pubblica integrata a scala UE. Il [ciclo ordinario](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44744205480) ha letto 5.726 schede EURES dopo la deduplica interna, con 330 richieste e circa 96,2 MB, e si è fermato al limite di richieste. Il collector cerca offerte tipizzate come internship e titoli multilingue in tutta Europa in ordine fisso, con `locationCodes` vuoto. La presenza del paese nel registro è il perimetro di ammissione. Il run non rende osservabile la copertura di ricerca per mercato, e l'ordine per lingua favorisce chi compare prima del limite. JobTech è integrato soltanto per la Svezia. Il resto deriva dai siti dei datori e dagli ATS con sede esplicita, o da una coda di ricerca ancora in revisione. [Codice di raccolta](https://github.com/nightlydeveloper8/eu-hr-internships/blob/0b08c30478c545a2e79b78ae0296d176c29f366f/collector/public_sources.py) · [Fonti pubbliche](../fonti-pubbliche.md)

## Confronto live EURES, ricerche geografiche

Un confronto in sola lettura sullo stesso endpoint, senza paginazione e con un termine per mercato. La tabella misura i record con sede nel paese nella prima pagina e il filtro «internship» separato. Il controllo NL ha restituito 41 stage HR riconosciuti su 50 schede, già presenti con lo stesso ID. Il test non ha cercato moduli di candidatura.

| Paese | Risultati del paese nella query globale | Query con filtro paese | Query internship per paese | Stage HR riconosciuti con il filtro geografico |
| --- | ---: | ---: | ---: | ---: |
| PL | 1 | 50 | 0 | 0 |
| IE | 0 | 2 | 0 | 0 |
| CZ | 1 | 50 | 0 | 0 |
| DK | 0 | 7 | 0 | 0 |

Il filtro ha soddisfatto il controllo geografico nel campione. Nei quattro paesi a zero schede aperte, il campione mirato ha letto 109 schede pertinenti geograficamente contro due delle query globali. Ha prodotto zero stage HR riconosciuti. Il test delimita un problema di ricerca e mostra la necessità di canali nazionali o aziendali alternativi. La resa di più espressioni locali e pagine resta da misurare. Costo totale del test: 14 richieste, 2.452.665 byte e 131,09 s. [Run pilota](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44766676817) · [Filtro paese EURES](https://europa.eu/eures/portal/jv-se/advanced-search?page=1%26resultsPerPage%3D10%26orderBy%3DBEST_MATCH%26locationCodes%3Des%2Cpt%26previousPageType%3DfindJob%26lang%3Den)

## Sequenza di lavoro

1. **Convertire le schede esistenti.** Partire da Italia, Svizzera e Svezia, che insieme hanno 65 schede pubbliche e zero candidature dirette. In Italia e Svizzera cercare i corrispondenti inventari ufficiali. Per la Svezia, cinque schede hanno un collegamento esterno già disponibile per una revisione del percorso. Austria, Finlandia e Lussemburgo hanno piste descritte sotto.
2. **Dare una strategia a chi è a zero anche come scoperta.** Per PL, CZ, IE e DK il confronto a parità di termine ha già isolato i limiti del campione EURES. Cercare rispettivamente tramite datori in polacco, datori in ceco, JobsIreland e Workindenmark, poi provare i canali ammissibili. Per i restanti mercati a zero, usare la pagina pubblica nazionale e termini locali per individuare datori con posizioni HR effettive. L'elenco pubblico della Commissione è una rubrica per questa ricerca, non una licenza di acquisizione. [Rete PES UE](https://employment-social-affairs.ec.europa.eu/policies-and-activities/coordination-employment-and-social-policies/european-network-public-employment-services-pes-network/public-employment-services_en)
3. **Cambiare l'unità di pianificazione EURES.** Provare un primo giro per paese prima della paginazione competitiva. Ridistribuire le richieste esistenti e misurare copertura delle query per paese, schede HR distinte nuove per 100 richieste, candidature dirette, byte e chiusure. Confrontare anche le opportunità perse nei paesi già produttivi. Il giro per paese è una proposta, da valutare prima di una modifica alla raccolta ordinaria.
4. **Continuare la copertura NL.** Portare avanti i comuni e il secondo lotto Recruitee su sedi con poche candidature, registrandone la resa separatamente dall'apertura di nuovi paesi.

## Percorso per mercato

Dirette e pubbliche sono stage HR aperti con evidenza policy v2 entro 48 ore dal catalogo. Storiche da verificare sono schede HR con stato unverified, utilizzabili come piste senza attribuire disponibilità. I datori monitorati sono il valore `companies_monitored_in_country` del [rapporto nazionale](https://github.com/nightlydeveloper8/eu-hr-internships/blob/0b08c30478c545a2e79b78ae0296d176c29f366f/docs/country-research-progress.json). Nessun numero dimostra una copertura nazionale completa.

| Paese | Dirette | Pubbliche | Da verificare | Datori monitorati | Canale e azione |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| AT | 0 | 4 | 1 | 0 | [AMS «alle jobs»](https://www.ams.at/arbeitsuchende/topicliste/bewerbung-praktikum). Le quattro schede EURES non dichiarano il datore. Cercare stage direttamente tramite AMS, poi inventario del datore. |
| BE | 4 | 18 | 3 | 7 | [VDAB, Actiris e Le Forem](https://employment-social-affairs.ec.europa.eu/policies-and-activities/coordination-employment-and-social-policies/european-network-public-employment-services-pes-network/public-employment-services_en). Cercare per regione e lingua, replicare Recruitee su datori con stage. API VDAB subordinata ad accordo. |
| BG | 0 | 0 | 0 | 0 | [Agenzia per l'impiego](https://www.az.government.bg/). Cercare «стаж човешки ресурси» su servizio nazionale e inventari dei datori; verificare condizioni di riuso. |
| CH (extra UE) | 0 | 30 | 1 | 0 | EURES e siti dei datori identificati nelle 30 schede. Campione per regione linguistica, FR/DE/IT. Job-Room richiede consenso per la ripubblicazione. |
| CY | 0 | 0 | 0 | 0 | [Servizio pubblico](https://www.mlsi.gov.cy/). Confrontare HR internship e termini greci, poi risalire a datori con annunci in sede cipriota. |
| CZ | 0 | 0 | 1 | 2 | [MPSV](https://data.mpsv.cz/web/data/uchazeci-a-volna-mista). Il precedente campione di 39.552 offerte aveva zero stage HR. Cercare inventari aziendali in ceco e inglese prima di ripetere il download. |
| DE | 4 | 28 | 33 | 24 | EURES e inventari ufficiali dei datori. Estendere il percorso Recruitee provato su ABRIO. Accesso diretto Jobsuche già escluso in [revisione](../fonti-pubbliche.md). |
| DK | 0 | 0 | 0 | 2 | [Workindenmark/Jobnet](https://workindenmark.dk/getting-started/finding-vacancies-in-denmark/use-our-job-portal). Alternare «HR internship» e «praktik i HR», distinguendo stage universitari e apprendistati. |
| EE | 0 | 0 | 0 | 0 | [Töötukassa](https://www.tootukassa.ee/). Cercare «personalipraktika» e «värbamine», poi controllare le pagine di datori con sede dichiarata. |
| ES | 1 | 2 | 20 | 6 | [SEPE](https://www.sepe.es/) come pista pubblica da qualificare. Siti dei datori con «prácticas recursos humanos» e «beca selección»; riusare il canale BSH già verificato. |
| FI | 0 | 2 | 0 | 0 | [Job Market Finland](https://tyomarkkinatori.fi/en/instructions-and-support/interfaces/interfaces-for-job-postings). API di lettura con whitelist IP secondo la revisione. Prima risalire a Carrot e StaffPoint dalle due schede EURES e riprendere la pista Barona. |
| FR | 7 | 39 | 137 | 15 | EURES e carriere aziendali con «stage RH» e «stage recrutement». Riprendere l'esito SmartRecruiters a livello di famiglia ATS. Accesso diretto France Travail già escluso in [revisione](../fonti-pubbliche.md). |
| GB (extra UE) | 0 | 0 | 7 | 0 | Fuori da EURES. Ricerca presso datori britannici e graduate careers ufficiali con «HR internship» o «people placement», controllando la sede. DWP esclusa e Reed in sospeso in [revisione](../fonti-pubbliche.md). |
| GR | 0 | 0 | 0 | 0 | [DYPA](https://www.dypa.gov.gr/). Cercare «πρακτική άσκηση ανθρώπινου δυναμικού» e HR internship; recuperare un canale del datore dalle offerte con sede greca. |
| HR | 0 | 0 | 0 | 1 | [HZZ](https://www.hzz.hr/). Cercare «studentska praksa» e «ljudski resursi» su portale nazionale e siti dei datori; confermare azienda e città. |
| HU | 0 | 0 | 2 | 2 | [NFSZ](https://nfsz.munka.hu/). Combinare «HR gyakornok» e «toborzás» con «HR internship», iniziando dai due datori che hanno già avuto raccolta parziale. |
| IE | 0 | 0 | 0 | 1 | [JobsIreland](https://jobsireland.ie/en-US/browse-jobs). Confrontare stage HR, people e talent acquisition con gli inventari dei datori; escludere programmi generici senza posizione HR. |
| IT | 0 | 30 | 39 | 4 | EURES: 30 schede attive attribuite a Gi Group; il relativo collector aziendale è parziale con zero corrispondenze. Cercare i corrispondenti annunci ufficiali per ID, sede e titolo. Kering e Société Générale sono piste indipendenti. |
| LT | 0 | 0 | 0 | 0 | [Užimtumo tarnyba](https://uzt.lt/). Cercare «personalo praktika» più «HR internship» e collegare i risultati al datore. |
| LU | 0 | 1 | 3 | 0 | [ADEM JobBoard](https://adem.public.lu/fr/demandeurs-demploi/consulter-offres-demploi/adem-jobboard.html). Prima cercare l'originale BorgWarner dalla scheda EURES, poi «stage RH», «HR internship» e «Praktikum Personal». |
| LV | 0 | 0 | 0 | 0 | [NVA](https://www.nva.gov.lv/). Cercare «personāla prakse» e «HR internship»; verificare l'inventario del datore prima della proposta di fonte. |
| MT | 0 | 0 | 1 | 0 | [Jobsplus](https://jobsplus.gov.mt/). Cercare «HR internship» e «recruitment placement» presso datori con sede maltese e percorso di candidatura pubblicato. |
| NL | 22 | 230 | 154 | 47 | EURES, datori e Recruitee. Proseguire il secondo lotto per province con poche opportunità e continuare la mappatura dei comuni. Riusare le query locali come controllo della ricerca paese per paese. |
| PL | 0 | 0 | 10 | 5 | EURES Polonia e datori ufficiali. Cercare «stażysta/stażystka w dziale HR», riprendendo Saint-Gobain. [ePraca](https://oferty.praca.gov.pl/portal/assets/for-integrators/warunki-udostepniania-ofert-pracy-z-systemu-ePraca.pdf) documenta accesso gratuito, con domanda firmata e IP fisso. Accesso da tenere sospeso con le decisioni attuali. |
| PT | 1 | 0 | 1 | 2 | [IEFP](https://www.iefp.pt/) come pista da qualificare. Cercare «estágio recursos humanos» e riprendere gli inventari dei datori Emma e Unit4. |
| RO | 0 | 0 | 0 | 0 | [ANOFM](https://www.anofm.ro/). Cercare «stagiu resurse umane» e «internship recrutare», poi verificare le schede degli inventari aziendali. |
| SE | 0 | 5 | 3 | 3 | JobTech fornisce cinque schede con link esterni. Prima seguire la [prova Jobandtalent #83](https://github.com/nightlydeveloper8/eu-hr-internships/pull/83) e riconciliare gli ID. Distinguere «praktik» da impiego per studenti. |
| SI | 0 | 0 | 0 | 0 | [ESS](https://www.ess.gov.si/). Cercare «kadrovska praksa» e «HR internship» su servizio nazionale e datori. Riprendere i risultati danneggiati da accesso fallito con fonte ufficiale alternativa. |
| SK | 0 | 0 | 0 | 0 | [ÚPSVAR](https://www.upsvar.sk/). Cercare «stáž personalistika» e «stáž ľudské zdroje», poi cercare un percorso pubblico del datore. |

`python -m scripts.audit_eu27_coverage` ricalcola dal catalogo i conteggi UE distinguendo stage con candidatura diretta, schede pubbliche attive e paesi senza opportunità aperte osservate. Il rapporto lascia disponibili i campi storici per i confronti precedenti. In particolare, `unverified_job_records` rimane il conteggio storico inclusivo delle schede pubbliche e non è la colonna «Da verificare» di questa tabella.

I canali nazionali indicati sono indirizzi per la ricerca. Prima di leggere automaticamente una nuova fonte servono verifica di riuso, robots.txt e accesso. Dall'annuncio al catalogo diretto serve la stessa posizione presso il datore, con corrispondenza di ID o altra prova univoca e percorso accessibile. Il pilota non ha attivato fonti e non ha modificato il catalogo.
