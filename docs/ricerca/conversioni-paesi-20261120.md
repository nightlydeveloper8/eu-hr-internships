# Conversioni e ricerca per paese · 20 novembre 2026

[Snapshot di produzione](https://github.com/nightlydeveloper8/eu-hr-internships/blob/7c5ce8037f9bdca7fd869d57668c9f420f40edc0/data/catalog.json). 887 ID, 39 candidature in sei paesi UE (NL 22, FR 7, DE 4, BE 4, ES 1, PT 1). 21 paesi UE senza candidature dirette, 16 senza schede HR pubbliche né dirette. Dati riferiti all'ora del catalogo. [Confronto catalogo servito](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44748297519).

## Rendimento per canale

| Priorità | Schede osservate | Risultato e criterio di arresto |
| --- | ---: | --- |
| JobTech, Svezia | 5 | Jobandtalent Malmö, JobTech 31558200 → Teamtailor 8503489, riconfermato il 20 novembre con inventario e modulo. [Prova corrente](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44770453908): in staging 39 → 40, stessi 887 ID. [Bozza disabilitata #89](https://github.com/nightlydeveloper8/eu-hr-internships/pull/89). Gli altri quattro puntano a Bosch SmartRecruiters, Suzuki Varbi, Splendor Hailey HR e alla home Perceptric. Non hanno una prova equivalente. |
| Gi Group, Italia | 30 | Un solo datore, 23 sedi provinciali. Due ID pubblici a Padova con lo stesso titolo e due annunci aziendali distinti ([Cittadella 1406689](https://www.gigroup.it/offerte-lavoro-dettaglio/cittadella-padova-stage-risorse-umane/1406689/), [Camposampiero 1405169](https://www.gigroup.it/offerte-lavoro-dettaglio/camposampiero-padova-stage-risorse-umane/1405169/)). I due dettagli di Padova e quello di Torino rimandano a pagine generiche tra gli URL Gi Group esaminati. Nessuna corrispondenza univoca. Il pulsante Candidati passa a it.mygigroup.com, fuori dal perimetro del collector esistente. |
| EURES, Svizzera | 30 | 19 denominazioni di datori, 10 sedi così come pubblicate. Tre schede Teoxane stesso titolo/sede. OFCL e BBL sono denominazioni linguistiche da riconciliare. HUG ha una [vacancy aziendale specifica](https://jobs.smartrecruiters.com/HUG/744000161747261), con scadenza 15 dicembre, che richiede l'invio tramite piattaforma. La [procedura HUG](https://www.hug.ch/emploi/comment-postuler) richiede un profilo. Nessuna prova live del modulo nel perimetro approvato. |
| Recruitee, Polonia e NL | 3 inventari tentati | SmartWays ha 14 record, 0 corrispondenze, 3 richieste / 418.529 byte. CM.com, feed JSON HTTP 404, 3 / 348.778. VDK, nessun link al tenant sulla pagina ufficiale provata, 2 / 95.481. Aveco ha un [modulo aziendale a Holten](https://www.werkenbijavecodebondt.nl/vacatures/stagiaire-hr-communicatie-kam-1/solliciteren), con slug diverso dalla vecchia scheda Recruitee. Nessuna attivazione. |

[Dettagli EURES e secondo lotto Recruitee](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44769455657). Cinque dettagli EURES, 6 richieste e 32.815 byte. Tre tentativi Recruitee, 8 richieste e 862.788 byte. Un risultato da indice o ricerca resta una pista fino alla verifica del percorso.

## Mercati senza candidature dirette

- **Danimarca.** Workindenmark rimanda a Jobnet. Per ILVA la pista di Sabro non dispone di prova del modulo. La ricerca danese presso i datori porta a [JKS](https://www.jks.dk/om-jks/job-i-jks), con moduli Talentech specifici di Esbjerg 160886, Odense 160782 e Vejle 157063. [Pilota e risultato live separato #90](https://github.com/nightlydeveloper8/eu-hr-internships/pull/90).
- **Irlanda.** I risultati HR di JobsIreland esaminati erano WPEP per persone con requisiti di welfare. [Regeneron R52961](https://careers.regeneron.com/en/jobs/r52961/intern-hr-technology-and-analytics/) a Dublino rimanda al percorso Workday R52961/apply. La lettura della pagina di arrivo non mostra campi candidabili. Nessuna approvazione di host o login.
- **Cechia.** Il precedente MPSV aveva 0 stage HR in 39.552 schede. La nuova ricerca ha trovato [SAP Recruiting Associate](https://jobs.sap.com/en/jobs/744000161307409/sap-ixp-intern-recruiting-associate-tech-td-limited-full-time/). Il percorso SmartRecruiters termina in una vista che richiede JavaScript. Il [tenant Manifesto](https://manifesto.careers-page.com/) aperto in diretta presentava cinque vacancy, nessuna HR, mentre l'indice di ricerca ne riportava sette inclusa HR. Non conteggiata.
- **Polonia.** ePraca richiede domanda firmata e IP fisso, come documentato nella [#87](https://github.com/nightlydeveloper8/eu-hr-internships/pull/87). Bosch 744000147492599 e Clifford Chance 744000151621729 dichiarano l'annuncio scaduto. Carlsberg Poznań dichiara la posizione coperta. [Saint-Gobain 329013 a Koło](https://joinus.saint-gobain.com/pl/pol/tpr/i/46130/329013/stazystastazystka-w-dziale-hr) mantiene l'ID nell'URL Aplikuj. L'HTML accessibile non fornisce un modulo candidato identificabile. SmartWays esaminato nell'inventario corrente.

## EURES, confronto a parità di pagine

[Primo campione](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44766676817) e [nuovo confronto su cinque mercati](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44769068221). Per ogni termine, stessa prima pagina e uguale limite di risultati. Conteggio geografico solo con paese esplicito. Deduplica per impronta del collector. Nei quattro mercati prioritari il primo campione dava 109 contro 2. Il secondo dà 116 contro 74, aumentando del 56,8% i risultati nel paese. Nessuno dei due produce un nuovo stage nei quattro mercati.

| Paese | Termine secondo campione | Schede nel paese, globale → filtrata | Stage HR distinti del paese, globale → filtrata | Nuovi su entrambe |
| --- | --- | ---: | ---: | ---: |
| CZ | stáž personalistika | 34 → 50 | 0 → 0 | 0 |
| DK | praktik rekruttering | 1 → 8 | 0 → 0 | 0 |
| IE | human resources intern | 0 → 8 | 0 → 0 | 0 |
| PL | staż rekrutacja | 39 → 50 | 0 → 0 | 0 |
| NL | stage hr | 36 → 50 | 34 → 41 | 0 |

I 36 ID grezzi del controllo globale NL sono tutti tra i 43 ID del controllo geografico. Dopo la deduplica, si ritrovano tutti i 34 stage più altri sette già noti. Undici richieste complessive (dieci pagine più robots), 2.145.117 byte, zero nuovi stage per 100 richieste. Ogni braccio misura il proprio paese bersaglio; le eventuali opportunità negli altri paesi restituite dalle pagine globali non sono comprese nel confronto.

Il prototipo distribuisce 28 prime pagine sui mercati configurati (UE27 e CH), prima della coda esistente, nello stesso BudgetClient da 330 richieste. A parità di un GET robots restano al massimo 301 richieste per il seguito, comprese pagine ulteriori, retry e controlli noti. Il campione live ha interrogato cinque mercati, non 28. Mancano i payload delle pagine ordinarie sostituite per stimare la conservazione su tutti i mercati; nessuna proiezione delle 34/34 NL alla giornata. Il rendimento osservato giustifica investire dapprima in inventari di datori in DK, IE, CZ e PL e conservare il controllo NL. Nessun cambio di frequenza o budget ordinario.

## Raggruppamento dello snapshot

Un gruppo è una coda di verifica, non una vacancy deduplicata. Le 65 identità pubbliche sono elencate per datore, sede e host esterno (EURES ove il catalogo non espone il link esterno). La prova di uno stesso ID ufficiale resta necessaria per fondere righe o promuoverle.

| Paese | Datore | Sede dichiarata | Piattaforma | Schede | ID catalogo |
| --- | --- | --- | --- | ---: | --- |
| CH | Amplifon AG | Zug | EURES | 1 | `713e682c28926e986294` |
| CH | Assura SA | Vaud | EURES | 1 | `9c9c0563f8a447d23471` |
| CH | BOBST MEX SA | Vaud | EURES | 2 | `917b19265b41db7f1c0e`, `b0c40dd8e9376efebc64` |
| CH | Bundesamt für Bauten und Logistik BBL | Bern / Berne | EURES | 2 | `1985c8c562257c1dc042`, `4f0dd17f3fd60b750a67` |
| CH | Direktion für Inneres und Justiz des Kantons Bern | Bern / Berne | EURES | 2 | `974bf5e47a920c028660`, `e7e22f40a237e1ab92ed` |
| CH | Etat de Vaud - Apprentissage | Vaud | EURES | 2 | `73dd72051fe3081ac7bc`, `b5c6693b958a1b449201` |
| CH | Genedis SA | Valais / Wallis | EURES | 1 | `53a4358143c5799226ad` |
| CH | Gi Group Luzern | Luzern | EURES | 1 | `662986b76a206230b9df` |
| CH | globegarden gmbh | Zürich | EURES | 1 | `fed4df4dbc1a1f38ae55` |
| CH | Integrierte Psychiatrie Winterthur – Zürcher Unterland ipw | Zürich | EURES | 2 | `570fe4c5a93626db54fe`, `ccd152d18c4ab38e45a1` |
| CH | Les hôpitaux universitaires de Genève | Genève | EURES | 1 | `5c907e15ec7101cf487d` |
| CH | Office fédéral constructions et logistique OFCL | Bern / Berne | EURES | 2 | `06de071c4b59b9528e59`, `66f41190436fac40bbb1` |
| CH | OK Job SA | Genève | EURES | 2 | `0c27827a81277ba468dc`, `500a08eb54a507a9d62f` |
| CH | Psychiatrie St.Gallen | St. Gallen | EURES | 1 | `308614c04145018b5478` |
| CH | Service recrutement de l'Ensemble Hospitalier de la Côte - EHC | Vaud | EURES | 1 | `96962ce82804fe18f325` |
| CH | Spital Muri | Aargau | EURES | 2 | `2599c24692142b4ebe75`, `2cd2456c52da3ef0c1e5` |
| CH | Sympajobs AG | Basel-Landschaft | EURES | 1 | `78ee3e5bacf1f8d3551f` |
| CH | Teoxane SA | Genève | EURES | 3 | `031bfc8ec80561a07ccf`, `769ac696a6c3b2951479`, `e85d778c21ba32076135` |
| CH | UCC COFFEE SWITZERLAND AG | Bern / Berne | EURES | 2 | `4070c9341dd077de33de`, `c0a0a523b16dfecfb128` |
| IT | GI GROUP S.P.A. | Ancona | EURES | 1 | `506604f79df8f6589902` |
| IT | GI GROUP S.P.A. | Bari | EURES | 1 | `29499780b0e09abded78` |
| IT | GI GROUP S.P.A. | Bergamo | EURES | 1 | `5104ab76d2e8e4a76ba7` |
| IT | GI GROUP S.P.A. | Catania | EURES | 1 | `ad709cec671ffb6fbf42` |
| IT | GI GROUP S.P.A. | Catanzaro | EURES | 1 | `79650f41f1d13abae35f` |
| IT | GI GROUP S.P.A. | Cuneo | EURES | 1 | `766b7f8930a79846804a` |
| IT | GI GROUP S.P.A. | Ferrara | EURES | 1 | `b942933c21b337f5b015` |
| IT | GI GROUP S.P.A. | Forlì-Cesena | EURES | 1 | `73ef488731b768351670` |
| IT | GI GROUP S.P.A. | Milano | EURES | 3 | `4b36afb1bf1140cd395e`, `95b2b90ad0a8d3366d81`, `bf99d957ac1d110850b7` |
| IT | GI GROUP S.P.A. | Modena | EURES | 1 | `e93e709e6d0c7df7b5e7` |
| IT | GI GROUP S.P.A. | Monza e della Brianza | EURES | 1 | `789a2a7bfd98d3b9f5bc` |
| IT | GI GROUP S.P.A. | Napoli | EURES | 1 | `746800fad65a73c04446` |
| IT | GI GROUP S.P.A. | Padova | EURES | 2 | `890c27af45605bfc13b8`, `eaa65d9c697589b26ce0` |
| IT | GI GROUP S.P.A. | Pavia | EURES | 2 | `1aa2cf02b5a29f2cfe5e`, `63cc89e3f6bc1b9f2108` |
| IT | GI GROUP S.P.A. | Pisa | EURES | 1 | `696b755a2e83b0615643` |
| IT | GI GROUP S.P.A. | Reggio nell’Emilia | EURES | 1 | `ae82acae8ea08ac27627` |
| IT | GI GROUP S.P.A. | Rimini | EURES | 1 | `9eadf1af75e195b6cd90` |
| IT | GI GROUP S.P.A. | Taranto | EURES | 1 | `c39a483f25ee1f537497` |
| IT | GI GROUP S.P.A. | Torino | EURES | 2 | `76277b50f9333db55be8`, `fe4a7bc318dcec8b1442` |
| IT | GI GROUP S.P.A. | Treviso | EURES | 2 | `3b2fa93581e62c7aa866`, `66f702980d370a1cc09b` |
| IT | GI GROUP S.P.A. | Venezia | EURES | 2 | `33598e9c67d7cab0ef46`, `c828e5278d13abbce4d0` |
| IT | GI GROUP S.P.A. | Verbano-Cusio-Ossola | EURES | 1 | `dc88725cd858afa9c092` |
| IT | GI GROUP S.P.A. | Vicenza | EURES | 1 | `8f661af2b7f38742f2a5` |
| SE | Bosch Thermoteknik AB | Tranås | jobs.smartrecruiters.com | 1 | `dba5642d135716b0f07f` |
| SE | Jobandtalent Sweden AB | Malmö | jobb.jobandtalent.com | 1 | `c8bdac2ae98420d4b1e7` |
| SE | Perceptric Al AB | Stockholm | perceptricapply.com | 1 | `fb3f0dca12d18592ee08` |
| SE | Splendor Plant Aktiebolag | Jonstorp | splendorplant.careers.haileyhr.app | 1 | `76edecc7054ab67ebd5a` |
| SE | Suzuki Garphyttan AB | Garphyttan | suzukigarphyttan.varbi.com | 1 | `92d027412527a37dee1f` |
