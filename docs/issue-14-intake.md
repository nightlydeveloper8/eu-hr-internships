# Issue #14 — intake nelle raccolte successive

Base verificata: `e61e950`, pubblicazione quotidiana successiva alle PR #7
(`3686021`) e #15 (`015717f`). Catalogo: **324 record**, 23 open,
300 unverified, uno closed. Nessun `intake` rimasto nel catalogo corrente.

## Riproduzione e correzione

La regressione offline sul `process_source()` originale fallisce con
`KeyError: intake`: il record rigenerato sostituisce quello storico senza
ricostruire il campo. Con la correzione passa attraverso adattatore Greenhouse,
verifica effettiva di pagina/modulo e `finalize()`, senza accesso alla rete.

L'estrattore accetta date esplicite con indicatori di inizio in olandese/inglese
(mese, giorno facoltativo, anno facoltativo; ISO con giorno). Conserva evidenza
e timestamp, non indovina anni e distingue date passate, anno assente e date
multiple/conflittuali. Non interpreta durata, anzianità di pubblicazione,
scadenze o finestre di candidatura come inizio dello stage. I formati non
riconosciuti restano senza intake: la copertura non pretende di essere universale.

Il testo della pagina ufficiale con titolo/identità corrispondenti prevale sul
feed/cache, anche quando il modulo non è disponibile. Una pagina che cambia
data o elimina l'inizio sostituisce o elimina il precedente intake; non esiste
fallback sull'intake storico. Se non si riesce a leggere la vacancy, si usa
soltanto il testo del record ufficiale disponibile in questa raccolta, senza
promuovere lo stato di verifica. Nessuna richiesta aggiuntiva introdotta.

Un annuncio assente da inventario incompleto/fallito conserva l'osservazione
storica con timestamp originario; non ottiene nuova verifica e resta soggetto
alla finestra di 48 ore. L'assenza da inventario completo continua invece a
seguire la normale riconciliazione conservativa.

## Confini di verifica e conservazione

Trunkrs e Domino's mantengono le revisioni bloccanti esistenti. VAR e Meerpaal
sono candidati di ricerca esterni al catalogo, rispettivamente con intake passato
e scadenza superata: due `needs-verification` rendono persistenti anche nel
finalize quotidiano questi esiti già documentati da PR #15. Un modulo attivo,
o persino una nuova data estratta, non sostituisce la revisione manuale.
Nessun candidato importato o promosso dalla correzione.

Il replay alla data di pubblicazione preserva tutti i 324 ID, source ownership,
stati, regioni e policy v2. Il finalize esistente riqualifica già link_status e
motivazione di verifica per 26 deadline invalide in record non verificati:
comportamento preesistente, estraneo a questa modifica. Catalogo, fonti,
datori, geografie e dati di pubblicazione non modificati.

## Validazioni

- **236 test Python**, inclusi 10 nuovi test offline: evidenze primarie Utrecht
  salvate, due raccolte successive, ripetizione idempotente, modifica/rimozione
  data, feed obsoleto, modulo assente, anno ignoto, date passate e conflittuali,
  scadenza superata, verifica disabilitata, inventari incompleti/falliti/completi,
  preservazione del catalogo e quattro blocchi di revisione su due cicli.
- **21 test frontend**; **64 esempi di classificazione**, zero errori.
- Validazione catalogo e registry datori/fonti/geografia; company coverage e
  build statica riusciti. Output derivati di copertura ripristinati alla base.
- Browser locale offline sul risultato di due raccolte: **Published start =
  2027-02**, nessun errore di pagina. Nessun browser scaricato.
- `git diff --check` superato.

Nessun merge, deployment, raccolta massiva, sottoagente o servizio a pagamento.
Il ripristino delle date nel sito richiederà una futura raccolta autorizzata con
questa correzione; questa PR non rigenera il catalogo pubblicato.

Refs #14.
