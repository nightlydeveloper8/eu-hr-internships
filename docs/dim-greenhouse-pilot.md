# DIM Greenhouse: audit economico di due cicli reali e scelta di un discovery feed UE

**Data di controllo:** 13 novembre 2026 · **Obiettivo:** piu' stage HR open/verified, distinti e candidabili, non piu' aziende in lista.

## 1. Selezione del tenant pilota

Il target e' `greenhouse-dim`, board ufficiale [DIM](https://job-boards.greenhouse.io/dim) (`board=dim`) nel registro attivo gia' pubblicato. La board presenta **33 annunci** nella consultazione web del 13 novembre, inclusa la vacancy <https://job-boards.greenhouse.io/dim/jobs/8331346>:

- `Stage Chargé(e) de Développement RH (H/F) - Janvier 2027` presso Rueil-Malmaison, **FR**, sei mesi da gennaio 2027.
- Attivita' HR: recruiting, follow-up di stagisti, employer branding, formazione. La pagina ospita un modulo di candidatura **della specifica vacancy**.
- L'annuncio richiede livello professionale di inglese; **non afferma che la sola lingua inglese sia sufficiente** per lavorare in quel ruolo. Campo English-only da mantenere sconosciuto/non confermato.
- Proprieta': datore DIM/DBI citato espressamente nell'annuncio sul tenant Greenhouse; e' necessario mantenere il vincolo di ownership su ogni record e non estenderlo a gruppi o affiliate per inferenza.
- API ufficiale [Greenhouse Job Board](https://docs.greenhouse.io/job-board): `GET https://boards-api.greenhouse.io/v1/boards/dim/jobs?content=true`, pubblico, senza autenticazione, documentato per leggere l'inventario e le descrizioni. Nessun POST/candidatura.

## 2. Prova da **due cicli di produzione completati**

La prova e' già prodotta dagli ordinari run giornalieri del progetto: **10** e **12 novembre 2026**, con 18 job verdi ciascuno. Non si tratta di due GET effettuati dalla presente PR, né di simulazioni. Recuperabili dai file `data/coverage.json` e `data/catalog.json` *alle revisioni indicate*, con timestamp source e URL apply.

| Campo | Ciclo 10 novembre | Ciclo 12 novembre |
| --- | ---: | ---: |
| Actions | [#42774047883](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42774047883) | [#43297447671](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43297447671) |
| Commit publish | `0e73e9a7b26d7c674110beb50697fd29a8e2fdf1` | `e7056c3351d06bedaa1f0d4a8e443f5a6e424a78` |
| Fonte, stato | greenhouse-dim / ok | greenhouse-dim / ok |
| Record raccolti / esaminati | 33/33 | 33/33 |
| Errori pagina | 0 | 0 |
| HR internships matching | 1 | 1 |
| Policy v2 HR internships verified | 1 | 1 |
| Richieste logiche | 4 | 4 |
| Durata fonte, secondi | 1,4 | 1,4 |
| Byte letti | 304.894 | 305.000 |
| ID catalogo verified | `270e918796f15d39a095` | `270e918796f15d39a095` |

**Delta realmente misurato:** 1 stage HR verified **mantenuto**, **0 nuovi ID verified** nel secondo ciclo, **0 persi**. Totale risorsa per i due cicli: **8 richieste logiche, 2,8 s di durata fonte, 609.894 byte**. Il costo aggregato della raccolta non comprende overhead GitHub Actions, altre fonti, Playwright setup e risorse CI. Il costo monetario non e' stato misurato.

Artefatto di audit in `docs/greenhouse-dim-two-cycles.json`, confrontabile senza rete:
```sh
python3 scripts/audit_greenhouse_cycles.py
python3 -m unittest tests.test_greenhouse_cycles -v
```

I test rifiutano due revisioni identiche dello stesso workflow, status partial, raccolte incomplete, duplicati, job fuori dal paese o senza modulo vacancy-specific, timestamp non coerenti e regressioni policy v2. L'audit **non scrive** su catalogo, sources o companies.

## 3. Riuso per nuovi datori BE/IE: fonte con licenza esplicita

**[Wikidata (CC0)](https://www.wikidata.org/wiki/Wikidata:Licensing)** e' adatta a un primo pilota piccolo per scoprire aziende e URL P856 (sito ufficiale) in Belgio/Irlanda, filtrando per paese P17 e categorie aziendali. Il [Wikidata Query Service](https://www.wikidata.org/wiki/Wikidata:Data_access/en) documenta un endpoint SPARQL GET/POST. Serve una query *bounded* (massimo 20-30 lead per paese come prima prova), User-Agent identificabile, nessun parallelismo, un massimo di due richieste iniziali; rispettare robots, 429/Retry-After e regole di rate limit pubblicate.

**Avvertenza:** Wikidata e' collaborativo, NON un registro imprese ufficiale. La proprieta' del dominio deve essere verificata indipendentemente prima di qualsiasi GET ai siti aziendali, nessun link Wikidata e' autorizzazione a entrare nel loro ATS. Non equivale a un inventario di annunci, non verifica lingua o candidabilita'. **Nessuna richiesta SPARQL live e' stata effettuata in questo intervento.**

Dopo i primi candidati Wikidata, usare a seconda del caso [CRO Ireland Company Records](https://opendata.cro.ie/dataset/companies), CC BY 4.0 e snapshot quotidiano, per identificativi legali; per il Belgio [CBE Open Data](https://economie.fgov.be/en/themes/enterprises/crossroads-bank-enterprises/services-everyone/public-data-available-reuse/cbe-open-data) richiede registrazione e accettazione termini. Evitare download massivi non necessari e servizi a pagamento. CRO/CBE da soli non provano vacancy HR.

L'alternativa migliore per **annunci** resta l'API pubblica del singolo ATS/tenant ufficiale, come Greenhouse, ma non esiste una lista globale di tutte le imprese e le vacancy su tale API pubblica.

## 4. Rendimento minimo: due KPI separati

**Mantenimento di fonte gia' attiva:** `HR verified preservati / richieste ciclo`. DIM = `1/4 = 0,25` per richiesta, o **25 mantenimenti per 100 richieste**, con inventario completo al 100% in due cicli. L'annuncio e' uno solo: le conferme ripetute non diventano due nuove opportunita'. Proporre un costo massimo iniziale di **8 richieste per ciclo per una board di dimensioni confrontabili**, cioe' due volte il benchmark DIM; questo e' un guardrail *proposto*, non globale.

**Espansione a nuovo tenant:** `nuovi ID HR verified netti / richieste totali` rispetto al catalogo prima del pilota. Come **criterio sperimentale**, promuovere una fonte a monitoraggio quotidiano solo se, con ownership e robots conformi, raccoglie l'inventario completo in **due cicli distinti**, produce almeno **uno stage HR nuovo, specifico, aperto e verificato** e usa al massimo **16 richieste logiche totali** (massimo 8 per ciclo). Se manca una nuova vacancy, non confondere la situazione con un errore del canale: conservare il candidato nella quota esplorativa con frequenza inferiore o rivalutare il limite dopo una finestra ragionevole. Non dichiarare mai verificato un annuncio con link generico o lingua inferita.

Il rapporto DIM soddisfa la prova di **mantenimento**, non prova nuove opportunita' ottenute con onboarding. La quota 70/20/10 e' ancora un'ipotesi, non una variabile di GitHub Actions o una politica di produzione.

## 5. Blocchi e prossima azione

`https://boards-api.greenhouse.io/robots.txt` non era recuperabile tramite tool web e la risoluzione DNS del runtime locale e' fallita. **Non** e' un robots disallow dimostrato, ma impedisce oggi un nuovo GET automatico autorizzato. La board frontend DIM invece risultava pubblicamente consultabile. Il confronto usa **solo due raccolte storiche reali** gia' riuscite; un nuovo pilot live richiede controlli robots riusciti in un runtime idoneo.

Non e' stato modificato alcun workflow, collector attivo, fonte autorizzata, catalogo, regola di freschezza 48h o gate Dynamic ATS #23. Questa PR e' una **PR di audit e test**, non un'attivazione o un rollout. Non fare merge senza autorizzazione specifica.
