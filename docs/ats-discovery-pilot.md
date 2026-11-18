# EU ATS Discovery — primo pilota in sola lettura

## Scopo

Preparare una coda di canali ufficiali di recruiting ATS per Germania (DE), Francia (FR), Belgio (BE) e Irlanda (IE), senza attivarli, eseguire HTTP o alterare le vacancy. L'obiettivo finale e' alimentare autonomamente il monitoraggio quotidiano europeo, non ampliare il censimento manuale.

## Baseline e fonte delle evidenze

- Main di riferimento: e7056c3351d06bedaa1f0d4a8e443f5a6e424a78 (12 novembre 2026).
- `docs/career-channel-scan.json`: 346 registrazioni storiche di scansione; 25 aziende con collegamenti ATS rilevati nell'insieme DE/FR/BE/IE (19 DE, 6 FR, 0 BE, 0 IE). Non significa che tutte possano essere integrate o che i link siano ancora attivi.
- La coda usa **solo** righe `reviewed` il cui URL di scansione coincide con il `career_url` o `website_url` dichiarato dal datore. Redirect verso un altro host non sono prove sufficienti.
- BE e IE restano nel campione anche se le vecchie scansioni non forniscono collegamenti positivi. Zero scoperta NON significa zero opportunita' nel paese.
- I `target_countries` dei datori sono candidati di ricerca, non evidenza che una vacancy sia ubicata in quel paese.

## Esito misurato del campione storico (sei datori per paese, se disponibili)

Il file `docs/ats-discovery-review.json` contiene la coda prodotta sullo snapshot storico e controllata da un test di regressione. Risultati del campione: DE 6 datori / 7 identita' ATS; FR 6 / 5; BE 6 / 0; IE 4 / 0. Le 12 identita' comprendono **6 gia' registrate**, **1 nuovo candidato in attesa di access review**, **1 access-review** e **4 provider non supportati**. Il candidato Personio Futrue e' gia' segnalato nella precedente `docs/additional-channel-review.json` per un robots.txt che ne nega l'accesso: **non va attivato senza nuova autorizzazione**, e non e' un risultato produttivo.

Questo piccolo campione non dimostra un aumento delle fonti utilizzabili. E' utile soprattutto per rendere riproducibili i gap: in BE e IE serve ancora acquisire prove ufficiali nuove, e per FR emergono soprattutto integrazioni Teamtailor non ancora disponibili.

## Funzionalita'

Il nuovo modulo `collector/ats_channel_discovery.py` riconosce tenant su Greenhouse, Lever, Recruitee e Personio XML da URL pubblicati nelle pagine censite. Collassa duplicati della stessa board/tenant, segnala se una fonte e' gia' presente nello stesso datore, rileva conflitti se un altro datore possiede la stessa board e produce esclusivamente candidature con `enabled=false`.

Ashby e SmartRecruiters sono segnalati come access-review, Teamtailor e Softgarden come non supportati dal connettore di questa PR. L'endpoint di feed e' un **hint da controllare**, non un URL autorizzato. Nessuna identificazione per semplice somiglianza di nome o gruppo societario.

Per generare la coda JSON in modo riproducibile, dalla root:

```sh
python3 scripts/ats_discovery_pilot.py --countries DE FR BE IE --per-country 6 --output docs/ats-discovery-review.json
```

Senza `--output`, il comando stampa il risultato e non scrive alcun file. Per provare gli stessi controlli su tutti i paesi, passare i codici dei 27 stati UE; e' sempre un audit sui dati gia' raccolti, non una scansione web.

## Misura dei costi e limiti

| Indicatore di questa PR | Risultato |
| --- | --- |
| Richieste HTTP aggiuntive del prototipo | 0 |
| Browser/rendering aggiuntivi | 0 |
| Nuove fonti abilitate | 0 |
| Nuovi stage HR verified in produzione | 0 |
| Modifiche a catalogo, aziende, sources, workflow | 0 |
| Tempo CI e costo monetario | Non ancora misurati |

Il rapporto enumera `companies_sampled`, `detected_channels`, `review_candidates`, `already_registered`, `ownership_review` e `blocked_or_unsupported` per paese. Ogni riga include la pagina originale, il link osservato, gli ID esistenti e la condizione di revisione host/robots. Sono risultati storici e **non** rinnovano la freschezza delle candidature.

## Verifiche e secondo ciclo

```sh
python3 -m unittest tests.test_ats_channel_discovery -v
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

I test nuovi includono due esecuzioni identiche di discovery, URL non HTTPS o con credenziali, pagina di origine non dichiarata, redirect cross-host, provider bloccati, dedup tenant e conflitto di proprieta'. I test gia' presenti della pipeline presidiano due passaggi di raccolta/finalizzazione; il nuovo codice non viene eseguito dal collector giornaliero.

## Passaggio successivo (non incluso)

Collegare, in una PR separata dopo revisione, la produzione periodica di osservazioni ufficiali ai checkpoint del crawler esistente. Abilitare nuove fonti solo dopo verifica live di host/robots, proprieta' del tenant, feed completo, paese effettivo, costi di richieste e idempotenza del catalogo. Non toccare il gate Dynamic ATS `pilot-v1` della Issue #23. Nessun merge o rollout autorizzato qui.

## Esito verifica d'accesso ATS (18/11/2026)

Censimento dal rapporto di copertura: le fonti generiche hanno incontrato SuccessFactors in 55 casi, Workday in 38, SmartRecruiters in 25, Personio in 24, Recruitee in 20, Teamtailor in 15 e Greenhouse in 13.

| Piattaforma | Esito | Prova |
|---|---|---|
| Workday (`*.myworkdayjobs.com`) | **Non integrabile** | Il robots.txt consente l'API delle bacheche (blocca solo `/refreshFacet/`). Però Cloudflare risponde **429 al client del progetto** (urllib) anche sul robots.txt, mentre accetta curl con lo stesso User-Agent dichiarato. Il filtro è sull'impronta del client, non sulla frequenza: cambiare client per passare sarebbe aggirare un blocco. Bacheche viste: Accenture, Airbus, Dow, GE Aerospace, Hitachi, LEGO, Medtronic, Michelin, Miele, Philips, Roche, Thales, Thermo Fisher, ESET, Infobip e altre. |
| SuccessFactors (portali `career*.successfactors.*`) | **Escluso** | robots.txt: `User-agent: *` / `Disallow: /`. I siti aziendali "Career Site Builder" su domini propri restano gestiti dallo scraper generico solo se il loro robots.txt lo consente. |
| SmartRecruiters | Escluso (già noto) | Il robots.txt esclude i bot generici. |
| Greenhouse / Lever (Doctolib, Delivery Hero, Qonto, Mollie, Picnic, sennder, Personio, Back Market, Team Lewis) | **Bacheche dismesse** | Le API ufficiali, sia USA (`boards-api.greenhouse.io`, `api.lever.co`) sia UE (`api.eu.lever.co`), rispondono 404 per tutti i codici. Le fonti `greenhouse-*` e `lever-*` restano disattivate: le aziende hanno cambiato ATS e i link visti dallo scraper sono vecchi. |

Conseguenza per la Fase 2: le due piattaforme più diffuse tra le multinazionali non si possono usare entro i vincoli del progetto (rispetto di robots.txt e nessun aggiramento di blocchi). Le strade rimaste sono:
1. Recruitee, Personio e Teamtailor sui siti delle singole aziende, con i raccoglitori esistenti o un nuovo raccoglitore Teamtailor.
2. I siti carriere delle multinazionali su domini propri che pubblicano dati `JobPosting` (Fase 3).
3. EURES, che porta gli annunci dei servizi pubblici di tutti i paesi.

## Fase 3: siti carriera con sitemap e JobPosting (18/11/2026)

Molte multinazionali pubblicano gli annunci su piattaforme (Radancy, Phenom) che espongono una sitemap e, su ogni pagina, i dati strutturati schema.org `JobPosting`. Il collettore `employer-sitemap` legge solo quei dati: nessuna estrazione dal testo della pagina.

- **Filtro sull'URL** (`url_slug_prefilter: true`): queste sitemap sono globali (fino a 31.000 annunci per Marriott). Si leggono solo le pagine il cui titolo nell'URL nomina già uno stage HR; poi la pagina viene classificata per intero. Lacuna nota: uno stage HR il cui URL non contiene né il termine HR né quello di stage.
- **Paese**: da `addressCountry` del JobPosting. Se è vuoto e una sezione del sito pubblica un solo paese, si usa una regola rivista (`url_country_patterns`, es. Adecco Francia `/26094/`).
- **Fonti aggiunte**: Procter & Gamble, The Adecco Group, AstraZeneca, Roche, BAT, Sanofi, Thermo Fisher, GE Aerospace, Mars, Marriott. Per Roche, Thermo Fisher e GE Aerospace sostituiscono il crawler automatico, che non trovava l'elenco degli annunci.
- **Verifica**: invariata (politica v2). Si conferma solo se la candidatura avviene su un modulo legato allo stesso annuncio. BAT e Unilever si verificano; Adecco (Lumesse TalentLink), Marriott (Oracle Cloud HCM) e Roche (Workday) hanno moduli solo JavaScript, quindi i loro stage restano "da verificare".
- **Prova del 18/11** (lettura reale, senza budget): Adecco 128 stage HR (127 in Francia, 1 in Portogallo), Marriott 9 (MT, PT, NL, ES, IT, DE, FR), Roche 3 (PL, DE), BAT 1 verificato (FR), Sanofi 1 (FR), P&G 12 pagine HR tutte chiuse ("has been filled"), AstraZeneca, Thermo Fisher, GE Aerospace e Mars 0 al momento.
- **Escluse**: SuccessFactors con dominio proprio (IDEMIA: nessun JobPosting), Vodafone (403), Coca-Cola (429), McDonald's (403), DHL (sitemap in errore 500), PepsiCo (URL senza titolo: il filtro non è applicabile e leggere 2.800 pagine al giorno non è proporzionato).

### Fase 3b (18/11/2026, sera): seconda mappatura

- **Esaminati 185 portali** di multinazionali in due tornate (probe automatico: robots.txt, sitemap, JobPosting, titoli leggibili negli URL). Circa 120 nomi di host non esistono o non rispondono; altri sono esclusi per robots (Novo Nordisk, Safran), 403 (Hyatt, IHG, Boehringer Ingelheim, UBS, BNP Paribas), siti SuccessFactors senza JobPosting (JTI, Swiss Re) o pagine senza JobPosting (EY, Capgemini, ZF, Volvo Group, Merck KGaA, TE, Atlas Copco).
- **Integrati 21 portali**: ABB, Thales, Siemens Healthineers, Allianz, Kuehne+Nagel, UPS, ING, Société Générale, Philips, BD, FedEx, Takeda, Mastercard, Hilti, Marsh McLennan, HPE, Stryker, AkzoNobel, Infineon, WTW, Ericsson. Allianz, BD, Hilti, Philips e Thales sostituiscono il crawler automatico. Infineon ed Ericsson (Eightfold) vietano `/` ma consentono esplicitamente `/careers`, dove stanno gli annunci.
- **Correzione Phenom**: la pagina servita senza JavaScript contiene sempre il riquadro "the job … is no longer available / has been filled", che il browser nasconde per gli annunci attivi. Lo stato si legge ora dal `jobDetail` incorporato (phApp): `hits` > 0 = annuncio attivo, 0 = chiuso. Prima di questa correzione gli stage di P&G, ABB, Thales e Allianz risultavano chiusi per errore.
- **Date**: le scadenze nel formato `2026/12/01` (Société Générale) sono ora lette correttamente.
