# Stage HR per paese — diagnosi e recupero, novembre 2026

## Sintesi per paese

Base `main@d69c664`, catalogo del 22 novembre 2026, ore 09:33 CET. Per ogni paese si contano le schede con `status=open` e quel paese in `countries`. Sono 16 paesi a zero dei 17 richiesti. GB ha già uno stage. ES e PT sono i due confronti a volume ridotto. La colonna «causa» indica il principale ostacolo documentato nel progetto. La causa completa dello zero e la disponibilità nel mercato restano **non dimostrato**.

I datori sono quelli con almeno un `workplace` confermato nel paese. La raccolta recente richiede fonte abilitata, report `ok` e completo secondo la semantica di `country_research_progress`, entro 48 ore dal timestamp del report. ATS e universali contano fonti distinte dei datori così individuati. La colonna «sede osservata» richiede anche il paese in `observed_countries`. Il registro registra destinazioni di ricerca anche senza workplace confermato. Lo zero registrale non misura il numero di datori reali.

| Paese | Aperte | Datori con sede / raccolta riuscita | ATS / universale / sede osservata | Causa | Prova | Intervento | Costo |
|---|---:|---:|---:|---|---|---|---|
| IE | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | Due prime pagine, 9 schede distinte, 0 match | Verificare la pista Regeneron della #94 e ampliare gli inventari ufficiali | 2 POST di confronto già spesi |
| GB | 1 | 1 / 1 | 1 / 0 / 1 | EURES fuori copertura | Fanatics già aperto via Greenhouse | Monitorare l’esito della fonte esistente | 4 GET misurati il 22/11 |
| PL | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | SmartWays verificato in staging nella #102 | Riutilizzare #102. Integrare il termine attestato nella ricerca | 9 GET misurati (#102) |
| DK | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | Quattro stage JKS in staging nella #102 | Riutilizzare #102 e qualificare Randstad | 18 GET misurati (#102) |
| CZ | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | Falso negativo dimostrato su Mark2. 0 match nelle due query | Correggere il titolo e qualificare una fonte per Mark2 | 2 POST di confronto già spesi. Fonte: non dimostrato |
| PT | 2 | 0 / 0 | 0 / 0 / 0 | Causa del volume ridotto non dimostrata | 2 aperti nel catalogo. 0 match nelle due query | Conservare i canali diretti e confrontare gli inventari dei datori | 2 POST di confronto già spesi |
| ES | 3 | 0 / 0 | 0 / 0 / 0 | Causa del volume ridotto non dimostrata | 3 aperti nel catalogo. 3 match EURES distinti già noti, uno da rivedere | Rivedere la scheda TITULADO e la coerenza paese/lingua delle schede attive | 2 POST di confronto già spesi |
| BG | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | Gameloft e INENSIA hanno pubblicato annunci HR | Qualificare le carriere ufficiali in bulgaro e in inglese | non dimostrato |
| HR | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 15 schede campionate senza match | Cercare datori in HZZ e verificare la fonte aziendale | non dimostrato |
| CY | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 0 risultati in entrambe le query greche. Stage storico XM a Limassol | Rivedere Lever EU di XM ed eseguire il confronto EN | 1 POST per la prima pagina EN. ATS: non dimostrato |
| EE | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 8 schede senza match | Verificare offerte dai datori e dal canale Töötukassa | non dimostrato |
| GR | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 0 risultati con entrambe le forme greche. Workable in revisione #114 | Completare il controllo same-ID e modulo sul tenant Workable | non dimostrato |
| HU | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | Tre schede ordinarie. Annuncio IBM a Budapest | Risalire alla vacancy del datore e cercare stage via canali studenti | non dimostrato |
| LV | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 26 e 23 schede distinte nei due campioni, senza match | Cercare stage su Prakse e risalire ai datori | non dimostrato |
| LT | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 0 risultati EURES. NEO Finance ha pubblicato su Teamtailor | Qualificare il tenant e il sitemap | non dimostrato |
| MT | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 27 schede distinte senza match | Qualificare la pista Hilton e il canale Jobsplus | non dimostrato |
| RO | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 17 schede senza match. BAT ha pubblicato a Bucarest | Confermare freschezza e fonte aziendale | non dimostrato |
| SK | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 0 risultati EURES. BNP Paribas Cardif ha pubblicato a Bratislava | Individuare il board del datore | non dimostrato |
| SI | 0 | 0 / 0 | 0 / 0 / 0 | Nessun datore con fonte | 11 schede senza match. Danfoss è una pista a Lubiana | Risalire al record ufficiale e cercare con termini sloveni | non dimostrato |

## EURES in staging

Una prima pagina per query (massimo 50), criterio `TITLE`, `BEST_MATCH`, `locationCodes` per paese, `el` per GR. Il primo giro usa la prima coppia locale generata dal vocabolario su main, EN per IE e MT. Le PR #87 e #88 avevano già confrontato ricerca globale e filtro geografico. Il pilota #87 aveva restituito 109 schede in IE/PL/DK/CZ, con zero stage HR riconosciuti. Questa prova riprende il filtro e rende visibili anche gli scarti. [PR #87](https://github.com/nightlydeveloper8/eu-hr-internships/pull/87) · [PR #88](https://github.com/nightlydeveloper8/eu-hr-internships/pull/88) I due lotti successivi aggiungono dieci coppie mirate, incluse le nuove forme. Ho contato le righe restituite, gli ID con paese esplicito o estratto dal record EURES, e i risultati distinti col fingerprint del collector. Le somme tra query rappresentano letture, con possibili ripetizioni. Un totale su tutte le pagine e tutte le coppie è **non dimostrato**.

«HR» significa che il classificatore accetta la scheda, senza verifica indipendente di applicabilità o iscrizione. Per gli scarti, «non stage» indica assenza del segnale di placement oppure un’esclusione esplicita, «non HR» indica un segnale di stage senza match HR. Questi sono esiti delle regole di diagnosi, correggibili dopo lettura della scheda. Ho riclassificato manualmente il veterinario sloveno come ruolo ordinario: `splošne prakse` indica pratica generale.

| Paese | Query | Righe API | ID nel paese | Schede distinte | HR | Non stage | Non HR |
|---|---|---:|---:|---:|---:|---:|---:|
| IE | intern hr | 9 | 9 | 9 | 0 | 5 | 4 |
| PL | staż hr | 50 | 50 | 48 | 0 | 12 | 36 |
| DK | praktikant hr | 1 | 1 | 1 | 0 | 0 | 1 |
| CZ | stáž hr | 50 | 50 | 47 | 0 | 46 | 1 |
| PT | estágio recursos humanos | 1 | 1 | 1 | 0 | 1 | 0 |
| ES | prácticas recursos humanos | 50 | 50 | 50 | 2 | 46 | 2 |
| BG | стаж човешки ресурси | 50 | 50 | 42 | 0 | 42 | 0 |
| HR | praksa ljudski potencijali | 15 | 15 | 15 | 0 | 15 | 0 |
| CY | πρακτική άσκηση ανθρώπινο δυναμικό | 0 | 0 | 0 | 0 | 0 | 0 |
| EE | praktika personal | 8 | 8 | 8 | 0 | 7 | 1 |
| GR | πρακτική άσκηση ανθρώπινο δυναμικό | 0 | 0 | 0 | 0 | 0 | 0 |
| HU | gyakornok hr | 3 | 3 | 3 | 0 | 3 | 0 |
| LV | prakse personāla | 27 | 27 | 26 | 0 | 26 | 0 |
| LT | praktika personalo | 0 | 0 | 0 | 0 | 0 | 0 |
| MT | intern hr | 28 | 28 | 27 | 0 | 26 | 1 |
| RO | stagiu resurse umane | 17 | 17 | 17 | 0 | 17 | 0 |
| SK | stáž hr | 0 | 0 | 0 | 0 | 0 | 0 |
| SI | praksa kadrovsk | 11 | 11 | 11 | 0 | 11 | 0 |
| IE | internship recruitment | 0 | 0 | 0 | 0 | 0 | 0 |
| PL | praktyka kadry | 50 | 50 | 49 | 0 | 48 | 1 |
| DK | praktik rekruttering | 9 | 9 | 9 | 0 | 8 | 1 |
| CZ | odborná praxe personalistika | 50 | 50 | 50 | 0 | 50 | 0 |
| PT | estágio recrutamento | 0 | 0 | 0 | 0 | 0 | 0 |
| ES | prácticas selección | 50 | 50 | 45 | 2 | 35 | 8 |
| GR | πρακτική άσκηση ανθρώπινου δυναμικού | 0 | 0 | 0 | 0 | 0 | 0 |
| CY | πρακτική άσκηση ανθρώπινου δυναμικού | 0 | 0 | 0 | 0 | 0 | 0 |
| LV | praktikants personāla atlases | 24 | 24 | 23 | 0 | 23 | 0 |
| LT | praktika personalo administravimas | 0 | 0 | 0 | 0 | 0 | 0 |
| GB | fuori copertura, nessuna query | — | — | — | — | — | — |

**Costi misurati.** Primo giro: 1 GET robots, 18 POST di ricerca, 1.332.823 byte e 180,54 s. Secondo: 1 GET robots, 8 POST di ricerca, 723.747 byte e 80,43 s. Terzo: 1 GET robots, 2 POST di ricerca, 129.660 byte e 20,41 s. Un tentativo precedente ha fallito TLS sulla GET robots (0 byte, 0,07 s). La ripetizione ha usato le CA di sistema con verifica TLS. Totale: 3 GET riuscite e 1 fallita, 28 POST di ricerca in sola lettura, 2.186.230 byte, 281,45 s cumulati. Traffico della consultazione web: non dimostrato.

### Scarti da rivedere

Fino a cinque schede distinte per paese dai due giri. Dove il campione contiene meno scarti, sono riportati tutti quelli disponibili. I link identificano la scheda osservata il 22 novembre.

**IE**

- non HR · [Construction - Quantity Surveyor Intern](https://europa.eu/eures/portal/jv-se/jv-details/SlY6NmZhNGFhZWUyNzMyNDllYzhiM2QwZjBkMjRjNzQ3MjYgMTg?lang=en)
- non HR · [Construction - Electrical Engineer Intern](https://europa.eu/eures/portal/jv-se/jv-details/SlY6OWI0MWQwMWU1N2MzNDM2NmEyODZlMGQwNDBiY2RhMDYgMTg?lang=en)
- non stage · [International Sales Executive – Portuguese Markets](https://europa.eu/eures/portal/jv-se/jv-details/SlY6YzYxNWZlYzUyNDc1NDNjYjk5MmU3YzQ5MzdmMzhjYjMgMTg?lang=en)
- non stage · [International Sales Executive for Argentina & Latin America](https://europa.eu/eures/portal/jv-se/jv-details/SlY6ZTc3NDUxOGE1ZjEwNDc4N2I2MTMyNWE1NzgyMmU4MWYgMTg?lang=en)
- non stage · [HGV Mechanics required for Zenton Limited t/a Lynn International](https://europa.eu/eures/portal/jv-se/jv-details/SlY6NDQxODQ5ZjkyZTljNDQ4NTk1YzhkYzk5ZDc5MzUzOTggMTg?lang=en)

**GB**

Fuori perimetro EURES, nessun esempio.

**PL**

- non HR · [Specjalista ds. programów - stażysta / specjalista ds. programów / specjalista ds. rozwoju zawodowego - stażysta / specjalista ds. rozwoju zawodowego K/M](https://europa.eu/eures/portal/jv-se/jv-details/MTQ5NDQxODcgMTI?lang=en)
- non HR · [Stażystka/ Stażysta młodsza asystentka/ młodszy asystent](https://europa.eu/eures/portal/jv-se/jv-details/MTQ5NDQwNzQgMTI?lang=en)
- non stage · [Kucharz (K_M) - oferta po stażu](https://europa.eu/eures/portal/jv-se/jv-details/MTQ5NDM2MjAgMTI?lang=en)
- non stage · [Specjalista/specjalistka ds. HR i kontroli wewnętrznej](https://europa.eu/eures/portal/jv-se/jv-details/MTQ5NDMxMjcgMTI?lang=en)
- non stage · [Osoba na stanowisku stażysty (po ukończeniu stażu urzędniczego osoba na stanowisku specjalisty ds. inwestycji i remontów)](https://europa.eu/eures/portal/jv-se/jv-details/MTQ5NDIxOTMgMTI?lang=en)

**DK**

- non HR · [Bruxelles kalder – bliv praktikant hos Folketingets repræsentant ved EU](https://europa.eu/eures/portal/jv-se/jv-details/MjRkZjk5YzYtMGQxMS00Yzc1LWJjMGEtZDZjN2FjNDk2MDU2IDc?lang=en)
- non stage · [Praktisk medarbejder til heste- og smådyrsværksted på Tinnetgaard](https://europa.eu/eures/portal/jv-se/jv-details/NDFjZWJjYmItYjJhZi00ZTY1LWE5MDEtZjVkOWRlYTZhODM4IDc?lang=en)
- non stage · [Socialpædagog med håndværkerbaggrund til Proaktiv](https://europa.eu/eures/portal/jv-se/jv-details/N2E4OWY2NGYtOTM4My00MGI5LThmNmYtYzFhNWU4MDRjYWVjIDc?lang=en)
- non stage · [Et praktisk deltidsjob med klare rammer – 7 timer om ugen i 8210 Aarhus V](https://europa.eu/eures/portal/jv-se/jv-details/YWYwMDJkYTItN2RiYS00MjI5LTgwMWMtYjg2ODVjOThjZDZhIDc?lang=en)
- non stage · [Dyrlæge til større privatejet praksis i Aalborgområdet](https://europa.eu/eures/portal/jv-se/jv-details/YzA2M2QxM2QtZjc1ZC00NzdkLWJiZTEtYjcwOTAwOWEzZmFiIDc?lang=en)

**CZ**

- non HR · [Stážista v oblasti řízení a hardwaru robotů (Robotics Controls and Hardware Intern)Inženýři elektronici ve výzkumu a vývoji, Inženýři elektronici ve výzkumu a vývoji](https://europa.eu/eures/portal/jv-se/jv-details/MzUwMjY0OTc3NTYgNg?lang=en)
- non stage · [Řidič autobusu, Řidiči autobusů v městské hromadné dopravě](https://europa.eu/eures/portal/jv-se/jv-details/MzUyMDAxMzA3NjMgNg?lang=en)
- non stage · [ŘIDIČI AUTOBUSŮ, Řidiči autobusů v městské hromadné dopravě](https://europa.eu/eures/portal/jv-se/jv-details/MzUxNzM1OTA3ODcgNg?lang=en)
- non stage · [Administrativní pracovník/pracovnice HR oddělení, Všeobecní administrativní pracovníci](https://europa.eu/eures/portal/jv-se/jv-details/MzUxNzI3NzA3NDkgNg?lang=en)
- non stage · [HR specialista, Specialisté v oblasti personálního řízení](https://europa.eu/eures/portal/jv-se/jv-details/MzUxNjc3MzA3MjYgNg?lang=en)

**PT**

- non stage · [ESPECIALISTA EM RECURSOS HUMANOS](https://europa.eu/eures/portal/jv-se/jv-details/NTg5NDU4OTQ2IDE0MQ?lang=en)

**ES**

- non HR · [PRÁCTICAS IT](https://europa.eu/eures/portal/jv-se/jv-details/NzQ2OTE0MyAxMDI?lang=en)
- non HR · [Prácticas Abogado](https://europa.eu/eures/portal/jv-se/jv-details/NzI0MTM4OSAxMDI?lang=en)
- non stage · [TÉCNICO RECURSOS HUMANOS VILLAVERDE ALTO](https://europa.eu/eures/portal/jv-se/jv-details/NzQ3MTU3MyAxMDI?lang=en)
- non stage · [TÉCNICOS MEDIOS EN RECURSOS HUMANOS, EN GENERAL](https://europa.eu/eures/portal/jv-se/jv-details/NzQ3MTI4MiAxMDI?lang=en)
- non stage · [GRADUADO EN RELACIONES LABORALES Y RECURSOS HUMANOS](https://europa.eu/eures/portal/jv-se/jv-details/NzQ3MTAwMCAxMDI?lang=en)

**BG**

- non stage · [Работник, тъкачен стан](https://europa.eu/eures/portal/jv-se/jv-details/MjEwMjM4NiA0?lang=en)
- non stage · [Учител, ресурсен](https://europa.eu/eures/portal/jv-se/jv-details/MjEwMTk4NSA0?lang=en)
- non stage · [Учител, ресурсен](https://europa.eu/eures/portal/jv-se/jv-details/MjEwMjEyMiA0?lang=en)
- non stage · [Учител, ресурсен](https://europa.eu/eures/portal/jv-se/jv-details/MjEwMjE1NSA0?lang=en)
- non stage · [Учител, ресурсен](https://europa.eu/eures/portal/jv-se/jv-details/MjEwMjEyNyA0?lang=en)

**HR**

- non stage · [REFERENT / REFERENTICA ZA POTREBE SLUŽBE ZA UPRAVLJANJE LJUDSKIM RESURSIMA](https://europa.eu/eures/portal/jv-se/jv-details/MjkzNzM4OCAxOQ?lang=en)
- non stage · [VIŠI/A STRUČNI/A SAVJETNIK/CA U ODSJEKU KADROVSKIH POSLOVA (VSS) (ODJEL ZA LJUDSKE POTENCIJALE, SLUŽBA ZA PRAVNE, OPĆE I KADROVSKE POSLOVE)](https://europa.eu/eures/portal/jv-se/jv-details/MjkzNTgzNiAxOQ?lang=en)
- non stage · [POMOĆNI RADNIK/RADNICA - PRALJA](https://europa.eu/eures/portal/jv-se/jv-details/MjkzNTY5NCAxOQ?lang=en)
- non stage · [REFERENT/ICA ZA LJUDSKE POTENCIJALE](https://europa.eu/eures/portal/jv-se/jv-details/MjkzNTE3MyAxOQ?lang=en)
- non stage · [VODITELJ/ICA VOZNOG PARKA - C/E KATEGORIJA](https://europa.eu/eures/portal/jv-se/jv-details/MjkzMzQ1MyAxOQ?lang=en)

**CY**

Nessun esempio nel campione.

**EE**

- non HR · [Külmatehniku abi - praktikant](https://europa.eu/eures/portal/jv-se/jv-details/MTY2Njc1MyA4?lang=en)
- non stage · [Personalispetsialist](https://europa.eu/eures/portal/jv-se/jv-details/MTY2OTgzOCA4?lang=en)
- non stage · [HR Specialist & Office Manager](https://europa.eu/eures/portal/jv-se/jv-details/MTY2OTc2OCA4?lang=en)
- non stage · [Personalispetsialist](https://europa.eu/eures/portal/jv-se/jv-details/MTY2OTcxNSA4?lang=en)
- non stage · [Personalijuht](https://europa.eu/eures/portal/jv-se/jv-details/MTY2ODA5NSA4?lang=en)

**GR**

Nessun esempio nel campione.

**HU**

- non stage · [Director Global HR (m/f/d) - Technology and Digital Transformation (Betriebswirt/in (Hochschule) - Personalmanagement)](https://europa.eu/eures/portal/jv-se/jv-details/MTAwMDEtMTAwMzg2NTYzNi1TIDE?lang=en)
- non stage · [Humánpolitikai adminisztrátor (HR Projektkoordinátor)](https://europa.eu/eures/portal/jv-se/jv-details/MTQ1NDgzMTI3OTUgMTY?lang=en)
- non stage · [Személyügyi tanácsadó (Senior regionális HR tanácsadó)](https://europa.eu/eures/portal/jv-se/jv-details/MTQ1NjEwMzgwMjEgMTY?lang=en)

**LV**

- non stage · [Personāla/ personālvadības struktūrvienības VADĪTĀJS/ DIREKTORS](https://europa.eu/eures/portal/jv-se/jv-details/MjYxMTE5LTExMCA0MDE?lang=en)
- non stage · [PERSONĀLA ATLASES SPECIĀLISTS](https://europa.eu/eures/portal/jv-se/jv-details/MjYxMTE5LTM0IDQwMQ?lang=en)
- non stage · [PERSONĀLA SPECIĀLISTS](https://europa.eu/eures/portal/jv-se/jv-details/MjYxMTE2LTQyIDQwMQ?lang=en)
- non stage · [PERSONĀLA SPECIĀLISTS](https://europa.eu/eures/portal/jv-se/jv-details/MjYxMTEzLTIwIDQwMQ?lang=en)
- non stage · [VECĀKAIS PERSONĀLA INSPEKTORS](https://europa.eu/eures/portal/jv-se/jv-details/MjYxMTExLTE2NCA0MDE?lang=en)

**LT**

Nessun esempio nel campione.

**MT**

- non HR · [ROOMS INTERN](https://europa.eu/eures/portal/jv-se/jv-details/NDYwNDE5IDEwMQ?lang=en)
- non stage · [HR OFFICER](https://europa.eu/eures/portal/jv-se/jv-details/NDYwNTUxIDEwMQ?lang=en)
- non stage · [HR ASSISTANT](https://europa.eu/eures/portal/jv-se/jv-details/NDYwNTQ5IDEwMQ?lang=en)
- non stage · [HR EXECUTIVE](https://europa.eu/eures/portal/jv-se/jv-details/NDYwMjU1IDEwMQ?lang=en)
- non stage · [INTERNATIONAL WELDER](https://europa.eu/eures/portal/jv-se/jv-details/NDYwMDA0IDEwMQ?lang=en)

**RO**

- non stage · [ELECTRICIAN EXPLOATARE CENTRALE SI STATII ELECTRICE](https://europa.eu/eures/portal/jv-se/jv-details/MzQzMTE5NCAxMw?lang=en)
- non stage · [ELECTRICIAN EXPLOATARE CENTRALE SI STATII ELECTRICE](https://europa.eu/eures/portal/jv-se/jv-details/MzQyMDYxNyAxMw?lang=en)
- non stage · [SPECIALIST RESURSE UMANE](https://europa.eu/eures/portal/jv-se/jv-details/MzQyMTc5NiAxMw?lang=en)
- non stage · [ELECTRICIAN EXPLOATARE CENTRALE SI STATII ELECTRICE](https://europa.eu/eures/portal/jv-se/jv-details/MzMxNDQ5MiAxMw?lang=en)
- non stage · [SPECIALIST RESURSE UMANE](https://europa.eu/eures/portal/jv-se/jv-details/MzQyOTE4NyAxMw?lang=en)

**SK**

Nessun esempio nel campione.

**SI**

- non stage · [VODJA ODDELKA ZZZS I V PRAVNO KADROVSKEM ODDELKU OE KOPER - M/Ž](https://europa.eu/eures/portal/jv-se/jv-details/MzUwNTg4NCAxNA?lang=en)
- non stage · [POMOČNIK-VZDRŽEVALEC VOZNEGA PARKA - M/Ž](https://europa.eu/eures/portal/jv-se/jv-details/MzUwNTY2MiAxNA?lang=en)
- non stage · [VETERINAR SPLOŠNE PRAKSE Z LICENCO - M/Ž](https://europa.eu/eures/portal/jv-se/jv-details/MzQ3NDg1Ny0yMDI2NDcgMTQ?lang=en)
- non stage · [PRAVNIK - PRAVNA SLUŽBA - M/Ž](https://europa.eu/eures/portal/jv-se/jv-details/MzQ5MzQ4OS0yMDI2NDcgMTQ?lang=en)
- non stage · [KOORDINATOR VOZNEGA PARKA, ŠKODNIH PRIMEROV IN POSLOVNE ADMINISTRACIJE - M/Ž](https://europa.eu/eures/portal/jv-se/jv-details/MzUwNDIzNSAxNA?lang=en)

## Vocabolario e classificazione

La verifica riguarda le lingue della ricerca nazionale, con una nota sui casi multilingui. La presenza di un termine indica che il vocabolario genera una query, anche quando la query non è stata eseguita in questo lotto. La lingua dell’annuncio non determina quella di lavoro.

| Paese | Lingua e coppie già configurate | Lacuna documentata o stato |
|---|---|---|
| IE | EN · intern, internship, trainee + HR, recruitment, payroll | GA assente dalle query. Uso in un annuncio HR pertinente: non dimostrato. |
| GB | EN · intern, internship + human resources, people, talent acquisition | GA, CYM e GLA assenti dalle query. Uso in un annuncio HR pertinente: non dimostrato. GB è fuori rete EURES. |
| PL | PL · staż, praktyki, stażysta + HR, kadry, rekrutacja | Aggiunto **praktyka**, attestato nell’annuncio Action Poland per l’amministrazione del personale e paghe. [Akademia WSB](https://wsb.edu.pl/student/akademickie-biuro-karier/oferty-pracy-job-offers/oferty-pracy-job-offers/praktyka-w-dziale-kadr-i-plac.html) |
| DK | DA · praktik, praktikant + HR, rekruttering, personale | Il titolo di Randstad è accettato dal classificatore. [Randstad](https://www.randstad.dk/en/jobs/hr-praktikant_kobenhavnfrb_14376/) |
| CZ | CS · stáž, stážista + HR, personalistika, nábor | Aggiunto **odborná praxe** (annuncio storico Alexander Hughes). La forma generica **praxe** indica anche esperienza precedente. Corretto il falso negativo **HR STÁŽ NA NÁBOROVÉM ODDĚLENÍ** (Mark2, 2 settembre 2026). [Alexander Hughes](https://www.vsem.cz/pracovni-a-odborne-staze.html?show=666) · [Mark2](https://www.vsem.cz/pracovni-a-odborne-staze.html?show=784) |
| PT | PT · estágio, estagiário + RH, recursos humanos, recrutamento | Lacuna con esempio d’uso e falso negativo: non dimostrato. |
| ES | ES · prácticas, becario + recursos humanos, RRHH, selección | CA, EU e GL assenti dalle query. Caso concreto nelle lingue regionali: non dimostrato. |
| BG | BG · стаж, стажант + човешки ресурси, подбор | Lacuna con esempio d’uso e falso negativo: non dimostrato. |
| HR | HR · praksa, pripravnik + ljudski potencijali, ljudski resursi | Lacuna con esempio d’uso e falso negativo: non dimostrato. |
| CY | EL e EN · πρακτική άσκηση / internship + ανθρώπινο δυναμικό / HR | La ricerca EL riceve la stessa aggiunta di GR. TR assente dalle query. Uso in un annuncio HR cipriota pertinente: non dimostrato. |
| EE | ET · praktika, praktikant + personal, värbamine | **Personalipraktika** può indicare una pratica HR aziendale. Falso negativo in una vacancy di stage attestata: non dimostrato. |
| GR | EL · πρακτική άσκηση + ανθρώπινο δυναμικό, HR | Aggiunto **ανθρώπινου δυναμικού** alle query. Il classificatore riconosceva già la forma flessa. [Annuncio iKnowHow](https://www.iekpeiraia.gr/αγγελίες-εργασίας/880-πρακτικη-ασκηση-σε-θεση-hr.html) |
| HU | HU · gyakornok + HR, emberi erőforrás, toborzás | Lacuna con esempio d’uso e falso negativo: non dimostrato. |
| LV | LV · prakse, praktikants + personāla, cilvēkresursi | Aggiunto **personāla atlases** per la selezione del personale. Il classificatore accettava già il titolo. [WD Market](https://www.prakse.lv/vacancy/175759/wd-market-sia/personala-atlases-praktikants-e) |
| LT | LT · praktika, praktikantas + personalo, žmogiškieji ištekliai | Aggiunto **personalo administravimas** per l’amministrazione HR. Il classificatore accettava già il titolo. [VMG Group](https://vmg.eu/karjera/praktikos-pozicijos/) |
| MT | EN · internship + HR, recruitment, talent acquisition | MT assente dalle query. Uso in un annuncio HR pertinente: non dimostrato. |
| RO | RO · stagiu, internship + resurse umane, recrutare | Lacuna con esempio d’uso e falso negativo: non dimostrato. |
| SK | SK · stáž, stážista + personalistika, ľudské zdroje, nábor | Il riconoscimento di `HR stáž` vale anche per la stessa grafia slovacca. Caso aggiuntivo nel campione: non dimostrato. |
| SI | SL · praksa, pripravnik + kadrovsk, človeški viri | `praksa` ricorre anche in titoli ordinari, come il veterinario del campione. Falso negativo HR: non dimostrato. |

I nuovi termini generano coppie aggiuntive nella ricerca globale. Il tetto resta quello configurato per la fonte. Il costo incrementale del ciclo ordinario è **non dimostrato**: l’aumento delle coppie compete con la paginazione e con il limite di richieste. Le fixture includono ruoli ordinari, un programma graduate e uno stage non HR. Nei test lingua, il testo ceco senza requisiti espliciti lascia le lingue sconosciute. L’esempio sintetico con requisito inglese documenta la lingua richiesta e lascia indeterminata la sufficienza del solo inglese.

## Regno Unito

L’elenco ufficiale EURES copre 31 paesi SEE e Svizzera. Il Regno Unito non compare fra i paesi coperti dopo la Brexit. L’alias storico `UK → GB` normalizza i record, senza stabilire copertura. Il canale DWP rimane escluso secondo la revisione del repository. Reed resta in attesa di decisione. [EURES, copertura geografica](https://eures.europa.eu/eures-services/help-and-support_en) · [Revisione DWP e Reed](fonti-pubbliche.md)

Il canale aziendale documentato è **Fanatics Collectibles, Greenhouse, Londra**, posting `4510457009`. La review del 22 novembre delimita i termini ai GET su board, vacancy e modulo pubblici e documenta la prova con robots. La fonte era già attiva su `main@d69c664`. Il catalogo marca **Summer 2027 Intern - HR Intern** come aperto e verificato. Il requisito undergraduate risulta nella prova già raccolta. Accessibilità per uno studente NHL Stenden, visto e lingua di lavoro: non dimostrato. Altri tenant GB con termini, robots e stage verificati nel perimetro di questo lavoro: non dimostrato. [Prova e termini](attivazione-ats-2026-11-22.md) · [Scheda Fanatics](https://job-boards.greenhouse.io/fanaticscollectibles/jobs/4510457009)

## Datori da qualificare con raccolta sospesa

Per tutte le proposte in tabella, `collection_activation_hold: true` sul datore e `enabled: false` sulla fonte candidata. La tabella è il dossier di preparazione. Provisioning e registri di produzione restano invariati. Le liste già aperte nelle PR sono richiamate dal loro branch. L’idoneità per NHL Stenden richiede prova separata di iscrizione ammessa, lingua, durata e accesso alla candidatura.

| Paese | Datore e prova dello stage | Canale candidato e verifica mancante |
|---|---|---|
| IE | Regeneron, pista #94; annuncio HR recente sul canale ufficiale non dimostrato | Carriere ufficiali. Completare #94. [PR #94](https://github.com/nightlydeveloper8/eu-hr-internships/pull/94) |
| PL | SmartWays, posting HR 31252 verificato in staging il 20/11. Action Poland, pratica in amministrazione del personale e paghe, data non dimostrata. | Recruitee interno, già predisposto in #102. Per Action Poland, ATS non dimostrato. [PR #102](https://github.com/nightlydeveloper8/eu-hr-internships/pull/102) · [Action Poland](https://wsb.edu.pl/student/akademickie-biuro-karier/oferty-pracy-job-offers/oferty-pracy-job-offers/praktyka-w-dziale-kadr-i-plac.html) |
| DK | JKS, quattro stage verificati il 20/11 in staging. Randstad, HR praktikant a Copenaghen. | JKS Talentech già predisposto in #102. Per Randstad, famiglia ATS e dimensione della sede non dimostrate. [PR #102](https://github.com/nightlydeveloper8/eu-hr-internships/pull/102) · [Randstad](https://www.randstad.dk/en/jobs/hr-praktikant_kobenhavnfrb_14376/) |
| CZ | Mark2 Corporation Czech, Praga, HR STÁŽ, 2/9/2026. | Annuncio del datore pubblicato da VŠEM. ATS del datore e dimensione non dimostrati. [VŠEM](https://www.vsem.cz/pracovni-a-odborne-staze.html?show=784) |
| BG | INENSIA, Sofia, HR Intern del 21/10/2026, 61 addetti su registro; Gameloft, Sofia, HR Intern, data non dimostrata. | ATS pubblico INENSIA non dimostrato. Gameloft espone la vacancy sul sito ufficiale; verificare perimetro host e termini. [INENSIA](https://www.jobs.bg/en/job/8663032) · [Gameloft](https://www.gameloft.com/jobs/HR%20Intern%20%28long-term%20labor%20contract%29-744000083478145) |
| HR | BAT, HR internship a Zagabria. Data entro 12 mesi: non dimostrato. | ATS compatibile non dimostrato. [Università di Zagabria](https://www.efzg.unizg.hr/become-hr-intern-in-bat-38313/38313) |
| CY | XM, People & Culture Intern, Limassol, estate 2026, requisiti di studio espliciti. Dimensione 50–999: non dimostrato. | Lever EU pubblico. Robots, termini e corrispondenza con l’ID storico da verificare. [Annuncio del datore](https://cy.linkedin.com/jobs/view/human-resources-intern-at-xm-4361824018) · [Board Lever](https://jobs.eu.lever.co/xm?department=Human+Resources) |
| EE | Datore con HR internship recente e ATS verificato: non dimostrato. | Töötukassa come pista di ricerca. |
| GR | iKnowHow, Atene, HR Intern attestato. La scheda della scuola richiede iscrizione presso un istituto riconosciuto in Grecia. | Workable, verifica del modulo da completare nel perimetro della #114. [Carriere iKnowHow](https://www.iknowhow.com/careers/) · [PR #114](https://github.com/nightlydeveloper8/eu-hr-internships/pull/114) |
| HU | IBM, Talent Acquisition Intern, Budapest, annuncio del 28/10/2026 ripreso dal board WCT. | ATS del datore per questa scheda non dimostrato. [Annuncio WCT](https://careers.wct-fct.com/companies/ibm-2-ac1a9733-081a-4a8e-80d2-933d126d8ce3/jobs/98236335-talent-acquisition-intern-english-german-french-spanish) |
| LV | DIGI MEDIA, Riga, Personāla vadības praktikants. WD Market, Ulbroka, Personāla atlases praktikants/-e. | Carriere ufficiali DIGI MEDIA e inserzione del datore su Prakse per WD. Dimensione e ATS non dimostrati. [DIGI MEDIA](https://digimedia.studio/lv/karjera/personala-vadibas-praktikants/) · [WD Market](https://www.prakse.lv/vacancy/175759/wd-market-sia/personala-atlases-praktikants-e) |
| LT | NEO Finance, Vilnius, HR Intern 8189703, 56 colleghi secondo il datore. VMG Group, HR praktika con scadenza indicata 28/2/2027. | Il sito NEO indica Teamtailor. Annuncio storico, robots e termini da verificare. Per VMG sede dell’annuncio e ATS non dimostrati. [Vacancy NEO](https://careers.neofinance.com/jobs/8189703-hr-intern) · [Board NEO](https://careers.neofinance.com/) · [VMG](https://vmg.eu/karjera/praktikos-pozicijos/) |
| MT | Hilton Malta, St. Julian’s, HR Intern tramite bacheca universitaria. Data entro 12 mesi: non dimostrato. | Annuncio sul board ufficiale e relativo ATS non dimostrati. [IULM](https://iulm.almalaurea.it/lau/annunci/bachecaannunci.aspx?idannuncio=871246&lang=en) |
| RO | BAT Romania, HR Intern, Bucarest. Data entro 12 mesi: non dimostrato. | Carriere ufficiali. Provenienza ATS e candidato eleggibile da confermare. [BAT](https://careers.bat.com/en/job/bucharest/hr-intern/1045/46198641856) |
| SK | BNP Paribas Cardif, HR Intern di due mesi, Bratislava, pubblicato il 26/6/2026. | Annuncio del datore su Profesia. Tenant ATS non dimostrato. [Profesia](https://www.profesia.sk/praca/bnp-paribas-cardif-poistovna/O5313178) |
| SI | Danfoss, HR Intern, Lubiana, pista indicizzata con scadenza indicata 21/12/2026. | Vacancy originale e ATS non dimostrati. [Copia indicizzata](https://bebee.com/si/jobs/hr-intern-hr-service-center-emea-danfoss-ljubljana--techmap_si_4481720697) |

## Simulazione della fase 2

Riesecuzione di `classify_role` prima e dopo sulle stesse schede staging, usando titolo, descrizione e tipo di rapporto EURES. Sul catalogo pubblicato il replay della finalizzazione con il registro reale, zero fonti selezionate e timestamp originale conserva **926 → 926 ID, 0 persi**. Un confronto limitato ai titoli del catalogo, dove le descrizioni originali non sono disponibili, produce **876 → 876** corrispondenze su 926 titoli.

La fixture esterna verificabile di Mark2 passa da esclusa a **talent-acquisition** in CZ. Titolo **HR STÁŽ NA NÁBOROVÉM ODDĚLENÍ**. È un caso di classificazione, fuori dall’inventario EURES campionato e senza promozione nel catalogo o prova di candidatura policy v2. Gli altri paesi passano da zero a zero in questo confronto su fixture nuove. Per ciascuno dei 18 paesi UE campionati: **0 nuovi record EURES** dopo il confronto con gli ID del catalogo. GB non è stato interrogato e ha **0 nuovi ID** nel replay. Per Werkstudent, traineeship e graduate la lista dei nuovi titoli è vuota.

Le schede spagnole **Prácticas Recursos Humanos**, **Beca departamento selección** e **TITULADO SUPERIOR ADE Y RECURSOS HUMANOS** sono già note al catalogo. L’ultima passa con il tipo EURES `internship` benché il titolo indichi una qualifica conseguita. Per la scheda TITULADO, il placement universitario risulta **non dimostrato**. Va verificato sul canale originale prima di usarla come risultato utile per studenti.

Per evitare regressioni nel replay, il test di conservazione passa ora il registro reale alla finalizzazione, come in produzione, selezionando zero fonti. Sul main di partenza il registro vuoto faceva revocare la prova Personio del record `2500a45f998ebbdf4d43` e fallivano due test. La correzione conserva l’asserzione sullo stato e la policy Personio.

I prossimi piloti prioritari sono le piste aziendali IE/CZ e il riesame già avviato di PL/DK (#102). Per PT/ES il confronto va ampliato agli inventari dei datori e all’originale delle schede pubbliche ambigue.
