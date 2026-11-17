# People Placement — ripresa trasversale dei lavori aperti (17 novembre 2026)

**Obiettivo misurabile:** stage HR **distinti, candidabili, policy v2 e ancora verificati da fonti ufficiali**. L'ultimo catalogo pubblicato su `main` `ab51981` contiene **363 ID, 28 stage HR open/verified, 1 working student open/verified**, aggiornamento `partial`. **Non confondere** stage in staging (Jobandtalent 29 virtuali) con nuove opportunità realmente pubblicate. EU27 non è coperta completamente dal fatto che 27 codici paese esistano nel registro.

## Tutte le PR aperte e loro stato

| PR | Intervento realmente eseguito | Stato / produzione |
|---|---|---|
| [#56](https://github.com/nightlydeveloper8/eu-hr-internships/pull/56) | JobTech SE→ATS policy v2, secondo ciclo, dedup; sorgente Jobandtalent `enabled=false`; nuovo audit giornaliero offline delle cause delle offerte non verificate | **Non merged, non attivato, 0 nuovi stage su main** |
| [#41](https://github.com/nightlydeveloper8/eu-hr-internships/pull/41) | Riallineata al main `ab51981` preservando prova di robots 403 per Comune Emmen e documenti, backup `backup/pr41-before-baseline-sync-20261117` | CI verde, **pronta per revisione documentale**, non merged, 0 nuovi stage |
| [#46](https://github.com/nightlydeveloper8/eu-hr-internships/pull/46) | Riallineata al main `ab51981` preservando sei indizi UE27 senza form attestato; fix `filled` e host 429 già in main, non reimplementati. Backup `backup/pr46-before-baseline-sync-20261117` | CI verde, **pronta per revisione documentale**, non merged, 0 nuovi stage |
| [#57](https://github.com/nightlydeveloper8/eu-hr-internships/pull/57) | Reconciliata **solo** la qualifica DOC Kaas (≥200 dipendenti) sui dati del 17/11, preservati gli stati di raccolta correnti e correggendo Hoogeveen e NL size_unknown. Backup `backup/pr57-before-fresh-reconciliation-20261117` | CI verde, **pronta per revisione**, non merged; 40 datori Drenthe, 28 qualificati, 12 ignoti. **0 nuovi stage** |

**Nessuna PR è stata integrata, chiusa o trasformata in rollout.** Le tre PR storiche sono state conservate e riportate allo stesso parent del main moderno con backup; controllo `mergeable=true`, CI riuscita, e ora **tutte e tre sono ready for review anziché draft**, senza merge. Il loro contenuto va comunque revisionato prima di decidere il merge: green CI non dimostra rendimento degli annunci.

## Issue ancora aperte

- [#1 — employer collection needs attention](https://github.com/nightlydeveloper8/eu-hr-internships/issues/1): **1.896 aziende attempted**, **68 collected, 32 verified-empty, 532 partial, 282 blocked/failed, 982 discovery-incomplete** nell'ultimo ciclo. Monitor qualità legittimamente aperto; pipeline ordinaria [#44042092898](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44042092898) è comunque 18/18 verde. Non chiudere Issue #1 finché non migliora la resa reale.
- [#18 — coverage improvement sprint](https://github.com/nightlydeveloper8/eu-hr-internships/issues/18): primo audit su **307 unverified** nel catalogo: **98 record storici quarantinati** per fonte esterna, **77** senza entry di candidatura specifica e **35** con ID di candidatura non dimostrato (altre cause come robots e 429). Queste sono cause di fallimento, **non 210 stage disponibili**. Nuovo generatore `scripts/opportunity_quality.py` classifica e ordina **offline** le famiglie di errori per host, fonte e costi degli ultimi report; integrato in `scripts/company_coverage.py` e aggiunto ai commit automatici del `publish` **soltanto dopo un futuro merge autorizzato**. Zero GET supplementari, nessun LLM, nessuna modifica ai criteri policy v2.
- [#23 — Dynamic ATS opt-in](https://github.com/nightlydeveloper8/eu-hr-internships/issues/23): `.github/workflows/collect.yml` passa già `vars.PEOPLE_PLACEMENT_DYNAMIC_ATS` ai job `collect`, ma non è disponibile qui una lettura certificata della repository variable; **non attestare feature ON/OFF dal solo YAML**. Nessun allargamento dei tre ID pilota o browser introdotto. Il rollback resta valore assente/off e serve una conferma esplicita dell'attivazione.

## Pilota live sull'errore strutturale nelle candidature ufficiali

[One-off #44108780920](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44108780920), **4 GET/60.427 B, 0 browser/POST/candidature**, eseguito sulla baseline main con host già approvati:
- **Danone NL HR Business Partner Internship** (catalogo attuale): il client ha ricevuto `HTTPError` alla lettura della pagina; **0** prova form, non classificare come candidato candidabile. Il diagnostico registra la classe di errore, **non il codice HTTP**, quindi non inventare quale blocco specifico sia avvenuto.
- **Tyche Bank IT HR Intern**: pagina official same-title letta, un link di candidatura on-host osservato ma **nessun link con lo stesso identificativo della vacancy**; modulo non stabilito, **0** verified.
- Nessuna scorciatoia: non sono stati inventati URL di candidatura o host, né aggirati cookie, login, CAPTCHA e robots. Work branch `diagnose/current-official-apply-gaps-20261117` mantiene codice e artifact del singolo test; workflow one-off eliminato dopo la prova. Due fonti puntuali **non** sono una raccolta nazionale o completa.
- Costo totale dei nuovi test live del giorno in questo incarico: **4 GET e 60.427 B**; i test Python/GitHub e audit del catalogo sono offline. **0 stage nuovi verified**, **0 nuovi dati in produzione**. La prova separata dell'adapter Jobandtalent [#44086636248](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44086636248) aveva già misurato **10 richieste, 723.606 B, 13,467s** e +1 stage distinto solo in staging; **non ripetuta** in questo intervento.

## Gate per avanzare con impatto invece di censire aziende

1. **First yield:** una decisione separata sul merge della [#56](https://github.com/nightlydeveloper8/eu-hr-internships/pull/56) con Jobandtalent ancora disabilitata e altri canali solo manuali; **il merge non prova né abilita** 29 stage in produzione. Poi un secondo giorno distinto, attivazione condizionata e primo `collect/publish` misurato.
2. **Second yield:** usare il report automatico per individuare **un pattern di candidatura ufficiale comune** e confrontare prima/dopo: richieste, byte, tempo, ID nuovi davvero verified. Non aggiungere permessi ad ATS proibiti; non ritentare 429 o 403 come normale discovery.
3. **Terzo yield:** secondo feed nazionale UE27 consentito con licenza/robots/API chiari e campione limitato; CZ MPSV/LV NVA (zero stage HR nel campione), LT (429) ed EURES (upstream non autorizzato) non sono ancora rendimenti positivi dimostrati. Investire su un nuovo feed solo quando produce un ATS aziendale verificabile a costo sostenibile.

**Definizioni da non confondere:** modifica nel ramo ≠ PR aperta ≠ merge ≠ fonte attivata ≠ stage pubblicato e verificato in produzione. Stato di produzione corrente: `main ab51981`, 28 stage HR verified; tutte le novità di questa ripresa sono su rami non integrati.
