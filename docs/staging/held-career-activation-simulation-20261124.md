# Simulazione di attivazione PR #142 — 24 novembre 2026

Catalogo di main a5e609065cf947162f6b3cec79b2a5fdbeac9475. Baseline policy v2 con freschezza di 48 ore, 578 aperti su 1.112 ID. Il simulatore abilita le fonti in memoria, rimuove l’hold nella copia e usa il percorso ordinario di raccolta e finalizzazione. I manifest versionati mantengono i due flag di hold.

| Lotto | Fonti provate | Aperte prima → dopo | Nuovi ID | ID esistenti promossi | ID persi | GET / byte | Stima collect.yml |
|---|---:|---:|---:|---:|---:|---|---:|
| CORPORATE | 2 | 578 → 589 | 13 | 0 | 0 | 25 / 2,282,757 | 24m45s |
| WORKDAY | 48 | 578 → 578 | 7 | 0 | 0 | 188 / 13,999,319 | 27m37s |

Stima sul campione con la durata seriale aggiuntiva massima osservata su uno shard, sommata alla [baseline da 24m02s](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45410068598). L’orologio del controllo e della variante è lo stesso per ciascun lotto. Tempo e resa a copertura completa non dimostrati.

## Stage aperti per paese

| Paese | Corporate | Workday |
|---|---:|---:|
| AT | 7 → 7 | 7 → 7 |
| BE | 26 → 26 | 26 → 26 |
| BG | 0 → 0 | 0 → 0 |
| HR | 0 → 0 | 0 → 0 |
| CY | 0 → 0 | 0 → 0 |
| CZ | 0 → 0 | 0 → 0 |
| DK | 0 → 0 | 0 → 0 |
| EE | 0 → 0 | 0 → 0 |
| FI | 1 → 1 | 1 → 1 |
| FR | 45 → 45 | 45 → 45 |
| DE | 66 → 75 | 66 → 66 |
| GR | 0 → 0 | 0 → 0 |
| HU | 0 → 2 | 0 → 0 |
| IE | 0 → 0 | 0 → 0 |
| IT | 103 → 103 | 103 → 103 |
| LV | 0 → 0 | 0 → 0 |
| LT | 0 → 0 | 0 → 0 |
| LU | 1 → 1 | 1 → 1 |
| MT | 0 → 0 | 0 → 0 |
| NL | 253 → 253 | 253 → 253 |
| PL | 8 → 8 | 8 → 8 |
| PT | 2 → 2 | 2 → 2 |
| RO | 0 → 0 | 0 → 0 |
| SK | 0 → 0 | 0 → 0 |
| SI | 0 → 0 | 0 → 0 |
| ES | 30 → 30 | 30 → 30 |
| SE | 6 → 6 | 6 → 6 |
| CH | 29 → 29 | 29 → 29 |
| GB | 1 → 1 | 1 → 1 |

## Evidenze e decisione

Mercedes-Benz. I 30 record iniziali corrispondevano a 13 ID. I dettagli HTTP 200 espongono JobPosting con data di pubblicazione, ID, luogo esplicito DE/HU e titolo HR di stage. Il pulsante Bewerben era pubblicato in un componente wb-button, invisibile al parser dei soli link. La regola rivista richiede l’ID della stessa scheda, un pulsante abilitato di quel componente e un target ufficiale riconosciuto. Il target non è visitato. Due versioni linguistiche con ID diversi puntano a una stessa requisizione esterna Workday con identificatore diverso e restano lead.

Dettagli del replay Mercedes: 15 candidati, 15 HTTP 200 con JSON-LD, 11 current listing e 2 lead. 57 configurazioni corporate hanno mantenuto il gate di accesso e sono rimaste fuori dalle richieste.

Workday. Un retry per host e scansione dopo almeno 60 s o un Retry-After più lungo, entro il budget esistente. Regeneron e ING erano nella corsia lenta simulata, costo osservato 1m24s. Host con HTTP 429 osservato: Snam, Lottomatica Group, IAG International Airlines Group, Workday, Kyndryl, Accenture, Alcon, Logitech, Aegon, Universal Music Group, Basic-Fit, CTP, Regeneron.

In base alle osservazioni, il manifest assegna alla corsia lenta 12 fonti Workday in hold. Riapplicando lo sharding alle durate osservate, la stima di collect.yml per Workday è 26m36s. Il tetto seriale della corsia lenta è 52 minuti con Gi Group incluso, entro i 60 minuti del workflow. I tenant con due 429 restano senza nuove osservazioni fino a un preflight riuscito.

Kering esclusa in modo permanente e Richemont sospesa per HTTP 403. Motivi e data in AGENTS.md e nel manifest.

La soglia di +30 aperti non è raggiunta. La PR resta in bozza con le fonti in hold.

## Controllo integrale dei titoli nuovi

| Lotto | ID | Paese | Titolo | Stato | Esclusione rilevata |
|---|---|---|---|---|---|
| CORPORATE | 0a31fe29018059812b6f | DE | AMG Praktikanten Personalmanagement ab Januar 2027 (m/w/d) | open | nessuna |
| CORPORATE | e6a8656095774d518b1c | DE | Intern Human Resources Development (m/f/d/x) | unverified | nessuna |
| CORPORATE | 54416d8e0cce1fa732b0 | DE | Praktikant Personalentwicklung (m/w/d/x) | unverified | nessuna |
| CORPORATE | 5361f69d2faaee62b0af | DE | Praktikant\*in Employee Engagement & Corporate Communications (Pflicht-Praktikum) | open | nessuna |
| CORPORATE | 865a00aa53dbf7cebbd2 | DE | Praktikant\*in Employer Branding und Recruiting bei Mercedes-Benz Management Consulting (Pflicht-Praktikum) | open | nessuna |
| CORPORATE | 3bf7099f44108ba655aa | DE | Praktikant\*in HR Top Management Sales & Customer (Pflicht-Praktikum) | open | nessuna |
| CORPORATE | e990e6abe9ed3675081e | DE | Praktikant\*in HR-Prozessmanagement & Document Lifecycle mit Schwerpunkt Testing und Qualitätssicherung (Pflicht-Praktikum) | open | nessuna |
| CORPORATE | 87c7d8b5b27ccc8f4a00 | DE | Praktikant\*in Human Resources | open | nessuna |
| CORPORATE | c7f4da00f6c168f98905 | DE | Praktikant\*in Personalentwicklung und Recruiting (Pflicht-Praktikum) | open | nessuna |
| CORPORATE | 59aad285212e96aa5101 | DE | Praktikant\*in Personalmanagement | open | nessuna |
| CORPORATE | 727cbf08a9c50241ccda | DE | Praktikant\*in im Personalbereich | open | nessuna |
| CORPORATE | a53c753c06f143c6f6b6 | HU | Gyakornok HR - képzés és oktatás területén | open | nessuna |
| CORPORATE | 37873d0211837358a77b | HU | Gyakornok HR adminisztratív területen | open | nessuna |
| WORKDAY | 37667f6c8d962f8c2cbe | DE | Praktikant Human Resources – Knowledge Management (w/m/d) | unverified | nessuna |
| WORKDAY | d3d4a03e0acd2fd25b0e | DE | Praktikant Human Resources – Young Talents (w/m/d) | unverified | nessuna |
| WORKDAY | 92974cec5898aa9f9f55 | DE | Praktikant Payroll (m/w/d) | unverified | nessuna |
| WORKDAY | 440fc6e5c1e23852d8bf | FR | STAGE 2027 - Gestionnaire de projets RH (ALL GENDER) | unverified | nessuna |
| WORKDAY | 7b962d31b864b8e82a08 | FR | Stagiaire Paie & Administration RH - Janvier 2027 | unverified | nessuna |
| WORKDAY | 685945dd40d1faff2543 | LU | INTERNSHIP - HR Communication & Intranet | unverified | nessuna |
| WORKDAY | ceaa2c44b3ca5e47ebd6 | LU | INTERNSHIP - HR Operations | unverified | nessuna |

Verifiche locali Python 3.12.16, 616 test passati. Superati test Node, classificatore, build, provisioning e validazione del catalogo.
