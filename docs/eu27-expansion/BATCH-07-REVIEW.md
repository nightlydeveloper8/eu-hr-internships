# Lotto 07 — Cipro, Grecia, Croazia e Malta

**Data:** 16 novembre 2026. **Risultato:** 8 indizi esaminati, 3 schede HR su siti ufficiali da verificare, **0 nuovi stage policy v2 verified**, **0 fonti attivate**. Le tre schede non equivalgono ancora a tre candidature verificabili. Evidenza completa nel [JSON del lotto](batch-07-review-2026-11-16.json).

**Baseline:** ultima raccolta documentata del 16 novembre 16:51:25 UTC, 362 annunci, **28 stage verified in cinque paesi + 1 working student DE**. PR #48 integrata su main nel commit bea9c85 e validazione #43915251768 riuscita. Nessun nuovo ciclo o deploy attribuibile a questo lotto.

## Priorità da verificare

| Paese | Offerta e collegamento ufficiale | Gate ancora mancante |
| --- | --- | --- |
| **Cipro** | [Brainstorm Hospitality — HR Intern](https://careers.fridays.com.cy/jobs/7649525-hr-intern) a Larnaca, ID **7649525**. [Inventario datore](https://careers.fridays.com.cy/) coerente, stage retribuito. | La CTA apre un modulo dinamico che nel lettore mostra **Loading application form**; campi visibili e invio abilitato **non dimostrati**. Robots e inventario non letti da BudgetClient. |
| **Grecia** | [iKnowHow S.A. — HR Intern (Talent Acquisition)](https://apply.workable.com/ikh/j/3F368EAC02), Neo Psychiko, ID **3F368EAC02**, inglese richiesto, iscrizione idonea a istituto greco richiesta. [Carriere aziendali](https://www.iknowhow.com/careers/) rimanda esattamente al [tenant Workable](https://apply.workable.com/ikh/); l'[informativa societaria](https://www.iknowhow.com/privacy-policy/) conferma Workable. | Prova ufficiale datore→ATS **confermata**; robots, feed completo, stessi ID/CTA e modulo candidato anonimo non attestati dal collector. |
| **Malta** | [Marriott / Westin Dragonara — Human Resources Intern](https://careers.marriott.com/human-resources-intern-the-westin-dragonara-resort/job/P1-7345932-0), St Julian's, ID **26132701**, presente anche nell'[inventario Westin](https://careers.marriott.com/brands/westin/jobs/page/52). CTA Oracle conserva l'ID nell'URL finale. Indennità lorda €835/mese, almeno 5–6 mesi. | Robots Marriott/Oracle non verificati; [CTA Oracle](https://ejwl.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX/job/26132701/apply/email?posting_type=1) restituisce nessun modulo leggibile nel lettore web. Nessuna autenticazione tentata. |

La priorità di pilot è Brainstorm (singolo job nell'inventario corrente), poi iKnowHow (identità datore→Workable accertata), poi Marriott (correlazione ID accertata, form Oracle sconosciuto). **Non** dichiarare candidabile una posizione soltanto per la CTA o per un HTTP 200.

## Esclusioni e limiti

- **Croazia:** la [vecchia pagina Rimac People Operations Intern](https://careers.rimac-group.com/position/people-operations-intern/) è tuttora pubblica, ma non figura tra le **124 vacancy dell'[inventario Rimac attuale](https://careers.rimac-group.com/)**. Gli altri HR sono ruoli permanenti; la vecchia pagina richiede **inglese e croato**. Non dichiarare l'annuncio aperto né chiuso senza prova di chiusura esplicita, ma non ammetterlo.
- **Croazia:** l'[avviso PLIVA AskHR](https://www.sczg.unizg.hr/poslovi/studentski-posao-u-odjelu-ljudskih-potencijala) scadeva il **9 novembre 2026** ed è un lavoro studentesco, non stage.
- **Malta:** per Xara Collection le pubblicazioni Hosco/LinkedIn indicano HR Intern, ma la [lista aziendale](https://xaracollection.com/xara-collection-vacancies/) contiene **HR Executive** e non lo stage; non confondere i due ruoli. Hilton HR Trainee marzo 2027 è documentato solo da siti terzi, senza identità ATS ufficiale precisa: non ammissibile.
- **Cipro:** il [board Stoiximan](https://apply.workable.com/stoiximan/?not_found=true) menziona HR Intern in materiale promozionale, ma dichiara **zero posizioni aperte in Corporate Functions**; non contarlo come stage live.

## Costi e operazioni

Sono state consultate pagine pubbliche e CTA tramite ricerca web, **senza inviare candidature, effettuare login, bypassare CAPTCHA o aprire zone protette**. I tentativi di lettura robots dai siti ATS col lettore web non hanno restituito dati utilizzabili; una prova HTTPS via runtime ha fallito la risoluzione DNS. Pertanto **robots, inventari completi e moduli anonimi non sono verificati**. Nessun crawler di produzione eseguito su queste fonti.

**Impatto reale:** 0 nuovi stage verificati, 0 nuove fonti abilitate, 0 richieste quotidiane in più, nessun catalogo modificato. Costi misurabili nel collector relativi a nuove fonti: **0 richieste, 0 rendering, 0 byte**; costi della navigazione web non misurati con BudgetClient.

**Budget solo proposto, non misurato:** massimo 12 richieste e 45 secondi-fonte per ciascuno dei tre canali (tetto 36 richieste e 135 secondi cumulati), senza rendering. Non abilita nuovi host o automatismi.

## Prossimo punto incompleto

1. Preflight con BudgetClient e robots sui singoli host di **Brainstorm CY** e **iKnowHow GR**: inventario, job ID e modulo candidato abilitato dello stesso annuncio; fermare gli host non consentiti.
2. Controllo separato **Marriott MT → Oracle** solo se il percorso esatto è consentito e il modulo anonimo leggibile, senza login.
3. **Croazia:** sostituire Rimac non attuale con un nuovo inventario HR student ufficiale realmente aperto. Non promuovere annunci chiusi o lavori studenteschi a stage.
4. Solo dopo le prove policy v2 predisporre bundle atomico/rollout specifico e misurare due cicli. Lotto 08 AT/DE/DK/FI/PL/SE già pianificato, **non schedulato**.

Questa PR cambia **solo documentazione** e il checkpoint globale; non altera registry, collector, catalogo, workflow o policy v2. PR #41 e #46 restano draft non pronti.
