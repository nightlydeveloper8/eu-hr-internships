# EU ATS Discovery — primo pilota in sola lettura

## Scopo

Preparare una coda di canali ufficiali di recruiting ATS per Germania (DE), Francia (FR), Belgio (BE) e Irlanda (IE), senza attivarli, eseguire HTTP o alterare le vacancy. L'obiettivo finale e' alimentare autonomamente il monitoraggio quotidiano europeo, non ampliare il censimento manuale.

## Baseline e fonte delle evidenze

- Main di riferimento: e7056c3351d06bedaa1f0d4a8e443f5a6e424a78 (12 novembre 2026).
- `docs/career-channel-scan.json`: 346 registrazioni storiche di scansione; 25 aziende con collegamenti ATS rilevati nell'insieme DE/FR/BE/IE (19 DE, 6 FR, 0 BE, 0 IE). Non significa che tutte possano essere integrate o che i link siano ancora attivi.
- La coda usa **solo** righe `reviewed` il cui URL di scansione coincide con il `career_url` o `website_url` dichiarato dal datore. Redirect verso un altro host non sono prove sufficienti.
- BE e IE restano nel campione anche se le vecchie scansioni non forniscono collegamenti positivi. Zero scoperta NON significa zero opportunita' nel paese.
- I `target_countries` dei datori sono candidati di ricerca, non evidenza che una vacancy sia ubicata in quel paese.

## Funzionalita'

Il nuovo modulo `collector/ats_channel_discovery.py` riconosce tenant su Greenhouse, Lever, Recruitee e Personio XML da URL pubblicati nelle pagine censite. Collassa duplicati della stessa board/tenant, segnala se una fonte e' gia' presente nello stesso datore, rileva conflitti se un altro datore possiede la stessa board e produce esclusivamente candidature con `enabled=false`.

Ashby e SmartRecruiters sono segnalati come access-review, Teamtailor e Softgarden come non supportati dal connettore di questa PR. L'endpoint di feed e' un **hint da controllare**, non un URL autorizzato. Nessuna identificazione per semplice somiglianza di nome o gruppo societario.

Per generare la coda JSON in modo riproducibile, dalla root:

```sh
python3 scripts/ats_discovery_pilot.py --countries DE FR BE IE --per-country 6 --output docs/ats-discovery-review.json
```

Senza `--output`, il comando stampa il risultato e non scrive alcun file. Per provare gli stessi controlli su tutti i paesi, passare i codici dei 27 stati UE; e' sempre un audit sui dati gia' raccolti, non una scansione web.

## Misura dei costi e limiti

| Indicatore di questa PR | Risultato |
| --- | --- |
| Richieste HTTP aggiuntive del prototipo | 0 |
| Browser/rendering aggiuntivi | 0 |
| Nuove fonti abilitate | 0 |
| Nuovi stage HR verified in produzione | 0 |
| Modifiche a catalogo, aziende, sources, workflow | 0 |
| Tempo CI e costo monetario | Non ancora misurati |

Il rapporto enumera `companies_sampled`, `detected_channels`, `review_candidates`, `already_registered`, `ownership_review` e `blocked_or_unsupported` per paese. Ogni riga include la pagina originale, il link osservato, gli ID esistenti e la condizione di revisione host/robots. Sono risultati storici e **non** rinnovano la freschezza delle candidature.

## Verifiche e secondo ciclo

```sh
python3 -m unittest tests.test_ats_channel_discovery -v
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

I test nuovi includono due esecuzioni identiche di discovery, URL non HTTPS o con credenziali, pagina di origine non dichiarata, redirect cross-host, provider bloccati, dedup tenant e conflitto di proprieta'. I test gia' presenti della pipeline presidiano due passaggi di raccolta/finalizzazione; il nuovo codice non viene eseguito dal collector giornaliero.

## Passaggio successivo (non incluso)

Collegare, in una PR separata dopo revisione, la produzione periodica di osservazioni ufficiali ai checkpoint del crawler esistente. Abilitare nuove fonti solo dopo verifica live di host/robots, proprieta' del tenant, feed completo, paese effettivo, costi di richieste e idempotenza del catalogo. Non toccare il gate Dynamic ATS `pilot-v1` della Issue #23. Nessun merge o rollout autorizzato qui.
