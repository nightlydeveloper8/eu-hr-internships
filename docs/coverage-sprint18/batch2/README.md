# Coverage Improvement Sprint #18 — secondo lotto

Collegata alla [Issue #18](https://github.com/nightlydeveloper8/eu-hr-internships/issues/18).
Base: ultimo `main` `2a9668545fd7fa64394014869d12b8b3eeb6b52d`, successivo alla PR #19 e alla raccolta dell'8 novembre 2026.

## Risultato

**Zero candidature aggiuntive verificabili sulle evidenze disponibili.** Due difetti nel collegamento tra vacancy e candidatura sono corretti, senza considerare sufficiente una CTA o una pagina priva di form.

| Misura sullo stesso snapshot | Prima | Dopo |
|---|---:|---:|
| Aziende residue ordinate / analizzate | 17 / 7 | 17 / 7 |
| Candidature HR note nel campione | 8 | 8 |
| Verificate policy v2 nel campione | 0 | 0 |
| Unverified nel campione | 8 | 8 |
| Candidate-to-verified conversion | 0% | 0% |
| Catalogo nel replay: open / unverified / closed | 24 / 296 / 4 | 24 / 296 / 4 |
| Nuove vacancy scoperte | 0 | 0 |

Baseline aziendale del campione: **partial=6, discovery-incomplete=1**, collected=0, verified-empty=0, blocked-or-failed=0. Non è stato riletto alcun inventario completo: nessun passaggio a collected/verified-empty o chiusura per assenza viene rivendicato. Dopo la diagnosi DeFabrique ha una restrizione sull'ATS; non viene ritentata o aggirata.

Il catalogo e i registry di produzione restano identici a `main`. Il replay confronta il verificatore esatto di `main` (sorgente compresso con SHA-256) e il verificatore corretto sugli stessi body ufficiali. Applica poi le osservazioni delle sole candidature note a una copia del catalogo con `finalize`: non simula la discovery di un inventario completo. Verifica ripetibilità del verificatore e due finalizzazioni idempotenti. I 324 ID, gli open esistenti, i closed, ownership, alias e prima scoperta sono preservati; le candidature esterne al campione sono identiche prima/dopo. Policy v2 e review block Trunkrs/Domino's, VAR/Meerpaal restano invariati.

## Priorità aggiornata, senza nuova ricerca

La [graduatoria JSON](ranking.json) contiene **soltanto le 17 righe non selezionate del primo lotto**, ricalcolate usando catalogo, employer-collection e source ID correnti. La shortlist originale non è riscritta.

Punteggio euristico: +20 per almeno un unverified, +40 per form mancante/ID candidatura non collegato, +30 senza URL pendenti, +20 con almeno una vacancy nota NL, +10 per massimo 10 pagine lette nell'ultima raccolta. Ordinamento per esclusione, score decrescente, pagine crescenti, ID. Blocchi documentati e aziende già verificate sono escluse dalla selezione. Selezionate le prime sette: nessun ID aziendale viene aggiunto o sostituito.

Unilever e AS Watson sono già verificate. Philips, Politie, Manpower, Technicum e Randstad hanno URL pendenti; Royal A-ware ha un problema diverso di identità/titolo. Econvert e Yobbers hanno candidature note rispettivamente FR/ES e ES: la presenza dell'azienda nei Paesi Bassi non rende NL queste vacancy. Restano in coda senza nuove letture. Requisiti linguistici espliciti conservati nella graduatoria; nessuna sufficienza dell'inglese inferita.

## Diagnosi e costi

**23 chiamate logiche** complessive, incluse robots e la conferma del runtime; limite di 8 chiamate e 45 secondi osservati per azienda. I redirect interni a urllib non sono conteggiati come chiamate separate; le durate escludono il doppio conteggio delle letture robots annidate. Manifest con timestamp UTC, URL iniziali/finali, hash, eventi e body compressi in `tests/fixtures/sprint18-batch2/`.

| Azienda | Score | Candidature | Chiamate | Secondi | Diagnosi e residuo |
|---|---:|---:|---:|---:|---|
| DeFabrique Holding | 120 | 1 | 4 | 1,305 | Il JSON-LD della vacancy pubblica l'ATS ID 405317, presente anche nella CTA ufficiale. Ora il collegamento è riconosciuto; robots dell'ATS risponde 406. Esclusa da ulteriori letture, resta unverified. |
| Center Parcs | 120 | 2 | 3 | 20,699 | Titoli e ID presenti, pulsanti Solliciteren JavaScript senza URL/form HTML. Nessun endpoint ricostruito. |
| AXS Logistiek | 120 | 1 | 4 | 2,999 | CTA con ID Salesforce diverso dall'ID nel percorso. Nessuna prova indipendente che colleghi i due; la destinazione letta per diagnosi non ha titolo specifico né form HTML. Nessuna promozione. |
| Bentacera | 110 | 1 | 2 | 1,383 | Toggle JavaScript del modulo, soli form preferiti/cookie nell'HTML. Non verificabile con queste evidenze. |
| Elevation Group | 110 | 1 | 4 | 1,786 | Pagina ufficiale accessibile con Python 3.12, nessuna candidatura HTML dimostrata. |
| OPACK / Oosterwolde Plastic Industrie | 110 | 1 | 2 | 1,329 | Toggle JavaScript; form job-alert e cookie esclusi correttamente. |
| Centraal Beheer Achmea | 110 | 1 | 4 | 1,734 | CTA figlia `/solliciteer` ora riconosciuta; destinazione con stesso titolo ma solo form cookie nell'HTML. Resta unverified. |

Le letture iniziali usavano Python di sistema 3.9.6. Il suo urllib ha restituito HTTP 308 su Elevation; una sola conferma con **Python 3.12.14, allineato alla CI**, ha letto la pagina. Tentativo originario e conferma sono conservati nel manifest e inclusi nel budget. Il confronto finale e tutti i test usano Python 3.12: non è stata introdotta una modifica generale alla gestione degli errori per questa differenza locale. Lo script ora richiede 3.12 per nuove acquisizioni.

## Correzione riutilizzabile

Un'unica area di intervento: **identità del collegamento vacancy → candidatura** in `collector/verification.py`.

1. Se manca il posting ID raccolto, un solo `JobPosting.identifier` pubblicato nella vacancy corrente, con titolo corrispondente, può collegare la CTA osservata all'ATS. Non si estrae un ID dalla CTA per convalidare la CTA stessa; ID discordanti/ambigui restano rifiutati. Il record non viene mutato.
2. Il percorso figlio esatto `/solliciteer` conserva l'identità della vacancy come `/apply` e `/application`. Percorsi generici, altre vacancy, host diversi e ulteriori segmenti non soddisfano questo controllo.

Restano richiesti host approvato, lettura corrente, identità, deadline valida e form candidato con submit abilitato. Fixture sintetiche negative coprono ID discordanti, titolo errato, host/redirect, challenge, scadenza e form disabilitato. Le prove positive sintetiche dimostrano il comportamento del codice e **non entrano nel conteggio delle verifiche reali**.

## Timeout Veepee

Nessun difetto riproducibile nella gestione generale degli errori. Test sullo stesso ID Veepee `638f5719bdad59dfc7be` verificano: tre timeout consecutivi su giorni diversi producono `unverified/incomplete`, conservano l'ultima verifica storica, non incrementano missing_count e non abilitano chiusure per assenza; una successiva risposta valida ripristina la verifica sullo stesso ID. Un timeout dell'inventario e un inventario partial vuoto preservano la storia. Il ripristino nel test usa HTML sintetico, senza dichiarare Veepee nuovamente verificata in produzione.

## Riproduzione e controlli

Con Python **3.12+** e Node:

```sh
python3 scripts/coverage_sprint18_batch2.py                 # ranking aggiornato, sola lettura
python3 scripts/replay_sprint18_batch2.py                   # replay offline, report congelato
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 scripts/company_coverage.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

Esiti: **261 test Python**, **21 frontend**, classificazione su **64 esempi senza errori**, registry **1.882 aziende / 1.882 monitorate**, validazione catalogo e build statico riusciti. I soli timestamp rigenerati dalle validazioni sono esclusi dalla PR.

Per acquisizioni future autorizzate, `--capture` rifiuta fixture preesistenti; `--capture-linked` segue al massimo una CTA osservata per fonte nel budget residuo. Non sono comandi di raccolta completa. Non utilizzare mai i body archiviati per rinnovare verifiche reali.

Nessuna nuova provincia, servizio a pagamento, sottoagente, invio di moduli, intervento umano sulle candidature, merge, deploy manuale o raccolta completa. Le correzioni sono nel percorso ordinario del collector: la raccolta quotidiana continuerà autonomamente con nuove evidenze live.
