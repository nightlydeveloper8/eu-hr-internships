# Ripresa operativa della mappatura e raccolta — 5 novembre 2026

Il registro passa da **530 a 842 datori**. Il catalogo passa da **16 a 22 opportunità HR aperte: 20 stage e 2 posizioni per studenti lavoratori**. I datori con monitoraggio configurato passano da 13 a **40**. L'ultima raccolta completa è riuscita su tutti i 40 canali, con verifica dei collegamenti delle offerte incluse. Il dettaglio dei risultati è in `data/coverage.json` e `docs/integrazione-canali-novembre-2026.md`.

## Nuova mappatura eseguita

- [Università di Bologna — aziende partecipanti](https://eventi.unibo.it/careerday/aziende-partecipanti-2026): esaminate 174 schede pubbliche; aggiunti 148 datori con sito dichiarato e collegamento HTTPS verificato o registrato come ancora da revisionare. Trovate 92 pagine carriera accessibili e poi esaminate per i canali di raccolta.
- [Confindustria Veneto Est — gruppi merceologici](https://bcomcve.confindustriavenest.it/gruppi-merceologici): letti i 21 elenchi settoriali pubblici e selezionati 200 candidati, distribuiti fra settori e dopo deduplicazione per nomi e domini conosciuti. Aggiunti 164 datori dopo verifica dei siti dichiarati. Sono state esaminate anche le loro 48 pagine carriera trovate. Le funzioni premium non sono state utilizzate; non sono stati raccolti contatti personali.

La seconda fonte permette di includere produttori, imprese familiari, servizi locali e operatori settoriali, oltre ai datori presenti negli eventi universitari. Le dimensioni e la capacità HR richiedono evidenze: nessuna impresa viene etichettata come media dal nome, dal settore o dalla sola appartenenza associativa.

I vecchi collegamenti HTTP dichiarati negli elenchi sono stati verificati anche in HTTPS mantenendo identici dominio e percorso. Il registro contiene la destinazione sicura solo dopo una risposta effettiva; gli insuccessi restano nell'audit. Il primo passaggio aveva aggiunto 107 aziende; la verifica HTTPS ne ha aggiunte altre 57.

La deduplicazione comprende nomi, domini e i gruppi già esplicitamente revisionati. Non costituisce una ricostruzione completa di tutti i gruppi societari: altre affiliazioni restano da controllare. Le società senza prove di un canale o di attività HR rimangono candidati da qualificare.

## Italia: quantità e verifica restano distinte

Il registro contiene ora **325 candidati per l'Italia**. Sono documentate sedi ufficiali per **10 datori**, di cui uno con raccolta HR configurata e verificata in Italia: Tyche Bank, con HR Intern a Bologna. Questo non soddisfa ancora la soglia strategica di 300 datori con presenza confermata: il divario rimane 290. Per gli altri candidati vanno verificati identità, sedi, dimensioni, funzione HR e canali effettivi.

La lettura dei dati aziendali `Organization`/`LocalBusiness` ha confermato sedi per nove datori della fonte territoriale; richiede un URL dell'organizzazione appartenente al sito ufficiale, città e paese espliciti. Un dominio italiano o l'appartenenza all'associazione non sono usati per dedurre una sede. Le regioni non riconosciute rimangono sconosciute.

## Accessi rimasti da approfondire

L'elenco di Bergamo restituisce HTML al posto di robots leggibile; la pagina UPFeina restituisce 403. Non sono stati aggirati. Il campione Talent Days esaminato comprende schede senza sito ufficiale dichiarato: non è stato importato come se fosse una nuova lista di aziende verificate. Queste fonti richiedono ulteriori ricerche o fonti alternative nei rispettivi paesi.

Le query e gli obiettivi per gli altri paesi UE restano compiti da eseguire. Questa tranche non completa la copertura europea; il prossimo lavoro deve ampliare gli altri paesi e qualificare i candidati già presenti.

## File riproducibili e audit

- `scripts/map_unibo_employers.py`: schede pubbliche e siti dichiarati.
- `scripts/map_veneto_employers.py`: elenchi settoriali pubblici, selezione distribuita e verifica siti.
- `scripts/inspect_career_channels.py`: verifica dei canali con filtri per paese e metodo di scoperta.
- `scripts/verify_employer_addresses.py`: verifica di indirizzi aziendali espliciti.
- `docs/unibo-mapping-audit.json`, `docs/veneto-mapping-audit.json`, `docs/veneto-https-review.json`, `docs/employer-address-audit.json`: esiti e limiti della ricerca.
- `docs/country-research-progress.json`: candidati e sedi confermate per tutti i 27 paesi.

Sono stati aggiunti connettori pubblici e controlli di regressione per feed, titoli, localizzazione, differenza fra stage e lavoro per studenti e dati aziendali. Le informazioni ancora sconosciute rimangono esplicite.
