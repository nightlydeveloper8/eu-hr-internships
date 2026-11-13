# People Placement — preflight Wikidata Belgio/Irlanda (13 novembre 2026)

## Decisione e limiti
Pilota esplorativo **non eseguito**: massimo 25 aziende per BE e 25 per IE, nessun nuovo collector, crawl giornaliero, host, API a pagamento, modifica catalogo o promozione a `verified`. Obiettivo: nuove candidature HR **verificabili da fonti ufficiali**, non il numero di aziende censite.

Base consultata: `main` `c1bd2b8066603c97c596cfdd868f03417736bbbf`. `AGENTS.md` non compare nell'albero ricorsivo di questo commit; consultati `README.md`, `docs/architecture.md`, `docs/stato-progetto.md`, Issue #18, #23 e PR #35.

## Preflight di accesso e policy

Fonti ufficiali:
- Wikimedia Foundation API Usage Guidelines: https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_Usage_Guidelines
  - User-Agent riconoscibile, rispetto di throttling/rate limiting/licenze sempre obbligatorio; robot policy esplicitamente obbligatoria per consumo automatico **su larga scala**.
  - L'uso di API coerente con la policy non richiede di per sé autorizzazione preventiva, ma ciò non è un permesso incondizionato per qualsiasi percorso.
- Wikidata Data access: https://www.wikidata.org/wiki/Wikidata:Data_access
  - Query Service per interrogazioni ristrette; API per entità note in piccoli batch; dump per volumi elevati; indicazioni su User-Agent, robot policy, compressione, 429 e timeout.
- Manuale WDQS: https://www.mediawiki.org/wiki/Wikidata_query_service/User_Manual
  - Timeout massimo query 60 s; budget di 60 s elaborazione ogni 60 s per client; arresto/backoff su 429 e `Retry-After`; limite documentato di 5 query parallele/IP (non obiettivo del pilota: usarne 1).
- Limiti API Wikimedia introdotti nel 2026: https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits
- `https://www.wikidata.org/robots.txt` accessibile al browser di documentazione il 13/11: per `User-agent: *` contiene `Disallow: /w/`, `Disallow: /api/` e `Disallow: /wiki/Special:`. Non confondere il divieto di crawling/indicizzazione con un giudizio legale definitivo sull'uso delle API ufficiali.
- Endpoint ufficiale SPARQL: https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service (indica `query.wikidata.org/sparql` e `/bigdata/namespace/wdq/sparql`); il file `query.wikidata.org/robots.txt` **non è stato letto direttamente con successo**. Fonti terze segnalano `Disallow: /sparql` e `/bigdata`, ma l'affermazione non è verificata da fonte primaria in questa esecuzione.

**Esito per People Placement:** accesso automatizzato mirato supportato in generale dalla documentazione Wikimedia, ma non ancora autorizzabile *operativamente secondo il vincolo del progetto di rispettare robots.txt*, senza chiarire il trattamento degli endpoint API/SPARQL nel caso specifico e senza una verifica diretta del robots WDQS. Una risposta HTTP 200 non basterebbe a chiarirlo. Non effettuare GET/POST di dati contro endpoint disallowed al solo scopo di testare se funzionano.

**Preflight di rete nel runtime di esecuzione (13/11):** tentati tre GET diagnostici verso:
1. `https://query.wikidata.org/robots.txt`
2. `https://www.wikidata.org/robots.txt`
3. `https://www.wikidata.org/w/api.php?action=query&meta=siteinfo&format=json`

Tutti e tre falliti **prima dell'HTTP** con `NameResolutionError: Temporary failure in name resolution`. Richieste HTTP completate verso Wikidata: **0**; record di entità scaricati: **0**; durate HTTP: **non misurabili**. Le letture delle pagine di policy tramite browser di ricerca non sono equivalenti a chiamate sperimentali API/WDQS con User-Agent controllato.

## Baseline ufficiale già presente in repository

Snapshot `data/catalog.json`: `updated_at=2026-11-13T07:36:08.215689+00:00`, `update_status=partial`, 336 record totali. Il dato **non** prova una nuova raccolta completamente riuscita.

| Metrica (non Wikidata) | BE | IE |
| --- | ---: | ---: |
| Aziende identificate in `docs/country-research-progress.json` | 12 | 5 |
| Aziende monitorate nel paese nello stesso report | 4 | 1 |
| Annunci nel catalogo | 2 | 0 |
| Stato `open` + `verification.state=verified` in catalogo | 1 | 0 |
| `unverified` nel catalogo | 1 | 0 |

La voce BE già verificata nel catalogo è **Veepee — HR & Office Manager internship**, ID `638f5719bdad59dfc7be`, fonte `lever-veepee`, applicazione `https://jobs.lever.co/veepee/39428d15-e52f-496f-9da5-f1df5e3d16d5/apply`, `last_verified_at=2026-11-13T07:25:18.159877+00:00`, motivazione `linked-same-vacancy-applicant-form`. È una **osservazione nel catalogo**, non una verifica live indipendente in questa ricerca. Il secondo annuncio BE (JDE) è `unverified`. Non attribuire nessuno dei due al futuro pilota Wikidata.

## Tre quesiti: evidenze e stato

| Domanda | Misura necessaria | Risultato del pilota |
| --- | --- | --- |
| Copertura | 25 QID BE + 25 QID IE, normalizzazione domini, deduplica QID/alias/identità/ownership con `data/companies.json`, `data/sources.json`, `data/catalog.json` | **Non misurata**, 0/50 entità Wikidata lette |
| Conversione | aziende nuove con sito e careers/ATS ufficiale consentito; inventario HR; vacancy-specific application con policy v2 e freschezza | **Non misurata**; 0 nuove vacancy *attribuibili al pilota*, non un tasso 0% misurato |
| Scalabilità | tempi, byte, HTTP, 429/5xx, elaborazione + storage, frequenza, costi economici effettivi | **Non misurata**; nessun break-even numerico difendibile |

## Protocollo del prossimo test (solo dopo il gate)

1. Verificare direttamente robots.txt da **entrambi** gli host, documentando User-Agent usato, data e percorsi; ottenere se necessario un chiarimento specifico dalla Wikimedia Foundation sulla separazione tra crawling e uso API. Non usare proxy/UI o rotazione UA per aggirare restrizioni.
2. Con un runtime HTTPS/DNS funzionante e un canale ufficiale consentito, fare al massimo **una query selettiva per paese** con `LIMIT 25`, timeout breve, 1 richiesta concorrente, User-Agent informativo con URL di progetto, compressione, controllo 429/Retry-After e logging di richieste/tempo/byte. Salvare QID, paese P17, classe, etichetta, sito P856 e provenienza. Non confondere una sede legale o una società madre con la sede dello stage.
3. Deduplicare prima contro entrambi i registri di datori e sorgenti per QID (se presente), dominio canonicalizzato, alias e parent/subsidiary, senza fondere aziende distinte solo per marchio.
4. Solo per nuovi candidati distinti con dominio attendibile, verificare manualmente *le regole d'accesso* delle careers/ATS, poi solo letture limitate consentite dell'inventario e della specifica candidatura. Conservare `unverified` se l'identità, la vacancy o il form non risultano sufficienti.
5. Riportare per BE e IE: candidati letti, validi, unici e nuovi, ATS consentiti, stage HR specifici, **nuovi** `open/verified` policy v2, richieste e costo marginale. Un pilota a zero stage verificati resta un risultato legittimo.

## Valutazione economica, non decisione di rollout

Confrontare sullo **stesso numero di aziende utili nuove** e sul medesimo orizzonte annuale:

`C_query_annuo = N_esecuzioni * (HTTP + tempo compute + QA + manutenzione)`

`C_dump_annuo = download completo iniziale + storage/estrazione + elaborazione + incrementali + manutenzione`

Un dump JSON settimanale e i dump incrementali giornalieri sono documentati in https://www.wikidata.org/wiki/Wikidata:Database_download, ma gli incrementali non sostituiscono la base iniziale né garantiscono risultati in ogni paese. Preferire le query ristrette finché costo, licenza, accesso e rendimento non giustificano un'infrastruttura dati europea condivisa. Nessun pareggio economico quantificato con i dati attuali.

## Modifiche e rischi residui
- Questo documento è un **preflight documentale**; nessuna raccolta Wikidata completata, nessun nuovo datore aggiunto, nessuna candidatura nuova, nessuna modifica a collector/allowlist/schedule/catalogo/produzione.
- Gate aperti: robots WDQS direttamente verificato, posizione esplicita per API compatibile con policy del progetto, rete funzionante, query effettive, 50 candidati deduplicati, verifica ufficiale degli stage, costi osservati.
- Nessun merge o rollout implicito nella PR documentale.
