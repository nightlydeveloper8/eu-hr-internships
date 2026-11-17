# People Placement — 12 SmartRecruiters FR/BE, verifica HTML same-ID (17 novembre 2026)

## Risultato GET live e limiti

[GitHub Actions #44173173596](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44173173596), job `bounded-read`: **success**. Campione estratto automaticamente dal catalogo `main` aggiornato alle **08:07 UTC del 17/11**, limitato a record `unverified`, `internship`, FR/BE, dominio esatto `jobs.smartrecruiters.com`: **12 record (11 FR, 1 BE)**. Eseguiti GET su **tutti e 12** i link ufficiali, più il preflight robots nella contabilizzazione BudgetClient: **13 richieste / 1.427.729 byte / 0 browser / 0 POST / 0 candidatura** in circa 8 secondi wall-clock della sezione di lettura. Non interrogata `api.smartrecruiters.com`, né altre API, endpoint inventati o host non revisionati.

Per tutti i 12 URL: risposta corrente HTTP 200, **titolo della pagina corrispondente all'annuncio** (`same_title=True`). Tutti presentano `structured_ids=[]` nell'HTML disponibile e **zero CTA HTML `Apply/Postuler` con percorso vacancy-specific same-ID dimostrabile**; nessun form visibile abilitato `strict` è stato trovato. **0 candidati a form same-ID**, **0 stage verificati**, **12 restano unverified**. Questa prova non dimostra chiusura degli annunci né indisponibilità dei flussi dinamici; un titolo corretto nell'HTML non basta a verificare il form.

| Datori esaminati | Record del campione | Esito |
|---|---:|---|
| ALTAREA | 1 | titolo corrispondente, no same-ID HTML form |
| Interlogement 93 | 1 | titolo corrispondente, no same-ID HTML form |
| Salomon | 3 | titolo corrispondente, no same-ID HTML form |
| Sia | 2 | titolo corrispondente, no same-ID HTML form |
| SMCP | 1 | titolo corrispondente, no same-ID HTML form |
| JDE Peet's | 2 (FR, BE) | titolo corrispondente, no same-ID HTML form |
| Lesaffre | 2 | titolo corrispondente, no same-ID HTML form |

## Metodo tecnico riutilizzabile

`scripts/pilot_smartrecruiters_public.py`: lista deterministica dal catalogo, `BudgetClient` robots-aware (`max_requests=30`, 90 s, 0,6 s delay), redirect confinati al solo host ufficiale, confronto di titolo e ID pubblicato, ricerca di **sole CTA effettivamente presenti** e poi modulo `strict` solo sullo stesso posting. Le 5 regressioni offline preservano URL di posti diversi, rifiutano CTA di altre posizioni e host esterni, non promuovono shell, non alterano il catalogo. CI [#44173173172](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44173173172) success.

Il codice di pilota **non** integra un nuovo collector SmartRecruiters o un'applicazione dinamica. Niente aggiramenti robots o assunzioni che un URL `/apply` possa essere costruito. Per proseguire serve **un punto di candidatura ufficiale effettivamente pubblicato, con identità e modulo consentiti**, oppure un percorso ufficiale alternativo verificabile dal sito del datore. Senza questo, evitare rendering ripetuti e conservare `unverified`.

## Stato

Letture correnti effettivamente eseguite in GitHub Actions isolata. Nessuna fonte nuova attivata, nessun merge, catalogo/sito non modificati; i 12 non vanno conteggiati come nuove vacancy policy v2. Workflow temporaneo da rimuovere dopo la prova; costi monetari non misurati.
