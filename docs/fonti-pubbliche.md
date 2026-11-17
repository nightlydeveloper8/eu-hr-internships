# Fonti pubbliche nazionali e paneuropee – revisione dell'accesso (Fase 1)

Revisione eseguita il **17 novembre 2026**. Per ogni fonte sono stati verificati termini d'uso, licenza dei dati e `robots.txt` prima di qualsiasi integrazione. Una fonte viene integrata solo se **tutte e tre** le condizioni sono soddisfatte; in caso di dubbio non viene integrata e si prepara una richiesta scritta (bozze in [richieste-accesso.md](richieste-accesso.md)).

Le fonti dei servizi pubblici per l'impiego sono un'eccezione documentata alla regola "nessun aggregatore" di [architecture.md](architecture.md): sono registri ufficiali con licenza esplicita di riuso, non bacheche commerciali.

## Esito

| Paese | Fonte | Termini / licenza | robots.txt | Decisione |
|---|---|---|---|---|
| SE | JobTech JobSearch (Arbetsförmedlingen, Platsbanken) | Open data, annunci in **CC0**; nessuna chiave richiesta; [pagina ufficiale open data](https://arbetsformedlingen.se/other-languages/english-engelska/about-the-website/apis-and-open-data) | assente (404) | **Integrata** (`public-se-jobtech`) |
| DE | Jobsuche, Bundesagentur für Arbeit | [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) §2a c.3: vietati robot/webspider e l'uso non autorizzato di interfacce di programmazione per estrarre contenuti. L'API non è offerta ufficialmente a terzi: la chiave `jobboerse-jobsuche` è quella del sito, documentata da un progetto comunitario (bund.dev) | `rest.arbeitsagentur.de` non verificabile (403) | **Esclusa**; richiesta di autorizzazione |
| FR | API Offres d'emploi v2, France Travail | Le [CGU di francetravail.fr](https://www.francetravail.fr/informations/informations-legales-et-conditio/conditions-generales-dutilisatio.html) prevedono la messa a disposizione via API ai partner che aderiscono alla licenza di riuso; account gratuito su francetravail.io (client id/secret) | **`api.francetravail.io/robots.txt`: `User-Agent: *` / `Disallow: /`** | **Esclusa per ora**: stessa regola già applicata a SmartRecruiters (API documentata ma robots.txt che esclude i bot generici). Richiesta di chiarimento. Nota: gli stage (convention de stage) non sono contratti di lavoro e sono rari su France Travail |
| UE | EURES (ELA) | L'[avviso legale](https://eures.europa.eu/eures-legal-notice_en) consente il riuso dei contenuti ELA citando la fonte, "salvo diversa indicazione". Le offerte sono però contenuti dei servizi nazionali (es. France Travail, BA) con licenze proprie; l'API di ricerca del portale non è documentata | nessuna clausola sull'accesso automatico | **Esclusa** (termini non chiari per le offerte); bozza di richiesta a ELA |
| CH | Job-Room / arbeit.swiss (SECO) | Le [note legali](https://www.arbeit.swiss/secoalv/de/home/service/rechtliche-hinweise.html) riservano i diritti sulle offerte; riproduzione e integrazione in altri siti richiedono consenso scritto preventivo. Il link semplice è consentito | consentito | **Esclusa**; richiesta di consenso |
| GB | Find a job (DWP) | L'endpoint `findajob.dwp.gov.uk/search` è censito su [api.gov.uk](https://www.api.gov.uk/dwp/find-a-job/) per l'integrazione da parte di altre amministrazioni; nessuna licenza o condizione per terzi; il servizio sta migrando al nuovo Jobs and Careers Service | 503 al momento della verifica | **Esclusa** |
| GB | Reed Jobseeker API | API documentata, chiave gratuita. Bacheca commerciale con molti annunci di agenzie; nessuna condizione d'uso specifica pubblicata nella pagina sviluppatori | – | **Decisione del titolare**: va contro la regola "nessun aggregatore" |
| GB | DfE Find an apprenticeship – Display advert API | Documentata, registrazione gratuita | – | **Fuori ambito**: apprendistati (contratti di lavoro per residenti nel Regno Unito), non stage |
| LV | NVA "Vakances" (data.gov.lv) | **CC0**, CSV giornaliero | consentito | Consentita, **non integrata**: solo settore pubblico, solo titoli; 0 stage HR su 1.260 annunci (17/11/2026) |
| CZ | MPSV volná místa (data.mpsv.cz) | Open data per legge (NV 425/2016) | consentito | Consentita, **non integrata**: 0 stage HR su 39.552 annunci, 3 titoli di stage in tutto; il file contiene contatti personali |
| FI | Työmarkkinatori (KEHA) | I [termini](https://tyomarkkinatori.fi/en/info/kehittajille/tyopaikkailmoitusten-rajapinnat/tyomarkkinatorin-tyopaikkailmoitusten-rajapintojen-kayttoehdot) consentono di mostrare gli annunci nel proprio servizio | – | **Blocco tecnico**: l'attivazione richiede una whitelist di indirizzi IP, incompatibile con i runner GitHub |
| BE | VDAB Vacature API | Richiede un accordo di cooperazione firmato | – | Esclusa (serve l'accordo) |
| EE, LT | Töötukassa, Užimtumo tarnyba | Nessuna API documentata per terzi | – | Escluse |

Fonti mai considerate, per vincolo del progetto: LinkedIn, Indeed e qualsiasi accesso che richieda login, aggiramento di CAPTCHA o di limiti.

## Integrazione svedese (`jobtech-search`)

- **Raccolta**: query per pertinenza (`+praktik +HR`, `+praktikant`, `+internship`, `+trainee +HR`…; fino a 400 risultati per query). Le query servono solo a trovare candidati: ogni annuncio deve comunque superare la classificazione esistente (titolo con segnale di stage + titolo HR) e avere un luogo di lavoro in Svezia. Gli annunci all'estero vengono scartati, perché la nazione arriva come etichetta svedese e non viene indovinata.
- **Chiusura**: l'assenza da una query non chiude mai un annuncio (`closure_complete: false`). Un annuncio noto che non compare viene ricontrollato con `/ad/{id}`: viene chiuso solo se l'API lo segnala rimosso o risponde 404, oppure se la scadenza pubblicata è passata.
- **Link**: `url` e `apply_url` puntano alla pagina ufficiale Platsbanken. Il link di candidatura dell'azienda, se pubblicato, serve solo alla deduplica (`external_application_url`).
- **Dati personali**: nomi dei contatti, email e numeri di telefono non vengono copiati. Il testo viene ripulito prima della classificazione e non entra mai nell'export pubblico.
- **Deduplica**: una copia del servizio pubblico viene unita all'annuncio dell'azienda già presente solo se c'è **una sola** corrispondenza, per link di candidatura oppure per datore di lavoro + titolo + paese normalizzati. Nei casi ambigui gli annunci restano separati. La fonte pubblica compare in `duplicate_source_ids` e `public_listing_urls`.
- **Verifica**: per ora gli annunci restano "da verificare" (`link_status: public-api-listed`). La regola che considera verificata la presenza in un'API ufficiale di soli annunci attivi è materia della Fase 5 e va documentata a parte.
- **Segreti**: nessuno.

Misura dal vivo del 17/11/2026: 889 annunci letti, 4 stage HR in Svezia (Höganäs, Malmö, Stoccolma, Tranås), 0 doppioni con il catalogo esistente.

## Segreti di GitHub Actions

Nessun segreto è necessario per le fonti integrate. Se France Travail confermerà che i client con licenza sono esclusi dal `robots.txt`, serviranno `FRANCE_TRAVAIL_CLIENT_ID` e `FRANCE_TRAVAIL_CLIENT_SECRET` (applicazione registrata su francetravail.io con la sottoscrizione "API Offres d'emploi v2"). Non vanno mai inseriti nel repository.

## Metrica

`scripts/country_metric.py` produce a ogni esecuzione delle Actions la tabella per paese (29 righe): sintesi del job e artefatti `country-metric-before.json` e `country-metric-after.json`. Non scrive nulla nel repository.
