# Riesame della PR #142 — 24 novembre 2026

Il replay usa il catalogo attuale di main, commit a5e609065cf947162f6b3cec79b2a5fdbeac9475, snapshot delle 14:28:01 UTC. La definizione del frontend con policy v2 e 48 ore di freschezza riproduce 578 aperti, tra cui IT 103, DE 66 e FR 45. La prima bozza esigeva un link_status che escludeva i servizi pubblici. Python 3.9 declassava inoltre 32 scadenze valide nel runtime 3.12. Il controllo e la variante di ogni lotto usano lo stesso orologio e Python 3.12.

| Lotto | GET | Byte | Maggiore tempo per shard misurato, seriale | Stima collect.yml sul campione |
|---|---:|---:|---:|---:|
| CORPORATE-SITEMAP | 98 | 9,163,434 | 1m25s | 25m27s |
| Controlli corporate già coperti | 227 | 26,100,563 | 1m36s | fuori dal rollout |
| WORKDAY | 237 | 20,689,361 | 0m54s | 24m56s |

La risoluzione dei tenant conta altre 98 GET Workday. Il budget di scoperta comprende robots, indici, sitemap e redirect, fino a 12 GET per host. I dettagli sono richiesti dopo il triage entro il budget complessivo e si fermano per blocco di accesso.

Scansione corporate su 12 host misurati, controlli inclusi. Mediana 3.5 GET di scoperta, massimo 12.
La stima somma il maggiore tempo seriale per shard misurato alla [baseline da 24m02s](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45410068598). Durata a copertura completa e rispetto della soglia di 45 minuti non dimostrati.

Kering resta esclusa. I termini di www.kering.com vietano «Use any deep-link, page-scrape, spider, robot, crawl, index, Internet agent or other automatic device». [Clausola Kering](https://www.kering.com/en/legal/)

## Controlli del maintainer e principali esiti per sito

| Sito | Attesi nel censimento | Candidati | Dettagli tentati (HTTP e markup) | Aperti per paese | Lead per paese | Esito |
|---|---:|---:|---|---|---|---|
| BMW | 19 | 23 | 19 200 microdata, 4 200 none, 23 302 | 18 DE | 0 | 4 × No unique JobPosting, 1 × Explicit workplace country outside scope or missing |
| Richemont | 17 | 13 | 1 403 | 0 | 0 | 1 × HTTP Error 403: Forbidden, 1 × Sitemap host stopped or request budget exhausted |
| L'Oréal | 12 | 0 | 0 | 0 | 0 | — |
| Danone | 9 | 8 | 7 200 none, 1 trasporto | 0 | 0 | 7 × No unique JobPosting, 1 × The read operation timed out |
| Roche | 9 | 9 | 9 200 json-ld | 0 | 1 DE | 8 × Usable JobPosting and explicit workplace country required · 4 sitemap in coda |
| Mercedes-Benz Group | 8 | 36 | 36 200 json-ld | 0 | 26 DE, 4 HU | 3 × Unreviewed hiring organization: Mercedes-Benz Manhattan, Inc., 3 × Unreviewed hiring organization: Mercedes-Benz Vietnam Ltd. |
| Schaeffler | 8 | 9 | 9 200 microdata | 8 DE | 0 | 1 × Usable JobPosting and explicit workplace country required |
| Accor | 8 | 10 | 10 200 json-ld | 0 | 0 | 10 × Usable JobPosting and explicit workplace country required |
| Vinci | 8 | — | — | — | — | Uso strettamente personale. [CGU Vinci art. 4](https://jobs.vinci.com/fr/Conditions-G%C3%A9n%C3%A9rales-d%E2%80%99Utilisation) |
| Infineon Technologies | 7 | 4 | 4 200 json-ld | 0 | 0 | 3 × Usable JobPosting and explicit workplace country required, 1 × No unique JobPosting |
| Nestlé | 7 | — | — | — | — | Termini applicabili al percorso non dimostrati. Dettagli non richiesti. |
| Thales | 6 | 5 | 5 200 json-ld | 0 | 1 BE, 2 FR | 1 × Usable JobPosting and explicit workplace country required · 9 sitemap in coda |
| ASML | 6 | 6 | 6 200 none | 0 | 0 | 6 × No unique JobPosting |
| TUI | — | 0 | 0 | 0 | 0 | — |
| Airbus (Workday) | — | 1 | 1 200 json-ld | 0 | 1 FR | — |
| Pernod Ricard (Workday) | — | 1 | 1 200 json-ld | 0 | 1 FR | — |
| Lottomatica Group (Workday) | — | 0 | 0 | 0 | 0 | — |
| Regeneron (Workday) | — | — | 0 | 0 | 0 | HTTP Error 429: Too Many Requests |
| Richemont (Workday) | — | — | 0 | 0 | 0 | HTTP Error 429: Too Many Requests |
| ING Group (Workday) | — | — | 0 | 0 | 0 | HTTP Error 429: Too Many Requests |

## Simulazione per paese

| Paese | Aperti allo snapshot | Corporate prima → dopo | Workday prima → dopo |
|---|---:|---:|---:|
| AT | 7 | 7 → 7 | 7 → 7 |
| BE | 26 | 26 → 26 | 26 → 26 |
| BG | 0 | 0 → 0 | 0 → 0 |
| HR | 0 | 0 → 0 | 0 → 0 |
| CY | 0 | 0 → 0 | 0 → 0 |
| CZ | 0 | 0 → 0 | 0 → 0 |
| DK | 0 | 0 → 0 | 0 → 0 |
| EE | 0 | 0 → 0 | 0 → 0 |
| FI | 1 | 1 → 1 | 1 → 1 |
| FR | 45 | 45 → 45 | 45 → 45 |
| DE | 66 | 66 → 66 | 66 → 66 |
| GR | 0 | 0 → 0 | 0 → 0 |
| HU | 0 | 0 → 0 | 0 → 0 |
| IE | 0 | 0 → 0 | 0 → 0 |
| IT | 103 | 103 → 103 | 103 → 103 |
| LV | 0 | 0 → 0 | 0 → 0 |
| LT | 0 | 0 → 0 | 0 → 0 |
| LU | 1 | 1 → 1 | 1 → 1 |
| MT | 0 | 0 → 0 | 0 → 0 |
| NL | 253 | 253 → 253 | 253 → 253 |
| PL | 8 | 8 → 8 | 8 → 8 |
| PT | 2 | 2 → 2 | 2 → 2 |
| RO | 0 | 0 → 0 | 0 → 0 |
| SK | 0 | 0 → 0 | 0 → 0 |
| SI | 0 | 0 → 0 | 0 → 0 |
| ES | 30 | 30 → 30 | 30 → 30 |
| SE | 6 | 6 → 6 | 6 → 6 |
| CH | 29 | 29 → 29 | 29 → 29 |
| GB | 1 | 1 → 1 | 1 → 1 |

Zero ID storici persi in entrambi i replay. Recall sul gold set per URL esatto invariato, DE 0/15 e IT 0/1. Recall sul censimento completo non dimostrato.

Ultima [CI di main](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45404395745) verde. Con Python 3.12.16, 608 test passati su main e 614 sul ramo. I dieci esiti negativi della prima bozza erano del replay locale con Python 3.9.

La verifica dei termini corporate oltre il campione rimane aperta. Citigroup e AB InBev non hanno esposto un inventario compatibile nel preflight. I percorsi Sandvik trovati riguardano più società o il canale interno. Le due righe Shell rimandano allo stesso tenant pubblico.

## Esiti HTTP e markup per host misurato

| Lotto | Datore | GET cumulati | Robots | Sitemap | Dettagli |
|---|---|---:|---|---|---|
| corporate | Richemont | 3 | 1 200 | 1 200 | 1 403 |
| corporate | TUI | 5 | 2 200 | 1 200, 1 301, 1 trasporto | 0 |
| corporate | Mercedes-Benz Group | 90 | 3 200 | 10 200, 3 307 | 73 200 json-ld, 1 302 |
| controls | BMW | 98 | 3 200 | 3 200 | 19 200 microdata, 4 200 none, 46 302, 23 trasporto |
| controls | Danone | 12 | 2 200 | 1 200, 1 trasporto | 7 200 none, 1 trasporto |
| controls | Roche | 21 | 1 200 | 11 200 | 9 200 json-ld |
| controls | Schaeffler | 22 | 2 200 | 2 200 | 18 200 microdata |
| controls | Infineon Technologies | 8 | 1 200 | 3 200 | 4 200 json-ld |
| controls | Thales | 34 | 2 200 | 22 200 | 9 200 json-ld, 1 trasporto |
| controls | L'Oréal | 5 | 2 200 | 1 200, 1 301, 1 trasporto | 0 |
| controls | Accor | 16 | 1 200 | 5 200 | 10 200 json-ld |
| controls | ASML | 11 | 1 200 | 4 200 | 6 200 none |
| workday | Leonardo | 2 | 1 200 | 1 200 | 0 |
| workday | Prysmian | 2 | 1 200 | 1 200 | 0 |
| workday | Snam | 1 | 1 200 | 0 | 0 |
| workday | Brunello Cucinelli | 2 | 1 200 | 1 200 | 0 |
| workday | Acciona | 2 | 1 200 | 1 200 | 0 |
| workday | Amadeus IT Group | 2 | 1 200 | 1 200 | 0 |
| workday | Banco Santander | 2 | 1 200 | 1 200 | 0 |
| workday | BBVA | 2 | 1 200 | 1 200 | 0 |
| workday | Enagás | 2 | 1 200 | 1 200 | 0 |
| workday | Ferrovial | 2 | 1 200 | 1 200 | 0 |
| workday | Iberdrola | 3 | 1 200 | 2 200 | 0 |
| workday | Repsol | 3 | 1 200 | 2 200 | 0 |
| workday | Laboratorios Farmacéuticos Rovi | 3 | 1 200 | 2 200 | 0 |
| workday | IAG International Airlines Group | 6 | 1 200 | 5 200 | 0 |
| workday | Airbus | 3 | 1 200 | 1 200 | 1 200 json-ld |
| workday | CTS Eventim | 9 | 1 200 | 8 200 | 0 |
| workday | Evonik | 3 | 1 200 | 2 200 | 0 |
| workday | KION Group | 3 | 1 200 | 2 200 | 0 |
| workday | Air Liquide | 3 | 1 200 | 2 200 | 0 |
| workday | Eiffage | 2 | 1 200 | 1 200 | 0 |
| workday | Michelin | 4 | 1 200 | 3 200 | 0 |
| workday | Pernod Ricard | 3 | 1 200 | 1 200 | 1 200 json-ld |
| workday | Renault | 4 | 1 200 | 3 200 | 0 |
| workday | Unibail-Rodamco-Westfield | 3 | 1 200 | 2 200 | 0 |
| workday | GN Store Nord | 9 | 1 200 | 8 200 | 0 |
| workday | Workday | 5 | 1 200 | 4 200 | 0 |
| workday | Aegon | 12 | 1 200 | 11 200 | 0 |
| workday | The Magnum Ice Cream Company | 2 | 1 200 | 1 200 | 0 |
| workday | RELX | 10 | 1 200 | 9 200 | 0 |
| workday | Universal Music Group | 7 | 1 200 | 6 200 | 0 |
| workday | Wolters Kluwer | 2 | 1 200 | 1 200 | 0 |
| workday | Basic-Fit | 6 | 1 200 | 5 200 | 0 |
| workday | CTP | 2 | 1 200 | 1 200 | 0 |
| workday | Vopak | 2 | 1 200 | 1 200 | 0 |
| workday | Lottomatica Group | 2 | 1 200 | 1 200 | 0 |
| workday | GEA Group | 3 | 1 200 | 2 200 | 0 |
| workday | Heidelberg Materials | 10 | 1 200 | 9 200 | 0 |
| workday | Regeneron | 12 | 3 200 | 6 200, 1 429 | 2 200 json-ld |
| workday | Kyndryl | 4 | 1 200 | 3 200 | 0 |
| workday | Shell | 12 | 1 200 | 11 200 | 0 |
| workday | Accenture | 5 | 1 200 | 4 200 | 0 |
| workday | Takeda | 2 | 1 200 | 1 200 | 0 |
| workday | Richemont | 9 | 2 200, 1 429 | 2 200 | 4 200 json-ld |
| workday | Alcon | 2 | 1 200 | 1 200 | 0 |
| workday | Galderma | 3 | 1 200 | 2 200 | 0 |
| workday | Logitech | 2 | 1 200 | 1 200 | 0 |
| workday | Julius Bär | 12 | 1 200 | 11 200 | 0 |
| workday | ING Group | 25 | 2 200, 1 429 | 8 200 | 14 200 json-ld |
| workday | Unilever | 6 | 1 200 | 5 200 | 0 |
