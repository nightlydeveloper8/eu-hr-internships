# Primi lotti ATS — 23 novembre 2026

Preparazione in hold a partire dalle chiavi dei tre crawl del [dossier #134](ats-tenant-discovery-2026-11.md). La popolazione di ricerca è di 9.100 chiavi: 3.289 Personio, 960 Recruitee, 4.783 Greenhouse e 68 Lever EU. La copertura del mercato europeo è **non dimostrata**.

## Censimento e accesso

Lo script `scripts/ats_held_census.py` parte dall’inventario integrale, senza estrazione a campione. Riutilizza gli adapter esistenti. Per ogni host esige robots con HTTP 200, controlla il percorso e rispetta il crawl delay. GET con user agent People Placement, nessun redirect fuori scope o login. Il limite giornaliero è di 15.000 GET, inclusi robots, paginazione e ritentativi. Il budget per tenant è di 12 GET, 45 s operativi, con attesa separata per un primo 429 a robots quando prevista. Il libro di staging consente di riprendere dagli esiti già scritti. L’ipotesi con un GET feed per tenant, un robots per ciascun host singolo e tre host centrali vale circa 13.352 GET sull’intero perimetro. Paginazione e retry possono richiedere più giorni. I limiti interrompono il lavoro e lasciano espliciti i tenant mancanti. [Regola d’accesso](../AGENTS.md#4-fonti-e-raccolta-dati) · [Documentazione e termini dei feed](ats-tenant-discovery-2026-11.md#staging-e-resa-per-paese)

Pausa minima iniziale di 1 s per host e successiva ripresa Greenhouse globale al ritmo di base di 0,5 s del collector, rispettando eventuali indicazioni più restrittive. Personio ha restituito 429 ripetuti su host distinti, quindi la coda è stata sospesa. Anche Recruitee è stata sospesa dopo 429 su tre host. Greenhouse EU non ha risolto in DNS nell’ambiente di staging. Greenhouse globale ha terminato i tentativi su tutte le 4.339 chiavi. Lever EU è stato tentato per tutte le 68 chiavi; un 404 resta un esito incompleto. I risultati non letti e i blocchi restano fuori dai lotti.

| ATS | Inventario | Tentativi / feed letti | Tenant con sede europea | Posting europei | Segnali HR per paese | GET / byte / s-fonte | GET per segnale |
|---|---:|---:|---:|---:|---|---|---:|
| Personio | 3.289 | 539 / 369 | 210 | 1.703 | DE 6 | 1.054 / 23.168.436 / 1932.829 | 175.7 |
| Recruitee | 960 | 24 / 20 | 16 | 612 | DE 1, NL 2 | 48 / 10.337.966 / 28.256 | 16.0 |
| Greenhouse | 4.783 | 4.640 / 4.124 | 920 | 15.123 | DE 2, FR 1, GB 2, NL 2 | 4.644 / 1.770.940.631 / 3939.945 | 663.4 |
| Lever EU | 68 | 68 / 67 | 53 | 1.445 | PL 1 | 79 / 38.591.312 / 78.474 | 79.0 |

Checkpoint: 5.271/9.100 chiavi con un esito, 4.580 feed letti, 1.199 tenant con almeno un posting europeo. GET misurati 5.825 e 1.843.038.345 byte. I due arresti del processo precedente al checkpoint possono aver lasciato GET in transito non registrati: il totale misurato è un limite inferiore. Censimento completo dei quattro ATS **non dimostrato**.

Il filtro territoriale applica il riconoscimento già usato dal collector ai soli campi di località del posting, con almeno una sede in UE27, CH o GB. I segnali richiedono la classificazione in stage HR per studenti. I paesi contano i segnali multilocalizzati in ciascuna sede riconosciuta; alias tra ATS diversi possono riferirsi allo stesso annuncio. La lettura feed stabilisce un segnale di inventario. La disponibilità di una candidatura ufficiale same-ID entro 48 ore richiede una verifica v2 distinta. Resa v2 **non dimostrata** in questa prova. I costi sono GET, byte dei corpi letti e secondi-fonte, non costi monetari.

## Registri e cadenza proposta

`scripts/prepare_ats_held_lots.py` prepara record con `enabled: false`, `collection_activation_hold: true` e `rollout_batch_id`. Ogni lotto contiene al massimo 500 fonti. Le chiavi già censite e le collisioni con nomi o alias noti sono escluse. Quando il feed non espone un nome univoco, il registro conserva la chiave visibile dell’ATS come etichetta di ricerca e marca `board-handle-only`; il nome legale resta **non dimostrato**. Le località osservate servono come paesi obiettivo, senza promuovere sedi di lavoro o regioni non provate. La preparazione verifica che il provisioning conservi tutti gli ID e l’insieme delle fonti attive.

| Lotto | Fonti disabilitate | Segnali HR osservati nel lotto | Stage effettivamente attesi |
|---|---:|---:|---|
| `ats-2026-11-01` | 500 | 12 | non dimostrato |
| `ats-2026-11-02` | 500 | 0 | non dimostrato |
| `ats-2026-11-03` | 177 | 0 | non dimostrato |

Totale pronti 1.177. Già registrati o conflitti di identità: greenhouse/identity-collision 1, greenhouse/registered 5, personio-xml/identity-collision 14, recruitee/identity-collision 1, recruitee/registered 1.

La futura regola per ATS può automatizzare i gate su host, robots, formato, identità del datore e candidatura same-ID, registrando eccezioni e collisioni. Prima di un’autorizzazione per lotto, validare attestazione del datore, alias con fonti esistenti, budget e controlli v2. Ogni tenant con segnale HR osservato negli ultimi 60 giorni entra nella proposta di lettura giornaliera. Gli altri sono distribuiti tra sette giorni mediante hash stabile. Stati incompleti e rate limit restano distinti da inventari letti senza segnali. La cadenza richiede un intervento futuro. Il workflow odierno legge tutte le fonti abilitate a ogni ciclo.

Per il lotto 1, 10 fonti a cadenza giornaliera e 490 settimanali, con picco 90 fonti e 1080 GET logici per ciclo a 12/tenant. Per i 16 shard attuali e 6 worker per shard, il picco è 13 fonti aggiuntive sul singolo shard, circa 135 s di budget in più in condizioni ideali e senza contesa. Gli host centrali devono condividere il limite fra shard, quindi la durata reale è **non dimostrata**. La raccolta baseline del 23 novembre è durata circa 23 minuti. Mantenere 16 shard nel primo scenario e misurare il p95 prima di risuddividerli. [Baseline di raccolta](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45227139250)

## Simulazione lotto 1

La selezione è eseguita su copie in memoria dei registri, usando il provisioning esistente. Nessuna fonte attiva o hold modificati nei file di produzione. Il replay del catalogo usa il timestamp dello snapshot di main e nessuna nuova osservazione v2. Le nuove aperture o candidature dirette dopo un’attivazione restano **non dimostrate**.

| Misura | Prima | Dopo (replay senza nuove prove) |
|---|---:|---:|
| ID distinti | 937 | 937 |
| ID persi | 0 | 0 |
| Stage aperti | 424 | 424 |
| Candidature dirette | 54 | 54 |
| Paesi con stage | 13 | 13 |

**Un merge dei registri avvierà `collect.yml`.** Le fonti di questi lotti resteranno disabilitate e il provisioning non creerà crawler universali per i datori in hold.
