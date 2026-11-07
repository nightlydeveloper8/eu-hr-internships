# Flevoland: ricerca preliminare per Provincial Factory (7 novembre 2026)

**Handoff ChatGPT → Codex; NON sono vacancy verificate né datori automaticamente integrabili.** Si tratta di una coda di ricerca preliminare basata su pagine ufficiali e, dove dichiarato, aggregatori. Riutilizzare gli ID esistenti e rispettare robots/limitazioni. La **PR #7 Utrecht** era ancora aperta al controllo e nei precedenti rapporti esiste lavoro **locale non committato su Flevoland**: preservarlo e confrontarlo prima di toccare file o cercare duplicati.

## Priorità e risultati

- 19 datori candidati nei **6 comuni**: Almere, Lelystad, Dronten, Noordoostpolder, Urk, Zeewolde.
- 7 opportunità HR candidate, di cui **3 su pagine ufficiali con urgenza/alto valore** (Gemeente Almere, Provincie Flevoland, SMT). Nessuna è stata verificata qui con corrispondenza/validità del modulo ufficiale: **0 stage dichiarati verificati da questa ricerca**.
- **Almere**: stage Recruitment scadenza **10 novembre 2026**, inizio febbraio 2027, da verificare prima che scada.
- **Provincie Flevoland**: stage werving/onboarding con scadenza **discordante**: annuncio riporta 29 novembre nel corpo e 30 novembre nell'intestazione; nessuna data univoca inventata.
- **SMT Emmeloord**: stage HR nel listino corrente del datore; requisiti espliciti di olandese.
- **Van Amersfoort Racing**: pagina specifica ancora pubblicata ma partenza settembre 2026, quindi non dedurre una nuova intake; la pagina careers generale non lo evidenzia nel risultato corrente.
- **Meerpaal**: pagina nello storico/elenco ufficiale ma scadenza 15 ottobre già passata; non dichiarare aperto.
- **Marfo**: stage reperito da aggregatore, ma la lista ufficiale consultata non lo mostra; occorre individuare URL e candidatura primaria, altrimenti lasciare unverified.
- **HLB Group**: aggregatore mostra stage HR ma manca la pagina di vacancy sul datore; non promuovere a verificato.
- **Urk**: diversi datori con pagine careers ufficiali, ma nessun stage HR corrente accertato da questa ricognizione; evitare inferenze.

## Input di ricerca per la futura Factory

I blocchi JSON seguenti sono **candidate-only** e non devono essere importati direttamente nei registri verificati. Il lettore della Issue deve validare schema, domini, provincia, freschezza, duplicati e permessi. Conservare evidenze e ragioni di esclusione, non riscrivere interi annunci.

### Employers (candidate schema v1)

```json
[
  {
    "candidate_id": "flv-e01",
    "employer": "Gemeente Almere",
    "municipality": "Almere",
    "official_career_url": "https://www.werkenbijalmere.nl/vacatures/stage-meewerkstage-team-recruitment-391873",
    "evidence_url": "https://www.werkenbijalmere.nl/vacatures/stage-meewerkstage-team-recruitment-391873",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e02",
    "employer": "Alfen",
    "municipality": "Almere",
    "official_career_url": "https://alfen.com/nl-nl/werken-bij/stage/stage-mogelijkheden",
    "evidence_url": "https://alfen.com/nl-nl/werken-bij/stage/stage-mogelijkheden",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e03",
    "employer": "Provincie Flevoland",
    "municipality": "Lelystad",
    "official_career_url": "https://flevoland.nl/wie-zijn-we/werken-bij-flevoland/vacatures",
    "evidence_url": "https://flevoland.nl/wie-zijn-we/werken-bij-flevoland/vacatures",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e04",
    "employer": "Marfo",
    "municipality": "Lelystad",
    "official_career_url": "https://www.werkenbijmarfo.nl/vacatures/",
    "evidence_url": "https://www.werkenbijmarfo.nl/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e05",
    "employer": "Farm Dairy",
    "municipality": "Lelystad",
    "official_career_url": "https://farmdairy.com/werken-bij-farm-dairy/",
    "evidence_url": "https://farmdairy.com/werken-bij-farm-dairy/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e06",
    "employer": "Giant Europe",
    "municipality": "Lelystad",
    "official_career_url": "https://www.giant-bicycles.com/nl/vacatures",
    "evidence_url": "https://www.giant-bicycles.com/nl/vacatures",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e07",
    "employer": "Meerpaal",
    "municipality": "Dronten",
    "official_career_url": "https://www.meerpaal.nl/vacatures/",
    "evidence_url": "https://www.meerpaal.nl/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e08",
    "employer": "Gemeente Dronten",
    "municipality": "Dronten",
    "official_career_url": "https://www.dronten.nl/bestuur-organisatie/werken-bij-gemeente-dronten",
    "evidence_url": "https://www.dronten.nl/bestuur-organisatie/werken-bij-gemeente-dronten",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e09",
    "employer": "HLB Group (HLB / De Groene Vlieg)",
    "municipality": "Dronten",
    "official_career_url": "https://nl.indeed.com/cmp/Hlb-Groep",
    "evidence_url": "https://nl.indeed.com/cmp/Hlb-Groep",
    "observed_at": "2026-11-07",
    "confidence": "secondary_discovery_only",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e10",
    "employer": "SMT Netherlands",
    "municipality": "Noordoostpolder",
    "official_career_url": "https://werkenbijsmt.nl/vacatures/",
    "evidence_url": "https://werkenbijsmt.nl/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e11",
    "employer": "Groothuisbouw",
    "municipality": "Noordoostpolder",
    "official_career_url": "https://www.groothuisbouw.nl/vacatures",
    "evidence_url": "https://www.groothuisbouw.nl/vacatures",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e12",
    "employer": "Gemeente Noordoostpolder",
    "municipality": "Noordoostpolder",
    "official_career_url": "https://www.noordoostpolder.nl/vacatures-gemeente-noordoostpolder",
    "evidence_url": "https://www.noordoostpolder.nl/vacatures-gemeente-noordoostpolder",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e13",
    "employer": "Sea Fresh",
    "municipality": "Urk",
    "official_career_url": "https://werkenbijseafresh.nl/vacatures/",
    "evidence_url": "https://werkenbijseafresh.nl/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e14",
    "employer": "Urker Zalmhuys",
    "municipality": "Urk",
    "official_career_url": "https://www.werkenbijzalmhuys.nl/",
    "evidence_url": "https://www.werkenbijzalmhuys.nl/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e15",
    "employer": "Neerlandia Urk",
    "municipality": "Urk",
    "official_career_url": "https://neerlandia.com/vacatures/",
    "evidence_url": "https://neerlandia.com/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e16",
    "employer": "Kramer Fish Group",
    "municipality": "Urk",
    "official_career_url": "https://kramerfish.nl/vacatures/",
    "evidence_url": "https://kramerfish.nl/vacatures/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e17",
    "employer": "Van Amersfoort Racing",
    "municipality": "Zeewolde",
    "official_career_url": "https://www.vanamersfoortracing.nl/careers/",
    "evidence_url": "https://www.vanamersfoortracing.nl/careers/",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e18",
    "employer": "Royal Herkel",
    "municipality": "Zeewolde",
    "official_career_url": "https://royalherkel.com/vacatures",
    "evidence_url": "https://royalherkel.com/vacatures",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  },
  {
    "candidate_id": "flv-e19",
    "employer": "Gemeente Zeewolde",
    "municipality": "Zeewolde",
    "official_career_url": "https://www.zeewolde.nl/werken-bij-de-gemeente",
    "evidence_url": "https://www.zeewolde.nl/werken-bij-de-gemeente",
    "observed_at": "2026-11-07",
    "confidence": "official_career_page_observed",
    "review_status": "candidate_not_integrated"
  }
]
```

### Opportunities (candidate schema v1)

```json
[
  {
    "candidate_id": "flv-v01",
    "employer": "Gemeente Almere",
    "municipality": "Almere",
    "title": "Stage: Meewerkstage team Recruitment",
    "evidence_url": "https://www.werkenbijalmere.nl/vacatures/stage-meewerkstage-team-recruitment-391873",
    "evidence_type": "official_vacancy_page",
    "deadline": "2026-11-10",
    "start": "2027-02",
    "priority": "urgent",
    "review_status": "official_vacancy_seen_application_unverified",
    "language_requirements": "unknown"
  },
  {
    "candidate_id": "flv-v02",
    "employer": "Provincie Flevoland",
    "municipality": "Lelystad",
    "title": "Stagiair HR van werving tot onboarding",
    "evidence_url": "https://flevoland.heeft-vacatures.com/vacatures/stagiair-hr-van-werving-tot-onboarding-1357003/",
    "evidence_type": "official_employer_recruitment_site",
    "deadline": "2026-11-29_or_30_unresolved",
    "start": null,
    "priority": "urgent",
    "review_status": "official_vacancy_seen_application_unverified",
    "language_requirements": "unknown"
  },
  {
    "candidate_id": "flv-v03",
    "employer": "SMT Netherlands",
    "municipality": "Noordoostpolder",
    "city": "Emmeloord",
    "title": "HR Stagiair(e)",
    "evidence_url": "https://werkenbijsmt.nl/vacature/hr-stagiaire/",
    "evidence_type": "official_vacancy_page",
    "deadline": null,
    "start": null,
    "priority": "high",
    "review_status": "official_vacancy_seen_application_unverified",
    "language_requirements": "Dutch_explicit"
  },
  {
    "candidate_id": "flv-v04",
    "employer": "Van Amersfoort Racing",
    "municipality": "Zeewolde",
    "title": "HR Stagiair",
    "evidence_url": "https://www.vanamersfoortracing.nl/careers/hr-stagiair/",
    "evidence_type": "official_vacancy_page",
    "deadline": null,
    "start": "2026-09_past",
    "priority": "review",
    "review_status": "past_start_not_on_current_careers_list_verify_before_publishing",
    "language_requirements": "Dutch_and_English_explicit"
  },
  {
    "candidate_id": "flv-v05",
    "employer": "Meerpaal",
    "municipality": "Dronten",
    "title": "Stagiair HR",
    "evidence_url": "https://www.meerpaal.nl/vacatures/stagiair-hr",
    "evidence_type": "official_vacancy_page",
    "deadline": "2026-10-15_past",
    "start": "2027_possible_but_deadline_past",
    "priority": "review",
    "review_status": "past_deadline_not_verified_open",
    "language_requirements": "unknown"
  },
  {
    "candidate_id": "flv-v06",
    "employer": "Marfo",
    "municipality": "Lelystad",
    "title": "HBO HR/Bedrijfskunde - Onderzoeksstage",
    "evidence_url": "https://baanlens.nl/vacature/marfo-hbo-hr-bedrijfskunde-onderzoeksstage-56250a5",
    "evidence_type": "secondary_aggregator",
    "deadline": "2026-11-17_per_secondary",
    "start": null,
    "priority": "review",
    "review_status": "secondary_only_absent_from_observed_official_vacancies",
    "language_requirements": "Dutch_and_English_per_secondary_unconfirmed"
  },
  {
    "candidate_id": "flv-v07",
    "employer": "HLB Group (HLB / De Groene Vlieg)",
    "municipality": "Dronten",
    "title": "Stagiair Organisatiecultuur & HR",
    "evidence_url": "https://nl.indeed.com/cmp/Hlb-Groep",
    "evidence_type": "secondary_aggregator",
    "deadline": null,
    "start": null,
    "priority": "review",
    "review_status": "secondary_only_official_vacancy_link_missing",
    "language_requirements": "unknown"
  }
]
```

## Ordine consigliato per il lavoro di Codex/Factory

1. Recuperare e proteggere **il lavoro Flevoland non committato** nel checkout originale; confrontare con main/branch/Issue prima di ripetere ricerche.
2. Verificare prioritariamente **Almere (scadenza 10/11)** e **Provincie Flevoland (29/30 novembre)**, poi SMT. Aprire il percorso di candidatura soltanto tramite link osservati e consentiti; classificare come verified esclusivamente se corrispondenza, disponibilità e requisiti di policy sono soddisfatti.
3. Controllare Marfo e HLB nella pagina ufficiale, senza accettare il solo aggregatore. Segnalare Meerpaal e VAR per date passate.
4. Confrontare tutti i datori con il registro globale e le fonti già configurate, riutilizzare ID, disambiguare gruppo/sede, verificare dimensioni da fonti probanti.
5. Eseguire scansioni delle fonti nei 6 comuni (nessuno zero-stage senza inventario completo). Se un adattatore non raggiunge l'intero inventario, mantenere partial/discovery-incomplete/blocked.
6. Preparare un rapporto con **fonti consultate, nuovi stage davvero verificati, canali completi, problemi e lavoro rimasto**. Non effettuare merge in main né introdurre nuove automazioni o costi.

## Note metodologiche
- Lo stato delle vacancy cambia: la presenza della pagina al 7 novembre non garantisce la candidabilità futura.
- Lingua dell'annuncio non equivale a lingua richiesta sul posto di lavoro.
- Non raccogliere dati personali, non inviare candidature, non aggirare CAPTCHA/robots.
- La geografia completa dovrà essere importata dall'API CBS versionata tramite importer condiviso; questa Issue non sostituisce l'import ufficiale.
- Il conteggio di 19 è **solo il lotto preliminare di fonti**, non copertura esaustiva.

Collegamento all'architettura: #8 — Provincial Factory v1.
