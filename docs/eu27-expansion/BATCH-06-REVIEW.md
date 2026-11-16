# Lotto 06 — otto paesi UE con copertura HR ancora non dimostrata

**Data:** 16 novembre 2026. **Esito:** 10 indizi su 9 datori in EE, LV, LT, BG, IT, HU, SI e SK, selezionati per verifica; **0 nuove candidature policy v2**, **0 nuovi canali abilitati**, nessuna modifica ai registri o alla raccolta. Il numero degli indizi non è il numero di stage aperti. Evidenze riproducibili nel [JSON del lotto](batch-06-review-2026-11-16.json).

### Baseline aggiornata

Dopo la [raccolta ordinaria #43909444414](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43909444414), riuscita, il catalogo aggiornato alle **16:51:25 UTC** contiene **362 annunci**, di cui **28 stage HR open/verified in cinque paesi e 1 working student DE**; 306 unverified e 27 closed. Questo è l'ultimo catalogo letto, non un incremento attribuibile al lotto. L'ultimo file `country-outcomes-2026-11-16.json` precedente descrive invece 361 annunci alle 16:08 UTC. Il nuovo audit offline `scripts/audit_eu27_coverage.py` deve derivare il quadro direttamente dal catalogo corrente, senza confondere una lista indicizzata con un censimento completo.

### Paesi e decisioni

| Paese | Canale ufficiale, annuncio e verifica | Decisione |
| --- | --- | --- |
| **LV** | [DIGI MEDIA — HR Manager Intern, Riga](https://digimedia.studio/careers/hr-manager-intern/). La [lista aziendale](https://digimedia.studio/careers/) mostra il ruolo; nella pagina dedicata sono presenti campi nome, email, CV, consenso e comando **Send application**. Inglese richiesto. | **Priorità 1**: è il percorso più corto verso una verifica completa, ma il collector non ha ancora letto robots, HTML/submit, stato e inventario entro budget. Non verified. |
| **LT** | [Girteka — Intern in Recruitment and HR Team, Vilnius](https://careers.girteka.eu/job/Vilnius-Intern-in-Recruitment-and-HR-Team/1375077055/), pubblicato il 30 ottobre 2026 sul sito aziendale. Inglese richiesto; russo, portoghese e spagnolo preferenziali. | **Priorità 2**: la CTA conserva il codice 1375077055, ma l'URL `/talentcommunity/apply/...` restituisce nel web un listone/home, non un modulo identico. Non verified. |
| **BG** | [CCEP — People Services Internship 2027, Sofia/Varna](https://www.ccep.jobs/en/job/varna/internship-program-2027-people-services-with-german-anguage-skills/1299/46554924352), job ID 114108, inglese **e tedesco**. | La CTA va a `jobs.ccep.com` con parametro identificativo differente; form anonimo e redirect non attestati. **Pending**, non English-only. |
| **BG** | [Gameloft — HR Intern, Sofia](https://www.gameloft.com/jobs/HR%20Intern%20(long-term%20labor%20contract)-744000083478145). Sito aziendale mostra la scheda, ma la CTA SmartRecruiters va a `/expired`. | **Scartato**: il sito datore mantiene una scheda chiusa. Non chiamare open per HTTP 200. |
| **IT** | [Heritage Holdings — HR Internship, Milan, ID 4945490101](https://job-boards.eu.greenhouse.io/heritageholdings/jobs/4945490101). La lista Greenhouse corrente comprende questo ruolo HR e il modulo della scheda mostra campi candidati e submit. | **Priorità 1**, ma manca ancora prova pubblica dal sito corporate al tenant esatto, oltre a robots/feed e check collector policy v2. |
| **IT** | [Heritage Holdings — HR Recruiter Internship, Milan, ID 4945390101](https://job-boards.eu.greenhouse.io/heritageholdings/jobs/4945390101). Distinto dal precedente per ID, titolo e attività; incluso nel medesimo board attuale. | **Priorità 1**, un solo tenant (non due aziende); stessi requisiti di ownership e verifica. Non duplicare vecchio titolo HR & Talent Acquisition Intern come terza offerta. |
| **EE** | [Bolt — Talent Acquisition Intern, Tallinn](https://bolt.eu/en/careers/positions/?gh_jid=8505592002&page=11), visto in una pagina corporate indicizzata. `bolt.eu/robots.txt` aveva direttiva `Allow: /`; risultati della vacancy esterni segnalano però termine 2 novembre 2026 e candidature non più accettate. | **Scartare la pista corrente** senza modulo nuovo verificato. Il permesso robots di un host non prova la disponibilità di un annuncio. |
| **HU** | [Betsson — HR & Office Intern, Budapest](https://job-boards.greenhouse.io/betsson/jobs/8187971), il cui modulo compare ancora nella scheda indicizzata; nella **lista aziendale Greenhouse corrente** non compare più il ruolo e il sito corporate avverte che non ci sono stage aperti. | **Scartato per inventario attuale contraddittorio**: un form isolato non supera il controllo freschezza. |
| **SI** | Danfoss — HR Intern, Ljubljana: il risultato storico di un terzo riferisce ritiro dal board aziendale il 30 ottobre 2026; manca l'URL ufficiale attuale. | **Scartato**, nessuna fonte derivata dall'aggregatore. |
| **SK** | [Adient — Part-Time Student HR, Bratislava](https://adient.wd3.myworkdayjobs.com/en-US/External/job/Part---Time-Student-HR-department_R-29080). Pagina Workday ufficiale, ma categoria diversa dallo stage e modulo non verificato. | **Coda working student**, non conteggiare come stage HR. |

### Costi e fonti

Questa è una **ricerca web mirata**, non un preflight con `BudgetClient`: nessun cron, host, allowlist, ATS o ID di fonte attivato; richieste del collector **0**, rendering del collector **0**, durata e byte **non misurati**, costo monetario **non misurato**. Non inventare valori a partire dalle richieste della ricerca web. L'accessibilità `robots.txt` per Digi Media, Girteka, CCEP, Heritage e gli ATS di destinazione non è stata verificabile con il tool web; il tentativo HTTPS del runtime non dispone di risoluzione DNS. Non aggirare questi limiti né aprire login/CAPTCHA.

Il beneficio della ricerca è **individuare tre percorsi prioritari riutilizzabili**: una pagina aziendale con form visibile (DIGI MEDIA LV), un board standard con due vacancy distinti (Heritage IT), una scheda employer ATS con URL stabile (Girteka LT). Sono tre canali candidati, non tre canali candidabili già dimostrati. CCEP rimane candidato incompleto; altri quattro indizi sono scartati/separati.

### Prossimo punto incompleto

1. Eseguire un **preflight circoscritto** con il client del repository per Digi Media LV e Heritage IT (un solo tenant, due posti): robots su ogni host esatto, link datore→ATS, inventario completo, titolo/ID e form anonimo dello stesso annuncio; massimo proposto 12 richieste/45 secondi *per fonte*, nessun rendering. Il budget è ipotetico, non misurato.
2. Verificare Girteka LT soltanto se l'URL corrente dell'offerta porta ad una domanda specifica senza autenticazione; in caso di talent community, fermarsi. Non rientrare sui vecchi 429 o URL scaduti.
3. Solo dopo prova v2 e deduplicazione rispetto ai registri preparare **bundle fonte+azienda atomico** e chiedere autorizzazione per specifico rollout. Nessuna promozione manuale del catalogo.
4. Proseguire gli altri 19 paesi con i lotti 07–10 **disgiunti**, dettagliati in [piano UE27](EU27-MAPPING-PLAN.md). Copertura completa è un criterio da dimostrare paese per paese; la semplice presenza di un lead non conclude il censimento.

Il nuovo [audit offline](../../scripts/audit_eu27_coverage.py) produce 27 righe e vieta implicitamente la promozione di paese a `complete` basata su un solo stage. I 27 paesi sono pianificati una volta in questo giro, con priorità e status; i cicli successivi possono approfondirli senza inventare chiusure nazionali.
