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
