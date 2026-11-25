# Sospensione delle fonti generiche — 25 novembre 2026

Il [run della PR #145](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45678653956) ha pubblicato il catalogo `5881b91`. Artefatto, main e sito pubblico corrispondono. Aperti visibili 589 → 645, 1.170 ID conservati, nessun timeout, durata 23m03s.

La simulazione usa gli ultimi 14 cataloghi effettivamente pubblicati, da `3c502cd` a `5881b91`. Seleziona solo fonti `auto-*` ed `employer-*` risultate attive in tutti e 14 gli snapshot e senza stage aperti attribuiti. Sono protette tutte le [203 candidate al riesame](migrazione-sitemap-riesame-203.csv), di cui 202 rientrano nella selezione storica, e tutte le fonti associate a record aperti o lead, inclusi gli alias. Fra le fonti a zero storico, 70 sono protette per record correnti. I gruppi di esclusione possono sovrapporsi.

La configurazione sospende **1.594 fonti**, da 1.976 a 382 nella corsia regolare. Imposta l'hold per 1.586 datori che esaurirebbero le fonti attive, per impedire che il provisioning le riattivi. Il replay del merge conserva tutti i **1.204 ID**, con **645 → 645** stage visibili sullo stesso orologio. Il confronto delle fonti assegnate agli shard esclude soltanto gli ID autorizzati.

### Durata

**23m03s misurati → 23m03s stimati.** Il modello usa le durate osservate per fonte, sei worker per shard, il massimo tra la durata della fonte più lenta e la somma dei tempi divisa per i worker. Il collo di bottiglia stimato è invariato. La riduzione di lavoro negli shard va misurata nel ciclo reale. Il rollback scatta oltre 45 minuti, al timeout di uno shard, alla perdita di un ID o al calo di oltre il 3% al netto della freschezza.
