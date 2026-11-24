# Agenzie per il lavoro in Spagna — 24 novembre 2026

Il lotto **AGENZIE-ES** prepara Adecco España e Grupo RAS. Il codice condiviso proviene dal [lotto IT-agenzie](https://github.com/nightlydeveloper8/eu-hr-internships/blob/cac8572b7cc32557a2a2b18c1feeeca633e4f2c9/docs/fonti-ad-alta-densita-2026-11.md). Il ramo parte da main `2cdbdd3` e riprende il codice riutilizzabile della PR #138. I registri italiani della #138 sono esclusi dal diff. Per NL, FR, DE e PL sono presenti le regole etichettate, mentre le misure di inventario, le simulazioni e il recall sono **non dimostrato**.

## Accesso e resa osservata

Il preflight usa il robots esatto di ogni host. I GET diretti includono robots, indici e dettagli candidati. I secondi HTTP sono cumulativi e non includono tempi di attesa. La pausa impostata è 2 s per host salvo Gi Group, dove è stata rispettata una pausa di almeno 120 s dopo l'indice. Consultazioni documentali tramite motore esterno fuori dalla telemetria. Gli zeri del triage riguardano i soli slug letti.

| Dominio | Esito | URL di offerta in sitemap | Candidati | HR confermati / non indicati | GET / byte / s HTTP |
|---|---|---:|---:|---|---:|
| Randstad ES | Escluso. Il paragrafo sulle attività vietate nomina software, script e Robot/Crawler | non dimostrato | non dimostrato | non dimostrato | 1 / 1.131 / 0,204 |
| Adecco ES | Sitemap nazionale e JobPosting pubblici sullo stesso host. Lettura ammessa sui percorsi verificati | 4444 | 8 | 8 / 0 | 12 / 4.239.090 / 24,743 |
| EULEN Flexiplán | Sitemap 403 con pagina di protezione. Stop | non dimostrato | non dimostrato | non dimostrato | 2 / 5.667 / 0,449 |
| Grupo RAS | Sitemap e JobPosting Teamtailor pubblici sul tenant. 45 URL nel file, 34 con percorso di vacancy | 34 | 19 | 0 / 19 | 21 / 1.097.251 / 7,296 |
| Grupo Crit | Redirect a pagina pubblica con 99 link di paginazione. Sitemap 404, pagina indice senza inventario JSON o JobPosting | non dimostrato | non dimostrato | non dimostrato | 4 / 68.499 / 1,215 |
| Intalentia | Sottoindice e JobPosting leggibili. Conteggi di staging. Termini limitano l'uso dei contenuti all'ambito privato | 14 | 1 | 1 / 0 | 5 / 123.709 / 0,775 |
| Gi Group ES | Alias con redirect a es.gigroup.com, robots rivisto separatamente. Sitemap di offerte leggibile | 353 | 0 | non dimostrato | 4 / 112.885 / 1,387 |
| Synergie ES | Dieci sottoindici editoriali e istituzionali. Indice strutturato di vacancy non dimostrato | non dimostrato | non dimostrato | non dimostrato | 3 / 176.335 / 0,848 |
| Manpower ES | Il gruppo robots `*` vieta tutti i percorsi | non dimostrato | non dimostrato | non dimostrato | 1 / 2.286 / 0,111 |

- Randstad e Manpower hanno terminato il preflight prima dei GET alla sitemap. [Avviso legale Randstad](https://www.randstad.es/aviso-legal/) · [Robots Manpower](https://www.manpower.es/robots.txt).
- Adecco dichiara l'indice paese nel sitemap dei job. Il footer porta al registro legale ES. Nei riferimenti pubblici del percorso rivisto non è emerso un divieto esplicito alla lettura automatizzata. I JobPosting validi contengono sede spagnola, data e scadenza. [Indice pubblico](https://www.adecco.com/jobsindex.xml) · [Registro legale](https://www.adeccogroup.com/es-es/registro-legal).
- RAS pubblica l'indice e schede pubbliche con data, titolo, indirizzo e un frame di candidatura con la stessa identità della vacancy. La documentazione Teamtailor associa lo stato Published alla disponibilità sul career site. La verifica current listing usa l'indice pubblico, la pagina ufficiale fresca con JobPosting e il frame esattamente sotto l'URL della stessa vacancy. La candidatura diretta richiede una prova distinta. [Robots RAS](https://empleo.gruporas.es/robots.txt) · [Condizioni del tenant](https://empleo.gruporas.es/privacy-policy) · [Stati Teamtailor](https://support.teamtailor.com/en/articles/2611060-job-and-job-ad-statuses).
- Intalentia ha un sottoindice specifico per le offerte. Il JobPosting aperto conferma un pubblico studentesco, anche in alternativa ai neolaureati. Il sito autorizza l'uso privato dei contenuti e richiede autorizzazione per altri usi. Rimane in staging e fuori dal lotto. [Avviso legale](https://intalentia.com/aviso-legal/).
- Il markup HTML della pagina indice di Grupo Crit ha link a pagine distinte e 10 offerte nella prima pagina. Un manifesto strutturato e un totale di vacancy dimostrato restano assenti dalla verifica. Non è stato usato un endpoint ricostruito. [Indice pubblico](https://jobs.grupo-crit.com/jobs) · [Avviso legale](https://jobs.grupo-crit.com/legal-notice?company=crit-desk&locale=es).
- Il gruppo generico di Gi Group permette i percorsi osservati. Il crawl delay di 120 s compare nel gruppo Bingbot e qui è rispettato come limite prudenziale. Con zero candidati dagli slug non è stato aperto un dettaglio. Il sito Synergie dichiara un indice WordPress che non contiene un sottoindice di vacancy nei percorsi osservati. [Robots Gi Group](https://es.gigroup.com/robots.txt) · [Sitemap Gi Group](https://es.gigroup.com/additional-sitemap-es.xml) · [Robots Synergie](https://www.synergie.es/robots.txt).

## Simulazione e recall

Replay di risposte live in staging attraverso lo stesso classificatore, verificatore e finalizzatore. La regola ES riconosce anche termini catalani su RAS, come `becari` e `selecció de personal`. Gli stage generici ammessi mostrano «Student eligibility not stated – check with the employer». Le prove separate di candidature non sono state raccolte. Le 40 righe ES del [ledger della PR #138](https://github.com/nightlydeveloper8/eu-hr-internships/blob/cac8572b7cc32557a2a2b18c1feeeca633e4f2c9/docs/recall-fonti-ad-alta-densita-2026-11.csv) sono state abbinate tramite URL canonico o ID di vacancy nello stesso host.

| Metrica | Prima | Dopo |
|---|---:|---:|
| ID di catalogo distinti | 944 | 971 |
| ID persi | 0 | 0 |
| ES stage HR aperti | 3 | 30 |
| Nuove current listing | 0 | 27 |
| Nuove candidature dirette | 0 | 0 |
| Recall aperto ES | 0/40 | 5/40 |

Budget proposto per fonte di 180 s, massimo 65 richieste e pausa di 2 s. Con la matrice esistente di 16 shard, RAS va nello shard 0 e Adecco nello shard 9. Il tetto nominale aggiuntivo è quindi +3 minuti per shard interessato. Il tempo incrementale end-to-end di `collect.yml` è **non dimostrato**. Nessun deploy, merge o attivazione. Il provisioning è idempotente e l'adattatore rifiuta il canale anche se una modifica accidentale al flag enabled lascia il hold presente.

Controlli in copia scrivibile con Python 3.12.14. Passano 588 test Python, 53 Node, 129 esempi di valutazione con zero errori, provisioning, copertura, build e validazione. Le fonti degli altri paesi non sono state provate.
