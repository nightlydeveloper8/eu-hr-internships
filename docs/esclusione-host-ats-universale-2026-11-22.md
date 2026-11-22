# Esclusione degli host SmartRecruiters e Ashby dal crawler universale

Base `dc72e6f` dopo #116. Audit sui report salvati del ciclo `2026-11-22T07:34:26.563397+00:00` e sul catalogo `2026-11-22T07:34:26.563397+00:00`. Nessuna raccolta mirata nuova. Le 17 fonti segnalate sommano **809 richieste contabilizzate per fonte** verso tutti gli host visitati e **31 righe di errore robots attribuibili ai due ATS**. Le richieste per singolo host non sono strumentate nei report disponibili. `n/d` significa dato non disponibile. I blocchi si contano dalle righe che citano robots e un host escluso nell’URL o nel messaggio. Sono un minimo osservabile, senza contare tentativi non emersi dai report del browser. Un errore HTTP 403 senza prova robots non rientra in questa colonna. I match HR del report possono includere più URL della stessa vacancy.

| Fonte | Richieste totali | Richieste agli ATS | Blocchi robots documentati | Match HR nel report | Schede dipendenti | Raccolta proposta |
| --- | ---: | --- | ---: | ---: | --- | --- |
| `auto-accor` | 48 | n/d | 0 | 3 | 1 chiuse | careers.accor.com |
| `auto-altarea` | 52 | n/d | 5 | 0 | 1 lead | Hold |
| `auto-avery-dennison` | 43 | n/d | 4 | 0 | 1 chiuse | Hold |
| `auto-bosch` | 61 | n/d | 0 | 1 | 2 lead | www.bosch.com |
| `auto-choco` | 4 | n/d | 1 | 0 | 0 | Hold |
| `auto-delta-electronics` | 40 | n/d | 2 | 0 | 0 | Hold |
| `auto-devoteam` | 88 | n/d | 4 | 0 | 1 chiuse | Hold |
| `auto-emidat` | 5 | n/d | 1 | 0 | 0 | Hold |
| `auto-interlogement-93` | 16 | n/d | 4 | 0 | 1 lead | Hold |
| `auto-jde-peet-s` | 94 | n/d | 0 | 3 | 3 lead | careers-nl.jdepeets.com |
| `auto-payrails` | 5 | n/d | 1 | 0 | 0 | Hold |
| `auto-reedsy` | 99 | n/d | 0 | 0 | 0 | Hold |
| `auto-salomon` | 69 | n/d | 0 | 2 | 3 lead | Hold |
| `auto-scoreplay` | 6 | n/d | 0 | 1 | 1 lead | Hold |
| `auto-sia` | 81 | n/d | 5 | 0 | 2 lead | Hold |
| `auto-smcp` | 88 | n/d | 4 | 0 | 1 lead | Hold |
| `auto-zefir` | 10 | n/d | 0 | 1 | 1 lead | Hold |

## Catalogo e comportamento proposto

Tra le 17 fonti e gli altri crawler universali che avevano già scoperto link a questi ATS, **22 record** dipendono da un URL vacancy o candidatura degli host esclusi: **0 aperti, 18 lead e 4 chiusi**. Oltre alle 17 fonti iniziali, ci sono schede storiche di SAP e Lesaffre. Gli URL dei record sono riportati per audit, senza nuove letture.

| Fonte | ID | Tipo | Stato | Annuncio |
| --- | --- | --- | --- | --- |
| `auto-accor` | `8669a06dbc5733f0698b` | internship | closed | [STAGE - Chargé(e) de Missions Ressources Humaines (Division Luxury Lifestyle & Orient Express) (F/M/X)](https://jobs.smartrecruiters.com/AccorCorpo/744000156510889-stage-charge-e-de-missions-ressources-humaines-division-luxury-lifestyle-orient-express-f-m-x-) |
| `auto-altarea` | `4f2b017b65bdf353078e` | internship | unverified | [Stage - Chargé de Projets - Développement RH - F/H](https://jobs.smartrecruiters.com/ALTAREA/744000156361909-stage-charge-de-projets-developpement-rh-f-h) |
| `auto-avery-dennison` | `c8fba8caa23dceacfb62` | internship | closed | [Internship: HR/Talent Acquisition & Employer Branding](https://jobs.smartrecruiters.com/AveryDennison/744000155814550-internship-hr-talent-acquisition-employer-branding) |
| `auto-bosch` | `7074bd65e78d1467e767` | internship | unverified | [Internship in Human Resources](https://jobs.smartrecruiters.com/BoschGroup/744000156530740-internship-in-human-resources-) |
| `auto-bosch` | `b2eb4368c94934767d21` | internship | unverified | [HR Internship (Administration, Training & Organization)](https://jobs.smartrecruiters.com/BoschGroup/744000155452020-hr-internship-administration-training-organization-) |
| `auto-devoteam` | `f7f6cb2ffbbdf07a0e48` | internship | closed | [Stage - Talent acquisition Specialist (H/F)](https://jobs.smartrecruiters.com/Devoteam/744000156731782-stage-talent-acquisition-specialist-h-f-) |
| `auto-interlogement-93` | `aa689cf2eabd61b43eb5` | internship | unverified | [Stage – Chargé·e de mission Développement RH](https://jobs.smartrecruiters.com/Interlogement93/744000152430750-stage-charge-e-de-mission-developpement-rh) |
| `auto-jde-peet-s` | `8cf3ff6ca1736f44247d` | internship | unverified | [Supply Chain HR Intern](https://jobs.smartrecruiters.com/JACOBSDOUWEEGBERTS/744000158480949-supply-chain-hr-intern) |
| `auto-jde-peet-s` | `b1028667f93844376544` | internship | unverified | [Internship/Stage Human Resources](https://jobs.smartrecruiters.com/JACOBSDOUWEEGBERTS/744000155017321-internship-stage-human-resources) |
| `auto-jde-peet-s` | `edd67b52f57d5ecfbd64` | internship | unverified | [Stage - Assistant(e) Ressources Humaines &#124; L’Or - Senseo – Tassimo](https://jobs.smartrecruiters.com/JACOBSDOUWEEGBERTS/744000159652250-stage-assistant-e-ressources-humaines-l-or-senseo-tassimo) |
| `auto-lesaffre` | `5c7577709116ec76c01d` | internship | unverified | [Stage 6 mois – Chargé(e) de projet automatisation IA pour les RH](https://jobs.smartrecruiters.com/Lesaffre/744000159915194-stage-6-mois-charge-e-de-projet-automatisation-ia-pour-les-rh-) |
| `auto-lesaffre` | `a036f3b2573251f46039` | internship | unverified | [Stage 6 mois – Chargé(e) de projet automatisation IA pour les RH](https://jobs.smartrecruiters.com/Lesaffre/744000160142259-stage-6-mois-charge-e-de-projet-automatisation-ia-pour-les-rh-) |
| `auto-salomon` | `63f811377cc21a394b32` | internship | unverified | [STAGE - Assistant(e) RH Généraliste (M/F/X)](https://jobs.smartrecruiters.com/Salomon/744000154123609-stage-assistant-e-rh-generaliste-m-f-x-) |
| `auto-salomon` | `766e672335d752d22711` | internship | unverified | [STAGE - Assistant(e) RH Généraliste (M/F/X)](https://jobs.smartrecruiters.com/Salomon/744000161490861-stage-assistant-e-rh-generaliste-m-f-x-) |
| `auto-salomon` | `9ec84dcf8cd7d8d98604` | internship | unverified | [STAGE – Employee Experience Assistant M/F/X](https://jobs.smartrecruiters.com/Salomon/744000161266375-stage-employee-experience-assistant-m-f-x) |
| `auto-sap` | `123717106021372a7704` | internship | closed | [SAP iXp Intern - Employer Brand Coordinator (limited part-time)](https://jobs.smartrecruiters.com/SAPITBusinessSysteme/744000158445999-sap-ixp-intern-employer-brand-coordinator-limited-part-time-) |
| `auto-sap` | `58700c661abc1d9f7e6c` | internship | unverified | [SAP iXp Intern – Tech Recruitment (limited contract)](https://jobs.smartrecruiters.com/SAPITBusinessSysteme/744000159389405-sap-ixp-intern-tech-recruitment-limited-contract-) |
| `auto-scoreplay` | `e284f2c837a26b71fbfe` | internship | unverified | [People Ops (HR & Recruitment) - Intern](https://jobs.ashbyhq.com/scoreplay/2b9ef38c-01b0-468f-b66c-eee5fdedc6bd) |
| `auto-sia` | `26e31dee42d5856440c9` | internship | unverified | [Stage – Consultant junior RH & Assessment](https://jobs.smartrecruiters.com/Sia/744000152226940-stage-consultant-junior-rh-assessment) |
| `auto-sia` | `44eb795a273b9ee0c6f8` | internship | unverified | [Final Year Internship Consultant - HR & Transformation](https://jobs.smartrecruiters.com/Sia/744000159655534-final-year-internship-consultant-hr-transformation) |
| `auto-smcp` | `61996388552eb3f33953` | internship | unverified | [(Janvier 2027) - Stage RH - Chargé(e) de recrutement - H/F](https://jobs.smartrecruiters.com/SMCP/744000150973440--janvier-2027-stage-rh-charge-e-de-recrutement-h-f) |
| `auto-zefir` | `b0b844cc55b42a6f547b` | internship | unverified | [Talent Acquisition Intern](https://jobs.ashbyhq.com/zefir/020d001f-d716-494e-aa99-3a7335360518) |

La configurazione conserva tre partenze su host careers propri, Bosch, JDE Peet’s e Accor. Le altre 14 fonti hanno hold sul datore e sulla fonte, senza URL di partenza ammessi nel registro. Il provisioning ignora URL esclusi anche quando sono l'unica destinazione registrata di un nuovo datore. Conservare l'URL storico come evidenza nel registro datori non lo rende un seed di raccolta. I collector attivi passano da **1.937 dopo #116 a 1.923** nella proposta.

Il controllo vale anche per discovery, checkpoint, feed, redirect HTTP, browser e verifica del modulo. Il browser in modalità universale rifiuta le risposte con redirect anziché lasciarle seguire automaticamente, perché Chromium può saltare l'intercettore nelle catene di redirect. Questo può ridurre il rendering su siti che ne dipendono. Il trasporto HTTP ordinario continua a seguire redirect ammessi, sotto robots. Le prove offline coprono questi ingressi e i link di ricordato inventario.

I record restano nel catalogo e seguono le regole ordinarie di freschezza e scadenza. Un URL escluso non può contare come assente da un inventario completo dell'host proprio. Gli ID possono essere riconciliati con una futura prova ammessa della stessa vacancy. Il catalogo versionato non è modificato. Finalizzazione offline sul catalogo corrente senza nuove osservazioni: **913 → 913 ID, zero persi**.

## Da decidere separatamente: Recruitee JSON e Amazon Jobs

**Recruitee.** Dal **10 febbraio 2027**, il provider annuncia HTTP 401 senza token per gli endpoint Careers Site API documentati, incluso `/offers`. L’eccezione riguarda XML e widget. I 32 feed attivi qui sotto sono da verificare individualmente, in particolare su host personalizzati. Proposta: migrare ai feed XML pubblici quando il tenant li pubblica e termini, robots, ID e modulo sono verificati. Se XML manca, rivedere il percorso pubblico o mettere la fonte in hold con autorizzazione separata. Conservare gli ID e non usare assenze da un feed incompleto per chiudere. Nessuna richiesta o modifica ai 32 feed in questa PR. [Documentazione Recruitee](https://docs.recruitee.com/reference/authentication-1)

| Fonte attiva | Feed consultato oggi |
| --- | --- |
| `auto-alliade` | `https://alliade.recruitee.com/api/offers/` |
| `auto-buko-infrasupport-b-v` | `https://bukoinfrasupport.recruitee.com/api/offers/` |
| `auto-ennatuurlijk` | `https://ennatuurlijkbv.recruitee.com/api/offers/` |
| `auto-haitsma-beton` | `https://ballastnedam.recruitee.com/api/offers/` |
| `auto-hogeschool-van-hall-larenstein` | `https://werkenbij.hvhl.nl/api/offers/` |
| `auto-intergas-verwarming-b-v` | `https://intergas.recruitee.com/api/offers/` |
| `auto-isero` | `https://werkenbijisero.nl/api/offers/` |
| `auto-koninklijke-remia-c-v` | `https://remiacv.recruitee.com/api/offers/` |
| `auto-nts-norma` | `https://nts.recruitee.com/api/offers/` |
| `auto-sw-vastgoedverbetering` | `https://werkenbij.swbv.nl/api/offers/` |
| `auto-trunkrs` | `https://werkenbij.trunkrs.nl/api/offers/` |
| `auto-wagenborg-passagiersdiensten` | `https://royalwagenborg1.recruitee.com/api/offers/` |
| `auto-wajer-yachts` | `https://werkenbijwajer.nl/api/offers/` |
| `recruitee-batch-abrio` | `https://abriogmbh.recruitee.com/api/offers/` |
| `recruitee-batch-chr-haute-senne` | `https://chrhautesenne.recruitee.com/api/offers/` |
| `recruitee-batch-vigo-groep` | `https://werkenbijvigogroep.recruitee.com/api/offers/` |
| `recruitee-bundl` | `https://bundl.recruitee.com/api/offers/` |
| `recruitee-dienst-dommelvallei` | `https://dommelvallei.recruitee.com/api/offers/` |
| `recruitee-edco` | `https://werkenbijedco.recruitee.com/api/offers/` |
| `recruitee-focus-entertainment` | `https://focushomeinteractive.recruitee.com/api/offers/` |
| `recruitee-franklin-institute` | `https://franklininstitute.recruitee.com/api/offers/` |
| `recruitee-gerard-bertrand` | `https://gerardbertrand.recruitee.com/api/offers/` |
| `recruitee-hotel-twentyseven` | `https://hoteltwentyseven.recruitee.com/api/offers/` |
| `recruitee-ibexa` | `https://ibexa.recruitee.com/api/offers/` |
| `recruitee-monsterscore` | `https://monsterscore.recruitee.com/api/offers/` |
| `recruitee-multifix` | `https://werkenbijmultifix.nl/api/offers/` |
| `recruitee-protiviti-gmbh` | `https://protiviti.recruitee.com/api/offers/` |
| `recruitee-psv` | `https://psv.recruitee.com/api/offers/` |
| `recruitee-sas-look-up-space` | `https://lookup.recruitee.com/api/offers/` |
| `recruitee-skytree` | `https://skytree.recruitee.com/api/offers/` |
| `recruitee-social-deal-b-v` | `https://werk.socialdeal.nl/api/offers/` |
| `recruitee-veldsink-groep` | `https://werkenbijveldsinkgroep.nl/api/offers/` |

**Amazon Jobs.** `amazon-hr-internships` è parziale nel ciclo osservato: 92 tentativi contati, 1,657,515 byte, 120.66 s, 30 match HR. Nel catalogo ci sono 0 aperti, 30 lead e 4 chiusi attribuiti alla fonte. Il progetto ha documentato risposte robots 403; il sito careers rimanda alle condizioni generali Amazon, il cui perimetro per le richieste automatiche di recruiting resta da chiarire. Nessuna scadenza tecnica analoga è emersa dai documenti esaminati. Proposta: review separata di termini e robots sugli endpoint effettivi, poi decidere se mantenere solo percorsi ammessi o sospendere questa fonte e conservare lo storico. [Rinvio dai termini Amazon Jobs](https://www.amazon.jobs/en-gb/privacy_page?notice_id=us-conditions-english&region_id=region_us)
