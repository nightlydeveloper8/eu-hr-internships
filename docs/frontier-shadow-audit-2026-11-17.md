# People Placement — pilota di pulizia URL pendenti (17 novembre 2026)

## Risultato effettivo e perimetro

Eseguita la [run #44172195252](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44172195252) su tutti **16 shard**; 16 scan + job aggregato **success**. La run ha ripristinato **solo** i checkpoint già salvati dalla raccolta ordinaria, senza contattare alcun datore. La prova applica esclusivamente il confronto offline a `data/coverage.json` del 17/11 (`main` `ab51981`) e ai corrispondenti `frontier.json` restituiti dalla cache GitHub Actions.

- **335** fonti `universal-employer` con `matching=0` e coda pendente; **335/335** checkpoint trovati.
- `pending_urls` del report: **146.122** voci; nel checkpoint sono effettivamente conservate **138.330** (limite 2.000 per fonte, differenza **7.792** già troncate). Non confondere queste grandezze.
- Voci ripetute con URL **esattamente identico**: **28.044**; file di risorsa tecnica del provider già riconosciuti da `provider_resource`: **149**; URL invalidi: **0**.
- **28.193 / 138.330 = 20,38%** delle voci salvate sono candidati a eliminazione senza rimuovere *alcun URL distinto di vacancy*. Rimangono **110.137 URL distinti non tecnici**. Altre **350** pagine di navigazione potenzialmente non pertinenti sono solo indizi da revisionare, **non escluse**.
- Esempi di duplicazioni: VDL Wientjes Roden 1.518/1.566; BVNG 1.444/1.937; VDL Smart Spaces 1.404/1.462; Flynth 1.263/1.759; Vinted 699/950. Si tratta di voci in coda, non di HTTP sprecati.
- Il [precedente audit #44169896860](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44169896860) attribuiva **100.762 URL pendenti a 232 fonti** nella sola categoria dei crawler universali incompleti: il campione di 335 include anche gli altri pattern tecnici, quindi la somma 146.122 non contraddice la precedente.

## Correzione tecnica proposta, NON in produzione

`collector/universal.py`: `distinct_frontier()` conserva **una sola voce per URL testualmente identico** prima di ordinare e salvare il checkpoint, unendo i flag `job` con OR e conservando la profondità minima per non perdere possibilità di scoperta. Vengono inoltre scartate le sole risorse statiche del provider già identificate. Non vengono collassati URL diversi, query con requisizioni diverse o form di candidatura. I nuovi contatori `frontier_duplicates_pruned`, `frontier_static_skips` e `frontier_checkpoint_dropped` faciliteranno la misura del ciclo successivo.

Test offline specifici: distinzione dei 2.000 URL salvati dal conteggio upstream; conservazione di ogni URL unico, posting flags, query diverse, incompletezza del source e controllo di checkpoint; test di integrazione `Crawler.run()` senza HTTP con coda duplicata. CI [#44172812792](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44172812792) **success** sul commit con gli ultimi test.

**Precisazione fondamentale:** la vecchia raccolta usava già `self.urls_seen` per evitare due visite allo stesso URL nello stesso ciclo. Questo intervento **non ha dimostrato un risparmio di HTTP o byte**, né un aumento degli stage `verified`: migliora la rappresentazione e la capacità del checkpoint, rendendo più URL distinti conservabili dopo la soglia 2.000. Non calcolare le 28.193 voci come 28.193 richieste risparmiate.

## Stato, cautela e prossimo test

Il codice è su un **branch e PR non integrati**; nessuna modifica a `main`, allowlist, robots, frequenza, budget o catalogo. Le fonti partial restano partial; nessuna chiusura o promozione di annunci. Il prossimo gate per il merge è una review dei test e del comportamento della frontier; dopo eventuale integrazione autorizzata, misurare **due cicli ordinari** con gli stessi source ID: richieste/byte/rendering, URL distinti ripresi, HR leads, candidature policy v2 e mancata perdita di record/ID. La riduzione potenziale non garantisce più stage verificati.
