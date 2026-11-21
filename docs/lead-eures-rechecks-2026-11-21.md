# Fase 2 — Ricontrollo delle schede EURES scadute

L'audit sul catalogo `a71b260` trova **57 lead con verifica scaduta, 53 EURES** (NL 36, FR 7, IT 4, CH 3, DE 2, BE 1). L'ultima osservazione risale al 18 novembre per 23 lead e al 19 per gli altri 30. Nessuno dei 53 è stato riosservato nel catalogo nei tre cicli del 20–21 novembre.

| Commit del report di copertura | Richieste totali | Byte letti | Secondi-fonte | Punto di arresto |
| --- | ---: | ---: | ---: | --- |
| `17aea99` · 18 nov | 330 | 95.433.488 | 755,21 | `стажант hr` |
| `3f20f51` · 19 nov | 330 | 95.705.908 | 644,56 | `стажант hr` |
| `49f9b5f` · 20 nov | 330 | 96.244.452 | 641,82 | `стажант човешки ресурси` |
| `7c5ce80` · 20 nov | 330 | 96.224.871 | 891,82 | `стажант човешки ресурси` |
| `a71b260` · 21 nov | 330 | 95.979.098 | 656,07 | `стажант човешки ресурси` |

I report contano insieme le ricerche in POST di sola lettura e i GET; le 330 richieste non sono tutte GET. Il registro assegna 330 richieste e 2.700 s. [Log del job collect (7)](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44879531709/job/136772250995): EURES da 07:24:08 a 07:35:04 UTC, stato partial, 362 match HR (352 verificati nel report e 10 incompleti). Nel codice il raggiungimento del tetto interrompe la ricerca e salta i GET di dettaglio. Anche arrivando alla coda finale, solo uno dei 53 scaduti compare nei primi 40 URL della coda storica. L'assenza dai risultati pubblicati di una ricerca parziale lascia aperto lo stato delle singole schede.

## Modifica e prova in staging

La raccolta ordinaria prova prima **fino a cinque** URL EURES già verificati, non chiusi e non osservati nelle ultime 24 ore, in ordine di ultima osservazione. Usa lo stesso endpoint di dettaglio e lo stesso budget. Un ID esplicitamente diverso nella risposta viene scartato sia nei ricontrolli prioritari sia in quelli ordinari. Il report registra l’URL e l’errore in `detail_errors`. Il ciclo prosegue, conserva le schede già raccolte e non usa la risposta discordante come prova di chiusura. Se la ricerca dello stesso ciclo restituisce l'ID, prevale la scheda della ricerca, anche in presenza di un 404 precedente. I dettagli passano ancora per la classificazione HR e per le verifiche del servizio pubblico. La coda storica resta entro il suo limite includendo le verifiche anticipate.

Confronto live in `.staging/`, stessa fonte, tetto di **8 richieste**, 155 s, robots.txt e attesa di almeno 10 s sullo stesso host. Il budget ridotto riproduce l'arresto prima della coda senza rifare un'intera raccolta.

| Variante | GET | POST ricerca | Byte letti | Secondi | Match HR | Attivi tra i cinque | 404 tra i cinque |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Prima | 1 | 7 | 2.151.215 | 81,094 | 11 | 0 | 0 |
| Dopo | 6 | 2 | 861.363 | 79,775 | 12 | 4 | 1 |

I quattro record passati dal verificatore erano **NL** `b6b6cd3b07b4e5311e12`, `90c2bfb459914d227158`, `76a9c1bc81a4b4e21702` e **IT** `c169cd999100bb8b5607`. Il 404 riguarda **IT** `dbd5231a2843100a8813`. I quattro riapparirebbero come **Public employment service**, con zero candidature dirette. A parità di coda e risposte, il campione indica fino a quattro recuperi nel primo ciclo. I restanti 48 lead sono fuori campione.

Totale prove live riuscite, incluso il preflight sugli stessi cinque ID: **13 GET, 9 POST di ricerca in sola lettura, 3.034.095 byte e 220,963 s**. Una prima esecuzione ha prodotto zero risposte HTTP per errore del trust store TLS, zero byte e 70,110 s complessivi. Il confronto riuscito ha usato il trust store di macOS.

Rischio: fino a cinque richieste sono sottratte alla ricerca se il tetto è raggiunto. Si può perdere recall nelle ultime query. Costi e conteggi del confronto a otto richieste non rappresentano un ciclo di produzione da 330. Il merge tocca `collector/**` e avvia subito la raccolta di produzione.

Snapshot del repository prima/dopo: **906 → 906 ID, 402 → 402 stage verificati, 37 → 37 candidature dirette, 367 → 367 lead, zero ID persi**. Il campione di staging non è stato pubblicato.
