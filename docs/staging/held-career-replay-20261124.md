# Lotti carriere in hold — 24 novembre 2026

Fotografia della prima bozza. Per baseline, metriche e verifiche aggiornate con Python 3.12, vedi il [riesame della PR #142](held-career-revision-20261124.md).

Replay su `a5e609065cf947162f6b3cec79b2a5fdbeac9475`, registri dei lotti in [staging](held-career-lots-20261124.json). I due flag di hold restano nei manifest. La raccolta ordinaria non include questi manifest.

| Lotto | Perimetro e osservazioni | GET misurate | ID persi | Budget aggiuntivo massimo sullo shard | Stima collect.yml |
|---|---|---:|---:|---:|---:|
| CORPORATE-SITEMAP | 95 righe, 33 già coperte, 1 esclusa, 61 in hold. 61 preflight robots HTTP 200. Campione dettagli limitato a Richemont e TUI. | 66 | 0 | 119 GET / 6m25s | 29m46s |
| WORKDAY | 55 righe, 2 duplicati, 34 tenant provati, 19 percorsi di tenant da identificare. Due stage HR classificati in FR come lead. | 133 | 0 | 68 GET / 3m40s | 27m01s |
| Oracle Recruiting | Valutazione di 9 aziende, volume HR non dimostrato. | 9 | n/a | n/a | n/a |

Le GET Workday si riferiscono alle scansioni e ai replay inventariati. Le verifiche diagnostiche del markup sono aggiuntive. I byte dei run Workday sono 7133845. I 5 GET del campione corporate hanno letto 897871 byte. Il preflight corporate ha contato solo lo stato HTTP e le direttive per ogni host.

Stima conservativa con somma seriale dei budget sullo shard più carico aggiunta alla [baseline da 23m21s](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45380157707). Il tetto di configurazione è 17 GET e 55 s per fonte con 16 shard e 6 worker. Sotto 45 minuti nel modello. Durata reale a lotti attivi non dimostrata.

Richemont ha esposto 13 candidati da sitemap. Il primo dettaglio ha restituito HTTP 403 e la scansione si è fermata. TUI si è fermata su un redirect. I termini Kering vietano esplicitamente la scansione. Citazione e URL sono nella riga del manifest. Per gli altri host corporate i termini o i dettagli restano da verificare.

Workday usa sitemap dichiarate in robots e il JobPosting pubblico. Due dettagli FR hanno identificato Airbus Atlantic `JR10436405` e G.H. Mumm `JR-055037`. Resta non dimostrato il percorso di candidatura. Il replay aggiunge due lead. Copertura della ricerca Workday oltre le sitemap pubblicate non dimostrata.

Recall per URL esatto sul [gold set](../recall-gold-set-2026-11.csv) invariato per ciascun replay. DE 0/15 → 0/15, IT 0/1 → 0/1. Recall di mercato e recall sui 327 segnali del CSV non dimostrati.

| Paese di lavoro | Corporate aperti / dirette / lead | Workday aperti / dirette / lead | Oracle volume |
|---|---|---|---|
| AT | 0 → 0 / 0 → 0 / 8 → 8 | 0 → 0 / 0 → 0 / 8 → 8 | non dimostrato |
| BE | 5 → 5 / 5 → 5 / 23 → 23 | 5 → 5 / 5 → 5 / 23 → 23 | non dimostrato |
| BG | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| HR | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| CY | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| CZ | 0 → 0 / 0 → 0 / 1 → 1 | 0 → 0 / 0 → 0 / 1 → 1 | non dimostrato |
| DK | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| EE | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| FI | 0 → 0 / 0 → 0 / 2 → 2 | 0 → 0 / 0 → 0 / 2 → 2 | non dimostrato |
| FR | 8 → 8 / 7 → 7 / 180 → 180 | 8 → 8 / 7 → 7 / 180 → 182 | non dimostrato |
| DE | 42 → 42 / 8 → 8 / 60 → 60 | 42 → 42 / 8 → 8 / 60 → 60 | non dimostrato |
| GR | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| HU | 0 → 0 / 0 → 0 / 2 → 2 | 0 → 0 / 0 → 0 / 2 → 2 | non dimostrato |
| IE | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| IT | 58 → 58 / 0 → 0 / 85 → 85 | 58 → 58 / 0 → 0 / 85 → 85 | non dimostrato |
| LV | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| LT | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| LU | 0 → 0 / 0 → 0 / 4 → 4 | 0 → 0 / 0 → 0 / 4 → 4 | non dimostrato |
| MT | 0 → 0 / 0 → 0 / 1 → 1 | 0 → 0 / 0 → 0 / 1 → 1 | non dimostrato |
| NL | 34 → 34 / 26 → 26 / 395 → 395 | 34 → 34 / 26 → 26 / 395 → 395 | non dimostrato |
| PL | 1 → 1 / 0 → 0 / 17 → 17 | 1 → 1 / 0 → 0 / 17 → 17 | non dimostrato |
| PT | 2 → 2 / 2 → 2 / 1 → 1 | 2 → 2 / 2 → 2 / 1 → 1 | non dimostrato |
| RO | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| SK | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| SI | 0 → 0 / 0 → 0 / 0 → 0 | 0 → 0 / 0 → 0 / 0 → 0 | non dimostrato |
| ES | 28 → 28 / 1 → 1 / 22 → 22 | 28 → 28 / 1 → 1 / 22 → 22 | non dimostrato |
| SE | 0 → 0 / 0 → 0 / 9 → 9 | 0 → 0 / 0 → 0 / 9 → 9 | non dimostrato |
| CH | 1 → 1 / 1 → 1 / 34 → 34 | 1 → 1 / 1 → 1 / 34 → 34 | non dimostrato |
| GB | 1 → 1 / 1 → 1 / 7 → 7 | 1 → 1 / 1 → 1 / 7 → 7 | non dimostrato |

Controlli locali con Python 3.9 e Node 24. Test mirati del nuovo adattatore e SF-RMK, test Node, build, valutazione dei 146 esempi e validazione catalogo superati. La suite Python completa ha riportato 6 failure e 4 errori su 612 test. I dieci casi hanno riprodotto lo stesso esito su `origin/main`.
