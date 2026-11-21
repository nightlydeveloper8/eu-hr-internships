# Sette fonti ATS: verifica circoscritta del 21 novembre 2026

Base di staging: main 99f8dad760bf270b433b6dc3bfe2d26d13facfba, 907 ID. Nessun invio di candidatura, attivazione o modifica manuale del catalogo. Prove GET, robots a runtime, host esatti e budget massimo 20 richieste/90 secondi per fonte. La prova live scade secondo la policy v2.

## Risultati e costi

La pipeline ordinaria è stata eseguita in staging e ripetuta per conservare i record completi e finalizzare in una directory temporanea. I costi sono del secondo singolo ciclo: i GET includono robots; i byte sono i corpi letti dal BudgetClient; i tempi sono per fonte, non costo monetario. Un ciclo preliminare separato ha verificato inventario e modulo.

| Fonte | Posting | Esito pipeline | GET | Byte | Secondi |
| --- | --- | --- | ---: | ---: | ---: |
| Climeworks, CH | 2831389 | 1 stage HR direct verified, studenti iscritti ammessi; anche neolaureati ammessi | 4 | 663200 | 2,147 |
| Peripass, BE | 2262981 | 1 stage HR direct verified; Master universitario in corso | 4 | 872349 | 2,171 |
| Fanatics Collectibles, GB | 4510457009 | 1 stage HR direct verified; undergraduate in corso, benché il campo automatico enrollment sia nullo | 4 | 3295091 | 3,073 |

Climeworks e Peripass: feed XML pubblico, vacancy, identificativo e modulo /c/new pubblicato con stesso posting. Fanatics: API board GET e modulo sulla vacancy con stesso ID. Somma **12 GET / 4.830.640 byte / 7,391 secondi-fonte**, non misura in produzione. Rendimento osservato 3/12; non estrapolare ad altri giorni. I due feed Recruitee restano incompleti ai fini della chiusura per assenza.

Finalizzazione su copia temporanea: **907 → 910 ID, 0 persi**, tre nuovi ID rispettivamente b1aa852290bb922a8053, 8153f1f158eff3ac20c7, 01261fa4346199c79b0c. Catalogo versionato invariato. Le opportunità potrebbero essere già rappresentate con denominazioni differenti nei servizi pubblici; il confronto automatico non dimostra una deduplicazione semantica completa.

## Altre quattro fonti

- **Sungrow (IT), Personio 2888661:** XML con 157 posizioni; 4 GET / 357.668 byte / 2,124 s. Campi visibili ma submit inizialmente disabilitato; verifica incompleta e iscrizione attuale non dimostrata dal feed. Non preparata.
- **Entrix (DE), Personio 2627450:** XML con 11 posizioni; ammette studenti iscritti e neolaureati; 4 GET / 331.972 byte / 2,213 s. Submit inizialmente disabilitato, quindi non verificato. Non preparata.
- **The Social Hub (NL), Greenhouse 5016646101:** inventario 104 posizioni; 2 GET / 1.741.846 byte / 1,289 s. Il board restituisce job-boards.eu.greenhouse.io; robots leggibile, nessuna regola attiva. La verifica successiva sullo stesso host ha trovato un modulo same-ID (4 GET / 1.809.746 byte / 1,966 s), ma un controllo mirato della pagina (2 GET / 67.900 byte / 1,150 s) conferma che la descrizione indica febbraio 2027 e il modulo richiede iscrizione per settembre 2026–gennaio 2027. Non preparata finché le date non siano riconciliate.
- **iKnowHow (GR), Workable:** endpoint pubblico documentato https://www.workable.com/api/accounts/ikh?details=true letto senza token: 21 posizioni, due HR per iscritti con shortcode distinti 7EAEC1444E e 3F368EAC02; 4 GET effettivi / almeno 86.620 byte / 1,794 s (il BudgetClient originario contava 3 richieste e non conteggiava il GET del redirect). Il controllo separato delle due pagine e dei percorsi /apply ha letto 5 GET / 29.926 byte / 2,650 s: HTML senza titolo o form riconoscibile; risposta 200 insufficiente. I due ruoli hanno titoli e responsabilità differenti, ma la distinzione finale e la verifica del modulo rimangono aperte.

Workable richiede un adapter nuovo: la PR propone un lettore GET pubblico, circoscritto e testato offline, senza fonte registrata né attivazione. I test coprono duplicati, URL e redirect non coerenti, 429 e form assente; non trattano l'inventario come prova del modulo. Il lettore aggiornato accetta soltanto il redirect ufficiale osservato verso apply.workable.com e lo conteggia nel budget: prova 4 GET / almeno 86.620 byte / 1,350 s per 21 record e due ID HR. Il body del 302 non è incluso nei byte del client. Prima di proporre una fonte attivabile occorrono prova same-ID del modulo utilizzabile, termini applicabili e ulteriori test di integrazione sul percorso applicativo reale. L'API v3 richiede token e non è usata; [endpoint dei lavori pubblici](https://workable.readme.io/reference/jobs-1) separato. Non confondere pubblicazione con autorizzazione generale al riuso.

## Robots e termini

Verifiche del 21 novembre UTC, risposte leggibili; il client ha letto robots a runtime. Il controllo separato Sungrow e quello dell'host europeo Greenhouse hanno restituito HTTP 200. Per gli altri host il browser ha mostrato il contenuto, ma qui non si attribuisce un codice HTTP non registrato.

| Host e percorso robots | Regola per * |
| --- | --- |
| sungrow-emea.jobs.personio.de/robots.txt, entrix.jobs.personio.de/robots.txt | Allow: / |
| climeworks.recruitee.com/robots.txt, peripass.recruitee.com/robots.txt | Disallow: /v/ |
| job-boards.greenhouse.io/robots.txt, job-boards.eu.greenhouse.io/robots.txt | nessuna regola attiva |
| boards-api.greenhouse.io/robots.txt | Disallow: /embed/ |
| apply.workable.com/robots.txt | Disallow: vuoto |
| www.workable.com/robots.txt | vieta /user_password_resets, /admin, /auth/google, /j/; non /api/accounts/ |

I percorsi effettivamente richiesti non corrispondono ai divieti indicati. [Personio](https://www.personio.com/terms/), [Tellent/Recruitee](https://recruitee.com/terms), [Greenhouse](https://www.greenhouse.com/master-subscription-agreement) e [Workable](https://www.workable.com/terms) pubblicano condizioni principalmente per il rapporto con i clienti; non le si interpreta come licenza generale per terzi. [Personio XML](https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML), [Recruitee XML](https://docs.recruitee.com/docs/feed) e [Greenhouse API](https://docs.greenhouse.io/job-board) documentano le rispettive interfacce. Prima di qualsiasi rollout occorre completare la review dei termini applicabili di provider e datori; robots e documentazione da soli non sostituiscono tale review.

## Gate

Le tre fonti proposte hanno enabled=false e collection_activation_hold=true; lo stesso hold è presente sul datore per impedire il provisioning automatico di crawler alternativi. Test di idempotenza e rifiuto di abilitazione con hold. Questa PR non autorizza merge, rollout, nuovi host globali o modifiche alla cadenza. Dopo review servono approvazione esplicita del merge e distinta approvazione per ogni attivazione, verifica fresca e controllo del primo ciclo reale.
