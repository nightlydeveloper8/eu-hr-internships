# Fonti ad alta densità — 23 novembre 2026

## Recall sul catalogo pubblicato

Il CSV allegato contiene 225 URL distinti in sette paesi. La [PR #137](https://github.com/nightlydeveloper8/eu-hr-internships/pull/137) documenta un campione precedente di 16 schede, con 15 Bosch e una Manpower. Il [registro riga per riga](recall-fonti-ad-alta-densita-2026-11.csv) usa l'allegato da 225 righe (SHA-256 `5fa0a504430058432f327e47eb4774c99753e22cf96ab91239ebcb043c858850`) e il catalogo pubblicato il 23 novembre alle 17:45 UTC. [Commit dei dati](https://github.com/nightlydeveloper8/eu-hr-internships/commit/8f1550403acd3225bd5f13785934fafecf1568e5) · [Base del ramo](https://github.com/nightlydeveloper8/eu-hr-internships/commit/03d22a5a883a0a311539df2bfd809bc44ca47e4d)

I match confermati usano URL della scheda o della candidatura, oppure ID del posting con il relativo spazio di identificazione per Danone, Amazon e BMW. Il titolo, il datore e la città aiutano a esaminare gli omonimi. Le somiglianze interpiattaforma senza un collegamento dimostrabile restano assenti dal conteggio dei match confermati e i candidati sono nel registro. L'assenza si riferisce alla stessa vacancy nello snapshot e la causa operativa rimane **non dimostrato** se l'unica prova è l'assenza dell'host o della configurazione. L'eventuale corrispondenza tra copie con URL e ID diversi è **non dimostrato**. Lead indica record non chiuso senza verifica attuale, comprese piste storiche che l'interfaccia può nascondere. La freschezza è calcolata all'ora del catalogo con la soglia di 48 ore.

| Paese | Righe | Aperto | Lead | Chiuso | Assente | Recall aperto confermato |
|---|---:|---:|---:|---:|---:|---:|
| DE | 30 | 0 | 4 | 0 | 26 | 0/30 |
| ES | 40 | 0 | 7 | 0 | 33 | 0/40 |
| FR | 30 | 0 | 1 | 0 | 29 | 0/30 |
| IE | 5 | 0 | 0 | 0 | 5 | 0/5 |
| IT | 70 | 0 | 10 | 0 | 60 | 0/70 |
| NL | 30 | 1 | 1 | 0 | 28 | 1/30 |
| PL | 20 | 0 | 1 | 0 | 19 | 0/20 |
| **Totale** | **225** | **1** | **24** | **0** | **200** | **0,44%** |

L'aperto confermato è Van Wijnen a Heerenveen, con candidatura diretta. Le quattro corrispondenze BMW e le sette Amazon ES sono lead. Il segmento `24107` nei link IKEA è condiviso da offerte diverse. Zwolle e Groningen hanno ID finali diversi. Le offerte Bosch con titoli simili su EURES hanno sedi o identificativi diversi. La corrispondenza ABB via università, quella Start People via aggregatore e i due ID Planon restano piste da dimostrare. Il riferimento del maintainer di 19 aperti era approssimato. Il conteggio qui include solo identità dimostrate.

## Accesso per dominio

Le misure sono GET pubblici in staging con user agent People Placement. I redirect indicano un host da verificare separatamente. Il preflight robots da solo lascia incerti l'accesso continuativo, i termini e il formato del post. La colonna stage si riferisce al conteggio completo degli stage HR per studenti del 23 novembre.

| Lotto | Dominio | HTTP robots | Byte | Secondi | Indicazioni dal robots | Stage HR oggi |
|---|---|---:|---:|---:|---|---|
| P1 | www.randstad.it | 200 | 986 | 0.114 | sitemap dichiarata | non dimostrato |
| P1 | www.manpower.it | 200 | 131 | 0.060 | sitemap dichiarata | non dimostrato |
| P1 | www.synergie-italia.it | 200 | 154 | 0.277 | sitemap dichiarata | non dimostrato |
| P1 | lavoro.humangest.it | 200 | 3,252 | 0.285 | — | non dimostrato |
| P1 | www.maw.it | 200 | 684 | 0.166 | sitemap dichiarata | non dimostrato |
| P1 | www.openjobmetis.it | 200 | 212 | 0.128 | — | non dimostrato |
| P1 | investitori.openjobmetis.it | 200 | 212 | 0.128 | — | non dimostrato |
| P1 | www.gigroup.it | 200 | 21,762 | 0.140 | sitemap dichiarata | non dimostrato |
| P1 | careers.gigroupholding.it | 200 | 3,276 | 0.210 | — | non dimostrato |
| P1 | www.adecco.com | 200 | 1,202 | 0.079 | sitemap dichiarata | non dimostrato |
| P1 | www.umana.it | 200 | 428 | 0.172 | sitemap dichiarata | non dimostrato |
| P1 | career.etjca.it | 200 | 3,204 | 0.283 | — | non dimostrato |
| P1 | www.orientajob.com | 200 | 3,232 | 0.300 | — | non dimostrato |
| P1 | www.randstad.es | 200 | 1,131 | 0.172 | sitemap dichiarata | non dimostrato |
| P1 | www.randstad.nl | 200 | 771 | 0.162 | sitemap dichiarata | non dimostrato |
| P1 | www.randstad.fr | 200 | 2,872 | 0.185 | sitemap dichiarata | non dimostrato |
| P1 | www.randstad.de | 200 | 1,762 | 0.137 | sitemap dichiarata | non dimostrato |
| P1 | www.randstad.pl | 200 | 772 | 0.135 | sitemap dichiarata | non dimostrato |
| P1 | www.randstad.ie | 301 | 27 | 0.167 | https://www.randstad.co.uk/ireland/ | non dimostrato |
| P1 | www.adecco.es | 301 | 162 | 0.261 | https://www.adecco.com/es-es | non dimostrato |
| P1 | www.adecco.nl | 404 | 103 | 0.359 | — | non dimostrato |
| P1 | www.adecco.fr | 301 | 162 | 0.265 | https://www.adecco.com/fr-fr | non dimostrato |
| P1 | www.adecco.de | 301 | 162 | 0.292 | https://www.adecco.com/de-de/robots.txt | non dimostrato |
| P1 | www.adecco.pl | 404 | 103 | 0.360 | — | non dimostrato |
| P1 | www.adecco.ie | 404 | 103 | 0.289 | — | non dimostrato |
| P1 | www.manpower.es | 200 | 2,286 | 0.151 | sitemap dichiarata | non dimostrato |
| P1 | www.manpower.nl | 200 | 1,655 | 0.182 | sitemap dichiarata | non dimostrato |
| P1 | www.manpower.fr | 200 | 1,661 | 0.101 | — | non dimostrato |
| P1 | www.manpower.de | 200 | 93 | 0.182 | sitemap dichiarata | non dimostrato |
| P1 | www.manpower.pl | 200 | 144 | 0.119 | sitemap dichiarata | non dimostrato |
| P1 | www.manpower.ie | 200 | 356 | 0.378 | sitemap dichiarata | non dimostrato |
| P1 | www.gigroup.es | 301 | 57 | 0.185 | https://es.gigroup.com/ | non dimostrato |
| P1 | www.gigroup.nl | 301 | 57 | 0.202 | https://nl.gigroup.com/ | non dimostrato |
| P1 | www.gigroup.fr | 301 | 57 | 0.284 | https://fr.gigroup.com/ | non dimostrato |
| P1 | www.gigroup.de | 301 | 57 | 0.261 | https://de.gigroup.com/ | non dimostrato |
| P1 | www.gigroup.pl | errore | 0 | 0.162 | — | non dimostrato |
| P1 | www.gigroup.ie | 301 | 0 | 0.143 | https://ie.gigroup.com/ | non dimostrato |
| P1 | www.synergie.es | 200 | 344 | 0.311 | sitemap dichiarata | non dimostrato |
| P1 | www.synergie.nl | 200 | 938 | 0.206 | sitemap dichiarata | non dimostrato |
| P1 | www.synergie.fr | 200 | 209 | 0.733 | sitemap dichiarata | non dimostrato |
| P1 | www.synergie.de | 301 | 0 | 0.552 | https://synergie.de/robots.txt | non dimostrato |
| P1 | www.synergie.pl | 404 | 89,902 | 0.604 | — | non dimostrato |
| P1 | www.synergie.ie | errore | 0 | 0.284 | — | non dimostrato |
| P1 | empleo-flexiplan.eulen.com | 200 | 79 | 0.310 | sitemap dichiarata | non dimostrato |
| P1 | empleo.gruporas.es | 200 | 262 | 1.132 | sitemap dichiarata | non dimostrato |
| P1 | jobs.grupo-crit.com | 200 | 130 | 0.320 | — | non dimostrato |
| P1 | www.intalentia.com | 301 | 0 | 2.135 | https://intalentia.com/robots.txt | non dimostrato |
| P1 | www.youngcapital.nl | 200 | 1,402 | 0.154 | sitemap dichiarata | non dimostrato |
| P1 | werkenbij.olympia.nl | 200 | 89 | 0.179 | sitemap dichiarata | non dimostrato |
| P1 | www.startpeople.nl | 200 | 71 | 0.202 | sitemap dichiarata | non dimostrato |
| P1 | www.tempo-team.nl | 200 | 1,001 | 0.161 | sitemap dichiarata | non dimostrato |
| P2 | bmwgroup.jobs | 302 | 0 | 0.547 | https://www.bmwgroup.jobs/robots.txt | non dimostrato |
| P2 | www.bmwgroup.jobs | 200 | 46 | 0.297 | sitemap dichiarata | non dimostrato |
| P2 | jobs.bmwgroup.com | 200 | 252 | 0.186 | — | non dimostrato |
| P2 | careers.kpmg.it | 200 | 252 | 0.234 | — | non dimostrato |
| P2 | careers.crif.com | 200 | 252 | 0.257 | — | non dimostrato |
| P2 | careers.essilorluxottica.com | 200 | 252 | 0.261 | — | non dimostrato |
| P2 | jobsearch.alstom.com | 200 | 252 | 0.244 | — | non dimostrato |
| P2 | careers.melia.com | 200 | 252 | 0.255 | — | non dimostrato |
| P2 | jobs.telefonica.com | 200 | 252 | 0.357 | — | non dimostrato |
| P2 | jobs.festo.com | 200 | 252 | 0.229 | — | non dimostrato |
| P2 | karriere.provinzial.com | 200 | 252 | 0.282 | — | non dimostrato |
| P2 | corningjobs.corning.com | 200 | 252 | 0.644 | — | non dimostrato |
| P2 | jobs.jti.com | 200 | 252 | 0.263 | — | non dimostrato |
| P2 | jobs.engie.com | 200 | 252 | 0.285 | — | non dimostrato |
| Riesame | api.smartrecruiters.com | 200 | 72 | 0.064 | — | non dimostrato |
| Riesame | jobs.smartrecruiters.com | 404 | 55,539 | 0.087 | — | non dimostrato |
| Riesame | www.amazon.jobs | 200 | 324 | 2.155 | — | non dimostrato |
| P3 | index.commoncrawl.org | errore | 0 | 0.370 | — | non dimostrato |

### P1 · Agenzie

**Randstad Italia.** Sitemap principale XML valida, con due sotto-inventari di dettaglio. I due XML sono completi e danno 5.000 e 4.997 URL di dettaglio. Il prefiltraggio sui titoli desunti dagli URL segnala 31 candidati nei due inventari e può perdere titoli opachi o generici. Un dettaglio Randstad a Udine espone `JobPosting`, il codice `CX590384` e una scadenza futura. L'iscrizione o la natura curriculare di quella scheda è **non dimostrato**. I termini letti disciplinano l'account candidato e non vietano espressamente il GET ai percorsi pubblici provati. Tra robot, sitemap, termini e dettaglio d'evidenza, il passaggio principale ha usato 6 GET / 2.730.955 byte / 1,652 s HTTP. Il primo preflight preliminare è separato. [Robots](https://www.randstad.it/robots.txt) · [Sitemap](https://www.randstad.it/sitemap.xml) · [Termini](https://www.randstad.it/terms-conditions-page/) · [Dettaglio](https://www.randstad.it/offerte-lavoro/stage-hr-recruiter_udine_1e26ce54-0bd0-4b8a-902d-5ad956b007b2/)

Il nuovo registro usa l'adattatore esistente `employer-sitemap` con host esatto, due sitemap, `enabled: false` e hold sul nuovo canale. Randstad Italia ha già un collector automatico pertanto il blocco sul singolo canale preserva il collegamento esistente. Anche un'abilitazione accidentale della nuova fonte viene respinta dall'adattatore prima di qualsiasi richiesta. La configurazione è un canale di discovery con prefiltraggio, che lascia il conteggio esaustivo **non dimostrato**. L'equivalenza di piattaforma tra paesi richiede un confronto dei percorsi e dello schema effettivi paese per paese.

**MAW** esclusa per il divieto esplicito già documentato nel benchmark. **Manpower Italia** ha sitemap nello stesso host e una verifica precedente di dettaglio; §§10–12 limitano riuso e collegamenti e l'ammissione all'integrazione resta **non dimostrato**. **Altri domini e paesi** hanno le prove di preflight nella tabella. Termini applicabili e almeno un formato e percorso verificati per ciascun host restano **non dimostrato**. I domini nazionali con redirect restano piste. Per un annuncio con cliente esplicitamente anonimo il datore va attribuito all'agenzia e la dicitura deve essere «cliente non indicato». La prova in questo lotto è una scheda con Randstad in `hiringOrganization`. Il supporto alla dicitura nei record normalizzati resta da implementare con un esempio esplicito. [Termini MAW](https://www.maw.it/termini-e-condizioni) · [Termini Manpower](https://www.manpower.it/it/terms-of-use)

### P2 · Grandi aziende

Su `www.bmwgroup.jobs` il robots annuncia una sitemap, ma il corpo ricevuto termina con un XML incompleto (HTTP 200, 114.688 byte, 3,582 s). Il dettaglio 197182 è stato letto in 1 GET / 100.000 byte / 0,630 s senza JobPosting JSON-LD rilevato. Il canale RMK `jobs.bmwgroup.com` ha dato per il dettaglio 196788 1 GET / 65.322 byte / 0,194 s e microdati HTML JobPosting, senza JSON-LD rilevato. Il percorso di candidatura osservato ricade sotto `/talentcommunity/`, vietato dal robots dello stesso host. Per gli altri host SuccessFactors il robots leggibile non dichiara sitemap nel preflight. RSS e altri formati ammessi per questi host sono **non dimostrato**. [Condizioni BMW](https://www.bmwgroup.jobs/en/general/terms-of-use.html) · [Documentazione SAP Career Site Builder](https://help.sap.com/docs/successfactors-recruiting/setting-up-and-maintaining-sap-successfactors-recruiting/site-configuration-in-career-site-builder-settings)

Il dossier enterprise documenta precedenti sitemap Workday leggibili per Damen e Huhtamaki. Il programma da 200 datori con evidenza di stage e la resa del campione da 50 sono **non dimostrato**. [Prove Workday e SAP esistenti](ats-enterprise-2026-11.md)

### P3 · ATS nazionali

Interrogata in staging la partizione WARC dell'indice colonnare `CC-MAIN-2026-43`, riusando i min/max SURT verificati nel lavoro precedente. Per ogni suffisso è stata letta l'unica partizione con un intervallo sovrapposto, con filtro su risposta indicizzata 200 e proiezione dell'host. Le righe sono host web distinti inclusi radici e sottodomini tecnici. Identità, paese del tenant, disponibilità e qualità delle vacancy richiedono validazione distinta. Le misure non comprendono i metadati del lavoro precedente. [Documentazione indice](https://commoncrawl.org/url-index) · [Metodo del censimento precedente](ats-tenant-discovery-2026-11.md)

| Suffisso interrogato | Host indicizzati | GET | HEAD | Byte contabilizzati | Secondi query |
|---|---:|---:|---:|---:|---:|
| bizneo.com | 5 | 5 | 1 | 678,356 | 0.112 |
| factorial.es | 36 | 5 | 1 | 631,842 | 0.282 |
| factorial.it | 14 | 5 | 1 | 614,993 | 0.116 |
| factorialhr.com | 16 | 5 | 1 | 638,246 | 0.158 |
| flatchr.io | 12 | 4 | 1 | 997,096 | 0.141 |
| taleez.com | 20 | 2 | 0 | 172,032 | 0.054 |
| talentclue.com | 1 | 5 | 1 | 685,556 | 0.100 |
| talentoteca.es | 1 | 5 | 1 | 524,017 | 0.120 |
| viterbit.com | 1 | 5 | 1 | 639,762 | 0.123 |
| werecruit.com | 2 | 5 | 1 | 657,638 | 0.105 |
| werecruit.io | 3 | 5 | 1 | 648,949 | 0.123 |

Un secondo passaggio sullo stesso crawl ha interrogato i percorsi dei board e restituito 188 identificatori distinti WeRecruit sotto `/fr/` o `/en/`, zero chiavi Flatchr sui percorsi `/company/`, `/fr/company/`, `/en/company/` e zero gruppi TalentClue sui percorsi localizzati `/group/<id>/offers`. I tre passaggi hanno impiegato rispettivamente 6 GET / 1 HEAD / 911.093 byte / 0,137 s, 5 GET / 1 HEAD / 1.464.040 byte / 0,228 s e 6 GET / 1 HEAD / 1.054.196 byte / 0,111 s. Le lingue dei percorsi non determinano il paese di un datore e gli zeri riguardano il singolo crawl e i percorsi interrogati. [Board WeRecruit](https://careers.werecruit.io/fr/la-compagnie/offres) · [Board Flatchr](https://careers.flatchr.io/fr/company/flatchr/)

Questo passaggio copre `factorial.es`, `factorial.it` e `factorialhr.com`; gli altri TLD di Factorial HR restano da verificare. Un indice per suffissi non intercetta tutti i domini propri. Per Teamtailor serve identificare gli host con evidenza CNAME verso l'infrastruttura career del fornitore oppure con marcatori verificabili del sito pubblico. Per Taleez e Talentoteca servono i percorsi, perché più enti o programmi possono vivere sullo stesso host. Anche i domini propri di Viterbit e Bizneo richiedono un controllo separato. Il conteggio di tenant per paese e la resa sul campione di cento sono **non dimostrato**. Usare conferme di paese pubblicate dal datore, lasciando i board multinazionali o privi di sede distinta con paese sconosciuto. [Configurazione domini propri Teamtailor](https://support.teamtailor.com/en/articles/113671-use-a-custom-domain-for-your-career-site)

## Riesami

**SmartRecruiters.** `api.smartrecruiters.com` dà 200 sul robots. `/v1/companies/` è consentito a LinkedInBot e il gruppo `*` vieta tutto. L'API è quindi esclusa per People Placement anche se è documentata separatamente come API pubblica. `jobs.smartrecruiters.com` ha risposto 404 al robots. Nessun GET ai posting nei due host. [Robots API](https://api.smartrecruiters.com/robots.txt) · [Robots sito annunci](https://jobs.smartrecruiters.com/robots.txt) · [Documentazione API](https://developers.smartrecruiters.com/docs/posting-api)

**Amazon Jobs.** Il robots di `www.amazon.jobs` limita AhrefsBot e vieta gli alberi `internal` al gruppo generico. Il percorso di ricerca pubblica già presente nel collector dà JSON con `hits`, `jobs` e offset osservabile. Un solo GET ha restituito un record su 29 hit del filtro ampio e non misura la resa HR per studenti. Il dettaglio 10572028 rende HTML con l'ID pubblicato e senza JSON-LD rilevato. Complessivamente 3 GET / 53.752 byte / 3,120 s HTTP circa. Il riesame dei termini locali applicabili resta **non dimostrato**. La fonte Amazon preesistente non è stata modificata. [Robots](https://www.amazon.jobs/robots.txt) · [Avvisi legali](https://www.amazon.jobs/content/en/legal-disclosures-and-notices)

## Replay in staging e limiti prima del rollout

Replay offline di pubblicazione P1 con inventario parziale e zero nuovi record pubblicabili dal dettaglio misurato. Il codice reale di finalizzazione riceve un risultato parziale senza candidati né evidenza di chiusura. Il confronto usa gli ID distinti e le stesse funzioni UI all'orario dello snapshot. Nessuna rimozione di hold o esecuzione live del nuovo collector. Il limite di 120 s del nuovo collector è un budget per fonte e non un tempo previsto dell'intero workflow.

| Lotto | ID prima → dopo (persi) | Aperti per paese | Dirette | Durata collect.yml simulata |
|---|---|---|---|---|
| P1 Randstad IT, replay parziale | 937 → 937 (0) | IT 27, ES 3, NL 241, FR 44, DE 36, PL 0, IE 0, invariati | 54 → 54 in catalogo | non dimostrato |
| P2 grandi aziende | non dimostrato | non dimostrato | non dimostrato | non dimostrato |
| P3 ATS nazionali | non dimostrato | non dimostrato | non dimostrato | non dimostrato |

Prima di una simulazione utile con nuovo rendimento verificato servono una misura Randstad completa senza inferire l'idoneità dall'etichetta stage, le verifiche di accesso per gli altri tenant e un controllo del tempo effettivo con gli shard del workflow.

Controlli in copia scrivibile con Python 3.12.14, 574 test Python e 51 test Node superati. Passano anche valutazione, copertura, build e validazione del catalogo. Provisioning idempotente con 1.916 datori e 1.937 collector attivi.

## Estensione Italia · lotto IT-agenzie

Le quantità di seguito sono misure degli indici pubblicati. Le sitemap non attestano che ogni vacancy sia ancora attiva né contengono il testo necessario alla classificazione per studenti. Il conteggio di stage HR per studenti di oggi rimane **non dimostrato**. I GET includono le letture utili al punto italiano in questa sessione. Il costo Randstad include il preflight e le letture riusate dalla prima sessione. Ritmo per host adottato per le verifiche iterative di 2 s, prima di eventuali ritardi imposti da robots. Budget per singola risposta di 15–25 s e 2–16 MB secondo il tipo di risposta. Il collector Randstad predisposto ha budget 80 richieste e 120 s. Nessun pilot di raccolta intera è partito.

| Dominio | Accesso e misura dell’inventario | Stage HR studenti oggi | GET / byte / secondi HTTP |
|---|---|---|---|
| Randstad IT | Sitemap e dettaglio JSON-LD ammessi. 9.997 URL distinti nei due XML completi, attualità di ciascuno non dimostrato | non dimostrato | 7 / 3.070.251 / 1,910 |
| Manpower IT | Termini §§10–12 su riuso e collegamenti. Ammissione al lotto non dimostrato | non dimostrato | 0 nuovi GET |
| Synergie IT | 4.617 ID distinti nella sitemap job. Lista web senza JobPosting JSON-LD, termini e formato bulk completo non dimostrato | non dimostrato | 2 / 1.429.894 / 0,748 |
| Humangest | Arca24, sitemap di navigazione e microdati. Totale non dimostrato | non dimostrato | 3 / 298.465 / 1,122 |
| Openjobmetis | Board pubblico con conteggio dichiarato variabile; inventario integrale e formato ammesso non dimostrato | non dimostrato | 0 nuovi GET diretti |
| Gi Group principale | 4.536 URL nella sitemap offerte, 4.501 con ID terminale numerico. Termini myGiGroup escludono ricerche automatizzate, portata sul distinto board pubblico non dimostrato | non dimostrato | 2 / 1.121.857 / 1,163 |
| Gi Group Holding | Arca24, sitemap di navigazione e microdati. Totale non dimostrato | non dimostrato | 3 / 290.518 / 1,293 |
| Adecco IT | Condizioni di estrazione restrittive su siti del gruppo. Applicabilità al percorso specifico e inventario non dimostrato | non dimostrato | 0 nuovi GET |
| Umana | Esclusa per divieto esplicito di estrazione automatica, individuato dopo i GET d’indice. Nessuna scheda letta | non dimostrato | 2 / 750 / 1,722 |
| Etjca | Arca24, sitemap di navigazione e microdati. Totale non dimostrato | non dimostrato | 3 / 316.660 / 1,131 |
| Orienta | Arca24, sitemap di navigazione e microdati. Totale non dimostrato | non dimostrato | 3 / 312.471 / 1,679 |
| MAW | Esclusa per i termini | non dimostrato | 0 nuovi GET |

Prove sui termini. [Umana](https://www.umana.it/condizioni-d-uso-del-sito/) · [Gi Group](https://www.gigroup.it/condizioni-di-utilizzo/) · [Adecco Group](https://www.adeccogroup.com/it-it/terms/terms-of-use) · [Manpower](https://www.manpower.it/it/terms-of-use) · [MAW](https://www.maw.it/termini-e-condizioni).

Il percorso `/job/view-job.php?id=` e gli asset `arca24-front` identificano la piattaforma condivisa dai quattro tenant. Tutte le sitemap dichiarate lette contengono quattro link di navigazione. Il primo indice mostra i dettagli e rimandi paginati con `source=`, che i robots vietano. Le quattro schede HTTP 200 usano microdati HTML `JobPosting` e JSON-LD di tipo `TravelAction` e `InteractAction`. La regola richiede JSON pubblico, sitemap di vacancy o JSON-LD JobPosting, oppure RSS pubblico secondo la richiesta. Un formato ammesso per le vacancy e un inventario completo su questi quattro host sono **non dimostrato**. L’adattatore e le voci di registro Arca24 restano bloccati su questa condizione.

Sulle schede di controllo, «Planner» di Etjca, «Cuoco/a ristorazione collettiva» di Orienta e «Impiegato/a amministrativo/a logistico» di Humangest sono ruoli non stage. «Stage risorse umane» sul portale Gi Group Holding è una pista senza verifica del formato e dell’ammissibilità. Per Randstad, «Stage HR Recruiter» a Udine ha JSON-LD ma prova studentesca **non dimostrato**. I titoli Werkstudent o graduate incontrati in un inventario completo sono **non dimostrato**.

Il solo nuovo canale già ammesso ai percorsi strutturati provati fa parte di `IT-agenzie`. L’export registra `agency_client: "non indicato"` e usa l’agenzia come datore quando l’annuncio di una fonte marcata agenzia dichiara esplicitamente il cliente riservato o non indicato. La scheda pubblica mostra «Client not disclosed (via <agenzia>)». Una menzione generica di un cliente o un nome presente nella scheda non attivano l’etichetta.

Il replay di controllo, eseguito con il lotto fermo, mantiene 937 → 937 ID, 0 persi, 27 → 27 stage italiani aperti tutti via servizio pubblico, 0 → 0 dirette e 39 → 39 lead italiani. Nessun titolo entra nel replay. La simulazione con nuovi titoli richiede una lettura integrale classificata. Per il solo Randstad, 9.997 GET di dettaglio a 2 s di distanza richiedono almeno 5 ore e 33 minuti, prima delle letture di inventario e candidatura. Questo limite inferiore riguarda il censimento seriale delle schede, non l’incremento del workflow. L’aumento di durata di `collect.yml`, l’elenco dei nuovi titoli effettivi e il recall italiano atteso dal lotto attivo sono **non dimostrato**. Il controllo di riferimento mantiene 0/70. Nessun rollout o publish avviato.
