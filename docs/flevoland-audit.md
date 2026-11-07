# Flevoland — audit Issue #9

Controllo del 7 novembre 2026; rapporto generato 2026-11-07T17:24:11.698524+00:00.

## 1. Base e salvaguardia

Workflow 42394431912: test, 16 shard e pubblicazione completati con successo. Base: `1f28fb2` (pubblicazione successiva al merge Utrecht); include PR #7, #11, #12 e #13. Ramo: `feat/flevoland-expansion`.

Checkout originale accessibile in `/Users/dennis/Documents/ChatGPT/Internship/eu-hr-internships`, ramo `feat/flevoland-unverified-opportunities`: tutte le modifiche locali sono rimaste intatte. Confrontati i 33 datori locali e i candidati della Issue; non importato indiscriminatamente il lotto precedente. Riutilizzato il checkout Utrecht pulito per il nuovo ramo. Ispezionati anche gli elenchi worktree Git; nessun worktree eliminato.

## 2. Geografia CBS

Import eseguito con `scripts/import_province_geography.py --province-code PV24 --nuts-code NL23 --output data/flevoland-geography.json`. Tabelle ufficiali annuali 86247NED e 86312NED, riferimento 1 gennaio 2026: 6 comuni, 19 codici località distinti.
- Almere: Almere.
- Dronten: Biddinghuizen, Dronten, Swifterbant.
- Lelystad: Lelystad.
- Noordoostpolder: Bant, Creil, Emmeloord, Ens, Espel, Kraggenburg, Luttelgeest, Marknesse, Nagele, Rutten, Schokland, Tollebeek.
- Urk: Urk.
- Zeewolde: Zeewolde.

Il quadro geografico completo non implica un censimento completo dei datori.

## 3. Datori e fonti

19 datori identificati e configurati, 19 tentativi circoscritti. 18 nuove identità; riutilizzati `alfen` e `auto-alfen`, preservando gli URL di partenza esistenti. Nessuna stima di organico nuova: dimensioni ancora da verificare per tutti i 19 nel lotto provinciale. La presenza della sede non assegna automaticamente una vacancy a quella città.

Stati Factory: **0 completi, 10 parziali, 7 incompleti, 2 bloccati**. Nessuno zero-stage dichiarato sulla sola lettura di una pagina careers. I canali universali hanno limiti di 8 pagine / 24 richieste e profondità 1 per i nuovi datori; questa raccolta ha applicato un limite di 40 secondi per fonte. HLB ha un lettore di schede ufficiali con località etichettata; SMT è limitato alla vacancy candidata.

| Datore | Comune | Fonte | Stato inventario |
|---|---|---|---|
| Gemeente Almere | Almere | `auto-gemeente-almere` | blocked |
| Alfen | Almere | `auto-alfen` | incomplete |
| Provincie Flevoland | Lelystad | `auto-provincie-flevoland` | partial |
| Marfo | Lelystad | `auto-marfo` | partial |
| Farm Dairy | Lelystad | `auto-farm-dairy` | incomplete |
| Giant Europe | Lelystad | `auto-giant-europe` | incomplete |
| Meerpaal | Dronten | `auto-meerpaal` | partial |
| Gemeente Dronten | Dronten | `auto-gemeente-dronten` | incomplete |
| HLB Group | Dronten | `auto-hlb-group` | partial |
| SMT Netherlands | Noordoostpolder | `auto-smt-netherlands` | partial |
| Groothuisbouw | Noordoostpolder | `auto-groothuisbouw` | partial |
| Gemeente Noordoostpolder | Noordoostpolder | `auto-gemeente-noordoostpolder` | blocked |
| Sea Fresh | Urk | `auto-sea-fresh` | partial |
| Urker Zalmhuys | Urk | `auto-urker-zalmhuys` | incomplete |
| Neerlandia Urk | Urk | `auto-neerlandia-urk` | partial |
| Kramer Fish Group | Urk | `auto-kramer-fish-group` | incomplete |
| Van Amersfoort Racing | Zeewolde | `auto-van-amersfoort-racing` | partial |
| Royal Herkel | Zeewolde | `auto-royal-herkel` | partial |
| Gemeente Zeewolde | Zeewolde | `auto-gemeente-zeewolde` | incomplete |

## 4. Sette opportunità originali

**1 stage verificato**: [HLB Group — Stagiair Organisatiecultuur & HR](https://www.hlbbv.nl/nl/vacature/stageplek-hr/), Dronten; ultima verifica `2026-11-07T17:17:06.708255+00:00`. Elenco ufficiale con località Dronten, titolo della pagina specifica corrispondente, istruzioni CV/motivazione e mailto `personeel@hlbbv.nl` concordanti. Verifica di istruzioni pubblicate, non consegna email. Inventario di gruppo parziale. Requisiti linguistici non espliciti: inglese sufficiente **non dimostrato**.

- `flv-v01` **Gemeente Almere — blocked**: Official crawler cannot read robots.txt (HTTP 406). Cached official page names vacancy 391873, deadline 2026-11-10 and February 2027 intake, but no live same-vacancy application form established. Fonte: https://www.werkenbijalmere.nl/vacatures/stage-meewerkstage-team-recruitment-391873; controllo 2026-11-07T17:11:10.613808+00:00.
- `flv-v02` **Provincie Flevoland — unverified**: Official page and rendered same-ID application entry 1357003 observed. Enabled first-step personal-data fields and title match; no submission or upload step attempted. Deadline conflict persists (header 30 November / body 29 November); vacancy-specific city is not explicit, so no HQ-based workplace inferred. Fonte: https://flevoland.heeft-vacatures.com/vacatures/stagiair-hr-van-werving-tot-onboarding-1357003/; controllo 2026-11-07T17:11:10.613808+00:00.
- `flv-v03` **SMT Netherlands — unverified**: Current official list and HR vacancy observed. Visible email address differs from mailto destination. Embedded form carries referer_title Service Planning Officer although queried_id is 2305. Existing strict official-email check fails; no generic form used as substitute. Fonte: https://werkenbijsmt.nl/vacature/hr-stagiaire/; controllo 2026-11-07T17:11:10.613808+00:00.
- `flv-v04` **Van Amersfoort Racing — past-intake**: Official vacancy still describes September 2026 start and requires Dutch and English; current career list does not establish a new intake. Fonte: https://www.vanamersfoortracing.nl/careers/hr-stagiair/; controllo 2026-11-07T17:11:10.613808+00:00.
- `flv-v05` **Meerpaal — expired**: Official page requests application before 15 October 2026 despite mentioning possible 2027 internships. No renewed deadline established. Fonte: https://www.meerpaal.nl/vacatures/stagiair-hr; controllo 2026-11-07T17:11:10.613808+00:00.
- `flv-v06` **Marfo — unverified**: Secondary research candidate absent from the two observed official Marfo listings. Official inventory remains partial: absence cannot establish closure, and no primary HR vacancy/application found. Fonte: https://baanlens.nl/vacature/marfo-hbo-hr-bedrijfskunde-onderzoeksstage-56250a5; controllo 2026-11-07T17:11:10.613808+00:00.

Per la Provincia il 29 novembre è soltanto una data prudenziale di pianificazione, non una risoluzione del conflitto ufficiale. La pagina sulle sedi descrive più possibilità di lavoro: non prova una città specifica per questo stage. Il primo passo del modulo 1357003 è stato renderizzato e verificato senza compilazione, senza avanzare al caricamento di documenti e senza inviare dati.

Per SMT l’olandese scritto/parlato è esplicito; per VAR olandese e inglese sono espliciti sul vecchio intake. Francese, inglese, olandese e altre lingue rimangono distinti in `workplace_requirements_by_language`; le affermazioni secondarie Marfo sono separate dai requisiti osservati. La lingua olandese della pagina HLB non è un requisito lavorativo.

## 5. Factory e provenienza

Usati `handoff`, `summary`, `checkpoint` e `checkpoint --resume`. Le 26 affermazioni preliminari (19 datori + 7 opportunità) sono conservate in una coda inerte. La Factory genera hash propri: `docs/flevoland-candidate-map.json` li collega agli ID originali. Timestamp normalizzati con fuso; confidence categorica convertita esplicitamente in numero; campi fuori schema conservati nei file originali. Nessun annuncio promosso dalla sola importazione.

Riproduzione: `python3 scripts/provincial_factory.py handoff flevoland --input docs/flevoland-factory-handoff.json`, poi `summary flevoland` e `checkpoint flevoland`. La coda e i checkpoint runtime restano in `.staging`; il riepilogo compatto è versionato in `docs/flevoland-factory-summary.txt`.

## 6. Differenze rispetto a main

Tutti i **322 record pubblicati** conservano esattamente ID e campi, inclusi Utrecht e precedenti verifiche. Aggiunti soltanto HLB verificato e SMT non verificato al catalogo (324 totali). Gli altri cinque candidati restano fuori dal catalogo e nella revisione. ID datori/fonti esistenti preservati; sola identità esistente estesa: Alfen. Aggiornati report globali derivati e copertura Flevoland; mantenuti i report delle altre province. Nessuna modifica a `collector/verification.py`, riconciliazione #12 o policy #11; #14 intake non ampliata. Aggiunta pagina Flevoland e link di navigazione; footer adattato per evitare overflow mobile con il link aggiuntivo.

## 7. Verifiche

- Python: 223 test superati, compresi geografia, schema Factory e regressioni esistenti.
- Frontend: 21 test superati.
- Classificazione: 64 esempi, 0 falsi positivi e 0 falsi negativi nel set di regressione.
- Catalogo e registro globale validati; integrazione provinciale idempotente.
- `finalize()` provato su record nuovo non verificato, mancata osservazione parziale, successiva prova verificata e riapparizione con alias: ID e prima scoperta conservati; nessuna promozione senza prova.
- Build statica eseguita; controllo Chromium desktop/mobile su cinque province e filtri comuni documentato in `docs/flevoland-ui-verification.json`.
- CI della nuova PR: controllare il risultato finale collegato alla PR; nessuna esecuzione quotidiana completa avviata da questo lavoro.

## 8. Limiti e seguito

Risolvere accesso Almere e Noordoostpolder senza aggiramenti; ottenere candidatura Almere prima della scadenza indicata. Chiarire data e sede dello stage provinciale; riconciliare i dati di candidatura SMT. Accertare eventuali nuove intake VAR/Meerpaal e una vacancy primaria Marfo. Completare inventari e dimensioni datori prima di dichiarare copertura esaustiva. Nessuna candidatura, messaggio a terzi, sottoagente, servizio a pagamento, merge, deploy manuale o chiusura Issue #9.
