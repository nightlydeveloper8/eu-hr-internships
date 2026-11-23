# Dai listing EURES alla candidatura diretta

Rilevazione del 22 novembre 2026. Graduatoria sul catalogo pubblicato in `f606443`. Simulazione sulla base aggiornata `d69c664`.

## Cosa mostrano gli audit precedenti

- L’audit ha classificato 367 lead. Su 176 mancava il modulo specifico, di cui 87 su Adecco FR.
- I due piloti Adecco hanno trovato due posting e zero moduli associati. Il percorso osservato conduceva all’area CV/account.
- Fra 57 prove scadute o invalide c’erano 53 EURES. Rivedere il listing pubblico può ripristinarne la freschezza senza provare una candidatura diretta.
- Nei 38 errori di ID, zero equivalenze provate, un ID diverso (Landal) e 37 casi con dati insufficienti. Il confronto esatto resta in uso.
- Danone ha mostrato due CTA verso login. Per 30 lead Amazon il robots rispondeva 403. Gli audit hanno prodotto zero conversioni.

[Audit dei lead](lead-conversion-audit-2026-11-21.md) · [Audit degli ID](lead-application-id-2026-11-21.md)

## Graduatoria

Dei 366 listing EURES aperti, 226 hanno il datore omesso. I 140 nominativi sono distribuiti fra 78 chiavi. La tabella copre 92 listing e 30 chiavi. Usa `collector.public_sources.employer_key`, la stessa normalizzazione della riconciliazione EURES, con pari merito risolti per chiave in ordine lessicografico. BBL e OFCL restano due chiavi del feed. Eventuali alias di gruppo richiedono prova per la singola vacancy.

Le classi sono **a** (ATS pubblico e match univoco con prova v2), **b** (careers ufficiale, ATS della vacancy non leggibile o non individuato), **c** (vacancy osservata solo via servizio pubblico, agenzia o mirror), **d** (accesso bloccato da robots o dalla risposta del server). **Non dimostrato** indica che le quattro classi non descrivono con certezza l’esito, ad esempio quando un ATS è leggibile e il match o il modulo resta incerto.

I costi sono GET tentate, byte ricevuti e somma dei secondi dei controlli diretti per datore. Contano robots, risposte di errore, verifiche EURES puntuali e staging. I motori di ricerca non espongono questi costi. I redirect sono indicati dove hanno impedito la verifica. Le risposte erano limitate a 1,5 MB nel campione diagnostico.

| # | Datore | EURES | Paesi | Esito | Evidenza | GET | Byte | s |
|---:|---|---:|---|---|---|---:|---:|---:|
| 1 | [GI GROUP S.P.A.](https://it.gigroupholding.com/entra-nel-nostro-team/offerte-lavoro/) | 27 | IT | b | Careers interno letto. I 27 titoli EURES sono generici. Corrispondenza per sede e posting **non dimostrata**. | 2 | 144.192 | 1,765 |
| 2 | [VITALIANS](https://application.mytalentplug.com/jobs/34324cc9-a6bf-4087-9aeb-c54625e028cd) | 7 | FR | d | MyTalentPlug espone il posting `34324cc9-a6bf-4087-9aeb-c54625e028cd` per l’agenzia Aprojob di Lyon 7e. Il robots del tenant ha restituito HTML. Modulo e termini **non dimostrati**. | 1 | 452 | 0,193 |
| 3 | [Robert Bosch GmbH](https://jobs.bosch.de/job/Pflichtpraktikum-im-Bereich-International-Human-Resources-Abstatt-bei-Stuttgart?id=d7c654bd-a8af-4a26-9dc4-17b126328a8b) | 5 | DE | non dimostrato | Bosch espone `REF299715K` e un link SmartRecruiters. L’annuncio di Abstatt ha un titolo simile. Identità e modulo per il preciso record EURES **non dimostrati**. | 2 | 175.841 | 0,880 |
| 4 | [ADECCO](https://careers.adeccogroup.com/fr/emploi/clermont-ferrand/stagiaire-charge-de-recrutement-h-f/26094/100751045072) | 4 | BE, FR | non dimostrato | ATS Radancy, posting di Clermont-Ferrand `100751045072`. Il pilota storico su due altri posting è terminato nell’area CV/account. Nessun match o modulo provato in questo lotto. | 2 | 89.428 | 1,731 |
| 5 | [BOBST MEX SA](https://jobs.bobst.com/Vacancies/7638/Description/3) | 4 | CH | d | ATS umantis. La scheda campionata `7638`, riferita al 2025, risponde 403. I quattro record attuali e il loro percorso restano **non dimostrati**. | 2 | 18.122 | 0,955 |
| 6 | [FERCHAU GmbH Niederlassung Rosenheim](https://touch.ferchau.com/de/de/job/414187/praktikant-im-bereich-rekrutierung) | 4 | DE | d | Rosenheim e requisizione `414187` nella scheda ufficiale e nel riferimento BA della copia EURES. Lo stesso ID compare nella CTA pubblicata, che risponde HTTP 401. | 4 | 421.059 | 2,934 |
| 7 | [NOEL FRANKLIN](https://www.noelfranklin.com/join-the-franklins) | 3 | BE | b | Pagina interna Join the Franklins. Nessun inventario ATS interno leggibile nella pagina campionata e nessun ID ufficiale per i tre record dimostrato. | 2 | 39.453 | 1,404 |
| 8 | [Teoxane SA](https://careers.teoxane.com/) | 3 | CH | non dimostrato | Portale ufficiale SuccessFactors letto. La posizione RH L&D compare sui mirror. ID ufficiale attuale e modulo specifico **non dimostrati**. | 2 | 73.655 | 1,004 |
| 9 | [AERTSSEN GROUP NV](https://jobs.aertssen.be/vacatures/detail/?id=2634&title=stagiair-hr-stabroek) | 2 | BE | d | Schede ufficiali `2634` e `2455`, entrambe Stabroek. VDAB conferma la referenza `V-2634`. Il robots dell’host HR Organizer della CTA `2634` risponde 403. Nessun GET al modulo. | 6 | 105.536 | 3,474 |
| 10 | [AUMOVIO SE Haupverwaltung](https://jobs.smartrecruiters.com/Aumovio/744000150669639-praktikum-hr-talent-acquisition) | 2 | DE | non dimostrato | SmartRecruiters `744000150669639` è la pista per Regensburg. `REF81997L` sul portale AUMOVIO riporta Karben, mentre EURES riporta Regensburg. Il percorso verificato e l’identità del secondo record restano **non dimostrati**. | 2 | 174.482 | 0,843 |
| 11 | [Bechtle AG](https://jobs.bechtle.com/go/Alle-Jobs/866002/) | 2 | DE | non dimostrato | Portale ATS ufficiale leggibile. I titoli candidati compaiono fuori dal portale. ID e modulo corrispondenti **non dimostrati**. | 2 | 108.610 | 0,964 |
| 12 | [Bundesamt für Bauten und Logistik BBL](https://jobs.admin.ch/) | 2 | CH | non dimostrato | Portale federale ufficiale con redirect di lingua. I due titoli BBL potrebbero essere collegati alla scheda OFCL in francese. Equivalenza e percorso di candidatura **non dimostrati**. | 2 | 164 | 0,895 |
| 13 | [Direktion für Inneres und Justiz des Kantons Bern](https://www.jobs.apps.be.ch/offene-stellen/praktikum-im-hr-recruiting/e586ad50-b6f4-421e-bb34-ae0638ef9b97) | 2 | CH | non dimostrato | Scheda cantonale identificata da `e586ad50-b6f4-421e-bb34-ae0638ef9b97`. Due ID EURES con stesso titolo e sede. La CTA conduce a un altro host, con timeout su robots. | 5 | 143.190 | 11,180 |
| 14 | EVENTIM Benelux | 2 | NL | non dimostrato | Recruitee `2813674`, modulo v2 leggibile. Il testo dei due dettagli EURES rimanda allo stesso posting. I termini del portale richiedono l’accordo preventivo per creare link. Escluso. | 15 | 1.714.012 | 5,808 |
| 15 | [Integrierte Psychiatrie Winterthur – Zürcher Unterland ipw](https://www.ipw.ch/) | 2 | CH | d | Il dominio canonico ha un robots leggibile, ma risponde 403 sulla pagina campionata. Match ufficiale **non dimostrato**. | 3 | 22.692 | 0,843 |
| 16 | [Office fédéral constructions et logistique OFCL](https://jobs.admin.ch/postes-vacants/Stagiaire-de-haute-cole-en-gestion-des-RH/75cb9cbd-864f-460d-bbd0-15c90f34cf35) | 2 | CH | non dimostrato | Scheda federale `75cb9cbd-864f-460d-bbd0-15c90f34cf35`. Due ID EURES con stesso titolo e area. Percorso applicativo e corrispondenza uno-a-uno **non dimostrati**. | 2 | 85.133 | 1,195 |
| 17 | [OK Job SA](https://www.okjob.ch/) | 2 | CH | c | Sito ufficiale dell’agenzia OK Job. Il ruolo emerge dai portali di lavoro. Nella pagina ufficiale campionata, posting e percorso specifico **non dimostrati**. | 2 | 537.611 | 0,887 |
| 18 | [Spital Muri](https://www.spital-muri.ch/jobs/stellenangebote.html/725) | 2 | CH | b | Pagina ufficiale delle posizioni. Gli annunci da 12 mesi sui portali esterni non hanno prodotto un ATS ufficiale leggibile per la stessa vacancy nel campione. | 2 | 49.505 | 0,734 |
| 19 | [UCC COFFEE SWITZERLAND AG](https://ucc-europe.com/de/careers/schweiz/) | 2 | CH | b | Pagina Careers Switzerland del gruppo. L’annuncio HR & Marketing compare su jobs.ch. ID e candidatura sul canale ufficiale **non dimostrati**. | 2 | 138.067 | 0,973 |
| 20 | [Vigier Management AG](https://vigier-bewerber.talent-soft.com/stelle/stelle-hr-praktikant-in_1834.aspx) | 2 | CH | non dimostrato | Talentsoft `2026-1834` mostra il ruolo a Lyss. Esiste anche una scheda storica `1805`. Attribuzione dei due ID EURES e modulo same-ID **non dimostrati**. | 2 | 30.233 | 1,188 |
| 21 | [Würzburger Versorgungs- und Verkehrs-GmbH](https://wvv.softgarden.io/job/68850200/Praktikant-im-Bereich-Arbeitgebermarketing-m-w-d-?jobDbPVId=291110715&l=de) | 2 | DE | non dimostrato | Softgarden `68850200` e `59125143` corrispondono ai titoli e alla sede. La CTA verificata per `68850200` conduce a una scelta applicativa con redirect di lingua. Modulo finale e termini **non dimostrati**. | 8 | 66.846 | 3,306 |
| 22 | [Actief Construct Torhout](https://www.actief.be/) | 1 | BE | c | L’annuncio è rintracciabile su VDAB a Zedelgem. Il sito dell’agenzia ha risposto con redirect di lingua. Canale interno specifico **non dimostrato**. | 2 | 186 | 0,853 |
| 23 | [Adecco Medical](https://theadeccogroup-career.talent-soft.com/Pages/Offre/detailoffre.aspx?LCID=1036&idOffre=19630&idOrigine=502&offerReference=AMS+BLOC+ORLEANS+-19630) | 1 | FR | non dimostrato | Talentsoft `19630` a Orléans rimanda al portale generale. Sono indicizzate più offerte simili in città diverse. Identità e candidatura specifica **non dimostrate**. | 2 | 118 | 0,890 |
| 24 | [Airbus Defence and Space GmbH](https://ag.wd3.myworkdayjobs.com/en-US/Airbus/job/Intern--D---M---W----Talent---Executive-Management_JR10434906) | 1 | DE | non dimostrato | Workday `JR10434906`, Ottobrunn/Taufkirchen, e riferimento BA `16947-981319511-S`. La GET al tenant ha restituito una pagina senza posting leggibile in HTML. Form e accesso senza account **non dimostrati**. | 2 | 16.878 | 1,186 |
| 25 | [Alte Schmiede Steak Burger](https://www.make-it-in-germany.com/de/arbeiten-in-deutschland/jobboerse/job/job-10001-1003922193-S) | 1 | DE | c | La scheda della Bundesagentur ripubblicata da Make it in Germany riporta `10001-1003922193-S`. Careers o ATS ufficiale del ristorante **non dimostrato**. | 0 | 0 | 0,000 |
| 26 | [Amac](https://werkenbijamac.nl/o/hr-stagiair-hbo) | 1 | NL | a | Recruitee `2828451`, Utrecht, stesso testo e stessa sede del dettaglio EURES. Feed, vacancy e modulo con lo stesso ID. Fonte disabilitata con hold. | 12 | 3.714.850 | 5,080 |
| 27 | [AMBASSADE DES ETATS-UNIS A PARIS](https://fr.usembassy.gov/jobs/) | 1 | FR | d | Il robots del dominio dell’Ambasciata risponde HTTP 403. Il posting EURES è visibile su intermediari. Percorso ufficiale **non dimostrato**. | 1 | 659.508 | 0,764 |
| 28 | [Amplifon AG](https://careers.amplifon.com/de/sites/CX_1/jobs) | 1 | CH | non dimostrato | Portale Amplifon/Oracle individuato. Il robots del portale canonico risponde con un redirect a una pagina di errore, fermato nel campione. Posting ufficiale **non dimostrato**. | 1 | 341 | 0,287 |
| 29 | [ANDROS GLOBAL SERVICES](https://www.andros.fr/) | 1 | FR | b | Sito del datore letto fino al limite della risposta. Ruolo a Biars-sur-Cère ripubblicato fuori dal sito. ATS ufficiale e posting **non dimostrati**. | 2 | 1.500.171 | 1,764 |
| 30 | [Assisteal formation](https://www.assisteal.fr/) | 1 | FR | b | Pagina Recrutement ufficiale. L’annuncio pubblico riguarda il coordinamento di stage. Che sia esso stesso uno stage per studenti è **non dimostrato**. | 4 | 286.539 | 5,137 |

Rilevazione totale **96 GET / 10.316.874 byte / 59,117 secondi-datore**.
Solo Amac ha restituito una conversione ammissibile. Lo staging del collector costa **4 GET / 1.852.861 byte / 1,799 s per conversione** su 53 posting letti con un solo match HR. Per gli altri datori il costo per conversione è **non dimostrato** perché il denominatore è zero. Un nuovo tentativo per Andros, OK Job o Adecco richiede prima un riferimento ufficiale preciso. Il precedente ciclo Adecco ha speso 217 GET / 19.528.306 byte / 117,75 s con zero prove dirette. [Audit dei lead](lead-conversion-audit-2026-11-21.md)

## Amac in staging

- EURES `556f17c88258233a2fa1` e posting Amac `2828451` descrivono lo stesso tirocinio HR a Utrecht, Amac HQ The Wall, Proostwetering 13, €420–500 al mese. Il confronto trova una sequenza identica di 193 caratteri fra descrizione EURES e feed, oltre alle stesse mansioni e al titolo del posting nel corpo EURES. C’è un solo match HR nell’inventario Amac. [Scheda EURES](https://europa.eu/eures/portal/jv-se/jv-details/NjBhZTRlNTctZmQ3Ni0wODhhLWUwNjMtNjg5M2IyMGFhM2M1IDQy?lang=en) · [Dettaglio EURES](https://europa.eu/eures/api/jv-searchengine/public/jv/id/NjBhZTRlNTctZmQ3Ni0wODhhLWUwNjMtNjg5M2IyMGFhM2M1IDQy?requestLang=en&preferredLang=en)
- Il feed XML pubblica il link al modulo. Feed, JSON-LD della vacancy e JSON-LD del modulo riportano tutti `2828451`. Il collector ha verificato campi visibili e abilitati e registrato `official-recruitee-same-posting-visible-form` alle 12:49 CET. [XML](https://werkenbijamac.nl/api/feeds/offers.xml) · [Vacancy](https://werkenbijamac.nl/o/hr-stagiair-hbo) · [Modulo](https://werkenbijamac.nl/o/hr-stagiair-hbo/c/new)
- Il robots del tenant consente i tre percorsi. Tellent documenta l’eccezione all’autenticazione per il feed XML pubblico. La privacy Amac disciplina il trattamento delle candidature. Nei testi accessibili non è emersa una restrizione alle GET circoscritte. Le condizioni commerciali Amac hanno restituito 429. Una licenza generale di ripubblicazione è **non dimostrata**. [Robots](https://werkenbijamac.nl/robots.txt) · [Tellent](https://recruitee.com/terms) · [Autenticazione e feed XML](https://docs.recruitee.com/reference/authentication-1) · [Privacy Amac](https://www.amac.nl/privacy-policy)
- Il registro contiene una sola coppia revisionata, `2828451` → URL EURES, e la usa solo dopo verifica dell’applicazione. In finalizzazione ho simulato anche una copia EURES più recente nello stesso ciclo. La precedenza della scheda del datore scatta con un solo candidato diretto verificato e collegato all’alias pubblico. Resta l’ID canonico `556f17c88258233a2fa1`; l’URL e il posting EURES e l’ID generato per il posting Amac `5c164e513cee70716d9f` entrano in `identity_aliases`.

## Simulazione finale

| Metrica | Prima | Dopo |
|---|---:|---:|
| ID canonici distinti | 926 | 926 |
| ID persi | 0 | 0 |
| Stage aperti verificati | 422 | 422 |
| Candidature dirette verificate | 52 | 53 |
| Stage aperti con fonte primaria EURES | 365 | 364 |
| Collector attivi | 1.937 | 1.937 |

La base aggiornata conta già la conversione Watson Farley & Williams. La diminuzione del conteggio con EURES come fonte primaria corrisponde allo stesso stage Amac ora attribuito al datore nel replay. I file pubblicati dal bot non sono stati modificati.

## Proposta di attivazione

Amac per prima, dopo revisione e una nuova verifica same-ID. `recruitee-amac-nl` è in `enabled: false` e il datore ha `collection_activation_hold: true`. Per WVV servono un modulo utilizzabile per ciascun ID e la verifica dei termini. Per EVENTIM servono chiarimenti sui termini e la gestione della doppia copia EURES con zero ID persi.
