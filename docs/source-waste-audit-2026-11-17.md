# People Placement — HTTP improduttivi, SmartRecruiters FR/BE e Ampelmann (17 novembre 2026)

## Ambito e prove
Audit **offline** del report versionato `data/coverage.json` su `main` commit `ab51981fff5c2bb57a775490eab3464f43b4825a`, eseguito su GitHub Actions [#44169896860](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44169896860), job `audit`, **success**. Script `python -m scripts.audit_source_waste --date 2026-11-17`, tre test regressione superati. La prima esecuzione temporanea [#44169729215](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44169729215) aveva fallito: la creazione di nuovi bucket ereditava per errore i totali già cumulati; difetto riparato e test confermato nella seconda run. Il file workflow temporaneo è previsto per la rimozione prima della consegna finale della PR. **Zero nuove HTTP verso datori, zero rendering, zero POST, zero modifiche a registri/cadenza/produzione.**

Sono stati osservati **1.894 report-fonte freschi** del 17/11, contro 1.896 aziende tentate in Issue #1: il filtro esclude report non datati quel giorno o senza conteggio HTTP intero. Totale: **42.445 HTTP, 4.992.916.331 byte, 3.652 rendering, 53.788,77 secondi-fonte cumulati**. Le **1.834 fonti senza match HR osservato** hanno consumato **40.287 HTTP (94,92%), 4.556.034.629 byte, 3.541 rendering, 51.253,24 secondi-fonte**. Sessanta fonti riportavano almeno un match HR; match significa candidato scoperto, **non** candidatura verificata policy v2. Il tempo sommato per fonte non è durata wall-clock o costo fatturato.

## Cinque gruppi tecnici disgiunti, ordinati per richieste

| Gruppo | Fonti | HTTP | Byte | Rendering | Secondi-fonte |
|---|---:|---:|---:|---:|---:|
| Universal crawl incompleto con URL pendenti | 232 | **14.630** | 2.098.964.971 | 1.101 | 19.074,01 |
| Errori di raccolta / restrizioni di accesso | 481 | **10.966** | 936.462.635 | 1.001 | 12.313,80 |
| Altri crawl che hanno renderizzato senza match HR | 554 | **8.834** | 863.476.094 | 1.439 | 11.733,59 |
| Universal incompleto senza frontier pendente | 518 | **5.609** | 621.982.934 | 0 | 7.947,57 |
| Adapter specifici incompleti | 7 | **41** | 2.876.553 | 0 | 40,95 |
| Controllo: raccolta completa senza HR, non difetto tecnico | 42 | 207 | 32.271.442 | 0 | 143,32 |

Per il primo gruppo sono documentati **100.762 URL pendenti**; nel gruppo errori altri **45.360**. Sono grandezze di coda per fonte, non necessariamente URL univoci globalmente. La classificazione assegna a ogni rapporto **un solo gruppo** in ordine deterministico: restrizione/errore, universal con frontier pendente, rendering, universal incompleto, adapter incompleto, controllo completo. Di conseguenza i 1.101 e 1.001 rendering nei primi due gruppi **non** ricompaiono nel terzo; i 3.541 rendering senza match HR sono il totale reale trasversale. La categoria errori include timeout e fallimenti, non soltanto robots; la categoria rendering non dimostra che la pagina renderizzata fosse evitabile.

**Priorità suggerita dai dati:** scoprire perché il frontier dei universal crawler resta così ampio e contiene richieste ripetitive/non-vacancy, usando campionamento riproducibile, filtri sicuri e confronti before/after. Esempi di massimo costo nel ciclo: `auto-asml`, `auto-baco-s-r-l`, `auto-camplus` (110 HTTP ciascuno); `auto-vinted` (108 HTTP, 950 URL pending, 18 rendering). Sono indizi per diagnosi strutturali, **non** un mandato a limitare arbitrariamente profondità o a chiudere fonti. Il secondo tema è qualificare e limitare con gate già autorizzati fallimenti ripetuti; non riprovare API proibite. Nessun risparmio è stato ancora realizzato con questo audit.

## SmartRecruiters: 12 non verificati nel catalogo, non 12 stage pronti

Sul medesimo `main` 17/11 08:07 UTC, **12 record unverified** HR internship FR (11) / BE (1) con URL SmartRecruiters: **8** riportano `Current page does not identify the same vacancy`; **3** `No available vacancy-specific application entry established`; **1** `Requires vacancy/application evidence under policy v2`. I 12 record appartengono a ALTAREA, Interlogement 93, Salomon (3), Sia (2), SMCP, JDE Peet's (2), Lesaffre (2). Salomon e Lesaffre hanno rispettivamente record con titolo molto simile ma ID diversi: **non deduplicare per solo titolo**. Alcuni `last_seen_at` risalgono al 6–7 novembre, quindi mancano prove live attuali.

La [PR #60](https://github.com/nightlydeveloper8/eu-hr-internships/pull/60) ha testato in modo circoscritto Salomon `744000161490861` e Sia `744000159655534`: due pagine ufficiali HTTP 200 con titolo coerente, **3 GET / 243.545 byte**, ma **nessun form rigoroso in HTML**, zero nuove candidature policy v2. Non inferire una conversione degli altri dieci. La causa strutturale da cercare è duplice: lettura robusta dell'identità del posting dalla **pagina ufficiale accessibile**, e collegamento da CTA di candidatura effettivamente pubblicata a pagina/form della stessa vacancy, con stato disponibile e submit verificabile. L'API `api.smartrecruiters.com` resta esclusa quando robots la vieta. Un renderer bounded è un esperimento possibile solo se autorizzato e permesso; JS/redirect senza form verificabile restano `unverified`. Non falsificare `application_url` o comporre route per tentativi.

## Ampelmann: pronto per provisioning gated, non produzione

La [PR #60](https://github.com/nightlydeveloper8/eu-hr-internships/pull/60) documenta due cicli `process_source() → finalize()` sul **17/11 nello stesso giorno**, con XML Recruitee pubblico, robots e host confinati, ID ufficiale `2822573`, stage HR `Internship People & Organisation` a Delft, modulo specifico same-ID strict. **9 GET / 1.887.074 byte / 12,841 secondi-fonte**, **1 stage nuovo verificato solo nello staging**, stesso ID in entrambi i cicli, nessuna chiusura per assenza. [Run #44147104809](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44147104809) superata e CI HEAD `61c5819` verde. Prima di produzione: prova a data diversa; review; provisioning esplicito di azienda + source **disabled** con nessuna raccolta universal accidentale; autorizzazione distinta a merge/attivazione; poi riscontro nel ciclo ordinario, commit dati e Cloudflare. **Non conteggiare il +1 su main**.

## Limiti e criteri per il prossimo intervento

Il rapporto attribuisce costi a *gruppi osservabili*, non a singole cause dimostrate, né calcola richieste evitabili o offerte perse in un controfattuale. Un risultato `partial` non è prova di inventario vuoto. Il prossimo cambiamento dovrebbe produrre un confronto su almeno due cicli di **HTTP, byte, rendering, pending URLs, ID preesistenti, match HR e stage verified**. Gli interventi che diminuiscono le richieste ma impediscono il recupero di stage brevi devono essere respinti. Nessun cambio di budget, cadenza o allowlist è autorizzato da questo audit.

Stati da non confondere: questo branch contiene diagnostica; PR #60 contiene nuovo adapter ancora **non mergiato**; Ampelmann è verificato **solo in staging**; SmartRecruiters ha **zero nuovi stage verificati** nei preflight; la raccolta ordinaria pubblicata resta quella su `main`.
