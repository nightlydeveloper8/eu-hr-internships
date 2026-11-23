# Attivazione proposta di fonti ATS riviste — 22 novembre 2026

Base `5181ca8` con #110, #113 e #115 integrate. La proposta toglie entrambi gli hold e abilita 14 fonti. La configurazione di Climeworks resta disabilitata e conserva entrambi gli hold. Il catalogo pubblicato e le altre fonti restano come su main.

## Termini applicati

Revisione il **22 novembre 2026** secondo la decisione del maintainer. Ogni fonte riporta in `review_notes` i testi del provider e del datore consultati, il perimetro e l’esito. Questo è un giudizio circoscritto alle GET di inventario, vacancy e modulo sul tenant esatto. Le restrizioni alla copia, ai dati dei candidati e alle aree riservate rimangono applicabili nel rispettivo perimetro. Le verifiche già svolte nella bozza #114 sono riusate.

- **Recruitee.** Il §2.9 descrive le Careers Site come listing pubblici e l'XML pubblico è escluso dall'autenticazione Careers API. I documenti consultati non vietano le GET dei feed e delle schede pubbliche in esame. I termini Climeworks §§1.1 e 3.6–3.7 vietano robot e monitoraggio sui siti associati. Il divieto Peripass PortPass riguarda il prodotto logistico. I termini commerciali di Aquablu e Zero Motorcycles non coprono espressamente il tenant Recruitee delle offerte. [#114](https://github.com/nightlydeveloper8/eu-hr-internships/pull/114) · [Termini Tellent](https://recruitee.com/terms) · [Perimetro XML](https://docs.recruitee.com/reference/authentication-1) · [Termini Climeworks](https://climeworks.com/website-terms-use)
- **Greenhouse.** La documentazione distingue GET pubbliche del Job Board API e POST di candidatura autenticati. L'accordo con la clausola anti-robot definisce il proprio servizio come MyGreenhouse, con account, fuori dagli host pubblici qui usati. I termini generali Fanatics escludono espressamente il recruiting e l'informativa collegata dal board riguarda i dati dei candidati. [Job Board API](https://docs.greenhouse.io/job-board.html) · [MyGreenhouse](https://my.greenhouse.io/users/agreement) · [Termini Fanatics](https://www.fanaticsinc.com/fanatics-holding-terms)
- **Personio.** Le condizioni generali sono indirizzate al cliente. Il provider documenta la GET XML delle posizioni aperte con rinvio alle pagine ufficiali. Le condizioni lette non vietano le GET del feed e delle pagine pubbliche sui tenant rivisti. Le GET statiche non richiedono il CDN che vieta i chunk JavaScript. [Condizioni Personio](https://www.personio.com/terms/) · [Feed GET](https://developer.personio.de/v1.0/reference/get_xml) · [Guida di integrazione](https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML)

## Prova di staging

Prova fresca del 22 novembre con collector ordinario, budget per fonte, controllo robots e host esatti. L'inventario pubblicato e il modulo della stessa vacancy sono stati riverificati per 14 fonti. Per Climeworks non sono stati richiesti feed o pagine dal collector. Telemetria del collector: i GET includono robots, i byte sono quelli letti e i tempi sono cumulati per fonte.

| Fonte | Paese | Posting | GET | Byte | Secondi | Esito |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Climeworks | CH | 2831389 | 0 | 0 | 0.000 | Mantiene hold. divieto del datore |
| Peripass | BE | 2262981 | 4 | 872.349 | 1.844 | Policy v2. proposta di attivazione |
| Fanatics Collectibles | GB | 4510457009 | 4 | 3.295.091 | 1.977 | Policy v2. proposta di attivazione |
| Aquablu | NL | 2822890 | 4 | 805.399 | 1.799 | Policy v2. proposta di attivazione |
| Zero Motorcycles | NL | 2668002 | 4 | 523.110 | 1.754 | Policy v2. proposta di attivazione |
| Youvia | NL | 2202199 | 4 | 493.165 | 1.801 | Policy v2. proposta di attivazione |
| Mercedes-Benz.io | PT | 2833968 | 4 | 721.076 | 1.709 | Policy v2. proposta di attivazione |
| ten23 health | CH | 2139342 | 4 | 248.928 | 1.765 | Policy v2. proposta di attivazione |
| Watson Farley & Williams LLP | DE | 2634127 | 4 | 223.608 | 1.734 | Policy v2. proposta di attivazione |
| Studyflix | DE | 1119140 | 4 | 272.895 | 1.666 | Policy v2. proposta di attivazione |
| Bloomwell Group | DE | 2888191 | 4 | 288.595 | 1.701 | Policy v2. proposta di attivazione |
| Vamo | DE | 2471392 | 4 | 330.055 | 2.669 | Policy v2. proposta di attivazione |
| Reformer Club | DE | 2669913 | 4 | 328.534 | 3.968 | Policy v2. proposta di attivazione |
| Wilken Software Group | DE | 2840229 | 4 | 448.002 | 2.294 | Policy v2. proposta di attivazione |
| Avantgarde | DE | 2888187 | 4 | 1.338.691 | 2.935 | Policy v2. proposta di attivazione |

Totale **56 GET / 10.189.498 byte / 29,616 secondi-fonte**. È la stima incrementale osservata per ciclo. Moduli, inventari, risposte e latenza possono cambiare.

La finalizzazione temporanea sul catalogo di base ha dato **913 → 926 ID, 0 persi**. Stage attuali verificati **407 → 420**, candidature dirette **36 → 50**, lead **365 → 365**, collector attivi **1.923 → 1.937**. Watson Farley & Williams aggiunge una candidatura diretta sullo stesso ID EURES. Le altre tredici candidature sono nuovi ID nel replay.

| Paese | Stage verificati | Dirette verificate |
| --- | ---: | ---: |
| Belgio | 23 → 24 | 4 → 5 |
| Germania | 32 → 38 | 4 → 11 |
| Paesi Bassi | 227 → 230 | 19 → 22 |
| Portogallo | 1 → 2 | 1 → 2 |
| Regno Unito | 0 → 1 | 0 → 1 |
| Svizzera | 32 → 33 | 0 → 1 |

## Verifiche dopo un eventuale merge

`Validate application` parte su aggiornamenti della PR e su push a main. Il merge tocca i registri, perciò avvia anche `Daily employer collection` e fa ricostruire il sito a Cloudflare Pages. Il monitor di freschezza mantiene la sua pianificazione. Controllare il primo ciclo con entrambi i registri del commit di attivazione, gli shard, il publish, gli ID storici, le nuove candidature dirette per paese, i rigetti di robots/rate limit e il costo per fonte rispetto alla misura di staging. Confermare Climeworks assente dagli shard attivi e la conversione EURES senza doppione. Verificare il catalogo servito dopo il deploy del commit dati.

## Audit separato delle fonti già attive

Riscontro sui **1.923** slot già attivi di main, incrociando adapter, host permessi e feed configurati con le evidenze note. Nessuna voce già attiva è stata modificata e nessun crawler è stato avviato per l'audit. Non è una certificazione dei termini di tutti i datori.

- **SmartRecruiters, 11 fonti** con almeno un host ATS soggetto alla revisione. Il repository tratta l'accesso SmartRecruiters come non autorizzato. I termini per candidati limitano l'accesso automatico a dati di altri utenti. Le fonti universali miste vanno valutate host per host. `auto-accor`, `auto-altarea`, `auto-avery-dennison`, `auto-bosch`, `auto-delta-electronics`, `auto-devoteam`, `auto-interlogement-93`, `auto-jde-peet-s`, `auto-salomon`, `auto-sia`, `auto-smcp`. [Termini SmartRecruiters](https://www.smartrecruiters.com/legal/terms-of-use/)
- **Ashby, 6 fonti** con host `jobs.ashbyhq.com` indicate dal progetto come soggette a riesame per una risposta robots 401 precedente. Il robots letto separatamente il 22 novembre elenca divieti per `/meeting/`, `/b/` e `/api/`. Va identificato il percorso realmente usato e verificato il runtime prima di attribuire un divieto al board pubblico. `auto-choco`, `auto-emidat`, `auto-payrails`, `auto-reedsy`, `auto-scoreplay`, `auto-zefir`. [Robots Ashby](https://jobs.ashbyhq.com/robots.txt)
- **Recruitee JSON, 32 fonti** configurate su `/api/offers/`, da ricontrollare prima del requisito di token annunciato per il 10 febbraio 2027. L’eccezione XML non si applica al JSON documentato. Le singole implementazioni su host personalizzati richiedono verifica. `auto-alliade`, `auto-buko-infrasupport-b-v`, `auto-ennatuurlijk`, `auto-haitsma-beton`, `auto-hogeschool-van-hall-larenstein`, `auto-intergas-verwarming-b-v`, `auto-isero`, `auto-koninklijke-remia-c-v`, `auto-nts-norma`, `auto-sw-vastgoedverbetering`, `auto-trunkrs`, `auto-wagenborg-passagiersdiensten`, `auto-wajer-yachts`, `recruitee-batch-abrio`, `recruitee-batch-chr-haute-senne`, `recruitee-batch-vigo-groep`, `recruitee-bundl`, `recruitee-dienst-dommelvallei`, `recruitee-edco`, `recruitee-focus-entertainment`, `recruitee-franklin-institute`, `recruitee-gerard-bertrand`, `recruitee-hotel-twentyseven`, `recruitee-ibexa`, `recruitee-monsterscore`, `recruitee-multifix`, `recruitee-protiviti-gmbh`, `recruitee-psv`, `recruitee-sas-look-up-space`, `recruitee-skytree`, `recruitee-social-deal-b-v`, `recruitee-veldsink-groep`. [Perimetro autenticazione Recruitee](https://docs.recruitee.com/reference/authentication-1)
- **Amazon Jobs, una fonte.** `amazon-hr-internships` è da rivedere per il blocco robots già documentato e perché la pagina Legal di Amazon Jobs rimanda alle condizioni generali Amazon. Non è stata attribuita al sito carriere una clausola letta nei contratti di altri servizi Amazon. [Rinvio Amazon Jobs](https://www.amazon.jobs/en-gb/privacy_page?notice_id=us-conditions-english&region_id=region_us)

Climeworks non compare tra le fonti già attive. Nessuna fonte configurata usa l'host MyGreenhouse; il divieto di quel servizio non è stato propagato agli endpoint pubblici Greenhouse.
