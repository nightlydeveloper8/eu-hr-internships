# Stato di ripresa — People Placement

## 11 novembre 2026 — Issue #23, diagnosi upstream e correzione proposta (PR in preparazione)

**Baseline:** `main` `0de282c597` con PR #25 integrata; CI di main verde. La raccolta completa successiva al merge **non è ancora osservata**, e il catalogo ordinario dell'11 novembre non è stato aggiornato dalla sola CI. PR #20 Drenthe e PR #26 audit rimangono indipendenti; non sono state modificate.

Nella raccolta ordinaria del 10 novembre il gate `PEOPLE_PLACEMENT_DYNAMIC_ATS=pilot-v1` era attivo, ma i tre source ID pilota non hanno prodotto candidati HR nuovi: `matching=0` nei rispettivi report. La `matching_hr_positions=1` del report aziendale comprende il catalogo **storico**, non è una nuova verifica. Fonti: [run #42774047883](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42774047883), `data/coverage.json`, `data/catalog.json` e [audit Issue #23](https://github.com/nightlydeveloper8/eu-hr-internships/issues/23#issuecomment-6794406970).

**Tre casi distinti da non confondere:**
- Bentacera, `Traineeship Salarisprofessional` a Leeuwarden: la pagina ufficiale [segnala esplicitamente la vacancy non più disponibile](https://www.werkenbijbentacera.nl/vacatures/traineeship-salarisprofessional-leeuwarden-284). È un traineeship, non uno stage curricolare. La vecchia scheda non va ripromossa. Un inventory parziale non può provare chiusure *per assenza*, ma una pagina fresca dell'identica URL che nomina la posizione e ne dichiara la chiusura può farlo.
- OPACKGROUP, `Stage Employer Branding` a Giessen: [pagina ufficiale del gruppo](https://werkenbijopackgroup.nl/vacatures/stage-employer-branding-giessen-385), non prova un'opportunità locale di Oosterwolde Plastic Industrie. Il vecchio source ID `auto-oosterwolde-plastic-industrie-b-v` non deve aggirare i controlli di hiringOrganization, né attribuire arbitrariamente la sede Giessen all'azienda di Oosterwolde. Richiede revisione distinta dell'ownership, non una scorciatoia per aumentare i verified.
- Achmea, `Hbo Meewerkstagiair HR Young Talent Recruitment`: [pagina ufficiale](https://www.werkenbijachmea.nl/vacatures/hbo-meewerkstagiair-hr-young-talent-recruitment-apeldoorn-a0wqs00000e0dr7iaj), stage HBO ad Apeldoorn, **lingua dichiarata olandese**. Nel ciclo precedente l'inventario aveva 169 URL pendenti; il pilot aveva già escluso CAPTCHA/host non approvato. Questi vincoli rimangono senza bypass. Nessuna sufficienza dell'inglese inferita.

**Intervento reversibile proposto (nuovo ramo, non produzione):**
1. Passare `known_job_titles` dal catalogo alla scansione dei soli URL storici non chiusi. Riconoscere soltanto un messaggio di chiusura ufficiale fresco, sulla **stessa URL non reindirizzata**, che **nomina esattamente** il titolo precedente. Il solo cache, pagine generiche, assenze, redirect e titoli diversi non chiudono nulla. Riusa `verified_closed_urls` e la logica centrale di `finalize`, senza modificare policy v2 o inventari completi.
2. Aggiungere ai rapporti conteggi `structured_identity_mismatches`, `explicit_known_closures` e `candidate_filter_reasons` (ownership respinta, non-stage/HR, candidato HR senza paese). Questi sono numeri diagnostici, **non** nuove candidature.
3. Aggiungere regressioni offline su pagina chiusa stessa vacancy, falsi match, redirect, cache, gruppo diverso, geografia ignota, preservazione ID e idempotenza. La CI e i risultati vanno dichiarati separatamente. La prova live di nuove candidature resta necessaria e non è implicata dai test.

**Limiti e costi:** nessun collector o source ID aggiunto, nessuna modifica ai tre host, al toggle, ai budget, alla matrice dei 16 shard o agli stati di produzione; nessun merge, rollout, invio candidature, nuova raccolta massiva o servizio a pagamento. Il delta open/verified atteso da questa PR è **non dimostrato** e va misurato dopo integrazione *eventualmente autorizzata* e un normale run. Il primo ciclo dopo PR #25 resta il gate di produzione da verificare. La Issue #18 rimane il successivo lavoro di copertura riutilizzabile.

## 11 novembre 2026 — correzione del test che blocca la raccolta

Obiettivo permanente: più stage HR distinti e candidabili da fonti ufficiali,
aggiornati ogni giorno; prima copertura dei Paesi Bassi, poi dell'Europa.

- Main di riferimento: `0e73e9a7b26d7c674110beb50697fd29a8e2fdf1`.
- [Raccolta automatica fallita](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42978923468)
  dell'11 novembre alle 08:21 Bruxelles: il test intake imponeva 324 record,
  mentre la raccolta ordinaria precedente aveva portato il catalogo a 327.
  Collect e publish saltati; errore riprodotto offline con Python 3.12.
- [Ultima raccolta riuscita](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42774047883):
  10 novembre, 18 job riusciti. Catalogo aggiornato alle 08:28 Bruxelles:
  327 ID univoci, 22 open, 298 unverified, 7 closed; tutti i 324 ID precedenti
  conservati. Sono stati storici, non nuove verifiche live dell'11 novembre.
- Correzione limitata a `tests/test_intake.py`: eliminato il conteggio storico
  fisso, mantenuti controlli su identità, campi, ownership, policy e review blocks;
  aggiunta regressione con un record sintetico in più e replay alla data del catalogo.
  Nessuna modifica a collector, catalogo, workflow, host, budget o gate ATS.
- Lavoro isolato dal checkout storico con WIP. Accesso Git dalla shell non
  disponibile; file aggiornati recuperati tramite connessione GitHub e confrontati
  con i blob di main prima della consegna. Nessuna raccolta completa manuale.
- Validazione con Python 3.12: 287 test Python (inclusi 12 intake), 21 frontend,
  64 esempi di classificazione senza errori, validazione catalogo e build riusciti.
  Tutti i blob locali di main coincidono con quelli remoti salvo il test modificato.
  CI riportata nella PR; non confondere test con nuove opportunità.
- Consegna tramite PR circoscritta, senza merge o rollout. La produzione resta
  bloccata dal vecchio test finché la correzione non viene integrata.

Prossimo passo: revisionare e integrare la PR solo con autorizzazione specifica,
poi verificare il successivo ciclo automatico (nessun controllo futuro AI configurato).
Completare quindi le evidenze su beneficio e costi Dynamic ATS della Issue #23;
la Issue #18 resta il lavoro di miglioramento della copertura. PR #20 Drenthe
separata, non integrata. Per la mappatura riprendere i checkpoint territoriali
senza dichiarare completa una provincia sulla base dei soli datori censiti.
