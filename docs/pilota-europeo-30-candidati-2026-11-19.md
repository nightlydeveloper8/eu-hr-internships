# Pilota 30 candidati HR in cinque mercati — 19 novembre 2026

Lotto bilanciato di sei candidati per Italia, Svizzera, Svezia, Polonia e Regno Unito. Sono stati incrociati annunci pubblici con datore noto e risultati di ricerca dei datori. La selezione è intenzionale, con più candidature su alcuni datori per riconoscere problemi e percorsi riusabili. Il risultato vale per il campione. Nessuna campagna sull'intero inventario, nessun POST, rendering o invio.

| Paese | Candidati | Tentati live | Pagine ufficiali riconfermate nel primo passaggio | Richieste iniziali + follow-up |
| --- | ---: | ---: | ---: | ---: |
| Italia | 6 | 6 | 3 | 9 + 0 |
| Svizzera | 6 | 4 | 3 | 9 + 4 |
| Svezia | 6 | 5 | 4 | 12 + 0 |
| Polonia | 6 | 6 | 3 | 12 + 4 |
| Regno Unito | 6 | 6 | 4 | 13 + 4 |

**Esito**. 30 candidati, 28 piste su domini datoriali o ATS, 27 letture di candidati nel primo passaggio e 17 pagine ufficiali riconfermate, incluse quelle poi fermate sulla sede o sulla candidatura. **0 nuove candidature confermate**. Jobandtalent mantiene la prova precedente del 19 novembre e rimane in attesa di riconciliazione con la copia pubblica `c8bdac2ae98420d4b1e7`. Spital Muri e UCC Coffee sono indizi con datore identificato, senza un URL datore specifico trovato. Totale **67 GET**, **3.521.275 B**. Le due esecuzioni isolate si sono concluse con successo. [Lotto](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44602944560) · [Approfondimento CTA](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44603288396) · [Prova precedente Jobandtalent](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44600388534).

Nei quattro link di candidatura indicati dagli employer con lo stesso ID, la verifica successiva ha osservato:

- **Danone PL**: passaggio verso una pagina `/login` iCIMS vietata da robots.txt. Nessuna richiesta alla pagina vietata.
- **Psychiatrie St.Gallen CH**: il link di Prospective ha prodotto un redirect oltre lo scope ammesso. Identità e modulo a destinazione rimangono da verificare.
- **L’Oréal GB**, due annunci distinti: il primo link ha restituito HTTP 403. Per il secondo, il pilota ha rispettato il blocco dell’host e non ha ritentato. Barclays aveva già un link same-ID nel primo passaggio, senza prova del modulo in HTML.
- **Suzuki SE**: il datore pubblica un link Varbi per la stessa vacancy. Il controllo non ha trovato un modulo abilitato. Il ruolo combina pratica ed extrajobb e richiede una verifica di eleggibilità curriculare.
- **Teamtailor SE**: Hemfrid e Veterankraft hanno pagine correnti, con percorso di candidatura non stabilito dal controllo HTML. Tacting ha risposto 410. Servono segnali pubblicati dal sito o prove tecniche consentite prima di espandere la famiglia.

## Registro del primo passaggio

| Paese | Datore | ID selezionato | Candidato | Esito |
| --- | --- | --- | --- | --- |
| IT | [Gi Group](https://it.gigroupholding.com/entra-nel-nostro-team/offerte-lavoro/lavoro/?id=A1775) | `A1775` | HR CONSULTANT | percorso di candidatura non stabilito |
| IT | [Gi Group](https://it.gigroupholding.com/entra-nel-nostro-team/offerte-lavoro/lavoro/?id=A1705) | `A1705` | TIROCINIO AMBITO RISORSE UMANE | percorso di candidatura non stabilito |
| IT | [Gi Group](https://careers.gigroupholding.it/job/view-job.php?id=1696-stage-hr-training-compliance-milano&language=it) | `1696` | STAGE HR TRAINING | pagina corrente della vacancy non confermata (Current employer page does not establish the selected vacancy title) |
| IT | [Gi Group](https://careers.gigroupholding.it/job/view-job.php?id=1700-stage-risorse-umane-reggio-emilia&language=it) | `1700` | STAGE RISORSE UMANE | pagina corrente della vacancy non confermata (Current employer page does not establish the selected vacancy title) |
| IT | [Gi Group](https://careers.gigroupholding.it/job/view-job.php?id=1760-stage-data-analyst-%3F-candidate-recruiting-milano&language=it) | `1760` | STAGE DATA ANALYST | pagina corrente della vacancy non confermata (Current employer page does not establish the selected vacancy title) |
| IT | [Synergie Italia](https://www.synergie-italia.it/candidato/offerte-di-lavoro/stage-hr-recruiter-365387) | `365387` | STAGE HR RECRUITER | percorso di candidatura non stabilito |
| CH | [Hôpitaux Universitaires de Genève](https://jobs.smartrecruiters.com/HUG/744000161747261-stagiaire-rh-conventionne-80-a-100-) | `744000161747261` | Stagiaire RH conventionné | percorso di candidatura non stabilito |
| CH | [Teoxane](https://careers.teoxane.com/job/Gen%C3%A8ve-Stagiaire-RH-L&D-1203/1376925555/) | `1376925555` | Stagiaire RH L&D | accesso limitato (robots.txt disallows https://careers.teoxane.com/talentcommunity/apply/1376925555?locale=en_US) |
| CH | [Psychiatrie St.Gallen](https://jobs.psychiatrie-sg.ch/karriere/offene-stellen/praktikantin-praktikant-hr/65899175-cde2-4b93-98d7-680977fd7f91) | `65899175-cde2-4b93-98d7-680977fd7f91` | Praktikantin / Praktikant HR | percorso di candidatura non stabilito |
| CH | [OK Job](https://www.okjob.ch/offres-demplois/offre-de-stage-assistante-en-recrutement-ressources-humaines-h-f-geneve/) | `500a08eb54a507a9d62f` | Assistante en recrutement | pagina corrente della vacancy non confermata (HTTP Error 404: Not Found) |
| CH | Spital Muri | `2cd2456c52da3ef0c1e5` | HR Praktikantin/Praktikant (befristet 12 Monate) | link del datore non trovato |
| CH | UCC Coffee | `c0a0a523b16dfecfb128` | Praktikant/in Human Resources & Marketing | link del datore non trovato |
| SE | [Jobandtalent Sweden](https://jobb.jobandtalent.com/jobs/8503489-praktik-inom-hr-och-rekrytering-i-malmo-varen-2027) | `8503489` | Praktik inom HR och rekrytering i Malmö | prova precedente positiva, riconciliazione da fare |
| SE | [Suzuki Garphyttan](https://www.suzuki-garphyttan.com/career/suzuki-garphyttan-soker-en-personalvetarstudent-for-extrajobb-och-praktik/) | `989715` | Suzuki Garphyttan söker en Personalvetarstudent | link same-ID, modulo non dimostrato |
| SE | [Bosch Thermoteknik](https://jobs.smartrecruiters.com/BoschGroup/744000156530019-internship-in-human-resources-) | `744000156530019` | Internship in Human Resources | percorso di candidatura non stabilito |
| SE | [Hemfrid](https://karriar.hemfrid.se/jobs/8492243-praktik-inom-rekrytering-hr-administration-vt2027) | `8492243` | Praktik inom rekrytering & HR-administration | percorso di candidatura non stabilito |
| SE | [Veterankraft](https://veterankraftab.teamtailor.com/jobs/8760668-praktik-inom-rekrytering-varterminen-2027) | `8760668` | Praktik inom rekrytering | percorso di candidatura non stabilito |
| SE | [Tacting](https://tacting.teamtailor.com/jobs/8621469-praktikplats-inom-rekrytering-hr-tacting-2027) | `8621469` | Praktikplats inom Rekrytering & HR | pagina corrente della vacancy non confermata (HTTP Error 410: Gone) |
| PL | [Align Technology](https://jobs.aligntech.com/postings/313446dd-471f-4fa0-83d2-be3f992e314a) | `313446dd-471f-4fa0-83d2-be3f992e314a` | Staż w dziale HR | pagina corrente della vacancy non confermata (Redirect does not retain the selected vacancy) |
| PL | [Danone](https://careers.danone.com/en-global/jobs/internship-program-danone-in-talent-acquisition-team-29170-en-us.html) | `29170` | Internship Program DanOne in Talent Acquisition Team | percorso di candidatura non stabilito |
| PL | [SEB](https://sebgroup.com/career/find-your-new-job/our-vacant-positions/internship-in-hr-department-486931a5-6fa2-4e4f-8fb8-6092c1ccec81) | `486931a5-6fa2-4e4f-8fb8-6092c1ccec81` | Internship in HR department | percorso di candidatura non stabilito |
| PL | [Roche](https://careers.roche.com/global/en/job/202610-125165/HR-Administrative-Support-Intern) | `202610-125165` | HR & Administrative Support Intern | sede non confermata dal pilota |
| PL | [Siemens Energy](https://jobs.siemens-energy.com/en_US/jobs/FolderDetail/HR-Intern-f-m-d/297869) | `297869` | HR Intern | pagina corrente della vacancy non confermata (HTTP Error 404: Not Found) |
| PL | [Schneider Electric](https://careers.se.com/jobs/134893?lang=en-us&previousLocale=en-US) | `134893` | Internship in People Technology | accesso limitato (robots.txt unavailable: 403) |
| GB | [Barclays](https://search.jobs.barclays/en/job/london/2027-human-resources-industrial-placement-programme-london/13015/100411085408) | `100411085408` | 2027 Human Resources Industrial Placement Programme London | link same-ID, modulo non dimostrato |
| GB | [L’Oréal](https://careers.loreal.com/en/job/london/human-resources-summer-intern-london/3456/46997800064) | `46997800064` | Human Resources Summer Intern | percorso di candidatura non stabilito |
| GB | [L’Oréal](https://careers.loreal.com/en/job/london/rewards-industrial-placement-2027-human-resources-6-months/3456/46795487872) | `46795487872` | Rewards Industrial Placement 2027 | percorso di candidatura non stabilito |
| GB | [GSK](https://jobs.gsk.com/be/en/job/445702/HR-Multiple-Roles-Industrial-Placement-2027) | `445702` | HR (Multiple Roles) Industrial Placement | sede non confermata dal pilota |
| GB | [Pernod Ricard](https://pernodricard.wd3.myworkdayjobs.com/pernod-ricard/job/London/Human-Resources--HR--Placement_JR-055444) | `JR-055444` | Human Resources (HR) Placement | pagina corrente della vacancy non confermata (Current employer page does not establish the selected vacancy title) |
| GB | [Unilever](https://unilever.wd3.myworkdayjobs.com/en-US/Unilever_Early_Careers/job/Unilever-Industrial-Placement-Programme---Human-Resources---UK_R-1188297) | `R-1188297` | Unilever Industrial Placement Programme - Human Resources | pagina corrente della vacancy non confermata (Current employer page does not establish the selected vacancy title) |

## Conseguenze per la strategia 100

Il tasso del lotto è 0/30 per nuove conferme. Il 25% usato nel calcolo di scenario resta un'ipotesi. Il prossimo lotto va selezionato sulla prova preliminare del percorso ufficiale: portale e identificativo già leggibili, candidatura pubblicata per l'ID esatto, accesso entro host, robots e budget. Misurare separatamente quante fonti arrivano a quel prerequisito e quante arrivano al modulo. La prima priorità tecnica rimane collegare Jobandtalent al catalogo già esistente e poi provare in due paesi le famiglie con accesso leggibile. L'incremento eventuale di candidature distinte è separato dagli annunci già elencati dai servizi pubblici.

Stato di produzione alla fine del lotto: `main` su `3f20f51`, 33 candidature confermate, 365 annunci pubblici attivi, nessuna fonte abilitata da questo lavoro. Workflow temporanei eliminati dal ramo.
