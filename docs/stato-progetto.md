# Stato di ripresa — People Placement

## 15 novembre 2026 — integrazione autorizzata delle PR pronte

L'utente ha autorizzato esplicitamente squash and merge di tutto il lavoro pronto.
Non chiedere di nuovo l'autorizzazione per completare questa integrazione.

- **PR #38 già merged**, squash `adf4c69dd1d47cc7f940a98421796940c818d7f3`.
  Verificati head esatto, CI/preview verdi e assenza di review bloccanti prima del merge.
- **PR #39 merged con squash**, `3a2830f558af8c3e58b1ec7673dbfd7df294fbef`.
  Include le modifiche pronte #20, #27, #28, #32, #33, #34, #35, #36, #37 e WEBO;
  il checkpoint #26 è superato dallo stato corrente. Le dieci vecchie PR sono
  chiuse come consolidate/superate, non come singoli merge; rami e prove preservati.
  Nessuna PR aperta resta al controllo finale. Checkout `merge-ready-20261115`.
- Due conflitti di codice risolti conservando sia i limiti host/checkpoint #38 sia
  titoli storici, telemetria e publisher ufficiali scoped delle #27/#28. Allarme
  testato anche avviando i test fuori dalla root, senza modificare gli script live.
- **356 test Python (3.12), 26 Node, 64 esempi, coverage e build riusciti.**
  La #28 aveva vecchie CI cancellate: non è stata assunta pronta sulla sola preview;
  il suo codice è incluso nella verifica combinata completa.
- Registro integrato: 1.887 datori e 1.931 fonti, cinque datori/fonti nuovi
  (Attero, Intergas, Reestmond, SW Vastgoedverbetering e WEBO). Le altre modifiche
  estendono o correggono identità/sedi e canali di datori già censiti.
- Tutti i 345 ID del catalogo corrente conservati, senza variazioni di status,
  identità o verifiche. Unica associazione aggiornata: Landal Nooitgedacht → NL13,
  derivata dalla sede ufficiale Drenthe già revisionata. Nessun snapshot storico
  di catalogo o coverage generale sovrascrive quello attuale.
- WEBO Stage HRM: 1 nuova candidatura verificabile nel pilota live del 15 novembre
  (3 richieste / 34,533 s), nessun invio. Fonte quotidiana configurata su main, parziale, host
  esatto e budget 80 richieste/120 s. Prima raccolta su main ancora da verificare;
  l'incremento effettivo di stage in produzione non è ancora attestato.
- Drenthe: lotto parziale di 40 datori, 27 qualificati nella ricerca del 14 novembre;
  non provincia completa. Overijssel: WEBO primo canale proposto; CBS 406 rispettato,
  municipality code ignoto. Le 171 vecchie schede OVI non sono aziende uniche.
- Directory/ATS discovery #33/#34 restano code offline, seed live disabilitati;
  #35 audit DIM conferma mantenimento storico, non nuove vacancy; #36 documenta un
  pilota Wikidata bloccato. Nessuna query o fonte live avviata per questi moduli.
- Gate Dynamic ATS `pilot-v1`, allowlist del pilota e schedule invariati. Nessuna
  raccolta completa manuale, email, candidatura o automazione AI aggiunta.

**Stato finale dell'integrazione:** CI prima del merge #43750190939/#43750185407
riuscita sullo head esatto `061426e`; CI dopo merge #43750497438 riuscita.
[Raccolta automatica #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
avviata dal merge #39, ancora in corso all'ultimo controllo. Nessun workflow
manuale avviato e nessun controllo AI futuro configurato.

La precedente raccolta dopo #38, #43748284250, è riuscita: test, 16 shard e
publish tutti verdi, commit dati `19c4258`. Catalogo 18:55 UTC: 345 ID, 19 open,
303 unverified, 23 closed. Prima/dopo #38: 341 → 345 record ma 19 → 19 verified;
nessun nuovo verified attribuito al fix. DAF: richieste 86 → 75, durata
100,46 → 86,13 s, pending 2.332 → 57, solo host www.daf.com. Inventario ancora
parziale: il risparmio osservato non prova completezza né nuove candidature.

**Primo punto incompleto:** leggere l'esito del run #43750497445, verificare
publish, nuovi ID, freschezza e opportunità WEBO; misurare costi e canali Drenthe.
Non dichiarare un incremento di produzione prima di quel risultato. Il controllo
pubblico del catalogo Cloudflare ha restituito HTTP 403: deployment/contenuto
servito non attestati dal runtime, distinzione conservata rispetto a GitHub.
Issue #18 e #23 restano aperte finché tutti i criteri di produzione non sono provati.
Le vecchie modifiche locali WEBO sono già incluse: non creare una PR duplicata
partendo dal checkout storico. Dettagli in docs/integration-2026-11-15.md.
