# Integrazione operativa dei canali — 5 novembre 2026

La mappatura dei nomi non aveva ancora prodotto offerte dalle nuove aziende: il catalogo iniziale conteneva 16 stage HR e il monitoraggio era configurato per 13 datori. Questa sessione completa una prima verifica sistematica dei canali già dichiarati.

## Risultati effettivamente eseguiti

- 346 pagine carriera controllate; 339 lette correttamente e 7 rimaste in revisione per problemi di accesso o risposta.
- 27 nuovi datori collegati e raccolti con esecuzioni riuscite; totale 40 datori con monitoraggio configurato.
- Due adattatori aggiunti per i feed pubblici Personio XML e Recruitee, più un adattatore per elenchi ufficiali di collegamenti e pagine curate con `JobPosting`.
- Catalogo passato da 16 a 22 opportunità aperte: 20 stage e 2 posizioni per studenti lavoratori, etichettate distintamente.

Le sei aggiunte sono:

| Datore nel registro | Titolo ufficiale | Tipo | Paese |
|---|---|---|---|
| Focus Entertainment / PULLUP Entertainment | PULLUP ENTERTAINMENT - STAGIAIRE DEVELOPPEMENT RH (H/F/NB) | Stage | Francia |
| TNG Technology Consulting | Praktikum im Bereich People & Events (m/w/d) | Stage | Germania |
| BAS Group | Meewerkstage HR | Stage | Paesi Bassi |
| Tyche Bank | HR Intern | Stage | Italia |
| QPLIX | Werkstudent (m/w/d) \| People & Organizational Culture (POC) | Studente lavoratore | Germania |
| TNG Technology Consulting | Werkstudierende Recruiting (m/w/d) | Studente lavoratore | Germania |

I collegamenti originali, le verifiche e i requisiti espliciti sono nel catalogo. La prima scoperta non viene presentata come data di pubblicazione: per esempio un'offerta ancora nel feed ufficiale può essere stata creata anni prima.

L’ultima raccolta complessiva è riuscita su tutti i 40 canali. Dopo il primo lotto sono state inoltre controllate 92 pagine carriera dei nuovi candidati italiani universitari e 48 delle imprese della fonte territoriale.

## Perimetro e verifiche

I feed Personio e Recruitee inventariano le posizioni pubbliche restituite; il titolo effettivo e la localizzazione decidono l'inclusione. Le pagine e le API sono controllate rispettando robots.txt. Le nuove sitemap vengono dichiarate dai siti carriera. Il canale BAS controlla una pagina ufficiale scoperta manualmente; non inventaria automaticamente tutte le offerte BAS: il suo elenco principale è dinamico e quello HR precedente conteneva collegamenti non più validi.

Il controllo delle pagine ha individuato anche link candidati per ALL IN GROUP e AXS Logistiek, che non espongono il formato JobPosting supportato. Questi annunci non sono stati inseriti nel catalogo come se fossero già verificati dal raccoglitore. Servono adattatori specifici e controllo del perimetro.

Il feed FUTRUE è bloccato da robots, quello Markteffect risponde 404. Altri canali restano da integrare. I fallimenti non vengono aggirati e non cancellano offerte precedenti. Avere una fonte configurata non dimostra copertura di ogni paese in cui opera il gruppo.

I nuovi connettori hanno permesso anche di correggere due casi reali: il titolo olandese «Meewerkstage HR», e la differenza fra «Werkstudierende» e stage. «People & Events» passa il filtro HR solo quando la descrizione contiene attività HR esplicite; l'organizzazione di eventi da sola non basta.

## Tracciabilità

- `docs/career-channel-scan.json`: controlli delle 346 pagine.
- `docs/feed-access-review.json`: prima revisione dei feed.
- `docs/additional-channel-review.json`: seconda revisione.
- `data/sources.json`: canali abilitati, host approvati e limiti.
- `data/coverage.json`: risultati delle raccolte, anche dei canali senza stage HR correnti.
- `scripts/inspect_career_channels.py`: verifica ripetibile delle pagine ancora senza fonti configurate, con opzione `--country`.

Documentazione usata: [Personio XML](https://developer.personio.de/docs/retrieving-open-job-positions), [collegamenti ai job Personio](https://developer.personio.de/docs/integration-of-open-positions), [Recruitee offers](https://docs.recruitee.com/reference/offers), [autenticazione Recruitee](https://docs.recruitee.com/reference/authentication-1). Recruitee annuncia l'obbligo di token Careers API dal 10 febbraio 2027: i canali dovranno essere rivalutati entro tale data, privilegiando un feed pubblico ammesso se disponibile. Nessun token è stato usato in queste esecuzioni.
