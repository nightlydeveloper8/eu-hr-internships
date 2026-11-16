# Stato di ripresa — People Placement

## 16 novembre 2026 — coda UE27 e primo lotto di espansione preparati

Ripresa del lavoro locale interrotto sul ramo `plan/eu27-expansion-20261115`,
checkout isolato `fix-jde-20261115`. Base aggiornata al main `e99f263` senza
sovrascrivere il lavoro delle altre sessioni. Il catalogo delle 09:06 UTC ha
347 record e 20 open/verified; nessun aumento attribuito a questa preparazione.
La PR #40 è merged; #18/#23 restano aperte e non limitano la ricerca UE27
richiesta esplicitamente dall'utente. NL resta prioritario senza attendere la
mappatura completa delle 12 province per ricercare nel resto dell'UE.

- Generatore offline riproducibile e coda per **27 paesi**, 1.926 identità di
  ricerca, 2.202 attività su canali. Riutilizza registro, esiti recenti, catalogo
  e scansioni esistenti. Le 39 nuove identità web sono da rivedere per gruppo e
  dimensioni: non sono aziende giuridicamente uniche accertate o fonti attive.
- **Primo lotto: 37 attività**, NL 11, BE 10, DE 11, FR 3, IE 2: 34 nuovi canali
  candidati e 3 conversioni di crawler generici (2-CNNCT, Gemeente Achtkarspelen,
  VTG GmbH Ingenieurbüro). Non è stato raggiunto l'obiettivo iniziale di 50:
  connettori dedicati già attivi, vecchi recuperi, identità condivise e prove
  contraddittorie sono esclusi, senza riempire il lotto con lavoro duplicato.
- **29 bozze per adattatori già disponibili**, tutte disabilitate nel solo
  documento `batch-01.json`; nessun file di produzione le carica. Restano da
  dimostrare collegamento datore/tenant, identità del gruppo, accesso del feed,
  completezza dell'inventario, sede e candidatura policy v2. Dimensioni non
  qualificate per tutte le 37 attività: quota PMI della strategia non dimostrata.
- Preflight live limitato a una pagina già osservata per canale supportato:
  **33 datori, 34 tentativi** (Zero Motorcycles ha poi una nuova URL vacancy
  osservata, distinta dalla precedente URL solo candidatura), **64 richieste
  logiche, 7.137.457 byte, 34,168 secondi-fonte, 16,583 secondi a muro cumulati**
  dei due processi, zero rendering. Robots e redirect sul solo host esatto
  rispettati; nessuna candidatura, API inventory o raccolta completa.
- **28 pagine con titolo corrispondente**, non 28 candidature verificate.
  DocMedico 404; JD Sports FR restituisce board Netherlands; Theodo timeout;
  Hospitality Recruiters redirect fuori scope, non seguito. Fidelity già
  contraddetta da apertura 404 resta fuori dal lotto. eXtra Shop richiede
  revisione del titolo e distinzione alternance/stage. Nessun aggiramento.
- Ricerca web complessiva delle due sessioni: 40 query e 6 aperture; costi
  monetari non misurati. **Nuove fonti attivate 0, nuove candidature verificate 0**.
  Report: `docs/eu27-expansion/README.md`, `queue.json`, `batch-01.json`, manifest
  degli indizi e due preflight con URL, date, hash e costi.

Validazione: **374 test Python 3.12 e 26 test Node superati**, 64 esempi di
classificazione senza errori, build riuscita; rigenerazione deterministica,
nessuna modifica a catalogo, registry, workflow o codice di produzione.
La coda completa è conservata anche compressa, oltre alla versione leggibile locale.

**Primo punto incompleto:** review e pilota circoscritto delle 29 proposte di
adattatore (priorità alle 28 con titolo live corrispondente), partendo dal legame
ufficiale datore→tenant e dal feed completo. Preparare l'integrazione soltanto
per canali con prove sufficienti, in un lotto; nessun merge/rollout implicito.
Per gli altri 22 paesi esiste la coda nazionale, non una nuova mappatura live.
Nessuna automazione di ricerca AI o nuova schedulazione configurata.

## Ripresa — verifica integrazione JDE

Verificata via API GitHub la PR #40: squash merge completato il 15 novembre 2026,
21:14:18 UTC, commit `216ea7300e5d666d6e78a0a1d2ba732d5109d502`.
La correzione di identità è quindi su main; i dettagli sotto descrivono la diagnosi
precedente al merge. Beneficio dimostrato dalla diagnosi: **0 nuove candidature**;
il target JDE restituiva JSON senza modulo. Nessuna PR duplicata, nuovo merge o
rollout in questa ripresa. Verifica della candidatura JDE e beneficio della raccolta
dopo merge ancora non attestati. Il runtime locale è disconnesso; stato aggiornato
tramite GitHub preservando il contenuto delle altre sessioni.

## 15 novembre 2026 — identità JDE e confronto Center Parcs/Landal

Ripresa dal primo punto incompleto sul main remoto `b51a602`. Checkout isolato
`fix-jde-20261115`, ramo `fix/jde-application-evidence-20261115`; preservato il
checkout principale e il lavoro delle altre sessioni.

- **Modifica proposta, non integrata:** riconoscimento conservativo dello stesso
  posting SmartRecruiters fra `job-posting-detail?id=` e prefisso numerico della
  CTA osservata. Nessun ID inferito dalla sola CTA; query ripetute, ID discordanti,
  host simili e ID nel tracking non bastano. Controlli titolo, host, redirect,
  chiusura e modulo restano obbligatori. Nessuna configurazione host/gate cambiata.
- **JDE: 0 nuove candidature verificate**, un solo record con tre URL osservate.
  Lettura live ufficiale e target ATS con robots: il target restituisce JSON della
  vacancy, non un modulo. Replay reale prima/dopo: errore d'identità risolto,
  successivo errore `Application page does not identify the same vacancy` mantenuto.
  Nessun aggiornamento del catalogo o timestamp di verifica da replay.
- Confronto live circoscritto: Center Parcs ha titolo/JobPosting della stessa
  vacancy e pulsante JavaScript `Solliciteren`, ma nessun href/modulo statico;
  Landal pubblica `JR104108`, mentre la CTA Workday osservata contiene `JR104108-1`.
  Nessuna promozione o presunzione di equivalenza della variante.
- Costi complessivi della diagnosi: **9 richieste / 17,505 secondi-fonte /
  0 rendering**, inclusi robots; JDE 5/4,685 s, Center Parcs 2/11,487 s,
  Landal 2/1,333 s. La correzione aggiunge una lettura del target nel replay;
  non dimostra un risparmio né nuove opportunità in produzione.
- Report riproducibile: `docs/jde-application-identity-2026-11-15.json`, due
  risposte reali compresse con SHA-256 e sei test nuovi, incluso replay in due cicli
  senza mutazione del record. Corretto anche il test WEBO che assumeva uno stage
  ancora assente dal catalogo: verifica ora inserimento e refresh/idempotenza.

Validazione locale: **362 test Python 3.12 e 26 Node superati**, 64 esempi di
classificazione senza errori, coverage e build riusciti. I file di copertura
rigenerati solo nel timestamp sono stati esclusi dal diff.

[PR #40 aperta](https://github.com/nightlydeveloper8/eu-hr-internships/pull/40),
commit codice `1f223d046368e3edc3f50087e7b448e36658f261`. CI GitHub e preview
avviate automaticamente, esito ancora da verificare. Nessun merge o attivazione.

**Primo punto incompleto:** diagnosi riutilizzabile del flusso DigitalRecruiters
Center Parcs attivato dal pulsante osservato, con letture non-submit e scope/budget
esistenti. Per JDE serve una prova ufficiale di candidatura oltre al JSON; per
Landal restano identità della variante Workday e modulo. Non ampliare rollout,
non avviare raccolte complete. Catalogo/produzione invariati; confronto pubblico
Cloudflare e Issue #18/#23 restano aperti. Nessun controllo AI futuro configurato.

## 15 novembre 2026 — esito della prima raccolta dopo #39

Ripreso il primo punto incompleto senza avviare raccolte manuali.
[Raccolta #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
conclusa con successo alle 20:20 ora svizzera: test, 16 shard e publish riusciti.
Commit dati `1ad28a9cae8076d9181974fa4ea07940e263a93d`.

- Catalogo: **345 → 346 ID; 19 → 20 open/verified; 303 unverified e 23 closed invariati**.
  Tutti i vecchi ID conservati e nessun cambio di status sui record precedenti.
  Le 20 verifiche aperte hanno checked_at del 15 novembre, fra 19:07:47 e 19:08:08 UTC.
- **WEBO — Stage HRM, Rijssen**: nuovo ID `538388e73bc1c0592ab5`,
  candidatura ufficiale via email documentata dal collector live, policy v2,
  `official-vacancy-email-instructions`; inizio febbraio 2027, lingua di lavoro
  sconosciuta. Nessuna email o candidatura inviata. È una nuova opportunità verificata,
  già presente come vecchia scheda aggregatore unverified: non due opportunità distinte.
  Fonte parziale: 11 richieste, 23,17 s, zero rendering. Gli errori su open application
  e working student non invalidano la prova della vacancy HR né rendono completo l'inventario.
- Cinque fonti nuove, costo complessivo **50 richieste / 71,73 secondi-fonte**:
  WEBO 11/23,17 s → 1 HR verificato; Attero 30/35,85 s → 0 HR osservati,
  lettura parziale (una scheda senza JobPosting); Intergas 2/1,21 s → inventario
  14 offerte, 0 HR; SW 2/1,63 s → inventario 39 offerte, 0 HR;
  Reestmond 5/9,87 s → discovery incompleta, non prova di zero offerte.
  Questi tempi non sono tempo a muro né costo monetario.
- Drenthe: 40/40 tentati, 27 con dimensione qualificata, 2 stage verificati totali
  (1 presso datori qualificati). Stati: 21 partial, 10 discovery-incomplete,
  5 blocked-or-failed, 4 collected. Provincia ancora incompleta.
- Totale monitoraggio: 1.887 datori tentati; 57 collected, 31 verified-empty,
  513 partial, 977 discovery-incomplete, 309 blocked-or-failed.
- Cloudflare check-run `132927454054`: **success sul commit dati esatto 1ad28a9**,
  deployment `a2442ea2-8a3b-4496-a134-1497fe0fdad6`.
  Il success del deployment è attestato; confronto del catalogo servito ancora
  incompleto: precedente accesso HTTP 403 e tentativo browser corrente in timeout.
- Dynamic ATS: Bentacera, OPACK e Achmea restano unverified. Nessuna nuova prova
  di beneficio di produzione per #23; #18/#23 rimangono aperte. Gate e rollout invariati.
- Nessuna PR aperta all'avvio della ripresa. Nessun nuovo merge, ampliamento host,
  rollout, modifica al catalogo o workflow manuale in questa attività.

**Primo punto incompleto aggiornato:** diagnosi riutilizzabile dei link ufficiali
di candidatura sui canali NL già letti, partendo da JDE: tre URL osservate nella raccolta condividono
lo stesso posting ID `744000158015131` e falliscono `Application link lacks a matching vacancy identifier`;
non sono tre opportunità distinte. Confrontare poi Center Parcs e Landal, preservando
policy v2, robots e host autorizzati. Prove live circoscritte solo quando utili;
nessuna raccolta completa manuale. Proseguire la copertura comunale NL tramite fonti
ufficiali accessibili; CBS, Groothuis e Wikidata restano esclusi finché bloccati.
Il confronto del sito servito resta una verifica indipendente da completare.
Nessun controllo AI futuro configurato.

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

**Punto di ripresa precedente (completato sopra):** leggere l'esito del run #43750497445, verificare
publish, nuovi ID, freschezza e opportunità WEBO; misurare costi e canali Drenthe.
Non dichiarare un incremento di produzione prima di quel risultato. Il controllo
pubblico del catalogo Cloudflare ha restituito HTTP 403: deployment/contenuto
servito non attestati dal runtime, distinzione conservata rispetto a GitHub.
Issue #18 e #23 restano aperte finché tutti i criteri di produzione non sono provati.
Le vecchie modifiche locali WEBO sono già incluse: non creare una PR duplicata
partendo dal checkout storico. Dettagli in docs/integration-2026-11-15.md.
