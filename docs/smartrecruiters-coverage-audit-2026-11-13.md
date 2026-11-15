# SmartRecruiters — diagnosi copertura e budget, 13 novembre 2026

## Domande e risposta basata sui dati

**Baseline:** `main` `c1bd2b8066603c97c596cfdd868f03417736bbbf`, catalogo `2026-11-13T07:36:08.215689+00:00`, raccolta `partial`; nessun nuovo ciclo live è stato lanciato per questo lavoro. Letti `data/sources.json`, `data/coverage.json`, `data/employer-collection.json`, `data/catalog.json` e `collector/universal.py`. `AGENTS.md` non compare nell'albero di `main` consultato.

1. **Bosch ha un inventario incompleto? Sì.** `auto-bosch` è un `universal-employer` attivo: 13/11 07:25 UTC, `status=partial`, `complete=false`, `records_inspected=0`, 69 pagine, 88 richieste, 97,63 s, 337 URL pendenti. Il tentativo di alimentare l'ATS SmartRecruiters ottiene `robots.txt disallows https://api.smartrecruiters.com/v1/companies/BoschGroup/postings?limit=100&offset=0`; inoltre viene tentata una risorsa tecnica `js-www.smartrecruiters.com/career-site-ui/static/js/libs.1ca70ecb2123c3f23310.js` (`robots.txt unavailable: 403`); rendering della homepage careers con timeout. **Nessun inventario completo né assenza verificata.**
2. **Altri datori? Sì, stessa restrizione di accesso.** `smartrecruiters-deltaelectronics`, `smartrecruiters-averydennison` e `smartrecruiters-jacobsdouweegberts` sono `enabled=false` per robots: nei report storici del 5/11 riportano tutti `robots.txt disallows` su `api.smartrecruiters.com`. `auto-jde-peet-s` esplora invece pagine ufficiali (13/11: `partial`, 7 record, 92 richieste, 65,75 s, 49 pagine e 40 URL pendenti; 3 annunci HR estratti nel ciclo), ma il legame vacancy/form non è sufficiente per verificarli. Il catalogo contiene **19** annunci con URL SmartRecruiters da **12** source ID: **15 unverified, 4 closed, 0 verified**; questi sono *indizi storici*, non automaticamente nuove offerte aperte. Bosch: 2 IT/SE `unverified`; JDE: 3 SmartRecruiters FR/NL/BE `unverified` + una pagina employer-hosted NL `unverified`.
3. **Quanto aumenterebbero le candidature con una correzione?** Dato **non misurabile** senza nuovi cicli completi consentiti. Gli attuali 15 indizi non sono un forecast né una base per promuovere verified. Un'ottimizzazione dei link tecnici può liberare budget, **non** superare un `robots.txt` né creare prove di candidatura.

### Segnalazione Bosch BE: candidata da verificare, non candidatura verified

Fonte ufficiale: https://jobs.smartrecruiters.com/BoschGroup/744000155193669-intern-human-resources . La pagina pubblica mostra `Intern Human Resources`, Bruxelles, inizio dicembre 2026 e istruzioni di candidatura; l'ID **non** è nel catalogo del 13/11. Non è stato eseguito un controllo di inventario completo, form vacancy-specific, identità o freschezza tramite collector; `open/verified` attribuibili al caso = **0 verificati**, non un tasso di conversione misurato. `auto-bosch.target_countries` contiene DE/HU/NL/RO, non BE: lacuna nei metadati di copertura candidata, non prova del motivo tecnico dell'assenza. Non allargare scope/host senza evidenze e gate.

## Correzione proposta — risorse statiche ATS, non accesso vietato

Il crawler cerca URL assoluti nel sorgente HTML e considera automaticamente navigabili anche sottodomini provider con percorsi `/static/js/` o asset `.js`, `.css`, immagini e font. Nel caso Bosch è stato osservato proprio un tentativo verso una libreria JS SmartRecruiters: consumo non produttivo per l'individuazione di annunci.

Nuovo predicato condiviso `provider_resource(url)`, applicato:
- agli URL provider estratti dall'HTML come potenziali riferimenti careers;
- alle iframe/risorse provider prima di accodarli;
- al riutilizzo dei checkpoint `pending` di raccolte passate, così non continuano a consumare budget i file tecnici.

Le **vere pagine di annunci** rimangono idonee alla lettura nei percorsi già permessi, e l'API proibita rimane proibita. Nessun nuovo endpoint, autorizzazione, host, portale aziendale o inventario viene inventato. L'assenza di un inventario completo non diventa `verified-empty` o condizione di chiusura.

### Benefici e costi

- Prova di regressione **offline/sintetica**, non produzione: una pagina careers con un annuncio ufficiale linkato e un file `libs.js` deve visitare soltanto la homepage e la pagina-annuncio (**2 GET del mock, nessun GET verso la libreria**), mantenendo 1 record scoperto ma non conclusione di inventario completo. Un vecchio checkpoint con la libreria non deve ritentarla; no false complete/closed.
- Baseline di produzione (Bosch: 88 richieste / 97,63 s / 0 record nel ciclo) e costo dopo la modifica **non confrontabili live**: la modifica è isolata in PR, nessun run di raccolta eseguito. Nessuna previsione di tempo o numero di stage verificati senza evidenze.
- Costo runtime aggiuntivo: solo filtro locale su URL già osservati, nessuna richiesta HTTP o dipendenza extra. Il beneficio effettivo per fonte si misurerà esclusivamente dopo un merge autorizzato con due raccolte ordinarie, conservando ID, policy v2, host e budget.

## Prossimo intervento distinto

Individuare un **indice completo ufficiale e accessibile** di Bosch/JDE e verificare gli URL candidature mediante letture consentite; evitare di usare `api.smartrecruiters.com` e non suggerire la disabilitazione di robots. Se il canale employer-hosted non contiene inventario completo, lo stato resta `partial`; non inventare una stima del numero di vacancy perse. Concentrarsi poi sui 15 indizi `unverified` solo mediante flussi riproducibili, non manutenzione manuale di singole vacancy.

## Stato della consegna

Branch `fix/avoid-ats-static-asset-crawls`, modifiche circoscritte a `collector/universal.py`, test regressione e documentazione. Nessun merge, rollout, pubblicazione, raccolta completa, richiesta live a SmartRecruiters o nuova vacancy verified. CI validata sul commit `f97fbb8`: [run #43466272089](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43466272089) riuscito, 289 test Python, 24 frontend, classificazione, coverage e build riusciti. Nessun run di raccolta live: costo e beneficio in produzione ancora non misurati.
