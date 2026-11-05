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

La crescita deve avvenire soprattutto attraverso adattatori riutilizzabili per famiglie di siti. Ogni datore mantiene identificativo, dominio e perimetro verificati: il riconoscimento usa identificativi presenti in collegamenti pubblicati dal datore e verifica l’accesso durante ogni raccolta. Non vengono inventati identificativi di bacheca.

| Livello | Raccolta richiesta | Stato nel progetto |
|---|---|---|
| API e feed pubblici | Tutte le posizioni pubblicate, tutte le pagine, campi completi | Greenhouse, Lever, Personio XML e Recruitee operativi su datori verificati; altre integrazioni richiedono revisione |
| Sitemap e JobPosting | Tutte le URL di lavoro nel perimetro dichiarato e lettura di ogni pagina | Lettura prima del filtro implementata; prova live su 84 pagine |
| HTML ordinario | Elenchi, paginazione, schede e campi visibili con selettori verificati | Estrattore generale di schede visibili implementato; i formati non leggibili restano esplicitamente incompleti |
| Siti dinamici | Browser che esegue JavaScript, segue filtri e «carica altro», poi estrae dati e testo visibili | Playwright installato sul runner, browser isolato e paginazione automatica implementati e provati |
| Accesso non disponibile | Fonte ufficiale alternativa, autorizzazione se necessaria o blocco documentato | Non conteggiato come raccolta funzionante |

Esempi di piattaforme da esaminare per connettori riutilizzabili: Workday, SuccessFactors, Taleo, iCIMS, SmartRecruiters, Teamtailor, Inrecruiting e altri sistemi locali. Non si presume che ciascun fornitore offra un'API pubblica utilizzabile: scegliere il canale effettivamente disponibile, documentato o visibile nel browser, rispettando le regole di accesso.

I browser devono far parte del processo eseguibile sul runner, con dipendenze riproducibili e controlli sul risultato. Aprire manualmente una pagina una volta non costituisce un adattatore né un monitoraggio automatico. [Playwright supporta l'esecuzione in CI](https://playwright.dev/docs/ci); questo livello è ora installato e attivato nel collector, con versione delle dipendenze fissata e prova del browser eseguita.

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

Il raccoglitore conserva una cache tecnica dei dettagli per massimo 48 ore di riuso e una coda delle pagine ancora da leggere. Privilegia le pagine non ancora in cache e conserva le attività interrotte. La concorrenza tra aziende è distinta dai limiti per dominio nello stesso gruppo di esecuzione. ETag e Last-Modified non sono ancora usati come prova generale di invariabilità.

La lettura approfondita aumenta le richieste. Il workflow ripartisce ora l’intero registro in otto gruppi, ciascuno con sei letture concorrenti e un limite di 55 minuti. Ogni azienda ha inoltre un budget autonomo di tempo e richieste: il lavoro residuo viene segnalato e conservato per il tentativo successivo. La disponibilità entro eventuali piani gratuiti va verificata sul carico reale.

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
- `data/employer-collection.json`: esito di raccolta per ciascuna azienda, distinto dalla configurazione.

La fotografia iniziale era 842 datori nel registro e 40 canali di raccolta. Sono stati aggiunti 802 raccoglitori generali: tutte le 842 aziende sono ora assegnate al processo automatico. Per le 301 aziende prive di pagina carriera, la scoperta parte dal sito censito. Configurazione, tentativo, lettura riuscita e copertura incompleta restano conteggi distinti nel report aziendale.

## Verifiche già eseguite in questa revisione

Corretta la lettura dei job prima del filtro sugli slug e la gestione delle pagine parzialmente fallite; corretto il conteggio nazionale per usare esecuzioni recenti con copertura effettivamente osservata; generata la coda di integrazione per tutti i datori. La precedente prova su 84 pagine strutturate è stata estesa al raccoglitore generale, all’HTML visibile, alla paginazione con browser e ai checkpoint. Sono passati 98 test Python, 12 test dell’interfaccia e 52 esempi di classificazione senza regressioni. Le prove su ALL IN GROUP e AXS logistiek hanno estratto e verificato due nuovi stage HR da portali prima non integrati. Il test di fusione degli otto gruppi verifica un esito per tutte le 842 aziende e conserva il catalogo in caso di errore generale. Gli esiti effettivi del primo ciclo completo sono nel report aziendale, senza assumere che ogni sito sia leggibile.


## Raccolta sull’intero registro: implementazione

Ogni azienda deve avere un raccoglitore attivo. Il flusso `collector.daily` aggiunge automaticamente un raccoglitore generale alle nuove aziende prive di connettore specifico e ripartisce la raccolta giornaliera su otto gruppi. La copertura configurata è distinta dagli esiti verificati per azienda. Procedura e limiti sono descritti in [raccolta-tutte-aziende.md](raccolta-tutte-aziende.md). Il traguardo di 100 aziende operative per paese rimane misurato sulle letture recenti e sulle sedi effettivamente osservate, senza trasformare i candidati o i tentativi falliti in copertura riuscita.


Il primo ciclo completo ha tentato tutte le 842 aziende. La revisione degli annunci distingue gli stage dai ruoli per studenti e dai traineeship, rimuove gli articoli informativi e unifica le traduzioni con lo stesso identificativo ufficiale. «Praktijk» e «intern» nel senso olandese di ruolo interno non vengono assunti come prove di tirocinio. Le schede già trovate hanno precedenza nella lettura giornaliera; una verifica più vecchia di 48 ore diventa non verificata. Le sitemap dichiarate in robots.txt costituiscono un ulteriore canale di scoperta, senza inventare percorsi.
