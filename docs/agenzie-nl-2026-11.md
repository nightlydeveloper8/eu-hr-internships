# Agenzie per il lavoro nei Paesi Bassi — 24 novembre 2026

**AGENZIE-NL** prepara Randstad Nederland, Tempo-Team e YoungCapital. Tutte le fonti sono disabilitate e in hold. Randstad e Tempo-Team riusano l’adattatore sitemap e il datore di gruppo già presente con la sua fonte carriere. Per YoungCapital, il nuovo datore è in hold anche nel registro aziende.

| Dominio | Accesso | URL offerte / candidati | HR confermati / idoneità non indicata | GET / byte / s HTTP |
|---|---|---:|---:|---:|
| randstad.nl | Sitemap e JobPosting ammessi | 2.904 / 3 | 1 / 2 | 5 / 1.122.281 / 1,832 |
| tempo-team.nl | Sitemap e JobPosting ammessi | 2.840 / 8 | 0 / 6 | 10 / 1.241.864 / 16,220 |
| youngcapital.nl | Sitemap e JobPosting pubblici | 3.545 / 21 | 6 / 6 | 24 / 3.033.883 / 5,794 |
| werkenbij.olympia.nl | Robots 200, verifica del disclaimer bloccata da CAPTCHA | non dimostrato | non dimostrato | 1 / 89 / 0,185 |
| startpeople.nl | Termini vietano download e raccolta | non dimostrato | non dimostrato | 2 / 143 / 0,358 |
| adecco.nl | Robots 404 su www.adecco.nl | non dimostrato | non dimostrato | 1 / 103 / 0,280 |
| asatalent.nl | Termini vietano download e raccolta | non dimostrato | non dimostrato | 1 / 90 / 0,203 |

- [Randstad, termini NL](https://www.randstad.nl/over-randstad/voorwaarden) e [Tempo-Team, termini NL](https://www.tempo-team.nl/over-tempo-team/voorwaarden/gebruikersvoorwaarden-algemeen) autorizzano la pubblicazione con attribuzione e link. Le [robots Randstad](https://www.randstad.nl/robots.txt) e [robots Tempo-Team](https://www.tempo-team.nl/robots.txt) dichiarano l’indice delle offerte.
- YoungCapital: [robots](https://www.youngcapital.nl/robots.txt), [indice](https://www.youngcapital.nl/sitemap.xml), [sitemap delle offerte](https://www.youngcapital.nl/sitemap/job_openings.xml). Stop ai soli URL olandesi ammessi. Nessun divieto esplicito di automazione individuato negli avvisi pubblici rivisti.
- [Robots Olympia](https://werkenbij.olympia.nl/robots.txt), [disclaimer Olympia](https://www.olympia.nl/voorwaarden/disclaimer/), [termini Start People](https://www.startpeople.nl/legal/disclaimer), [robots Adecco](https://www.adecco.nl/robots.txt), [termini ASA](https://asatalent.nl/legal/disclaimer).
- Pausa di almeno 2 s fra dettagli dello stesso host. Crawl delay dichiarato nei gruppi applicabili alle tre fonti: assente. Secondi HTTP al netto della pausa. Le consultazioni documentali esterne sono fuori telemetria. Per i tre inventari sono stati letti solo i candidati dagli slug. I titoli `Stagiair intercedent` e `Stagiaire intercedent` non superano il classificatore HR esistente. La copertura sugli slug esclusi è non dimostrato.

## Replay in staging

| Metrica | Prima | Dopo |
|---|---:|---:|
| ID totali | 944 | 954 |
| ID persi | 0 | 0 |
| Stage HR aperti nei Paesi Bassi | 240 | 249 |
| Candidature dirette nei Paesi Bassi | 26 | 26 |
| Lead NL | 213 | 214 |
| Recall aperto NL | 1/30 | 2/30 |

Le 9 nuove *current listing* sono 1 con idoneità confermata e 8 con idoneità non indicata. Sono verificate da sitemap e JobPosting fresco con scadenza futura. I 12 esiti YoungCapital ammessi dal classificatore restano lead prima della deduplicazione. Le pagine non pubblicano una scadenza, e il replay non verifica una candidatura per lo stesso ID. Il recall usa URL canonici sulle 30 righe del [ledger di confronto](https://github.com/nightlydeveloper8/eu-hr-internships/blob/cac8572b7cc32557a2a2b18c1feeeca633e4f2c9/docs/recall-fonti-ad-alta-densita-2026-11.csv). Budget aggiuntivo nominale: 180 s per gli shard 6, 12 e 15. Durata effettiva di `collect.yml`: non dimostrato.
