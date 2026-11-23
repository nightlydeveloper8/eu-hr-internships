# Benchmark di recall degli stage HR per studenti — 23 novembre 2026

**Campione parziale: 16 schede pubbliche attuali su 220 previste.** Una è in Italia, 15 in Germania e tutte le 15 tedesche provengono dallo stesso gruppo. Le 16 schede sono assenti dallo snapshot del portale. Il recall di mercato nei sei paesi e il numero di candidature utilizzabili che le leve recupererebbero sono **non dimostrato**. [CSV delle schede osservate](recall-gold-set-2026-11.csv)

## Come è stato costruito il campione

La ricerca ha usato termini locali per stage HR e requisiti per studenti. Le schede conteggiate provengono da sitemap pubbliche indicate nel robots dello stesso host, con dettaglio HTTP 200, identificatore coerente, JobPosting e prove esplicite di tirocinio per studenti e attività HR. Per Manpower c’è anche una scadenza futura. La presenza congiunta nella sitemap aziendale corrente e nel dettaglio conferma la pubblicazione Bosch. L’effettiva utilizzabilità della candidatura policy v2 resta **non dimostrato** per tutte le righe. Le due lingue dello stesso annuncio, più città per un solo ID e i risultati duplicati dei motori si contano una volta.

La selezione per titoli dalla sitemap Bosch privilegia le offerte che nominano HR, recruiting o funzioni equivalenti. La ricerca non è probabilistica e l’alta concentrazione per gruppo impedisce di estendere le quote al paese. Sono esclusi graduate programme, Werkstudent, ruoli senza placement HR identificato e indici privi di prova attuale. Nessun accesso diretto a LinkedIn, Indeed, InfoJobs o Glassdoor. L’indice ha mostrato risultati Indeed per l’Italia. L’esclusività «visibile solo su Indeed» per una singola vacancy è **non dimostrato**, quindi non ci sono righe o dati raccolti da questi risultati.

## Recall per paese

Il recall aperto osservato è il numero di schede del campione con la stessa vacancy aperta e verificata entro 48 ore nel catalogo diviso per le schede del campione. La colonna lead conta eventuali corrispondenze ancora visibili come piste. Il riferimento è `data/catalog.json` da [8f15504](https://github.com/nightlydeveloper8/eu-hr-internships/commit/8f15504), aggiornato il 23 novembre alle 17:45 UTC, con registri e regole da [03d22a5](https://github.com/nightlydeveloper8/eu-hr-internships/commit/03d22a5). Il confronto usa URL, ID del posting, ID ATS e datore/titolo/città. Le varianti Bosch già nel catalogo EURES hanno titoli, sedi o identificativi differenti. Un’eventuale corrispondenza con un intermediario anonimo è **non dimostrato**.

| Paese | Quota | Schede | Aperto | Lead | Assente | Recall aperto osservato | Recall di mercato |
|---|---:|---:|---:|---:|---:|---|---|
| Italia | 60 | 1 | 0 | 0 | 1 | 0/1 | non dimostrato |
| Spagna | 60 | 0 | 0 | 0 | 0 | non dimostrato | non dimostrato |
| Francia | 30 | 0 | 0 | 0 | 0 | non dimostrato | non dimostrato |
| Germania | 30 | 15 | 0 | 0 | 15 | 0/15 | non dimostrato |
| Polonia | 20 | 0 | 0 | 0 | 0 | non dimostrato | non dimostrato |
| Irlanda | 20 | 0 | 0 | 0 | 0 | non dimostrato | non dimostrato |

Come contesto separato, lo snapshot contiene i seguenti record con sede nel paese, secondo `verifiedJob` e `applicationConfirmed` all’ora dello snapshot. Per i lead sono contati i record non chiusi che non passano `verifiedJob`. Una scheda con più paesi può comparire in più righe.

| Paese | Aperti v2 | Di cui diretti | Lead | Chiusi |
|---|---:|---:|---:|---:|
| Italia | 27 | 0 | 39 | 8 |
| Spagna | 3 | 1 | 20 | 0 |
| Francia | 44 | 7 | 144 | 7 |
| Germania | 36 | 11 | 37 | 6 |
| Polonia | 0 | 0 | 10 | 0 |
| Irlanda | 0 | 0 | 0 | 0 |

## Cause e piattaforme dei mancati

Le cause sono a) datore assente, b) ATS senza supporto, c) ATS supportato senza tenant, d) classificazione dimostrata sul titolo e sulla regola, e) annuncio esclusivamente su piattaforma vietata, f) agenzia, g) università o ErasmusIntern, h) altro. Le 15 schede Bosch sono pubblicate su un canale careers leggibile ma fuori da `allowed_hosts` di `auto-bosch`. L’adapter SmartRecruiters esiste, il dominio di candidatura è escluso dalla regola e il portale del datore è un canale distinto. La causa principale osservabile è h. La mancata acquisizione a causa del classificatore è **non dimostrato**.

| Paese | a | b | c | d | e | f | g | h | Piattaforme tra le schede mancanti |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Italia | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | Manpower Italia 1 |
| Germania | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 15 | Bosch Stellenportal 15, con rinvio SmartRecruiters BoschGroup 15 |
| Spagna, Francia, Polonia, Irlanda | — | — | — | — | — | — | — | — | non dimostrato |

Il datore Manpower è nel registro, ma l’host di `auto-manpower` è olandese. La lettura a basso ritmo è riuscita sul percorso italiano indicato dalla sitemap. I termini §§10–12 limitano riuso e collegamenti da terzi, quindi la possibilità di pubblicare questo canale è **non dimostrato**. La verifica Bosch riguarda il sito del datore. Nessun GET è stato inviato a SmartRecruiters. [Termini Manpower](https://www.manpower.it/it/terms-of-use) · [Note legali Bosch Karriere](https://jobs.bosch.com/de/rechtliche-hinweise/)

| Paese | >1.000 a livello di gruppo | PMI documentate | Dimensione non dimostrata |
|---|---:|---:|---:|
| Italia | 0/1 | 0/1 | 1/1 |
| Germania | 15/15 | 0/15 | 0/15 |
| Spagna, Francia, Polonia, Irlanda | non dimostrato | non dimostrato | non dimostrato |

La dimensione tedesca è quella del gruppo, 412.800 addetti dichiarati, condivisa dalle schede delle diverse società. La quota per singola entità giuridica e le quote nazionali restano **non dimostrato**. [Bosch, dati societari](https://www.bosch.com/company/facts-and-figures/)

## Dove estendere la ricerca e costo delle leve

Le priorità seguenti derivano dalle schede mancanti e dalle piste indicizzate. I costi sono stime di lavoro per un pilota, da verificare in staging. Le stime di schede recuperabili sono limiti condizionati sul campione, senza estrapolazione. Per candidature verificate v2, tutte le celle sono **non dimostrato**.

| Leva | Costo di lavoro stimato | IT | ES | FR | DE | PL | IE |
|---|---|---|---|---|---|---|---|
| 1. Verificare i portali careers propri dei datori già censiti e collegare le stesse vacancy a un percorso di candidatura ammesso | 1–2 giorni per un pilota monosito, inclusi ID, host e controllo della candidatura | non dimostrato | non dimostrato | non dimostrato | 0–15 schede Bosch | non dimostrato | non dimostrato |
| 2. Verificare i canali nazionali delle agenzie con placement curriculari e condizioni compatibili con la pubblicazione | 1–2 giorni per 3 host e deduplicazione | 0–1 schede Manpower | non dimostrato | non dimostrato | non dimostrato | non dimostrato | non dimostrato |
| 3. Ampliare la discovery attraverso portali universitari pubblici e placement Erasmus con un link ufficiale verificabile | 2–3 giorni per 4 portali e controllo dei percorsi pubblici | non dimostrato | non dimostrato | non dimostrato | non dimostrato | non dimostrato | non dimostrato |

**Italia.** Ampliare la ricerca locale per `stage curriculare`, `laureando` e `convenzione universitaria`, incrociando career site, agenzie e portali universitari pubblici. L’annuncio Manpower Torino mostra un canale italiano distinto dal registro corrente. Verificare le condizioni di riuso prima di considerare quel canale. Gi Group Novara è una pista curriculare indicizzata, con termini e formato automatizzato ancora incerti. MAW vieta espressamente l’estrazione automatizzata, quindi serve un’altra fonte ammessa per le eventuali vacancy viste nell’indice. [Gi Group Novara](https://careers.gigroupholding.it/job/view-job.php?id=1746-tirocinio-risorse-umane-novara-novara&language=it) · [Termini MAW](https://www.maw.it/termini-e-condizioni)

**Spagna.** Cercare esplicitamente `prácticas recursos humanos` insieme a `convenio con universidad`, con attenzione agli ID duplicati fra spagnolo e inglese. Partire dai portali universitari pubblici come FUE-UJI e dalle careers che espongono il formato e il percorso ammessi. Il caso W Barcelona documenta il convenio nell’indice, con applicabilità dei termini Marriott al sito careers incerta. Il caso Expat Globe ha una scadenza indicizzata a gennaio 2027, ma il robots di ErasmusIntern ha risposto 403 e il sito segnala la migrazione a Erasmus Careers. Questi sono punti da verificare prima di contare schede o proporre un recupero. [FUE-UJI](https://www.fue.uji.es/practicas/oferta/estudiante-grado-psicologia-grado-relaciones-laborales-rrhhmaster-psicologia-del-trabajo-las-organizaciones-los-recursos-humanos-master-direccion-recursos-humanos--4752) · [W Barcelona](https://careers.marriott.com/es/pr%C3%A1cticas-recursos-humanos-w-barcelona/job/P1-7674787-0) · [Expat Globe](https://erasmusintern.org/traineeship/talent-acquisition-human-resources-and-international-relations-internship)

In Francia l’indice Safran mostra stage HR etichettati per studenti. La portata dei termini sul download e riuso è incerta. In Irlanda Fidelity e Stryker espongono placement HR per studenti nell’indice, con attualità e accesso automatizzato **non dimostrato**. In Polonia la ricerca ha soprattutto restituito aggregatori. Anche il caso studentesco Bosch Rexroth Varsavia richiede una scheda ufficiale prima dell’ammissione. [Safran](https://www.safran-group.com/fr/offres?contracts%5B0%5D=42-stage&job_fields%5B0%5D=1602-ressources-humaines) · [Condizioni Safran](https://www.safran-group.com/fr/informations-legales) · [Fidelity](https://jobs.fidelity.com/ie/jobs/2136467/human-resources-internship/) · [Stryker](https://careers.stryker.com/human-resources-co-op/job/67D793579047E5227D3851417A1A60D4)

## Telemetria e verifiche

**35 GET diretti, 7.785.625 byte di corpi HTTP, 20,069 s cumulativi in curl**, esclusi attese fra richieste, GitHub, consultazione degli indici e test. Sono inclusi 16 GET robots (un controllo preliminare ripetuto), 3 GET sitemap e 16 schede. Le richieste sottostanti del motore di ricerca, i suoi byte e il tempo complessivo di lavoro sono **non dimostrato**. I riscontri di staging non sono versionati. Nessun accesso a moduli di candidatura.

Il diff riguarda tre file di documentazione. Il catalogo resta a 937 ID, con zero persi. Sulla base intatta, in copia temporanea, passano 51 test Node, 105 esempi del classificatore, coverage, build, validazione del catalogo e provisioning. Lo stesso controllo Python sulla base intatta ha eseguito 573 test, con 3 fallimenti (stati attesi nei replay) e 4 errori (fixture e simulazioni HTTP). Il campione resta incompleto di 204 schede. Il passo successivo è estendere il campione a più datori e canali ammessi in ogni paese, partendo dai due paesi con quota 60.
