# Migrazione sitemap — replay delle correzioni del 25 novembre 2026

Replay isolato su `a2274be`. **589 → 642 stage visibili**, 1170 ID iniziali tutti conservati. La stima di **26m02s** aggiunge 240 s di budget sullo shard più carico ai 22m02s del [ciclo di riferimento](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45661154805), mantenendo i vecchi crawler. Nessun tempo reale di produzione per la configurazione candidata.

Il gate si ferma sui dettagli validi che restano senza prova completa. Adecco ha un titolo HR in sitemap con paese mancante e identità societaria irrisolta, Infineon ha un dettaglio senza markup utile e Randstad resta lead. Nessuna apertura PR o modifica in produzione. La disattivazione di fonti generiche è subordinata al publish di questo lotto.

## Diagnosi per piattaforma

| Piattaforma | Host | Annuncio campione | Passaggio | Aperti prima → dopo |
|---|---|---|---|---:|
| Radancy / TalentBrew | careers.loreal.com | [Praktikum HR – Personalentwicklung, Ausbildung & Betriebliches Gesundheitsmanagement](https://careers.loreal.com/en/job/muggensturm/praktikum-hr-personalentwicklung-ausbildung-and-betriebliches-gesundheitsmanagement-m-w-d-ab-april-/3456/44773515328) | Idoneità e riferimento di candidatura. Il titolo descrive funzioni HR e la CTA riporta lo stesso ID. Recuperato. | 0 → 12 |
| Radancy / TalentBrew | careers.ing.com | [Internship – HR Operations](https://careers.ing.com/en/job/luxembourg/internship-hr-operations/3121/38478345920) | Riferimento Workday. La CTA incorpora la requisizione REQ-10115027. Recuperato. | 0 → 5 |
| Radancy / TalentBrew | careers.adeccogroup.com | [Chargé de recrutement stagiaire](https://careers.adeccogroup.com/en/job/toulouse/charge-de-recrutement-stagiaire-h-f/26094/96160244880) | HTTP 200 e JSON-LD. Paese vuoto e organizzazione DO SUD non riconciliata. Il budget termina prima dei dettagli di tutti i 128 candidati. | 0 → 0 |
| Workflow sul sito employer | careers.accor.com | [Stage Ressources Humaines – Sofitel Paris Arc de Triomphe](https://careers.accor.com/global/en/job/stage-ressources-humaines-a-partir-de-janvier-2027-6-mois-h-f-in-sofitel-paris-arc-de-triomphe-paris-france-jid-49270) | Il paese era nel campo località. Il workflow ufficiale espone il medesimo vacancyId del canonical. Recuperato. | 0 → 6 |
| Next.js / Workday | www.asml.com | [Human Resource Management & Business Administration internship](https://www.asml.com/en/careers/find-your-job/human-resource-management--business-administration-internship-onboarding-operations-improvement-j00355161) | JSON-LD assente. Lo stato pubblico Next.js dichiara vacancy aperta, sede e requisizione della CTA Workday. Recuperato. | 0 → 3 |
| SuccessFactors RMK | careers.knorr-bremse.com | [Mandatory Internship Global HR Team](https://careers.knorr-bremse.com/job/M%C3%BCnchen-Mandatory-Internship-Global-HR-Team-%28mfd%29-80809/1457013233/) | Microdati senza titolo. Metadati coerenti, indirizzo esplicito e CTA RMK con lo stesso ID. Recuperato. | 0 → 2 |
| SuccessFactors RMK | jobs.pirelli.com | [Praktikum / Abschlussarbeit Recruiting](https://jobs.pirelli.com/job/Breuberg-Praktikum-Abschlussarbeit-Recruiting/531457401/) | HTTP 302 verso il dettaglio, poi markup senza paese esplicito e CTA generica. Nessuna promozione. | 0 → 0 |
| Eightfold | jobs.infineon.com | [Praktikum Global Talent Marketing & Employer Branding](https://jobs.infineon.com/careers/job/563808972330858-praktikum-global-talent-marketing-and-employer-branding-f-m-div--munich?domain=infineon.com) | HTTP 200 del dettaglio pubblico, senza JobPosting utile. Nessuna promozione. | 0 → 0 |
| Phenom | careers.abb | [Student Internship – HR Intern with French](https://careers.abb/global/en/job/JR00054047/Student-Internship-HR-Intern-with-French) | HTTP 200 e JSON-LD residuo, ma la pagina dichiara esplicitamente l’annuncio non disponibile. | 0 → 0 |
| Phenom | join.pmicareers.com | [People and Culture Intern – Social Media & Digital Marketing](https://join.pmicareers.com/earlycareers/gb/en/job/33661/People-and-Culture-Intern-Social-Media-Digital-Marketing) | La sitemap del sito in inglese porta a un annuncio in Indonesia. Nessun campione europeo dimostrato e 18 mappe pendenti. | 0 → 0 |
| Phenom | jobs.kuehne-nagel.com | [Human Resources Intern](https://jobs.kuehne-nagel.com/belux/nl/job/20766/Human-Resources-Intern) | La sitemap del sito Belux porta a un annuncio in Messico. Nessun campione europeo dimostrato e 10 mappe pendenti. | 0 → 0 |
| Sito proprio | www.werkenbijrandstad.nl | [Stage recruitment en HR](https://www.werkenbijrandstad.nl/vacature/1814/stage-recruitment-en-hr) | Luogo NL, titolo e JSON-LD validi. La CTA punta a un’ancora senza modulo nel documento statico. Resta lead. | 0 → 0 |

## Bosch

**jobs.bosch.de 0 → 25**. Tutti i 25 candidati HR del replay sono current listing. Il layout pubblico collega UUID del dettaglio, società, stato online, ID ATS e CTA, e conserva la sottosocietà sotto Bosch. Nessuna richiesta ai percorsi SmartRecruiters. **jobs.bosch.com 0 → 0** dopo robots e undici sitemap. Il layout è configurato in hold per entrambi gli host. La [nota legale Bosch](https://jobs.bosch.com/de/rechtliche-hinweise/) limita il riuso commerciale. Il replay locale conserva solo i metadati essenziali.

## Paesi

AT 9 → 9, BE 27 → 27, CH 23 → 23, CZ 1 → 1, DE 77 → 111, ES 34 → 35, FI 1 → 1, FR 49 → 60, GB 1 → 2, HU 3 → 3, IT 113 → 113, LU 1 → 3, NL 232 → 236, PL 10 → 10, PT 2 → 2, SE 6 → 6. Altri paesi 0 → 0.

## Titoli nuovi o appena verificati

| Paese | Stato nel replay | Titolo | ID |
|---|---|---|---|
| DE | current listing, nuovo ID | [Mandatory Internship Global HR Team (m/f/d)](https://careers.knorr-bremse.com/job/M%C3%BCnchen-Mandatory-Internship-Global-HR-Team-%28mfd%29-80809/1457013233) | `126961d11f85554d7a3d` |
| DE | current listing, nuovo ID | [Pflichtpraktikant global HR-Team (m/w/d)](https://careers.knorr-bremse.com/job/M%C3%BCnchen-Pflichtpraktikant-global-HR-Team-%28mwd%29-80809/1457013333) | `5626ec93e44f76716ee2` |
| DE | current listing, nuovo ID | [Pflichtpraktikum Assistenz Werkleitung & Organisationsentwicklung](https://jobs.bosch.de/job/Pflichtpraktikum-Assistenz-Werkleitung-Organisationsentwicklung-Schweinfurt?id=2c40cd52-2570-4dc5-a6c9-72781e098fcb) | `e9bd3b44af2e9434aeaa` |
| DE | current listing, nuovo ID | [Pflichtpraktikum HR Administration / Personalbetreuung](https://jobs.bosch.de/job/Pflichtpraktikum-HR-Administration-_-Personalbetreuung-Muenchen-Neuperlach?id=1b68bac6-8b38-4329-9f26-e8a422d8cef9) | `2a6c9fb8dffe69022fd9` |
| DE | current listing, nuovo ID | [Pflichtpraktikum HR Digital Content Management](https://jobs.bosch.de/job/Pflichtpraktikum-HR-Digital-Content-Management-Gerlingen-Schillerhoehe?id=9695ea61-2f7b-451a-b136-95f9966b6a19) | `0911d6c20d255cd8a9d8` |
| DE | current listing, nuovo ID | [Pflichtpraktikum HR People & Culture - Personalentwicklung](https://jobs.bosch.de/job/Pflichtpraktikum-HR-People-Culture-Personalentwicklung-Schweinfurt?id=d12d8008-b302-4da6-aba8-ae94c9217f28) | `c55016ab7e9a904d0fe7` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im Bereich Human Resources](https://jobs.bosch.de/job/Pflichtpraktikum-im-Bereich-Human-Resources-Stuttgart-Feuerbach?id=f59a8f17-ba42-437c-8dae-fd8b4fa578cd) | `2e5d7a31110bca5fe6ba` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im Bereich Human Resources](https://jobs.bosch.de/job/Pflichtpraktikum-im-Bereich-Human-Resources-Renningen?id=8046a588-fe0a-433b-b4fa-072d6391d9bf) | `b2a237c5e90c8ad141df` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im Bereich International Human Resources](https://jobs.bosch.de/job/Pflichtpraktikum-im-Bereich-International-Human-Resources-Abstatt-bei-Stuttgart?id=d7c654bd-a8af-4a26-9dc4-17b126328a8b) | `fa798b90fcf21741021d` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im Bereich International Human Resources und HR Strategy](https://jobs.bosch.de/job/Pflichtpraktikum-im-Bereich-International-Human-Resources-und-HR-Strategy-Abstatt-bei-Stuttgart?id=e88ea062-5397-4487-95ef-006ea4a03684) | `6c4795095ee829cd8fb5` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im HR- Service Deutschland](https://jobs.bosch.de/job/Pflichtpraktikum-im-HR-Service-Deutschland-Gerlingen?id=63553fe7-2d41-479a-9e78-c0fe485f5e25) | `9d8ca7c1033ff1502a45` |
| DE | current listing, nuovo ID | [Pflichtpraktikum im internationalen Personalwesen - Human Resources](https://jobs.bosch.de/job/Pflichtpraktikum-im-internationalen-Personalwesen-Human-Resources-Leonberg?id=00071e8d-f484-4910-abfe-244353c76899) | `ac266df76e0f88ab0bb3` |
| DE | current listing, nuovo ID | [Pflichtpraktikum in der Personalabteilung (m/w/div.)](https://jobs.bosch.de/job/Pflichtpraktikum-in-der-Personalabteilung-m_w_div.-Waiblingen-Alte-Bundesstrasse?id=e3162597-e66d-4074-a1f7-cdaeacc9ac23) | `0294da9661d60402d251` |
| DE | current listing, nuovo ID | [Pflichtpraktikum in der Personalabteilung - Gesundheit- und DEI-Management](https://jobs.bosch.de/job/Pflichtpraktikum-in-der-Personalabteilung-Gesundheit-und-DEI-Management-Stuttgart-Feuerbach?id=674e0351-62ed-40ec-8f95-89a80f5eec43) | `b5182017b42593cd52d2` |
| DE | current listing, nuovo ID | [Pflichtpraktikum in der Personalabteilung – Aus- und Weiterbildung](https://jobs.bosch.de/job/Pflichtpraktikum-in-der-Personalabteilung-%E2%80%93-Aus-und-Weiterbildung-Schweinfurt?id=fd9d524b-ccdb-4f9f-8f96-eae985430adf) | `a147d434f95c97044bfd` |
| DE | current listing, nuovo ID | [Pflichtpraktikum in Human Resources bei Bosch Global Real Estate](https://jobs.bosch.de/job/Pflichtpraktikum-in-Human-Resources-bei-Bosch-Global-Real-Estate-Gerlingen-Schillerhoehe?id=7859f55e-2e41-48fe-958f-0b467f8e0ee6) | `c0c3925427c51baedd4a` |
| DE | current listing, ID conservato | [Praktikant Human Resources – Knowledge Management (w/m/d)](https://careers.ing.com/en/job/frankfurt-am-main/praktikant-human-resources-knowledge-management-w-m-d/3121/46679847040) | `2a1be644a716df5d480e` |
| DE | current listing, ID conservato | [Praktikant Human Resources – Young Talents (w/m/d)](https://careers.ing.com/en/job/frankfurt-am-main/praktikant-human-resources-young-talents-w-m-d/3121/46391158464) | `bc87f454af5b4f8de64c` |
| DE | current listing, ID conservato | [Praktikant Payroll (m/w/d)](https://careers.ing.com/en/job/frankfurt-am-main/praktikant-payroll-m-w-d/3121/46286546624) | `1e75a57690445a3a4346` |
| DE | current listing, nuovo ID | [PRAKTIKUM (M/W/D) HR Business Partner ab März 2027](https://careers.loreal.com/en/job/dusseldorf/praktikum-m-w-d-hr-business-partner-ab-marz-2027/3456/43955561408) | `1cc8002a42523a9b253c` |
| DE | current listing, ID conservato | [Praktikum (m/w/d) Human Resources bei L‘Oréal Luxe in Mönchengladbach – ab November 2026](https://careers.loreal.com/en/job/monchengladbach/praktikum-m-w-d-human-resources-bei-l-oreal-luxe-in-monchengladbach-ab-november-2026/3456/44834322624) | `85b674dbf0ae7701a850` |
| DE | current listing, nuovo ID | [Praktikum HR Betreuung und Talent Attraction](https://jobs.bosch.de/job/Praktikum-HR-Betreuung-und-Talent-Attraction-Lohr-am-Main?id=1e5129b6-0cdd-478b-8dc6-ba3c2b184de2) | `07052a16d10336b181bf` |
| DE | current listing, ID conservato | [Praktikum HR: Personalentwicklung, Ausbildung & Betriebliches Gesundheitsmanagement (m/w/d) - ab April 2027](https://careers.loreal.com/en/job/muggensturm/praktikum-hr-personalentwicklung-ausbildung-and-betriebliches-gesundheitsmanagement-m-w-d-ab-april-/3456/44773515328) | `6f7abf37b7bf09d0a4f6` |
| DE | current listing, ID conservato | [Praktikum Human Resources (m/w/d) - Start: Februar/März 2027](https://careers.loreal.com/en/job/karlsruhe/praktikum-human-resources-m-w-d-start-februar-marz-2027/3456/42700046976) | `f04e3dbc13b626f2217b` |
| DE | current listing, nuovo ID | [Praktikum im Bereich HR-Recruiting und Talent Attraction](https://jobs.bosch.de/job/Praktikum-im-Bereich-HR-Recruiting-und-Talent-Attraction-Lohr-am-Main?id=1f3eaf30-bdc5-4371-86c0-fae83f2bb49e) | `9ffcddf7db6ccbfc98ed` |
| DE | current listing, nuovo ID | [Praktikum im Bereich Human Resources / Talent Acquisition & Development](https://jobs.bosch.de/job/Praktikum-im-Bereich-Human-Resources-_-Talent-Acquisition-Development-Lohr-am-Main?id=e33d7096-ba41-4a8b-a00c-59acbfd1fb4b) | `f8872a3b540362c588af` |
| DE | current listing, nuovo ID | [Praktikum im Bereich Human Resources bei Bosch Smart Home](https://jobs.bosch.de/job/Praktikum-im-Bereich-Human-Resources-bei-Bosch-Smart-Home-Stuttgart-Vaihingen?id=45916750-52bb-4e6f-9df7-7263e2b4cd4f) | `cda8be00ab611586d01e` |
| DE | current listing, nuovo ID | [Praktikum im Personalmanagement mit Schwerpunkt Studierendenbetreuung](https://jobs.bosch.de/job/Praktikum-im-Personalmanagement-mit-Schwerpunkt-Studierendenbetreuung-Abstatt-bei-Stuttgart?id=b96ffbae-cfbf-45d7-a478-55c0abc15bbe) | `ef197460f7837ce8af80` |
| DE | current listing, nuovo ID | [Praktikum im Recruiting und Personalmanagement](https://jobs.bosch.de/job/Praktikum-im-Recruiting-und-Personalmanagement-Eisenach?id=c2dccfd7-3635-4e6b-9edf-65cd34a775bd) | `a523275bf7227c94d7a6` |
| DE | current listing, nuovo ID | [Praktikum in der Personalentwicklung und Recruiting](https://jobs.bosch.de/job/Praktikum-in-der-Personalentwicklung-und-Recruiting-Muenchen-Neuperlach?id=d00256c1-ca67-4328-b004-c16f51ab40ed) | `4eee1f55dd72b344575f` |
| DE | current listing, nuovo ID | [Praktikum in Personalmanagement](https://jobs.bosch.de/job/Praktikum-in-Personalmanagement-Reutlingen-Kusterdingen?id=e0ea21dc-20e6-413c-a47f-cc0506d96c59) | `3e15e0adc63b52cad8ef` |
| DE | current listing, nuovo ID | [Praktikum Personalentwicklung, Technische Weiterbildung und Ausbildung](https://jobs.bosch.de/job/Praktikum-Personalentwicklung-Technische-Weiterbildung-und-Ausbildung-Muenchen-Neuperlach?id=561658f3-0c1a-4ccf-a7f3-13602cac1958) | `c2fa3e8616c870360c01` |
| DE | current listing, nuovo ID | [Praktikum Personalmanagement](https://jobs.bosch.de/job/Praktikum-Personalmanagement-Lohr-am-Main?id=806bc3a8-524d-45cb-836d-7d87294806fd) | `ca2b7407157c5d9c4d35` |
| DE | current listing, nuovo ID | [Praktikum Recruiting & Employer Branding](https://jobs.bosch.de/job/Praktikum-Recruiting-Employer-Branding-Muenchen-Neuperlach?id=3e8b4f6e-448a-4204-8b91-13f396b05ab2) | `785cff241a94ddb81358` |
| ES | current listing, ID conservato | [People & Culture Internship](https://careers.accor.com/global/en/job/people-and-culture-internship-in-hyde-hotel-ibiza-eivissa-spain-jid-112077) | `9e36b272a2a0311c8a54` |
| FR | current listing, ID conservato | [4-MONTH INTERNSHIP - Starting January 2027 – Data Analyst & Visualisation - HR Tech – Licence 3 - €1300/month](https://careers.loreal.com/en/job/paris/4-month-internship-starting-january-2027-data-analyst-and-visualisation-hr-tech-licence-3-1300-month/3456/46428950976) | `7afeb2b794b13da33547` |
| FR | current listing, ID conservato | [6-MONTH INTERNSHIP - Starting January 2027 – HRBP Junior & Labor Relations – Master's ½ - €1700/month](https://careers.loreal.com/en/job/paris/6-month-internship-starting-january-2027-hrbp-junior-and-labor-relations-master-s-1700-month/3456/45030409088) | `eb83a5f6f4de82050b06` |
| FR | current listing, ID conservato | [6-MONTH INTERNSHIP - Starting January 2027 – Talent Acquisition – Master's ½ - €1700/month](https://careers.loreal.com/en/job/paris/6-month-internship-starting-january-2027-talent-acquisition-master-s-1700-month/3456/45617213440) | `de16a93f04941e0ffa51` |
| FR | current listing, ID conservato | [Global Recruitment Excellence Intern - F/M/X](https://careers.accor.com/global/en/job/global-recruitment-excellence-intern-f-m-x-in-issy-les-moulineaux-france-jid-111670) | `dcb835c378d165c60c93` |
| FR | current listing, ID conservato | [Internship – Global Schools Partnerships & Young Talent Acquisition Coordinator - 6 months - F/M/X](https://careers.accor.com/global/en/job/internship-global-schools-partnerships-and-young-talent-acquisition-coordinator-6-months-f-m-x-in-issy-les-moulineaux-france-jid-74997) | `7b9e2037d73ee47523d6` |
| FR | current listing, ID conservato | [STAGE 6 MOIS - À partir de janvier 2027 – Projet Transformation Digitale & IA Juridique RH](https://careers.loreal.com/en/job/clichy/stage-6-mois-a-partir-de-janvier-2027-projet-transformation-digitale-and-ia-juridique-rh/3456/46447903872) | `f61088c4ef3de49da111` |
| FR | current listing, ID conservato | [Stage Ressources Humaines (à partir de janvier 2027 - 6 mois) (H/F)](https://careers.accor.com/global/en/job/stage-ressources-humaines-a-partir-de-janvier-2027-6-mois-h-f-in-sofitel-paris-arc-de-triomphe-paris-france-jid-49270) | `261ed8b40294ea3a6ab2` |
| FR | current listing, ID conservato | [Stage RH \| 6 mois \| De Janvier à Juin 2027 \| Région parisienne \| Master 1 ou 2 \| 1700€ brut mensuels \| Nombreuses opportunités](https://careers.loreal.com/en/job/paris/stage-rh-6-mois-de-janvier-a-juin-2027-region-parisienne-master-1-ou-2-1700-brut-mensuels-nombreuse/3456/36074467072) | `3f9e2c13db6a06672080` |
| FR | current listing, ID conservato | [Stagiaire des Ressources Humaines](https://careers.accor.com/global/en/job/stagiaire-des-ressources-humaines-in-25hours-hotel-paris-terminus-nord-paris-france-jid-117113) | `20eb3604fcc1d16ef383` |
| FR | current listing, nuovo ID | [Stagiaire ressources humaines (H/F/NB)](https://careers.accor.com/global/en/job/stagiaire-ressources-humaines-h-f-nb-in-mama-shelter-paris-east-paris-france-jid-114506) | `34c1527d23c711324e4e` |
| FR | current listing, ID conservato | [Usine de Caudry - S1- STAGE 5 MOIS - A partir de mai 2027 - Ressources Humaines - Master 2 - 1 700€/mois (H/F)](https://careers.loreal.com/en/job/caudry/usine-de-caudry-s1-stage-5-mois-a-partir-de-mai-2027-ressources-humaines-master-2-1-700-mois-h-f/3456/45305415168) | `0b4db58c3f42d7349b2c` |
| GB | current listing, nuovo ID | [Human Resources Summer Intern – London](https://careers.loreal.com/en/job/london/human-resources-summer-intern-london/3456/46997800064) | `8d95ec2a4cab4d383743` |
| LU | current listing, ID conservato | [INTERNSHIP - HR Communication & Intranet](https://careers.ing.com/en/job/luxembourg/internship-hr-communication-and-intranet/3121/46201154432) | `b40b26a9fb30985840e6` |
| LU | current listing, ID conservato | [INTERNSHIP - HR Operations](https://careers.ing.com/en/job/luxembourg/internship-hr-operations/3121/38478345920) | `29d6b4ffa447d4975237` |
| NL | current listing, nuovo ID | [HR Communications Internship - Internal Communications & Employee Engagement](https://www.asml.com/en/careers/find-your-job/hr-communications-internship-internal-communications-employee-engagement-j00356570) | `c4226b7394165eb039cc` |
| NL | current listing, nuovo ID | [HR \| Business Administration Internship: Early career Events, Programs and Talent Engagement](https://www.asml.com/en/careers/find-your-job/hr--business-administration-internship-early-career-events-programs-and-talent-engagement-j00355639) | `e052283857539ce5b5fb` |
| NL | current listing, nuovo ID | [Human Resource Management \| Business Administration internship: onboarding operations improvement](https://www.asml.com/en/careers/find-your-job/human-resource-management--business-administration-internship-onboarding-operations-improvement-j00355161) | `a2de9a5c49e82d57b61c` |
| NL | current listing, ID conservato | [Internships HR (Paid) - February 2027](https://careers.loreal.com/en/job/hoofddorp/internships-hr-paid-february-2027/3456/43655304704) | `b026de1118de01bb5cb7` |
| NL | lead, nuovo ID | [stage recruitment en HR](https://www.werkenbijrandstad.nl/vacature/1814/stage-recruitment-en-hr) | `9134a80d5570e06eddc2` |

## Costo dei controlli e verifiche

| Fonte | GET osservati | Byte misurati | Secondi |
|---|---:|---:|---:|
| sitemap-careers-abb | 16 | n.d. | 30.8 |
| sitemap-careers-accor-com | 18 | 9711397 | 36.6 |
| sitemap-careers-adeccogroup-com | 61 | n.d. | 118.9 |
| sitemap-careers-ing-com | 10 | 6359667 | 20.3 |
| sitemap-careers-knorr-bremse-com | 4 | 292365 | 8.3 |
| sitemap-careers-loreal-com | 16 | 2720100 | 32.2 |
| sitemap-jobs-bosch-com | 12 | n.d. | 22.2 |
| sitemap-jobs-bosch-de | 27 | 4643832 | 54.2 |
| sitemap-jobs-infineon-com | 8 | n.d. | 16.3 |
| sitemap-jobs-kuehne-nagel-com | 15 | n.d. | 28.7 |
| sitemap-jobs-pirelli-com | 8 | n.d. | 14.4 |
| sitemap-join-pmicareers-com | 16 | n.d. | 30.5 |
| sitemap-www-asml-com | 12 | 1409176 | 24.1 |
| sitemap-www-werkenbijrandstad-nl | 9 | n.d. | 16.4 |

Python 3.12 locale, 625 test passati. Node, 54 passati. Valutazione, 160 esempi e zero errori. Build e coverage riusciti. Il replay live ha usato il runtime di sistema dove il runtime Python 3.12 locale rifiutava la catena TLS. Modulo o invio di candidatura mai esercitati.
