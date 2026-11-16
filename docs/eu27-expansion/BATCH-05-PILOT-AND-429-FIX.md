# Lotto 05 — pilota limitato Marquardt, SLB, TikTok e correzioni strutturali

Data di revisione: **16 novembre 2026**. Separato dalla [PR #46](https://github.com/nightlydeveloper8/eu-hr-internships/pull/46) (ricognizione CZ/RO/SE/IE). **Non ammissione, non attivazione.** Nessuna candidatura, login, POST o renderizzazione eseguita.

## Verifiche sulle fonti ufficiali

Sono state consultate e seguite le pagine **ufficiali** e le rispettive CTA tramite ricerca web. Il tool di consultazione non espone una lettura affidabile dei file `robots.txt` dei tre host; i redirect e le pagine di arrivo non equivalgono a una sessione con il `BudgetClient` conforme al progetto. **Robots, inventario completo e form anonimo non attestati dal pilot**: tutte e tre le opportunità restano **unverified**; non configurare connettori giornalieri da questa ricognizione.

| Datore | URL vacancy ufficiale | Evidenze osservate | Candidatura/limite | Esito |
| --- | --- | --- | --- | --- |
| Marquardt RO | https://www.marquardt.com/careers/job-search/detail/hr-internship-french-english-speakers-f-m | Ruolo HR in Sibiu, presente anche nella job search dell'azienda; richiede francese+inglese, accordo universitario, non retribuito; CTA aziendale `Apply now` verso `https://marquardt-ro.mingle.ro/en/apply/sUQZQQ` | La pagina Mingle raggiunta dal collegamento mostra solo shell/iframe nel tool: nessun modulo visibile abilitato e identità nel form non verificati | **Unverified**; migliore priorità tecnica per verifica futura |
| SLB RO | https://careers.slb.com/jobdescription.aspx?id=EF12289-en_US+1 | Human Resources Internship a Bucharest, CTA ufficiale verso `https://apply.slb.com/careers/apply?domain=slb.com&pid=563499731000279`, compenso 4.444 RON lordi/mese | Il portale Eightfold mostra configurazione con `disableLoggedOutApply: true`, `recaptchaEnabled: true`; non è prova di un modulo anonimo per questa vacancy e non si entra | **Unverified**, non ammettere |
| TikTok IE | https://lifeattiktok.com/search/7694622895491205429 | Ruolo HR Operations Lifecycle Intern 2027 Dublin, job code A187616, CTA specifica verso `https://careers.tiktok.com/resume/7694622895491205429/apply`; datore e lead già nel lotto 01 | Il collegamento fa redirect verso `lifeattiktok.com/resume/7694622895491205429/apply`, non accessibile al tool; form/robots non dimostrati | **Unverified**, non contare nuova azienda/lead |

Non dichiarare i tre ruoli English-only. L'utente non ha autorizzato aggiramenti e il tool non ha prova verificabile dell'accessibilità dei moduli.

## Verifica Electrolux e difetto HTTP 429

La prova già archiviata nel [preflight lotto 05](batch-05-preflight-2026-11-16.json) documenta `JR81378`: risposta HTTP 200 con JSON-LD `JobPosting`, ma testo ufficiale “The job you are trying to apply for has been filled”. La verifica di chiusura nel codice riconosceva “no longer available” ma non questa formulazione. La nuova regressione forza precedenza del **testo attuale** sul JSON-LD residuo, mantenendo closed la vacancy; non cambia `validThrough`, policy v2 o regole di candidatura.

Il client `BudgetClient` precedentemente contabilizzava ogni URL e, dopo il primo 429, poteva continuare a chiamare lo stesso host (documentato sul tenant Manifesto nel preflight precedente con cinque URL 429). Ora dopo **un HTTP 429 effettivo** viene sospeso quell'host **per il processo di raccolta corrente**. Lo stato è condiviso tra client nello stesso processo, non tra esecuzioni o macchine diverse. I successivi tentativi danno immediatamente un HTTP 429 locale senza nuova richiesta; vengono registrati come errore/blocco e non come inventario vuoto. Host indipendenti non sono sospesi, come dimostrano le regressioni simulate. Requisiti robots, autorizzazioni dei redirect e budget non cambiano; nessun retry forzato, nessun bypass.

## Misura del beneficio e dei costi

- **Beneficio reale di disponibilità nel pilota:** zero nuove offerte candidabili policy v2, zero record pubblicati, baseline di produzione documentata a **28 stage verified + 1 working student**, 361 annunci.
- **Riduzione misurabile nelle fixture offline:** dopo un 429 per lo stesso host la seconda URL produce **zero ulteriori chiamate di rete**, e il contatore dei request effettivi rimane stabile. Questo misura un risparmio potenziale delle richieste ripetute, **non** un aumento delle candidature.
- **Costo addizionale quotidiano in produzione:** **0** (nessuna sorgente abilitata). Le consultazioni via ricerca web non sono una misurazione del runtime: durata/byte del nuovo pilota non disponibili.
- **Tetto di pianificazione condizionale**, non spesa misurata: usando i limiti del preflight per tre fonti (massimo **8 richieste e 45 secondi-fonte per datore**), il tetto aggregato sarebbe 24 richieste e 135 secondi-fonte giornalieri, oltre a 0 browser. **Non è una previsione attendibile di consumo**, e non si autorizza alcuna delle tre fonti con queste sole prove. Gli host ATS esterni, i redirect e i rispettivi robots richiedono review.
- **Confronto col preflight già documentato:** 27 richieste, 14,721 secondi-fonte, 1.222.790 byte su CZ/RO/SE/IE; i cinque 429 osservati su URL Manifesto sono storico, non un nuovo risparmio live attribuibile al fix.

## Verifiche e prossime azioni

Modifiche isolate a `collector/runtime.py` (circuit breaker host 429), `collector/applications.py` (chiusura filled) e `tests/test_rate_limit_and_filled.py`. I test sono offline, simulano 429 sequenziali, client diversi, redirect 429, errore 503, robots 429, contrasto JSON-LD/HTML ed esempio non chiuso. La CI va controllata; nessun run collector ordinario né test live completo eseguiti da questa PR. Nessun rollout, merge o cambio sorgente.

**Primo punto incompleto**: usare il client del progetto in un ambiente HTTPS con robots verificabili per un pilota limitato e riproducibile. Scegliere per primo il tenant Mingle di Marquardt soltanto dopo verifiche ufficiali di ownership/robots e campi visibili della stessa vacancy. Scartare senza login il flusso SLB se l'applicazione anonima è disabilitata. Verificare l'arrivo TikTok esclusivamente attraverso redirect pubblici e accessibili, senza eludere i blocchi. Se nessun percorso dà un form anonimo, sostituire le fonti anziché integrare link non verificati.
