# Lotto 04 — tre fonti ufficiali pronte per raccolta quotidiana

Il pilota live del 16 novembre 2026 dimostra **due stage distinti candidabili e una posizione working student**. Questa verifica non è una pubblicazione in produzione e non costituisce copertura nazionale completa.

| Datore | Paese | Tipo | Inventario | Candidatura |
|---|---|---|---:|---|
| Hotel TwentySeven | NL | Stage HR, Amsterdam | 24 pubblicate | URL /c/new pubblicato dal feed, stesso titolo/datore, modulo visibile abilitato |
| Bundl | BE | HR Intern, Antwerp | 6 pubblicate | URL /c/new pubblicato dal feed, stesso titolo/datore, modulo visibile abilitato |
| Franklin Institute | DE | Werkstudent/Praktikant HR, München, conteggio working student | 11 pubblicate | URL /c/new pubblicato dal feed, stesso titolo/datore, modulo visibile abilitato |

I tre collegamenti azienda→tenant sono espliciti sulle pagine ufficiali: Hotel homepage CAREERS; Bundl /internships; Franklin /career, che pubblica anche lo stesso annuncio HR. Prove e hash delle risposte nel JSON di revisione; raw temporanei non necessari alla raccolta quotidiana.

## Correzione riutilizzabile

Il client chiedeva JSON anche quando leggeva documenti. Due CMS rispondevano con frammenti JSON senza la navigazione Careers: Hotel (Duda) e The Social Hub (Optimizely). Il nuovo Accept predefinito chiede HTML/XHTML; Client.json richiede esplicitamente JSON, robots.txt testo semplice. Identità del bot, robots, host, redirect, budget e limiti invariati, anche nel fallback TLS. Sei regressioni verificano rappresentazioni, budget, scope, robots e identità del bot; tre feed API reali sono stati letti con il codice finale.

## Altri quattro indizi

- Kickmaker: corporate→WTTJ confermato, pagina intermedia 403; nessun retry, collegamento all'esatto tenant Lever incompleto.
- Zero Motorcycles: /employment contiene il widget Recruitee ma il tenant esatto non è stabilito; nessuna integrazione.
- The Social Hub: HTML corretto e un asset JS pubblicato letti, senza prova del tenant Greenhouse o della sede associata al ruolo; nessuna integrazione.
- Settels Savenije: widget aziendale 28485 e companyId ATS coincidono, ma il pilota non supera il controllo del nome del datore e l'inizio osservato è febbraio 2026. Non si promuove la candidatura né si attiva la fonte.

## Costi, conteggi e limiti

Tre piloti ammessi: **15 richieste logiche, 6,924 secondi-fonte, 3.768.689 byte**. Tutte le fasi di ricerca e diagnosi di questo lotto, comprese le rappresentazioni CMS errate e i quattro indizi non integrati: **52 richieste, 26,114 secondi-fonte, 11.849.666 byte**, zero rendering, nove query web. Sono conteggi logici comprensivi di robots; i redirect non hanno contatore HTTP separato. Un asset Social Hub pesa circa 4,7 MB senza offrire un collegamento ATS utile: non è previsto nel monitoraggio quotidiano.

Budget quotidiano per ciascuna nuova fonte: massimo 12 richieste/45 secondi, un solo host Recruitee esatto, nessun rendering, nessun invio o login. Inventario completo limitatamente alle offerte pubblicate restituite dal feed; closure_complete=false, nessuna chiusura per assenza. Gate Dynamic ATS e schedule invariati.

Bundl richiede inglese **e** olandese. Franklin richiede tedesco e inglese nel testo; l'estrattore attuale lascia sconosciuto questo costrutto tedesco. Hotel: lingua di lavoro sconosciuta. Non si dichiara alcuna offerta English-only. Dimensioni societarie sconosciute; nessuna qualifica PMI inferita.

Simulazione offline su catalogo 355 record: 358 dopo integrazione, tutti i 355 ID conservati, secondo ciclo identico. Non si importano nel catalogo risultati del pilota: solo la raccolta ordinaria dopo il merge può attestare incremento e costi in produzione.

Registri applicati atomicamente (tre aziende + tre fonti attive). Rollback: rimuovere entrambe le serie insieme; disabilitare solo le fonti attiverebbe il fallback generico del provisioner.

Validazione: 413 test Python, 26 Node, 64 esempi di classificazione, generazione coverage e build. PR #44 precedente effettivamente integrata con squash 464d87c; ciclo ordinario #43898333473 riuscito con 18 job verdi, dati b5e14d0: 356 record e 26 stage verificati, ID precedenti conservati, inglese BSH documentato. Dettagli in pr44-first-production-cycle-2026-11-16.json. Questo lotto richiede ancora PR, CI, squash e misura del primo ciclo ordinario prima di attestare produzione.
