# Utrecht — stage HR e copertura provinciale

> Rapporto storico della prima PR #7. L’aggiornamento successivo è in [utrecht-recovery.md](utrecht-recovery.md): quattro stage attualmente verificati; Trunkrs e Domino’s non verificati per intake non confermato. I sei canali tecnici descritti sotto non equivalgono a sei intake disponibili.

Fotografia del 7 novembre 2026, rapporto generato 2026-11-07T08:03:46.759044+00:00. Ricerca in ampliamento, non censimento esaustivo. Base main `3ec0afd`, con PR #5 e #6 già integrate; PR, commit e workflow controllati in `utrecht-baseline.json`. Il checkout con il lavoro Flevoland è rimasto intatto. Ramo dedicato `feat/utrecht-expansion` in un clone separato nel workspace. Nessun merge o deploy di produzione effettuato.

## Territorio e qualità della copertura

Importatore provinciale esistente, API CBS paginate: [86247NED](https://www.cbs.nl/nl-nl/cijfers/detail/86247NED) e [86312NED](https://www.cbs.nl/nl-nl/cijfers/detail/86312NED). Riferimento amministrativo 1 gennaio 2026, snapshot annuale BAG provvisorio. **26 comuni e 104 località**; provincia CBS `PV26`, codice NUTS 2024 **NL35**, coerente con il registro nazionale già presente (non il precedente NL31). Geografia, varianti e omonimie complete in `data/utrecht-geography.json`.

Provincia, comune, località e luogo della vacancy rimangono distinti. L’importatore rifiuta località assegnate al comune sbagliato; presenze solo comunali conservano località nulla. Gli annunci ricevono la regione solo se coincidono datore, paese e città documentata: la sede legale non attribuisce offerte altrove a Utrecht. La composizione ufficiale completa non significa che siano stati censiti datori in tutte le 104 località.

**51 datori distinti**, 20 con dimensione documentata ≥50 e 31 ignota. Configurati 51; tentativo recente per 51. Tutti i comuni hanno almeno un datore ricercato; 17 hanno almeno un datore qualificato. Organico di gruppo e di sede restano distinti, volontari esclusi. Non si dichiara raggiunta la quota dimensionale 50–999 del piano europeo.

| Comune | Località CBS | Datori | Qualificati ≥50 | Dimensione ignota | Stage verificati |
|---|---:|---:|---:|---:|---:|
| Amersfoort | 4 | 3 | 2 | 1 | 0 |
| Baarn | 2 | 2 | 2 | 0 | 0 |
| Bunnik | 3 | 2 | 1 | 1 | 0 |
| Bunschoten | 2 | 1 | 0 | 1 | 0 |
| De Bilt | 6 | 1 | 1 | 0 | 0 |
| De Ronde Venen | 8 | 3 | 2 | 1 | 0 |
| Eemnes | 1 | 1 | 1 | 0 | 0 |
| Houten | 4 | 2 | 2 | 0 | 0 |
| IJsselstein | 1 | 2 | 0 | 2 | 0 |
| Leusden | 3 | 2 | 2 | 0 | 0 |
| Lopik | 5 | 2 | 1 | 1 | 0 |
| Montfoort | 2 | 2 | 1 | 1 | 0 |
| Nieuwegein | 1 | 3 | 1 | 2 | 1 |
| Oudewater | 4 | 1 | 0 | 1 | 0 |
| Renswoude | 1 | 2 | 0 | 2 | 2 |
| Rhenen | 2 | 2 | 1 | 1 | 0 |
| Soest | 2 | 3 | 2 | 1 | 0 |
| Stichtse Vecht | 11 | 2 | 1 | 1 | 0 |
| Utrecht | 4 | 8 | 2 | 6 | 1 |
| Utrechtse Heuvelrug | 7 | 1 | 0 | 1 | 0 |
| Veenendaal | 1 | 2 | 1 | 1 | 0 |
| Vijfheerenlanden | 17 | 2 | 0 | 2 | 0 |
| Wijk bij Duurstede | 3 | 1 | 0 | 1 | 0 |
| Woerden | 4 | 2 | 0 | 2 | 1 |
| Woudenberg | 1 | 2 | 0 | 2 | 0 |
| Zeist | 5 | 2 | 1 | 1 | 1 |

Totali comunali sovrapposti per sedi multiple. Danone, Rijkswaterstaat e Royal A-ware riutilizzano gli ID e canali europei esistenti. Woerden/Oudewater è un solo datore; BEL è l’organizzazione condivisa. Walraven Group e Van Walraven sono datori distinti. Eemhart incorpora Amerpoort/Sherpa; non si duplicano quei datori.

## Stage candidabili verificati

**6 stage verificati** nel catalogo provinciale. La verifica combina vacancy corrente e candidatura corrispondente, senza invio. Le prove della pipeline, metodi e timestamp individuali sono nell’audit; hash e dettagli delle letture primarie in `utrecht-research-vacancies.json`. Una risposta HTTP 200 non è prova sufficiente.

### Koninklijke Remia C.V. — HR Stagiair(e)

[Annuncio ufficiale](https://remiacv.recruitee.com/o/hr-stagiaire) · Den Dolder (Zeist). Candidatura: same-vacancy-applicant-form. Partenza: 2027-02. Durata: almeno quattro mesi. Rimborso: €400/mese a tempo pieno.

Feed ufficiale con 13 record e modulo della stessa vacancy con nome, email, CV e invio attivo. Il corpo ammette mbo/hbo/wo, ma la sezione requisiti specifica HBO: occorre considerare il requisito più stringente. Nessuna lingua di lavoro esplicita rilevata.

### Trunkrs — HR Stagiair

[Annuncio ufficiale](https://werkenbij.trunkrs.nl/o/hr-stagiair) · Woerden (Woerden). Candidatura: same-vacancy-applicant-form. Partenza: 2026-09-01. Durata: non documentata. Rimborso: rimborso previsto, importo non indicato.

Feed ufficiale con 6 record e modulo attivo della stessa vacancy. La partenza del 1 settembre 2026 è passata: feed e modulo attestano la candidabilità osservata, senza stabilire una nuova data di avvio. Confermare la prossima disponibilità con il datore. Olandese e inglese entrambi richiesti.

### AS Watson Benelux — Stage HR Business Partner Kruidvat

[Annuncio ufficiale](https://www.werkenbijaswatson.nl/banen/renswoude/stage-hr-business-partner-kruidvat/3560/46386869952) · Renswoude (Renswoude). Candidatura: rendered-watson-same-requisition-form. Partenza: 2027-02. Durata: almeno cinque mesi; quattro giorni/settimana. Rimborso: €500 lordi/mese a tempo pieno.

Elenco dipartimentale ufficiale e modulo renderizzato della stessa vacancy: titolo, identificativo nel link e campo nascosto della requisizione corrispondono. Campi del candidato e invio presenti; stato di chiusura ricontrollato. Inventario aziendale più ampio ancora parziale.

### AS Watson Benelux — Stage Employer Branding en Recruitment

[Annuncio ufficiale](https://www.werkenbijaswatson.nl/banen/renswoude/stage-employer-branding-en-recruitment/3560/45611367488) · Renswoude (Renswoude). Candidatura: rendered-watson-same-requisition-form. Partenza: 2027-02. Durata: circa cinque mesi. Rimborso: €500 lordi/mese a tempo pieno.

Elenco dipartimentale ufficiale e modulo renderizzato della stessa vacancy: titolo, identificativo nel link e campo nascosto della requisizione corrispondono. Campi del candidato e invio presenti; stato di chiusura ricontrollato. Inventario aziendale più ampio ancora parziale.

### Berenschot — stagiair(e) Advies & Onderzoek – Arbeidsmarkt en Strategisch HRM

[Annuncio ufficiale](https://berenschot.recruitee.com/o/stagiaire-advies-onderzoek-arbeidsmarkt-en-strategisch-hrm) · Utrecht (Utrecht). Candidatura: same-vacancy-applicant-form. Partenza: non documentata. Durata: non documentata. Rimborso: €600 lordi/mese a tempo pieno.

La raccolta ha verificato il modulo ufficiale della stessa vacancy. Le attività riguardano pianificazione del personale, competenze, talento, formazione, occupabilità sostenibile e trasformazioni HR. Richiesti percorso WO-master e iscrizione durante lo stage; partenza e durata non documentate.

### Domino's Pizza Netherlands — Meewerkstage HR

[Annuncio ufficiale](https://werkenbijdominos.nl/hoofdkantoor/meewerkstage-hr) · Nieuwegein (Nieuwegein). Candidatura: official-vacancy-email-instructions. Partenza: settembre, anno non pubblicato. Durata: non documentata. Rimborso: €500 su 40 ore/settimana.

Nove link inventariati, quattro pagine interpretate e cinque errori di formato/sede: raccolta parziale, senza chiusure per assenza. Titolo e sede Nieuwegein sono estratti dalla pagina corrente. Le istruzioni ufficiali invitano a inviare motivazione e CV all’indirizzo indicato nella vacancy, con collegamento email corrispondente verificato. Nessun invio effettuato. Partenza a settembre senza anno: confermare la prossima disponibilità. Buona conoscenza dell’olandese esplicitamente richiesta.

## Opportunità non verificate e programmi

I candidati non verificati vengono mostrati solo attivando il filtro dedicato, con motivazione distinta e link ufficiale quando disponibile. Il numero nel catalogo può includere copie storiche di aggregatori già presenti nella baseline: non sono vacancy verificate aggiuntive. Il registro di ricerca conserva anche opportunità non ancora estraibili automaticamente.

- **DeFabrique Holding — Stage HRM** ([originale](https://www.defabriqueholding.nl/vacatures/stage-hrm-defabrique-holding)): `unverified_opportunity`, blocked-official-application. Testo corrente con partenza febbraio 2027. Il canale CVW collegato non è verificabile: robots restituisce HTTP 406 e non viene aggirato. La descrizione strutturata è vuota; l’estrattore HTML condiviso legge sede e testo visibili. La corrispondenza della candidatura non è confermata.

- **HB RTS — HR Intern** ([originale](https://www.hb-rts.com/en-uk/careers/stagiair-hr)): `unverified_opportunity`, application-entry-not-established. Annuncio specifico corrente con sede Utrecht. L’indirizzo pubblicato è per domande, senza istruzioni per inviare una candidatura; nessun modulo confermato. L’inglese è indicato come preferenza, senza prova che basti per lavorare.

- **HB RTS — Learning & Development Intern** ([originale](https://www.hb-rts.com/en-uk/careers/stagiair-learning-development)): `unverified_opportunity`, application-entry-not-established. Annuncio specifico corrente con sede Utrecht. L’indirizzo pubblicato è per domande, senza istruzioni per inviare una candidatura; nessun modulo confermato. L’inglese è indicato come preferenza, senza prova che basti per lavorare.

- **Prénatal — Meewerkstage HR - Amersfoort** ([originale](https://www.werkenbij.prenatal.nl/vacature-servicekantoor/meewerkstage-hr-amersfoort)): `unverified_opportunity`, application-entry-not-established. Stage specifico di 32–38 ore. La pagina richiede il pulsante di candidatura ed esclude candidature per email/WhatsApp. Né lettura diretta né rendering hanno stabilito un modulo utilizzabile: il contatto informativo non viene riutilizzato per candidarsi.

- **Danone — Internship HR Business Partner Intern** ([originale](https://careers.danone.com/benelux/en/jobs/internship-hr-business-partner-intern-28754-en-us.html)): `unverified_opportunity`, robots-disallowed-application. Vacancy HRBP 28754 corrente, candidatura ufficiale iCIMS vietata da robots. Il corpo riporta scadenza 10 novembre 2026. Richiesta iscrizione Bachelor/Master durante tutto il periodo; per studenti non UE università olandese e accordo Nuffic. Inglese fluente esplicito, sufficienza del solo inglese sconosciuta. L’analisi riguarda il testo primario, senza importare requisiti da offerte correlate.

- **Sopra Steria — Stage HR** ([originale](https://careers.soprasteria.com/job/stage-hr-in-nieuwegein-netherlands-jid-9153)): `excluded_closed`, explicitly-expired. La pagina conserva la descrizione ma dichiara esplicitamente che la vacancy è scaduta. Il lettore condiviso rifiuta questo messaggio, con test di regressione. Non viene contata fra gli stage candidabili.

- **Rijkswaterstaat — Stage organisatiepsychologie, HR en bestuurskunde** ([originale](https://www.werkenvoornederland.nl/vacatures/stage-organisatiepsychologie-hr-en-bestuurskunde-RWS-2026-5392)): `excluded_unavailable`, current-page-vacature-niet-beschikbaar. La copia indicizzata descriveva uno stage da febbraio 2027 con scadenza 16 novembre 2026; la pagina ufficiale corrente visualizza “Vacature niet beschikbaar”. Prevale la verifica corrente sulla copia indicizzata. Nessuna candidatura confermata.

Il programma generale AS Watson è separato dalle vacancy specifiche. BCN è una pista di ricerca con accesso 403, non un programma validato o uno stage aggiuntivo. La descrizione del team Miele che nomina un HR stagiair non è un annuncio di selezione.

## Lingue e requisiti

Il testo olandese non comporta esclusione, né dimostra un requisito linguistico. Trunkrs richiede esplicitamente olandese **e** inglese; Domino’s richiede olandese. Per Remia, Berenschot e i due AS Watson non hanno requisiti di lingua espliciti accertati. Danone richiede inglese, ma resta non verificato per la candidatura. HB RTS indica inglese come preferenza (“English is a plus”), non prova di lavoro solo in inglese; il parser conserva il limite e il rapporto primario registra la preferenza. La sufficienza del solo inglese rimane sconosciuta.

Formazione e iscrizione derivano dal testo originale. Remia menziona mbo/hbo/wo nel corpo e HBO nei requisiti: conservare il requisito più stringente. Trunkrs HBO/WO; Berenschot WO-master e iscrizione durante lo stage; AS Watson richiede profilo HBO, ma l’estrattore non ricava da questo una prova separata di iscrizione per tutto il periodo. Non viene inventata una scadenza quando assente.

## Datori e raccolta eseguita

Eseguiti **58 tentativi su 51 fonti distinte**, comprese le verifiche mirate. Stati correnti: 33 partial, 4 blocked-or-failed, 10 discovery-incomplete, 4 collected. Tempi, richieste, record, errori, perimetri e limiti per ogni esecuzione sono salvati integralmente in `utrecht-collection-audit.json`.

Remia: feed ufficiale 13/13 record osservati; Trunkrs: 6/6. AS Watson: due annunci nel sottoinsieme dipartimentale letto, inventario aziendale più ampio non completo. Gli elenchi e sitemap parziali non dimostrano l’assenza di stage e non chiudono offerte per assenza. Gli inventari vuoti accettati dal lettore hanno prova esplicita; nessuna copertura nazionale viene dedotta da zero record senza paese osservato.

| Datore | Comune / città | Dimensione | Stato raccolta | Recruiting ufficiale |
|---|---|---|---|---|
| Danone | Utrecht / Utrecht | ignota | partial | [canale](https://careers.danone.com) |
| Rijkswaterstaat | Utrecht / Utrecht | ignota | partial | [canale](https://www.werkenvoornederland.nl/organisaties/ministerie-van-infrastructuur-en-waterstaat/rijkswaterstaat) |
| Royal A-ware | Lopik / Lopik | circa 5300 | partial | [canale](https://werkenbijaware.com/) |
| Gemeente Baarn | Baarn / Baarn | circa 180 | blocked-or-failed | [canale](https://werkenbijgemeentebaarn.nl/over-baarn) |
| Gemeente Bunnik | Odijk / Bunnik | circa 100 | discovery-incomplete | [canale](https://www.baanbijbunnik.nl/) |
| Gemeente Bunschoten | località da confermare / Bunschoten | ignota | partial | [canale](https://www.bunschoten.nl/werkenbij) |
| Gemeente De Bilt | Bilthoven / De Bilt | circa 230 | partial | [canale](https://www.werkenvoordebilt.nl/) |
| Gemeente De Ronde Venen | Mijdrecht / De Ronde Venen | circa 350 | discovery-incomplete | [canale](https://werkenvoorderondevenen.nl/) |
| Gemeente Houten | Houten / Houten | circa 350 | partial | [canale](https://www.werkenbijhouten.nl/) |
| Gemeente IJsselstein | IJsselstein / IJsselstein | ignota | discovery-incomplete | [canale](https://www.ijsselstein.nl/werken-bij-de-gemeente-ijsselstein) |
| Gemeente Leusden | Leusden / Leusden | circa 200 | partial | [canale](https://www.leusden.nl/werkenbijleusden) |
| Gemeente Lopik | località da confermare / Lopik | ignota | discovery-incomplete | [canale](https://www.lopik.nl/werken-bij-lopik) |
| Gemeente Montfoort | località da confermare / Montfoort | ignota | discovery-incomplete | [canale](https://www.montfoort.nl/Alle_onderwerpen/Bestuur_en_organisatie/Werken_bij_Montfoort) |
| Gemeente Nieuwegein | Nieuwegein / Nieuwegein | ignota | partial | [canale](https://www.nieuwegein.nl/gemeente-bestuur-en-organisatie/organisatie/werken-bij-de-gemeente) |
| Gemeente Renswoude | Renswoude / Renswoude | ignota | partial | [canale](https://www.renswoude.nl/werken-bij-de-gemeente) |
| Gemeente Rhenen | località da confermare / Rhenen | circa 200 | partial | [canale](https://www.rhenen.nl/info-over-de-gemeente/werken-bij-de-gemeente-rhenen) |
| Gemeente Soest | località da confermare / Soest | ignota | partial | [canale](https://www.soest.nl/vacatures) |
| Gemeente Stichtse Vecht | Maarssen / Stichtse Vecht | circa 500 | partial | [canale](https://www.werkenbijstichtsevecht.nl/) |
| Gemeente Utrechtse Heuvelrug | località da confermare / Utrechtse Heuvelrug | ignota | collected | [canale](https://www.heuvelrug.nl/werken-bij-de-gemeente) |
| Gemeente Veenendaal | località da confermare / Veenendaal | ignota | partial | [canale](https://www.veenendaal.nl/info-over-de-gemeente/over-de-gemeente/werken-voor-veenendaal/veens-werken) |
| Gemeente Vijfheerenlanden | località da confermare / Vijfheerenlanden | ignota | partial | [canale](https://www.vijfheerenlanden.nl/vacatures) |
| Gemeente Wijk bij Duurstede | Wijk bij Duurstede / Wijk bij Duurstede | ignota | discovery-incomplete | [canale](https://www.werkenbijgemeentewijkbijduurstede.nl/) |
| Gemeente Woerden | Woerden / Woerden; Oudewater / Oudewater | ignota | partial | [canale](https://werkenbij.woerden.nl/) |
| Gemeente Woudenberg | località da confermare / Woudenberg | ignota | partial | [canale](https://www.woudenberg.nl/over-de-gemeente/vacatures) |
| Gemeente Zeist | Zeist / Zeist | circa 600 | discovery-incomplete | [canale](https://www.werkenbijzeist.nl/vacatures/) |
| BEL gemeenten | Eemnes / Eemnes | circa 250 | discovery-incomplete | [canale](https://werkenvoorbel.nl/) |
| DeFabrique Holding | Utrecht / Utrecht | ignota | partial | [canale](https://www.defabriqueholding.nl/vacatures) |
| Koninklijke Remia C.V. | Den Dolder / Zeist | ignota | collected | [canale](https://remiacv.recruitee.com/) |
| Trunkrs | Woerden / Woerden | ignota | collected | [canale](https://werkenbij.trunkrs.nl/) |
| AS Watson Benelux | Renswoude / Renswoude | ignota | partial | [canale](https://www.werkenbijaswatson.nl/vacatures-zoeken) |
| Sopra Steria | Nieuwegein / Nieuwegein | ≥51000 | partial | [canale](https://careers.soprasteria.com/) |
| Prénatal | Amersfoort / Amersfoort | ignota | partial | [canale](https://www.werkenbij.prenatal.nl/) |
| Domino's Pizza Netherlands | Nieuwegein / Nieuwegein | ignota | partial | [canale](https://www.werkenbijdominos.nl/stages) |
| HB RTS | Utrecht / Utrecht | ignota | partial | [canale](https://www.hb-rts.com/en-uk/careers) |
| AFAS Software | Leusden / Leusden | circa 680 | partial | [canale](https://www.werkenbijafas.nl/) |
| HSO | Veenendaal / Veenendaal | ≥2200 | discovery-incomplete | [canale](https://www.hso.com/nl/carriere/join-hso/) |
| Berenschot | Utrecht / Utrecht | circa 500 | partial | [canale](https://www.berenschot.nl/vacatures) |
| Terberg Techniek | IJsselstein / IJsselstein | ignota | partial | [canale](https://www.terbergtechniek.nl/vacatures) |
| Universiteit Utrecht | Utrecht / Utrecht | ignota | partial | [canale](https://www.uu.nl/organisatie/werken-bij-de-universiteit-utrecht) |
| BCN | Utrecht / Utrecht | ignota | blocked-or-failed | [canale](https://werkenbij.bcn.nl/) |
| Vrumona | Bunnik / Bunnik | ignota | blocked-or-failed | [canale](https://www.vrumona.nl/) |
| ONVZ | Houten / Houten | circa 400 | partial | [canale](https://werkenbijonvz.nl/) |
| Van den Pol Elektrotechniek | Montfoort / Montfoort; Amersfoort / Amersfoort | circa 250 | partial | [canale](https://werkenbijvandenpol.nl/vacatures/) |
| Miele Nederland B.V. | Vianen / Vijfheerenlanden | ignota | discovery-incomplete | [canale](https://career.miele.nl/) |
| Kontakt der Kontinenten | Soesterberg / Soest | circa 80 | partial | [canale](https://www.kontaktderkontinenten.nl/vacatures/) |
| Walraven Group | Mijdrecht / De Ronde Venen | circa 1300 | blocked-or-failed | [canale](https://www.walraven.com/nl/werken-bij-walraven/) |
| Van Walraven | Mijdrecht / De Ronde Venen | ignota | partial | [canale](https://werkenbij.vanwalraven.com/jobs) |
| Eemhart | Baarn / Baarn; Utrecht / Utrecht; Amersfoort / Amersfoort; Soest / Soest | circa 4000 | partial | [canale](https://www.werkenbijeemhart.nl/) |
| VAK Infra | Woudenberg / Woudenberg | ignota | partial | [canale](https://vak-bv.nl/vacatures/) |
| Ouwehands Dierenpark | Rhenen / Rhenen | ignota | partial | [canale](https://www.ouwehand.nl/over-ons/werken-bij) |
| ZorgDomein | Breukelen / Stichtse Vecht | ignota | collected | [canale](https://zorgdomein.com/werken-bij/) |

Gli elenchi comunali possono collegare portali sovracomunali: le posizioni fuori provincia restano fuori dal risultato Utrecht. Heteren, Bergschenhoek, Bergambacht e Hoofddorp non sono sedi Utrecht. Non si aggirano robots.txt, CAPTCHA, autenticazioni o blocchi. La quota di siti configurati non viene presentata come raccolta completa.

## Integrazione e interfaccia

Riutilizzati importer CBS, integrazione provinciale, registro europeo, adattatori feed/HTML/browser e classificatore. Nuova verifica Watson: requisizione JSON-LD, link osservato, titolo, ReqId nascosto, campi e submit del modulo devono corrispondere; il DOM finale deve essere libero da challenge e messaggi di chiusura. Test negativi coprono modulo errato, requisizione errata, campi mancanti e modulo conservato su annuncio scaduto.

La pagina `utrecht.html` usa il modello condiviso `province.js`: stage verificati, filtro per non verificati, ricerca, lingua dell’annuncio e requisiti linguistici di lavoro, programmi separati, fonti, copertura comunale e timestamp. Navigazione collegata dal catalogo europeo e dal registro. Il workflow quotidiano `collect.yml` include i datori nei **16 shard esistenti**, rigenera tutti e quattro i rapporti provinciali, senza nuove automazioni o chiamate ricorrenti AI. Orario invariato: 06:17 UTC, 07:17 invernale / 08:17 estiva a Zurigo e Amsterdam, soggetto a ritardi GitHub.

## Verifiche e conservazione

**182 test Python e 18 frontend superati; 64 esempi di classificazione senza falsi positivi o negativi; validazione del catalogo e del registro, build statica e controllo delle differenze riusciti.** Browser a 1280 e 390 px: quattro province, filtri, ricerca e conteggi comunali, 27 paesi; nessun errore JavaScript o overflow. Frisia conserva uno stage verificato, Groningen due e Drenthe due secondo la policy corrente.

Comandi e risultati effettivi: `utrecht-validation.json`; test browser: `utrecht-ui-verification.json`. Il confronto con main conserva tutti gli ID di datori/fonti e tutte le URL precedenti, le altre ricerche provinciali e i luoghi di altre regioni. Nessun report non riuscito è marcato completo. Dettagli e conteggi baseline/finali nell’audit.

```sh
python3 scripts/import_province_geography.py --province-code PV26 --nuts-code NL35 --output data/utrecht-geography.json
python3 scripts/integrate_utrecht.py
python3 scripts/collect_province.py utrecht --workers 6
python3 scripts/company_coverage.py
python3 -m unittest discover -s tests
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
python3 scripts/check_province_ui.py
```

La consegna comprende la PR revisionabile. Il merge e la pubblicazione in produzione richiedono autorizzazione separata e non sono stati eseguiti. Il primo ciclo remoto con Utrecht e l’eventuale deployment successivo sono ancora da osservare dopo il merge: i controlli locali non vengono presentati come prova della futura automazione.

## Lacune e priorità successive

Ampliare i datori privati 50–999 e qualificare le 31 dimensioni ignote; estendere le sedi oltre il primo lotto e le letture oltre gli inventari parziali. Confermare nuova partenza Trunkrs; verificare canali autorizzati Danone/CVW, moduli Prénatal e HB RTS senza invii; mantenere esclusioni per scadenze effettive. Approfondire opportunità nei comuni senza stage verificati. Nessun denominatore nominativo completo delle imprese provinciali è stato ottenuto, quindi non si calcola una percentuale di copertura del mercato.
