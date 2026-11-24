# Polonia — AGENZIE-PL

Verifica del 24 novembre 2026. Randstad Polska è l’unico dominio ammesso nel lotto. La fonte e il datore sono disabilitati e in hold.

| Host | Esito |
|---|---|
| www.randstad.pl | Robots 200 e avvisi pubblici del sito rivisti, senza divieto esplicito individuato per le rotte lette. Otto sottoindici vacancy con 5.710 URL distinti, comprese varianti di lingua. Il lotto usa i due sottoindici polacchi con 1.432 URL. Venticinque URL candidati equivalgono a sette ID, tutti letti in polacco. [Indice](https://www.randstad.pl/sitemaps/sitemap.xml) · [Avvisi del sito](https://www.randstad.pl/) |
| www.adecco.pl e www.adecco.com | Il primo robots risponde 404. Sul secondo i [termini PL](https://www.adecco.com/pl-pl/warunki-uzytkowania) vietano espressamente l’estrazione. |
| www.manpower.pl | Robots 200. Il [regolamento](https://www.manpower.pl/pl/regulamin-serwisu) riserva l’uso del sito alla sfera personale. |
| www.michaelpage.pl | [Termini](https://www.michaelpage.pl/regulamin-korzystania-ze-strony) rivisti. Sitemap 503 con pagina di manutenzione. La riga del benchmark resta senza prova attuale. |
| www.hays.pl | Robots in redirect a una rotta localizzata di un altro host. Accesso sull’alias indeterminato. |
| pl.gigroup.com | 552 URL nel sottoindice nazionale. Un solo candidato dagli slug, tenuto fuori dal lotto dopo che la revisione automatica ha bloccato l’apertura del dettaglio per dubbio sui termini applicabili. [Regolamento](https://pl.gigroup.com/regulamin/) |
| pl.trenkwalder.com | [Sitemap vacancy](https://pl.trenkwalder.com/sitemap-jobs) con 185 identificatori opachi. Triage per titolo indeterminato, zero dettagli letti. |

I GET hanno identificato People Placement e rispettato la pausa di almeno 2 s per host, elevata a 10 s per Trenkwalder. Preflight di 30 GET, 4.621.793 byte e 14,645 s HTTP, escluse pause e consultazioni documentali esterne.

## Simulazione

| Metrica | Prima → dopo |
|---|---:|
| ID distinti | 944 → 951 |
| ID persi | 0 |
| Stage HR aperti PL | 0 → 7 |
| Candidature dirette PL | 0 → 0 |
| Recall aperto PL | 0/20 → 0/20 |

Replay con le risposte catturate, adapter e finalizzatore reali, baseline del 24 novembre alle 07:56 UTC. I sette JobPosting ufficiali sono ancora nell’inventario e pubblicano una scadenza futura. La regola PL non ha trovato prove sufficienti di idoneità individuale né esclusioni nei sette dettagli. Le sette *current listing* mantengono tutte «Student eligibility not stated – check with the employer». La ricorrenza della stessa scadenza nelle schede e le date iniziali di pubblicazione storiche rendono particolarmente importante la presenza nell’inventario corrente. Il [ledger #138](https://github.com/nightlydeveloper8/eu-hr-internships/blob/cac8572b7cc32557a2a2b18c1feeeca633e4f2c9/docs/recall-fonti-ad-alta-densita-2026-11.csv) è abbinato per URL canonico o ID di catalogo già dimostrato.

Budget nominale aggiuntivo per lo shard 7 di 180 s, 40 richieste, pausa di 2 s. Gli altri shard hanno incremento zero per il lotto. Il replay ha fatto 16 letture logiche, inclusa la rilettura di ogni scheda per la verifica. Incremento end-to-end del workflow da dimostrare.
