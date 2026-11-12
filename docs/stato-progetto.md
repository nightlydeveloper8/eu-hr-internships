# Stato di ripresa — People Placement

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

## 12 novembre 2026 — Drenthe, PR #20 ancora separata

Il testo globale precedente è conservato come fotografia della sessione che ha preparato #25. Il fix #25 è ora presente nella baseline main `0de282c`; questa fase non attesta il successivo ciclo di produzione. Preservati integralmente il test e la regressione aggiuntiva di main.

- [Sesta fase e residui](drenthe-2026-11-12.md), [audit](drenthe-2026-11-12-audit.json), [validazione](drenthe-2026-11-12-validation.json). Precedente head PR `ff5da7c` conservato; nuovo SHA/CI nella descrizione della PR.
- Intergas a Coevorden aggiunta con prove ufficiali di sede, organico arrotondato circa 500 e catena di recruiting. 39 datori, 25 qualificati ≥50, 14 dimensioni ignote. Feed pubblico: 14 pubblicati, nessuna vacancy HR specifica.
- Programma generale Intergas 2027 che include HR registrato separatamente dalle vacancy. Incarico, periodo, lingue e usabilità del modulo non verificati come stage HR specifico. Nessuna nuova vacancy candidabile verificata.
- Catalogo corrente di main identico byte per byte: 327 annunci. WIP storico, ricerche/sedi delle altre province e rollout ATS preservati; nessun merge in main, deployment o raccolta completa manuale.
- Forbo/Aareon restano canali dinamici incompleti; il messaggio vuoto nel template Aareon non prova assenza. Proseguire su datori/località poco coperti e prove delle dimensioni ignote. Non ripetere i blocchi o trasformare programmi generali in vacancy.

Storico Drenthe: rapporti datati 8–11 novembre, conservati nel branch della PR.
