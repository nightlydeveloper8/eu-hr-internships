# EU employer discovery — acquisizione incrementale senza iscrivere fonti

## Perché

Il nostro repertorio di aziende è già ampio, ma la maggioranza delle letture rimane incompleta. Creare altri censimenti comunali o importare dump nazionali non produce stage HR aperti. Le directory universitarie di aziende che reclutano possono offrire *indizi* su aziende mai censite; solo il sito ufficiale del datore potrà confermare un ATS e poi una specifica candidatura, secondo policy v2.

Il vecchio `scripts/map_employers.py` possiede parser per eventi universitari DE/FR/NL ma, dopo l'importazione, può visitare centinaia di host nuovi e modificare direttamente `data/companies.json`. Questa PR isola l'acquisizione in una **coda in sola lettura** da un sito sorgente alla volta.

## Architettura proposta: tre stadi indipendenti

1. **Directory discovery:** leggere una pagina di espositori dichiarata e approvata, deduplicare nomi e domini rispetto al registro, conservare link e provenienza. Non seguire i link verso siti aziendali. Il codice qui proposto opera solo in questo stadio.
2. **ATS onboarding:** solo per candidati revisionati, collegare l'azienda alla sua pagina career ufficiale, verificare l'identità del tenant e gli host/robots, poi integrare tramite i connettori della PR #33 o quelli esistenti. Nessuna attivazione automatica di nuovi host in questa PR.
3. **Monitoraggio quotidiano:** una volta registrata e autorizzata la fonte, il workflow ordinario già crea un collector per nuove aziende prive di connettore specifico e controlla quelle approvate. Prima di collegare una nuova directory a quel workflow, misurare la resa e i costi.

## Primo prototipo

File: `collector/eu_directory_discovery.py`, `scripts/eu_directory_discovery.py`, `data/eu-discovery-seeds.json`, `tests/test_eu_directory_discovery.py`.

Regole:
- Solo pagine ufficiali presenti nel manifest; `access_reviewed=false` di default.
- Modalità **offline** con file HTML già acquisiti e metadata di osservazione separati, quindi nessuna richiesta in esecuzione predefinita.
- Modalità `--live` solo per seed autorizzati: GET/HTTPS, `robots.txt`, host di partenza obbligatorio anche prima dei redirect, 6 chiamate logiche e 20 secondi massimo per seed; i redirect HTTP interni possono generare richieste ulteriori e non sono conteggiati separatamente, 1 MB max, mai CAPTCHA/login/POST.
- Parsing delle fiere universitarie già note senza eseguire il vecchio script massivo; per altre fonti si richiede un marcatore CSS card esplicitamente revisionato. Nessuna estrazione indiscriminata di link di navigazione, aggregatori, social o persone.
- Deduplica per azienda e host, anche tra paesi; matching conservativo contro gli employer esistenti; i dati mancanti non chiudono candidature. Stato `identity-and-host-review-required`, mai verified.
- Per un feed fallito o non rieseguito, preservare i candidati precedenti senza falsare l'ultimo timestamp osservato.

Uso offline (serve un file `<seed-id>.html` e `<seed-id>.meta.json` per ciascun seed da analizzare):

```sh
python3 scripts/eu_directory_discovery.py --snapshot-dir /tmp/approved-eu-directories --output /tmp/eu-discovery-review.json
python3 scripts/eu_directory_discovery.py --snapshot-dir /tmp/approved-eu-directories --previous /tmp/eu-discovery-review.json
```

Live solo dopo aver rivisto l'accesso e aggiornato esplicitamente il flag del seed in una successiva PR autorizzata:

```sh
python3 scripts/eu_directory_discovery.py --live --output /tmp/eu-discovery-live.json
```

Tutti i seed committati ora hanno `access_reviewed=false`: il comando live non richiederà nessuna pagina, anche se l'utente lo avvia, finché gli accessi non sono revisionati. Nessun nuovo job programmato viene introdotto.

## Quattro paesi del pilot

| Paese | Fonte proposta | Evidenza / limite |
| --- | --- | --- |
| DE | IKOM TUM 2026 | Directory conosciuta dal vecchio importer, da riautorizzare prima di usare GET live |
| FR | PhDTalent exhibitor directory | Directory conosciuta, da riautorizzare |
| BE | Hogeschool PXL Jobevent | Nomi e URL di siti aziendali osservati via web; robots e termini non ancora verificati |
| IE | Dublin City University employer reference | La pagina pubblica non prova un elenco completo con collegamenti diretti ai siti dei datori; richiede validazione |

Le ultime due sono **candidature di ricerca**, non feed di produzione né fonte ufficiale di vacancy. Non inventiamo siti o posizioni, non attribuiamo un workplace in base all'evento.

## BE e IE — prime fonti con collegamenti ufficiali a datori (12 novembre 2026)

Una verifica web delle pagine pubbliche ha individuato:

- **Belgio:** [Hogeschool PXL — Deelnemende bedrijven](https://www.pxl.be/bedrijven-en-organisaties/jobevent/deelnemende-bedrijven/): tabella `Standhouders` con nome dell'espositore e collegamento cliccabile verso sito ufficiale o carriera dell'azienda.
- **Irlanda:** [Tech Industry Alliance — Member Listing 2026](https://techindustryalliance.ie/members/): tabella `Company | Website`, con link diretti ai siti degli aderenti. Un membro di un'associazione **non** prova che stia reclutando; e' una fonte di soli candidati.

La configurazione per entrambi usa il nuovo parser **employer-table**, con marcatore di sezione esplicito e lettura esclusiva delle righe nome+link HTTPS. Questa estensione e' un'opzione di riconoscimento; **non abbiamo catturato HTML grezzo autorizzato dai due host per eseguire realmente i nuovi parser**. I test usano piccole fixture HTML sintetiche, e non vanno scambiati con prove live di estrazione.

`data/eu-discovery-seeds.json` conserva `access_reviewed=false` per PXL e Tech Industry Alliance. Entrambi i siti risultano consultabili attraverso una visualizzazione web, ma l'accesso diretto ai rispettivi **robots.txt non e' riuscito** e le condizioni di riuso automatico non sono state confermate. Pertanto nessuna chiamata di raccolta automatica e' stata eseguita e nessun nuovo host e' autorizzato. I vecchi candidati VTK e DCU (nomi senza link employer-owned sufficienti) rimangono documentati come superseded.

### Campione di evidenze web (non un inventario completo)

Il file `docs/eu-discovery-web-evidence.json` salva **8 collegamenti PXL e 8 collegamenti Tech Industry Alliance** osservati nelle rispettive pagine. Sono stati confrontati con l'attuale registro di 1.882 aziende sulla base del nome normalizzato e del dominio dichiarato:

| Misura | BE | IE | Totale |
|---|---:|---:|---:|
| Aziende con link osservate nel campione | 8 | 8 | 16 |
| Match esatti nome o dominio | 0 | 0 | 0 |
| Lead da sottoporre a review identita'/gruppo | 8 | 8 | 16 |
| Nuove aziende con unicita' societaria dimostrata | 0 | 0 | 0 |
| Stage HR open/verified dimostrati | 0 | 0 | 0 |

Il risultato e' **un incremento reale di lead candidati rispetto allo snapshot storico precedente**, che non aveva nuovi datori. Non e' un incremento di fonti operative, stage verificati o copertura nazionale. Non si sono controllate dimensioni, mansioni HR, language requirements, ATS, candidatura, robots del singolo datore o sovrapposizione fra gruppi.

**Costi del prototipo aggiuntivo:** richieste crawler GitHub 0; browser rendering 0; nuove fonti attive 0; costo monetario non misurato. La consultazione web manualmente mirata delle pagine di provenienza non equivale a un run del collector. Prima del vero pilot misurare numero di richieste autorizzate, durata, bytes e 2 cicli live su una fotografia stabile.

## Verifica del riuso dello storico

Ho confrontato `docs/employer-mapping-audit.json` con le aziende oggi censite, usando nome e dominio come chiavi conservative: **472 righe** (DE 233, FR 97, NL 142), tutte gia' presenti. **Nuove aziende effettivamente individuate nello storico = 0**. Il risultato evita di spendere altre risorse sullo stesso snapshot. Le due nuove aziende dei test unitari sono esempi sintetici; non contano verso la copertura europea.

La CI della PR #34 al commit `e4aca924a870e24bd053583b881a6fd5585e8515` e' verde (run [#43306446272](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43306446272) e [#43306529615](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43306529615)): **294 test Python**, **24 frontend**, 64 esempi di valutazione, build e company coverage. Durata test Python del run ispezionato 48,3 secondi, non tempo complessivo del job.

## Beneficio e costo

Questa PR dimostra soltanto il processo di acquisizione con test su documenti sintetici: due aziende nuove simulate, una già nota scartata, riconciliazione cross-country, due esecuzioni idempotenti e quarantena di HTTP/host sospetti. **0 nuovi stage HR verified, 0 fonti ATS nuove, 0 richieste live, 0 rendering**. Tempo CI da misurare nel workflow, costo monetario non noto. Anche se il primo risultato live sarà zero, lo segnaleremo come zero e non come raccolta di aziende completata.

## Allocazione futura del budget

L'allocazione non cambia in questa PR. Quando saranno disponibili almeno due cicli comparabili, suggerisco un budget giornaliero con 70% per fonti produttive e candidati HR verificabili, 20% per nuove fonti/country gaps, 10% per recupero di fonti degradate. Sono **percentuali da validare con dati reali**, non configurazione già attiva.

Rendere visibili per ogni fonte: richieste, secondi, browser rendering, inventario completo/parziale, candidati HR distinti, candidature same-vacancy policy v2, freschezza e country effettivamente confermato. Misurare `delta verified internships / richieste` su raccolte riuscite (non dividere i record storici per un numero di richieste di un run parziale).

## Verifiche prima di qualunque rollout

```sh
python3 -m unittest tests.test_eu_directory_discovery -v
python3 -m unittest discover -s tests -q
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
```

Non aggiungere ancora `schedule` o abilitare seed senza conferma robots, termini, identità, ricavo reale e budget. Restano separate le PR #33, #32, #28 e la Issue #23. Non si fanno merge.
