# PAESI-PICCOLI — verifica preliminare del 25 novembre 2026

Baseline del [catalogo ec2b201](https://github.com/nightlydeveloper8/eu-hr-internships/blob/ec2b2016ec754fe8a238103066fb89e1d393ce89/data/catalog.json) al suo timestamp 19:45:42 UTC, con il predicato `openings` di `scripts/stage_held_career_lot.py`. Il catalogo contiene 1.205 ID e 644 stage aperti. Il confronto dopo il lotto e le verifiche di produzione sono pendenti.

| Paese | Aperti prima | Paese | Aperti prima |
|---|---:|---|---:|
| IE | 0 | BG | 0 |
| GB | 2 | GR | 0 |
| DK | 0 | CY | 0 |
| FI | 1 | MT | 0 |
| SE | 6 | PT | 3 |
| AT | 9 | LU | 3 |
| PL | 11 | EE | 0 |
| CZ | 1 | LV | 0 |
| SK | 0 | LT | 0 |
| HU | 3 | HR | 0 |
| RO | 0 | SI | 0 |

## B — Università

La tabella registra il preflight effettuato con lo user agent PeoplePlacementBot. Un risultato 200 indica solo che il robots.txt è leggibile. Gli host con revisione incompleta restano incerti.

| Host | robots.txt | Evidenza sul formato o prossimo controllo |
|---|---:|---|
| praktika.ut.ee | 200 | Sitemap dedicata `internship_offers-sitemap.xml`, 142 URL. Consultati anche [manuale e condizioni](https://praktika.ut.ee/futulabi_kasutusjuhend/) e [informativa](https://praktika.ut.ee/andmekaitsetingimused/). |
| vilniustech.lt | 200 | Elenco HTML e dettaglio pubblico Citco. Il dettaglio serve HTML senza JobPosting. |
| career.tu-sofia.bg | 404 | Verifica fermata. La regola richiede un robots.txt leggibile. |
| jobboerse.aau.at | 200 | Due sitemap `wp-sitemap-posts-job-*.xml`. Dettaglio Kelag con JobPosting, datore dichiarato e luogo AT. [Impressum](https://jobboerse.aau.at/impressum/) consultato. |
| careercenter.uni-graz.at | 200 | [Portale HTML](https://careercenter.uni-graz.at/de/job-und-praktikaportal/). Da verificare formato del dettaglio e condizioni del portale. |
| biurokarier.p.lodz.pl | 200 | Le regole per PeoplePlacementBot vietano `/files/` e `/ajax/` salvo eccezioni esplicite. Da verificare i dettagli delle offerte. |
| biurokarier.uj.edu.pl | 200 | [Elenco pubblico HTML](https://biurokarier.uj.edu.pl/pl/oferty). Sitemap dichiarata su HTTP, percorso HTTPS da verificare. |
| kariery.uken.krakow.pl | 200 | Mappa WordPress di post generici, da verificare il percorso degli annunci. |
| kariera.euba.sk | 200 | Da verificare inventario pubblico e condizioni. |
| kariera.ucm.sk | 200 | Mappa WordPress di post ed eventi, da verificare il percorso degli annunci. |
| pkc.vscht.cz | 200 | Corpo vuoto. Da verificare inventario pubblico e condizioni. |
| career.auth.gr | 200 | `Crawl-delay: 10`. Da verificare inventario pubblico e condizioni. |
| career.uoa.gr | 200 | `Crawl-delay: 10` per il gruppo applicabile. Da verificare inventario pubblico e condizioni. |
| saidasprofissionais.iscsp.ulisboa.pt | 200 | Regole Drupal. Da verificare i percorsi effettivi delle offerte e le condizioni. |
| iccd.unwe.bg | 200 | Da verificare inventario pubblico e condizioni. |

### Candidati individuati

- AT, Kelag, **Praxissemester „Learning/Development“ bzw. „Diversity/Health“**. La scheda strutturata indica Klagenfurt, idoneità durante gli studi e scadenza 9 gennaio 2027. La vacancy compare anche nell'elenco ufficiale Kelag. Verifica della destinazione di candidatura pendente. [Università](https://jobboerse.aau.at/job/praxissemester-learning-development-bzw-diversity-health-all-genders-2/) · [Kelag](https://www.kelag.at/ueber-kelag/jobs.htm)
- AT, Infineon, **Industriepraktikum – HR Early Career Talent Support**, Villach, riferimento HRC1854805. Verifica del percorso di candidatura pendente. [Università](https://jobboerse.aau.at/en/job/industriepraktikum-hr-early-career-talent-support-w-m-div/)
- LT, Citco, **Internship Talent Acquisition Team**, Vilnius, scadenza 31 dicembre 2026 nel portale fonte. Il riferimento Oracle è 20485, il robots.txt del tenant restituisce 404 e la verifica automatizzata si ferma. [VILNIUS TECH](https://vilniustech.lt/studijos/karjera-ir-praktika/darbo-ir-praktikos-skelbimai/internship-talent-acquisition-team-citco/) · [Dettaglio KTU con la sede](https://wanted.ktu.edu/studentams-praktika-skelbimas/?id=4114)
- EE, Rocket Nova, **Curricular Internship – HR & Administration (Fully Remote, 9 months)**. Il portale mostra Estonia. Restano da verificare il luogo ammesso per il lavoro remoto e il percorso ufficiale di candidatura. [Università](https://praktika.ut.ee/en/internship-offers/)
- EE, Estonian Student Satellite, **Human Resources Intern (General)**. Escluso per natura del ruolo, descritto come «The role is voluntary and unpaid» e come ruolo da membro del team HR. [Scheda](https://praktika.ut.ee/en/internship_offers/human-resources-intern-general/)

Verifica preliminare, nessuna candidatura confermata secondo policy v2. I conteggi del CSV si riferiscono al censimento e non misurano candidabilità attuale. Le richieste diagnostiche non sono un benchmark di raccolta.

## C, A e D

Il CSV probe ha 876 righe e 551 valori host distinti, compreso un valore vuoto. Il CSV sitemap ha 81 host distinti, di cui 25 coincidono con gli host carriera o consentiti delle fonti già attive, normalizzando il prefisso www. Restano 56 host per la revisione di A. C e D sono da svolgere. Nessun ATS di D è stato aggiunto.

## C — Agenzie locali

Triage diagnostico delle sitemap con percorso di scheda e coppia di termini stage/HR. Le visite a termini e privacy via motore di ricerca sono fuori dalla telemetria. Il tempo HTTP cumulativo esclude le pause, mentre i tempi dell'adattatore le includono.

| Fonte | URL di scheda | Candidati da slug | GET / byte / s HTTP | Esito |
|---|---:|---:|---:|---|
| Randstad DK | 188 | 0 | 6 / 33.419 / 1,285 | Sitemap nazionale e varianti inglesi. Verifica termini del percorso pendente. |
| Randstad LU | 85 | 0 | 6 / 45.519 / 1,555 | Sitemap pubbliche e [condizioni locali](https://www.randstad.lu/conditions-generales/). |
| Randstad AT | 522 | 0 | 4 / 92.969 / 0,858 | Sitemap pubbliche. [Condizioni locali](https://www.randstad.at/nutzungsbestimmungen/) consultate. |
| Manpower LU | 125 | 0 | 3 / 19.084 / 3,212 | Indice Matador. Revisione termini pendente. |
| Manpower HR | 50 | 0 | 3 / 43.531 / 0,565 | Inventario EN, altra sitemap in redirect. Revisione termini pendente. |
| Manpower SI | 102 | 0 | 3 / 51.242 / 0,438 | Inventario EN, altra sitemap in redirect. Revisione termini pendente. |
| Manpower HU | 74 | 0 | 3 / 42.086 / 0,499 | Inventario EN, altra sitemap in redirect. Revisione termini pendente. |
| Adecco PT | 1.803 | 0 | 3 / 341.181 / 3,759 | Sottoindice portoghese. Revisione termini del percorso pendente. |
| Michael Page PT | 239 | 0 | 3 / 64.787 / 1,043 | Escluso dai [termini locali](https://www.michaelpage.pt/Termos-e-Condi%C3%A7%C3%B5es-Gerais), «exclusivamente para a sua utilização pessoal». |
| Grafton CZ | 64.575 | 10 | 35 / 21.076.779 / 12,963 | Escluso dai [termini locali](https://www.grafton.cz/cs/vseobecne-podminky), «není dovoleno stahovat nebo jinak kopírovat jakýkoli obsah» salvo uso personale o permesso esplicito. |
| Grafton SK | 7.020 | 7 | 8 / 4.870.266 / 2,916 | Escluso dai [termini locali §4.3](https://www.grafton.sk/sk/podmienky), «Automatizovaný zber informácií z Webovej stránky je zakázaný.» |
| Grafton PL | 1.718 | 3 | 4 / 724.073 / 2,005 | Escluso dai [termini locali §3.1](https://pl.grafton.com/pl/regulamin), «Kandydat nie jest uprawniony do korzystania z Witryny w innych celach.» |
| StaffPoint FI | 0 | 0 | 2 / 253.652 / 0,523 | Sitemap del sito senza dettagli riconosciuti dal filtro. |
| Uniflex SE | 196 | 1 | 2 / 35.533 / 0,532 | [Unico candidato](https://karriar.uniflex.se/jobs/8642377-nu-soker-vi-hr-student-for-praktik-till-varterminen) scaduto il 15 novembre. |

Randstad Polska è già abilitato in main. Nessuna duplicazione di fonte. Gli indici Grafton e Michael Page sono stati letti nel preflight prima di completare la revisione dei termini. La revisione ha poi fermato il passaggio ai dettagli. I candidati da slug includono falsi positivi e duplicati.

## A — Sitemap corporate e di piattaforma

Preflight dei 56 host residui. 51 robots HTTP 200, uno con redirect, uno HTTP 404 e tre esclusioni già documentate (Ryanair, SEB, Novartis). Le verifiche dei termini, dell'inventario e delle offerte per gli host residui restano da completare. Il Politecnico di Sofia conserva lo stop per robots 404.

Randstad PL, con Python 3.12, ha confermato 8 schede correnti (19 GET, 6.111.290 byte, 68,34 s). Sono osservazioni della fonte già attiva e non costituiscono un incremento del lotto.

JKS ha prodotto 9 candidati, 7 con scadenza futura nel JobPosting e 2 chiusi (20 GET, 1.754.714 byte, 38,41 s). Il controllo diretto ha confermato che tutte e sette le date visibili coincidono con il JobPosting live. Hjørring 155081 è stata esclusa dal perimetro perché si sovrappone alla posizione primavera 2027 più recente, 160962, nella stessa sede. Il replay filtrato ha confermato sei aperti e due chiusi (18 GET, 1.558.874 byte, 34,40 s). [Scheda](https://www.jks.dk/jobs/praktikant-til-hr-og-rekrutteringsopgaver-hos-jks-hjoerring-155081)

## B — Riesame dei quattro candidati

- Kelag (AT) ha una scheda pubblica con sede, requisiti studenteschi e scadenza futura, riscontrata anche presso il datore.
- Infineon (AT) espone il riferimento HRC1854805 e il requisito studentesco. L'effettiva scadenza resta da dimostrare.
- Rocket Nova (EE) espone la scadenza 17 dicembre, conferma convenzione universitaria e sede Estonia per il lavoro remoto. [Scheda di Tartu](https://praktika.ut.ee/en/internship_offers/curricular-internship-hr-administration-fully-remote-9-months/)
- Citco (LT) ha un annuncio universitario pubblico con scadenza 31 dicembre e sede Vilnius riscontrata su KTU. Il 404 sul robots di Oracle limita la verifica di quel tenant. Il livello richiesto per la pubblicazione è current listing. I quattro portali universitari non sono inclusi nella configurazione di raccolta di questa PR parziale.

## Simulazione del sottoinsieme BYD e JKS

Replay del finalizzatore con risposte live del 25 novembre e baseline ec2b201. 1.205 → 1.215 ID, zero persi, 644 → 652 stage aperti nel predicato della simulazione, DK 0 → 6 e HU 3 → 5, tutti gli altri paesi invariati. Otto current listing aggiunti, candidature dirette 51 → 51 e lead 366 → 366. Due altri ID sono schede chiuse. Le mansioni sono HR e i paesi di lavoro sono espliciti nel JobPosting. Nessun titolo escluso nella simulazione.

- [International HR Intern – Szeged](https://careers-hun.byd.com/jobs/8615703-international-hr-intern-szeged)
- [HRBP Intern – Szeged Vehicle Division](https://careers-hun.byd.com/jobs/8708153-hrbp-intern-szeged-vehicle-division)

- [Praktikant søges til vikar- og rekrutteringsbranchen hos JKS Randers](https://www.jks.dk/jobs/praktikant-soeges-til-vikar-og-rekrutteringsbranchen-hos-jks-randers-160605)
- [Praktikant søges til vikar- og rekrutteringsopgaver hos JKS Hobro – forår 2027](https://www.jks.dk/jobs/praktikant-soeges-til-vikar-og-rekrutteringsopgaver-hos-jks-hobro-foraar-2027-160534)
- [Praktikant til HR- og rekrutteringsopgaver hos JKS, Hjørring (forår 2027)](https://www.jks.dk/jobs/praktikant-til-hr-og-rekrutteringsopgaver-hos-jks-hjoerring-foraar-2027-160962)
- [Praktikant til HR, rekruttering, salg og markedsføring hos JKS Esbjerg -](https://www.jks.dk/jobs/praktikant-til-hr-rekruttering-salg-og-markedsfoering-hos-jks-esbjerg-160886)
- [Praktikanter til HR- og rekrutteringsopgaver søges til JKS i hele Danmark](https://www.jks.dk/jobs/praktikanter-til-hr-og-rekrutteringsopgaver-soeges-til-jks-i-hele-danmark-159170)
- [Studiepraktikant søges til HR- og rekrutteringsopgaver hos JKS i Odense](https://www.jks.dk/jobs/studiepraktikant-soeges-til-hr-og-rekrutteringsopgaver-hos-jks-i-odense-160782)

Nuovi ID chiusi, fuori dagli aperti simulati

- [Praktikant til HR- og rekrutteringsopgaver hos JKS i Hobro](https://www.jks.dk/jobs/praktikant-til-hr-og-rekrutteringsopgaver-hos-jks-i-hobro-151193)
- [Praktikant til HR- og rekrutteringsopgaver hos JKS i Hobro](https://www.jks.dk/jobs/praktikant-til-hr-og-rekrutteringsopgaver-hos-jks-i-hobro-151999)

Teamtailor verificato con l'adattatore già in uso per Grupo RAS. 2 candidati e 2 correnti, 6 GET, 18.511.329 byte, 10,93 s, pausa di 2 s. Stima del workflow 24m34s, ottenuta aggiungendo conservativamente il maggiore dei due budget (100 s, JKS) su shard distinti alla durata di 22m54s dell'[ultimo ciclo riuscito](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45684692063). La stima comprende soltanto BYD e JKS. D è rinviato.
