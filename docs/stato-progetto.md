# Stato di ripresa — People Placement

## 11 novembre 2026 — identità aziendali contestuali (nuova PR, NON produzione)

**Obiettivo:** distinguere datore pubblicato, identità del gruppo e dominio di recruiting senza importare automaticamente gli alias aziendali nel crawler o confondere annunci di un ATS condiviso con una controllata. Base `main` `0de282c597be00147792383bd596c761d5cac85f` con PR #25 integrata. PR #20, #26 e #27 non sono state modificate né integrate.

**Audit offline del catalogo di 327 record (ultima raccolta riuscita il 10 novembre):** 1.882 aziende, 1.926 fonti, 30 aziende con alias nel registro e **zero fonti con `employer_aliases` espliciti**. 232 record in 29 fonti hanno un nome datore diverso dal nome fonte, **non equivalenti a 232 errori di ownership**; 108 di queste discrepanze provengono dalla fonte `auto-tilburg-university`, da non riassegnare automaticamente. Baseline e calcolo riproducibili con `python -m scripts.employer_identity_audit`. I dati sono storici, non attestano candidature aperte oggi.

**Meccanismo proposto e isolamento:**
- `collector/employer_resolution.py`: validazione fail-closed di relazioni con ID fonte/azienda, nome esatto del publisher, tipo di relazione, data, prova HTTPS e **singolo host già autorizzato**. Solo `official-recruiting-publisher` può consentire il match di `JobPosting.hiringOrganization` sul dominio esatto. `group-parent`, `brand`, `subsidiary` e `shared-ats` restano metadati non autorizzativi.
- `data/employer-identity-reviews.json`: due prove ufficiali. **Achmea** è un publisher esplicito sul solo `www.werkenbijachmea.nl`, osservato nel portale corporate e marchi; non propaga FBTO/De Friesland, non inferisce la sede Centraal Beheer. **OPACKGROUP** è il gruppo di Oosterwolde Plastic Industry, come attestato sul sito ufficiale, ma non autorizza il collector della controllata a rivendicare stage corporate di Giessen.
- `collector/daily.py` e `collector/pipeline.py`: leggono e validano le prove una volta per esecuzione/shard, applicandole **soltanto in memoria** alle rispettive fonti. Nessuna scrittura di `employer_aliases` in `data/sources.json`, nessun cambio host, query, budget, shard, rollout, CAPTCHA, policy v2.
- `collector/ownership.py` e `collector/universal.py`: match rigoroso del nome pubblicato e del dominio di quell'annuncio, più identità strutturata sulla medesima vacancy. Il solo fatto di essere un gruppo o condividere un ATS non costituisce prova dell'ownership.
- Regressioni offline in `tests/test_employer_resolution.py`: Achmea, alias di marchio non approvati, OPACKGROUP non autorizzato sulla fonte Oosterwolde, ATS universitario estraneo, prova mancante, host malevoli, catalogo invariato e idempotenza. L'audit non usa la rete.

**Beneficio atteso, da non confondere con produzione:** una corrispondenza storica Achmea diviene leggibile dal filtro di identità ufficiale; zero verifiche di candidature nuove dimostrate, zero modifiche al catalogo e nessuna riscrittura automatica delle 108 attribuzioni Tilburg. **Costo incrementale di rete e rendering del risolutore: 0**, costo di esecuzione CI da misurare; il matching aggiunge solo una verifica esatta in memoria. La creazione della PR e l'esito finale CI sono da registrare separatamente. Prima di qualsiasi merge autorizzato controllare la suite completa, mantenere 327 ID e usare una raccolta ordinaria per valutare il recupero reale senza promuovere candidati per il solo nome.

**Punto successivo:** revisionare la PR insieme alla PR #27, consolidare i checkpoint documentali con la PR #26 prima del merge, controllare prima il ripristino del daily post-#25, quindi raccogliere metriche sul prossimo ciclo effettivo (matched/verified/open, richieste, durata, fonti parziali, errori di ownership). Le riassegnazioni di OPACKGROUP/Tilburg richiedono prove individuali; non fare migrazioni massicce né allargare l'allowlist.

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
