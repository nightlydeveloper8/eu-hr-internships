# Migrazione delle sitemap corporate — 24 novembre 2026

Replay sul catalogo baseline 8b7f061. Sono attivati solo i percorsi che hanno prodotto current listing. I vecchi collector sono sostituiti se coprono lo stesso host e la baseline non contiene aperti attribuiti a loro. I percorsi più ampi mantengono il vecchio collector e condividono lo shard. I percorsi senza prova restano in hold e non modificano le fonti esistenti. Nessuna richiesta alle candidature.

| Host | Prima → dopo | Esito | Vecchia fonte | Nuova fonte | GET |
|---|---:|---|---|---|---:|
| careers.loreal.com | 0 → 0 | hold | auto-l-oreal | sitemap-careers-loreal-com | 16 |
| careers.danone.com | 0 → 3 | sostituita | employer-danone | sitemap-careers-danone-com | 10 |
| careers.roche.com | 0 → 2 | sostituita | employer-roche | sitemap-careers-roche-com | 18 |
| careers.accor.com | 0 → 0 | hold | auto-accor | sitemap-careers-accor-com | 1 |
| jobs.infineon.com | 0 → 0 | hold | employer-infineon | sitemap-jobs-infineon-com | 1 |
| careers.thalesgroup.com | 0 → 3 | sostituita | employer-thales | sitemap-careers-thalesgroup-com | 16 |
| careers.ing.com | 0 → 0 | hold | employer-ing | sitemap-careers-ing-com | 10 |
| www.asml.com | 0 → 0 | hold | auto-asml | sitemap-www-asml-com | 11 |
| jobs.sap.com | 0 → 3 | sostituita | auto-sap | sitemap-jobs-sap-com | 12 |
| careers.abb | 0 → 0 | hold | employer-abb | sitemap-careers-abb | 16 |
| careers.allianz.com | 0 → 2 | sostituita | employer-allianz | sitemap-careers-allianz-com | 15 |
| join.pmicareers.com | 0 → 0 | hold | auto-philip-morris-international | sitemap-join-pmicareers-com | 16 |
| careers.adeccogroup.com | 0 → 0 | hold | employer-adecco-group | sitemap-careers-adeccogroup-com | 59 |
| jobs.pirelli.com | 0 → 0 | hold | auto-pirelli | sitemap-jobs-pirelli-com | 8 |
| careers.knorr-bremse.com | 0 → 0 | hold | auto-knorr-bremse-ag | sitemap-careers-knorr-bremse-com | 4 |
| jobs.kuehne-nagel.com | 0 → 0 | hold | employer-kuehne-nagel | sitemap-jobs-kuehne-nagel-com | 15 |
| www.werkenbijrandstad.nl | 0 → 0 | hold | auto-randstad-groep-nederland | sitemap-www-werkenbijrandstad-nl | 9 |

**589 → 602 aperti**, 2 nuovi ID e zero ID persi. Stima conservativa 27m52s, 23m52s di baseline più il budget seriale aggiuntivo massimo per shard. Gli alias usano il medesimo URL o l’identificatore pubblicato e conservano gli ID del catalogo.

| Paese | Prima → dopo |
|---|---:|
| AT | 7 → 7 |
| BE | 26 → 27 |
| BG | 0 → 0 |
| HR | 0 → 0 |
| CY | 0 → 0 |
| CZ | 0 → 1 |
| DK | 0 → 0 |
| EE | 0 → 0 |
| FI | 1 → 1 |
| FR | 45 → 49 |
| DE | 75 → 77 |
| GR | 0 → 0 |
| HU | 2 → 3 |
| IE | 0 → 0 |
| IT | 104 → 104 |
| LV | 0 → 0 |
| LT | 0 → 0 |
| LU | 1 → 1 |
| MT | 0 → 0 |
| NL | 252 → 252 |
| PL | 8 → 9 |
| PT | 2 → 3 |
| RO | 0 → 0 |
| SK | 0 → 0 |
| SI | 0 → 0 |
| ES | 30 → 32 |
| SE | 6 → 6 |
| CH | 29 → 29 |
| GB | 1 → 1 |

## Titoli nuovi e promossi

| ID | Paese | Titolo | Stato |
|---|---|---|---|
| efb97f2166e7b9828d0c | BE | Stage Ressources humaines | open |
| 06fe7ca830c0856c4d9d | CZ | SAP iXp Intern - Recruiting Associate (Tech TD) (limited full-time) | open |
| 1576057fe613bb7279a7 | DE | Praktikum HR Management (m/w/d) Fokus: Recruiting | open |
| 412e9fb5bb384d80202c | DE | Praktikum im Bereich: Recruitment Strategy & Operations (m/w/d) | open |
| 714f47bbc72420b610a8 | ES | HR Learning Intern | open |
| 2bf1791900dad311cc62 | ES | HRBP Intern (m/f/d) | open |
| 892f8db8801d94e19666 | FR | STAGE - CHARGÉ DE RECRUTEMENT (F/H) | open |
| eebb7dd0cecadb034301 | FR | STAGE - Chargé(e) de Formation & Projets RH - janvier 2027 - (H/F) | open |
| 20e6f9c433c432b16902 | FR | STAGE - Talent Acquisition Partner - F/H | open |
| c8f5f0bc4354c2b53e2a | FR | STAGE Assistant(e) RH – F/H | open |
| 0cf3242bd190f71e4f01 | HU | SAP iXp Intern – Tech Recruitment (limited contract) | open |
| e77cadf41d57a10ca395 | PL | HR & Administrative Support Intern | open |
| 3ff388015cf60711e4dc | PT | EMEA Recruitment Admin Intern | open |
