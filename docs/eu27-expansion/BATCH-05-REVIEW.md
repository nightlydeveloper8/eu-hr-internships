# Lotto 05 — Cechia, Romania, Svezia, Irlanda (review successiva al preflight)

**Data:** 16 novembre 2026. **Stato: ricerca ufficiale mirata, senza ammissioni o rollout.** Questa review estende [il preflight già misurato](batch-05-preflight-2026-11-16.json). Le pagine sono state individuate e lette tramite ricerca/navigazione web; **non** sono state rieseguite con il client del collector, non è stata misurata la completezza dei feed, né ispezionato un modulo anonimo completo per la stessa vacancy in un pilota policy v2. Quindi **0 nuovi stage verified**, **0 nuove fonti abilitate**, **0 modifiche a produzione**, **0 candidature inviate**. Baseline dell'ultimo ciclo ordinario documentato: **28 stage HR verified + 1 working student**, catalogo 361 record, commit dati `d764bec`.

## Esito dei quattro indizi precedenti

| Paese | Indizio precedente | Prova e decisione |
| --- | --- | --- |
| CZ | Manifesto Group, HR Intern (unpaid), Praga | Corporate→tenant esatto e annuncio con CTA *Apply now* pubblicati. Il preflight precedente ha incontrato 429 su più URL di candidatura; non replicare la scansione. Nessuna forma anonima policy v2 stabilita. **blocked / non admit**; Ceco+inglese richiesti. |
| RO | Continental, HR Recruitment 8h Tires | La pagina ufficiale dello specifico annuncio dichiarava closed; **exclude**. Non inferire la chiusura dell'intero datore. |
| SE | Electrolux, HR Project Management Intern, `JR81378` | La risposta ufficiale del preflight era HTTP 200 con `JobPosting` e città Stockholm, **ma il corpo riportava esplicitamente “The job you are trying to apply for has been filled”**. Lo stato effettivo della vacancy prevale sul dato strutturato rimasto in cache. **closed / exclude**. |
| IE | Fidelity, Human Resources Internship | L'URL ufficiale aveva HTTP 404: **unavailable / exclude**, senza retry dello stesso URL. |

## Sostituti e nuovi indizi dai siti del datore

Queste sono **piste da verificare**, non un elenco di stage candidabili aggiunti al sito. Ogni datore→fonte, inventario completo, identità vacancy/CTA, robots/redirect e modulo senza login vanno verificati **prima** di qualunque adapter o classificazione `verified`.

| Priorità | Paese | Datore / opportunità | URL ufficiale e prova osservata | Blocco residuo |
| --- | --- | --- | --- | --- |
| 1 | RO | **Marquardt Romania — HR internship, French & English speakers** (Sibiu) | https://www.marquardt.com/careers/job-search/detail/hr-internship-french-english-speakers-f-m — pagina aziendale con mansioni HR, compenso **non retribuito**, università convenzionata, **francese+inglese**, CTA `Apply now` che conduce al dominio `marquardt-ro.mingle.ro/en/apply/sUQZQQ` | La pagina candidatura esterna non espone un modulo anonimo verificabile nella lettura disponibile; accertare ownership e inventario senza scraping completo |
| 2 | RO | **SLB — Human Resources Internship** (Bucharest) | https://careers.slb.com/jobdescription.aspx?id=EF12289-en_US+1 — pagina ufficiale HR con `Apply Now` verso `apply.slb.com/careers/apply?domain=slb.com&pid=563499731000279`; la pagina esplicita remunerazione mensile 4.444 RON lordi | Il target mostra shell/configurazione di applicazione, non il modulo anonimo della stessa vacancy; status policy v2 unknown |
| 3 | RO | **British American Tobacco — HR Intern** (Bucharest) | https://careers.bat.com/en/job/bucharest/hr-intern/1045/46198641856 — pagina HR internship e CTA diretta verso `careers.bat.com/en/apply?locale=en_GB&req=81347`, inglese avanzato e competenza normativa RO | Sulla pagina d'arrivo non compare un modulo verificabile: non promuovere solo per `Apply Now` |
| 4 | CZ | **Amazon Logistic Prague — Operations Human Resources Partner Intern, job 10561439** (Kojetín, Cechia) | https://www.amazon.jobs/en/jobs/10561439/operations-human-resources-partner-intern-6-months-2027 — pagina aziendale specifica HR, CTA `Apply now`, onboarding gennaio–settembre 2027 | CTA devia a sistema di accesso Amazon; **non tentare login**; ceco e inglese C1 richiesti, quindi non English-only |
| 5 | IE | **TikTok — HR Operations Lifecycle Intern 2027, A187616** (Dublin) | https://lifeattiktok.com/search/7694622895491205429 — **scheda ufficiale specifica** HR Operations Lifecycle, Dublin, job code A187616, master HR e competenze UK/IE; la CTA **Apply to this job** porta allo stesso codice pubblicazione su `careers.tiktok.com/resume/7694622895491205429/apply` | È **già un indizio della coda lotto 01**. Scheda e CTA specifiche ora trovate: **il modulo resta non verificato** (il controllo web non ha potuto aprire il redirect `lifeattiktok.com/resume/7694622895491205429/apply`); non inferire login né successo; nessuna nuova fonte da contare |
| 6 | SE | **Procter & Gamble — Human Resources Summer Internship 2027, R000160141** (Solna/Stockholm) | Il riferimento esatto e la scadenza **1 dicembre 2026** compaiono in risultati indicizzati, ma **non è stata verificata una scheda ufficiale individuale P&G** | Solo lead esterno: recuperare tramite canale datore ammesso prima di leggere dettagli o promuovere; non usare aggregatori come fonte di produzione |

## Electrolux — verifica di completezza

La correzione sul caso `JR81378` è deterministica: l'annuncio è **filled** secondo il corpo ufficiale dell'ultimo preflight. Ulteriori tracce:
- `JR81338` **Talent Transformation Intern (Talent Acquisition)** figura in un elenco indicizzato Electrolux, ma la scheda Workday indicizzata riportava **End Date 8 novembre 2026**, già trascorsa. Il target Workday non era accessibile nel controllo web; **non ammettere** senza nuova prova di apertura e candidatura.
- `JR81695` **Learning & Development Intern** appare in archivio indicizzato con **End Date 8 novembre 2026**; **non ammettere**.
- La pagina corporate https://career.electroluxgroup.com/global/en/search-results include risultati potenzialmente non allineati allo stato della scheda; **non usare il listing né JobPosting come prova di apertura**.

**Miglioramento riutilizzabile da implementare separatamente:** per la famiglia Phenom/Workday, rilevare `filled` e scadenza nell'HTML corrente **prima** di utilizzare `JobPosting` residuo; non promuovere su CTA “Join Community” (talent pool), e mantenere inventario incomplete se feed dinamico non accessibile. Servono test offline di contrasto body-structured-data e deadline trascorsa. Per Manifesto/host che restituiscono 429, il client deve interrompere le ulteriori URL sullo stesso host nel medesimo run, con cooldown esplicito; non aggirare il 429 né espandere gli host.

## Metriche, limiti e prossimo passo

Il **preflight esistente** ha consumato **27 richieste logiche, 14,721 secondi-fonte, 1.222.790 byte, 14 query di ricerca** senza nuovi verified. Questa review è una ricognizione di fonti via web (non una raccolta programmatica): non attribuire ad essa nuovi contatori HTTP del collector, tempi, costi monetari o attestazione di robots per i nuovi host. Nessun runtime abilitato o raccolta completa. Non reinterrogati tramite collector i percorsi 429/404/closed.

**Risultato attribuibile a questa PR:** quattro esiti precedenti riclassificati prudentemente, **sei piste di sostituzione in quattro paesi, di cui TikTok già presente nel lotto 01**, **0 candidature verificate aggiunte**, **0 richieste quotidiane aggiunte**.

**Primo punto incompleto:** ammettere soltanto dopo prova live del percorso datore→ATS e della candidatura per la stessa vacancy, e dopo confronto con registri correnti. Priorità Marquardt/SLB in Romania e scheda P&G esatta in Svezia; Amazon/TikTok rimangono esplorabili senza autenticazione ma non sono verified. Consolidare un miglioramento generico di stop-after-429 senza ritentare Manifesto oggi. Nessun merge/attivazione suggerito su queste sole prove.
