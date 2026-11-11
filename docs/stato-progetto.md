# Stato di ripresa — People Placement

## 11 novembre 2026 — audit dopo PR #25: produzione e Dynamic ATS

**Stato di produzione distinto dalla CI:**
- [PR #25](https://github.com/nightlydeveloper8/eu-hr-internships/pull/25) **merged** il 2026-11-11 11:08:19Z, commit `0de282c597be00147792383bd596c761d5cac85f`; la [CI di `main` #43009433333](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43009433333) è **success**.
- L'ultima [raccolta completa riuscita #42774047883](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42774047883) resta quella del **10 novembre**, con 18 job riusciti e catalogo di **327 ID**: **22 open, 298 unverified, 7 closed** (stati storici, non osservazioni live dell'11).
- Il [run ordinario dell'11 novembre #42978923468](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42978923468) era fallito prima dei job collect/publish per il test a conteggio fisso; la correzione ora è integrata, ma **non c'è ancora un nuovo run di produzione riuscito dopo il merge**. Lo schedule è `17 6 * * *` UTC; GitHub può ritardarlo. La CI non prova l'aggiornamento di catalogo e sito.
- [PR #20 Drenthe](https://github.com/nightlydeveloper8/eu-hr-internships/pull/20) rimane **draft, non mergiata**; nessuna sua modifica è stata toccata in questo audit.

**Pilot Dynamic ATS: prova di esecuzione ordinaria del 10 novembre.** I log di collect per shard 7, 2 e 8 attestano `PEOPLE_PLACEMENT_DYNAMIC_ATS=pilot-v1` nell'ambiente GitHub Actions. Dunque il pilot **era già abilitato in quel run**; non serve duplicarne l'attivazione. La variabile corrente non è stata letta direttamente via Settings. Il confronto con la [Issue #23](https://github.com/nightlydeveloper8/eu-hr-internships/issues/23#issuecomment-6794406970) è:

| Fonte | Record ispezionati | HR match nuovi nel run | Stato | Pagine pendenti | Sedi irrisolte | Richieste | Durata fonte |
|---|---:|---:|---|---:|---:|---:|---:|
| `auto-bentacera` | 34 | 0 | partial | 0 | 1 | 24 | 13,28 s |
| `auto-oosterwolde-plastic-industrie-b-v` | 2 | 0 | partial | 0 | 2 | 33 | 24,51 s |
| `auto-centraal-beheer-achmea` | 3 | 0 | partial | 169 | 0 | 71 | 49,69 s |

- **Zero rendering di verifica dinamica osservati** per le tre fonti nel run. Nei report non sono presenti eventi `dynamic_ats` delle tre fonti, perché nessuna posizione candidata è arrivata a `verify_vacancy`; `matching_hr_positions=1` nel report aziendale comprende il **catalogo storico conservato**, non una nuova posizione letta nel ciclo.
- Le posizioni pilota del catalogo (Bentacera `985543752c20a8abaeba`, OPACK `994018cb6659595e818f`, Achmea `e83537f80a3c4be51eae`) sono ancora **unverified**; gli ultimi avvistamenti storici risalgono rispettivamente al 9, 7 e 7 novembre. La prova live circoscritta 8 novembre (2/3 candidate verificabili con rendering) non equivale a una promozione nel catalogo del 10.
- Per OPACK, la posizione storica è etichettata OPACKGROUP a **Giessen** sotto la fonte denominata Oosterwolde Plastic Industrie: **ownership/sede da verificare**, non attribuire automaticamente il gruppo alla sede. Achmea resta fuori dalla promozione per CAPTCHA e host di candidatura non autorizzato.
- Costo delle tre fonti nel ciclo ordinario: **128 richieste**, **87,48 s** come somma delle durate delle fonti (lavori concorrenti, non wall-clock), nessun rendering dynamic verificato; costo monetario dei runner non misurato. Nessun servizio a pagamento introdotto nell'audit.

**Primo punto incompleto da riprendere:** osservare il primo ciclo schedulato dopo il merge PR #25 e la pubblicazione di catalogo/sito. Poi diagnosticare in modo limitato i tre percorsi `known_job_urls → Crawler → ownership/classificazione/paese → verify_vacancy`, riusando le prove e i budget del pilot. Correggere solo cause riutilizzabili dimostrate, mantenendo policy v2, robots, allowed hosts, ID e niente candidature inviate. Documentare due cicli, delta open/verified, richieste, rendering, tempi, errori e freschezza prima di qualsiasi espansione. [Issue #18](https://github.com/nightlydeveloper8/eu-hr-internships/issues/18) rimane aperta per la copertura più ampia.

La mappatura OVI-01–17 resta una **coda nominale nella chat**, con 171 schede OVI-14 non riconciliate in gruppi unici: non è integrata né prova stage verificati in produzione. Nessuna modifica a codice, sorgenti o workflow, nessun merge/rollout o raccolta completa manuale è stato eseguito nell'audit.

*La sezione sottostante conserva il checkpoint storico preparato prima del merge della PR #25; non descrive più il gate attuale.*

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
