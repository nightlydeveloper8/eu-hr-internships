# People Placement — Ampelmann full staging v2, SmartRecruiters FR e replay costi (17 novembre 2026)

## Risultato confermato

**Ampelmann Delft** ha superato **due cicli completi** del percorso ordinario `process_source() → finalize()` con feed Recruitee XML ufficiale (GET senza autenticazione) e candidatura specifica pubblicata nel feed, sempre via GET. I due cicli sono stati eseguiti **nella stessa sessione del 17 novembre**, non in giorni distinti. Entrambi restituiscono `policy_version=2`, `status=open`, `verification.state=verified`, stesso ID catalogo **`b05fc810ebc3e04dc51b`**, titolo esatto **Internship People & Organisation**, sede **Delft, NL**, identità posting **`2822573`**, metodo `official-recruitee-same-posting-visible-form`, modulo abilitato e stesso ID nel percorso applicativo. **Zero invii, zero POST, zero rendering**. Riferimento [workflow isolato #44147104809](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44147104809), job `ampelmann-staging`, riuscito.

| Misura | Ciclo 1 | Ciclo 2 | Totale |
|---|---:|---:|---:|
| HTTP GET BudgetClient | 5 | 4 | **9** |
| Byte | 943.578 | 943.496 | **1.887.074** |
| Secondi-fonte | 6,926 | 5,915 | **12,841** |
| Stage HR verificati nello staging | 1 | 1, stesso ID | **1 distinto** |
| ID baseline catalogo preservati | sì | sì | **363/363** |

Replay temporaneo: **363 → 364 schede** e **28 → 29 internship HR verified SOLO nello staging**, con `closure_eligible=[]`, **nessuna chiusura per assenza**. La produzione `main` resta **363 / 28** all'ultimo snapshot confrontato `ab51981` (17/11 08:07 UTC). L'unico source di prova `staging-ampelmann-nl` è un oggetto **in memoria disabilitato**: non è stato aggiunto ai registri, non si può attivare con `enabled=true`, e nessun lavoro programmato lo legge. Non equiparare la prova a un incremento nel sito.

## Come funziona senza credenziali

Il sito aziendale `https://careers.ampelmann.nl/` pubblica l'XML `https://careers.ampelmann.nl/api/feeds/offers.xml`, letto dal `BudgetClient` dopo robots e confinamento all'host. Feed HTTP 200, root `offers`, **5** offerte pubblicate. L'offerta `id=2822573` contiene i campi `careers_url` e `apply_url` con valore effettivamente pubblicato **`https://careers.ampelmann.nl/o/internship-people-organisation-1/c/new`**; **non** è stato inventato il suffisso `/c/new`. Questa pagina risponde 200, ha il titolo e l'ID corrispondenti e `applicant_form(...,strict=True)` positivo. Evidenza della scoperta: [run #44146027267](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44146027267), job `public-recruitee-feed`: **3 GET/348.010 B/2,543 s**, nessun POST.

La [documentazione Tellent Recruitee](https://docs.recruitee.com/reference/authentication-1) specifica che il requisito di token per la **Careers Site API** entra in vigore il **10 febbraio 2027**, mentre **XML offer feed e jobs widget non sono coperti dal token**. Nessuna API privata né credenziale è stata usata e non sono state rimosse protezioni. Il nuovo ramo introduce `feed_format=recruitee-public-xml` esclusivamente opt-in per l'adapter `recruitee`, con host approvato, ID e URL apply realmente pubblicati, nessun DTD, nessun URL su host estranei, nessuna inferenza di chiusure; l'adapter JSON preesistente rimane invariato. Piccolo gate del classificatore `People & Organisation`: richiede evidenze testuali HR esplicite, non soltanto il nome del reparto.

**Lavoro mancante prima della produzione:** review dei test/CI, seconda prova su data diversa per freschezza, identità azienda/registrazione fonte **disabilitata** nel medesimo passo di provisioning (evitare crawler universali accidentali), autorizzazione distinta prima di merge, attivazione e primo ciclo ordinario con confronto SHA e Cloudflare. Nessuna attivazione automatica da questo ramo.

## SmartRecruiters: campione francese e causa strutturale

[Action #44145799104](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44145799104), job `ats-readonly`, controlla con `BudgetClient` un annuncio Salomon `744000161490861` e uno Sia `744000159655534` su **`jobs.smartrecruiters.com`**: entrambi **HTTP 200, URL e titolo corrispondenti**, nessun form `strict` nell'HTML statico. Salomon: **2 GET/118.857 B/1,358 s**; Sia: **1 GET/124.688 B/0,870 s** (robots cache del processo). **0 stage recuperati**. Queste pagine ufficiali accessibili non autorizzano l'uso dell'API `api.smartrecruiters.com`, precedentemente vietata da robots. Non è stato tentato l'aggiramento né la presentazione di candidature.

Nel catalogo 17/11: **FR 46 internship (5 verified, 37 unverified, 4 closed)**, tra cui **11** `unverified` su SmartRecruiters; **BE 4 internship (3 verified, 1 unverified su SmartRecruiters)**. Il tratto comune è che una pagina pubblica può confermare titolo ma non dimostrare un **form specifico e abilitato**; non è ancora dimostrato che una sola patch possa recuperare tutti e 12 gli indizi. Possibili duplicati e requisiti di sede/identità da preservare. Prima di investire in nuovo rendering o endpoint verificare presenza di un link ufficiale pubblicato di `Apply` con ID, nel rispetto di robots, stessa host allowlist e spesa; se assente, restare `unverified`. Il precedente [audit SmartRecruiters](smartrecruiters-coverage-audit-2026-11-13.md) resta valido sulla restrizione API.

## Backtest dei costi: 14 giorni di calendario, 12 snapshot

Lo script riproducibile `python -m scripts.audit_cadence_history --start 2026-11-04 --end 2026-11-17` legge **esclusivamente** la cronologia Git dei report `data/coverage.json` e sceglie l'ultimo commit per ciascun giorno UTC. **12 date** disponibili (5–10 e 12–17 novembre), **4 e 11 novembre mancanti**; non sono assenze di stage né giorni `verified-empty`. Per ogni fonte conta soltanto il report con `checked_at` dello stesso giorno.

**Totali osservati in quelle 12 fotografie giornaliere:** 21.494 rapporti-fonte nuovi; **439.871 richieste**, **47.391.604.300 B**, **42.113 rendering**, **542.156,15 secondi-fonte cumulati**. Questi ultimi sono **150,60 ore-fonte**, non tempo reale di esecuzione né ore fatturabili.

**Politica prudente simulata, NON attivata:** dopo **3 osservazioni complete e senza HR match** (`status=ok`, nessun inventario dichiarato incompleto), uno shadow-skip nei giorni pari, senza presumere che fonte partial, bloccata o non raggiunta sia vuota. Replay: **104 source-day skip**, **401 HTTP (0,09%)**, **73.297.337 B**, **4 rendering**, **298,09 secondi-fonte** evitabili teoricamente. **0 nuovi match HR sulle 104 osservazioni simulate come saltate**, ma questo **non dimostra** assenza di opportunità tra due visite e non garantisce zero vacancy perse. Simulazione non equivale a modifica della cadenza reale e con 2 giorni senza snapshot non copre 14 giornate osservate. Evidenza: [Action #44147104809](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44147104809), job `cadence-history`, test e replay success.

Il 16/11 il 94,5% delle richieste era speso da fonti senza HR match; tuttavia quasi tutte erano `partial/discovery-incomplete`, NON `verified-empty`. **Risparmio del semplice rallentamento conservativo trascurabile**; priorità sul costo delle esplorazioni incomplete e rendering delle fonti non produttive, mantenendo protezione delle offerte brevi. Svolgere diagnosi per **pattern tecnico**, non disabilitare 1.832 fonti dopo un solo ciclo.

## Operazioni e confini

- **Effettivamente eseguiti:** più preflight GET bounded, un adapter XML opt-in, test offline (12 test specifici), due staging completi con `finalize` in cartella temporanea, backtest 12 snapshot, report; nessun POST, browser o candidatura.
- **Modifica codice** solo su branch `research/ats-and-cadence-20261117`; **nessun merge**, **nessuna attivazione**, **nessuna produzione verificata**. Il workflow temporaneo di prova deve essere rimosso dopo l'esito, prima di presentare la PR come pulita.
- I numeri di costo sono consumo HTTP e secondi-fonte, **non euro di fatturazione**. Runner standard Github Actions nei repository pubblici normalmente gratuiti, ma nessun dato di billing personale esaminato.

