# Ricerca tenant ATS europei — 23 novembre 2026

Base `8b630bb`. Ripresa esplicita della ricerca. L’[inventario di ricerca](ats-tenant-discovery-2026-11.json) contiene **zero catture utilizzabili**. Tutte le query del pilota sono fallite prima della prima pagina. Numero di tenant distinti, quota europea, recall ed esaustività: **non dimostrato**. Un inventario completo dei tenant pubblici richiederebbe anche una misura della copertura dei domini personalizzati e delle bacheche assenti dall’indice.

## Common Crawl

Il catalogo pubblico ha indicato `CC-MAIN-2026-43` e `CC-MAIN-2026-39` come i due crawl più recenti. Su entrambi, conteggio delle pagine CDX per Workable e InRecruiting via query per dominio con un blocco per pagina. Quattro query, due tentativi ciascuna, tutti HTTP 504. Il pilota strumentato ha registrato 9 GET inclusa la lettura del catalogo, 35.501 byte di corpi letti e 127,413 s cumulati nelle misure del client, che in questa esecuzione includevano parte del backoff. I corpi degli errori non erano letti. Probe separati su Recruitee, Personio e Lever hanno restituito 504. Anche il controllo puntuale `berenschot.recruitee.com/` sul crawl più recente ha restituito 504 in 5,319 s. Dopo questi errori la scansione CDX è stata fermata.

I termini Common Crawl (revisione 7 marzo 2024, §§1–3) concedono accesso limitato e richiedono di rispettare leggi, diritti e termini separati dei titolari dei contenuti. Vietano di interferire con il servizio, aggirarne le protezioni e raccogliere informazioni personali per usi separati. Il server indica l’indice colonnare per le aggregazioni estese. Il pilota ha interrogato il solo indice Common Crawl, in serie con pausa e backoff, senza scaricare WARC o conservare query string di annunci nell’inventario. Il codice accetta solo gli ID dei crawl e i domini previsti, limita pagine e byte e conserva lo stato delle query parziali. [Termini Common Crawl](https://commoncrawl.org/terms-of-use) · [Server CDX](https://index.commoncrawl.org/) · [Indice colonnare](https://commoncrawl.org/columnar-index)

| ATS | Chiave candidata | Riferimenti distinti nel registro locale | Tenant CDX / già presenti / nuovi |
|---|---|---:|---|
| Recruitee | subdominio `recruitee.com` | 32 | non dimostrato |
| Lever | prima componente del percorso, regione EU distinta | 6 | non dimostrato |
| Greenhouse | slug di bacheca, alias globali uniti e regione EU distinta | 16 | non dimostrato |
| Personio | host `jobs.personio.de/.com` | 22 | non dimostrato |
| Teamtailor | subdominio `teamtailor.com` | 1 | non dimostrato |
| Workable | slug su `apply.workable.com` | 0 | non dimostrato |
| JKS/Talentech | `cid` numerico su `candidate.hr-manager.net/ApplicationInit.aspx` | 0 | non dimostrato |
| InRecruiting/Zucchetti | subdominio `intervieweb.it` con pagina career o jobs | 2 | non dimostrato |
| Altamira, Factorial, Bizneo | domini candidati e percorsi career, richiedono validazione | 0 | non dimostrato |
| TalentClue | subdominio candidato | 0 | non dimostrato |
| Welcome to the Jungle | slug `companies`, candidata scheda pubblica | 0 | non dimostrato |
| softgarden | subdomini candidati `softgarden.io/.de` | 0 | non dimostrato |

I 79 riferimenti provengono da URL riconoscibili e chiavi degli adapter nei registri, incluse fonti disabilitate. Sono il denominatore di un primo controllo di recall interno per ATS. Il rapporto catture/chiavi note è calcolabile quando le relative query sono complete. Aggiungere un campione indipendente di tenant ufficiali per paese e controllare anche la percentuale di falsi positivi, gli alias fra domini e i profili editoriali. Copertura di installazioni con dominio personalizzato, varianti locali e nuovi provider: **non dimostrato**. Un TLD del provider e una lingua condivisa da più paesi lasciano il paese `sconosciuto`. Usare un indirizzo documentato o altra prova univoca e conservare la provenienza. Il paese del tenant e il luogo di lavoro del posting sono due campi distinti. [Esempio Talentech JKS](https://candidate.hr-manager.net/ApplicationInit.aspx?ProjectId=157629&cid=1601) · [InRecruiting](https://www.in-recruiting.com/en/) · [TalentClue](https://welcome.talentclue.com/hubfs/Mi_empresa_y_Filiales_Onboarding.pdf) · [Factorial](https://help.factorialhr.com/en_US/applicant-tracking-system/how-to-display-job-openings)

Per una prova mirata, eseguire `python3 scripts/ats_tenant_discovery.py --provider workable --page-cap 1`. Per estrarre l’intero quadro osservabile usare l’indice colonnare filtrando le partizioni dei crawl e proiettando URL, status e timestamp, con gli stessi regimi di identità. Una lettura completa del colonnare resta da eseguire. Per un benchmark, campionare datori con ATS ufficialmente documentato, misurare il recall per famiglia e aggiungere famiglie scoperte al di fuori delle regole correnti quando documentate. SmartRecruiters e Ashby sono esclusi.

## Staging e confronto dei costi

Campione riproducibile per ATS dai soli tenant nuovi osservati, senza reinserimento, `min(300, N)`, seed `2026-11-23`. `scripts/ats_tenant_yield.py` legge l’inventario in `.staging/ats-tenant-discovery/`. Il preflight stampa gli stati. L’opzione `--live` usa un file di staging `access-review.json` con una riga per tenant (`ats`, `tenant`, `observed_url`, `hosts`, `terms_url`, `terms_basis`, `approved_for_staging`) e il controllo robots live dell’adapter. Budget proposto di 12 richieste logiche e 45 s per tenant, un tenant alla volta. Sono cablati gli adapter pubblici esistenti di Recruitee, Personio, Greenhouse, Lever e Workable. Per le altre famiglie, disponibilità di un feed conforme utilizzabile con gli adapter esistenti **non dimostrato**. Applicare il classificatore esistente e conservare il livello feed negli esiti. Prima di contare uno stage candidabile serve un passaggio di verifica v2 su identità e percorso ufficiale, con host e termini revisionati e deduplicazione col catalogo. La prova tecnica di una candidatura e il legame con il datore vanno entrambi dimostrati.

Esecuzione staging con campione vuoto: 0 tenant letti, 0 GET ai feed, 0 byte feed. Posting, stage HR per paese, esiti v2, costo unitario ed estrapolazione **non dimostrato**. Il costo della ricognizione storica separata non è imputato a questo campione. I conteggi delle richieste degli adapter sono logici. Per il confronto definitivo misurare anche GET effettivi, redirect, byte e attese, separando POST di lettura, costi di verifica e costo monetario.

Per ciascun ATS, con quadro di campionamento completo e letture valide, stimare `N × media degli stage verificati per tenant` con un intervallo al 95% basato sul campionamento di tenant e correzione per popolazione finita. Per rese rare o distribuzioni fortemente asimmetriche usare un intervallo adeguato ai conteggi e pubblicare anche il tasso di tenant con almeno uno stage. Un campione con zero riscontri richiede un limite superiore per quel tasso. Con risposte mancanti riportare la copertura e l’incertezza da non risposta. La stima vale per il quadro osservato e va deduplicata tra ATS prima di aggregarla. La stima europea resta **non dimostrato**.

| Riferimento storico | Costo osservato | Unità della resa |
|---|---|---|
| Universal-employer, cinque fonti del pilota del 15 novembre | 50 richieste e 71,73 secondi-fonte per 1 stage verificato | campione mirato, byte non dimostrato |
| EURES, run 44879531709 | 330 richieste miste e 656 s per 352 match verificati nel report, circa 0,94 richieste e 1,86 s per match | scheda del servizio pubblico, costo per candidatura diretta e byte del run non dimostrato |
| ATS da CDX | non dimostrato | feed e prova v2 da misurare separatamente |

Il confronto di costo per nuovo stage diretto richiede lo stesso periodo, verifica v2 e deduplicazione, contando anche i tenant tentati senza resa. [Diario, lotto del 15 novembre](stato-progetto.md) · [EURES, ricontrollo e log del run](lead-eures-rechecks-2026-11-21.md)

## Proposta per produzione

1. Registrare in una futura PR le candidature a fonte con `enabled: false`, revisione di proprietà, prova d’accesso, host esatti e hold. Il hold aziendale esistente richiede attenzione quando il datore ha già un crawler attivo. Prevedere un hold per fonte in un intervento separato, oppure rinviare il caso fino alla decisione sul crawler precedente. Attivazione a lotti dopo approvazione esplicita del maintainer e verifica del primo ciclo.
2. Scenario iniziale da validare in staging: 100 tenant per lotto, 12 GET logici e 45 s per fonte, tetto complessivo di 360 GET per ciclo per i nuovi ATS. Rileggere quotidianamente i tenant con stage HR aperti o da verificare. Distribuire su sette giorni i tenant letti con successo senza stage HR. Tenere i fallimenti in coda con motivazione e backoff, senza equipararli a feed vuoti. Interrompere le richieste su host limitati. Un refresh mensile dell’indice propone i nuovi tenant e registra gli alias e i cambiamenti, senza promozione automatica.
3. `collect.yml` ha 16 shard e 6 worker per shard. Con 100 tenant, di cui 10 giornalieri e 90 a rotazione, un ciclo avrebbe circa 23 letture (fino a 276 GET logici ai tetti per fonte). A 45 s per lettura, circa 1.035 secondi-worker di budget cumulato. Con distribuzione uniforme di al massimo due letture aggiuntive per shard e worker liberi, l'ordine di grandezza è un massimo di 45 s di lavoro in più per shard, ignorando attese e contesa. Lo scenario peggiore con 23 letture serializzate sullo stesso host arriva a circa 17 minuti entro i budget per tenant. Durata reale e necessità di aumentare gli shard **non dimostrato**. Tenere 16 shard nella proposta iniziale e misurare p95 del job più lento, concentrazione dei tenant per host, richieste effettive e durata a muro prima di ampliarla.
4. Crawler universal-employer sostituibili oggi: **non dimostrato**. Individuarli per `source_id` con un confronto affiancato che dimostri parità su tutti gli stage verificati e mantenga le prove e gli ID. Berenschot è un candidato per il confronto per la sovrapposizione storica con Recruitee. Tenere in conto le pagine ufficiali, i canali di candidatura via email e le sedi che il feed non copre. [Inventario ATS del 21 novembre](inventario-ats-2026-11-21.md)

I file della ricerca sono in `scripts/`, `tests/` e `docs/`, fuori dai trigger push di `collect.yml`. Nessuna fonte è stata aggiunta o attivata.
