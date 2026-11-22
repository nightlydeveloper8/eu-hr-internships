# Decisioni di attivazione e strategia ATS — 22 novembre 2026

## Perimetro e base

Revisione documentale e dei dati già misurati, non una nuova raccolta con BudgetClient. Base disponibile sul `main` dopo #110: 907 ID di catalogo, 407 stage correnti e 37 candidature dirette secondo l'ultimo audit documentato (fotografia del 21/11, da riconfermare su un nuovo catalogo). **Nessuno stage aggiunto da questa revisione, zero fonti abilitate, zero ID rimossi**. Le consultazioni delle pagine pubbliche tramite browser di ricerca non hanno telemetria GET/byte/tempo comparabile; non sono conteggiate come zero traffico totale.

Confermata #110: tre fonti `enabled=false` e `collection_activation_hold=true` sia sulla fonte sia sul datore. Staging precedente: CH/BE/GB +1 candidatura v2 ciascuna, 12 GET, 4.830.640 byte e 7,391 secondi-fonte, finalizzazione temporanea 907→910 ID con zero persi. Misura del 21/11, non nuova verifica live o produzione. Rapporto: [sette-fonti-ats-2026-11-21](sette-fonti-ats-2026-11-21.md).

## Gate per le tre fonti di #110

| Fonte | Decisione ora | Evidenza e limite |
|---|---|---|
| Climeworks (CH, Recruitee XML) | **HOLD: non abilitare** | [Termini Climeworks §1.1 e §3.6–3.7](https://climeworks.com/website-terms-use) includono siti collegati e vietano monitoraggio/copia automatica; non è dimostrato che la pagina Recruitee sia fuori ambito. Il feed pubblico e robots permissivo non eliminano questo conflitto. |
| Peripass (BE, Recruitee XML) | **HOLD: review incompleta** | Il [feed XML Recruitee](https://docs.recruitee.com/docs/feed) è documentato e l'offerta HR resta elencata su [carriere Peripass](https://peripass.recruitee.com/vacancies). Da individuare i termini applicabili alla pagina di recruiting e all'uso da parte di terzi, non confondere le condizioni di altri prodotti Peripass con quelle careers. |
| Fanatics Collectibles (GB, Greenhouse) | **HOLD: review recruiting specifica** | L'[annuncio 4510457009](https://job-boards.greenhouse.io/fanaticscollectibles/jobs/4510457009) mostra modulo e requisiti per studenti; il [Job Board API Greenhouse](https://docs.greenhouse.io/job-board) documenta GET pubblici. I [termini generali Fanatics](https://www.fanaticsinc.com/fanatics-holding-terms) vietano l'estrazione automatica dalle proprie Properties, **ma § iniziale esclude esplicitamente recruiting e candidature dal loro campo**: non attribuire automaticamente quel divieto al board Greenhouse; chiarire i termini del recruiting e i diritti di riutilizzo, perché documentazione API ≠ licenza generale. |

Il [contratto Tellent/Recruitee](https://recruitee.com/terms) è prevalentemente per abbonati. Nota specifica: [documentazione ufficiale di autenticazione](https://docs.recruitee.com/reference/authentication-1) dichiara token Careers Site API obbligatorio entro il **10 febbraio 2027** per `/offers`, `/offers/:id`, `/offers/:offer_slug/candidates`; **XML offer feed e jobs widget sono espressamente esclusi**. Il progetto usa XML, non deve iniziare a usare API private o con token. Anche il [MSA Greenhouse](https://www.greenhouse.com/master-subscription-agreement) disciplina i clienti, non costituisce automaticamente permesso per un aggregatore terzo.

**Gate di rollout separato per fonte:** (a) termini del datore e provider compatibili e perimetro documentato; (b) robots live per ogni host e percorso, consentito; (c) prova entro 48 ore di inventario, titolo, ID, ruolo HR per studenti e modulo ufficiale same-ID accessibile senza login; (d) prova staging con budget e conservazione ID; (e) autorizzazione esplicita del maintainer alla specifica attivazione; (f) soltanto allora rimuovere entrambi gli hold e impostare `enabled=true` in PR dedicata. Dopo merge autorizzato, controllare primo ciclo automatico, variazione netta di candidature distinte e costi. Nessuna di queste attivazioni è stata eseguita.

## Workable Grecia: blocco esatto

Il lettore pubblico `collector/workable_public.py` integrato da #110 è solo inventario; non costituisce prova di candidatura. Su [iKnowHow HR Intern 7EAEC1444E](https://apply.workable.com/ikh/j/7EAEC1444E) e [HR Intern (Talent Acquisition) 3F368EAC02](https://apply.workable.com/ikh/j/3F368EAC02) i titoli e le pagine pubbliche sono rintracciabili, ma la risposta HTML disponibile non contiene un modulo candidato dimostrabile; `HTTP 200` non è sufficiente. Due **lead**, zero nuove candidature verificate. Il report #110 ha misurato per l'inventario 21 posizioni / 4 GET / almeno 86.620 byte / 1,794 s; controllo separato delle due pagine/apply 5 GET / 29.926 byte / 2,650 s. Queste sono misure pregresse.

Un prossimo pilota, solo se condizioni/robots e budget lo permettono, può provare il **DOM reso nel browser** sulla URL ufficiale, verificando stesso shortcode, input del candidato, submit abilitato, destinazione consentita e assenza di login/CAPTCHA, senza compilare né inviare. Se manca la prova, restano lead. Non sbloccare i tre piloti del rendering generico e non usare API Workable con chiave. Riferimenti: [opzioni careers Workable](https://help.workable.com/hc/en-us/articles/115012944968-Comparing-careers-page-options), [termini Workable](https://www.workable.com/terms). Non è stata eseguita una prova Playwright nuova in questa attività.

## Portafoglio ATS da valutare in lotti, non da abilitare in blocco

| Priorità | Paesi e lavoro già presente | Beneficio misurato (solo staging) | Decisione |
|---|---|---|---|
| 1 | **PL/DK/SE**, [PR #102](https://github.com/nightlydeveloper8/eu-hr-internships/pull/102): SmartWays (Recruitee), JKS (Talentech), JobTech→Jobandtalent | PL 1, DK 4 moduli; SE 1 conversione di ID esistente (non nuovo ID). | Non duplicare: riallineare base/confitti, prove fresche, autorizzazioni per ciascuna fonte. |
| 2 | **CH/BE/GB**, #110 integrata | 3 moduli provati il 21/11; licenze/termini ancora gated, come sopra | Non attivare in gruppo automaticamente. |
| 3 | **GR**, Workable iKnowHow | 2 lead distinti; **0 moduli v2** provati | Pilota rendering conservativo dopo gate termini/robots. |
| 4 | **IE/CZ/PL** ancora scoperte, [PR #94](https://github.com/nightlydeveloper8/eu-hr-internships/pull/94): coda offline dei tenant ufficiali e indizi del catalogo | 0 candidature dimostrate dalla PR | Verificare prima proprietario, host ufficiale, robots, condizioni e modulo same-ID su **un campione piccolo per ATS**. Escludere SmartRecruiters e Ashby non autorizzati. |
| 5 | **NL**, [PR #113](https://github.com/nightlydeveloper8/eu-hr-internships/pull/113) | 3 moduli Recruitee in staging, non produzione | Lotto utile ma non riduce i paesi UE a zero: seconda priorità rispetto a PL/DK/IE/CZ/GR. |

Il [rapporto di inventario ATS](inventario-ats-2026-11-21.md) ha censito 68 coppie datore/tenant, di cui 20 non attive: non equivalgono a 20 candidature. La sua nuova scansione ha prodotto **zero candidature distinte**. Non usare la sola presenza del nome dell'ATS o un URL come prova di ownership, interesse HR o modulo. Per ogni nuova famiglia procedere `discovery → 2 tenant pilota (datori distinti) → GET ufficiale → same-ID form → staging → test e gate → proposta di rollout` evitando raccolte manuali esaustive e duplicati con `auto-*` già attivi.

## Costi, modifiche e prossimo passo

- In questa revisione documentale: **0 nuove richieste BudgetClient e 0 byte/secondi misurati dal collector** (consultazioni web non strumentate); **0 stage/candidature addizionali, 0 fonti abilitate, 0 ID rimossi, 0 file bot/catalogo modificati**.
- Solo `docs/` sulla branch di revisione; nessuna attivazione, deploy o merge. I controlli CI della PR documentale non equivalgono a test della raccolta live.
- Prossimo passo concreto: non abilitare Climeworks prima di risolvere il conflitto dei termini; completare gate Peripass/Fanatics, poi richiedere via libera **specifico** per la prima fonte idonea. In parallelo risolvere conflitti e ripetere prova fresca di #102 (priorità paesi-zero); Workable rimane un pilota tecnico e non deve bloccare i lotti con prove v2 già disponibili.
