# Strategia di raccolta approfondita degli stage HR

Revisione del 5 novembre 2026. Sostituisce la precedente soglia di 300 sedi confermate: la prima soglia richiesta è ora **100 datori con raccolta operativa per ciascuno dei 27 paesi UE**. Non è un limite al registro né una quota di stage da pubblicare. L'ampliamento successivo continua oltre 100.

## 1. Il risultato da ottenere

Un datore conta verso la soglia nazionale solo quando un raccoglitore ha completato una verifica recente, entro 48 ore, e l'inventario effettivamente letto dimostra la copertura del paese. Un nome, una homepage raggiungibile o una fonte abilitata senza esecuzione non soddisfano il requisito.

Le aziende senza stage correnti restano parte del monitoraggio: zero stage è un risultato valido quando il canale è stato letto correttamente. Un elenco vuoto senza prova del perimetro geografico non dimostra invece copertura di un paese. Per questi casi servirà documentare il filtro nazionale o altro perimetro ufficiale e verificarlo.

Ogni azienda individuata deve avere un'attività di integrazione. L'obiettivo è trasformare l'intero universo dei candidati in monitoraggio delle offerte; la coda non viene presentata come se fosse già raccolta. Dove l'accesso non è disponibile si registra il blocco, si cerca una fonte ufficiale alternativa e si cercano altri datori per raggiungere i 100 operativi del paese.

Il conteggio nazionale usa gruppi distinti per le affiliazioni già documentate. Un gruppo può contribuire a più paesi solo con prove di raccolta in ciascuno. I 2.700 rapporti datore–paese del primo traguardo non sono necessariamente 2.700 gruppi unici europei.

## 2. Due ricerche complementari

**Partire dalle posizioni:** cercare stage HR nelle lingue locali attraverso motori di ricerca, portali universitari e bacheche consultabili nei modi consentiti. Individuare l'annuncio originale e risalire al datore e all'intero canale ufficiale, che verrà poi monitorato. Gli aggregatori servono alla scoperta; un risultato di ricerca non prova la disponibilità attuale.

**Partire dai datori:** mappare imprese attraverso associazioni territoriali, distretti industriali, camere di commercio, agenzie regionali, career centre e programmi studenti. Per ogni nuovo datore cercare subito il canale di recruiting e l'adattatore. Evitare nuovi lotti concentrati sullo stesso paese quando la verifica dei canali precedenti rimane indietro.

Le imprese con 50–249 e 250–999 addetti sono centrali, insieme a piccole aziende con funzione HR o programmi studenti documentati. La notorietà del marchio e la facilità tecnica non determinano l'universo della ricerca. Dimensioni sconosciute rimangono sconosciute. La quota operativa del piano dedica almeno il 60% delle ricerche alle fasce 50–999, cercando almeno il 35% nella fascia 50–249; questo non autorizza ad attribuire dimensioni prive di evidenza.

Le fasce sono categorie di ricerca, non un'attestazione giuridica di PMI: la [definizione della Commissione](https://single-market-economy.ec.europa.eu/smes/sme-fundamentals/sme-definition_en) comprende anche requisiti finanziari e rapporti societari.

## 3. Raccoglitori riutilizzabili, per sistema di recruiting

La crescita deve avvenire soprattutto attraverso adattatori riutilizzabili per famiglie di siti. Ogni datore mantiene identificativo, dominio e perimetro verificati: il riconoscimento del fornitore non abilita automaticamente una bacheca non controllata.

| Livello | Raccolta richiesta | Stato nel progetto |
|---|---|---|
| API e feed pubblici | Tutte le posizioni pubblicate, tutte le pagine, campi completi | Greenhouse, Lever, Personio XML e Recruitee operativi su datori verificati; altre integrazioni richiedono revisione |
| Sitemap e JobPosting | Tutte le URL di lavoro nel perimetro dichiarato e lettura di ogni pagina | Lettura prima del filtro implementata; prova live su 84 pagine |
| HTML ordinario | Elenchi, paginazione, schede e campi visibili con selettori verificati | Inventario di collegamenti implementato; estrattori senza JobPosting da ampliare |
| Siti dinamici | Browser che esegue JavaScript, segue filtri e «carica altro», poi estrae dati e testo visibili | Da implementare e provare nel processo di raccolta |
| Accesso non disponibile | Fonte ufficiale alternativa, autorizzazione se necessaria o blocco documentato | Non conteggiato come raccolta funzionante |

Esempi di piattaforme da esaminare per connettori riutilizzabili: Workday, SuccessFactors, Taleo, iCIMS, SmartRecruiters, Teamtailor, Inrecruiting e altri sistemi locali. Non si presume che ciascun fornitore offra un'API pubblica utilizzabile: scegliere il canale effettivamente disponibile, documentato o visibile nel browser, rispettando le regole di accesso.

I browser devono far parte del processo eseguibile sul runner, con dipendenze riproducibili e controlli sul risultato. Aprire manualmente una pagina una volta non costituisce un adattatore né un monitoraggio automatico. [Playwright supporta l'esecuzione in CI](https://playwright.dev/docs/ci); questo livello non è ancora installato o attivato nel collector.

## 4. Profondità dell'inventario

La raccolta deve raggiungere tutte le pagine del canale dichiarato, comprese paginazione, «carica altro», filtri nazionali e portali ATS esterni collegati dal datore. Limitare la navigazione ai domini e alle sezioni revisionati; seguire collegamenti realmente osservati, senza inventare identificativi o percorsi di offerte.

Per le sitemap, **lo slug non decide se aprire un annuncio**. Una URL numerica può contenere uno stage HR. Per gli elenchi, un'etichetta generica sul pulsante non può sostituire il titolo reale. La nuova pipeline legge le pagine strutturate inventariate prima della classificazione; la prova su Tyche Bank e Var Group ha letto 7 e 77 annunci senza errori.

La scoperta da sitemap non garantisce che il datore inserisca tutte le offerte nella sitemap. Affiancare inventario, elenchi e conteggi pubblicati dal sito, e misurare gli scostamenti. Un limite di sicurezza o una pagina mancante non può essere presentato come inventario completo.

I siti JavaScript possono avere un HTML iniziale privo degli annunci; questo richiede il rendering e una seconda estrazione di link e dati. [Google documenta questa distinzione](https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics). Se manca JSON-LD, estrarre il contenuto visibile delle sezioni dell'offerta con un adattatore verificato, non fermarsi alla sola assenza di dati strutturati.

## 5. Selezione HR e stage dopo la lettura

Generare candidati con titolo, descrizione, categoria HR, dipartimento, tipo contrattuale e termini nelle lingue locali. Esempi: HR, Human Resources, People Operations, Talent Acquisition, Personalwesen, Recruiting, risorse umane, ressources humaines, recursos humanos; internship, stage, tirocinio, Praktikum, prácticas e termini equivalenti.

L'allargamento serve a trovare candidati da verificare, non a includere automaticamente ogni ruolo che menzioni la funzione HR o una parola «intern». Il testo deve descrivere attività HR e un'opportunità di stage esplicita. Ruoli permanenti che citano stagisti, software HR venduto ai clienti e sourcing negli acquisti sono casi negativi. Working student e apprendistato rimangono tipi distinti. I casi ambigui vanno in revisione.

L'estrazione di sede, lingue, iscrizione universitaria e altri requisiti deriva da affermazioni esplicite. Le sedi del gruppo e i paesi candidati non vengono assegnati a ogni offerta. I paesi dichiarati nei dati strutturati restano disponibili anche quando le città hanno nomi non ancora riconosciuti.

## 6. Frequenza, carico e aggiornamenti

Inventario giornaliero dei canali; prevedere controlli più frequenti per le fonti utili solo dopo misura dei tempi e dei limiti. La frequenza maggiore non è attivata da questa revisione.

Per scalare a migliaia di datori, aggiungere aggiornamenti incrementali: identificativi dei job, date di modifica, ETag e Last-Modified quando affidabili, cache di metadati consentiti, verifica periodica completa e coda dei dettagli nuovi o cambiati. Separare la concorrenza tra aziende dai limiti per singolo host. Queste ottimizzazioni non sono ancora implementate nel client.

La nuova lettura integrale aumenta le richieste sulle sitemap. Prima di estendere il numero di datori misurare tempi e budget del runner: il workflow è stato portato a un limite di 60 minuti per verificare la raccolta ampliata. Non tagliare silenziosamente l'inventario per rispettare il timeout; usare partizioni e checkpoint quando necessari. La disponibilità entro eventuali piani gratuiti va verificata sul carico reale.

Il sito pubblicato resta statico; raccolta e rendering si eseguono nel processo separato. Il codice e i dati locali devono essere pubblicati nel repository eseguito dai workflow prima che le modifiche arrivino al servizio remoto.

## 7. Errori e disponibilità

Gli errori su una pagina devono comparire nel rapporto. Le pagine lette correttamente possono produrre nuovi risultati; una fonte incompleta resta «partial» e non soddisfa la soglia nazionale di raccolta completa. Le offerte precedenti vengono conservate se manca una verifica affidabile della chiusura.

Per le sitemap la semplice scomparsa non prova la chiusura. Usare prove come stato ufficiale dell'annuncio, scadenza esplicita, rimozione confermata o politica di assenza ripetuta su inventari completi, secondo il canale. Una risposta HTTP 200, da sola, non prova la disponibilità.

## 8. Cruscotto che misura raccolta effettiva

Per datore registrare: canale, adattatore, ultimo tentativo, ultimo successo, perimetro geografico, posizioni inventariate, pagine lette, errori, offerte HR valide e prossima attività di integrazione. Gli stati devono distinguere scoperta del canale, integrazione richiesta, raccolta operativa e raccolta degradata.

Per paese: datori candidati, datori monitorati recentemente nel paese, divario rispetto a 100, fonti complete/parziali/bloccate, stage aperti, dimensioni e settori quando documentati. Le sedi confermate restano un dato distinto; la verifica dell'anagrafica non deve impedire l'inserimento di uno stage con sede ufficiale già verificata nell'annuncio.

File operativi:

- `data/employer-research-plan.json`: prima soglia 100 e obiettivi successivi per i 27 paesi.
- `docs/country-research-progress.json`: avanzamento basato sulle raccolte effettive recenti.
- `docs/company-integration-queue.json`: ogni datore e attività necessaria per la raccolta.
- `data/coverage.json`: inventari, pagine lette, errori e paesi osservati.

La fotografia di partenza è 842 datori nel registro e 40 canali configurati e già eseguiti. Dei restanti 802, 501 hanno una pagina carriera da integrare e 301 richiedono prima la scoperta del canale. Questi sono lavori aperti, non 802 fonti operative.

## Verifiche già eseguite in questa revisione

Corretta la lettura dei job prima del filtro sugli slug e la gestione delle pagine parzialmente fallite; corretto il conteggio nazionale per usare esecuzioni recenti con copertura effettivamente osservata; generata la coda di integrazione per tutti i datori. Prova live: 84 pagine su due fonti, senza errori, con catalogo rimasto a 22 opportunità. Browser, nuovi fornitori ATS, estrazione HTML senza JSON-LD, paginazione generalizzata e cache incrementale richiedono ancora implementazione e verifica.
