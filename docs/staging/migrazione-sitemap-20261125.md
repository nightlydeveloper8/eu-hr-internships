# Verifica della migrazione sitemap — 25 novembre 2026

Replay isolato con Python 3.12 su `a2274be`, al momento della prova. Il catalogo contiene 1.170 ID e 599 record con stato `open`. Applicando il filtro pubblico e la finestra di freschezza, gli stage visibili sono **589 → 589**. Il replay conserva tutti i 1.170 ID. Lo snapshot storico `8b7f061`, valutato allo stesso orario, dà 551 → 551 per effetto della freschezza.

| Host | Aperti prima → dopo | Candidati da sitemap | Secondi |
|---|---:|---:|---:|
| careers.loreal.com | 0 → 0 | 13 | 32,7 |
| careers.accor.com | 0 → 0 | 12 | 36,6 |
| jobs.infineon.com | 0 → 0 | 4 | 16,4 |
| careers.ing.com | 0 → 0 | 7 | 20,4 |
| www.asml.com | 0 → 0 | 7 | 24,2 |
| careers.abb | 0 → 0 | 4 | 32,4 |
| join.pmicareers.com | 0 → 0 | 4 | 33,7 |
| careers.adeccogroup.com | 0 → 0 | 128 | 118,5 |
| jobs.pirelli.com | 0 → 0 | 3 | 16,3 |
| careers.knorr-bremse.com | 0 → 0 | 2 | 8,4 |
| jobs.kuehne-nagel.com | 0 → 0 | 3 | 30,6 |
| www.werkenbijrandstad.nl | 0 → 0 | 1 | 19,1 |
| jobs.bosch.de | 0 → 0 | 25 | 54,1 |
| jobs.bosch.com | 0 → 0 | 0 | 24,1 |

Paesi invariati. AT 9, BE 27, CH 23, CZ 1, DE 77, ES 34, FI 1, FR 49, GB 1, HU 3, IT 113, LU 1, NL 232, PL 10, PT 2, SE 6. Altri paesi 0.

Nuovi ID, tutti da verificare: **Human Resources Summer Intern – London** (GB), **PRAKTIKUM (M/W/D) HR Business Partner ab März 2027** (DE), **stage recruitment en HR** (NL).

Il controllo dei titoli fallisce. La scheda L’Oréal [Praktikum HR Personalentwicklung, Ausbildung & Betriebliches Gesundheitsmanagement](https://careers.loreal.com/en/job/muggensturm/praktikum-hr-personalentwicklung-ausbildung-and-betriebliches-gesundheitsmanagement-m-w-d-ab-april-/3456/44773515328) ricade nel filtro di idoneità. Il filtro a monte esclude inoltre i candidati con termini da working student. Adecco esaurisce il budget durante la lettura e ABB, PMI e Kuehne+Nagel lasciano sitemap pendenti.

Su Bosch DE risultano 25 candidati letti, con cinque denominazioni societarie da verificare per l’ownership. La [scheda campione](https://jobs.bosch.de/job/Praktikum-im-Personalmanagement-mit-Schwerpunkt-Studierendenbetreuung-Abstatt-bei-Stuttgart?id=b96ffbae-cfbf-45d7-a478-55c0abc15bbe) associa nello stato della pagina ufficiale `idClient`, `idFS` e `applicationUrl`. Il controllo esistente cerca l’ID della scheda anche nell’URL di candidatura. La [FAQ Bosch](https://www.bosch.de/karriere/faq/) indirizza gli altri paesi al portale globale, dove le 11 sitemap lette non hanno restituito candidati da slug. Nessuna richiesta alla candidatura SmartRecruiters.

Il test parallelo ha impiegato circa 2 minuti. La stima conservativa di 26m02s somma al [ciclo di riferimento da 22m02s](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45661154805) il massimo budget aggiuntivo di un singolo shard (240 s), senza scontare i crawler generici. La stima vale per la configurazione e i budget provati. Il criterio sui titoli ha fermato il rollout prima di PR, CI remota, raccolta e publish.

## Misura sulle fonti generiche

Dei 1.871 ID attivi `auto-*` ed `employer-*`, 1.856 non hanno stage aperti attribuiti in nessuno degli ultimi 14 cataloghi pubblicati (`94f8144` → `a2274be`). Corrispondono a 1.819 host, deduplicati sulla URL carriere configurata. Il test ha letto `robots.txt` e al massimo una sitemap dichiarata, senza seguire redirect o indici figli, con il crawl delay applicabile. Le risposte bloccate, i redirect e i timeout sono esiti inconcludenti.

90 fonti mostrano **13.472 URL probabili di annunci** direttamente nelle sitemap. Altre 113 fonti mostrano 106 indici con riferimenti a sitemap figlie potenzialmente dedicate agli annunci. Il budget di due GET lascia ignoto il numero delle relative schede. I 203 sono candidati al riesame. Il conteggio usa il percorso URL e, quando richiesto dalla forma del percorso, un identificatore riconosciuto. Il [CSV](../migrazione-sitemap-candidati.csv) riporta le 50 fonti con più URL osservati.
