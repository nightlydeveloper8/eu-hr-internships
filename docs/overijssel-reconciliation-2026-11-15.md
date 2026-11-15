# Overijssel — primo stage verificabile e integrazione proposta

## Risultato corrente, 15 novembre 2026

**WEBO — Stage HRM, Rijssen:** verifica live della stessa vacancy e delle istruzioni
esplicite per candidarsi via l'indirizzo email pubblicato. Prova policy v2 nel JSON
`overijssel-webo-live-verification-2026-11-15.json`, timestamp 18:21:57 UTC.
Nessuna email o candidatura inviata; `delivery_verified=false`.
Incremento nel pilota circoscritto: 0 → 1. Incremento in produzione: 0 fino a
integrazione autorizzata e nuova raccolta ordinaria; catalogo main non modificato.

Il verificatore riconosce ora anche l'invito esplicito olandese a candidarsi
 direttamente via email quando non è prescritto un CV. Serve sempre l'indirizzo
revisionato nel mailto, la stessa vacancy attuale e un invito chiaro. Contatto per
sole domande, negazione, indirizzo distante o diverso e vacancy discordante restano
esclusi. La modifica è riutilizzabile per gli altri canali email già revisionati.

## Fonte quotidiana proposta

Un datore `webo`, una fonte `auto-webo` con adapter `employer-index` esistente,
solo host `www.webo.nl`, massimo 80 richieste/120 secondi, nessun browser.
La fonte legge la pagina careers ufficiale e il seed della vacancy osservata;
seguono normale lettura delle schede, estrazione della sede e verifica.
La nuova opzione opt-in `include_index_visible` permette a un seed visibile senza
JobPosting di entrare nell'inventario, senza dichiararlo aperto: sede e candidatura
sono ancora verificate separatamente. Solo il formato visible già revisionato
può usarla; la URL deve corrispondere al pattern delle vacancy e avere un H1 HR.

La pagina completa `/vacatures/` è andata in timeout. La pagina alternativa
`/werken-bij-webo/` è stata letta: quattro collegamenti osservati, senza lo stage
nel blocco in evidenza. Lo stage è perciò un seed osservato, non una URL inventata.
**Inventario parziale e nessuna chiusura per assenza.** Non si dichiara copertura
completa di WEBO né di Rijssen-Holten o Overijssel. La fonte è proposta in branch;
non attiva in main. Tutte le future verifiche richiedono nuove letture, non replay.

## Altri canali e geografia

- De Nieuwe Zaak: API pubblica Recruitee leggibile, 12 offerte; l'ID HR 2780092
  coincide con il data-offer-slug della pagina aziendale nuova. Identità collegata,
  candidatura ancora non verificata: submit disabilitato nel markup ricevuto.
- Groothuis Bouwgroep: il link AFAS pubblicato è escluso da robots. Accesso fermato;
  nessun aggiramento e nessuna fonte attivata. I form generici in pagina non sono
  sufficienti a dichiarare un'altra candidatura della stessa vacancy.
- CBS: import del quadro comunale fermato da robots HTTP 406. Nessun codice
  comunale o settlement inventato. Il workplace WEBO documenta Rijssen/NL21;
  municipality e municipality_code restano null. Associazione storica a
  Rijssen-Holten mantenuta come ricerca, non import CBS.
- Le 171 schede OVI e le piste in 25 comuni rimangono materiale storico non
  deduplicato, non copertura completa. Riusi Elis, Wagenborg e Countus nel JSON.

## Misurazione e verifiche

Le nuove letture di questa fase sommano 13 richieste conteggiate, 724.122 byte,
128,295 secondi-fonte cumulati; non sono tempo a muro né costo monetario.
WEBO verifica: 3 richieste / 34,533 s. Zero rendering, autenticazioni o submit.
Le precedenti letture restano separate nel checkpoint JSON.

Quattro test nuovi coprono istruzioni positive/negative, mailto e identità,
seed visible e due finalizzazioni offline: un solo nuovo ID sintetico, tutti gli
ID esistenti conservati e sede NL21. Le fixture non attestano nuove letture live.
I 1.882 datori e 1.926 source preesistenti restano identici; catalogo intatto.
Dimensione WEBO sconosciuta. Nessuna dipendenza o automazione aggiunta.

Prossimo passo dopo review: eventuale merge specificamente autorizzato e misura
della prima raccolta ordinaria WEBO; poi avanzare sul lead successivo accessibile.
La PR #38 rimane indipendente e non integrata. Nessuna raccolta completa manuale.
