# People Placement — primo benchmark dei portali stage HR (17 novembre 2026)

## Decisione e limite
**Risultato:** in un campione mirato di **7 annunci HR NL da Magnet.me**, **5 datori/annunci non risultano nel catalogo main** cercando datore e titolo, **2 hanno corrispondenze già non verificate** (Philips, JDE Peet's). **Sei** dispongono di una pagina ufficiale specifica leggibile nella ricognizione web odierna; per **JDE** il collegamento ufficiale proviene dal catalogo preesistente ma non è stato nuovamente letto. **Una** (Ampelmann) mostra nel contenuto HTML pubblico i campi del form di candidatura. **Zero nuove candidature policy v2**: non sono stati eseguiti preflight BudgetClient/robots/host, staging, due cicli o publish per questo benchmark.

**Riferimento verificato:** `data/catalog.json` main, `updated_at=2026-11-17T08:07:40.055449+00:00`, blob `40f655ca915de1f921ec688b4e7f98ade46cbbc0`: **363 ID**, **28 stage HR open/verified**, **1 working student open/verified**, **307 unverified**, **27 closed**. Gli stage verificati sono in **NL 18, BE 3, FR 5, ES 1, PT 1**. Nessuna delle sette piste modifica questo numero.

Il file strutturato [benchmark-hr-portals-2026-11-17.json](benchmark-hr-portals-2026-11-17.json) conserva identificativi e link. Campione intenzionale, solo un portale e solo NL: **non** stimare quota di mercato UE27, duplicazioni globali, freschezza o tasso di conversione reale dei concorrenti da questi 7 casi.

## Portali osservati e limiti del confronto

| Portale | Segnale utile | Limite prima di usare il portale come fonte |
|---|---|---|
| [Magnet.me — HR NL](https://magnet.me/en/internships/netherlands/human-resources) | Pagine specifiche, datore e luogo; 7 piste tracciate in questo lotto | Annuncio su aggregatore ≠ candidatura ancora aperta; non automatizzare il prelievo senza controllo di termini e robots |
| [iAgora — HR Europa](https://www.iagora.com/work/en/internships/hr/europe) | Ricerca HR per area europea e filtri linguistici | Conteggi riportati dal sito non sono opportunità uniche/candidabili, alcuni datori non nominati |
| [Stageplaza — HR/HRM](https://stageplaza.nl/stage/hr-hrm/) | Catalogo specializzato negli stage olandesi | Le quantità in pagina non misurano la disponibilità su sito aziendale |
| [JobTeaser](https://www.jobteaser.com/en/) | Annunci HR europei con requisiti accademici, spesso dati azienda | Accesso e modalità candidatura variano; confrontare sempre la pagina ufficiale |
| [Welcome to the Jungle](https://www.welcometothejungle.com/en/jobs) | Pagine di internship/People Operations di aziende europee | Possibile pagina editoriale o ATS terzo, nessun automatico `verified` |

Non effettuati scraping, esportazioni o importazione del contenuto dei concorrenti nel catalogo. Il benchmark consiste in letture web limitate di annunci individuati e pagine **ufficiali**. Prima di costruire discovery automatica da aggregatori verificare condizioni d'uso, robots.txt, provenienza e licenze; preferire inventari dei datori e feed pubblici esplicitamente autorizzati.

## Campione verificato sulle pagine aziendali, ma non secondo policy v2

| Priorità | Datore / vacancy / ID | Riscontro ufficiale | Stato nel catalogo / motivo residuo |
|---|---|---|---|
| **1** | [Ampelmann — Internship People & Organisation](https://careers.ampelmann.nl/o/internship-people-organisation-1), Delft | Scheda HR, sede, scadenza 24/11/2026, form visibile (nome, email, CV, domande); **inglese richiesto, olandese plus** | **Non trovata**; migliore candidata a un preflight ufficiale controllato e a un adapter riutilizzabile, senza promozione anticipata |
| **2** | [Henkel — HRBP Intern](https://www.henkel.com/careers/find-your-job-apply/2273404-2273404), Amsterdam/Utrecht, job ID 26101817 | Pagina ufficiale e link al sistema Henkel Cornerstone; **inglese richiesto, olandese preferito** | **Non trovata**; manca attestazione modulo sullo stesso ID, non usare email di contatto per candidarsi |
| **3** | [Stryker — Human Resources Intern](https://careers.stryker.com/human-resources-intern/job/CA0F9085968EB37DDF81736932C396BF), Amsterdam, R576472 | Annuncio aziendale con link `Apply Now` a [Workday stesso ID](https://stryker.wd1.myworkdayjobs.com/StrykerCareers/job/Amsterdam-Netherlands/Human-Resources-Intern_R576472-1) | **Non trovata**; Workday aperto dal lettore ma non mostra modulo leggibile, niente `verified` |
| **4** | [ASML — Early career Events / Talent Engagement](https://www.asml.com/en/careers/find-your-job/hr--business-administration-internship-early-career-events-programs-and-talent-engagement-j00355639), Veldhoven, J-00355639 | Annuncio ufficiale, internship non-thesis da febbraio 2027, **inglese eccellente** | **Non trovata**; candidatura non attestata con prova specifica |
| **5** | [Hunkemöller — HR Global Projects & Recruitment](https://jobs.hunkemoller.com/en/vacancies/internship-hr-global-projects-and-recruitment-hilversum-jr78931), Hilversum, JR78931 | Scheda aziendale con CTA `Apply`; **olandese fluente obbligatorio** | **Non trovata**; modulo non attestato, priorità minore per studenti solo anglofoni |
| **6** | [Philips — Internship HR](https://www.careers.philips.com/global/en/job/594564/Intern-Manufacturing-People-Partnering), Drachten, 594564 | Vacancy ufficiale, inizio febbraio 2027, **olandese + inglese** | **Già nel catalogo, ID `903efc58fb2fabb24b59`**; `unverified`: nessuna application entry specifica stabilita |
| **7** | [JDE Peet's — Internship Talent Acquisition](https://careers-nl.jdepeets.com/job-posting-detail?id=744000158015131&return_url=%2Fjob-search%2F), NL | URL aziendale già registrata, **non accessibile al lettore web in questa sessione**; il concorrente mostra un titolo affine | **Possibile sovrapposizione**, ID `8b5138f67090ed0cd3b4` unverified (form non stabilito); esiste anche mirror storico `ba254a8016887ae59fee` quarantinato per ownership. **Non** contare due offerte né dichiarare la stessa ID senza nuova verifica |

Fonte di scoperta per i 7 lead: [Magnet.me](https://magnet.me/en/internships/netherlands/human-resources); URL individuali nella coda JSON. Osservazione puntuale il **17/11/2026**; le risposte del lettore web **non** sostituiscono controlli GET/robots, inventario completo, same-vacancy, identità del datore, host autorizzati, durata e candidatura aperta in collector.

## Misura, classificazione e beneficio reale

- **7 lead**, **6 pagine ufficiali specifiche lette oggi** e **1 URL ufficiale storico nel catalogo non riletto (JDE)**, **5 non presenti per datore+titolo nella baseline**, **2 già presenti come `unverified` / possibili match**, **1 form pubblico visibile**, **0 stage policy v2 promossi**.
- Costo di **questa modifica al progetto**: **0 GET BudgetClient, 0 rendering, 0 byte collector, 0 POST**, nessun nuovo monitoraggio quotidiano, nessuna candidatura. Sono state usate ricerche/aperture web esterne al collector; il loro costo monetario non è misurato. Non attribuire risparmi o rendimento di produzione a questo report.
- **Beneficio effettivo:** backlog riproducibile di gap nel catalogo, con URL ufficiali, ID, classificazione linguistica e ordine di adattamento. La copertura **non è aumentata** su `main`.
- **Non** usare portali terzi come `source_type=universal-employer` o come proprietà del datore: rischio già osservato sul mirror storico JDE/Tilburg. Separare sempre discovery dalla lettura ATS ufficiale, con dedup per identità della vacancy.

## Lavoro successivo orientato al risultato

1. **Ampelmann:** controllare termini/robots dell'host e ATS, source ownership, inventario, form sullo stesso ID in un unico preflight BudgetClient *bounded*; poi due cicli di staging con contatori richieste/byte/tempo e zero POST. Se passa, proporre fonte **disabled** in PR dedicata, senza attivazione in produzione. Non è ancora un `verified`.
2. **Henkel e Stryker:** preferire la soluzione riutilizzabile per Cornerstone/Workday e controllo della pagina candidatura specifica, non eccezioni per URL individuali. Non aggiungere nuovi host alla allowlist senza review; rispettare auth/CAPTCHA/429 e budget.
3. **ASML e Hunkemöller:** distinguere pagina HR da candidatura completa, dare precedenza a requisiti linguistici che ammettono inglese; nessun abbassamento di policy v2.
4. **Philips/JDE:** aprire diagnosi della causa strutturale di application entry già nota, senza duplicare record e senza riaprire il mirror di terzi.
5. Per misurare il valore comparato, costruire **campioni replicabili in più paesi e più portali** solo se accesso consentito; il vero KPI è `nuovi stage HR distinti e verificati / HTTP, byte, secondi e manutenzione`, non il numero dichiarato dai portali.

**Confini:** documentazione e dati di benchmark su branch separato, nessuna fonte, catalogo o workflow modificati; nessun merge/rollout, scheduler o produzione. Riesaminare il materiale insieme alle PR #56 (feed nazionali) e alla Issue #18 (miglioramento resa), evitando lavoro ATS duplicato.
