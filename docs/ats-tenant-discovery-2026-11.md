# Ricerca tenant ATS — 23 novembre 2026

Il passaggio all’indice colonnare sostituisce il CDX, che aveva restituito HTTP 504 nella prima versione della PR. I risultati coprono i prefissi testati in `CC-MAIN-2026-43`, `CC-MAIN-2026-39` e `CC-MAIN-2026-34`. Copertura di tutti i tenant europei **non dimostrato**. Il [riepilogo di ricerca](ats-tenant-discovery-2026-11.json) contiene conteggi, metriche e limiti. L’inventario con le chiavi dei tenant e i report live rimangono in `.staging/ats-tenant-discovery/`.

## Enumerazione e confronto con il registro

`scripts/ats_tenant_discovery.py` legge il catalogo dei crawl, i manifest `cc-index-table.paths.gz` e, con DuckDB 2.0 e `httpfs`, i footer delle 900 partizioni WARC dell’indice. I nomi numerici dei file risultano permutati rispetto all’ordine SURT. Per ogni prefisso, interseca l’intervallo semiaperto `[prefisso, prefisso + U+FFFF)` con min/max Parquet e consulta tutti i file che lo intersecano. Se mancano statistiche SURT o fallisce una lettura, marca la ricerca interessata come incompleta. Nessun WARC scaricato. I GET sono seriali, con timeout, un solo ritentativo HTTP e riuso dei footer. Il riepilogo conta GET, HEAD e byte dei corpi GET tramite Content-Length delle risposte DuckDB. Le durate delle query e il tempo a muro sono separati. [Documentazione dell’indice](https://commoncrawl.org/columnar-index) · [Log HTTP DuckDB](https://duckdb.org/docs/current/operations_manual/logging/overview)

I termini Common Crawl concedono accesso limitato, richiedono di rispettare i diritti e i termini dei titolari dei contenuti e vietano di interferire col servizio o aggirarne i controlli. Si è usato l’indice colonnare per l’aggregazione, con filtri e proiezione delle colonne necessarie. Le stringhe delle query delle vacancy e i corpi di pagina non fanno parte dell’export. [Termini Common Crawl](https://commoncrawl.org/terms-of-use) · [Indicazioni del server CDX](https://index.commoncrawl.org/)

| ATS | Tenant osservati | Già nel registro | Nuovi | Chiavi di riferimento nel registro |
|---|---:|---:|---:|---:|
| Greenhouse | 4.783 | 6 | 4.777 | 16 |
| Workable | 5.558 | 0 | 5.558 | 0 |
| Lever | 68 | 0 | 68 | 6 |
| Personio | 3.289 | 8 | 3.281 | 22 |
| Recruitee | 960 | 22 | 938 | 32 |
| Teamtailor | 1.233 | 0 | 1.233 | 1 |
| JKS/Talentech | 349 | 0 | 349 | 0 |
| InRecruiting | 0 | 0 | 0 | 2 |
| Altamira | 6 | 0 | 6 | 0 |
| Factorial | 46 | 0 | 46 | 0 |
| TalentClue | 0 | 0 | 0 | 0 |
| Bizneo | 1 | 0 | 1 | 0 |
| Welcome to the Jungle | 2.247 | 0 | 2.247 | 0 |
| softgarden | 630 | 0 | 630 | 0 |
| eRecruiter | 42 | 0 | 42 | 0 |
| Varbi | 253 | 0 | 253 | 0 |
| Jobylon | 17 | 0 | 17 | 0 |
| **Totale** | 19.482 | 36 | 19.446 | 79 |

Il passaggio finale ha letto 374 GET per 67.588.891 byte in 9.397 s a muro, con i footer già in cache. La scoperta dei footer ha usato 900 GET, 900 HEAD, 237.754.627 byte e 57.172 s cumulati nelle query. I passaggi di messa a punto e i manifest sono separati nel riepilogo JSON.

L’unità è la chiave pubblica del tenant. Le regioni Lever e Greenhouse sono distinte, con alias Greenhouse riuniti nella rispettiva regione. Personio usa l’host preciso. Il confronto include chiavi ATS dei registri fonti e datori, incluse fonti disabilitate, su `8b630bb`. “Nuovo” significa assente da tale confronto per chiave osservabile. Domini personalizzati, identità aziendali e alias fra famiglie richiedono riconciliazione. I conteggi derivano dalle catture storiche HTTP 200 e comprendono tenant con bacheche oggi vuote o irraggiungibili. I 68 Lever sono tutti della regione EU. Il controllo del prefisso globale senza filtro di stato non ha trovato catture nei tre crawl. Il recall di Lever globale e la spiegazione dello scarto dal benchmark del maintainer su `2025-43` sono **non dimostrato**. Il paese di ogni tenant resta `sconosciuto`.

## Staging e resa per paese

Campione casuale senza reinserimento, seed `2026-11-23`, fino a 300 nuove chiavi per ATS. Strati proporzionali basati su presenza in uno o più crawl, con almeno un’osservazione per strato non vuoto. Si usano i lettori esistenti e il classificatore invariato. Le sedi provengono dai campi di località del posting. Si contano i posting con almeno una sede riconosciuta in UE27, CH o GB. Una sede ambigua o senza paese riconoscibile resta sconosciuta. Una vacancy con più paesi può apparire in più righe geografiche.

I test usano feed pubblici documentati, GET con scope esatto e robots live, paginazione e redirect secondo i lettori esistenti. Rispettano il crawl delay, con minimo locale di 1 s per host negli esperimenti. Il client interrompe le letture dell’host in presenza di 429. I termini dei fornitori rivisti per lo staging e i precedenti sui singoli host sono documentati. Una pubblicazione continuativa richiederebbe anche revisione di proprietà, termini applicabili e uso previsto. [Revisione ATS e Workable](sette-fonti-ats-2026-11-21.md) · [Greenhouse Job Board](https://developers.greenhouse.io/job-board.html) · [Lever Postings API](https://github.com/lever/postings-api) · [Personio XML](https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML) · [Recruitee](https://docs.recruitee.com/docs/feed) · [Workable](https://workable.readme.io/reference/jobs-1)

| ATS | Campione / feed letti | Tenant con posting UE/CH/GB | Posting europei | Segnali HR per paese | GET / byte / s-fonte | Costo per segnale (GET / byte / s) | Stima tenant con rilevazione (IC 95%) |
|---|---:|---:|---:|---|---|---|---|
| Greenhouse | 300 / 252 | 53 | 1.100 | GB 1 | 301 / 143.161.539 / 308.335 | 301.0 / 143.161.539 / 308.33 | 15.9 [2–183] |
| Workable | 300 / 231 | 26 | 197 | 0 osservati | 604 / 23.434.933 / 303.420 | **non dimostrato** | 0.0 [0–181] |
| Lever | 68 / 67 | 53 | 1.438 | PL 1 | 80 / 38.444.756 / 79.519 | 80.0 / 38.444.756 / 79.52 | 1.0 [1–1] |
| Personio | 300 / 217 | 146 | 1.128 | DE 4 | 589 / 12.858.710 / 395.221 | 147.2 / 3.214.678 / 98.81 | 32.8 [6–163] |
| Recruitee | 300 / 265 | 199 | 2.980 | FR 1; NL 6 | 589 / 86.989.309 / 340.150 | 84.1 / 12.427.044 / 48.59 | 15.6 [4–57] |

Il campione finale ha richiesto 2.163 GET, 304.889.247 byte e 1426.645 s-fonte. In aggiunta, 452 GET, 1.893.862 byte e 90.083 s-fonte per tentativi Recruitee con trust store non adatto, ritentativi Greenhouse e osservazioni Workable fuori dal campione finale dopo aver scartato il falso tenant `media`. Il controllo RSS Teamtailor è conteggiato a parte.

Le righe riportano segnali classificati da feed. La verifica v2 del percorso di candidatura e il costo per candidatura diretta sono **non dimostrato**. Le letture Workable riuscite confermano l’uso del lettore esistente per l’inventario pubblico. I suoi test verificano lo scope del redirect, la coerenza dello shortcode, i duplicati e l’assenza di prova del modulo dal solo feed. Le altre famiglie senza lettore esistente restano fuori dalle misure di resa. I GET contano i tentativi urllib, compresi robots e redirect. I byte comprendono i corpi letti dal client, con esclusione dei corpi di errore e redirect non letti. I secondi-fonte comprendono attese e fallimenti, possono sovrapporsi fra ATS e non rappresentano costo monetario.

La stima operativa conta quanti tenant nuovi restituirebbero almeno un segnale con lo stesso protocollo e le stesse condizioni di accesso. L’intervallo approssimato al 95% combina intervalli di Wilson per strato con correzione Bonferroni e usa conteggi esatti negli strati censiti. Un fallimento contribuisce zero rilevazioni al protocollo. L’estrapolazione del **numero effettivo di stage**, inclusi i tenant illeggibili e le candidature verificabili, resta **non dimostrato**. Nei campioni senza fallimenti e con abbastanza riscontri per strato, lo script può stimare il totale di segnali feed con una correzione per popolazione finita.

Riferimenti storici non omogenei: un lotto di cinque universal-employer ha prodotto uno stage verificato con 50 richieste e 71,73 s-fonte. Il run EURES ha contato 352 schede verificate nel servizio pubblico in 330 richieste miste e 656 s, circa 0,94 richieste e 1,86 s per scheda. La comparabilità con le candidature dirette e il costo in byte dei due riferimenti sono **non dimostrato**. [Diario del 15 novembre](stato-progetto.md) · [EURES, confronto e log](lead-eures-rechecks-2026-11-21.md)

## ATS locali

I giorni indicati sono stime di implementazione e test per un adattatore a partire da un endpoint ammissibile, esclusi i tempi di revisione di accesso. Tutti i conteggi sono candidati osservati, circoscritti alle forme URL elencate. Il valore zero indica nessuna chiave recuperata dalle catture conformi ai filtri.

| ATS | Chiavi | SURT e prova della forma | Feed e impegno stimato |
|---|---:|---|---|
| InRecruiting / Zucchetti | 0 | `it,intervieweb,`, host o host/slug in una pagina career. [Colorobbia](https://inrecruiting.intervieweb.it/colorobbia/it/career) · [Zucchetti](https://zucchetti.intervieweb.it/it/career) | Feed conforme **non dimostrato**. Parsing HTML paginato, 2–4 gg |
| Altamira | 6 | `com,altamiraweb,`, host e percorso jobs. [Air Dolomiti](https://airdolomiti.altamiraweb.com/jobs) | Feed conforme **non dimostrato**, HTML, 2–3 gg |
| Factorial | 46 | `com,factorialhr,`, host del tenant. [Absolute Internship](https://absoluteinternship.factorialhr.com/) · [Configurazione dominio ufficiale](https://help.factorialhr.com/en_US/managing-my-company-account/how-to-register-your-company%E2%80%99s-domain) | Company Page pubblica. Feed senza chiave conforme **non dimostrato**, 2–4 gg |
| TalentClue | 0 | `com,talentclue,` e `com,talentclue,careers)/es/group/`, più le varianti en/ca. [ACEBSA](https://acebsa.talentclue.com/es/acebsa) · [Bacheca condivisa](https://careers.talentclue.com/es/group/340663/offers/menu/modal) | Alias gruppo/host e feed conforme **non dimostrato**, 3–5 gg |
| Bizneo | 1 | `com,bizneo,`, percorso di carriera. [Globalia Call Center](https://globaliacallcenter.bizneo.com/jobs) | Un candidato indice, pubblicazione attuale e feed conforme **non dimostrato**, 3–5 gg |
| Welcome to the Jungle | 2.247 | `com,welcometothejungle,www)/fr/companies/`, altre lingue e host app. [Doctolib](https://www.welcometothejungle.com/fr/companies/doctolib) | Profilo pubblico, feed riutilizzabile conforme **non dimostrato**, 3–5 gg |
| softgarden | 630 | `io,softgarden,` e `de,softgarden,`. [Bacheca Builtech](https://builtech.softgarden.io/job/55815822/Spontanans%C3%B6kan) | Frontend API v3 documentata con Client ID, esclusa dal pilota senza chiavi. Feed alternativo conforme **non dimostrato**, 2–3 gg. [Documentazione](https://support.softgarden.de/en/articles/501015-how-can-i-use-the-frontend-api-v3-to-integrate-my-career-site-with-softgarden) |
| eRecruiter | 42 | `at,bewerberportal,`, `eu,kandidatenportal,`, `net,erecruiter,`; pagina job/jobs. [Domini ufficiali](https://support.erecruiter.net/portal/de/kb/articles/integration-des-bewerberportals) · [Bacheca](https://jobs.erecruiter.net/Jobs) | API PublishedJob documentata, inventario anonimo conforme **non dimostrato**, 3–5 gg |
| Varbi | 253 | `com,varbi,`; chiave host. [Karolinska Institutet](https://ki.varbi.com/en/what%3Ajob/jobID%3A847812/where%3A4/) | Pagine pubbliche, feed conforme **non dimostrato**, 2–4 gg |
| Jobylon | 17 | `com,jobylon,emp)/companies/`; ID numerico. [Esempio ufficiale](https://emp.jobylon.com/companies/6/) | API documentata, feed anonimo conforme **non dimostrato**, 2–4 gg. [API](https://support.jobylon.com/en/articles/69898-jobylon-api) |
| JKS / Talentech | 349 | `net,hr-manager,candidate)/applicationinit.aspx`; ID `cid`. [JKS](https://candidate.hr-manager.net/ApplicationInit.aspx?ProjectId=157629&cid=1601) | Feed multi-tenant conforme **non dimostrato**, 3–5 gg |
| Teamtailor | 1.233 | `com,teamtailor,`; host. [RSS ufficiale](https://support.teamtailor.com/en/articles/11171756-rss-feed-how-to-guide) | RSS pubblico documentato. Lettore di staging compatibile con la produzione **non dimostrato**, 1–2 gg più review |

SmartRecruiters e Ashby restano esclusi. Per misurare recall usare un campione indipendente di board ufficiali, includendo i domini personalizzati. InRecruiting e TalentClue hanno esempi pubblici confermati fuori dall’insieme delle catture recuperate. Per Bizneo e per i prefissi che includono servizi incidentali va verificata manualmente la precisione su un campione.

## Proposta di produzione

1. Prima di proporre una fonte, associare il tenant a un datore tramite prove ufficiali, conservare scope, termini e livello di prova. Registrare la fonte disabilitata e usare un hold. Per datori con crawler attivo l’hold aziendale può entrare in conflitto con il provisioning. Valutare un hold a livello di fonte in un intervento separato.
2. Lotti di 500 dopo approvazione esplicita. Turno giornaliero per tenant con posting europei e settimanale per i restanti. Tenere separati feed letti senza esiti europei e accessi incompleti, con backoff e nuova revisione per errori persistenti. Rigenerare mensilmente l’elenco da Common Crawl, con diff degli alias e candidati da revisionare, senza attivazione automatica.
3. Scenario di budget da validare, con 100 dei 500 tenant a cadenza giornaliera e 400 settimanali. Picco pianificato di 158 letture per ciclo. Con 12 richieste e 45 s per tenant, massimo teorico di 1.896 richieste logiche e 7.110 secondi-worker. Imporre un tetto di 1.900 richieste logiche e partizioni anche per host in modo che il burst rispetti il crawl delay. Con 16 shard e 6 worker, distribuzione ideale uniforme e worker liberi, sono circa due ondate da 45 s per shard. Contesa e code per host condivisi possono dominare il p95. Variazione reale della durata e nuovo numero di shard **non dimostrato**. Mantenere 16 shard nella prima stima, misurare p95 e richieste effettive in staging e ridurre il lotto operativo prima di alzare la concorrenza.
4. Crawler universal-employer oggi eliminabili **non dimostrato**. Confrontare gli ID e le prove v2 in raccolte affiancate, comprese sedi e percorsi ufficiali fuori feed. Berenschot/Recruitee resta un candidato di confronto dal precedente inventario. La PR non modifica registri, collector o trigger. [Inventario del 21 novembre](inventario-ats-2026-11-21.md)

## Riproduzione

In una venv dedicata dentro `.staging/` installare DuckDB 2.0 con `httpfs`; per macOS `truststore` è facoltativo e usa la verifica TLS nativa. Eseguire `python scripts/ats_tenant_discovery.py` e poi `python scripts/ats_tenant_yield.py --live` (aggiungere `--native-trust` per il trust store di sistema). `--provider` restringe il pilota; `--resume` riusa tentativi della stessa sessione di staging. Con `--retry-transport` ripete solo i precedenti errori URL. I sistemi senza adapter esistente vengono segnalati senza richieste. In CI i test d’identità, selezione e resa usano fixture e mock senza DuckDB.
