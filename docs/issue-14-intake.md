# Issue #14 — intake nelle raccolte successive

Base: `e61e950`, pubblicazione successiva alle PR #7 (`3686021`) e #15
(`015717f`). **324 record**, 23 open, 300 unverified, uno closed; nessun
intake rimasto. La regressione originale riproduce il campo perduto nel
`process_source()` precedente alla PR. Questo aggiornamento corregge i tre P2
della revisione indipendente sul primo commit della PR #16, `e9106c9`.

## 1. Cache e provenienza temporale

`PageCache` propaga la provenienza del testo e il timestamp della sua prima
osservazione, anche per i record annidati del crawler universale. Le cache
preesistenti usano `stored_at`, senza inventare una provenienza live. Una
riscrittura tecnica della cache conserva il timestamp originario della prova.

L'intake esporta `provenance` (`live`, `feed`, `cache`), `observed_via` e
`checked_at`. Una pagina live identificata prevale sul feed/cache; se la lettura
fallisce e rimane soltanto la cache, l'intake usa il vecchio timestamp. Non
riceve la data del nuovo tentativo. La UI distingue pagina ufficiale, feed e
prova storica in cache, mostrando quando è stata osservata. Il timestamp del
tentativo di verifica può cambiare: non rappresenta una nuova prova riuscita.

Regressione completa con sitemap, parser della pagina, PageCache reale,
verifica e finalize: prima lettura live, poi pagina bloccata con cache di **12 e
36 ore**, due cicli successivi e ripetizione idempotente. Restano invariati
`intake.checked_at`, `last_verified_at`, ID e ownership; lo stato non è
verificato. Il file della cache non viene riscritto dal semplice utilizzo.
Coperto anche il caso di cache legacy e riscrittura tecnica successiva.

## 2. Date estranee all'intake

`vanaf`, `per` o la semplice disponibilità non bastano: occorre un contesto di
inizio stage. Candidature, compensi, pubblicazione, scadenze, storia aziendale
e campagne non diventano intake. Le due frasi segnalate sono negative anche
nel percorso completo:

- `Solliciteer vanaf februari 2027.`
- `Per februari 2027 bedraagt de stagevergoeding 500 euro.`

Restano riconosciuti `Stage vanaf februari 2027`, `per februari 2027 starten`,
`Starting in February 2027`, `Startdatum`, il testo Utrecht documentato e una
vera frase di inizio che menziona anche il compenso. Date multiple/conflittuali
restano in `alternatives`, con `published_start=null`: la UI non mostra una
data confermata. Anni assenti restano esplicitamente ignoti; date passate non
vengono trasferite all'anno seguente. Formati non riconosciuti restano senza
intake; l'estrazione è conservativa e non pretende copertura universale.

## 3. Deadline scaduta e precedenza delle prove

La pagina ufficiale viene identificata per URL, titolo e requisition prima di
acquisire il nuovo intake e propagare la chiusura. Una deadline scaduta o un
banner di chiusura continuano a chiudere la candidatura, ma non impediscono più
alla pagina corrente di sostituire o rimuovere la data del feed/cache.

Caso obbligatorio coperto con feed Greenhouse e verifica reale: **feed febbraio
2027; pagina `Start in overleg`; deadline 15 ottobre 2026 → closed, nessun
intake febbraio ripubblicato**. Coperti due cicli successivi e idempotenza.
Per sitemap, il parser può differire il controllo di scadenza fino alla
verifica/finalize: anche una pagina scaduta non presente in cache aggiorna i
metadati prima della chiusura. Il comportamento standalone del parser resta
conservativo. Testati inoltre cambio a marzo, rimozione successiva e banner
esplicito di chiusura. Nessuna richiesta aggiuntiva alla vacancy introdotta.

## Conservazione e verifiche

Trunkrs/Domino's e VAR/Meerpaal mantengono i blocchi di revisione, anche con
modulo attivo e nuova data. VAR/Meerpaal restano candidati esterni al catalogo.
Gli inventari incompleti/falliti non rinnovano la prova storica; resta la
finestra di 48 ore. L'assenza da inventario completo segue la riconciliazione
conservativa esistente.

Il replay conserva i **324 ID**, source ownership, stati, regioni e policy v2.
Il finalize preesistente riqualifica già link_status/motivazione di 26 deadline
invalide in record non verificati: comportamento estraneo alla correzione.
Catalogo pubblicato, fonti, datori, geografie e listing reviews non modificati
in questo aggiornamento. Ripristinati gli output derivati delle validazioni.

- **243 test Python**: 17 regressioni intake, incluse sei nuove prove complete
  sitemap/PageCache e il caso feed con deadline scaduta. I nuovi test completi
  falliscono su `e9106c9` e passano con le correzioni.
- **21 test frontend**, **64 esempi di classificazione**, zero errori.
- Browser offline: Published start 2027-02, etichetta `Historical cached evidence`
  e osservazione originale dell’8 novembre dopo il ciclo del 9; nessun errore.
- Catalogo e registry datori/fonti/geografia validati; company coverage,
  build statica e `git diff --check` superati.

Nessuna nuova Issue o PR, sottoagente, raccolta massiva, merge o deployment.
Il ripristino sul sito richiederà una futura raccolta con la correzione.

Refs #14; aggiornamento esclusivamente nella PR #16.
