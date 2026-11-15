# Raccolta ufficiale: errori storici, parsing e deriva dei checkpoint

Base: `a70117cee3697bcf61238a1999e32baa916dca9a`, 15 novembre 2026.
Collegamento: Issue #18. Nessun incremento di candidature dimostrato da questo fix.

## Diagnosi corretta

I quattro motivi `sequence item ... NoneType found` nel catalogo non sono errori
prodotti il 15 novembre: le osservazioni risalgono al 6–7 novembre. Il join del
verificatore dei form è già stato corretto nella PR #19. Non serve rifare quel fix.
Il confronto riproducibile di due raccolte reali, 14 e 15 novembre, è in
`collection-priority-audit-2026-11-15.json`; script offline:

```sh
python scripts/audit_collection_backlog.py \
  --before a33e530f05a2bf1e6852b8fafce6766cee9a1d64 \
  --after a70117cee3697bcf61238a1999e32baa916dca9a \
  --output /tmp/collection-priority-audit.json
```

- Due cicli: 19 → 19 stage HR verified freschi rispetto a ciascuno snapshot;
  un nuovo ID non verificato, nessun ID rimosso.
- Tilburg: 108 record storici su host esterni a quello dichiarato; 99 osservazioni
  antecedenti all'ultimo ciclo, tutte del 7 novembre. I 71 motivi di budget contenuti
  in quel gruppo non provano 71 tentativi falliti oggi. Il ciclo odierno legge 70
  pagine, restituisce zero record e conserva 39 URL pendenti. Non si riassegnano
  gli annunci esterni, non si aggiornano le loro verifiche e non si chiudono per assenza.
- DAF: il report odierno riporta letture di pagine Randstad, 86 richieste, 100,46 s,
  2.332 URL pendenti e zero record. I due errori form storici restano invariati.
- Becton Dickinson: blocchi robots sulle pagine di ricerca, zero record odierni;
  nessun aggiramento. Belsimpel: 23 record raccolti, zero match; il vecchio errore
  non dimostra né apertura né chiusura della vacancy storica.

## Due difetti riprodotti e correzione

1. `Document` usa attributi HTML opzionali in concatenazioni e regex. HTMLParser
   restituisce `None` quando `class`, `itemprop` o `data-icon` non hanno valore;
   il documento può interrompersi. Normalizzati quei valori a testo vuoto nel solo
   estrattore di documento. I controlli dei form, disabled/hidden e policy v2 restano
   invariati. Il report Tilburg contiene un errore compatibile; la pagina corrente
   restituisce 403, quindi il preciso tag live non è stato identificato.
2. Con `ownership_scope=reviewed-hosts`, il crawler filtrava i link ma riutilizzava
   senza controllo il `preferred_career_url` del checkpoint e i suoi host. Adesso
   gli host provengono dal registro revisionato; seed, coda e record rispettano quel
   perimetro e una risposta rediretta fuori perimetro non autorizza né estrae il nuovo
   host. Il controllo della destinazione avviene dopo la risposta del trasporto
   esistente: non è un nuovo blocco preventivo di tutti i redirect HTTP.

DAF usa ora lo stesso scope già esistente per Tilburg, restringendo la discovery
al dominio già revisionato `www.daf.com`. Nessun host aggiunto: eventuali canali
esterni DAF richiedono una review separata. Il cambio è proposto in PR, non attivo.
Gli altri collector conservano il comportamento di discovery già configurato.

## Prove, costi e limiti

- Prima del fix: quattro regressioni mirate, due fallimenti, un errore e un caso
  positivo. Dopo: tutte e quattro passano, inclusi due cicli con checkpoint persistito,
  record HR interno conservato e canale esterno esplicitamente revisionato utilizzabile.
- Scenario sintetico con checkpoint contaminato: 3 → 2 letture nel primo ciclo,
  zero letture al dominio esterno e stesso record interno. Questo non quantifica
  un risparmio di produzione né nuove candidature.
- Validazione su Python 3.12.16: 291 test Python riusciti; 24 frontend, 64 esempi HR,
  generazione coverage e build riusciti. La prima prova con Python 3.9 falliva per
  incompatibilità già previste dai test; non è il runtime CI. Nessuna dipendenza
  runtime del progetto aggiunta.
- Diagnostica live limitata: DAF starting page HTTP 200; pagina Tilburg segnalata
  dal report HTTP 403. Totale 4 richieste conteggiate, compresi robots, 25,108 s e
  123.021 byte restituiti conteggiati. Zero browser, candidature inviate o raccolte
  complete. Evidenze e hash DAF in `career-scope-live-diagnosis-2026-11-15.json`.
- Catalogo, ID, stato delle vacancy, soglia di freschezza, budget, schedule e gate
  Dynamic ATS non modificati. Il beneficio reale si misura sul primo ciclo ordinario
  dopo un eventuale merge autorizzato: host effettivamente letti, costo DAF, match HR
  e verifiche policy v2; non si dichiarano annunci nuovi sulla base delle fixture.

## Prossimo passo

Review della PR e CI sul commit finale. Nessun merge autorizzato da questa attività.
Non attendere un futuro ciclo per riconciliare i lead Overijssel già recuperati:
preparare un lotto distinto, preservando identità esistenti, prove storiche e lacune.
