# Germania — AGENZIE-DE e DE-CORPORATE

Verifica del 24 novembre 2026. Il lotto **AGENZIE-DE** è in hold senza fonti registrate. **DE-CORPORATE** include il solo canale DB in hold nel registro delle fonti e dei datori.

## AGENZIE-DE

| Host | Inventario e risultato |
|---|---|
| www.randstad.de | Robots e [condizioni](https://www.randstad.de/nutzungsbedingungen/) rivisti. 12.963 URL nei tre sottoindici vacancy, zero slug candidati. |
| www.manpower.de | Robots e [avviso](https://www.manpower.de/de/impressum) rivisti. 5.625 URL nel ramo `/de/jobs/` dell’indice, zero slug candidati. |
| www.hays.de | Robots e avvisi rivisti. 4.162 URL nel sottoindice offerte, zero slug candidati. Letture distanziate di almeno 10 s come indicato dal robots. |
| www.tempton.de | Robots e [avviso](https://www.tempton.de/impressum) rivisti. L’indice contiene 28.743 URL nel ramo `/jobs/`. Il solo slug candidato porta a un JobPosting per un ruolo impiegatizio HR. Il dettaglio lo esclude dal lotto stage. |
| www.dis-ag.com | Robots e [condizioni](https://www.dis-ag.com/de-de/nutzungsbedingungen) rivisti. L’indice DE dichiara 299 URL di contenuti e nessun sottoindice vacancy. |
| www.adecco.de | Il robots reindirizza a una pagina di un altro host sotto `/de-de/`. Accesso sul dominio originario indeterminato. Le [condizioni del sito di gruppo](https://www.adecco.com/de-de/nutzungsbedingungen-adeccogroup) vietano l’estrazione per il perimetro cui si applicano. |
| www.gigroup.de | Il robots reindirizza alla home di un altro host. Diagnosi interrotta sull’alias. L’[avviso del dominio di destinazione](https://de.gigroup.com/impressum/) limita la riproduzione dei dati. |

## DE-CORPORATE

| Host | Sitemap → triage → dettaglio |
|---|---|
| www.bmwgroup.jobs | Robots e [impressum](https://www.bmwgroup.jobs/content/grpw/websites/bmwgroup_com/de/general/impressum.html) rivisti. Sitemap di 2.706 URL, di cui 712 schede con ID opaco. Il titolo delle 12 righe benchmark di questo host non è ricavabile dagli URL. Nessuna scheda aperta su questo host. |
| jobs.bmwgroup.com | Sitemap pubblica di 769 URL con slug descrittivi. 15 candidati nel perimetro DE osservato, selezionati dal titolo e dai marcatori geografici degli slug. Dopo il redirect sullo stesso host, 15 dettagli con microdati HTML e zero JobPosting JSON-LD. Le due righe benchmark su questo host restano senza prova ammessa. |
| jobs.festo.com | 131 URL di offerte con slug, quattro candidati e quattro dettagli con microdati HTML. Zero JobPosting JSON-LD. Le rotte di candidatura `/talentcommunity/` sono escluse dal robots. |
| karriere.provinzial.com | 157 URL con slug, quattro candidati e quattro dettagli con microdati HTML. Zero JobPosting JSON-LD. È presente la vacancy del benchmark. |
| jobsearch.daimlertruck.com | [Sitemap](https://jobsearch.daimlertruck.com/sitemap.xml) con 358 URL, tutti opachi `ac=jobad&id=…`. Il triage per titolo è indeterminato, comprese le due righe benchmark. Zero dettagli aperti. [Avviso legale](https://www.daimlertruck.com/anbieter-rechtliche-hinweise) |
| db.jobs | [Avviso](https://db.jobs/de-de/Impressum-5555662) e robots rivisti. Dall’indice tedesco e dal sottoindice gzip risultano 3.984 URL totali. Tre slug stage HR prima delle esclusioni, due dettagli letti dopo aver escluso Werkstudent. Un JobPosting supera il classificatore HR e conferma l’idoneità studentesca. È la riga benchmark di Monaco. Rimane lead per assenza di scadenza e di prova di candidatura per lo stesso ID. |

I microdati HTML non rientrano nei formati di dettaglio ammessi da AGENTS.md. Il preflight ha usato lo user agent People Placement, almeno 2 s di pausa per host e solo GET. I conteggi HTTP sotto includono robots e redirect osservati, escludono le consultazioni documentali esterne e includono nei GET i timeout iniziali su BMW e Manpower. I secondi si riferiscono alle risposte registrate.

| Lotto | Domini ammessi | Stage DE aperti | Recall aperto DE | ID prima → dopo / persi | Costo del preflight | Tetto nominale per shard |
|---|---|---:|---:|---|---|---|
| AGENZIE-DE | 0/7 | 36 → 36 | 0/30 → 0/30 | 944 → 944 / 0 | 18 GET, 9.987.613 B, 4,764 s HTTP | +0 s su tutti |
| DE-CORPORATE | 1/6, DB | 36 → 36 | 0/30 → 0/30 | 944 → 945 / 0 | 54 GET, 4.956.751 B, 12,684 s HTTP | shard 2 +180 s, massimo 30 richieste, altri +0 s |

Simulazione isolata a partire dal catalogo del 24 novembre alle 07:56 UTC. Adapter e finalizzatore hanno usato le risposte catturate. Cinque letture logiche DB nel replay, di cui una ripetizione della scheda per la verifica. Il recall aperto usa URL canonico, ID di catalogo dimostrato o ID dello stesso contenuto editoriale DB sul medesimo host, quindi la query `jobId` non fa perdere l’identità del benchmark. Nessuna estensione alle fonti attive. Durata end-to-end del workflow da dimostrare.
