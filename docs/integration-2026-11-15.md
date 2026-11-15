# Integrazione delle PR pronte — 15 novembre 2026

Autorizzazione dell'utente: squash and merge di tutto ciò che è pronto.
Base: main `adf4c69`, con PR #38 già integrata. I checkout altrui sono preservati.

| PR | Contenuto incluso | Limite mantenuto |
|---|---|---|
| #20 | Drenthe, fonti Unigarant/ASTRON/Interzorg, feed e identità Workday | Nessuna vacancy forzata verified; inventari incompleti restano tali |
| #26 | Evidenze audit Dynamic ATS storico, conservate nella cronologia PR | Nessuna attivazione aggiuntiva |
| #27 | Chiusura ufficiale nominativa e telemetria upstream | Solo GET fresco, stessa URL e titolo noto; niente chiusura da cache/assenza |
| #28 | Publisher ufficiali per source/host esatti | Gruppi e controllate non sono grant; CI cancellata sostituita da validazione combinata |
| #32 | Regressione del ciclo di vita allarme zero verified | Nessun incidente o messaggio provocato manualmente |
| #33 | Coda offline ATS europea | Nessuna fonte nuova abilitata |
| #34 | Discovery directory delimitata e review queue | Seed live OFF, nessun onboarding automatico |
| #35 | Audit due cicli DIM | Storico, zero incremento attribuito |
| #36 | Preflight Wikidata storico bloccato | Nessuna query live o workaround |
| #37 | Esclusione asset tecnici dalle ricerche ATS | Nessuna rimozione dei vincoli robots |
| WEBO | Fonte index visibile e candidatura email esplicita | Inventario parziale, nessuna candidatura inviata |

Le sovrapposizioni di codice sono risolte nella PR unica. Il riepilogo corrente
non viene sovrascritto dai checkpoint storici delle altre PR, che restano nella
loro cronologia e nei rapporti specifici. Dopo il merge consolidato le PR originali
sono chiuse come incorporate, non presentate come singoli squash merge.

## Verifica integrata

356 test Python, 26 Node, 64 esempi HR senza errori; validazione registry/catalogo,
generazione coverage e build riusciti. Test Node reali degli script workflow con
GitHub Issues simulato, senza rete. Due piccoli conflitti di codice risolti
combinando le modifiche, senza ripristinare i vecchi host permissivi.

Confronto catalogo main: tutti i 341 ID conservati, nessun cambio di stato,
last_verified_at o application proof. Solo il campo region_codes di Landal
95921c56e78ac43dffa1 passa da [] a [NL13] dalla sede Nooitgedacht revisionata.
1.887 aziende e 1.931 source; tutti gli ID precedenti di entrambi i registri
sono conservati. Nessun catalogo storico sovrascrive i dati recenti.

## Produzione e criterio di completamento

I test non equivalgono a stage nuovi. WEBO è verificato nel pilota circoscritto,
non ancora aggiunto al conteggio di produzione; la prima raccolta ordinaria deve
leggere e verificare di nuovo la candidatura. Le altre nuove configurazioni non
promettono un numero di stage. Vedere JSON live WEBO e report Drenthe.

Il merge su main avvia il workflow esistente. I push più recenti cancellano quelli
precedenti secondo la concorrenza già configurata: nessuna raccolta manuale.
Controllare test, 16 shard, publish e dati di produzione, distinguendo Cloudflare.
Nessuna nuova automazione AI o promessa di verifica futura automatica.
