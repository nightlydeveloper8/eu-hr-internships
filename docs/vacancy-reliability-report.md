# Affidabilità vacancy e lingue — 6 novembre 2026

Base: `main` aggiornato a `1579e4f`, dopo Groningen. Nessuna nuova fonte, azienda o area geografica; nessun merge, refresh del catalogo di produzione o servizio AI aggiunto.

## Lacune osservate prima delle modifiche

Il catalogo di base conteneva 183 record: 177 `open`, 6 `unverified`, 3 con `application_verification`. Per la maggioranza dei connettori, due HEAD riuscite potevano promuovere un record a `open`: non dimostravano né una candidatura disponibile né la corrispondenza della pagina dopo un redirect. Questi numeri descrivono i vecchi flag, non certificano 177 vacancy realmente aperte.

Erano già corretti la raccolta senza filtro sulla lingua dell'annuncio, i 27 paesi selezionabili, la separazione working student/stage, il blocco delle chiusure da fonti parziali, la quarantena delle sparizioni massive e la conservazione dopo errori. Mancavano Employee Relations e alcune varianti L&D. Preferenze, negazioni e alternative linguistiche potevano diventare requisiti obbligatori; il filtro inglese accettava anche una preferenza. Non esisteva un filtro dedicato ai requisiti sconosciuti.

Altri bug riprodotti: chiuso → non verificato durante la riconciliazione; fusione tramite portale generico di candidature; vecchia verifica positiva prevalente su un mirror chiuso più recente; perdita dei nuovi record validi dopo un errore tardivo di enrichment; shard completi di run differenti pubblicabili insieme.

## Confronto riproducibile

| Controllo sullo stesso set | Prima (`1579e4f`) | Dopo |
|---|---:|---:|
| Errori di inclusione/specializzazione, 64 casi etichettati | 8 | 0 |
| Errori requisiti/inglese, 12 casi etichettati | 8 | 0 |
| Una HEAD riuscita può dimostrare `open` | Sì | No |
| Inglese preferito soddisfa il filtro di lavoro | Sì | No |
| Inglese da solo | Non modellato | Solo dichiarazione esplicita; altrimenti sconosciuto |
| Filtro requisiti sconosciuti | Assente | Presente |
| Shard di run differenti | Non distinti | Rigettati prima di pubblicare |

I set sono piccoli e costruiti per le regressioni: non sono stime dell'accuratezza sull'intero mercato UE. I 52 casi preesistenti rimangono corretti. Le 12 aggiunte coprono Employee/Industrial Relations, L&D francese, programme generici, lavoro graduate e falsi positivi benefits. Le regole restano deterministiche, con brevi estratti e metodo di estrazione; non certificano idoneità, sufficienza linguistica o interpretazione completa dell'annuncio.

Nel campione live finale: 4 fonti esistenti, 3 vacancy leggibili, 3 pagine positive alla HEAD del link principale, **2 vacancy con candidatura verificata e 1 verifica incompleta**. Una quarta fonte ha avuto un timeout dell'inventario. Le osservazioni hanno timestamp individuali nel [rapporto JSON](vacancy-live-audit.json):

- Emma, People Process Automation Intern: inventario pubblico corrente, titolo della vacancy, percorso della medesima requisition `/apply`, form e controllo di invio disponibili. Inglese esplicito; sufficienza del solo inglese sconosciuta.
- Fotofabriek, Stage HRM: posizione nell'indice corrente e form Odoo della stessa vacancy, campi candidati e controllo di invio del template osservato. Lingua di lavoro sconosciuta: l'annuncio olandese non permette di dedurre un requisito.
- HRBP Intern, Talent Programs: titolo e inventario leggibili; candidatura non stabilita dal documento statico, quindi verifica incompleta. Inglese esplicito; inglese da solo sconosciuto.
- Veepee: timeout; nessuna deduzione di chiusura o assenza. Anche Emma ha avuto un timeout in un tentativo precedente: il controllo successivo è riportato col suo timestamp.

Non è stato verificato nuovamente l'intero catalogo. La diminuzione dei flag verificati durante la migrazione misura il cambio di soglia probatoria, non una diminuzione dimostrata delle vacancy sul mercato.

## Comportamento introdotto

`verification.state` distingue `verified`, `incomplete`, `blocked`, `closed`, con motivo, timestamp e versione della policy. Gli inventari pubblici correnti sono registrati quando disponibili; le cache non vengono spacciate per inventari correnti. Titolo, identificativi strutturati, percorso della requisition, form/campi e controlli abilitati devono corrispondere. I template già revisionati sono riutilizzati. Redirect ambigui, form non dimostrabili, account/JavaScript non supportati e budget esauriti rimangono incompleti. Nessuna candidatura viene inviata.

Chiusure esplicite e scadenze pubblicate sono trattate separatamente dalle assenze: queste ultime richiedono ancora tre inventari completi in almeno 48 ore. Un record chiuso non riapre per assenza. La deduplicazione conserva lo stato dell'osservazione più recente, la prima scoperta e il precedente timestamp positivo come storico; un link generico non identifica una vacancy.

La lingua dell'annuncio resta separata dalla lingua di lavoro. Requisiti/preferenze/alternative/lingua di lavoro hanno evidenze distinte. `language_requirements` espone lingue richieste, alternative, possibilità documentata dell'inglese e sufficienza del solo inglese, con sconosciuto come esito esplicito. Un'etichetta confermata indica un estratto testuale riconosciuto dalle regole, non una garanzia semantica o di ammissibilità. I testi integrali non sono esportati; i link originali restano disponibili.

Il frontend, il registro aziende e le pagine provinciali applicano la stessa soglia: le vecchie verifiche HEAD non contano come vacancy verificate; rimangono esplorabili attivando i non verificati. Dopo il merge una raccolta completa dovrà rivalutare i record. Le prove più vecchie di 48 ore non alimentano i risultati verificati, anche quando il sito statico resta pubblicato senza nuovi dati.

## Raccolta quotidiana e timestamp

Cron invariato: `17 6 * * *` UTC, ossia 07:17 a Zurigo in inverno, 08:17 in estate. È stata osservata una vera esecuzione `schedule` riuscita il 6 novembre: [run 42180468791](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42180468791), avviata alle 07:22:39 UTC e terminata alle 07:42:40 UTC, quindi con ritardo rispetto al cron. Anche la raccolta dopo il merge Groningen è riuscita: [run 42264583427](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42264583427). Sono prove dell'infrastruttura precedente, non dell'esecuzione in produzione del nuovo codice. Dati dello storico in [vacancy-schedule-audit.json](vacancy-schedule-audit.json).

La nuova pubblicazione esige run ID e tentativo coerenti, tutti gli shard attesi, fingerprint del registro, timestamp con timezone, avvii entro 24 ore, intervalli coerenti e fine non oltre 5 minuti nel futuro. Un errore conserva il catalogo precedente. Dopo un rerun parziale dei soli job falliti occorre rieseguire tutti i job: gli artifact del tentativo precedente vengono intenzionalmente rifiutati. La UI mostra anche ora e fuso; distingue ultima raccolta, osservazione, tentativo e verifica positiva. Il monitor di obsolescenza a 36 ore rimane attivo.

## Validazione e limiti residui

163 test Python e 15 test frontend superati; valutazione 64 casi, validazione catalogo e build riuscite. Test browser locale desktop/mobile riuscito: migrazione, requisiti sconosciuti, filtri combinati paese/specializzazione/lingua, inglese da solo, link originale, nessun errore JS o overflow orizzontale. Casi limite offline: working student, graduate programme, annunci multilingue, scadenze, chiusura francese accentata, candidatura disabilitata, identità discordanti, redirect errati/robots, fonte parziale, errore tardivo, duplicati e shard incoerenti.

Restano falsi negativi possibili per lingue/formulazioni non riconosciute, pagine JavaScript/SSO, redirect legittimi non revisionati e form nuovi. Le restrizioni robots/accesso rimangono bloccanti; anche le destinazioni dei redirect sono controllate prima di seguirle. Il trasporto TLS alternativo rifiuta redirect automatici non revisionati. I timeout non diventano chiusure. La copertura UE resta parziale e non esaustiva. Nessuna espansione geografica è stata avviata.

Riproduzione:

```sh
python3 -m unittest discover -s tests -v
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
python3 scripts/audit_vacancy_evidence.py --output /tmp/regression-comparison.json
python3 scripts/audit_vacancy_evidence.py --sources lever-emma-sleep lever-veepee auto-fotofabriek greenhouse-talentprograms --output /tmp/live-evidence.json
# Opzionale: Playwright già previsto in requirements-collector.txt
python3 scripts/check_evidence_ui.py
```
