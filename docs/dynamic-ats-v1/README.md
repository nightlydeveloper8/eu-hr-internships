# Dynamic ATS Verification v1 — pilot People Placement

Collegata alla [Issue #18](https://github.com/nightlydeveloper8/eu-hr-internships/issues/18). Base: `main` **1d198a4**, successivo alle PR #19 e #21. Solo Bentacera, OPACK / Oosterwolde Plastic Industrie e Centraal Beheer Achmea; nessuna nuova ricerca o lettura di inventari.

## Esito sulle stesse evidenze

**Due candidature aggiuntive verificabili automaticamente**, senza modificare il catalogo. Baseline e verificatore nuovo valutano gli stessi HTML correnti; il nuovo percorso acquisisce anche il DOM fresco con Playwright. La baseline è il sorgente esatto di main, congelato con SHA-256. Le prove sintetiche non contribuiscono al risultato live.

| Fonte / candidatura nota | HTML ordinario | Fallback live definitivo | Richieste totali | Rendering / secondi rendering | Risorse browser |
|---|---|---|---:|---:|---:|
| Bentacera — Traineeship Salarisprofessional | unverified | verified | 20 | 1 / 9,888 | 18 / 1.373.636 byte |
| OPACK — Stage Employer Branding | unverified | verified | 19 | 1 / 9,270 | 17 / 1.332.642 byte |
| Achmea — Hbo Meewerkstagiair HR Young Talent Recruitment | unverified | unverified, escluso per CAPTCHA | 3 | 0 / 0 | 0 |

Conversione nel campione: **0/3 → 2/3**. Nessuna nuova vacancy scoperta. Bentacera e OPACK caricano un `form name="apply-form"` con nome, cognome, email e submit abilitato nella vacancy corrente con titolo corrispondente. Non si tratta dei form preferiti, contatto, cookie o job alert presenti nello stesso documento. Nessuna candidatura è stata compilata o inviata.

Achmea pubblica `cxsForm.init`, un host Salesforce **non approvato** e `useCaptcha: "True"`. Il gate interrompe il percorso prima del browser. Nessuna richiesta verso Salesforce, autenticazione, interazione CAPTCHA o approvazione di host.

Il catalogo di main rimane **324 ID: 25 open, 295 unverified, 4 closed**. Il delta live +2 riguarda solo le prove del pilot: nessuna promozione è scritta in produzione. Gli stati aziendali rimangono partial: non abbiamo verificato la completezza degli inventari né dichiarato verified-empty. Requisiti linguistici, intake, ownership e alias non vengono riscritti.

## Architettura e sicurezza

1. `verify_vacancy` esegue prima la policy v2 ordinaria. Soltanto due esiti tipizzati di form mancante possono arrivare al gate: assenza di CTA sul documento identificato oppure assenza del form sulla destinazione già collegata alla stessa vacancy.
2. Il gate richiede sia `PEOPLE_PLACEMENT_DYNAMIC_ATS=pilot-v1` sia uno dei **tre source ID** pilota. Richiede il placeholder/toggle osservato nelle fixture #21 oppure il template Salesforce riconosciuto. Non contiene ID, titoli o URL di singole vacancy. Form HTML già presenti ma indisponibili, CAPTCHA, scadenze note, errori di identità, ATS ID discordanti, redirect, robots e blocchi HTTP non sono motivi per tentare il browser.
3. Si riusa **`collector/rendering.py:render_pages`**, con lo stesso semaforo a due browser, Chromium e client della raccolta. Il contesto è nuovo, senza credenziali; service worker e WebSocket vengono bloccati. La modalità esistente per inventari rimane separata dalla modalità stretta di lettura candidature; non è stato aggiunto un secondo sistema browser.
4. Ogni risorsa trasmessa, inclusi JS e CSS, richiede HTTPS, host già approvato, robots e budget, con lock e throttling del client esistente. Solo GET/HEAD; nessuna eccezione POST di ricerca nella modalità candidature. Nessun header Authorization e nessun percorso login/signin/oauth/authenticate. Immagini, font, media e tracker vengono soppressi prima della rete.
5. Playwright può non intercettare ogni passaggio di un redirect. Per questo la route usa **`route.fetch(max_redirects=0, max_retries=0)`**, rifiuta ogni risposta non 2xx e consegna al browser solo la risposta controllata. Non si autorizza un host dalla destinazione di un redirect. Vengono controllati anche i domini espliciti negli `action` dei form.
6. L'unico click consentito è un `div.btn` visibile, esterno ai form, con testo esatto “Solliciteer direct” e handler esatto `toggleForm('…')`. Nessun click su button/submit, nessuna compilazione o scroll/paginazione arbitraria. Le richieste eventualmente prodotte rimangono soggette agli stessi vincoli.
7. Il DOM corrente deve identificare la stessa vacancy, non confliggere con gli ATS ID noti e contenere un form candidato abilitato. Controlli nascosti/disabilitati e fieldset disabilitati non bastano. Newsletter, alert, cookie, ricerca e community sono esclusi. La policy v2 viene poi rieseguita sul medesimo DOM acquisito nella chiamata, conservando tutti i controlli ordinari di titolo, ID, CTA e deadline. Un errore conserva unverified; una chiusura ufficiale esplicita mantiene la gestione ordinaria closed.

Nessun HTML storico/cache entra nel percorso di verifica live. Le fixture compresse sono esclusivamente prove offline; i replay non rinnovano `last_verified_at` in produzione.

## Budget e costo osservato

Il rendering usa una finestra più stretta del client già attivo: **25 secondi, 32 richieste**, massimo un tentativo per client/fonte e **tre per processo/shard**. I limiti residui della raccolta prevalgono; con meno di 5 secondi o 4 richieste residue il browser non parte. Non ci sono retry del fallback. La modalità stretta limita a 20 MB i body delle risorse cumulati e il DOM; libera le risposte Playwright. Il controllo dei byte avviene dopo l'acquisizione della risposta: non è un hard limit di memoria durante il download. La memoria RSS del processo Chromium non è stata misurata, quindi non si rivendica un limite RSS verificato.

Ultimo pilot completo: **42 richieste trasmesse, 2 rendering, 22,816 secondi complessivi di verifica**, di cui 19,158 nel rendering; 2,706 MB di body browser. Le richieste comprendono i controlli HTML e robots; per la pagina browser ogni risorsa trasmessa è conteggiata. Le durate totale/rendering si sovrappongono e non vanno sommate. 60 risorse non necessarie sono state soppresse. Non sono stime di fatturazione: nessun servizio a pagamento è stato usato, il costo monetario della CI non è misurato.

Per trasparenza sono conservate **tutte e quattro le iterazioni di sviluppo**: 168 richieste conteggiate, 8 rendering, circa 91,2 secondi totali di verifica. Le prime due iterazioni conservavano unverified perché rifiutavano anche il tracker `analytics.floydhamilton.tech/matomo.js`. Quel tracker ora è soppresso come gli altri analytics, senza contattarlo o approvarlo. La terza ha dimostrato i due form; la quarta ha confermato il risultato con il trasporto definitivo senza redirect. I contatori delle prime tre iterazioni misurano le richieste iniziali intercettate; non attestano gli eventuali hop di redirect non intercettati. Solo l'ultima usa il trasporto che rifiuta ogni redirect. Nessuna ulteriore lettura live è necessaria per riprodurre il rapporto.

`dynamic_ats` nei report per fonte e nei log registra tentativi, richieste, durata, byte browser, risorse soppresse/rifiutate, motivo di successo/fallimento ed esclusione. Il catalogo non contiene questi log diagnostici.

## Evidenze, replay e test

- **Storico #21:** `tests/fixtures/sprint18-batch2/`, tre pagine note; replay HTML 0 → 0, zero richieste live.
- **Live reale:** `tests/fixtures/dynamic-ats-release/`, timestamp UTC, URL iniziali/finali, hash SHA-256, HTML e DOM; 0 → 2. Gli altri tre tentativi sono conservati nelle directory `dynamic-ats-live`, `dynamic-ats-diagnostic`, `dynamic-ats-final`.
- **Replay del DOM acquisito:** riesegue il verificatore finale sugli stessi body, conferma 0 → 2; zero richieste live. Non è una nuova osservazione delle vacancy.
- **Sintetico:** test di form valido, titolo/ATS ID errati, campo ID nascosto discordante, form mancante/disabilitato/nascosto, newsletter/cookie, host/action e redirect proibiti, robots, CAPTCHA, timeout, budget per fonte/processo e scadenze. Il trasporto browser simulato esegue le route reali per JS/CSS, POST inclusi search, Authorization, redirect HTTP e status di blocco; verifica che nessuna richiesta vietata parta e che non venga cliccato submit.
- **Storia:** snapshot di catalogo e verificatore di main con hash in `dynamic-ats-baseline`; due finalizzazioni idempotenti su copie, conservazione dei 324 ID, alias, ownership, prima scoperta, open/closed e righe esterne alla modifica sintetica. Nessun rinnovo da fixture nel catalogo reale.

Con Python 3.12+ e Node:

```sh
python3 scripts/dynamic_ats_pilot.py
python3 scripts/dynamic_ats_pilot.py --report docs/dynamic-ats-v1/comparison.json
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 scripts/company_coverage.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

Controlli locali superati: **282 test Python, 21 frontend**, classificazione su 64 esempi senza errori, registry/coverage di 1.882 aziende, validazione catalogo e build. Il rapporto JSON rigenerato due volte è identico byte per byte. La CI della PR viene controllata separatamente.

I comandi predefiniti sono offline. `--capture DIRECTORY_NUOVA` è una lettura live delle sole tre candidature già note, rifiuta directory esistenti e non esegue discovery/raccolte complete. Non è richiesto per CI o riproduzione del rapporto.

## Rischi e rollout controllato

**Disattivato per impostazione predefinita**, nessuna modifica alle configurazioni del workflow o ai registry. Dopo review e merge, il primo rollout potrà impostare la variabile solo in un'esecuzione controllata sulle fonti pilota, con metriche e confronto dei risultati. La raccolta ordinaria resterà autonoma per le vacancy future di quelle fonti: nessun intervento manuale sul singolo annuncio. Il limite di un tentativo per fonte privilegia il costo e può lasciare altre candidature unverified nello stesso giro.

Il beneficio dimostrato è circoscritto ai due siti con template condiviso. Gli altri datori non entrano nel fallback. Non estendere l'allowlist sulla base di un DOM o di un errore: eventuali altri host ATS richiedono review separata. Achmea resta esclusa. Le forme e i toggle possono cambiare; un risultato sintetico positivo non giustifica nuove fonti. Falsi negativi per budget, tracker non riconosciuti, contenuti che richiedono interazioni ulteriori, HTTP non 2xx o form nascosti sono accettati.

Valutare richieste/durata, timeout e nuove verifiche prima di ogni ampliamento. Per rollback basta rimuovere la variabile: torna il solo percorso HTML. Le verifiche successive devono sempre rileggere le pagine correnti. Nessun merge, deploy, raccolta completa, contatto con aziende, sottoagente o modifica manuale del catalogo è stato eseguito.
