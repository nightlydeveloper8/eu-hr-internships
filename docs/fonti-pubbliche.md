# Fonti pubbliche nazionali e paneuropee – revisione dell'accesso (Fase 1)

Revisione eseguita il **17 novembre 2026**. Per ogni fonte sono stati verificati termini d'uso, licenza dei dati e `robots.txt` prima di qualsiasi integrazione. Una fonte viene integrata solo se **tutte e tre** le condizioni sono soddisfatte. Il titolare del progetto ha scelto di non inviare richieste di autorizzazione: le fonti escluse restano escluse finché i loro termini non cambiano.

Le fonti dei servizi pubblici per l'impiego sono un'eccezione documentata alla regola "nessun aggregatore" di [architecture.md](architecture.md): sono registri ufficiali con licenza esplicita di riuso, non bacheche commerciali.

## Esito

| Paese | Fonte | Termini / licenza | robots.txt | Decisione |
|---|---|---|---|---|
| SE | JobTech JobSearch (Arbetsförmedlingen, Platsbanken) | Open data, annunci in **CC0**; nessuna chiave richiesta; [pagina ufficiale open data](https://arbetsformedlingen.se/other-languages/english-engelska/about-the-website/apis-and-open-data) | assente (404) | **Integrata** (`public-se-jobtech`) |
| DE | Jobsuche, Bundesagentur für Arbeit | [Nutzungsbedingungen](https://www.arbeitsagentur.de/nutzungsbedingungen) §2a c.3: vietati robot/webspider e l'uso non autorizzato di interfacce di programmazione per estrarre contenuti. L'API non è offerta ufficialmente a terzi: la chiave `jobboerse-jobsuche` è quella del sito, documentata da un progetto comunitario (bund.dev) | `rest.arbeitsagentur.de` non verificabile (403) | **Esclusa** (i suoi annunci arrivano comunque tramite EURES) |
| FR | API Offres d'emploi v2, France Travail | Le [CGU di francetravail.fr](https://www.francetravail.fr/informations/informations-legales-et-conditio/conditions-generales-dutilisatio.html) prevedono la messa a disposizione via API ai partner che aderiscono alla licenza di riuso; account gratuito su francetravail.io (client id/secret) | **`api.francetravail.io/robots.txt`: `User-Agent: *` / `Disallow: /`** | **Esclusa**: stessa regola già applicata a SmartRecruiters (API documentata ma robots.txt che esclude i bot generici). Le offerte francesi trasmesse a EURES arrivano da lì. Nota: gli stage (convention de stage) non sono contratti di lavoro e sono rari su France Travail |
| UE + CH | EURES (ELA) | L'[avviso legale](https://eures.europa.eu/eures-legal-notice_en) autorizza il riuso dei contenuti del sito citando l'ELA come fonte, "salvo diversa indicazione"; nessuna clausola vieta l'accesso automatico. La ricerca usata è quella pubblica del portale (`/eures/api/jv-searchengine/public/jv-search/search`), non documentata ma senza login | `europa.eu/robots.txt` non esclude `/eures/api`; **Crawl-delay: 10** rispettato | **Integrata** per decisione del titolare (17/11/2026), con attribuzione all'ELA (`public-eu-eures`) |
| CH | Job-Room / arbeit.swiss (SECO) | Le [note legali](https://www.arbeit.swiss/secoalv/de/home/service/rechtliche-hinweise.html) riservano i diritti sulle offerte; riproduzione e integrazione in altri siti richiedono consenso scritto preventivo. Il link semplice è consentito | consentito | **Esclusa**; gli annunci svizzeri trasmessi a EURES arrivano da lì (attivi con la Fase 4) |
| GB | Find a job (DWP) | L'endpoint `findajob.dwp.gov.uk/search` è censito su [api.gov.uk](https://www.api.gov.uk/dwp/find-a-job/) per l'integrazione da parte di altre amministrazioni; nessuna licenza o condizione per terzi; il servizio sta migrando al nuovo Jobs and Careers Service | 503 al momento della verifica | **Esclusa** |
| GB | Reed Jobseeker API | API documentata, chiave gratuita. Bacheca commerciale con molti annunci di agenzie; nessuna condizione d'uso specifica pubblicata nella pagina sviluppatori | – | **Decisione del titolare**: va contro la regola "nessun aggregatore" |
| GB | DfE Find an apprenticeship – Display advert API | Documentata, registrazione gratuita | – | **Fuori ambito**: apprendistati (contratti di lavoro per residenti nel Regno Unito), non stage |
| LV | NVA "Vakances" (data.gov.lv) | **CC0**, CSV giornaliero | consentito | Consentita, **non integrata**: solo settore pubblico, solo titoli; 0 stage HR su 1.260 annunci (17/11/2026) |
| CZ | MPSV volná místa (data.mpsv.cz) | Open data per legge (NV 425/2016) | consentito | Consentita, **non integrata**: 0 stage HR su 39.552 annunci, 3 titoli di stage in tutto; il file contiene contatti personali |
| FI | Työmarkkinatori (KEHA) | I [termini](https://tyomarkkinatori.fi/en/info/kehittajille/tyopaikkailmoitusten-rajapinnat/tyomarkkinatorin-tyopaikkailmoitusten-rajapintojen-kayttoehdot) consentono di mostrare gli annunci nel proprio servizio | – | **Blocco tecnico**: l'attivazione richiede una whitelist di indirizzi IP, incompatibile con i runner GitHub |
| BE | VDAB Vacature API | Richiede un accordo di cooperazione firmato | – | Esclusa (serve l'accordo) |
| EE, LT | Töötukassa, Užimtumo tarnyba | Nessuna API documentata per terzi | – | Escluse |

Fonti mai considerate, per vincolo del progetto: LinkedIn, Indeed e qualsiasi accesso che richieda login, aggiramento di CAPTCHA o di limiti.

## EURES (`eures-search`)

- **Raccolta**:
  1. Tutte le offerte che i servizi nazionali hanno codificato come *internship* (~870).
  2. 164 ricerche a coppie (termine di stage + termine HR) generate da `data/hr-vocabulary.json` in 22 lingue, a partire dalle lingue con più annunci. Ogni coppia va avanti di pagina, fino a 3 pagine, solo se la pagina precedente ha portato nuovi stage HR.
  3. Se resta tempo, le 22 ricerche combinate per lingua.

  Le pagine sono da 50 risultati, con la pausa di 10 secondi imposta dal robots.txt: circa 35-40 minuti al giorno, su un budget di 45. A budget esaurito la fonte si ferma e conserva quanto raccolto (stato "parziale").

  **Validazione dal vivo del 18/11/2026**: la ricerca combinata trovava 82 stage HR in italiano e 91 in tedesco; le coppie ne trovano 96 e 108. La combinata ne perdeva il 17-18%, mentre ne aggiungeva solo 2-3 che alle coppie sfuggivano: per questo si eseguono entrambe, coppie prima.
- **Classificazione**: la stessa usata per le altre fonti. Se il servizio nazionale ha codificato l'offerta come *internship*, quel codice vale come segnale di stage, ma il titolo deve comunque essere HR.
- **Paesi**: quelli indicati da EURES (`EL` → GR). Il luogo è il nome NUTS da `data/geography.json`. Gli annunci in Svizzera vengono raccolti ma restano fuori dal catalogo fino alla Fase 4; Norvegia, Islanda e Liechtenstein sono fuori ambito.
- **Chiusura**: l'assenza dai risultati non chiude mai un annuncio. Fino a 40 annunci noti per esecuzione vengono ricontrollati singolarmente; un 404 li chiude.
- **Dati personali**: i contatti (nomi, email, telefoni) della scheda di dettaglio non vengono mai letti nel record, e il testo viene ripulito. Se il servizio nazionale non trasmette il nome del datore di lavoro (es. UWV), si mostra "Employer not disclosed (see EURES advertisement)".
- **Datore di lavoro negli annunci ripresi dal web** (UWV): se manca il campo datore ma la pagina riportata inizia con "<Nome> logo" e il nome si ripete nel testo, si usa quel nome; i nomi di bacheche (Indeed, LinkedIn, werk.nl…) sono esclusi.
- **Lingua dell'annuncio**: l'etichetta di lingua di EURES è quella predefinita del servizio nazionale (UWV etichetta come olandesi anche gli annunci in inglese). Se il testo è chiaramente in un'altra lingua, vale la lettura del testo (marcata come stima).
- **Annunci ripubblicati**: lo stesso annuncio a volte compare con un nuovo id (ripubblicazione o seconda versione linguistica). Se titolo, luogo, datore e i primi 300 caratteri del testo dopo il titolo coincidono, si tiene solo la copia più recente (`republished_duplicates_folded` nel report della fonte).
- **Deduplica**: una copia EURES cede il posto all'annuncio dell'azienda e poi a quello di un servizio nazionale (es. JobTech), sempre solo se la corrispondenza è unica.
- **Attribuzione**: la fonte mostrata è "EURES – European Job Mobility Portal (European Labour Authority)". I link portano alla scheda del portale EURES.
- **Rischio residuo**: l'interfaccia non è documentata e può cambiare senza preavviso. In quel caso la fonte risulta "failed" nella copertura, ma gli annunci già raccolti restano. Se l'ELA chiede di smettere, basta disattivare la fonte.

Scansione di prova del 17/11/2026: 2.924 annunci esaminati, 362 stage HR (NL 150, DE 102, IT 31, FR 29, CH 20, BE 15, AT 4, SE 4, ES 3, FI 3, LU 1).

## Integrazione svedese (`jobtech-search`)

- **Raccolta**: query per pertinenza generate dal dizionario svedese (`+praktik +hr`, `+praktikant +rekrytering`…) più alcune inglesi; fino a 400 risultati per query. Verifica dal vivo del 18/11: stessi 5 stage HR delle query scritte a mano. Le query servono solo a trovare candidati: ogni annuncio deve comunque superare la classificazione esistente (titolo con segnale di stage + titolo HR) e avere un luogo di lavoro in Svezia. Gli annunci all'estero vengono scartati, perché la nazione arriva come etichetta svedese e non viene indovinata.
- **Chiusura**: l'assenza da una query non chiude mai un annuncio (`closure_complete: false`). Un annuncio noto che non compare viene ricontrollato con `/ad/{id}`: viene chiuso solo se l'API lo segnala rimosso o risponde 404, oppure se la scadenza pubblicata è passata.
- **Link**: `url` e `apply_url` puntano alla pagina ufficiale Platsbanken. Il link di candidatura dell'azienda, se pubblicato, serve solo alla deduplica (`external_application_url`).
- **Dati personali**: nomi dei contatti, email e numeri di telefono non vengono copiati. Il testo viene ripulito prima della classificazione e non entra mai nell'export pubblico.
- **Deduplica**: una copia del servizio pubblico viene unita all'annuncio dell'azienda già presente solo se c'è **una sola** corrispondenza, per link di candidatura oppure per datore di lavoro + titolo + paese normalizzati. Nei casi ambigui gli annunci restano separati. La fonte pubblica compare in `duplicate_source_ids` e `public_listing_urls`.
- **Verifica**: regola per le API pubbliche (sezione seguente).
- **Segreti**: nessuno.

Misura dal vivo del 17/11/2026: 889 annunci letti, 4 stage HR in Svezia (Höganäs, Malmö, Stoccolma, Tranås), 0 doppioni con il catalogo esistente.

## Regola di verifica per le API pubbliche (Fase 5)

Le fonti aziendali restano verificate solo con la prova del modulo di candidatura (policy v2, invariata). Per le API ufficiali dei servizi pubblici per l'impiego vale una regola distinta: **se l'API elenca soltanto annunci attualmente pubblicati, l'essere restituito da quell'API è la prova che l'annuncio è attivo.**

Un annuncio viene considerato verificato (`status: open`, `link_status: public-api-active-listing`, `verification.policy: public-api-active-listing`) solo se valgono **tutte** queste condizioni:

1. La fonte è stata esaminata e dichiarata `active_listing_api: true` nel registro, con il motivo scritto in `active_listing_evidence`. Oggi lo sono JobTech (la ricerca restituisce solo gli annunci pubblicati in Platsbanken; quelli rimossi risultano `removed`) ed EURES (la ricerca del portale restituisce solo le offerte in pubblicazione; quelle ritirate danno 404).
2. L'annuncio è stato restituito dall'API **in questa esecuzione**: la prova non si eredita da una raccolta precedente.
3. La scadenza pubblicata, se c'è, non è passata.
4. Se non c'è una scadenza, la data di pubblicazione deve essere valida e risalire a **non più di 180 giorni** prima. Gli annunci senza data e senza scadenza restano da verificare.
5. La data di pubblicazione non è nel futuro.

Le regole comuni a tutte le fonti continuano a valere:
- una verifica più vecchia di 48 ore riporta l'annuncio a "da verificare". Un annuncio che non compare più nelle ricerche perde quindi la verifica entro due giorni, anche se non viene chiuso;
- una scadenza passata o un 404 esplicito chiudono l'annuncio.

Nell'interfaccia il messaggio è diverso da quello delle fonti aziendali: indica che l'annuncio risulta aperto presso il servizio pubblico e che la pagina di candidatura dell'azienda non è stata controllata.

**Deduplica**: se la copia pubblica è verificata e l'annuncio aziendale corrispondente (unico) non lo è, resta visibile la copia pubblica. L'annuncio aziendale finisce in `duplicate_source_ids` / `related_listing_urls`. Un annuncio aziendale verificato non viene mai sostituito. Questo non abbassa la soglia per le fonti aziendali: la loro verifica resta quella del modulo.

## Segreti di GitHub Actions

Nessun segreto è necessario per le fonti integrate.

## Metrica

`scripts/country_metric.py` produce a ogni esecuzione delle Actions la tabella per paese (29 righe): sintesi del job e artefatti `country-metric-before.json` e `country-metric-after.json`. Non scrive nulla nel repository.
