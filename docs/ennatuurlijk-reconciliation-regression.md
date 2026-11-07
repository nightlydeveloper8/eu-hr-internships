# Issue #10 — regressione della riconciliazione quotidiana

Base: `main` / `1d3a0ab`, dopo Actions `42376359936`.

## Riproduzione offline

`python3 -m unittest tests.test_ennatuurlijk_reconciliation -q`

Il test usa il record storico reale `70d297b765fc2696c836` già marcato missing,
una fixture del feed Recruitee e una pagina con titolo e form candidati.
Esegue adattatore, classificazione, verifica policy v2, `finalize()` ed export
JSON, senza rete e senza modificare lo stato dello storico per renderlo aperto.
Prima della correzione il feed produce una vacancy verificata, mentre il catalogo
la retrocede: quattro asserzioni di regressione falliscono.

## Causa e correzione

L'ID generato dal nuovo canale ufficiale differisce dall'ID storico. Il vecchio
ordine calcola l'assenza prima della revisione di ownership e dell'unificazione
delle identità. Il timestamp sintetico di missing può poi vincere sulla verifica.

Le revisioni individuali si applicano ora a storico e osservazioni prima della
riconciliazione. Le identità condivise (ID, URL e alias di vacancy già ammessi)
sono risolte prima del conteggio delle assenze. Storico e osservazioni correnti
sono consolidati separatamente: il risultato corrente prevale anche se negativo,
conservando ID e prima scoperta storici. Una ricomparsa azzera tutti i marcatori
di assenza. Nessuna preferenza globale per record aperti o verificati.

## Verifica e seguito

Coperti cicli consecutivi, riesecuzione idempotente, sorgenti incomplete,
chiusura dopo tre assenze complete e almeno 48 ore, candidatura non dimostrata,
chiusura ufficiale, verifica disabilitata e attribuzione Ennatuurlijk.
Suite Python/frontend, valutazione, validazione catalogo/registro e build offline.
Catalogo di produzione, budget e workflow invariati; nessuna raccolta avviata.

Issue #10 resta aperta: dopo un eventuale merge autorizzato occorre confrontare
l'output della fonte con il catalogo della successiva raccolta completa su main.

## Revisione P1 — alias transitivo

Il nuovo test `test_transitive_historical_bridge_retains_every_current_observation`
attraversa `finalize()` e rilegge il catalogo esportato. Due osservazioni correnti
non condividono direttamente le chiavi: soltanto lo storico collega l'URL della
prima al percorso di candidatura specifico della seconda. Prima della correzione
`deduplicate(rows)[0]` scartava la seconda osservazione, anche se più recente e
chiusa o non verificata (due sottocasi falliti, catalogo erroneamente aperto).

`consolidate_group()` ora considera tutti i membri del componente già riconosciuto,
senza suddividerlo nuovamente. Gli alias storici effettivamente collegati restano
nel record esportato per mantenere il collegamento anche al ciclo successivo;
i portali generici di candidatura continuano a non costituire identità.
Il test controlla chiusura/esito non verificato, ID e prima scoperta, marcatori di
assenza, ripetizione nello stesso giorno e nel giorno seguente, con fonti parziali.
Restano attivi i test originari Ennatuurlijk, policy v2 e assenze incomplete.
