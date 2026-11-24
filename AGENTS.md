# AGENTS.md — istruzioni per agenti AI che lavorano su People Placement

Questo file vale per qualsiasi assistente che modifica il repository (Codex/ChatGPT, Claude, altri).
Se una richiesta del maintainer contraddice questo file, vale la richiesta del maintainer.

## 1. Il progetto in breve

People Placement (https://people-placement-eu.pages.dev/) è un sito statico, senza registrazione, che mostra
**stage HR per studenti universitari** nei 27 paesi UE, in Svizzera e nel Regno Unito.
- `collector/` (Python, solo libreria standard + Playwright per alcune pagine) raccoglie gli annunci da fonti pubbliche.
- GitHub Actions esegue la raccolta ogni giorno e il bot pubblica `data/catalog.json` su `main`.
- Cloudflare Pages ricostruisce il sito (`python3 scripts/build.py` → `dist/`) a **ogni push su `main`**.
- L'interfaccia (`src/`) è JavaScript nativo senza dipendenze.

## 2. Prima di iniziare qualsiasi lavoro

1. Leggi `docs/stato-progetto.md`: è il diario operativo con le voci più recenti in alto, le decisioni e il prossimo passo.
   Per approfondire: `README.md`, `docs/architecture.md`, `docs/fonti-pubbliche.md`.
2. Controlla le PR aperte e le branch recenti. Molte PR sono piloti ancora in revisione: riusa il loro lavoro invece di duplicarlo e non riscrivere file che un'altra PR aperta sta cambiando senza dirlo.
3. Parti da `main` aggiornato e lavora su una **branch dedicata**. Prefissi in uso: `fix/`, `design/`, `pilot/`, `review/`, `research/`, `analysis/`, `prep/`, `verify/`, `integration/`, `docs/`.

## 3. Autorizzazioni: cosa NON fare senza un via libera esplicito del maintainer

- **Niente merge, squash merge, rebase o push su `main`.** Un push su `main` è un deploy in produzione (Cloudflare Pages).
  Inoltre, un push che tocca `collector/**`, `data/sources.json`, `data/companies.json`, `data/*-geography.json`,
  `data/*-opportunities.json`, `scripts/company_coverage.py`, `requirements-collector.txt` o `.github/workflows/collect.yml`
  **avvia subito la raccolta di produzione** (`collect.yml`).
- **Massimo 5 PR aperte create da agenti**, incluse bozze e PR con base su un altro ramo. Prima di aprirne una, controlla le PR aperte del repository e conta quelle create da agenti, anche se pubblicate tramite l'account del maintainer. Usa la provenienza del lavoro e la descrizione della PR, oltre all'autore GitHub. Se il limite è raggiunto, oppure non puoi stabilire che ci sia posto, fermati e segnala il conteggio o l'incertezza. Indica nella descrizione che la PR è stata creata da un agente.
- **Niente nuovi piloti di ricerca di fonti o paesi** finché il maintainer non li riapre esplicitamente. Sono ammessi correzioni, monitoraggio e lavoro sull'interfaccia per gli studenti.
- **Niente attivazione di fonti in produzione.** Le nuove fonti restano `"enabled": false` (o con l'hold, vedi §4) finché il maintainer non approva il rollout.
- **Niente chiusura di PR o issue**, niente modifica di impostazioni del repository, secrets, variabili Actions o Cloudflare.
- Una richiesta di lavoro ("fai X") **non** è un'autorizzazione al merge. Alla fine apri una PR pronta per la revisione e fermati.

## 4. Fonti e raccolta dati

- **Solo fonti pubbliche accessibili direttamente**: ATS pubblici, sitemap e pagine careers dei datori, servizi pubblici per l'impiego già rivisti (EURES `public-eu-eures`, JobTech `public-se-jobtech`).
  Controlla robots.txt e termini d'uso prima di integrare una fonte e documenta la verifica (`permission_basis`, `review_notes`, `reviewed_on` in `data/sources.json`).
- **Accesso automatizzato a piattaforme e tenant.** Un canale è ammesso soltanto se valgono tutte le condizioni seguenti.
  1. Scaricare con successo `robots.txt` e controllare che il percorso usato sia consentito. Se robots non è leggibile, fermarsi. Su un primo 429 a robots, ritentare lentamente e rispettare `Retry-After` e il crawl delay.
  2. Il dato è pubblico e raggiungibile senza login, chiave, CAPTCHA o elusione di blocchi.
  3. Il formato è quello già usato dalla pagina pubblica (JSON), una sitemap o markup JSON-LD schema.org `JobPosting`.
  4. I termini applicabili non vietano esplicitamente l’accesso automatizzato. Il silenzio non è un divieto.
  5. Usare un ritmo basso, rispettare il crawl delay e identificare onestamente People Placement nello user agent.
  6. Interrompere e registrare subito l’accesso in caso di 403/429 ripetuti o di richiesta del datore.
  Classificare come **incerto** solo se almeno una condizione non è verificabile. Esempio ammesso: sitemap Workday di Damen dichiarata nel robots dello stesso host e consentita il 23 novembre 2026, con termini del percorso rivisti. Esempio escluso: Welcome to the Jungle, che vieta espressamente lo scraping nelle condizioni d’uso.
- **Vietato**: chiedere autorizzazioni ad autorità o enti (BA, ELA, SECO, France Travail, DWP…), usare API a pagamento o con chiave,
  aggirare login, captcha, robots o blocchi, fingersi un crawler autorizzato, inviare candidature.
  Restano disabilitate SmartRecruiters (robots lo vieta) e Ashby (robots 401) finché l'accesso non è chiarito.
- **Provisioning automatico — attenzione.** `python -m collector.daily provision` collega un crawler `universal-employer` **attivo**
  a ogni datore di `data/companies.json` che non ha una fonte attiva. Quindi aggiungere un datore equivale ad attivarlo al primo merge.
  Per preparare un datore senza attivarlo usa `"collection_activation_hold": true` sul datore e la fonte rivista `"enabled": false`
  (vedi `tests/test_ampelmann_disabled_provision.py`). L'attivazione richiede di togliere l'hold **e** abilitare la fonte in una modifica autorizzata.
- **Non modificare a mano i file pubblicati dal bot**: `data/catalog.json`, `data/coverage.json`, `data/company-coverage.json`,
  `data/employer-collection.json`, `data/*-coverage.json`, `docs/evaluation-report.json`, `docs/country-research-progress.json`,
  `docs/company-integration-queue.json`. Cambiano solo tramite la raccolta. Una rimozione deliberata di record va fatta in un commit rivisto e dichiarato.
- **Nessun ID esistente deve andare perso.** Gli ID sono hash stabili di fonte e posting; i record che riappaiono si riaprono.
  La chiusura richiede tre snapshot completi mancanti in almeno 48 ore; una fonte fallita o incompleta non conta come assenza.
- Rispetta crawl delay e budget di richieste. Nei piloti misura sempre richieste GET, byte e tempo.
- Le prove live vanno in staging (`.staging/`, ignorata da git) o in run `workflow_dispatch`, mai pubblicando su `main`.

## 5. Regole di dominio (non negoziabili)

- **Solo stage/placement per studenti con un ruolo HR.** Esclusi: Werkstudent/working student/lavori part-time per studenti;
  traineeship e graduate programme per neolaureati (un titolo "trainee" vale solo se il posting documenta un placement per studenti);
  ruoli ordinari, anche se la descrizione cita gli stagisti.
- **Idoneità studentesca in Italia.** Includere tirocini curriculari, stage per studenti iscritti e stage con convenzione universitaria (`student_eligibility: confirmed`). Includere stage HR e tirocini HR senza indicazione curriculare o extracurriculare né esclusione esplicita (`student_eligibility: not_stated`), con l’etichetta «Student eligibility not stated – check with the employer». Escludere tirocini extracurriculari, annunci riservati a neolaureati, disoccupati o percettori di sostegni e programmi graduate. Campo e livello di prova sono indipendenti.
- **Idoneità studentesca per le agenzie europee.** ES include prácticas curriculares ed extracurriculares per iscritti e offerte becario/a, ed esclude il contratto en prácticas per laureati. FR include stage con convention de stage ed esclude alternance e apprentissage. NL include stage, meewerkstage e afstudeerstage ed esclude werkstudent, bijbaan e traineeship. DE include Pflichtpraktikum e freiwilliges Praktikum ed esclude Werkstudent, Trainee e Ausbildung. PL include praktyki studenckie e staż per studenti ed esclude lo staż dell’urząd pracy riservato ai disoccupati. Uno stage HR generico senza esclusione esplicita mantiene l’etichetta «Student eligibility not stated – check with the employer». L’idoneità non modifica il livello di prova.
- **Livelli di prova** (definiti in `src/logic.js` e `collector/verification.py`, `POLICY_VERSION = 2`). Non confonderli mai:
  1. *Direct application verified* (`applicationConfirmed`): vacancy attuale **e** percorso di candidatura ufficiale per quella vacancy confermati entro **48 ore** (policy v2).
  2. *Public employment service* (`publicEmploymentListing`): attivo su EURES/JobTech entro 48 ore; il modulo del datore **non** è verificato.
  3. *Current listing*: verificato ma senza prova del percorso di candidatura.
  4. *Lead*: non verificato ora. Non è un'offerta confermata e nemmeno chiusa confermata.
  Un URL raggiungibile da solo **non** verifica nulla. Non promuovere mai un record a un livello superiore senza la prova richiesta.
- **Zero annunci ≠ zero stage.** Non presentare mai l'assenza nella raccolta come assenza nel mercato.
- **Lingue.** Lingua dell'annuncio e lingua di lavoro sono campi distinti. Un annuncio in inglese non prova che basti l'inglese.
  I requisiti linguistici servono da un estratto esplicito. Il portale deve rendere visibile quanti annunci sono in inglese e quanti nella lingua del paese.
- **Nessuna inferenza** su visti, permessi di lavoro, cittadinanza, retribuzione o idoneità. Paesi e città sconosciuti o ambigui restano sconosciuti.
- Il vocabolario HR multilingue è in `data/hr-vocabulary.json`. Ogni modifica a regole di classificazione richiede esempi etichettati
  positivi **e** negativi (`data/evaluation.json`, `data/language-evaluation.json`) e `scripts/evaluate.py` con zero errori.
- Niente dati di contatto personali nell'export pubblico; le descrizioni complete restano solo in cache tecnica (max 48 ore).

## 6. Interfaccia (`src/`)

- L'interfaccia pubblica è **in inglese**. Design "premium dark" (PR #100): mappa SVG dell'Europa protagonista, `src/style.css` è il design system condiviso anche da `employers.html` e dalle pagine provinciali.
- Preserva: geometrie e codici paese (`src/eu-map.js` è generato da `scripts/generate_eu_map.mjs`), ID degli elementi usati da `app.js`,
  parametri URL dei filtri (`shareableFilterParams`: `unverified` non va mai persistito), preferiti in `localStorage` `people-placement:saved`, accessibilità da tastiera.
- Nessuna dipendenza npm, font esterni, analytics, tracking, cookie o servizi a pagamento. La CSP in `scripts/build.py` consente solo risorse `self` (immagini anche `data:`).
- Requisiti: contrasto WCAG AA, `prefers-reduced-motion`, target touch adeguati, nessun overflow orizzontale a 375 px, niente informazioni disponibili solo con l'hover.
- Verifica le modifiche visive sulla build `dist/` a 375, 768 e 1440 px, con screenshot prima/dopo quando possibile.

## 7. Comandi

Python 3.9+ (la CI usa 3.12) e Node 22+. Non servono pacchetti per test e build. Playwright (`requirements-collector.txt`) serve solo alla raccolta.

```sh
# Gli stessi controlli della CI (.github/workflows/check.yml): devono passare tutti prima di aprire una PR
python3 -m unittest discover -s tests -v
node --test tests/*.test.js
python3 scripts/evaluate.py            # classificazione: zero errori
python3 scripts/company_coverage.py
python3 scripts/build.py               # valida i dati e genera dist/

# Il job test di collect.yml esegue anche:
python3 -m collector.daily provision   # deve essere idempotente: su main non deve cambiare file

# Anteprima locale
python3 -m http.server 5173 --directory dist

# Raccolta mirata e validazione (diagnosi locale; non pubblicare il catalogo risultante)
python3 -m collector.pipeline --sources <source-id> [<source-id> ...]
python3 -m collector.pipeline --validate
python3 scripts/country_metric.py      # tabella dei 29 paesi
```

**Attenzione:** `scripts/company_coverage.py` (e la raccolta) riscrive file pubblicati dal bot, per esempio `data/company-coverage.json`
e `data/*-coverage.json`. Dopo i controlli esegui `git status`: se non volevi cambiarli, ripristinali con `git checkout -- data/` e non includerli nella PR.

`--no-verify` è solo diagnostico: non usarlo per aggiornamenti normali.
Per run multi-shard manuali usa lo stesso `--run-id` (o `COLLECTOR_RUN_ID`) per tutti i `collect` e il `merge`.

## 8. Mappa del repository

| Percorso | Contenuto |
| --- | --- |
| `collector/` | Raccolta: `pipeline.py`, `daily.py` (shard, provisioning, merge), `adapters.py`, `classify.py`, `verification.py`, `applications.py`, `public_sources.py`, `universal.py`, `dynamic_ats.py`, adapter specifici |
| `data/sources.json` | Registro di circa 2.000 fonti (adapter, `enabled`, `status`, `allowed_hosts`, prove di accesso) |
| `data/companies.json` | Registro dei datori (provisioning automatico, `collection_activation_hold`) |
| `data/catalog.json` | Catalogo pubblico (scritto dal bot) |
| `data/hr-vocabulary.json`, `data/evaluation.json` | Vocabolario HR multilingue e set di regressione |
| `src/` | Sito: `index.html`, `app.js`, `logic.js` (regole condivise con i monitor di Actions), `map.js`, `eu-map.js`, `style.css`, pagine registro e province |
| `scripts/` | Build, valutazione, audit, metriche per paese, strumenti di integrazione |
| `tests/` | Test Python (`unittest`) e Node (`frontend.test.js`, `monitor-alert.test.js`) |
| `docs/stato-progetto.md` | Diario operativo consolidato al merge |
| `.github/workflows/` | `check.yml` (test su push/PR), `collect.yml` (raccolta quotidiana 06:17 UTC + push su main), `stale.yml` (monitor freschezza) |

## 9. Come consegnare il lavoro

1. Esegui tutti i comandi della sezione 7. Se un test fallisce già su `main`, documentalo; non correggerlo di nascosto.
2. Scrivi la voce in `docs/diario/<nome-branch>.md` usando il nome completo del ramo, per esempio `docs/diario/fix/esempio.md`. Usa al massimo 8 righe fisiche, inclusi titolo e righe vuote. Inizia con `## <data> — <titolo>` e registra in italiano risultato, verifiche, limiti e prossimo passo. Scrivi i link relativi come se la voce fosse già in `docs/stato-progetto.md`. La PR lascia `docs/stato-progetto.md` intatto.
   - Solo nel checkout di integrazione, dopo aver applicato la PR e prima di creare il commit che la integra, esegui `python3 scripts/consolida_diario.py <nome-branch>`. Includi nello stesso commit il diario aggiornato e la rimozione del frammento. Il pulsante di merge GitHub da solo salta questo passaggio.
   - Per una PR esistente che modifica ancora il diario, trasferisci la voce nel frammento e mantieni la versione corrente del diario durante la risoluzione dei conflitti. Per un accorpamento, conserva evidenze e riferimenti nella voce del ramo che sarà integrato.
3. Commit con messaggi in inglese, chiari e piccoli. Titolo e descrizione della PR in italiano.
4. La descrizione della PR deve contenere:
   - obiettivo e perimetro (cosa è stato toccato e cosa no);
   - **numeri misurati prima/dopo**: stage attuali verificati, candidature dirette verificate, lead, per paese quando rilevante; ID persi (deve essere zero);
   - costo dei piloti: richieste GET, byte, tempo; link ai run di Actions o agli artifact;
   - test eseguiti e risultato;
   - rischi, limiti e cosa **non** è stato verificato;
   - l'azione richiesta al maintainer (es. "autorizzare il merge", "autorizzare l'attivazione delle fonti X").
5. Non dichiarare risultati non misurati e non presentare stime come fatti. Se un obiettivo non è raggiungibile, spiega perché e indica la prossima leva migliore.
6. Fermati dopo aver aperto la PR.

## 10. Lingue

- Interfaccia pubblica, codice, commenti e messaggi di commit: **inglese**.
- `docs/stato-progetto.md`, descrizioni delle PR e resoconti al maintainer: **italiano**.
