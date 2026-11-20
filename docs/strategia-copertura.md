# Strategia di raccolta approfondita degli stage HR

Revisione del 5 novembre 2026. Sostituisce la precedente soglia di 300 sedi confermate: la prima soglia richiesta è ora **100 datori con raccolta operativa per ciascuno dei 27 paesi UE**. Non è un limite al registro né una quota di stage da pubblicare. L'ampliamento successivo continua oltre 100.

## Priorità operativa del 20 novembre 2026

Decidere il lavoro per **famiglia ATS e blocco ripetuto**, con una coda di candidature già individuate e una coda di scoperta per paese. Continuano la priorità Paesi Bassi e la mappatura geograficamente rappresentativa dell'Europa. Nella raccolta si preferisce come ingresso l'inventario ufficiale conosciuto di un datore, con ricerca del canale come ripiego. Le nuove fonti e le modifiche di frequenza passano da un confronto prima/dopo e dal consueto gate di attivazione.

### Evidenze misurate

- Snapshot del 19 novembre, main `3f20f51`. **1.919 fonti abilitate con report recente**, 32.591 tentativi registrati, di cui **31.163 nel crawler generico (95,6%)**. 30.192 tentativi presso fonti con zero corrispondenze HR riportate, di cui 29.987 nel crawler generico. Anche le fonti con inventario parziale possono riportare zero. Questi numeri non stimano richieste risparmiabili.
- **33 stage con candidatura diretta recente in 6 paesi**, più 365 schede attive su servizi pubblici in 11 paesi. Solo cinque di queste ultime espongono un URL esterno nel catalogo, tutte svedesi. Recruitee ha prodotto 12 delle 33 candidature dirette nel catalogo (NL, FR, BE, DE). Il percorso osservato Recruitee registra 29 fonti, 88 tentativi e 13 corrispondenze. I segnali di piattaforma nel report possono coesistere per una stessa fonte.
- **13 pagine campionate su sei datori**, 22 tentativi GET nel BudgetClient, 4.844.129 byte, 23,772 s, zero nuovi moduli verificati. Su tutte le pagine i titoli corrispondono. Tre Adecco indicano il tenant Talentsoft, due Danone indicano iCIMS localizzati, due Marriott indicano Oracle, due ING indicano Workday. Questi host esterni sono emersi dalle pagine già ammesse e il pilota li ha lasciati fuori dalle richieste. Randstad mostra pulsanti senza link nel campione. Il modulo L'Oréal ha risposto 403 sul percorso ammesso e lì il test si ferma. [Prova live](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44690039887)

### Priorità per i prossimi lotti

| Lavoro | Perimetro iniziale | Criterio di esito |
| --- | --- | --- |
| Recuperare candidature per una famiglia | Adecco ha 84 schede recenti con lo stesso errore. Valutare accesso e legame per ID sul tenant Talentsoft osservato. Danone/iCIMS ha 9 schede in 4 paesi e Marriott/Oracle 8 in 7 paesi. | Due esempi distinti con provenienza, ID e modulo utilizzabile prima di qualsiasi estensione. Se l'accesso manca, passare a un canale autorizzato alternativo e tenere il gruppo in attesa. |
| Cercare opportunità prima di censire nuovi datori | Recruitee nei Paesi Bassi e nei paesi UE con poche conferme, Teamtailor come lotto comune per cinque posting HR trovati su quattro tenant svedesi assenti dal registro. Integrare il candidato come fonte ricorrente solo dopo prova dell'inventario e del percorso ufficiale. | Stage distinti verificati per paese e GET per conferma, con requisiti di iscrizione e sede documentati dalla fonte. |
| Collegare i portali pubblici ai datori | Italia: 34 schede pubbliche di Gi Group si concentrano su un solo datore, con pagina ufficiale dello staff e portale candidato. Svizzera: Assura offre un primo incrocio possibile tra la scheda pubblica e il proprio sito. NL: il posting IKEA Zwolle è fuori dal perimetro Groningen dell'attuale fonte. | Per ogni correlazione, inventario ufficiale, località, identità pubblica e ID del datore. Conservare l'ID esistente solo con legame dimostrato. |
| Ridurre il costo della scoperta | Usare il report per i crawler con molte richieste e nessun match, partendo dai siti con indice ufficiale rintracciabile. Usare i dati di [#63](https://github.com/nightlydeveloper8/eu-hr-internships/pull/63) per il confronto delle code, senza contare duplicati rimossi come GET risparmiati. | Confronto sugli stessi datori in cicli distinti, con meno richieste e byte, inventario e freschezza delle verifiche conservati, perdita di stage misurata. |

Indizi da verificare con il metodo sopra. [Gi Group](https://careers.gigroupholding.it/job/view-job.php?id=1700-stage-risorse-umane-reggio-emilia&language=it), [Assura](https://www.assura.ch/fr/carriere/postes-a-pourvoir/stagiaire-rh-processus), [IKEA Zwolle](https://jobs.ikea.com/en/job/zwolle/hr-stage/24107/100616030528), [Get Skills](https://getskills.teamtailor.com/jobs/7470836-lia-praktik-hr-rekrytering), [Tacting](https://tacting.teamtailor.com/jobs/8621469-praktikplats-inom-rekrytering-hr-tacting-2027), [Skill 8456336](https://skillscandinavia-1737118918.teamtailor.com/jobs/8456336-skill-soker-hr-student-for-praktikplats-i-var), [Skill 8456449](https://skillscandinavia-1737118918.teamtailor.com/jobs/8456449-studerar-du-inom-rekrytering-eller-bemanning-sok-varens-lia-hos-skill), [Skillity](https://skillity.teamtailor.com/jobs/8699758-lia-praktik-inom-rekrytering-varen-2027).

### Uso del rapporto

`python -m scripts.collection_portfolio` ricalcola il quadro in sola lettura dai tre file `data/catalog.json`, `data/coverage.json` e `data/sources.json`. Il rapporto calcola freschezza rispetto all'ora dello snapshot, gestisce gli stati pubblici e diretti distinti, raggruppa le candidature recenti per tipo di errore e le schede pubbliche per datore e paese. Il verificatore propone di salvare nel report del collector solo hostname CTA, presenza di un identificativo corrispondente e appartenenza agli host ammessi per le pagine già lette e non confermate. Il campo assente nei vecchi snapshot indica mancanza di questa misura. La raccolta di tali segnali nelle pagine già lette aggiunge zero richieste. Due replay identici sulla fotografia reale e sei test mirati superati. [Run offline](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44690735644)

## 1. Il risultato da ottenere

L’obiettivo primario è rendere disponibili agli studenti stage HR realmente aperti, distinti, con una sede verificata e una candidatura utilizzabile. La mappatura delle aziende serve questo risultato. I tentativi automatici, i nomi censiti e i test tecnici non sono indicatori di opportunità disponibili. Gli indicatori principali sono gli stage verificati per paese, le nuove opportunità pubblicate, la freschezza delle verifiche e i requisiti di candidatura leggibili.

Un datore conta verso la soglia nazionale solo quando un raccoglitore ha completato una verifica recente, entro 48 ore, e l'inventario effettivamente letto dimostra la copertura del paese. Un nome, una homepage raggiungibile o una fonte abilitata senza esecuzione non soddisfano il requisito.

Le aziende senza stage correnti restano parte del monitoraggio: zero stage è un risultato valido quando il canale è stato letto correttamente. Un elenco vuoto senza prova del perimetro geografico non dimostra invece copertura di un paese. Per questi casi servirà documentare il filtro nazionale o altro perimetro ufficiale e verificarlo.

Ogni azienda individuata deve avere un'attività di integrazione. L'obiettivo è trasformare l'intero universo dei candidati in monitoraggio delle offerte; la coda non viene presentata come se fosse già raccolta. Dove l'accesso non è disponibile si registra il blocco, si cerca una fonte ufficiale alternativa e si cercano altri datori per raggiungere i 100 operativi del paese.

Il conteggio nazionale usa gruppi distinti per le affiliazioni già documentate. Un gruppo può contribuire a più paesi solo con prove di raccolta in ciascuno. I 2.700 rapporti datore–paese del primo traguardo non sono necessariamente 2.700 gruppi unici europei.

## 2. Due ricerche complementari

**Priorità: partire dalle posizioni.** Cercare stage HR nelle lingue locali attraverso motori di ricerca, portali universitari e bacheche consultabili nei modi consentiti. Individuare l'annuncio originale e risalire al datore e all'intero canale ufficiale, che verrà poi monitorato. Gli aggregatori servono alla scoperta; un risultato di ricerca non prova la disponibilità attuale.

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

Corretta la lettura dei job prima del filtro sugli slug e la gestione delle pagine parzialmente fallite; corretto il conteggio nazionale per usare esecuzioni recenti con copertura effettivamente osservata; generata la coda di integrazione per tutti i datori. La precedente prova su 84 pagine strutturate è stata estesa al raccoglitore generale, all’HTML visibile, alla paginazione con browser e ai checkpoint. Sono passati 113 test Python, 12 test dell’interfaccia e 52 esempi di classificazione senza regressioni. Le prove su ALL IN GROUP e AXS logistiek hanno estratto e verificato due nuovi stage HR da portali prima non integrati. Il test di fusione degli otto gruppi verifica un esito per tutte le 842 aziende e conserva il catalogo in caso di errore generale. Gli esiti effettivi del primo ciclo completo sono nel report aziendale, senza assumere che ogni sito sia leggibile.


## Raccolta sull’intero registro: implementazione

Ogni azienda deve avere un raccoglitore attivo. Il flusso `collector.daily` aggiunge automaticamente un raccoglitore generale alle nuove aziende prive di connettore specifico e ripartisce la raccolta giornaliera su otto gruppi. La copertura configurata è distinta dagli esiti verificati per azienda. Procedura e limiti sono descritti in [raccolta-tutte-aziende.md](raccolta-tutte-aziende.md). Il traguardo di 100 aziende operative per paese rimane misurato sulle letture recenti e sulle sedi effettivamente osservate, senza trasformare i candidati o i tentativi falliti in copertura riuscita.


Il primo ciclo completo ha tentato tutte le 842 aziende. La revisione degli annunci distingue gli stage dai ruoli per studenti e dai traineeship, rimuove gli articoli informativi e unifica le traduzioni con lo stesso identificativo ufficiale. «Praktijk» e «intern» nel senso olandese di ruolo interno non vengono assunti come prove di tirocinio. Le schede già trovate hanno precedenza nella lettura giornaliera; una verifica più vecchia di 48 ore diventa non verificata. Le sitemap dichiarate in robots.txt costituiscono un ulteriore canale di scoperta, senza inventare percorsi.


## Revisione centrata sulle candidature

La prima raccolta non ha raggiunto una copertura adeguata. Le aziende tentate restano una misura del lavoro svolto, distinta dai risultati utili agli studenti. La ricerca mirata delle offerte originali ha individuato canali pubblici che il raccoglitore interpretava male.

Il connettore Amazon legge la rappresentazione JSON della ricerca ufficiale e confronta totale, posizione di paginazione e identificativi. Il primo inventario verificato comprende 37 risultati globali e 27 stage HR in UE. Le sedi e i requisiti derivano dai campi pubblicati. Il connettore SmartRecruiters legge anche la rappresentazione JSON della singola scheda ufficiale e scarta le candidature esplicitamente disattivate. I collegamenti scoperti sono inseriti nei canali automatici. Le fonti già produttive hanno precedenza nell’esecuzione giornaliera.

È stato corretto un errore che interrompeva la pubblicazione quando due duplicati avevano la verifica del collegamento mancante. Gli otto risultati salvati dal ciclo remoto sono stati recuperati, controllati contro il registro originale e riconciliati con il catalogo. Una forte riduzione dell’inventario impedisce chiusure automatiche per assenza, senza impedire la pubblicazione dei nuovi stage validi.

Le risposte malformate di robots.txt vengono analizzate per le direttive effettivamente presenti, secondo [RFC 9309, sezioni 2.3.1.1 e 2.3.1.5](https://www.rfc-editor.org/rfc/rfc9309.html#section-2.3.1.5). I divieti espliciti, le restrizioni di accesso e le verifiche anti-bot continuano a fermare la lettura.

La fotografia aggiornata, con tipi distinti e risultati per paese, è in `docs/jobs-first-results-2026-11-05.json`. Non costituisce il raggiungimento dell’obiettivo nazionale o la conclusione della copertura europea.


## Priorità territoriale: Fryslân — 6 novembre 2026

La richiesta attuale dà precedenza agli stage raggiungibili dagli studenti residenti in Frisia. L'unità di ricerca è il comune: la composizione CBS 2026 comprende 18 comuni e 419 woonplaatsen. Varianti olandesi/frisone e località omonime sono gestite separatamente; non si attribuisce una sede a un comune sulla base di un nome ambiguo.

La prima passata provinciale ha letto tutti i 901 profili della directory WRK e 1650 pagine sui siti ufficiali di 780 datori. Il registro integra 893 datori con presenza provinciale documentata, dei quali 146 qualificati con evidenza di almeno 50 addetti presso il datore/gruppo (145 gruppi distinti). Organico del gruppo, organico locale e personale stagionale retribuito restano distinti. I candidati senza prova dimensionale non sono contati come aziende medio-grandi.

Sono verificati 7 stage HR locali distinti: Philips e BD a Drachten, Sijperda a Sneek, Royal A-ware a Heerenveen, Kenonz a Gorredijk, Haitsma/ BallastNedam a Kootstertille e Tempo-Team a Bolsward. Quattro programmi HR aperti alla richiesta di uno stage restano separati dalle vacancy. Una pagina di Kapenga con HTTP 200 è stata esclusa dopo che il pulsante ufficiale ha comunicato che la posizione è chiusa.

Tutti gli 893 datori regionali integrati hanno ricevuto un tentativo reale. Non tutti i canali sono stati letti completamente: fra i 146 qualificati, 13 inventari osservati sono stati letti, 71 sono parziali, 48 hanno ancora lacune nella scoperta degli annunci e 14 sono bloccati/falliti. Questi stati non equivalgono a zero stage. Le fonti bloccate restano una coda di integrazione e cercano nuovamente i canali pubblici al ciclo successivo; non si aggirano restrizioni di accesso.

La raccolta remota usa 16 gruppi di 6 letture concorrenti, con precedenza per i datori frisoni qualificati e per gli annunci già trovati. Il controllo è programmato ogni giorno alle 06:17 UTC:07:17 in inverno e 08:17 in estate nei Paesi Bassi e in Svizzera. Gli annunci già nel catalogo vengono riletti entro un massimo di 12 ore di riuso della cache; le altre schede possono usare 48 ore. Feed pubblici completi, elenchi HTML e campi visibili revisionati alimentano la stessa raccolta. Il rapporto comunale viene rigenerato e pubblicato dal medesimo ciclo.

La directory non è un registro completo delle imprese provinciali. Per dichiarare un censimento esaustivo serve un confronto con il registro provinciale delle sedi/occupazione o altra base completa, distinguendo sedi da gruppi e applicando lo stesso criterio dimensionale. I profili della directory interamente letti non vengono presentati come tutte le aziende della Frisia.

Dati e metodo aggiornati: [friesland-mappatura.md](friesland-mappatura.md). Pagina pubblica: [stage HR in Fryslân](https://people-placement-eu.pages.dev/friesland.html).


## Estensione provinciale: Groningen — 6 novembre 2026

Avviato il lotto Groningen riutilizzando registro e raccolta: frame CBS completo di 10 comuni e 199 località, 31 datori provinciali, 27 qualificati ≥50 addetti e 4 dimensioni ignote. Eseguiti tutti i 30 canali distinti; i due stage con modulo verificato sono HANOS e Fotofabriek, entrambi in città Groningen e con partenza febbraio 2027. I due annunci IKEA restano non verificati perché il canale di candidatura collegato vieta la lettura al raccoglitore. I programmi generali HR rimangono separati dalle vacancy.

Rapporti e interfaccia provinciali condividono ora la stessa implementazione; anche Groningen viene rigenerato e pubblicato dal workflow mattutino esistente. Nessuna nuova chiamata ricorrente a modelli. Il lotto non è un censimento esaustivo. Metodo, stati comunali, fonti e prova remota: [groningen-mappatura.md](groningen-mappatura.md).


## Estensione provinciale: Drenthe — 6 novembre 2026

Frame CBS completo di 12 comuni e 227 località. Primo lotto di 31 datori, 14 qualificati ≥50 addetti; due stage candidabili verificati presso SKK e Ziengs/Scapino ad Assen. Tentati realmente tutti i 31 canali: due inventari osservati letti, 20 parziali, cinque discovery incomplete, quattro blocchi/fallimenti. NNCZ e Scania non vengono contati fra gli stage verificati. Riutilizzati import, registro, pagina provinciale e workflow quotidiano; produzione remota da verificare dopo merge autorizzato. Nessuna nuova automazione o chiamata ricorrente AI. Dettagli: [drenthe-mappatura.md](drenthe-mappatura.md).


## Estensione provinciale: Utrecht — 7 novembre 2026

Frame CBS completo di 26 comuni e 104 località, con codice NUTS 2024 NL35. Integrati 51 datori distinti, 20 qualificati ≥50 e 31 dimensioni ignote; 58 tentativi reali su 51 fonti. Sei stage con candidatura verificata: Remia, Trunkrs, Berenschot, due AS Watson e Domino’s. Le partenze Trunkrs/Domino’s richiedono conferma del nuovo intake. Stati correnti: quattro inventari osservati letti, 33 parziali, dieci scoperte incomplete, quattro blocchi/fallimenti. Tutti i comuni hanno datori ricercati; questo non equivale a un censimento né alla copertura di ogni località. Registro, importatore, report, pagina provinciale e sedici shard quotidiani sono condivisi. Nessuna nuova automazione o chiamata ricorrente AI; merge e produzione ancora da autorizzare. [Rapporto dettagliato](utrecht-mappatura.md).
