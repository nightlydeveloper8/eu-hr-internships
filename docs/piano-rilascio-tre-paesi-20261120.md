# Release candidate a tre paesi — 20 novembre 2026

## Ambito, autorizzazione, baseline

Questa PR riunisce **solo codice e fonti disabilitate** delle catene JKS **#90 + #92**, SmartWays **#95 + #96** e Jobandtalent **#89 + #91**. Non include #93: il quarto indice JKS non ha prodotto nuove candidature. Nessun merge, cambio di cron, abilitazione o pubblicazione. In `main` la baseline verificata dopo #86 è **887 ID distinti, 39 candidature HR dirette**, 1.923 fonti enabled. Nel candidato integrato le fonti registrate diventano 1.980 (da 1.977); le fonti **enabled restano 1.923**. Il numero di fonti non rappresenta opportunità.

## Evidenza live indipendente

| Paese / fonte | Staging policy v2 | ID catalogo e candidature, prova isolata | Costo misurato nel run | Stato |
| --- | --- | --- | --- | --- |
| **Polonia — SmartWays** | [#44798505750](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44798505750) | `31252` Kraków, **+1 ID / +1 candidatura**; 887→888, 39→40 | **9 GET / 1.160.973 byte** | Resolver dell'alias Recruitee e gate corretto sulla lista di host ordinata; registrata **disabled** |
| **Danimarca — JKS** | [#44797837098](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44797837098) | Vejle 157063, Slagelse 156880, Esbjerg 160886, Odense 160782: **+4 ID / +4 candidature**; 887→891, 39→43 | **18 GET / 2.397.607 byte** | Forma Talentech stesso progetto, scope e budget 24 GET; registrata **disabled** |
| **Svezia — Jobandtalent** | [#44770453908](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44770453908) | JobTech `31558200` → ATS `8503489`: **+0 ID / +1 candidatura**, con adozione esatta dell'ID esistente nei test del fix [#91](https://github.com/nightlydeveloper8/eu-hr-internships/pull/91) | **8 GET / 416.375 byte** nel pilota precedente | Manual-only, budget condiviso ATS; registrata **disabled**; serve nuovo dossier live sul fix |

Sono tutte prove del **20 novembre 2026**, quindi **non sono** prove a distanza di un giorno. Dati del sito in produzione **non aggiornati**. L'effetto cumulativo ipotetico, solo se gli annunci sono ancora candidabili e il merge/rollout preserva gli ID, è **887→892 ID e 39→45 candidature**, non una misura attuale del catalogo pubblico. Non sommare automaticamente conversioni da fonti pubbliche e nuovi ID.

## Conflitti d'integrazione risolti

- `collector/verification.py` era modificato in due catene: il dispatcher integrato mantiene il verifier **JKS** con scope Talentech e quello **SmartWays** con scope Recruitee, senza attivare browser fallback per questi due percorsi.
- `data/sources.json` contiene esattamente le tre nuove fonti **disabled**; nessuna altra voce e nessun valore `enabled` preesistente è cambiato. Il gate quotidiano resta esplicitamente spento.
- `collector/pipeline.py` mantiene il ramo JobTech esistente e la pipeline originale per tutti gli altri adapter; `collector/adapters.py` aggiunge JKS; `collector/public_feeds.py` il resolver SmartWays.
- Nuovo test integrato `tests/test_three_country_release_candidate.py`: identità univoche, no auto-provisioning, gate separati e blocco network prima di autorizzazione, ID storico JobTech preservato. Il test non attribuisce successi live ai soli esiti CI.

## Freschezza delle candidature JKS e date dichiarate

Il controllo ufficiale del 20 novembre ha evidenziato quattro scadenze *Udløber* pubblicate dal datore, non dedotte da un vecchio slug URL: **Slagelse 25 novembre 2026**, **Vejle 28 novembre 2026**, **Esbjerg 21 dicembre 2026**, **Odense 1 gennaio 2027**. Il collector integrato legge la data direttamente dall'HTML già scaricato, richiede un valore unico, la riconcilia con una nuova lettura della stessa pagina e registra `valid_through`. Se la scadenza è passata, blocca la verifica del modulo ed evita GET aggiuntive. `finalize()` applica già la regola della data inclusiva e chiude il record senza interpretare l'assenza dall'inventario. Si tratta di una modifica di sicurezza **non ancora riconfermata live dopo il cambiamento**, che va inclusa nella seconda verifica su data distinta. La necessità del danese indicata da alcuni annunci resta requisito linguistico da mostrare agli utenti; non considerare questi annunci automaticamente accessibili a chi parla solo inglese.

## Correzione sulla scadenza JKS dopo la seconda prova live nello stesso giorno

La [prova del 20 novembre #44802609771](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44802609771) ha evidenziato una normalizzazione imprecisa: la proprietà JSON-LD `validThrough` indicava mezzanotte e prevaleva sulla data visibile `Udløber`, impedendo il conteggio fino al termine dell'ultimo giorno. La variante corretta usa la fine della giornata a **Copenaghen** (CET/CEST) per scadenze solo-data, rispetta orari espliciti più restrittivi e rifiuta date contraddittorie. [Ripetizione #44803197999](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44803197999): JKS **4 stage diretti / 18 GET / 2.400.777 B**, scadenze in catalogo **2026-11-25T22:59:59.999999Z** (Slagelse), **2026-11-28T22:59:59.999999Z** (Vejle), **2026-12-21T22:59:59.999999Z** (Esbjerg), **2027-01-01T22:59:59.999999Z** (Odense); SmartWays **1 stage diretto / 9 GET / 1.160.973 B**, entrambe le fonti disabled. **27 GET / 3.561.750 B** complessivi per due preview separate. La ripetizione è avvenuta nella stessa data, non vale come conferma in un giorno successivo.

## Stop obbligatori prima della produzione

1. Conferma **in data diversa dal 20 novembre**, in sola lettura, dei tre moduli e dei relativi ID. Jobandtalent impone preview manuale esplicita: non introdurre trigger automatici PR/cron per aggirare il requisito.
2. Review e autorizzazione **specifica per ciascun merge** delle catene originali o di questa PR integrata, seguita da autorizzazione distinta **per ciascuna attivazione** (JKS, SmartWays, Jobandtalent). L'attuale PR di integrazione non abilita nulla.
3. Eseguire poi il **primo ciclo quotidiano già configurato** e controllare preservazione degli 887 ID baseline, nessuna nuova chiusura da inventario parziale, delta candidature per singolo datore/paese, timestamp di freschezza, GET, byte, tempo, errori/robots e assenza duplicati.
4. Verificare la **pubblicazione** effettiva sul sito e il catalogo remoto, non limitarsi al verde della CI. Mantenere i link di candidatura separati da eventuali requisiti universitari sul datore.

Il budget rilevato dei tre piloti separati somma **35 GET / 3.974.955 byte**; non è un costo simulato per un ciclo integrato né garantisce la stessa resa giornaliera. Nessuna candidatura inviata, nessun accesso o CAPTCHA aggirato.
