# CORPORATE-RMK — 24 novembre 2026

Dieci fonti disabilitate e in hold nella PR #139. Il lotto copre i semi già verificati e un primo campione DAX/MDAX. Il censimento dei sette indici rimane aperto.

## Rettifica su BMW, Festo e Provinzial

Nessuna clausola di divieto esplicito è stata individuata negli avvisi pubblici applicabili rivisti. L’esclusione precedente dipendeva dalla regola sul formato dei dettagli, che all’epoca ammetteva JSON-LD. I tre robots identici consentono le schede `/job/` e vietano `/applybutton/`, `/talentcommunity/`, `/mobile/talentcommunity/`, `/emailsubscribe/`, `/email/image/`, `/services/`, `/preapply/`, `/error`, `/unsubscribe/` e `/reset/`. Tutti e tre i domini sono ammessi nel lotto. [BMW](https://www.bmwgroup.jobs/de/de/general/impressum.html) · [Festo](https://www.festo.com/imprint) · [Provinzial](https://www.provinzial.de/suedwest/unternehmen/impressum.html)

## Inventario e dettagli

I GET riportati sono le letture riprodotte nel replay, inclusi robots, indice, candidati e redirect osservati. I controlli legali esterni e il preflight degli host esclusi sono fuori da questi conteggi. Il triage identifica titoli candidati, mentre paese e idoneità richiedono prova sul dettaglio o nei dati strutturati pubblici della stessa vacancy.

| Host | Accesso | Annunci/ID | Candidati | Stage HR per paese e classe | GET |
|---|---|---:|---:|---|---:|
| jobs.bmwgroup.com | Ammesso | 769 | 25 | DE 20 non indicata. Quattro formati non supportati e un paese non dimostrato tra i candidati | 52 |
| jobs.festo.com | Ammesso | 131 | 4 | DE 1 confermata, 3 non indicata | 6 |
| karriere.provinzial.com | Ammesso | 152 ID su 157 URL | 4 | DE 1 confermata, 3 non indicata | 6 |
| jobs.schaeffler.com | Ammesso. Campione [MDAX](https://www.schaeffler.com/en/media/press-releases/press-releases-detail.jsp?id=88176003), [termini](https://jobs.schaeffler.com/content/Nutzungsbedingungen/?locale=de_DE) | 660 | 9 | DE 2 confermata, 6 non indicata. Un paese non dimostrato tra i candidati | 11 |
| jobs.rwe.com | Ammesso. Campione [DAX](https://www.boerse-hannover.de/indizes/DE0008469008/dax-performance-index/), [avviso](https://www.rwe.com/en/disclaimer/) | 189 | 0 | Nessuno dagli slug | 2 |
| careers.kpmg.it | Ammesso. [Sito istituzionale](https://kpmg.com/it/it/careers.html) | 223 | 1 | IT 1 esclusa per regola locale | 3 |
| careers.crif.com | Ammesso. Il link Terms of use del sito porta all’informativa A.N.C.I.C., riferita ai dati commerciali. [Informativa](https://www.crif.com/privacy-policy/) | 37 | 1 | IT 1 esclusa per stage extracurriculare | 3 |
| recrutement.francetelevisions.fr | Ammesso. [Condizioni](https://recrutement.francetelevisions.fr/content/conditions-generales-utilisation/?locale=fr_FR) | 11 | 1 | FR 1 non indicata | 3 |
| jobs.danishcrown.com | Ammesso. [Portale istituzionale](https://www.danishcrown.com/global/job-and-career/vacancies/) | 203 | 1 | PL 1 non indicata | 3 |
| jobs.jti.com | Ammesso per l’inventario pubblico. [Avviso](https://www.jti.com/en/privacy-and-legal) | 374 | 0 | Nessuno dagli slug | 2 |
| careers.essilorluxottica.com | Auto-review ha bloccato la richiesta alla sitemap per le restrizioni sull’estrazione. Termini della rotta carriera da chiarire | — | — | Non misurato | 2 preflight |
| jobsearch.alstom.com | Escluso per il divieto di download nel perimetro dei siti Alstom. [Avviso](https://www.alstom.com/fr/notice-legale) | — | — | Non misurato | 1 preflight |
| careers.melia.com | Il footer rimanda all’avviso che limita la copia all’uso personale. [Avviso](https://www.melia.com/es/aviso-legal) | — | — | Non misurato | 2 preflight |
| jobs.telefonica.com | Il footer rimanda all’avviso che limita la riproduzione a scopi personali o privati. [Avviso](https://www.telefonica.com/es/aviso-legal/) | — | — | Non misurato | 2 preflight |
| jobs.engie.com | Il footer rimanda all’avviso che vieta espressamente l’estrazione di elementi delle basi dati. [Avviso](https://www.engie.com/en/legal-information/) | — | — | Non misurato | 2 preflight |
| careers.mediamarktsaturn.com | Il link legale del footer risponde 404. Condizioni del percorso da verificare | — | — | Non misurato | 2 preflight |
| corningjobs.corning.com | La rotta sitemap ha restituito HTML. Inventario XML non dimostrato. [Termini carriere](https://www.corning.com/worldwide/en/careers/terms.html) | — | — | Non misurato | 2 preflight |

SAP, Bayer e L’Oréal non hanno mostrato la firma robots richiesta sugli host provati. Le verifiche su Eni, Air Liquide, Orlen, Santander, Pirelli, Prysmian ed Euronext si sono fermate prima dell’inventario per errori TLS/DNS, redirect o robots assente. Questi controlli non escludono altri tenant ufficiali dei rispettivi gruppi. Restano da completare le verifiche per singolo emittente di DAX 40, MDAX, FTSE MIB, IBEX 35, CAC 40, AEX e WIG20.

## Simulazione

Sulla baseline di 944 ID, il replay isolato di CORPORATE-RMK porta il catalogo a 982 ID, con zero persi. L’identità nel [ledger #138](https://github.com/nightlydeveloper8/eu-hr-internships/blob/5646a77241976dc4a0cbdda54f261234d527a477/docs/recall-fonti-ad-alta-densita-2026-11.csv) usa URL canonico, ID RMK sullo stesso host o ID di catalogo documentato. I sette stage Randstad PL già simulati appartengono a un lotto distinto.

| Paese | Domini associati al paese | Stage aperti prima → dopo | Recall aperto prima → dopo |
|---|---:|---:|---:|
| DE | 5 | 36 → 72 | 0/30 → 4/30 |
| DK | 1 | 0 → 0 | nessuna riga |
| FR | 1 | 44 → 45 | 0/30 → 1/30 |
| IT | 2 | 27 → 27 | 0/70 → 0/70 |
| PL | 2 | 0 → 1 | 0/20 → 1/20 |

Il canale Danish Crown è contato sia per DK sia per PL. Le 38 offerte aggiunte sono tutte *current listing*. La verifica richiede presenza nella sitemap, scheda live identificata con contenuto strutturato, data pubblicata o scadenza utilizzabile e link di candidatura visibile per il medesimo ID. Quel link è usato esclusivamente come segnale sulla scheda pubblica. Zero richieste ai percorsi di candidatura e zero candidature dirette verificate.

Tetto aggiuntivo per shard nella matrice da 16. Shard 8, 540 s e 195 richieste. Shard 0, 4, 7, 9, 13, 14 e 15, 180 s e 65 richieste ciascuno. Altri shard, zero. Preflight di replay complessivo di 91 GET, cumulati per tutte le fonti ammesse. Durata end-to-end da dimostrare.
