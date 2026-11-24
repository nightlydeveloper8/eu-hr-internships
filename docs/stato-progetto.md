# Stato di ripresa — People Placement

## 23 novembre 2026 — benchmark di recall HR parziale
[Rapporto](recall-benchmark-2026-11.md) e [campione](recall-gold-set-2026-11.csv): 16/220 schede attuali, 1 IT e 15 DE, tutte assenti dallo snapshot `8f15504`.
Staging: 35 GET, 7.785.625 byte, 20,069 secondi HTTP. Recall nazionale e candidature v2 non dimostrato.
937 ID preservati. Passano Node, valutazione, coverage, build, validazione e provisioning; su base intatta Python ha 3 fallimenti e 4 errori.
Prossimo passo: estendere il campione a più datori, con priorità a portali universitari e canali locali ammessi in Italia e Spagna.

## 23 novembre 2026 — scoperta tenant ATS da Common Crawl
[Dossier iniziale](ats-tenant-discovery-2026-11.md): 19.482 chiavi, 36 nel registro, 13 segnali HR da 1.032 feed. Candidature v2 e copertura europea completa non dimostrate.
[Dossier enterprise](ats-enterprise-2026-11.md): 9.574 chiavi su tre crawl; regola di accesso del maintainer aggiunta in AGENTS.md. Workday, iCIMS, Avature e Cornerstone campionati in staging sui percorsi ammessi.
Staging: 348 tenant estratti, 158 ammessi, zero segnali HR. Sottocampione JSON-LD: 123/153 pagine, zero link di candidatura espliciti. Prossimo passo: valutare recall e sensibilità del campionamento, preservando i limiti di accesso. Nessuna fonte aggiunta o attivata.

## 23 novembre 2026 — conversione EURES Amac predisposta in hold
[PR #120](https://github.com/nightlydeveloper8/eu-hr-internships/pull/120) · [Dossier dei 30 datori](eures-to-direct-2026-11.md). Prova storica same-ID Recruitee 2828451, 4 GET / 1.852.861 byte / 1,799 s.
Il replay storico mantiene 926 ID e una sola scheda Amac, con 52 → 53 candidature dirette in simulazione. Fonte disabilitata e hold aziendale mantenuto.
La raccolta successiva al commit deve confermare la conservazione di ID, stage e candidature dirette, con EURES operativo e Amac esclusa.

## 23 novembre 2026 — lingua dell’annuncio e requisiti linguistici
[Rapporto e campione](lingue-2026-11.md) di 80 annunci EURES. Il collector usa metadati e corpo; l’interfaccia distingue anche bilingue e sconosciuto.
Campione prima → dopo: precisione e copertura 80/80 → 80/80; annunci con estratti 25 → 30; coppie stage–lingua corrette 23 → 51.
Il filtro di inizio e la soglia di durata IHRM sono coperti dai test Node. Replay parziale su evidenze salvate: 126/927 schede (94/414 aperte), zero cambi di lingua. Stage aperti con estratto nominativo: 104 → 109.
Il maintainer ha accettato il replay parziale. Istantanea pre-merge dal catalogo bot `94f8144`. Prossimo passo: confrontare la prima raccolta dopo il merge con quella baseline prima di procedere con #120.

## 22 novembre 2026 — monitoraggio della raccolta di produzione

La raccolta innescata da #118 controlla ID persi, calo degli stage >15%, EURES fallito o vuoto e guasti >20% tra fonti recentemente riuscite. Il monitor pianificato segnala catalogo oltre 36 ore.
[Prima raccolta dopo #116](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45002015989) riuscita. Baseline pubblicata in `d69c664`: 926 ID, 422 stage aperti, 52 candidature dirette, 13 paesi con stage.
Verifica prima di #118: CI Python 3.12 verde dopo #132; #124 e #123 integrate. Filtro di inizio e scheda senza data verificati sul sito pubblico a 375 e 1440 px.
Prossimo passo: verificare run e publish post-merge, integrità degli ID, variazioni di freschezza, candidature dirette, EURES e issue del monitor.

## 22 novembre 2026 — finestra di stage IHRM del secondo anno

Filtro di inizio dal 5 gennaio al 13 marzo 2027. Il filtro di durata compare da 10 stage verificati con durata esplicita.
Baseline `d69c664`: 926 ID, 422 stage aperti, 52 candidature dirette, 13 paesi con stage aperti.
Il replay ripreso da #119 è già integrato con #132. La PR non attiva collect.yml.
Prossimo passo: verificare il deploy Cloudflare e il sito pubblico a 375 e 1440 px.

## 22 novembre 2026 — diario per ramo e limite alle PR degli agenti

Frammenti di massimo otto righe, consolidati nel commit di integrazione.
Limite di cinque PR aperte create da agenti e sospensione dei nuovi piloti di ricerca.
Verifica offline del consolidatore; nessun cambiamento alla raccolta.
Prossimo passo: usare il frammento nelle PR e ridurre la coda con le decisioni del maintainer.

## 22 novembre 2026 — attivazione ATS proposta dopo verifica fresca

[#113](https://github.com/nightlydeveloper8/eu-hr-internships/pull/113) e [#115](https://github.com/nightlydeveloper8/eu-hr-internships/pull/115) integrate su autorizzazione, con le fonti ancora in hold. Su `main@5181ca8`, [proposta e misure](attivazione-ats-2026-11-22.md) confermano 14 fonti idonee, 56 GET / 10.189.498 byte / 29,616 secondi-fonte. Climeworks resta in hold per i termini. Simulazione 913 → 926 ID, zero persi, 407 → 420 stage verificati e 36 → 50 diretti. Audit delle fonti già attive senza modifiche. Prossimo passo: revisione del maintainer, poi controllare il primo ciclo e il catalogo servito in caso di merge autorizzato.

## 22 novembre 2026 — metodo Personio e nove fonti con hold

[Verifica di staging e costi](personio-static-applications-2026-11-22.md). Su `main@f606443`, otto candidature Personio con feed e modulo stesso ID e una Recruitee v2. Mercedes-Benz.io, ten23 health e Reformer Club indicano anche l’ammissione di neolaureati. Watson Farley & Williams conserva l’ID EURES; Studyflix resta a un annuncio. Nove fonti predisposte disabilitate e con hold. 38 GET, 4.210.328 byte, 20,734 secondi-fonte nel ciclo conclusivo. Simulazione 913 → 921 ID, zero persi, 407 → 415 stage verificati, 36 → 45 diretti, 365 lead invariati. Nessuna raccolta o attivazione di produzione. Prossimo passo: revisione della PR e, prima di un eventuale rollout, termini dei singoli datori e prova fresca.

## 21 novembre 2026 — revisione annunci Recruitee

[Risultati, requisiti e costi](recruitee-hr-internships-2026-11-21.md). Tre fonti NL con candidatura diretta v2 (Aquablu, Zero Motorcycles, Youvia), predisposte disabilitate e con hold. Finalizzazione temporanea 907 → 910 ID, 0 persi. Mercedes-Benz.io è un caso limite con modulo verificato e ammissione di neolaureati. Prossimo passo: revisione, decisione sul caso limite e prova fresca prima di ogni eventuale attivazione. Base `2c937f7`. Verificati 531 test Python 3.12, 35 test Node, build, catalogo e provisioning idempotente. 1.923 collector attivi prima e dopo.

## 21 novembre 2026 — inventario ATS e staging di tenant già noti

[Rapporto e inventario](inventario-ats-2026-11-21.md): individuate 68 coppie datore–tenant, 20 non registrate come ATS attivo; i paesi sono soltanto ambito di ricerca. 18 tenant esaminati o bloccati e due Lever esclusi. La scansione ha riconfermato tre vacancy già predisposte da #110; Berenschot è già nel catalogo come candidatura diretta, mentre Focus/PulluP richiede riconciliazione e Mynaric Personio ha submit disabilitato. **0 nuove candidature distinte e 0 nuove fonti preparate**. Spesi 50 GET / almeno 11.747.768 byte / 36,115 secondi cumulati, senza POST né invio; PR #110 già integrata in `841278f`.

Python 3.12: 531 test; Node: 35; classificazione, build, validazione e provisioning idempotente riusciti. Catalogo invariato: 907 ID, 0 persi. Il primo run con Python 3.9 non è riuscito; dettagli nel rapporto. Nessuna attivazione o modifica a file del bot.

**Prossimo passo:** rivedere l'identità Focus/PulluP e il conflitto fra hold aziendale e crawler universale già attivo, salvaguardando provisioning e ID; ricercare altre fonti e tenere Personio incompleto finché il modulo non è dimostrato. Esclusione dalle PR aperte verificata su descrizioni e modifiche ai registri, non su ogni file; completare prima di preparare fonti ulteriori.

## 21 novembre 2026 — sette fonti ATS, staging senza attivazione

[Verifica e costi](sette-fonti-ats-2026-11-21.md): Climeworks CH, Peripass BE e Fanatics GB ciascuna con una candidatura diretta policy v2 nello staging, studenti iscritti ammessi. Fonti disabilitate e hold sui tre datori. 12 GET / 4.830.640 byte / 7,391 secondi-fonte nel ciclo misurato. Finalizzazione temporanea 907 → 910 ID, zero persi. Nessuna variazione al catalogo di produzione. Sungrow e Entrix non superano il controllo del modulo; Social Hub ha host e date da riconciliare; Workable espone due HR ma il modulo non è dimostrato. Robots e limiti dei termini nel rapporto e review_notes. Il lettore Workable pubblico è proposto con test, senza fonte registrata. Verifica locale: 531 test Python 3.12, 35 Node, valutazione, copertura, build e validazione catalogo riusciti.

Prossimo passo: review della PR e dei termini applicabili provider/datori; solo dopo eventuale approvazione esplicita del merge e approvazioni distinte per l'attivazione. Rifare le prove se scadute prima di qualunque rilascio; non avviare raccolte complete.

## 21 novembre 2026 — fase 2, ricontrollo EURES prima della ricerca

[Diagnosi e confronto in staging](lead-eures-rechecks-2026-11-21.md) sul catalogo `a71b260`: cinque cicli al tetto di 330 richieste. La proposta anticipa al massimo cinque verifiche. Nel campione, 4 schede attive come Public employment service e 1 risposta 404. Se la PR verrà integrata, verificare recuperi e recall nel primo ciclo automatico.

Revisione del maintainer. [#107](https://github.com/nightlydeveloper8/eu-hr-internships/pull/107) integrata in `517f3a4`, [#109](https://github.com/nightlydeveloper8/eu-hr-internships/pull/109) in `b16dc7a`. Nella [#108](https://github.com/nightlydeveloper8/eu-hr-internships/pull/108), un ID discordante ora viene scartato e segnalato anche durante i ricontrolli ordinari. Il test riproduce il fallimento sul vecchio codice e conferma che la raccolta prosegue. Passati 521 test Python, 35 Node, valutazione, copertura, build, validazione catalogo e provisioning idempotente. Zero nuove letture live e zero ID persi. Verificare l’esito del primo ciclo automatico dopo il merge della #108.

## 21 novembre 2026 — fase 3, candidatura Adecco/Radancy

[Cinque posting FR in staging](lead-adecco-entry-2026-11-21.md): la CTA porta a una scheda Talentsoft con ID, i percorsi successivi osservati sono CV generico o account. 0 moduli specifici nel campione, 0 recuperi stimati. Proposta di causale circoscritta ai casi documentati, da rivedere se compare un percorso specifico.

## 21 novembre 2026 — fase 1, identificativi candidatura

[Audit dei 38 record](lead-application-id-2026-11-21.md) sul catalogo `a71b260`: 0 equivalenze dimostrate, 1 CTA storica con ID diverso, 37 casi con dati insufficienti. Test Workday esteso alla variante con suffisso; 0 recuperi stimati e 0 GET. Per valutare una regola serve la coppia vacancy/CTA con identità documentata.

## 21 novembre 2026 — diagnosi misurata dei 367 lead, senza promozioni

- **Branch dedicata:** `analysis/lead-conversion-audit-20261121`, a partire da `main@f0cfe6`. Prima del lavoro letti `AGENTS.md`, questo stato e **29 PR aperte**; in particolare evitata la sovrascrittura della diagnosi ATS in [#84](https://github.com/nightlydeveloper8/eu-hr-internships/pull/84) e degli interventi connessi.
- **Baseline verificata dal blob catalogo del 21/11 alle 07:35 UTC:** 906 ID distinti, 402 stage HR correnti (37 candidatura diretta policy v2 e 365 elenchi di servizi pubblici), 367 lead da diagnosticare. **93 record storici con URL esterno e ownership non stabilita** sono mantenuti separatamente, senza promozioni o eliminazioni.
- **Audit ripetibile:** aggiunti `scripts/lead_conversion_audit.py`, `tests/test_lead_conversion_audit.py`, [rapporto completo](lead-conversion-audit-2026-11-21.md) con **76 righe motivo × paese × famiglia ATS/adattatore**. Controllo 367/367: 176 senza modulo specifico, 57 con prova scaduta (53 EURES), 38 con ID non coincidente, 30 robots indisponibile, 14 identità vacancy mancante, 14 budget di tempo, più 38 in altre ragioni. Stessa fotografia per paese: FR 142, NL 94, IT 39, DE 36, ES 20, PL 10, altri 26. Le famiglie non confermate sono etichettate come adattatore, non come ATS certo.
- **Costo documentato del ciclo ordinario [#44879531709](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44879531709):** Adecco/Radancy 87 lead, 217 GET / 19.528.306 byte / 117,75 s per tutta la fonte; EURES 63 lead, 330 GET / 95.979.098 byte / 656,07 s per tutta la fonte; Amazon.jobs 30 lead, 92 GET / 1.657.511 byte / 88,27 s per tutta la fonte. I costi di fonte **non** sono costi marginali per lead. L'audit offline effettua **0 GET / 0 byte scaricati dai siti**; durata dell'elaborazione non strumentata.
- **Nessuna conversione live dimostrata in questa attività.** Il target **+50 non raggiunto**. I piloti [Adecco (2 posting, nessun modulo specifico)](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44736268862) e [Danone (2 CTA verso login)](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44736658503) impediscono la promozione di massa senza prove ulteriori; 53 EURES scaduti non sono candidature dirette e 30 Amazon sono bloccati da robots 403. **Non** si afferma che tutte queste vacancy siano chiuse.
- **Codice non modificato:** collector, ATS adapter, policy v2, fonti, registri, catalogo e workflow invariati. Dati del catalogo prima/dopo la sola modifica di audit: **906→906 ID, 402→402 stage verificati correnti, 37→37 candidature dirette e 367→367 lead; 0 ID rimossi**. Nessun merge, deploy, nuova fonte attiva o invio di candidatura.
- **Verifiche:** [CI sul codice audit #44925992565](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44925992565) riuscita: 518 test Python, 33 Node, evaluate, copertura e build. Il rapporto documenta i conteggi letti direttamente nel blob; la CI sulla branch riallineata alle PR #104/#105 è da controllare separatamente. La raccolta live in staging non è stata eseguita: costi nuovi, delta candidatura e nuovi form non verificati.
- **Primo passo successivo:** un pilota breve e reversibile su **due vacancy di due datori distinti** con ATS pubblico, ID stesso posting e modulo di candidatura autorizzato, misurando GET/byte/tempo prima di progettare un adapter generalizzato. Non convertire automaticamente né abilitare nuove fonti.

## 21 novembre 2026 — rifinitura UI premium dark (in produzione con PR #105, squash `eea045c`)

- Secondo giro UI sul catalogo di `a71b260`. Nella [matrice Playwright](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44916252439) Chromium 143, Firefox 144 e WebKit 26 hanno verificato la build a 375, 768 e 1440 px. Collisioni dei badge Benelux prima → dopo in ognuno dei 3 browser: **2 → 0**, **1 → 0**, **1 → 0**. Al posto dei badge in conflitto appaiono 3 pulsanti sincronizzati con selezione e conteggi della mappa. Verificati tastiera, tocco a 375 px, riduzione del movimento, nessun overflow orizzontale oltre 1 px e salvataggio della stessa chiave preferiti nella fixture.
- A parità di pertinenza il percorso diretto verificato sale da secondo a primo nella fixture con 2 risultati ugualmente pertinenti. Gli ordinamenti per data e la priorità NL mantengono i criteri preesistenti. La scheda EURES della fixture mostra EURES e una dicitura compatta sul datore non indicato. La CTA resta “View official listing”.
- Distribuzione della lingua dell’annuncio: homepage **31 inglese, 368 in lingua locale diversa dall’inglese, 3 altre** su 402. Pannello NL **19 inglese, 199 olandese, 2 altre** su 220. Gli annunci in più paesi sono contati una volta in homepage, mentre contribuiscono a ciascun pannello pertinente.
- Catalogo prima/dopo identico byte per byte (**2.306.279 byte**), **906 → 906 ID** distinti, **402 → 402 attuali**, **37 → 37 diretti**, **365 → 365** via servizio pubblico, **367 → 367 lead** e **44 → 44 chiusi** alla stessa ora fissata. Zero richieste a fonti di raccolta. I risultati della fixture verificano il comportamento dell’interfaccia.
- Caricamento homepage da build locale: 10 → 10 risposte HTTP 200 su Chromium/WebKit (**7.768.698 → 7.775.744 byte**) e 11 → 11 su Firefox, favicon inclusa (**7.769.101 → 7.776.147 byte**). Cinque asset HTML/CSS/JS modificati: **34.146 → 35.993 byte gzip**. Tempo al primo rendering osservato, mediana dei 3 viewport: chromium 349 → 346 ms, firefox 420 → 396 ms, webkit 1516 → 1481 ms. Una misurazione per viewport.
- [CI](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44916252414): 514 test Python, 35 Node, classificazione, report di copertura e build. 9 combinazioni browser/larghezza, 51 screenshot prima/dopo ([chromium](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44916252439/artifacts/14711768006) · [firefox](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44916252439/artifacts/14711698158) · [webkit](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44916252439/artifacts/14711452689)). Contrasto: zero violazioni rilevate da axe in homepage e nel pannello paese. Per i nuovi testi controllati a mano sui colori CSS, rapporto minimo **4,98:1** su fondo `#1d2938`. Screen reader, contrasto dei casi non risolti da axe e verifica live della rifinitura restano fuori da queste misure.
- **Rilascio.** Revisione e merge autorizzati dal maintainer il 21/11: PR #105 unita in `eea045c`. Ricontrollati prima del merge sulla build: 35 test Node, 47 controlli di interazione Playwright, nessun overflow a 375/768/1440 px. Difetti minori noti: su desktop il riquadro Benelux tocca la legenda di circa 3 px; nelle schede EURES senza datore indicato non compare più la riga sul modulo del datore non verificato (resta il badge "Public employment service").

## 21 novembre 2026 — audit delle 27 PR rimaste aperte (esclusa #104) e quattro branch riallineate senza merge

- Inventario completo delle **27 PR ancora aperte oltre alla #104** in [`docs/backlog-pr.md`](backlog-pr.md): **2 A**, **2 B**, **13 C**, **9 D**, **1 E** al controllo finale, con diff `main...head`, CI e indicazione degli stage **misurati** (staging vs produzione). Nessuna delle 27 è stata chiusa o fusa da questo audit. `AGENTS.md` è ora presente su `main` grazie al merge della #103 effettuato da un'altra sessione; `docs/AGENTS.md` non era presente (404).
- Base osservata [main `a71b260`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/a71b260465c79515f044eb187289bc39a0d268a6), [run raccolta #44879531709](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44879531709) success, catalogo `updated_at=2026-11-21T07:35:04Z` ma `update_status=partial`: **906 ID su 906 record, 402 internship HR open, 37 candidature dirette policy v2 con prova strutturata, 365 annunci pubblici attivi senza modulo datore verificato**. Nessun confronto indipendente byte-per-byte con il sito effettuato.
- **Riallineamenti su branch dedicate:** [#102 `1adbc65`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/1adbc65ad367f4afa870fcaae8228b213d0f8e4e) incorpora 10 file dati aggiornati di main, mantenendo i 23 file ATS proposti e tutte le fonti disabilitate; [CI #44914400088](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44914400088) **success** su Python, Node, build e valutazioni. [#63 `fdfc39d`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/fdfc39d3fa074159450ed84e76f41e68289ec48b) conserva codice crawler e rapporto storico con [CI #44914504550](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44914504550) **success** (Python/Node/build); [#94 `635b575`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/635b575b285a74df7d8365f5c339b69b2054e176) conserva script/test/report di prioritizzazione ATS con [CI #44914546177](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44914546177) **success** (Python/Node/build). Nessuna modifica alla branch main né deploy.
- **Aggiornamento concorrente:** durante l'audit è stata aperta la [PR #103](https://github.com/nightlydeveloper8/eu-hr-internships/pull/103) (nuovo `AGENTS.md`, [CI #44914792134](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44914792134) success) e aggiornata da altra sessione la [#41](https://github.com/nightlydeveloper8/eu-hr-internships/pull/41) (WZA Drenthe, HEAD `a091aef`, [CI #44914275710](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44914275710) success). La #103 è stata successivamente **fusa da un'altra sessione** su `main` al commit [`f0cfe6`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/f0cfe6ead0fb6f3c1c3f6b26175f1a6a052b9d85): non figura più nelle **27 PR aperte** del backlog. La #41 è ancora aperta e il suo merge tocca `data/companies.json`, quindi potrebbe innescare la raccolta. La [#104](https://github.com/nightlydeveloper8/eu-hr-internships/pull/104) è l'output documentale di questo audit, conteggiata separatamente. Nessun branch #41/#103 modificato dall'audit.
- **Riallineamento al main dopo #103:** oltre alle tre branch originarie, [#41 `e34cc4`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/e34cc4c097724e709c00aa01932cded127438fdc) ora conserva tutte le quattro note Drenthe. Riapplicato il nuovo diario `AGENTS.md`/redesign a [#63 `7c2b367`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/7c2b367ee9150ebd72bfd1a7f5cab3c3092f9a5d), [#94 `8cf7880`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/8cf7880cd40e557b1224716ca7b7e7f9709164b6), [#102 `d31f896`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/d31f89600297c9b0ee1101d4eff370cd0e5fbfbd). Le nuove CI [#44915827940](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44915827940), [#44915696350](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44915696350), [#44915705348](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44915705348), [#44915713772](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44915713772) sono tutte **success** sui nuovi commit, con Python, Node, valutazione, coperture e build superati. Confronti su `main@f0cfe6`: **23 diverged, 4 ahead**; **11/27 unibili sulla propria base GitHub, 16/27 non unibili**. `data/sources.json` misurato: **1.977→1.980 fonti**, **1.923 abilitate invariate** (+3 disabilitate). Nessun merge verso main.
- **Risultato e limiti:** 0 nuovi stage o candidature aggiunti dalla presente attività; 0 fonti attivate, 0 richieste BudgetClient, 0 byte collector, 0 rendering aggiunto e 0 candidature inviate. Richieste/byte/tempi del traffico GitHub API non strumentati. Lo staging del 20/11 per #102 ha trovato **5 nuovi ID e 6 percorsi di candidatura** (4 JKS DK, 1 SmartWays PL, 1 conversione JobTech SE senza nuovo ID) in run separati: 18 GET / 2.400.777 B, 9 GET / 1.160.973 B, 8 GET / 416.375 B. Non sono risultati di produzione né verifiche live su data nuova. Scenario **condizionale** sul catalogo 21/11, da riconfermare: 906→911 ID, 402→407 stage aperti, 37→43 candidature dirette; non è una misura post-merge.
- **Primo prossimo passo:** revisione del [backlog delle PR](backlog-pr.md), review finale di #63 e #94 (CI già verdi) e nuova prova live in data distinta per la #102, poi richiesta di autorizzazione specifica ai singoli merge e separatamente ai rollout. Le 13 chiusure proposte in classe C restano soltanto proposte.

## 21 novembre 2026 — `AGENTS.md`: regole comuni per gli agenti AI

- Nuovo `AGENTS.md` nella radice. Raccoglie in un unico punto, letto automaticamente da Codex/ChatGPT e Claude: perimetro del progetto, autorizzazioni (niente merge, push su `main`, attivazione di fonti o chiusura di PR senza via libera), fonti ammesse, regole di dominio (solo stage HR per studenti; esclusi working student e graduate; livelli di prova policy v2 a 48 ore), regole UI, comandi di verifica, mappa del repository e formato richiesto per PR e resoconti.
- Due rischi operativi resi espliciti: un push su `main` che tocca `collector/**`, `data/sources.json` o `data/companies.json` avvia subito la raccolta di produzione; il provisioning attiva automaticamente un crawler per ogni datore senza fonte attiva, salvo `collection_activation_hold`.
- Comandi verificati su `a71b260`: 514 test `unittest`, 33 test Node, `evaluate.py`, `company_coverage.py`, `build.py`, `collector.daily provision` (idempotente). `company_coverage.py` riscrive i file `data/*-coverage.json`: documentato in `AGENTS.md`.
- Corretta la voce del 20/11 sul redesign, che risultava ancora "non in produzione".
- Solo documentazione: nessun cambiamento a codice, dati, fonti o workflow.

## 20 novembre 2026 — redesign visivo premium dark (in produzione con PR #100, squash `5ffb2d1`)

- **Ambito solo UI/UX.** Modificati `src/index.html`, `src/style.css`, `src/app.js`, `src/map.js`, `src/favicon.svg`, l'intestazione delle pagine secondarie e due helper puri in `src/logic.js` (`evidenceLevel`, `zoomViewBox`). Invariati collector, fonti, policy v2, verifiche delle candidature, catalogo, geometrie e codici paese, ID, URL dei filtri e preferiti locali (`people-placement:saved`).
- **Integra la branch `fix/application-evidence-filter-20261119`** (filtro *Application route confirmed*, mai unita a main) invece di riscriverla: la distinzione fra stage attuali (428), candidatura diretta verificata (39), annunci dei servizi pubblici (389) e lead da verificare (323) è la base della nuova UI.
- **Homepage map-first.** La mappa occupa circa il 70% della larghezza utile a 1440 px, inquadrata sui paesi interattivi; hover con un unico overlay luminoso (glow + bordo + gradiente), stati hover, selezionato e focus da tastiera distinti; tooltip con conteggi per livello di prova; badge numerici a dimensione costante con indicatore verde per le candidature dirette; area di tocco ampliata per Lussemburgo e Malta; zoom accessibile (+/−/reset) solo di visualizzazione. I paesi senza annunci sono descritti come "None observed yet", non come assenza di stage.
- **Progressive disclosure.** Ricerca + 3 filtri immediati (paese, specializzazione, lingua) e drawer "Advanced" (regione, tipo, modalità, lingua dell'annuncio, requisiti inglese, lead). `?view=advanced` apre il drawer. Statistiche di raccolta, conteggi d'archivio, salute delle fonti e metodologia sono nella finestra "About our sources / How we verify internships". Avvisi di freschezza, copertura parziale e lead restano visibili nell'area risultati.
- **Schede.** Gerarchia azienda → titolo → specializzazione/durata/modalità → badge di prova + massimo tre lingue documentate; CTA diversa per livello: "Apply on employer site" solo con candidatura verificata, "View official listing" per EURES/servizi pubblici, "Check at employer" per i lead. Dettagli ed evidenze linguistiche in un pannello espandibile.
- **Verifiche locali.** 33 test Node (2 nuovi), 514 test Python, 47 controlli Playwright su build `dist/` (conteggi mappa/filtri/risultati coerenti col catalogo `7c5ce80`, sincronizzazione mappa↔filtri↔URL, tastiera, Escape, drawer inerte, preferiti persistenti, link legacy `?unverified=true` ignorato, tap mobile senza tooltip-hover, bottom sheet, nessun overflow a 375/768/1440, reduced motion). Contrasto AA: testo più tenue 5,0:1 sulla superficie più chiara.
- **Peso e prestazioni (headless, senza GPU).** Asset frontend esclusi dati e `eu-map.js`: 25,8 → 34,3 KB gzip (+8,5 KB). Nessuna dipendenza, font esterno o tracking; CSP invariata. Costo dell'hover 32 → 36 ms ogni due frame dopo aver rimosso vignettatura e `backdrop-filter` sopra la mappa; tempo al primo rendering dei risultati 257 → 330 ms (mediana di 5).
- **Rilascio.** [PR #100](https://github.com/nightlydeveloper8/eu-hr-internships/pull/100) unita il 20/11 alle 20:31 CET in [`5ffb2d1`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/5ffb2d1cc9ae8127f23347e945dda4c28acc9c8b). [CI](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44802920549) e [Cloudflare Pages](https://github.com/nightlydeveloper8/eu-hr-internships/runs/136524081014) riusciti sul redesign. La [prima raccolta automatica successiva](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44879531709) ha concluso 18/18 job e pubblicato `a71b260`, con [Cloudflare Pages riuscito](https://github.com/nightlydeveloper8/eu-hr-internships/runs/136878899562). PR #79 chiusa come assorbita.
- **Non verificato.** Browser reali Safari/Firefox e screen reader.

## 20 novembre 2026 — lotto Recruitee verificato in produzione

- Squash merge della [PR #86](https://github.com/nightlydeveloper8/eu-hr-internships/pull/86) in `12a4832`. Ampelmann, VIGO, CHR Haute Senne e ABRIO sono attivi nella raccolta ordinaria.
- Il [run automatico](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44744205480) ha completato test, 16 shard e pubblicazione. Il commit catalogo `7c5ce80` contiene 887 ID distinti rispetto ai 877 precedenti, tutti conservati. Le candidature HR dirette aperte passano da 33 a 39, con Paesi Bassi 18 → 22, Belgio 3 → 4 e Germania 3 → 4.
- Le sei candidature del lotto sono aperte e verificate con policy v2 e modulo ufficiale della stessa vacancy. La [verifica pubblica](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44748297519) ha ricevuto HTTP 200 per homepage e catalogo e ha confrontato byte per byte il catalogo online con `7c5ce80`. SHA-256 `ed0bbca0364b4d9cad668263bd852401416e6cac08358ff171cb5783204fdd73`.
- Le quattro fonti hanno raccolto 144 schede e verificato sei candidature con 20 richieste, 15.524.027 byte e 26,61 s complessivi di lavoro per fonte. Hanno concluso senza errori. VIGO rappresenta 12.626.582 byte del lotto. Il catalogo globale resta parziale per lo stato di altre fonti.
- Prossimo passo: misurare la tenuta delle sei candidature e il costo VIGO dal prossimo ciclo ordinario già configurato.

## 20 novembre 2026 — lotto Recruitee con sei candidature confermate in staging

- Base `49f9b5f`, catalogo pubblicato con 877 ID e 33 stage con candidatura diretta. Sei nuovi ID verificati in staging portano il totale temporaneo a 883 ID e 39 stage diretti. Paesi Bassi 18 → 22, Belgio 3 → 4, Germania 3 → 4. Nessun ID precedente perso, nessun duplicato di ID e file di catalogo versionato invariato. [Prova live del lotto](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44738908240)
- Il lotto riunisce Ampelmann, VIGO, CHR Haute Senne e ABRIO. Il collector richiede feed corrente, coincidenza di titolo e ID, host rivisto e modulo pubblico per la stessa vacancy. Recruitee riusa la pagina fresca già letta per la verifica. Ampelmann ha impiegato quattro GET in questo ciclo. I candidati del lotto sono:

| Datore e sede | ID Recruitee e candidature |
| --- | --- |
| Ampelmann, Delft | [2822573 · People & Organisation](https://careers.ampelmann.nl/o/internship-people-organisation-1/c/new) |
| VIGO, Venray | [2834709 · Recruitment](https://werkenbijvigogroep.recruitee.com/o/meewerkstage-recruitment-venray-en-zetten/c/new), [2795750 · HR Leren & Ontwikkelen](https://werkenbijvigogroep.recruitee.com/o/stagiaire-hr-leren-ontwikkelen-32-uur-vigo-2027/c/new), [2532996 · HR Advies](https://werkenbijvigogroep.recruitee.com/o/afstudeerstage-hr-advies-venray/c/new) |
| CHR Haute Senne, Soignies | [2157482 · Développement RH](https://chrhautesenne.recruitee.com/o/stagiaire-en-ressources-humaines-developpement-des-ressources-humaines-soft-rh/c/new) |
| ABRIO, Francoforte | [2758064 · Recruiting & Employer Branding](https://abriogmbh.recruitee.com/o/praktikum-hr-recruiting-employer-branding-mwd-3/c/new) |

- Life Outdoor Living espone un host aziendale diverso dal tenant e un redirect esterno al perimetro verificato. Deerns pubblica URL di host estranei all'allowlist controllata. Gli indici correnti GoodDays e De Nieuwe Zaak non hanno restituito i link attesi al collector. Il controllo puntuale si è fermato rispettivamente alla prova di associazione con l'ID e alla validazione del percorso del modulo. Questi candidati restano in ricerca. [Inventario e hold](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44739418958) · [Verifica dei percorsi](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44739624176)
- Misura dei piloti live: 52 tentativi GET e 18.591.880 byte per il lotto e i controlli indipendenti. Il primo lotto ha impiegato 32 GET e 16.315.466 byte, dei quali 12.691.834 attribuiti al feed e alle pagine di VIGO. I quattro profili sono stati verificati in staging con hold prima del via libera. I rispettivi inventari sono esclusi dalle chiusure per assenza.
- Simulazione in memoria: attivazione delle sole quattro fonti, da 1.919 a 1.923 attive, zero fonti universali aggiunte, provisioning idempotente e 25 test mirati superati. La bozza consolida il codice delle [PR #80](https://github.com/nightlydeveloper8/eu-hr-internships/pull/80) e [#81](https://github.com/nightlydeveloper8/eu-hr-internships/pull/81) sulla base corrente. Rollout autorizzato il 20 novembre per le sole quattro fonti di questo lotto. La PR #86 abilita le quattro voci e rimuove i rispettivi hold. Il primo ciclo automatico deve confermare quali candidature sono pubblicabili. [Verifica di rilascio](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44739820014)

## 19 novembre 2026 — 33 candidature confermate, filtro dedicato e Ampelmann al secondo giorno

- **Raccolta ordinaria.** [Run #44479557241](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44479557241): 18/18 job riusciti. Catalogo pubblicato su main al commit [3f20f51](https://github.com/nightlydeveloper8/eu-hr-internships/commit/3f20f511092d7cd5cb12aa3428bf8b4edc0ca3e6), aggiornato alle 08:46 CET. Da `17aea99`: **816 → 835 ID**, +19 e zero persi, **379 → 398 stage attuali**. Fra i 398, **33** hanno una prova fresca del percorso di candidatura (+1, ProWurk, Surhuisterveen) e **365** sono elencati come attivi dai servizi pubblici (+18: EURES 360, JobTech 5). I 33 sono in NL 19, FR 6, BE 3, DE 3, ES 1 e PT 1. I due numeri misurano evidenze distinte. [Issue #1](https://github.com/nightlydeveloper8/eu-hr-internships/issues/1): 1.896 datori tentati, 71 collected, 34 verified-empty, 528 partial, 275 blocked-or-failed, 988 discovery-incomplete. La corrispondenza byte per byte del catalogo servito dal sito di produzione resta da verificare.
- **Interfaccia in revisione.** Il filtro **Application route confirmed** usa la prova strutturata e la verifica v2 entro 48 ore. Mappa, schede e report di copertura mostrano il livello di prova, con azione verso il servizio ufficiale o il percorso di candidatura verificato. L'impostazione iniziale continua a mostrare tutti gli stage attuali. Stessi ID, fonti, policy e cadenza. 29 casi del frontend verificati localmente. Zero richieste del collector per questa modifica, che resta sul branch della PR.
- **Ampelmann, prova live isolata.** [Run #44500469749](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44500469749) del 19/11 alle 10:53 CET. Stesso posting ufficiale `2822573` e stesso ID staging `b05fc810ebc3e04dc51b` del 17/11. Il feed XML e il modulo Recruitee pubblicato per lo stesso posting hanno prodotto +1 stage verified nello staging e conservato tutti i 363 record della baseline di prova. **5 GET, 943.779 byte, 5,741 s, 0 rendering e 0 invii.** Workflow temporaneo rimosso nel commit [81391cd](https://github.com/nightlydeveloper8/eu-hr-internships/commit/81391cddab4efeeb2d30be8a3104131337e7dc0e). Gate del giorno distinto soddisfatto. [PR #60](https://github.com/nightlydeveloper8/eu-hr-internships/pull/60) da riallineare a main e [PR #65](https://github.com/nightlydeveloper8/eu-hr-internships/pull/65) ancora in attesa della dipendenza e delle autorizzazioni. Ampelmann resta fuori dal catalogo main.
- **Prima attività residua.** Riallineare l'adapter Recruitee #60 al main attuale e verificare la compatibilità con la configurazione disabilitata #65. Per #63, portare a CI corrente la deduplica delle code prima di misurare il risparmio HTTP in produzione. L'audit precedente riguarda il 20,38% delle voci salvate, non una riduzione equivalente di HTTP. Nessun merge o attivazione in questa sessione.

## 17 novembre 2026 — riparato il gate CI che ha interrotto la raccolta programmata

**Incidente accertato:** la [run giornaliera #44038748025](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44038748025), avviata il 17 novembre 07:26 UTC dal cron (commit main `8aad7fa`), si è conclusa **failure** nel job `test` prima di `collect` e `publish` (entrambi **skipped**). Risultato: 451 test Python eseguiti, **2 falliti**, nessuna nuova raccolta né pubblicazione attribuibile a quella run. L'avviso Node.js 20 deprecato non è la causa del fallimento.

**Causa radice documentata nei log:** `tests/test_batch10_historical_ownership.py::test_real_registry_and_cumulative_finalize_preserve_existing_catalog` simulava `finalize()` con un timestamp fisso del 16 novembre alle 18:55 UTC, anteriore a verifiche più recenti del catalogo (ciclo delle 19:15); il controllo di freschezza ha legittimamente prodotto `incomplete` anziché `verified`. `tests/test_intake.py::test_published_records_ownership_policy_and_review_blocks_survive` assumeva esattamente due `review_note`, ma l'audit storico di ownership ha aggiunto altre note a record di terze parti (5 invece di 2). Sono **fixture/test non aggiornati al catalogo mutevole**, non una prova di difetto nella raccolta live né di annunci realmente chiusi.

**Correzione già pronta, revisionata e integrata:** la [PR #54](https://github.com/nightlydeveloper8/eu-hr-internships/pull/54), HEAD `252b747`, corregge entrambi i test (timestamp da `prior.last_attempt_at`; selezione esplicita degli URL con review `needs-verification`), aggiunge una regressione per `employmentType` JSON-LD contenente valori `null` e migliora il parser senza modificare i gate policy v2. Verificati i check CI [#43950990459](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43950990459) e [#43951004591](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43951004591) **success**, Cloudflare preview success, PR senza conflitti o review bloccanti. Eseguito **squash merge** su main, commit [`73d641d`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/73d641d9149e3c915cfb903708c410dbd2737b89), senza integrare PR #56 o altre PR e senza ampliare le fonti, i budget o l'allowlist.

**Ripresa della pipeline:** il push del merge ha avviato [Daily employer collection #44042092898](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44042092898) e [Validate application #44042092969](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44042092969). **Il job `test` post-merge è success**; al controllo successivo tutti i **16 shard collect risultano in progress**. Il gate iniziale della raccolta è quindi effettivamente riparato su `main`. Non dichiarare l'odierna raccolta o la pubblicazione riuscite senza controllare i successivi job `test`, i 16 shard `collect`, il job `publish`, il catalogo, il conteggio stage policy v2 e il check Cloudflare sul commit dati esatto. Il rerun del vecchio SHA non correggerebbe la causa. La ripresa è un trigger già esistente da push, non un nuovo scheduler.

**Costi/benefici:** diagnosi e revisione offline: 0 nuove richieste BudgetClient, 0 rendering, 0 candidature. Beneficio verificato prima del merge: test sulla PR verdi e fix dei due falsi fallimenti; beneficio di raccolta e costi delle richieste nella nuova run **non ancora misurati**. Non attribuire nuovi stage alla sola riparazione della CI; il conteggio confermato nell'ultimo ciclo antecedente era **27 HR internship verified** più un working student DE, non 28. Próssimo controllo concreto: esito completo della run post-merge, confronto ID/stati e produzione Cloudflare; se la raccolta si blocca nuovamente, identificare il nuovo step prima di qualsiasi ulteriore modifica.

## 16 novembre 2026 — verifica DOPO PR #53: quarantena effettiva, Malt timeout e produzione 27 stage

**Run realmente completato:** [Daily employer collection #43937080485](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43937080485), avviato dal merge PR #53 commit `656183b4e616d7ad0624770dc36465cceaf465fb`: **18/18 job success** (1 test, 16 collect, 1 publish). Il publish ha creato su `main` il commit dati [`8aad7fa`](https://github.com/nightlydeveloper8/eu-hr-internships/commit/8aad7faac950499cda60c983bd9b6b13d93093a4), catalogo `updated_at=2026-11-16T19:26:03.398409+00:00`, `update_status=partial`. Commit esatto verificato, non confondere workflow verde con copertura completa.

**Confronto programmatico dei due cataloghi (prima `9ea1373`, dopo `8aad7fa`):** 362 → **362 ID**, 0 ID aggiunti, 0 persi, 230 record modificati. **28 → 27 stage HR open/verified policy v2**; 1 working student DE resta open/verified. **Unverified 306 → 307**, closed 27 → 27. Per paesi ora NL 18, BE 3, FR **4** (prima 5), ES 1, PT 1: **zero stage nuovi verificati**. La patch #53 ha marcato realmente **108** record storici `ownership_risk=historical-unreviewed-external-host`, di cui **98 unverified** e 10 closed, senza rimuoverne ID e mantenendo i closed. Il frontend già integrato non li presenta nelle candidature non verificate. Questi 98 non costituiscono nuove offerte né risultati di raccolta.

**La singola perdita verified è identificata:** ID catalogo `6656e514ade9446b3c5e`, **Malt — HR Internship - Talent Acquisition Specialist (January 2027)**, Parigi, ID Lever `2ed4df4e-f6dc-469f-ba40-52dc5b5c508d`. Ultima verifica v2 positiva `2026-11-16T18:42:38.461536+00:00`. Il ciclo delle 19:15:43 ha prodotto `The read operation timed out` e ha declassato `status=open, verification=verified` a `status=unverified, verification=incomplete`; `last_verified_at` resta storico e non va conteggiato come nuova prova. **Non è una chiusura dimostrata.** Una ricerca contestuale online del board ufficiale Malt e della pagina `/apply` mostra ancora la stessa posizione e campi candidatura, ma non equivale al preflight corrente con BudgetClient/robots e non giustifica una promozione manuale. Primo prossimo controllo: singola fonte `lever-malt`, bounded, robots/host allowlist, inventory corrente e candidatura same-ID, registrando GET, byte, tempo e risultato; non rieseguire per questo l'intera raccolta da 1.896 aziende.

**Copertura del ciclo:** Issue [#1](https://github.com/nightlydeveloper8/eu-hr-internships/issues/1) aggiornata automaticamente con **1.896 aziende attempted; 67 collected; 33 verified-empty; 528 partial; 276 blocked-or-failed; 992 discovery-incomplete**. Issue di qualità aperta **non significa workflow failed**. Il check GitHub **Cloudflare Pages = success** sul commit dati `8aad7fa` e fornisce preview `https://98b7ed97.people-placement-eu.pages.dev`; il lettore esterno non riesce a leggere il JSON del sito, quindi **uguaglianza del catalogo pubblico e SHA256 non verificata indipendentemente**.

**Costo e impatto:** nessuna nuova fonte, host, scheduler o rendering aggiuntivo introdotto dall'audit in questa ripresa. Controllo offline dei cataloghi GitHub e lettura contestuale web; **0 nuove richieste BudgetClient** in questa attività. I costi della nuova raccolta ordinaria (richieste/byte/rendering aggregati) **non sono stati ricalcolati** dal report fonte da 3,36 MB; non attribuire risparmi non misurati. Il confronto precedente (#43931128227) misurava 36.174 richieste e 3.286 rendering; non è il costo certificato del run #43937080485. Costo monetario non misurato, zero candidature inviate e zero bypass.

**Correzione riutilizzabile proposta in questa PR (non in produzione):** `collector/employer_pages.py` evita che un elenco Schema.org `employmentType` contenente `null` interrompa l'estrazione dell'annuncio, ignora i soli elementi non testuali e conserva le evidenze dichiarate. Test offline dedicato con lista mista, lista solo null, scalare null e stringa, più controllo host non approvato. L'errore `sequence item ... NoneType` è presente nei report di cinque record del lotto 10, fra cui due DAF; **non è dimostrato** che il medesimo punto del parser sia la causa per tutti, né che questa correzione renda gli annunci candidabili. Verificare CI sulla HEAD; nessuna verifica live o guadagno di stage attribuibile alla patch. Nessun cambiamento ai gate di candidatura, ownership, robots, host o budget.

**Manutenzione della CI a seguito del catalogo aggiornato:** due regressioni precedenti alla patch di parser (riscontrate anche sulla prima commit solo-documentale) dipendevano da dati mutevoli: il test ownership simulava una pubblicazione alle 18:55 UTC precedente alle verifiche delle 19:15, per cui la regola corretta 48h declassava un record; ora il replay usa `prior.last_attempt_at`. Il test intake contava esattamente due record con `review_note`, ma dopo la quarantena ce ne sono anche di terze parti; ora seleziona soltanto le URL con review esplicita `needs-verification`, mantenendo il controllo su entrambe le vacancy esaminate. Non è cambiato il codice produttivo relativo a scadenza, ownership o deduplica. Verificare CI definitiva sulla HEAD della PR; nessun benchmark live effettuato.

**Ordine dei punti aperti:** (1) nuova verifica circoscritta del timeout Malt senza trattamento privilegiato della vacancy; (2) recupero **strutturale** delle 44 anomalie di `application entry`, delle 18 con application ID differente e delle 16 con titolo/identità discordanti, senza allentare policy v2; (3) misure multi-giorno sul costo delle 1.832 fonti senza match HR nel precedente ciclo, prima di ridurne la frequenza. **EU27: coda di ricerca prevista per 27/27, mappatura nazionale completa per 0/27; solo cinque paesi con stage verified.** Questa nota di checkpoint è una proposta documentale separata: nessun nuovo merge o attivazione.

## 16 novembre 2026 — lotto 10 NL/BE/FR/ES/PT: 108 mirror storici fuori ownership, raccolta ordinaria pubblicata

**Risultato reale:** analizzati offline i 257 annunci del lotto 10 nel catalogo delle 16:51 UTC: **28 stage HR policy v2 verified**, 209 non verificati e 20 chiusi. **108** record storici legati a `auto-tilburg-university` provengono invece da `www.nationalevacaturebank.nl` (98 unverified, 10 closed), cioè un portale esterno con tanti datori differenti, non stage ufficiali dell'università. Nessun record aveva `last_verified_at`, l'ultima osservazione era del 7 novembre. Non ampliare budget Tilburg per tentare di recuperarli come stage ufficiali.

**Modifica strutturale predisposta:** il frontend `src/logic.js` esclude inoltre le righe con `ownership_risk` dal filtro **Include unverified** e dai KPI visibili, lasciandole nel JSON storico; i record non vengono trasformati in chiusure. Test Node dedicato.  segnalare automaticamente, senza cancellare record/ID o riattribuire datori, le sole righe storiche su host diversi da quelli della fonte con `ownership_scope=reviewed-hosts` o `require_employer_identity`, eccetto trasferimenti individuali già revisionati. Conservare i closed come tali, classificare gli unverified come `review-required` e registrare un contatore di qualità nell'output. Nuovo audit offline `python -m scripts.audit_batch10_recovery` con prove negative per sorgenti legittime, storico chiuso, rehoming e status. Beneficio offline: **98 righe etichettabili come ownership non confermata**, non offerte perse; la coda di **209 unverified scende a 111 da riesaminare per prove ufficiali** (NL62, BE1, FR36, ES12, PT0). Nessun nuovo stage prodotto né fonte abilitata.

**Problemi prioritari residui:** 44 casi senza application entry, 18 con identificativo candidatura differente, 16 con titolo/identità diversa e 8 su robots 403. Controlli web puntuali: L'Oréal stage RH Parigi ID 229626 ufficiale ma CTA su altro host `careers-apply.loreal.com` respinta HTTP 406 (non approvarlo implicitamente); DAF HR Officer stage Eindhoven ufficiale ma form non attestato, lingua olandese richiesta; AXS HR Stage indicizzato, la pagina esatta restituisce 404 nel lettore; JDE BE titolo differente; Amazon ES robots non disponibile (non riprovare con workaround). Nessuna verifica di formulario sufficiente per aumentare i verified.

**Verifica richiesta della nuova raccolta ordinaria:** [#43931128227](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43931128227) **success**, 1 test + 16 collect + 1 publish riusciti. Pubblicazione su `main` commit **`9ea1373`**, 16 novembre 18:53:11 UTC: **362 record, 28 internship verified, 1 working student DE**, uguali a prima; 134 righe modificate, **0 nuovi ID, 0 ID persi e 0 verified guadagnati o persi**. Stato catalogo **partial**, report aziende: **1.896 attempted, 67 collected, 32 verified-empty, 530 partial, 277 blocked-or-failed, 990 discovery-incomplete**. Check Cloudflare Pages **success** sul commit esatto; impossibile scaricare da lettore web il JSON pubblico per confrontare SHA256: la pubblicazione indipendente lato browser resta **non verificata**. Il ciclo annullato precedente #43929695521 non va contato come riuscito.

**Test indipendenti dalla cronologia:** un fixture esistente costruiva nuovi annunci sintetici copiando anche `identity_aliases` dal primo record del catalogo, modificato legittimamente nel ciclo delle 18:53. È stato corretto il fixture per non far collidere identità fittizie, lasciando invariata la deduplica di produzione; controllare la CI della HEAD della PR.\n\n**Costo osservato del ciclo ordinario prima della correzione:** sui 1.894 rapporti aggiornati (esclusi 19 vecchi) risultano **36.174 richieste / 4.159.256.878 byte / 3.286 rendering / 43.410,44 secondi-fonte cumulati**. **1.832 fonti senza match HR in questo ciclo** consumano **34.192 richieste, 3.765.755.480 byte e 3.187 rendering**. Il costo monetario e il tempo wall-clock non sono ricavati da questi totali. Non spegnere fonti sulla base di un solo ciclo; misurare una politica conservativa di frequenza dopo l'integrazione. **Risparmio della patch lotto 10 non ancora provato in produzione**.

**Costi e confini:** audit offline e patch **0 nuove richieste collector, 0 rendering, 0 byte**, nessuna variazione di scheduling o `data/companies.json`/`data/sources.json`; la ricerca web non è metrica BudgetClient, costo monetario non misurato. Risparmio operativo effettivo del nuovo codice **ancora non misurato in produzione**. Nessun invio candidatura, login o aggiramento protezioni.

**Prove:** [BATCH-10-REVIEW.md](eu27-expansion/BATCH-10-REVIEW.md), [batch-10-recovery-audit-2026-11-16.json](eu27-expansion/batch-10-recovery-audit-2026-11-16.json). PR tecnica di questo checkpoint da controllare per CI/merge nella relativa conversazione GitHub; **la raccolta ordinaria citata è precedente alla patch**, che non deve essere presentata come già eseguita in produzione. Primo lavoro residuo: integrare solo se CI/review verdi, confrontare il primo ciclo successivo con gli stessi 362 ID e il conteggio dei 108 casi di ownership, poi lavorare sulle cause del mancato formulario senza allentare policy v2. **UE27 non mappata completamente**.

## 16 novembre 2026 — lotto 09 CZ/RO/IE/LU, PANDOO via email provata ma non promossa

**Risultato effettivo:** 4 paesi, 8 canali ufficiali nel preflight GET-only, **25 richieste, 2.410.101 byte, 22,233 secondi-fonte**, 0 rendering e **0 nuove vacancy verified**. Piste CZ SAP recruiting REF3475V (inglese + tedesco) e Amazon 10561439 (ceco + inglese), entrambi annunci/indici 200 ma senza form anonimo; RO BAT HR Intern req 81347 (form landing "Hi there") e Marquardt Mingle sUQZQQ (shell); IE TikTok 7694622895491205429 (pagina/redirect same-ID ma nessun modulo statico); LU PANDOO, EY HR Mobility Intern 1749932 e Deloitte L&D Intern 13618 (annunci pubblici, EY/Deloitte senza form). Manifesto CZ precedentemente 429 e Fidelity IE 404 non riprovati. **Nessuna fonte nuova attivata**.

**PANDOO LU:** il portale aziendale `pandoo.lu/jobs` elenca HR Intern F/M/D e la pagina ufficiale specifica `/hr-intern-f/m/d` contiene `mailto:hr@pandoo.lu` con etichetta **Apply now** e frase affermativa **“please send us your application”**. Nuovo supporto riutilizzabile per queste istruzioni inglesi dentro `application_check='official-email'`, senza cambiare policy v2, senza email inviate e senza accettare generici contatti. Il controllo finale con `verify_vacancy` sul contenuto live conferma `official-vacancy-email-instructions`, `delivery_verified=false`; riuso del documento già letto elimina un secondo GET di verification. **Non promuovere PANDOO**: la singola vacancy non specifica esplicitamente il luogo dello stage, mentre l'indirizzo Luxembourg compare soltanto nel footer societario; la sede lavorativa deve essere provata autonomamente. Nessun nuovo ID catalogo creato.

**Costo PANDOO reale:** tre run one-shot, ognuno 3 richieste / 45.842 byte, con errori di pilot nel primo (link non-HTTP) e secondo (triplice link grafico alla stessa vacancy), corretti e dichiarati; durate 5,201 + 3,786 + 3,739 secondi-fonte. **Totale lotto 09 incluse ripetizioni: 34 GET, 2.547.627 byte, 34,959 s-fonte, 0 rendering.** Nessun costo aggiuntivo quotidiano e costo monetario non misurato. Tutti i workflow pilot sono stati **rimossi** dai rami isolati, non integrati su main.

**Personio in parallelo:** PR tecnica [#51](https://github.com/nightlydeveloper8/eu-hr-internships/pull/51) **squash merged `bbfe4e8`**, CI 435 test Python/26 Node verde. I form Personio con campi nome/email/CV e submit inizialmente disabled restano **incomplete**, ma il collector evita rendering inutili senza agire sui dati personali; gli altri ATS mantengono il fallback. Beneficio economico live ancora da misurare.

**Evidenze:** [BATCH-09-REVIEW.md](eu27-expansion/BATCH-09-REVIEW.md) e [batch-09-live-preflight-2026-11-16.json](eu27-expansion/batch-09-live-preflight-2026-11-16.json), contenente i quattro run reali, redirect, hash e costi. Nuovo codice su PR review di lotto, non ancora integrato/attivato; catalogo precedente resta **362 record, 28 stage HR verified in cinque paesi + 1 working student DE** (ultimo snapshot 16:51:25 UTC). La CI, eventuale merge e produzione vanno verificati separatamente.

**Primo punto incompleto:** provare la località effettiva dello stage PANDOO su fonte ufficiale, poi eventuale proposta azienda+fonte disabled e approvazione specifica del rollout. Non attivare sulla sola sede legale. Per CZ/RO/IE cercare nuovi canali con modulo consentito e verificabile. Successivo lotto geografico **10 — NL, BE, FR, ES, PT**; **nessuna copertura nazionale UE27 dichiarata completa**.

## 16 novembre 2026 — lotto 08 AT/DE/DK/FI/PL/SE, feed Personio validi ma nessuna candidatura v2

**Risultato effettivo:** 6 paesi esaminati, 7 canali ATS/aziendali sottoposti a GET read-only su GitHub Actions isolata, più un controllo dei moduli e feed. **Zero nuovi stage HR candidabili e verificati policy v2, zero nuove fonti attivate, zero nuovi paesi con stage verified**. Catalogo di riferimento invariato nell'ultimo ciclo realmente letto: **362 record / 28 stage verified in 5 paesi + 1 working student DE** (16 novembre 16:51:25 UTC). L'ultima validazione post-merge di #49, [#43920247195](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43920247195), è **success**. Nessuna evidenza di aumento della produzione attribuibile al lotto 08.

**Fonti e blocchi principali:**
- **DE Audi Business Innovation:** corporate→Personio esatto pubblicato; board e vacancy **2540621** e application same-ID HTTP 200; feed Personio XML corrente **4 posizioni totali**; form con 18 campi, CV/email/nome, ma **submit inizialmente disabled**. Il solo sito corporate Audi durante prova BudgetClient ha dato `robots.txt unavailable: 403`; Personio invece ha superato robots sulle URL consentite. Non accedere al corporate HTML in presenza del blocco.
- **DE Studyflix:** board/XML Personio corrente **19 posizioni totali** (non 19 stage), vacancy HR **1119149**, modulo con 8 campi ma **submit disabled**; collegamento datore→tenant esatto da riconciliare. Non verified.
- **FI StaffPoint:** HR-harjoittelija HoReCa **3Bkmpb**, deadline 22 novembre; employer site e CTA Talentadore 200, ma nella form statica solo token/hidden + `form_json`/timezone/submit, **non** nome/email/CV. Altra form riguarda withdrawal; non verified.
- **AT Peek & Cloppenburg:** corporate e CSOD 200, ma solo ATS shell e nessun specifico posting ID; annuncio HR da terzi non prova vacancy ufficiale. **DK Maersk** req R199126 Workday solo shell; **PL Michael Page** Stażysta HR JN-112026-7142697, 200 ma categoria `Stała` e form non provata; **SE SnabbPass** Talent Acquisition & Digital Growth Internship misto, listing 200 ma nessun form attivo; vecchi GANT e Compass HRG esplicitamente non disponibili.

**Costo misurato** su ramo pilota: [primo preflight #43923132314](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43923132314) **28 richieste / 3.005.009 B / 21,121 s-fonte**; [ripetizione involontaria su push #43923524759](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43923524759) **28 / 3.003.820 B / 17,131 s**; [diagnosi #43923560176](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43923560176) **8 / 497.931 B / 4,885 s**. **Totale reale 64 richieste, 6.506.760 B, 43,137 s-fonte, zero rendering**. Registrare la duplicazione impedisce una sottostima. Tutti i run sono success; il workflow temporaneo è stato **rimosso dal ramo pilota**, mai inserito in main; nessun aumento delle richieste quotidiane o del costo collector in produzione. Nessun login, modulo compilato, POST, CAPTCHA, candidatura o ampliamento rollout.

**Evidenze riproducibili:** [BATCH-08-REVIEW.md](eu27-expansion/BATCH-08-REVIEW.md) e [batch-08-live-preflight-2026-11-16.json](eu27-expansion/batch-08-live-preflight-2026-11-16.json), con hash e dati di struttura senza dati personali. Modificati soltanto documenti e stato in PR separata, nessun cambio codice fonte/registri/catalogo/workflow di produzione. PR #41 e #46 restano draft non pronte.

**Primo punto incompleto:** decidere tramite review policy v2 come valutare form Personio che disabilitano il submit finché l'utente non compila i campi; **non** promuovere lo stage né fingere di abilitarlo. Valutare provider con app form abilitato e identità esatta, integrare solo quelli policy v2 validi. **Lotto 09 CZ/RO/IE/LU** è il prossimo geografico e non equivale a copertura nazionale completa.

## 16 novembre 2026 — lotto 07 CY/GR/HR/MT, GET pilot misurato senza fonti attive

**Risultato reale:** 8 indizi esaminati in 4 paesi, tre vacancy HR di fonte ufficiale con identità precisa ma **0 nuove candidature verified policy v2** e **0 nuove fonti enabled**. Baseline di produzione invariata nell'ultimo catalogo letto: **362 record, 28 stage HR open/verified in 5 paesi, 1 working student DE** (16 novembre 16:51:25 UTC). Nessun rollout né aggiornamento del catalogo da questo lotto.

**Piste prioritarie e prove:** Brainstorm Hospitality **CY** HR Intern Larnaca, Teamtailor ID **7649525**, inventario aziendale corrente e pagina specifica; form dinamico non leggibile in HTML statico. iKnowHow **GR** HR Intern (Talent Acquisition), Workable ID **3F368EAC02**, collegamento corporate→tenant esatto; form HTML statico assente e feed del board non stabilito. Marriott Westin **MT** HR Intern, ID **26132701**, listing aziendale e CTA Oracle con job ID conservato, ma l'HTML della pagina Oracle non mostra campi per candidarsi. Requisiti iKnowHow inglese fluente e iscrizione a istituto greco, Marriott stage 5–6 mesi/€835 lordi mensili. **Croazia:** Rimac People Operations Intern non appare nel board attuale nonostante la pagina vecchia; PLIVA AskHR scaduta il 9 novembre ed è working student, non stage. Xara MT HR Intern solo su mirror, Hilton MT solo fonte terza, Stoiximan CY programma HR senza vacancy corporate attuale: nessuno ammesso.

**Preflight GET reale e limitato:** su ramo separato di GitHub Actions, [run #43918927512](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43918927512) **success**. Client originale BudgetClient con controllo robots attivo e allowlist redirect esatta. **11 richieste logiche totali**, di cui Brainstorm 3, iKnowHow 3, Marriott/Oracle 5; **1.356.253 byte letti** e **5,403 secondi-fonte cumulati**, **0 rendering, 0 HTTP 429**. Le 3 vacancy hanno HTTP 200, ma **nessuna pagina ha mostrato campi e submit anonimi abilitati**. La guardia robots ha consentito *queste URL*; il dump non registra direttive/status dei robots, né prova accesso all'intero sito. L'ambiente locale aveva DNS non disponibile, perciò la prova è stata eseguita sul runner; solo GET, niente login, CAPTCHA, POST o candidature. Nessuna fonte attivata: **incremento richieste quotidiane 0**, costo effettivo del singolo test 11 GET e 1,36 MB, costo monetario non misurato.

Prove in [BATCH-07-REVIEW.md](eu27-expansion/BATCH-07-REVIEW.md), [JSON indizi](eu27-expansion/batch-07-review-2026-11-16.json) e [JSON del probe live](eu27-expansion/batch-07-live-preflight-2026-11-16.json); il workflow pilota NON è su main, non è programmato come raccolta quotidiana. Modificati solo documenti e stato, PR dell'attività da verificare CI/merge. Le PR #41 e #46 restano draft indipendenti e non ready.

**Primo punto incompleto:** individuare per Teamtailor/Workable un percorso ufficiale e riutilizzabile verso il vero modulo anonimo senza abilitare indiscriminatamente renderer o variare policy v2; Oracle resta blocked/unverified quanto a form. In HR trovare una vacancy corrente sostitutiva. **Prossimo lotto 08: AT/DE/DK/FI/PL/SE**. Non dichiarare mappatura completa dei quattro paesi.


## 16 novembre 2026 — lotto 06 (EE/LV/LT/BG/IT/HU/SI/SK), audit UE27 senza rollout

**Baseline dopo PR #47:** workflow #43909444414 (raccolta) e #43909444577 (validazione) riusciti. Catalogo main 16 novembre 16:51:25 UTC: **362 annunci, 28 stage HR verified in cinque paesi, 1 working student DE, 306 unverified, 27 closed**. PR #47 squash merge 5364825: fix host 429 e messaggi filled. Nessun nuovo stage verificato attribuibile al lotto 06.

**Ricognizione lotto 06:** 8 paesi, 10 indizi, 9 datori, **0 nuove fonti abilitate / 0 nuove candidature policy v2**. Piste ancora non ammesse: DIGI MEDIA LV (ruolo HR e form visibile sulla pagina aziendale), Girteka LT (stage HR ma candidatura /talentcommunity incompleta), CCEP BG (People Services 2027, inglese e tedesco, form non stabilito), Heritage IT (due HR stage nel board Greenhouse corrente, ID 4945490101/4945390101, moduli presenti ma manca link dal sito corporate al tenant esatto). Altre cinque evidenze: Gameloft BG candidatura expired; Bolt EE scadenza esterna passata; Betsson HU ruolo non presente nel board corrente; Danfoss SI rimosso; Adient SK working student e non stage.

Prove in [BATCH-06-REVIEW.md](eu27-expansion/BATCH-06-REVIEW.md) e [JSON](eu27-expansion/batch-06-review-2026-11-16.json). [Piano EU27](eu27-expansion/EU27-MAPPING-PLAN.md) assegna i 27 paesi ai lotti 06–10 senza sovrapposizioni, ma pianificare non equivale a mappare. Nuovo script audit offline dei 27 paesi e test con filtro v2/freschezza, nessuna nuova esecuzione programmata. Nessuna copertura nazionale dichiarata completa.

**Costi:** 0 nuove richieste collector, 0 rendering e 0 carico quotidiano aggiuntivo perché nessuna fonte attivata. Ricerca web svolta, ma byte/durata/richieste web non misurate come costi collector. Accesso HTTPS diretto al preflight bloccato da DNS e robots dei canali prioritari non disponibili al tool: nessuna prova completa di inventario/candidatura.

**Primo punto incompleto:** preflight limitato con BudgetClient e robots su DIGI MEDIA LV e Heritage IT (una fonte, due posizioni), poi Girteka LT se il link arriva a modulo stesso annuncio. Misurare richieste, secondi, byte, deduplica e ripetibilità su due cicli. Review CI della PR audit e procedere col lotto 07 CY/GR/HR/MT senza promuovere indizi bloccati.

## 16 novembre 2026 — lotto 04 attivo e produzione verificata

**Risultato reale: 26 → 28 stage HR verificati, più 1 working student in Germania.** Tre nuove fonti ufficiali attive: Hotel TwentySeven (stage NL, Amsterdam), Bundl (stage BE, Antwerp) e Franklin Institute (posizione mista DE, München, conteggiata working student). Nessuna candidatura inviata, nessuna raccolta completa manuale, nessun gate Dynamic ATS o schedule ampliato.

L'utente ha autorizzato prossimo lotto e squash and merge autonomi del lavoro pronto: **PR #44 merged `464d87c` e PR #45 merged `8ab36e9`**. CI PR45 head `f406f16`: 413 Python, 26 Node, 64 esempi, coverage e build; run #43901346530/#43901406534 e dopo merge #43901780674 riusciti. PR #41 resta draft non pronta e non viene integrata. Autorizzazione agli squash pronti da mantenere senza richiederla nuovamente.

**Primo ciclo ordinario dopo #45: [#43901780885](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43901780885), tutti i 18 job riusciti.** Dati main `d764bececa798a089893754afde022dff9a2f90e`, catalogo 16:08:16 UTC: **356 → 361 record, tutti i 356 ID precedenti conservati**, tre nuove candidature verificate; due altre aggiunte automatiche TNG/Yobbers restano unverified. Tutte le vecchie opportunità verificate conservate. Cloudflare Pages riuscito sullo stesso commit dati; GET pubblico 200 alle 16:09:32 UTC, 888.716 byte identici alla pubblicazione, hash nel rapporto. Il ciclo #44 #43898333473 era riuscito con 26 stage invariati; BSH inglese ora documented, sufficienza da solo unknown.

Costi di produzione delle tre fonti: **15 richieste logiche / 8,84 secondi-fonte / 3.768.689 byte / zero rendering**. Ciascuna usa 5 richieste, entro massimo 12/45 s, solo il proprio host Recruitee. Inventari 24+6+11 offerte, un match verificato ciascuno; completezza solo del feed restituito, closure_complete=false. Nuove aziende/fonti applicate atomicamente. Correzione riutilizzabile del client: documenti HTML, API JSON esplicito, robots testo semplice; identità bot, host, robots e budget preservati. Nessun catalogo promosso manualmente.

Bundl richiede inglese+olandese; Franklin tedesco+inglese nel testo, costrutto non ancora estratto; Hotel lingua unknown. Nessuna offerta dichiarata English-only, nessuna dimensione PMI inferita. Opportunità verificate per paese: NL 18 stage, FR 5, BE 3, ES 1, PT 1; DE 1 working student e 0 stage. **UE27 ancora incompleta**, non presentare sei paesi con qualche opportunità come sei mappature complete. Quadro dei 27 paesi in [COUNTRY-OUTCOMES.md](eu27-expansion/COUNTRY-OUTCOMES.md).

Ricerca/ammissione lotto 04: 52 richieste/26,114 s/11.849.666 byte, nove query web, zero rendering (include letture CMS errate e asset JS Social Hub da circa 4,7 MB, escluso dal monitoraggio). Kickmaker 403 intermedio, Zero Motorcycles e Social Hub ownership incompleta, Settels inizio febbraio 2026 e controllo datore fallito: nessuno attivato.

Lotto successivo preparato durante il ciclo: CZ/RO/SE/IE, 27 richieste/14,721 s/1.222.790 byte e 14 query, zero nuove fonti/verified. Manifesto CZ: corporate→tenant esatto confermato, 8 link, stage non retribuito ceco+inglese; modulo non stabilito, cinque URL distinti 429. Nessun ulteriore accesso oggi; il lettore generico continua altri URL dopo primo 429, difetto da correggere prima di ammettere questo canale. Singola offerta Continental RO esplicitamente chiusa; Fidelity IE 404, nessun retry; Electrolux SE JR81378 con sede strutturata Stockholm, candidatura/inventario incompleti. Non contare questi indizi come stage candidabili.

Prove: [rapporto di produzione](eu27-expansion/batch-04-first-production-cycle-2026-11-16.json), [review lotto 04](eu27-expansion/BATCH-04-REVIEW.md), preflight lotto 05 e `next-structural-priorities-2026-11-16.json`. **Primo punto incompleto:** verificare inventario/candidatura Electrolux SE e cercare sostituti ufficiali per le due offerte RO/IE non disponibili, senza ripetere i blocchi del giorno. In parallelo diagnosi della causa comune dei link senza identificativo partendo dai 13 record L'Oréal: sono record unverified, non 13 recuperi promessi; totale 36 di quel motivo nel catalogo di baseline. Nessun nuovo controllo AI futuro configurato.

## 16 novembre 2026 — lotto DE/DK/PL/FI verificato, nessuna nuova fonte ammissibile

**Quattro indizi → zero nuove fonti attivabili, zero nuovi stage aggiunti.**
Consegna nella [PR #44](https://github.com/nightlydeveloper8/eu-hr-internships/pull/44),
ramo `review/eu27-de-dk-pl-fi-20261116`, base main `876794a`.
Rapporto [BATCH-03-REVIEW.md](eu27-expansion/BATCH-03-REVIEW.md) e
[evidenze JSON](eu27-expansion/batch-03-review-2026-11-16.json).

Constructor: 28 posizioni nel feed, uno stage HR a Bremen, ID 4772353101,
modulo stesso titolo/ID visibile abilitato. Marchio e sito coerenti, ma nessun
collegamento ufficiale azienda→tenant esatto stabilito nelle pagine consentite.
Careers usa l'endpoint pubblicato `/api/v2/jobs`, vietato da robots: contenuto
non scaricato. Proposta incompleta fuori runtime in
`batch-03-constructor-pending-proposal.json`; non integrare sulla sola prova del
modulo o del backlink ATS→azienda. Limite di 12 richieste raggiunto; stop su questo caso.

FirstMind: 38 posizioni nel feed, Global Talent Intern assente, zero HR studenti
classificati; non è un errore attuale del filtro e non si promuovono ruoli sales.
Saint-Gobain: scheda HTTP 403 dopo robots 404, nessun retry; inventario e
candidatura sconosciuti, datore già censito. Barona: JobPosting 116361 a Tampere,
collegamento corporate→Barona Careers confermato; pagina “Sign in and Apply”,
nessuna candidatura anonima stabilita e nessun login. Inglese e finlandese
elencati, non una proposta di lavoro con solo inglese.

Preparati due miglioramenti riutilizzabili: forme polacche Stażysta/Stażystka
riconosciute, “staż pracy” distinto dall'esperienza richiesta in ruoli permanenti;
“Inglés nivel B2” riconosciuto con esclusione di corsi/CV e gestione di
opzionalità/negazione. Replay BSH: requisito inglese unknown → documented,
**inglese sufficiente da solo resta unknown**, nessuna disponibilità o timestamp
rinnovati. La lingua del CV e i corsi Constructor restano esclusi.

**407 test Python, 26 Node, 64 esempi e build passati**, 12 nuove regressioni.
Costo verifica: **22 richieste logiche, 10,940 secondi-fonte cumulati,
1.962.584 byte, zero rendering**, più cinque query web. Budget per datore 12/45 s
rispettato. Catalogo/registri/workflow invariati, nessun gate/host di produzione
esteso, nessun merge o attivazione; baseline **26 stage verificati** preservata.

**Primo punto incompleto:** review della PR con i filtri corretti; eventuale
merge richiede autorizzazione specifica. Nuovo lotto con collegamento pubblico
datore→ATS e candidatura anonima controllati in anticipo. Constructor resta
incompleta per ownership; non spendere una nuova sessione soltanto sui blocchi
di questo lotto e non aggirare 403/API vietate/sign-in.

## 16 novembre 2026 — BSH attiva, primo ciclo e pubblicazione verificati

**Risultato reale: 25 → 26 stage HR aperti e verificati (+1 distinto), primo
stage verificato in Spagna.** PR [#43](https://github.com/nightlydeveloper8/eu-hr-internships/pull/43)
integrata con squash su autorizzazione specifica dell'utente: head attivazione
`d0903bd01f75617aeb3453adcb5234b958f55119`, merge
`e101e7415b08c14b543a259053f1e67719310b5e`. CI e preview verdi, nessuna review
bloccante; 395 test Python, 26 Node e build superati.

Azienda `bsh-electrodomesticos-espana` e fonte `index-bsh-es` aggiunte insieme:
1.892 → 1.893 aziende, 1.936 → 1.937 sorgenti. Fonte abilitata su main,
unico host `jobs.bsh-group.de`, budget 10 richieste/75 s, crawl-delay 10 s;
provisioner idempotente. Nessun altro gate, host di produzione o schedule esteso.
Rollback: revert congiunto di azienda e fonte; disabilitare solo la fonte
lasciando l'azienda attiverebbe il fallback generico.

Raccolta ordinaria avviata automaticamente dal merge, evento push:
[run 43878488280](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43878488280),
**18 job riusciti**, publish `946ebb7911641301defebd6e2d4d403210ead018`.
Catalogo del 16 novembre 14:56:56 ora svizzera (13:56:56 UTC): **352 → 355 ID**,
tutti i 352 precedenti preservati, nessun precedente stato modificato.
Un nuovo stage verificato: BSH, Prácticas Recursos Humanos - Formación,
Zaragoza, ID 46112. Gli altri due nuovi record (FITZ traineeship e Rohde & Schwarz
working student) restano **unverified** e non aumentano le opportunità disponibili.
Conteggio frontend confermato: **26 verifiedInternships**, zero altri tipi verificati.

BSH nel ciclo: 15 posizioni effettive, una corrispondenza HR con prova live
policy v2, inventario completo nello scope revisionato, nessun errore;
**5 richieste logiche, 61,16 secondi-fonte, 109.503 byte**, budget rispettati.
Zero rendering nel percorso BSH; non è il tempo a muro dell'intero workflow.
Chiusure per assenza ancora disabilitate; un solo ciclo ordinario non prova
il refresh seguente o disponibilità futura. Annuncio spagnolo, inglese B2
documentato manualmente; la frase B2 non è ancora riconosciuta dall'estrattore,
solo inglese non stabilito: nessun tag forzato.

Cloudflare Pages success sul commit dati `946ebb7`, deployment
`f093bcb5-b3be-4c5c-82ec-b2967fa7a32b`. Catalogo pubblico GET HTTP 200 e identico
byte per byte al file Git: pubblicazione e distribuzione effettivamente verificate.
Nessuna modifica manuale del catalogo, importazione di replay, workflow_dispatch,
raccolta completa manuale o nuova automazione AI. La pianificazione quotidiana
preesistente resta invariata (06:17 UTC, 07:17 ora svizzera in questa data).
Report: [bsh-first-production-cycle-2026-11-16.json](eu27-expansion/bsh-first-production-cycle-2026-11-16.json);
autorizzazione/baseline/rollback: [bsh-activation-2026-11-16.json](eu27-expansion/bsh-activation-2026-11-16.json).

Stage verificati osservati: NL 17, FR 5, BE 2, PT 1, ES 1. Sono cinque paesi con
opportunità recenti, non cinque mappature nazionali complete; gli zeri negli
altri paesi non provano mercati vuoti. Durante l'attesa preparati quattro indizi
ufficiali per DE/DK/PL/FI in
[next-uncovered-country-leads-2026-11-16.json](eu27-expansion/next-uncovered-country-leads-2026-11-16.json),
8 query di ricerca, zero feed letti o nuove fonti attivate. Saint-Gobain è già
censita e richiede un nuovo canale-paese, non una nuova azienda.

**Primo punto incompleto:** verificare in lotto identità, inventario, candidatura
e lingue dei nuovi canali DE/DK/PL/FI, priorità agli indizi HR espliciti già
compatibili col classificatore. FirstMind richiede prova delle mansioni HR,
Saint-Gobain review della forma polacca Stażysta/Stażystka. Mantenere fuori
runtime le proposte fino a nuova autorizzazione specifica. Il secondo ciclo BSH
compete alla raccolta ordinaria; nessun controllo AI futuro promesso.

## 16 novembre 2026 — lotto IT/ES/PT/AT verificato, BSH preparata senza rollout

**Otto indizi → una nuova integrazione ammissibile (BSH Spagna), una candidatura già in produzione (Emma), sei indizi non ammissibili.** Consegna nella [PR #43](https://github.com/nightlydeveloper8/eu-hr-internships/pull/43),
ramo `review/eu27-it-es-pt-at-20261116`, base main `2e68639182be2bda95cc2c9bf87b1d065c6ffc57`.
Rapporto [BATCH-02-REVIEW.md](eu27-expansion/BATCH-02-REVIEW.md), evidenze e costi
[batch-02-review-2026-11-16.json](eu27-expansion/batch-02-review-2026-11-16.json).

BSH: collegamento ufficiale datore→portale, 15 posizioni effettive coincidenti
con il conteggio pubblicato, due candidature spontanee escluse. Uno stage HR
Formación a Zaragoza, ID 46112; modulo dello stesso ID/titolo visibile abilitato.
**Pilota singola fonte riuscito: 5 richieste, 60,682 secondi, 109.503 byte,
zero rendering/errori**, budget 10/75 rispettato; crawl-delay 10 s e redirect
rispettati. Beneficio potenziale +1; **zero nuovi annunci pubblicati**.
Annuncio spagnolo, inglese B2 documentato; solo inglese non stabilito e frase B2
non ancora riconosciuta dall'estrattore automatico delle lingue, senza tag forzati.

Correzioni riutilizzabili: prefisso spagnolo Prácticas nel filtro; scope esatto e
conteggio degli elenchi, titoli completi opt-in prima di aprire le schede;
`publication-linked` verifica CTA osservata, identità e modulo dello stesso ID.
**395 test Python, 26 Node, 64 esempi e build superati**, 11 nuove regressioni,
due cicli offline con ID conservati. Fixture non sono nuove prove live.
Dopo il pilota corretta l'etichetta di report sui titoli: comportamento di rete
invariato. Bundle [batch-02-integration-bundle.json](eu27-expansion/batch-02-integration-bundle.json)
fuori runtime, fonte disabilitata: nessun registry/catalogo/workflow modificato,
nessun merge, gate o host di produzione esteso. Inserire azienda e fonte attiva
insieme solo dopo autorizzazione specifica, evitando fallback generici.

Altri esiti: Ginori/Kering e ENGIE bloccati da robots sul percorso di candidatura;
Gucci rimanda al listone (non dichiarato chiuso); Société Générale reindirizza
via JavaScript al login Taleo (nessuna autenticazione); Revolution Event ha XML
con 8 posizioni e una HR ma submit disabilitato/cf-turnstile e paese office non
risolto dal connettore; Unit4 429 su robots, nessun retry; Emma già verificata,
nessun doppione o nuova richiesta. **Costo totale lotto e pilota: 39 richieste
logiche, 115,265 secondi-fonte cumulati, zero rendering**, più tre query web.
Produzione resta baseline 352 record / 25 stage verificati del ciclo precedente.

**Primo punto incompleto:** review della PR, eventuale attivazione specificamente
autorizzata e primo ciclo ordinario BSH; nessuna raccolta completa manuale o
nuova automazione. Proseguire la ricerca di canali accessibili nei paesi non
coperti senza concentrare la sessione sui blocchi tecnici di questo lotto.

## 16 novembre 2026 — cinque fonti attive, primo ciclo e sito verificati

**Risultato reale: 20 → 25 stage HR aperti e verificati (+5 distinti, +25%).**
PR [#42](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42) integrata
con squash su autorizzazione specifica dell'utente: head `bb2dfbd`, merge
`87e3c56fa0daac6e5badccabde713e2210a3f1a2`. CI e preview verdi, nessuna review
bloccante. 384 test Python, 26 Node e build superati.

Aggiunti insieme cinque datori e cinque sorgenti Recruitee abilitate:
Monsterscore e SKYTREE (NL), Ibexa (BE), Gérard Bertrand e SAS LOOK UP SPACE (FR).
Quest'ultimo è diritto sociale a supporto HR: sottotipo esplicito.
Registro 1.887 → 1.892 datori, 1.931 → 1.936 sorgenti; provision idempotente.
Ogni sorgente usa soltanto il tenant esatto revisionato, `recruitee-linked`,
12 richieste/45 s. Nessun altro host, gate Dynamic ATS o schedule esteso.
Rollback: revert congiunto delle cinque aggiunte aziende/fonti; disabilitare le
sole fonti lasciando i datori genererebbe fallback generici via provisioner.

Il merge ha avviato il workflow esistente, evento push, senza workflow_dispatch:
[run 43857890201](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43857890201),
**18 job riusciti**, pubblicazione automatica `00b211644fb3fb8194b4b65b555b7ee22d243b97`.
Catalogo 16 novembre 11:41:24 UTC: **347 → 352 ID**, tutti i 347 precedenti
preservati, cinque nuove candidature con prova live policy v2. I due cambiamenti
su record precedenti sono unverified → closed, senza riduzione dei 20 verified.
Conteggio della logica frontend confermato: 25 verifiedInternships.

Costo incrementale delle cinque fonti nel ciclo: **25 richieste (5 ciascuna),
16,1 secondi-fonte cumulati, 5.052.141 byte**, nessun errore; budget rispettati.
Non è la durata a muro dell'intero workflow né un costo monetario misurato.
Inventari completi; `closure_complete=false` resta esplicito: questo primo ciclo
non dimostra ancora il refresh successivo o il comportamento di chiusura live.
Rapporto: `docs/eu27-expansion/first-production-cycle-2026-11-16.json`;
autorizzazione/configurazione: `activation-2026-11-16.json`.

**Produzione verificata:** Cloudflare Pages success sul commit dati `00b2116`,
deployment `04844850-2805-45e9-977c-beb80a2b6a63`. GET del catalogo pubblico
HTTP 200, timestamp e 352 record corrispondenti, confronto byte per byte identico
al file su Git. Nessuna modifica manuale del catalogo o importazione di replay.
La raccolta quotidiana preesistente rimane schedulata alle 06:17 UTC.
Nessuna nuova automazione AI configurata.

**Limiti e primo punto incompleto:** il successo di questi cinque canali non
rende completa la copertura UE27. Il report generale conserva 321 datori
blocked-or-failed, 514 partial e 964 discovery-incomplete; non sono inventari vuoti.
Restano 24 proposte del primo lotto non ammissibili. Per espandere i paesi,
preparati otto indizi ufficiali in IT/ES/PT/AT in
`next-country-leads-2026-11-16.json`: ancora da rivedere, nessuna fonte attivata.
Deduplicare Kering/Ginori/Gucci come gruppo; Emma è già monitorata; ENGIE ES
richiede review di host diverso dall'attuale fonte italiana. Prossimo intervento:
verificare in un lotto datore→ATS, accesso, inventario e candidature dei nuovi
canali IT/ES/PT/AT. Ulteriore rollout richiede autorizzazione specifica.
Il secondo ciclo live delle cinque fonti compete alla pianificazione ordinaria;
nessuna promessa di controllo AI automatico successivo.

## 16 novembre 2026 — verifica delle 29 proposte, cinque integrazioni ammissibili

Richiesta esplicita: verificare datore→ATS, feed, inventario e candidature delle
29 proposte, preparando l'integrazione senza merge o attivazioni. La PR #42 è
ancora aperta allo head `7d5940b`; questo lavoro ne completa il contenuto.

- **29 feed tentati, 21 inventari letti, 366 posizioni e 20 ruoli HR per studenti
  classificati.** Quattro fonti hanno risposto 429, senza retry. Tre XML Personio
  404; Hotel Beveren pubblica URL su un host diverso non approvato e rimane
  escluso. Le otto letture non stabilite non sono inventari vuoti.
- **Cinque stage distinti con prova live completa del pilota:** Monsterscore
  (HRM, Amsterdam NL), SKYTREE (HR & People Operations, Amsterdam NL), Ibexa
  (Human Resources, Louvain-la-Neuve BE), Gérard Bertrand (SIRH, Narbonne FR),
  SAS LOOK UP SPACE (diritto sociale a supporto HR, Toulouse FR).
  Per ognuno: collegamento ufficiale del datore al tenant esatto, feed letto,
  ID/titolo/datore corrispondenti e candidatura con campi visibili abilitati.
  Non equivalgono a cinque annunci già pubblicati sul sito.
- Correzione riutilizzabile **opt-in** `application_check=recruitee-linked`:
  conserva l'entry di candidatura realmente pubblicata nel feed, senza inventare
  `/c/new`; verifica ID/titolo/datore sulle due pagine, percorso, host, redirect,
  chiusure/scadenze e modulo visibile. Evita di prendere per prova il form nella
  scheda nascosta della vacancy. Connettori Recruitee già registrati invariati.
- Bundle fuori dal runtime: `docs/eu27-expansion/reviewed-integration-bundle.json`,
  cinque aziende/fonti disabilitate, metadati e prove. **Non aggiungere da sole
  aziende con fonti disabilitate:** `daily.provision` attiverebbe crawler generici.
  L'eventuale attivazione richiede integrazione congiunta nel medesimo commit e
  autorizzazione specifica. Nessun registry, catalogo o workflow modificato.
- Verifica offline su risposte salvate con il codice finale: due cicli
  **347 → 352 ID e 20 → 25 open/verified**, tutti gli ID precedenti conservati,
  idempotenza confermata. È una simulazione, non un conteggio di produzione e
  non rinnova le evidenze live. Il futuro collector dovrà rileggere tutto live;
  nessuno snapshot di questo pilota viene importato nel catalogo.
- Costo totale delle fasi: **165 richieste logiche**, 83,071 secondi-fonte,
  24,570 secondi a muro cumulati dei processi, zero rendering; massimo osservato
  10 richieste per datore su budget 12/45 secondi. Ulteriori 16 query web e
  7 aperture/find per la ricerca di pagine ufficiali; costi monetari non misurati.
- Restano **24 proposte non ammissibili**, con motivi nel report `REVIEW.md`:
  accesso/feed, identità societaria/pubblicatore, applicazione o classificazione.
  Altares e Toreon non mostrano nel feed lo stage HR indicizzato; non è una prova
  generale di chiusura. threon HRIS richiede review del filtro. Dimensioni/gruppi
  non qualificati come PMI; lingue e intake sconosciuti rimangono tali.

Consegna nella [PR #42](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42),
con estensione opt-in e bundle disabilitato. **384 test Python 3.12, 26 Node,
64 esempi di classificazione e build superati**; dieci nuove regressioni sul
percorso Recruitee e due cicli con ID preservati. CI sul nuovo head da verificare.

**Primo punto incompleto:** review della modifica e del bundle dei cinque datori,
poi integrazione/attivazione solo con autorizzazione specifica. Dopo attivazione,
misurare il primo ciclo ordinario reale (cinque prove pilota non garantiscono
cinque nuove vacancy ancora aperte in quel ciclo). Avanzare in modo indipendente
su fonti dei paesi successivi, senza ritentare qui i quattro 429 né avviare una
raccolta completa manuale. Nessuna nuova automazione o schedulazione configurata.

## 16 novembre 2026 — coda UE27 e primo lotto di espansione preparati

Ripresa del lavoro locale interrotto sul ramo `plan/eu27-expansion-20261115`,
checkout isolato `fix-jde-20261115`. Base aggiornata al main `e99f263` senza
sovrascrivere il lavoro delle altre sessioni. Il catalogo delle 09:06 UTC ha
347 record e 20 open/verified; nessun aumento attribuito a questa preparazione.
La PR #40 è merged; #18/#23 restano aperte e non limitano la ricerca UE27
richiesta esplicitamente dall'utente. NL resta prioritario senza attendere la
mappatura completa delle 12 province per ricercare nel resto dell'UE.

- Generatore offline riproducibile e coda per **27 paesi**, 1.926 identità di
  ricerca, 2.202 attività su canali. Riutilizza registro, esiti recenti, catalogo
  e scansioni esistenti. Le 39 nuove identità web sono da rivedere per gruppo e
  dimensioni: non sono aziende giuridicamente uniche accertate o fonti attive.
- **Primo lotto: 37 attività**, NL 11, BE 10, DE 11, FR 3, IE 2: 34 nuovi canali
  candidati e 3 conversioni di crawler generici (2-CNNCT, Gemeente Achtkarspelen,
  VTG GmbH Ingenieurbüro). Non è stato raggiunto l'obiettivo iniziale di 50:
  connettori dedicati già attivi, vecchi recuperi, identità condivise e prove
  contraddittorie sono esclusi, senza riempire il lotto con lavoro duplicato.
- **29 bozze per adattatori già disponibili**, tutte disabilitate nel solo
  documento `batch-01.json`; nessun file di produzione le carica. Restano da
  dimostrare collegamento datore/tenant, identità del gruppo, accesso del feed,
  completezza dell'inventario, sede e candidatura policy v2. Dimensioni non
  qualificate per tutte le 37 attività: quota PMI della strategia non dimostrata.
- Preflight live limitato a una pagina già osservata per canale supportato:
  **33 datori, 34 tentativi** (Zero Motorcycles ha poi una nuova URL vacancy
  osservata, distinta dalla precedente URL solo candidatura), **64 richieste
  logiche, 7.137.457 byte, 34,168 secondi-fonte, 16,583 secondi a muro cumulati**
  dei due processi, zero rendering. Robots e redirect sul solo host esatto
  rispettati; nessuna candidatura, API inventory o raccolta completa.
- **28 pagine con titolo corrispondente**, non 28 candidature verificate.
  DocMedico 404; JD Sports FR restituisce board Netherlands; Theodo timeout;
  Hospitality Recruiters redirect fuori scope, non seguito. Fidelity già
  contraddetta da apertura 404 resta fuori dal lotto. eXtra Shop richiede
  revisione del titolo e distinzione alternance/stage. Nessun aggiramento.
- Ricerca web complessiva delle due sessioni: 40 query e 6 aperture; costi
  monetari non misurati. **Nuove fonti attivate 0, nuove candidature verificate 0**.
  Report: `docs/eu27-expansion/README.md`, `queue.json`, `batch-01.json`, manifest
  degli indizi e due preflight con URL, date, hash e costi.

Validazione: **374 test Python 3.12 e 26 test Node superati**, 64 esempi di
classificazione senza errori, build riuscita; rigenerazione deterministica,
nessuna modifica a catalogo, registry, workflow o codice di produzione.
La coda completa è conservata anche compressa, oltre alla versione leggibile locale.

[PR #42 aperta](https://github.com/nightlydeveloper8/eu-hr-internships/pull/42),
commit codice `f5864f87f951071d1cac285f4a89250148776ed5`. CI/preview avviate
automaticamente, esito ancora da verificare. Nessun merge o attivazione.

**Primo punto incompleto:** review e pilota circoscritto delle 29 proposte di
adattatore (priorità alle 28 con titolo live corrispondente), partendo dal legame
ufficiale datore→tenant e dal feed completo. Preparare l'integrazione soltanto
per canali con prove sufficienti, in un lotto; nessun merge/rollout implicito.
Per gli altri 22 paesi esiste la coda nazionale, non una nuova mappatura live.
Nessuna automazione di ricerca AI o nuova schedulazione configurata.

## Ripresa — verifica integrazione JDE

Verificata via API GitHub la PR #40: squash merge completato il 15 novembre 2026,
21:14:18 UTC, commit `216ea7300e5d666d6e78a0a1d2ba732d5109d502`.
La correzione di identità è quindi su main; i dettagli sotto descrivono la diagnosi
precedente al merge. Beneficio dimostrato dalla diagnosi: **0 nuove candidature**;
il target JDE restituiva JSON senza modulo. Nessuna PR duplicata, nuovo merge o
rollout in questa ripresa. Verifica della candidatura JDE e beneficio della raccolta
dopo merge ancora non attestati. Il runtime locale è disconnesso; stato aggiornato
tramite GitHub preservando il contenuto delle altre sessioni.

## 15 novembre 2026 — identità JDE e confronto Center Parcs/Landal

Ripresa dal primo punto incompleto sul main remoto `b51a602`. Checkout isolato
`fix-jde-20261115`, ramo `fix/jde-application-evidence-20261115`; preservato il
checkout principale e il lavoro delle altre sessioni.

- **Modifica proposta, non integrata:** riconoscimento conservativo dello stesso
  posting SmartRecruiters fra `job-posting-detail?id=` e prefisso numerico della
  CTA osservata. Nessun ID inferito dalla sola CTA; query ripetute, ID discordanti,
  host simili e ID nel tracking non bastano. Controlli titolo, host, redirect,
  chiusura e modulo restano obbligatori. Nessuna configurazione host/gate cambiata.
- **JDE: 0 nuove candidature verificate**, un solo record con tre URL osservate.
  Lettura live ufficiale e target ATS con robots: il target restituisce JSON della
  vacancy, non un modulo. Replay reale prima/dopo: errore d'identità risolto,
  successivo errore `Application page does not identify the same vacancy` mantenuto.
  Nessun aggiornamento del catalogo o timestamp di verifica da replay.
- Confronto live circoscritto: Center Parcs ha titolo/JobPosting della stessa
  vacancy e pulsante JavaScript `Solliciteren`, ma nessun href/modulo statico;
  Landal pubblica `JR104108`, mentre la CTA Workday osservata contiene `JR104108-1`.
  Nessuna promozione o presunzione di equivalenza della variante.
- Costi complessivi della diagnosi: **9 richieste / 17,505 secondi-fonte /
  0 rendering**, inclusi robots; JDE 5/4,685 s, Center Parcs 2/11,487 s,
  Landal 2/1,333 s. La correzione aggiunge una lettura del target nel replay;
  non dimostra un risparmio né nuove opportunità in produzione.
- Report riproducibile: `docs/jde-application-identity-2026-11-15.json`, due
  risposte reali compresse con SHA-256 e sei test nuovi, incluso replay in due cicli
  senza mutazione del record. Corretto anche il test WEBO che assumeva uno stage
  ancora assente dal catalogo: verifica ora inserimento e refresh/idempotenza.

Validazione locale: **362 test Python 3.12 e 26 Node superati**, 64 esempi di
classificazione senza errori, coverage e build riusciti. I file di copertura
rigenerati solo nel timestamp sono stati esclusi dal diff.

[PR #40 aperta](https://github.com/nightlydeveloper8/eu-hr-internships/pull/40),
commit codice `1f223d046368e3edc3f50087e7b448e36658f261`. CI GitHub e preview
avviate automaticamente, esito ancora da verificare. Nessun merge o attivazione.

**Primo punto incompleto:** diagnosi riutilizzabile del flusso DigitalRecruiters
Center Parcs attivato dal pulsante osservato, con letture non-submit e scope/budget
esistenti. Per JDE serve una prova ufficiale di candidatura oltre al JSON; per
Landal restano identità della variante Workday e modulo. Non ampliare rollout,
non avviare raccolte complete. Catalogo/produzione invariati; confronto pubblico
Cloudflare e Issue #18/#23 restano aperti. Nessun controllo AI futuro configurato.

## 15 novembre 2026 — esito della prima raccolta dopo #39

Ripreso il primo punto incompleto senza avviare raccolte manuali.
[Raccolta #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
conclusa con successo alle 20:20 ora svizzera: test, 16 shard e publish riusciti.
Commit dati `1ad28a9cae8076d9181974fa4ea07940e263a93d`.

- Catalogo: **345 → 346 ID; 19 → 20 open/verified; 303 unverified e 23 closed invariati**.
  Tutti i vecchi ID conservati e nessun cambio di status sui record precedenti.
  Le 20 verifiche aperte hanno checked_at del 15 novembre, fra 19:07:47 e 19:08:08 UTC.
- **WEBO — Stage HRM, Rijssen**: nuovo ID `538388e73bc1c0592ab5`,
  candidatura ufficiale via email documentata dal collector live, policy v2,
  `official-vacancy-email-instructions`; inizio febbraio 2027, lingua di lavoro
  sconosciuta. Nessuna email o candidatura inviata. È una nuova opportunità verificata,
  già presente come vecchia scheda aggregatore unverified: non due opportunità distinte.
  Fonte parziale: 11 richieste, 23,17 s, zero rendering. Gli errori su open application
  e working student non invalidano la prova della vacancy HR né rendono completo l'inventario.
- Cinque fonti nuove, costo complessivo **50 richieste / 71,73 secondi-fonte**:
  WEBO 11/23,17 s → 1 HR verificato; Attero 30/35,85 s → 0 HR osservati,
  lettura parziale (una scheda senza JobPosting); Intergas 2/1,21 s → inventario
  14 offerte, 0 HR; SW 2/1,63 s → inventario 39 offerte, 0 HR;
  Reestmond 5/9,87 s → discovery incompleta, non prova di zero offerte.
  Questi tempi non sono tempo a muro né costo monetario.
- Drenthe: 40/40 tentati, 27 con dimensione qualificata, 2 stage verificati totali
  (1 presso datori qualificati). Stati: 21 partial, 10 discovery-incomplete,
  5 blocked-or-failed, 4 collected. Provincia ancora incompleta.
- Totale monitoraggio: 1.887 datori tentati; 57 collected, 31 verified-empty,
  513 partial, 977 discovery-incomplete, 309 blocked-or-failed.
- Cloudflare check-run `132927454054`: **success sul commit dati esatto 1ad28a9**,
  deployment `a2442ea2-8a3b-4496-a134-1497fe0fdad6`.
  Il success del deployment è attestato; confronto del catalogo servito ancora
  incompleto: precedente accesso HTTP 403 e tentativo browser corrente in timeout.
- Dynamic ATS: Bentacera, OPACK e Achmea restano unverified. Nessuna nuova prova
  di beneficio di produzione per #23; #18/#23 rimangono aperte. Gate e rollout invariati.
- Nessuna PR aperta all'avvio della ripresa. Nessun nuovo merge, ampliamento host,
  rollout, modifica al catalogo o workflow manuale in questa attività.

**Primo punto incompleto aggiornato:** diagnosi riutilizzabile dei link ufficiali
di candidatura sui canali NL già letti, partendo da JDE: tre URL osservate nella raccolta condividono
lo stesso posting ID `744000158015131` e falliscono `Application link lacks a matching vacancy identifier`;
non sono tre opportunità distinte. Confrontare poi Center Parcs e Landal, preservando
policy v2, robots e host autorizzati. Prove live circoscritte solo quando utili;
nessuna raccolta completa manuale. Proseguire la copertura comunale NL tramite fonti
ufficiali accessibili; CBS, Groothuis e Wikidata restano esclusi finché bloccati.
Il confronto del sito servito resta una verifica indipendente da completare.
Nessun controllo AI futuro configurato.

## 15 novembre 2026 — integrazione autorizzata delle PR pronte

L'utente ha autorizzato esplicitamente squash and merge di tutto il lavoro pronto.
Non chiedere di nuovo l'autorizzazione per completare questa integrazione.

- **PR #38 già merged**, squash `adf4c69dd1d47cc7f940a98421796940c818d7f3`.
  Verificati head esatto, CI/preview verdi e assenza di review bloccanti prima del merge.
- **PR #39 merged con squash**, `3a2830f558af8c3e58b1ec7673dbfd7df294fbef`.
  Include le modifiche pronte #20, #27, #28, #32, #33, #34, #35, #36, #37 e WEBO;
  il checkpoint #26 è superato dallo stato corrente. Le dieci vecchie PR sono
  chiuse come consolidate/superate, non come singoli merge; rami e prove preservati.
  Nessuna PR aperta resta al controllo finale. Checkout `merge-ready-20261115`.
- Due conflitti di codice risolti conservando sia i limiti host/checkpoint #38 sia
  titoli storici, telemetria e publisher ufficiali scoped delle #27/#28. Allarme
  testato anche avviando i test fuori dalla root, senza modificare gli script live.
- **356 test Python (3.12), 26 Node, 64 esempi, coverage e build riusciti.**
  La #28 aveva vecchie CI cancellate: non è stata assunta pronta sulla sola preview;
  il suo codice è incluso nella verifica combinata completa.
- Registro integrato: 1.887 datori e 1.931 fonti, cinque datori/fonti nuovi
  (Attero, Intergas, Reestmond, SW Vastgoedverbetering e WEBO). Le altre modifiche
  estendono o correggono identità/sedi e canali di datori già censiti.
- Tutti i 345 ID del catalogo corrente conservati, senza variazioni di status,
  identità o verifiche. Unica associazione aggiornata: Landal Nooitgedacht → NL13,
  derivata dalla sede ufficiale Drenthe già revisionata. Nessun snapshot storico
  di catalogo o coverage generale sovrascrive quello attuale.
- WEBO Stage HRM: 1 nuova candidatura verificabile nel pilota live del 15 novembre
  (3 richieste / 34,533 s), nessun invio. Fonte quotidiana configurata su main, parziale, host
  esatto e budget 80 richieste/120 s. Prima raccolta su main ancora da verificare;
  l'incremento effettivo di stage in produzione non è ancora attestato.
- Drenthe: lotto parziale di 40 datori, 27 qualificati nella ricerca del 14 novembre;
  non provincia completa. Overijssel: WEBO primo canale proposto; CBS 406 rispettato,
  municipality code ignoto. Le 171 vecchie schede OVI non sono aziende uniche.
- Directory/ATS discovery #33/#34 restano code offline, seed live disabilitati;
  #35 audit DIM conferma mantenimento storico, non nuove vacancy; #36 documenta un
  pilota Wikidata bloccato. Nessuna query o fonte live avviata per questi moduli.
- Gate Dynamic ATS `pilot-v1`, allowlist del pilota e schedule invariati. Nessuna
  raccolta completa manuale, email, candidatura o automazione AI aggiunta.

**Stato finale dell'integrazione:** CI prima del merge #43750190939/#43750185407
riuscita sullo head esatto `061426e`; CI dopo merge #43750497438 riuscita.
[Raccolta automatica #43750497445](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43750497445)
avviata dal merge #39, ancora in corso all'ultimo controllo. Nessun workflow
manuale avviato e nessun controllo AI futuro configurato.

La precedente raccolta dopo #38, #43748284250, è riuscita: test, 16 shard e
publish tutti verdi, commit dati `19c4258`. Catalogo 18:55 UTC: 345 ID, 19 open,
303 unverified, 23 closed. Prima/dopo #38: 341 → 345 record ma 19 → 19 verified;
nessun nuovo verified attribuito al fix. DAF: richieste 86 → 75, durata
100,46 → 86,13 s, pending 2.332 → 57, solo host www.daf.com. Inventario ancora
parziale: il risparmio osservato non prova completezza né nuove candidature.

**Punto di ripresa precedente (completato sopra):** leggere l'esito del run #43750497445, verificare
publish, nuovi ID, freschezza e opportunità WEBO; misurare costi e canali Drenthe.
Non dichiarare un incremento di produzione prima di quel risultato. Il controllo
pubblico del catalogo Cloudflare ha restituito HTTP 403: deployment/contenuto
servito non attestati dal runtime, distinzione conservata rispetto a GitHub.
Issue #18 e #23 restano aperte finché tutti i criteri di produzione non sono provati.
Le vecchie modifiche locali WEBO sono già incluse: non creare una PR duplicata
partendo dal checkout storico. Dettagli in docs/integration-2026-11-15.md.

## 16 novembre 2026 — pilota Marquardt/SLB/TikTok e fix strutturali 429/filled (PR tecnica)

La review ufficiale delle tre schede e CTA produce **0 nuove candidature verified**: Marquardt RO ha vacancy HR Sibiu e CTA Mingle ma modulo non stabilito; SLB RO mostra configurazione Eightfold `disableLoggedOutApply: true`/`recaptchaEnabled: true`, senza applicazione anonima dimostrata; TikTok IE A187616 ha CTA verso ID corrispondente, ma il redirect finale non è leggibile dal tool e il datore era già nella coda precedente. **robots, inventari completi e moduli validi non attestati**; nessuna fonte ammissibile, nessun nuovo contatore di produzione. Baseline documentata invariata: **28 stage verificati + 1 working student**, 361 record; nessuna attivazione o raccolta completa.

Correzioni **proposte su ramo separato, non integrate**: `collector/runtime.py` applica uno stop nello stesso processo dopo primo HTTP 429 per host (no ulteriori chiamate di rete a quel host; altri host continuano). `collector/applications.py` riconosce “job ... has been filled” di Electrolux `JR81378` anche in presenza di JSON-LD obsoleto. Test offline per 429 multipli, client separati, redirect, robots, 503 non-bloccante, chiusura con JobPosting residuo. Esiti CI e merge da verificare, zero modifica registri/workflow, zero rollout.

Costo produzione aggiuntivo **0**. Il pilota web non dispone di conteggio HTTP/tempo/byte del collector: non equipararlo al preflight documentato (27 richieste, 14,721 secondi-fonte). Con ipotetico massimo 8 richieste/45 secondi per ciascuna di tre fonti, tetto condizionale 24 richieste e 135 secondi-fonte **solo dopo ammissione**, non misurazione live. Dettagli, evidenze e prossimi blocchi: [BATCH-05-PILOT-AND-429-FIX.md](eu27-expansion/BATCH-05-PILOT-AND-429-FIX.md).

**Primo punto incompleto:** controllare CI della PR tecnica; pilota client HTTPS/robots su Marquardt/SLB/TikTok e same-vacancy form anonimo, senza CAPTCHA/login. Non attivare i tre canali finché un percorso non supera policy v2; se nessuno passa, cercare fonti sostitutive.

