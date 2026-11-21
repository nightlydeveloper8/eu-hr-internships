# Audit conversione lead HR — snapshot 21 novembre 2026

## Perimetro verificato

- Base: [main `f0cfe6`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/f0cfe6ead0fb6f3c1c3f6b26175f1a6a052b9d85); catalogo `updated_at=2026-11-21T07:35:04.489010+00:00`, `update_status=partial`.
- Catalogo: **906 record, 906 ID distinti, 402 stage HR attuali**, di cui **37 candidature dirette policy v2** e **365 annunci dei servizi pubblici**. Questi ultimi non hanno automaticamente la candidatura del datore verificata.
- Diagnosi **367 lead**: internship con `status=unverified` esclusi i **93 record** il cui URL storico esterno non dimostra la titolarità del datore. I 93 restano nel catalogo e non vengono promossi né cancellati. I record chiusi e i working student non sono lead candidabili.
- **Nessun collector eseguito in questa diagnosi; 0 nuove richieste HTTP agli employer, 0 byte scaricati dai siti, 0 stage convertiti dimostrati.** Le misure per fonte sottostanti provengono dal report della raccolta ordinaria, non sono nuovi piloti. Nessun cambiamento a `catalog.json`, `sources.json`, `companies.json` o alla policy v2.
- Riproduzione: `python3 scripts/lead_conversion_audit.py --json .staging/lead-audit.json --csv .staging/lead-matrix.csv`. La tabella è una **fotografia diagnostica storica**, non una prova live delle singole candidature oggi.

## Diagnosi per motivo — 367/367

| Ragione conservativa | Lead |
|---|---:|
| missing-application-entry | 176 |
| expired-verification | 57 |
| application-id-not-matched | 38 |
| robots-unavailable | 30 |
| vacancy-identity-mismatch | 14 |
| time-budget-exhausted | 14 |
| public-listing-too-old-or-undated | 10 |
| rate-limited | 6 |
| application-identity-mismatch | 6 |
| dynamic-form-or-login-unconfirmed | 3 |
| robots-disallowed | 3 |
| disabled-applicant-submit | 2 |
| parsing-error | 2 |
| ownership-review-required | 2 |
| legacy-proof-ineligible | 1 |
| redirect-identity-unconfirmed | 1 |
| read-timeout | 1 |
| request-budget-exhausted | 1 |
| **Totale** | **367** |

La causale riflette la **prova disponibile**: per esempio `missing-application-entry` non stabilisce se un modulo esista altrove, `expired-verification` non conferma che l'annuncio sia ancora online e `robots-unavailable` non autorizza a ritentare eludendo robots.

## Paesi — 367/367

| Paese | Lead |
|---|---:|
| FR | 142 |
| NL | 94 |
| IT | 39 |
| DE | 36 |
| ES | 20 |
| PL | 10 |
| GB | 7 |
| CH | 4 |
| BE | 3 |
| SE | 3 |
| LU | 3 |
| HU | 2 |
| CZ | 1 |
| AT | 1 |
| PT | 1 |
| MT | 1 |
| **Totale** | **367** |

## Motivo × paese × famiglia ATS/adattatore (76 righe, tutti i 367 lead)

La famiglia viene nominata come ATS **solo quando un dominio provider esatto o il registro delle fonti lo supporta**. Le righe `(ATS unconfirmed)` indicano l'adattatore del collector, **non** un fornitore ATS identificato.

| Paese | Famiglia ATS/adattatore | Blocco osservato | Conteggio |
|---|---|---|---:|
| FR | Radancy (source reviewed) | missing-application-entry | 87 |
| NL | EURES | expired-verification | 36 |
| FR | universal-employer (ATS unconfirmed) | application-id-not-matched | 14 |
| NL | universal-employer (ATS unconfirmed) | missing-application-entry | 13 |
| IT | universal-employer (ATS unconfirmed) | missing-application-entry | 12 |
| FR | employer-sitemap (ATS unconfirmed) | missing-application-entry | 10 |
| IT | universal-employer (ATS unconfirmed) | time-budget-exhausted | 9 |
| NL | employer-index (ATS unconfirmed) | missing-application-entry | 8 |
| ES | Amazon.jobs | robots-unavailable | 8 |
| NL | universal-employer (ATS unconfirmed) | application-id-not-matched | 7 |
| DE | Amazon.jobs | robots-unavailable | 7 |
| FR | SmartRecruiters | vacancy-identity-mismatch | 7 |
| PL | employer-sitemap (ATS unconfirmed) | missing-application-entry | 7 |
| FR | EURES | expired-verification | 7 |
| IT | employer-sitemap (ATS unconfirmed) | missing-application-entry | 7 |
| GB | Amazon.jobs | robots-unavailable | 7 |
| FR | universal-employer (ATS unconfirmed) | missing-application-entry | 6 |
| NL | universal-employer (ATS unconfirmed) | rate-limited | 6 |
| DE | universal-employer (ATS unconfirmed) | time-budget-exhausted | 5 |
| ES | employer-sitemap (ATS unconfirmed) | missing-application-entry | 5 |
| DE | EURES | public-listing-too-old-or-undated | 5 |
| DE | employer-sitemap (ATS unconfirmed) | missing-application-entry | 4 |
| IT | Amazon.jobs | robots-unavailable | 4 |
| DE | universal-employer (ATS unconfirmed) | application-id-not-matched | 4 |
| ES | EURES | public-listing-too-old-or-undated | 4 |
| IT | EURES | expired-verification | 4 |
| NL | employer-sitemap (ATS unconfirmed) | missing-application-entry | 4 |
| PL | Amazon.jobs | robots-unavailable | 3 |
| FR | SmartRecruiters | missing-application-entry | 3 |
| NL | universal-employer (ATS unconfirmed) | dynamic-form-or-login-unconfirmed | 3 |
| FR | universal-employer (ATS unconfirmed) | application-identity-mismatch | 3 |
| CH | EURES | expired-verification | 3 |
| DE | Radancy (source reviewed) | application-id-not-matched | 3 |
| DE | Personio | disabled-applicant-submit | 2 |
| NL | universal-employer (ATS unconfirmed) | parsing-error | 2 |
| DE | universal-employer (ATS unconfirmed) | missing-application-entry | 2 |
| NL | employer-index (ATS unconfirmed) | robots-disallowed | 2 |
| NL | employer-index (ATS unconfirmed) | expired-verification | 2 |
| DE | EURES | expired-verification | 2 |
| SE | employer-sitemap (ATS unconfirmed) | missing-application-entry | 2 |
| FR | employer-sitemap (ATS unconfirmed) | application-id-not-matched | 2 |
| LU | Radancy (source reviewed) | application-id-not-matched | 2 |
| IT | employer-sitemap (ATS unconfirmed) | application-id-not-matched | 1 |
| DE | universal-employer (ATS unconfirmed) | vacancy-identity-mismatch | 1 |
| HU | universal-employer (ATS unconfirmed) | application-id-not-matched | 1 |
| CZ | Amazon.jobs | robots-unavailable | 1 |
| IT | SmartRecruiters | vacancy-identity-mismatch | 1 |
| NL | SmartRecruiters | vacancy-identity-mismatch | 1 |
| BE | SmartRecruiters | vacancy-identity-mismatch | 1 |
| HU | SmartRecruiters | vacancy-identity-mismatch | 1 |
| SE | SmartRecruiters | missing-application-entry | 1 |
| ES | universal-employer (ATS unconfirmed) | missing-application-entry | 1 |
| AT | universal-employer (ATS unconfirmed) | missing-application-entry | 1 |
| LU | universal-employer (ATS unconfirmed) | expired-verification | 1 |
| FR | SmartRecruiters | legacy-proof-ineligible | 1 |
| NL | Radancy (source reviewed) | missing-application-entry | 1 |
| NL | employer-index (ATS unconfirmed) | vacancy-identity-mismatch | 1 |
| ES | universal-employer (ATS unconfirmed) | redirect-identity-unconfirmed | 1 |
| NL | universal-employer (ATS unconfirmed) | read-timeout | 1 |
| NL | Workday | vacancy-identity-mismatch | 1 |
| DE | universal-employer (ATS unconfirmed) | request-budget-exhausted | 1 |
| NL | Recruitee | ownership-review-required | 1 |
| NL | employer-index (ATS unconfirmed) | application-identity-mismatch | 1 |
| NL | employer-index (ATS unconfirmed) | ownership-review-required | 1 |
| NL | universal-employer (ATS unconfirmed) | application-identity-mismatch | 1 |
| NL | Recruitee | expired-verification | 1 |
| ES | universal-employer (ATS unconfirmed) | application-id-not-matched | 1 |
| BE | EURES | expired-verification | 1 |
| IT | universal-employer (ATS unconfirmed) | robots-disallowed | 1 |
| CH | EURES | public-listing-too-old-or-undated | 1 |
| PT | employer-sitemap (ATS unconfirmed) | missing-application-entry | 1 |
| MT | employer-sitemap (ATS unconfirmed) | missing-application-entry | 1 |
| FR | Radancy (source reviewed) | application-identity-mismatch | 1 |
| BE | employer-sitemap (ATS unconfirmed) | application-id-not-matched | 1 |
| NL | Radancy (source reviewed) | application-id-not-matched | 1 |
| FR | Radancy (source reviewed) | application-id-not-matched | 1 |

## Metriche del ciclo ordinario 21/11 per le fonti con più lead

**Attenzione:** GET, byte e durata indicano l'intera fonte, compresi gli altri annunci raccolti, e **non** il costo marginale dei soli lead qui contati. Un run `partial` non prova che tutti i lead siano stati ricontrollati.

| Fonte | Lead in catalogo | GET ciclo | Byte letti ciclo | Secondi fonte | Stato |
|---|---:|---:|---:|---:|---|
| `employer-adecco-group` | 87 | 217 | 19528306 | 117.75 | partial |
| `public-eu-eures` | 63 | 330 | 95979098 | 656.07 | partial |
| `amazon-hr-internships` | 30 | 92 | 1657511 | 88.27 | partial |
| `auto-randstad-italia-spa` | 20 | 30 | 13276217 | 103.23 | partial |
| `auto-l-oreal` | 11 | 64 | 17042457 | 149.17 | partial |
| `employer-danone` | 9 | 75 | 16016929 | 180.1 | partial |
| `employer-marriott` | 9 | 59 | 25204718 | 63.3 | partial |
| `employer-ing` | 7 | 15 | 11519723 | 19 | partial |
| `auto-landal` | 5 | 76 | 10206210 | 112.53 | partial |
| `auto-bmw-group` | 5 | 43 | 943641 | 120.2 | partial |
| `auto-axs-logistiek` | 4 | 71 | 14137154 | 102.12 | partial |
| `auto-jde-peet-s` | 4 | 94 | 6145853 | 84.52 | partial |

Run del catalogo: [Daily #44879531709](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44879531709). Lo script computa 0 nuove richieste; il tempo di calcolo locale e i byte del traffico GitHub connector non sono stati strumentati.

## Le tre leve più importanti, e cosa **non** è lecito fare

1. **Modulo vacancy-specific non trovato (176 lead, di cui 87 Adecco FR).** Il sito Adecco è Radancy nel registro. Il ciclo ordinario per `employer-adecco-group` ha consumato **217 GET / 19.528.306 byte / 117,75 s** e non ha prodotto candidature verificate per il gruppo. [Pilota ufficiale #44735997779](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44735997779) e [percorso #44736268862](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44736268862): 2 posting distinti, 0 moduli specifici confermati; percorso osservato verso area CV/account senza identità della vacancy. **Non basta allentare il matching.** Le altre 89 schede del motivo richiedono analisi delle rispettive famiglie, non un workaround unico.
2. **Prova scaduta o invalida (57 lead; 53 EURES).** La sola via corretta è ri-osservare il medesimo identificativo nel servizio pubblico in una nuova raccolta conforme al suo crawl-delay. Il ciclo EURES ha consumato **330 GET / 95.979.098 byte / 656,07 s**, con 352 listing correnti e 10 listing vecchi/non datati non promossi. Anche recuperando la freschezza, EURES dà **listing pubblico**, **non candidatura diretta**: quindi non risolve l'obiettivo di +50 domande dirette.
3. **Identificatore domanda-vacancy non coincidente (38 lead).** Fra i casi `auto-l-oreal` ci sono 7 posizioni FR di questo tipo, ma non una prova di modulo same-ID. L'eventuale correzione deve ottenere l'ID da una CTA **ufficiale osservata**, verificare l'host e controllare il modulo; **mai dedurlo dall'URL inventato**. [Pilota Danone #44736658503](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44736658503) conferma in 2 casi CTA verso login: 0 candidature verificabili senza autenticazione.

**Blocco distinto da non aggirare:** 30 lead Amazon.jobs (in `amazon-search`) hanno `robots.txt` non disponibile con HTTP 403; il ciclo fonte ha registrato **92 GET / 1.657.511 byte / 88,27 s**, ma zero prove di candidatura per quei record. Non si propone di aggirare il blocco.

### Perché +50 non sono dimostrabili in questo checkpoint

Il catalogo **non contiene** prova policy v2 fresca con percorso candidatura diretto per 50 dei 367 lead. I due piloti Adecco mostrano un percorso senza modulo vacancy-specific; Danone conduce al login; 53 EURES scaduti non possono costituire candidature del datore; Amazon ha blocco di accesso. **Non è una prova che questi stage non esistano**: significa che non è possibile promuoverli in blocco in sicurezza dal materiale disponibile. Non sono stati effettuati nuovi test live in staging, perciò non si affermano incrementi verificati né nuovi costi di rete.

**Prossima leva migliore:** ottenere, con piloti GET/robots-aware strettamente limitati, prima **due vacancy di due datori distinti della stessa famiglia ATS**, per cui siano visibili inventario ufficiale, ID vacancy e formulario same-ID pubblico, e misurare costo marginale/resa su snapshot separati. Preferire ATS con precedente prova riuscita (per esempio Recruitee con [lotto #86](https://github.com/nightlydeveloper8/eu-hr-internships/pull/86), sei candidature dirette reali), **non** grandi gruppi privi di formulario. Ogni fonte nuova rimane disabilitata o in hold; l'eventuale rollout richiede altra autorizzazione.

## Stato della modifica

Solo `scripts/lead_conversion_audit.py`, test dedicati e documentazione; implementazione per conversione dei tre adapter **non eseguita** senza nuove prove di sicurezza e disponibilità. Validazione del codice attraverso CI della branch/PR: vedere la PR; *nessuna prova live nuova e nessun deploy*. Il target **+50** non è raggiunto.