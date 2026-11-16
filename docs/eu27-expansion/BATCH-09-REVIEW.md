# Lotto 09 — Cechia, Romania, Irlanda, Lussemburgo

**Checkpoint: 16 novembre 2026.** Quattro paesi, **otto canali ufficiali** sottoposti a un pilot GET-only con `BudgetClient`; un secondo micro-pilota ha confermato sul sito PANDOO un percorso di candidatura *via email* conforme al controllo strutturale. **Zero nuove vacancy aggiunte al catalogo, zero fonti enabled in produzione, zero nuovi stage policy v2 verified**, perché nessuna nuova sorgente è stata registrata e PANDOO non esplicita la sede lavorativa della specifica vacancy (il footer indica soltanto la sede societaria). Questa distinzione è obbligatoria per non confondere **canale candidatura verificato** e **opportunità geografica verificata**.

La baseline resta il catalogo 16 novembre 16:51:25 UTC, **362 record, 28 stage HR verified in cinque paesi e 1 working student DE**. Non è una nuova misurazione di produzione. La PR #51 ha integrato la diagnosi Personio in `main` nel commit `bbfe4e8`: i bottoni submit inizialmente disabilitati rimangono incomplete e non consumano rendering inutili, senza rilassare la policy v2.

## Evidenze del lotto — inventario, candidatura, blocchi

| Paese | Canale e annuncio ufficiale | Risultato reale del client | Decisione |
| --- | --- | --- | --- |
| **CZ** | [SAP iXp Intern – Recruiting Associate](https://jobs.sap.com/en/jobs/744000161307409/sap-ixp-intern-recruiting-associate-tech-td-limited-full-time/), Praga, ID **REF3475V**; presente nell'[inventario corporate](https://jobs.sap.com/en/jobs/?location=Prague). Lingue **inglese + tedesco** obbligatorie. | 3 richieste; lista e scheda HTTP 200, H1 coerente, **nessun modulo candidato in HTML**. | **Unverified**; non dichiarare English-only. |
| **CZ** | [Amazon Operations Human Resources Partner Intern 2027](https://www.amazon.jobs/en/jobs/10561439/operations-human-resources-partner-intern-6-months-2027), Kojetín, ID **10561439**, presente nella [ricerca aziendale](https://www.amazon.jobs/en/search?base_query=human+resources+intern). Lingue **ceco e inglese C1** richieste. | 3 richieste, 200. CTA osservata `https://www.amazon.jobs/applicant/jobs/10561439/apply`, ma modulo anonimo non letto e il portale può richiedere autenticazione. | **Unverified**; niente login. Manifesto CZ precedente ha prodotto HTTP 429: non interrogato nuovamente. |
| **RO** | [BAT — HR Intern](https://careers.bat.com/en/job/bucharest/hr-intern/1045/46198641856), Bucarest, presente nel [listing BAT](https://careers.bat.com/en/search_jobs/bucharest/1045/1/1). | 4 richieste, pagina/CTA/landing 200; annuncio ufficiale rimanda a `careers.bat.com/apply?req=81347&locale=en_GB` e l'landing mostra **“Hi there”**, non un form anonimo same-ID utilizzabile. | **Unverified**, requisiti includono inglese e conoscenza normativa romena. |
| **RO** | [Marquardt — HR Internship, French & English speakers](https://www.marquardt.com/careers/job-search/detail/hr-internship-french-english-speakers-f-m), Sibiu; CTA sul tenant `marquardt-ro.mingle.ro/en/apply/sUQZQQ`. | 4 richieste, due pagine 200 ma shell senza H1/form utilizzabili nella lettura statica. | **Unverified**, richiede francese e inglese; non bypassare un modulo dinamico. |
| **IE** | [TikTok HR Operations Lifecycle Intern 2027](https://lifeattiktok.com/search/7694622895491205429), Dublino, ID **7694622895491205429**; datore già presente nella coda precedente. | 4 richieste, vacancy e redirect alla pagina same-ID `lifeattiktok.com/resume/7694622895491205429/apply` entrambi 200, **nessun form HTML leggibile**. | **Unverified**, nessun nuovo datore. Fidelity IE 2136467 continua a restituire 404 nel lettore web; non riprovata nel pilot. |
| **LU** | [PANDOO Administration — HR Intern (F/M/D)](https://pandoo.lu/hr-intern-f/m/d), stage di almeno 6 mesi; [lista ufficiale jobs](https://pandoo.lu/jobs) contiene il ruolo. Inglese obbligatorio, francese e tedesco preferenziali. | 3 richieste GET, due pagine 200; link `mailto:hr@pandoo.lu` etichettato **Apply now**. Un controllo successivo con il verificatore v2 della nuova regola inglese conferma `official-vacancy-email-instructions`, `delivery_verified=false`, e riusa il documento già letto. | **Canale diretto verificato**, ma **vacancy non promoted**: la scheda non esplicita il luogo dello stage, soltanto l'indirizzo della società nel footer. Nessuna email inviata. |
| **LU** | [EY — HR Mobility Intern](https://careers.ey.com/ey/job/Luxembourg-HR-Mobility-Intern-L-1855/1444849033/), ID **1749932**, pubblicato 4 novembre; lingua inglese **o** francese. | 2 richieste e annuncio 200; SuccessFactors CTA, ma **nessun form candidato specifico leggibile** nel GET. | **Unverified**, evitare login e API non approvate. |
| **LU** | [Deloitte — Learning & Development Intern](https://jobs.deloitte.lu/job/Learning-%26-Development-Intern/13618-en_GB), ID **13618**, avvio 8 ottobre, ruolo L&D nel dipartimento HR. | 2 richieste, annuncio 200, nessun modulo candidato attivo in HTML statico. | **Unverified**, categoria L&D confermata, candidatura non provata. |

L'attività per il lotto 09 è una **review mirata**, non un censimento nazionale completo. Nel materiale consultato non si sono trovate prove sufficienti per un inventario nazionale esaustivo in nessuno dei quattro paesi.

## Prova specifica sul canale email PANDOO

La funzione `application_check='official-email'` esisteva già per istruzioni dirette olandesi. Ho aggiunto **una variante riutilizzabile per l'inglese**, senza allentare il vincolo:

1. Il ruolo deve avere **titolo esatto sul sito del datore e link canonico nella pagina careers corrente**.
2. Nel testo dello stesso annuncio deve essere presente un invito affermativo esplicito, come **“please send us your application”**.
3. Sulla stessa pagina deve comparire un **`mailto:` con indirizzo già registrato** ed etichetta **“Apply now”** o “Send application”; contatti generici, richieste di informazioni, email diverse o frasi negative sono rifiutati.
4. La prova ammette soltanto il **canale email**: `delivery_verified=false` e nessuna domanda viene inviata. La verifica del ruolo, data, titolo, geografia e stato resta indipendente.

Il codice riusa il documento corrente già passato alla verifica: **elimina una seconda lettura HTTP identica** per le sorgenti official-email, senza saltare robots, titolo, identità, chiusura o freschezza. Regressioni offline per email errata, contatto generico, link non Apply e vacancy già assegnata.

Tre prove PANDOO una tantum sono state eseguite su ramo isolato: il primo script includeva per errore un link `mailto:` nella funzione di canonicalizzazione HTTP, il secondo contava tre link grafici allo stesso stage come tre offerte e il terzo ha **deduplicato correttamente per URL canonico**, ottenendo esito positivo per il solo canale email. Tutte le prove, inclusi errori, hash e costi, nel [JSON machine-readable](batch-09-live-preflight-2026-11-16.json). Nessuno script di prova è stato integrato in produzione e **tutti i workflow one-shot sono stati rimossi dai rami pilota**.

## Misura reale dei costi

| Prova | Richieste | Byte | Secondi-fonte | Risultato |
| --- | ---: | ---: | ---: | --- |
| [Preflight 8 canali #43926439506](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43926439506) | 25 | 2.410.101 | 22,233 | 4 paesi, 8 fonti, 0 nuove vacancy verified |
| [PANDOO controllo iniziale #43928876091](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43928876091) | 3 | 45.842 | 5,201 | Script fallito sul filtro `mailto` |
| [PANDOO link grafici #43929207076](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43929207076) | 3 | 45.842 | 3,786 | Test logico respinto per triplo link alla medesima offerta |
| [PANDOO deduplicato #43929440391](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43929440391) | 3 | 45.842 | 3,739 | **Canale di candidatura email verificato**; nessuna geografia inventata |
| **Costo totale effettivo** | **34** | **2.547.627** | **34,959** | **0 nuovi stage verified in produzione, 0 fonti abilitate** |

La durata è cumulata per fonte, non il tempo totale di calendario. Nessun rendering, autenticazione, CAPTCHA, POST o invio candidature. Costo monetario non misurato. Incremento di richieste della raccolta quotidiana **0** perché non è stata attivata alcuna nuova fonte.

## Persona/Personio — miglioramento separato già integrato

La [PR #51](https://github.com/nightlydeveloper8/eu-hr-internships/pull/51) sul ramo separato è stata integrata con squash `bbfe4e8`, **435 test Python e 26 Node** verdi. La correzione è limitata ai domini Personio: distingue moduli con nome/email/CV e submit inizialmente disabilitato da shell JS senza form, evita un rendering che non può dimostrare l'abilitazione, e **mantiene stato incomplete** (non verified). Gli altri ATS mantengono i loro fallback. **Nessun rilassamento della policy v2** e nessun aumento pubblicato di stage.

## Prossimo punto incompleto

- **PANDOO LU:** documentare sul sito ufficiale la **sede lavorativa specifica** (non solo l'indirizzo sociale) e, se confermata, preparare un bundle azienda+fonte `employer-index` con `application_check='official-email'`, inizialmente **disabled**, verificando identità, classificazione HR, fase di intake e deduplica. L'eventuale attivazione richiede approvazione specifica; non scrivere manualmente record nel catalogo.
- **CZ/RO/IE:** selezionare nuovi tenant ufficiali con form anonimi leggibili, evitando il già bloccato Manifesto, il Fidelity 404, e pagine Login/JS-only che non superano policy v2.
- **Persone Personio:** misurare nel primo ciclo ordinario il numero di rendering evitati. Il contatore è un beneficio economico potenziale, non nuovi stage. Non ampliare rollout per simulare guadagni.
- **UE27:** lotto 10 (NL, BE, FR, ES, PT) copre i paesi già con stage verificati, ma nessun paese è completamente mappato. Lo scopo è aumentare le candidature distinte *verificate*, non il solo numero di datori nel registro.

Questa PR contiene la logica inglese per email ufficiale e i report; **nessuna fonte in produzione, nessuna autorizzazione host allargata**.
