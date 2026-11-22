# Inventario ATS e staging — 21 novembre 2026

Base `main` 841278f82fac0ad89d2c4e59c318fece09bb276e, PR #110 già integrata. Questo è un campione ricavato da dati già esistenti, non una mappatura territoriale esaustiva. Ricerca offline con `identify_channel` su `career_url`, `website_url`, `evidence_url`, URL associati delle fonti e URL/apply_url dei job con lo stesso source_id. L'associazione è un indizio e non prova automaticamente la titolarità. URL in campi diversi non esaminati e collegamenti non presenti nei dati non sono coperti. Esclusione per chiave ATS attiva tramite `_registered_keys`, non per semplice crawler universale. Sono state controllate le descrizioni delle PR aperte e le patch del registro fonti delle PR che lo modificano; non è stato verificato ogni file di tutte le PR: esclusione PR pertanto **non esaustiva**.

Totale rilevato: 68 coppie datore–tenant, 66 datori; 48 coppie con chiave ATS attiva e 20 non attive (19 datori). Queste ultime includono le tre già predisposte da #110. Per ATS: Greenhouse 9, Recruitee 6, Personio 3, Lever 2. Paesi obiettivo dichiarati (un datore può comparire in più paesi; non dimostrano la sede della vacancy): BE 2, CH 1, DE 12, ES 6, FR 9, GB 1, GR 1, IE 1, IT 4, NL 9, PL 1, PT 1, SE 1.

| Datore | Paesi obiettivo | ATS / tenant | Feed o esclusione | GET / byte letti / secondi |
|---|---|---|---|---|
| 2-CNNCT | NL | recruitee / `2cnnct.recruitee.com` | feed: 0 posizioni, 0 indizi HR | 2 / 141 / 1.082 |
| Back Market | DE, ES, FR | lever / `backmarket` | escluso: accesso non chiarito | 0 / 0 / 0 |
| Back Market | DE, ES, FR | greenhouse / `backmarket` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 0.162 |
| Berenschot | NL | recruitee / `berenschot.recruitee.com` | feed: 51 posizioni, 1 indizi HR | 10 / 5302833 / 8.994 |
| Climeworks | CH | recruitee / `climeworks.recruitee.com` | feed: 6 posizioni, 1 indizi HR | 5 / 663286 / 5.201 |
| Datamaran | NL | personio-xml / `datamaran.jobs.personio.com` | incompleto: robots disallows feed | 1 / 26 / 0.138 |
| Delivery Hero | DE, GR, SE | greenhouse / `deliveryhero` | incompleto: HTTP Error 404: Not Found | 2 / 131 / 1.181 |
| Doctolib | DE, FR, IT | greenhouse / `doctolib` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 1.009 |
| Fanatics Collectibles | GB | greenhouse / `fanaticscollectibles` | feed: 230 posizioni, 1 indizi HR | 3 / 3294960 / 2.856 |
| Focus Entertainment | FR | recruitee / `focusentertainment.recruitee.com` | feed: 6 posizioni, 1 indizi HR | 7 / 1256660 / 4.616 |
| Gemeente Achtkarspelen | NL | recruitee / `gemeenteachtkarspelen.recruitee.com` | incompleto: HTTP Error 301: Moved Permanently | 1 / 0 / 0.109 |
| Mollie | BE, DE, FR, NL, PT | greenhouse / `mollie` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 0.163 |
| Mynaric AG | DE | personio-xml / `mynaric.jobs.personio.de` | feed: 26 posizioni, 1 indizi HR | 5 / 357275 / 3.329 |
| Peripass | BE | recruitee / `peripass.recruitee.com` | feed: 16 posizioni, 1 indizi HR | 5 / 872433 / 3.384 |
| Personio | DE, ES, IE, NL | greenhouse / `personio` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 0.162 |
| Picnic | DE, FR, NL | greenhouse / `picnic` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 1.008 |
| Qonto | DE, ES, FR, IT | greenhouse / `qonto` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 0.628 |
| sennder | DE, ES, FR, IT, NL, PL | greenhouse / `sennder` | incompleto: HTTP Error 404: Not Found | 1 / 0 / 0.990 |
| TEAM LEWIS | DE, ES, FR, IT, NL | lever / `teamlewis` | escluso: accesso non chiarito | 0 / 0 / 0 |
| VTG GmbH Ingenieurbüro | DE | personio-xml / `vtg-gmbh-ingenieurbuero.jobs.personio.de` | incompleto: HTTP Error 404: Not Found | 2 / 23 / 1.103 |

## Vacancy osservate e prove

| Datore, paese | Stage HR identificato | Policy v2 | Requisiti espliciti rilevanti |
|---|---|---|---|
| Climeworks, CH | 1, 2831389 | sì, già predisposto in #110 | iscrizione o laurea/apprendistato recente; inglese fluente e buon tedesco; visto non indicato |
| Fanatics Collectibles, GB | 1, 4510457009 | sì, già predisposto in #110 | undergraduate in corso; lingua di lavoro e visto non indicati |
| Peripass, BE | 1, 2262981 | sì, già predisposto in #110 | master universitario in corso, olandese fluente e buona conoscenza inglese; visto non indicato |
| Berenschot, NL | 1, 2818815 | sì, usando alias circoscritto `Berenschot Groep B.V.` | master universitario in corso; lingua di lavoro e visto non indicati |
| Focus Entertainment / PulluP, FR | 1, 2791407 | no: datore diverso nel markup, relazione non dimostrata | master HR, inglese fluente desiderato; visto non indicato |
| Mynaric, DE | 1, 2864862 | no: submit inizialmente disabilitato | iscrizione a università tedesca, tedesco e inglese fluenti; visto non indicato |

Le prime tre sono già nel registro come fonte disabilitata con hold in #110: **non sono nuove fonti di questa ricerca**. Berenschot è già nel catalogo sotto `auto-berenschot`, ID `68bbbe8c4218385f7c9d`, stessa URL e verifica diretta v2 al 21 novembre: **non è un'aggiunta**. Il primo controllo ha respinto il nome societario; un controllo successivo ha usato l'alias esatto ricavato da `hiringOrganization` della vacancy, senza modificarlo nel registro. Il crawler attivo ammette già lo stesso host e dichiara la stessa vacancy; attivare un secondo collector rischierebbe doppioni. Focus va riconciliata con PulluP prima di attribuire la posizione. I feed senza risultati classificati, gli HTTP 404, il 301 e robots negato non dimostrano assenza di stage.

Nessuna nuova fonte è stata preparata: i tre soli nuovi indizi non danno un incremento distinto verificato. Inoltre l'hold aziendale attuale rifiuta qualsiasi fonte attiva: imporlo a un datore con crawler già attivo farebbe fallire il provisioning. Non è stato allentato il gate o disattivato il crawler. Si propone una revisione separata del modello di hold e della deduplicazione prima di configurare un eventuale secondo canale, se emergerà un'opportunità aggiuntiva.

## Accesso, costi e limiti

Scan GET-only con robots prima di ciascun host, attesa almeno un secondo per host, redirect non seguiti e una richiesta feed per tenant. Lever escluso: robots di `api.lever.co` e `jobs.lever.co` non leggibile dal lettore web; i [termini Lever](https://www.lever.co/legal/terms-of-service) riguardano principalmente i clienti e non attestano un diritto generale di riuso. Nessun feed Lever interrogato. Per Recruitee, Personio e Greenhouse i riferimenti e la review preliminare del provider sono nel [rapporto #110](sette-fonti-ats-2026-11-21.md); non valgono da licenza generale e le fonti di questa ricerca non sono state integrate.

Scansione e controlli: **50 GET / almeno 11.747.768 byte / 36,115 secondi cumulati**, inclusi robots e ripetizioni, non tempo a muro né costo monetario. I corpi degli errori HTTP non sono letti e non sono inclusi nei byte; le consultazioni separate del lettore web per termini e robots non hanno telemetria HTTP comparabile e non sono comprese nel totale strumentato. Due richieste successive di pagina per chiarire le denominazioni e tre per la ripetizione Berenschot sono incluse. Nessun POST, login, bypass o candidatura. 18 feed tentati o bloccati da robots: 7 letti (6 con un indizio HR ciascuno e uno vuoto), altri 11 incompleti; due tenant Lever esclusi. Budget 600 non raggiunto; la scansione si è fermata alla fine di questa coda preliminare, non perché il budget fosse esaurito. I file tecnici dei feed rimangono in `.staging/` ignorato da git.

Potenziale delle tre fonti già predisposte da #110, se riattivate dopo una nuova verifica e decisione separata: CH +1, BE +1, GB +1; ciclo precedente #110 **12 GET / 4.830.640 byte / 7,391 secondi-fonte**, non una previsione garantita né il costo di questa scansione. Incremento distinto attribuibile al nuovo lotto: **0**.

## Personio

Sungrow, Entrix e ora Mynaric mostrano campi ma pulsante disabilitato. `disabled_submit_applicant_form` si applica a queste forme e il test `test_an_enabled_form_remains_eligible_without_policy_relaxation` dimostra offline che un modulo Personio con submit abilitato non è bloccato incondizionatamente. Il comportamento dinamico dopo compilazione non è stato dimostrato; non si può concludere se il problema riguardi ogni tenant reale né promuovere un modulo disabilitato sulla sola fixture. Nessuna correzione proposta senza prova di un falso negativo e test che mantengano policy v2.

## Verifiche locali

Copia isolata dell'albero `841278f`: **531 test Python 3.12.14** e **35 test Node** superati; 103 esempi classificazione, zero falsi positivi/negativi nel set; coverage, build e `collector.pipeline --validate` riusciti. Provisioning su copia confrontato in memoria: baseline invariata, secondo passaggio identico, 1.923 fonti abilitate. Un primo tentativo con Python di sistema 3.9.6 ha fallito 3 test e prodotto 4 errori; non è la versione CI e non viene dichiarato riuscito.

Nessun file catalogo modificato: baseline 907 ID distinti → 907, **0 ID persi** nell'albero di questa PR. È un controllo di conservazione del catalogo invariato, non una finalizzazione simulata delle nuove fonti. 407 stage correnti e 37 candidature dirette secondo l'audit offline a data del test, senza variazione dovuta alla PR.
