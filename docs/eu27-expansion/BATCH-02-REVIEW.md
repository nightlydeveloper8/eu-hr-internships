# Lotto 02 — Italia, Spagna, Portogallo e Austria

> Aggiornamento successivo alla preparazione: BSH è stata attivata con autorizzazione nella PR #43. Primo ciclo ordinario: 25 → 26 stage verificati; catalogo e sito pubblico confermati. Vedi [rapporto di produzione](bsh-first-production-cycle-2026-11-16.json). Il resto del documento fotografa la fase preparatoria.

**Otto indizi verificati: una nuova fonte ammissibile preparata (BSH Spagna), uno stage già monitorato (Emma), sei indizi non ammissibili. Nessuna attivazione o modifica del catalogo.**

| Paese | Datore / indizio | Esito effettivo |
|---|---|---|
| IT | Kering / Ginori 1735 | Vacancy R172404 presente; robots vieta il percorso di candidatura osservato. Nessuna alternativa tentata. |
| IT | Kering / Gucci | Il vecchio URL rimanda all'elenco Europa; identità della stessa vacancy non stabilita. Non dichiarata chiusa. Stesso gruppo di Ginori. |
| IT | Société Générale | Vacancy 26000NCI corrispondente; Taleo restituisce un redirect JavaScript al login, senza modulo candidato verificabile. Nessuna autenticazione. |
| ES | ENGIE | Vacancy di Madrid e CTA corrispondenti; robots vieta il percorso di candidatura. Non estesa la fonte italiana esistente. |
| ES | BSH | **15 posizioni effettive, 1 stage HR verificato nel pilota**, due candidature spontanee escluse. Collegamento ufficiale datore→portale e modulo visibile abilitato dello stesso ID 46112. |
| AT | Revolution Event | Datore→tenant Personio confermato; XML con 8 posizioni, una HR. Modulo dello stesso ID, ma submit disabilitato e contenitore cf-turnstile: prova di candidatura non stabilita. Anche il paese dell'office non è risolto dal connettore corrente. |
| PT | Unit4 | robots restituisce 429; nessun nuovo tentativo. Inventario sconosciuto, non vuoto. |
| PT | Emma | Lo stesso stage People Process Automation Intern è già verificato dalla fonte Lever in produzione. Nessuna nuova richiesta o duplicazione. |

## Integrazione preparata: BSH Spagna

[Stage di formazione HR a Zaragoza](https://jobs.bsh-group.de/46112-practicas-recursos-humanos-formacion/es/job.html?persisted_lang=es). Lingua dell'annuncio spagnola; inglese B2 esplicito; lavoro con solo inglese **non stabilito**. La frase B2 è conservata nel bundle: l'estrattore automatico delle lingue non la riconosce ancora e non si forza il tag inglese. Requisiti e condizioni documentate: studente di laurea/master nelle discipline indicate, stage retribuito, 30–32 ore settimanali.

Il [sito del datore](https://www.bsh-group.com/es/es/trabajar-en-bsh/bienvenido-a-bsh/) collega esattamente `jobs.bsh-group.de/index/es`. L'elenco dichiara 15 posizioni e contiene due tabelle distinte: `publicationsList` per le posizioni effettive, `publicationsUnsolicitedList` per candidature spontanee. Il numero dichiarato deve coincidere con tutti i link della prima tabella. Nessuna completezza globale BSH o nazionale spagnola dichiarata; chiusure per assenza disabilitate.

Tre modifiche riutilizzabili, ancora in review:

- Filtro stage: riconosce **Prácticas** all'inizio del titolo o della tipologia contrattuale. Un riferimento a buone pratiche nella descrizione di un ruolo permanente non basta.
- Elenchi HTML: contenitore revisionato esatto, unico e presente; titoli completi revisionati e conteggio obbligatorio. Solo con questo opt-in si filtrano i ruoli prima di aprire le schede. Gli elenchi precedenti mantengono l'arricchimento completo. Titoli mancanti/troncati o conteggi discordanti falliscono esplicitamente.
- Candidatura `publication-linked`: segue solo la CTA pubblicata della stessa vacancy/ID, controlla titolo, host, redirect di sola lingua, azione del modulo dello stesso ID, campi visibili abilitati e submit. Non inventa endpoint, non usa login, non invia dati. Riutilizza la pagina appena verificata per evitare un GET duplicato.

Bundle fuori dal runtime: [batch-02-integration-bundle.json](batch-02-integration-bundle.json). Un'azienda e una fonte **disabilitata**, nessuna estensione dei registri, degli host di produzione o del gate Dynamic ATS. Eventuale attivazione soltanto con autorizzazione specifica e inserimento atomico azienda+fonte abilitata; un'azienda da sola attiverebbe il fallback del provisioner.

## Beneficio e costo misurati

**Pilota live limitato al solo canale BSH:** 15 posizioni, 14 escluse dal filtro HR/studenti, uno stage aperto con prova policy v2; **5 richieste logiche, 60,682 secondi, 109.503 byte, zero rendering e zero errori**. Budget 10 richieste/75 secondi rispettato. Il portale impone crawl-delay di 10 secondi: si rispettano i ritardi, compresi quelli dei redirect. Una fonte ulteriore non equivale a un aumento già pubblicato: beneficio potenziale **+1**, produzione invariata.

L'intera verifica degli otto indizi più pilota: **39 richieste logiche, 115,265 secondi-fonte cumulati, 2.377.523 byte**, zero rendering; tre query di ricerca aggiuntive, separate da questi contatori. Le richieste logiche includono robots e tentativi respinti prima di leggere il contenuto; non contano separatamente ogni hop HTTP. Non è una misura del tempo a muro della sessione o dei costi monetari.

Evidenze e manifest delle letture: [batch-02-review-2026-11-16.json](batch-02-review-2026-11-16.json). I raw GET temporanei non sono importati nel catalogo. Fixture reali ridotte rimuovono valori di input nascosti e token pubblici di sessione; provano regressioni, non disponibilità attuale. Dopo il pilota è stata corretta soltanto l'etichetta del report che descrive il filtraggio da titoli; nessuna rilettura live per questa correzione descrittiva.

Validazione: **395 test Python, 26 Node, 64 esempi di classificazione e build superati**; 11 nuovi test su inventario, identità/modulo, contesto geografico e due cicli offline idempotenti con tutti gli ID precedenti conservati. Un secondo ciclo live e l'aumento in produzione non sono ancora dimostrati.

## Prossimo punto incompleto

Review della PR e, solo su autorizzazione specifica, integrazione/attivazione atomica BSH e misura del primo ciclo ordinario. Revolution Event resta nella coda tecnica per modulo dinamico e paese del feed; non allargare il gate esistente sulla base del solo titolo. Unit4 resta sospesa per 429. Kering e ENGIE non vanno ritentati su percorsi alternativi. Cercare il prossimo lotto negli altri paesi su canali ufficiali con inventari e candidatura accessibili; questi otto indizi non completano nessun paese UE.
