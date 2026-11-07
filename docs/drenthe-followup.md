# Drenthe: approfondimento del 7 novembre 2026

Questa fase continua da main `699d1a4`, dopo la PR #4 e la verifica della produzione già concluse. Non ripete l'import CBS, il merge o la pubblicazione. Nessun merge in main, deployment di produzione, invio di candidatura o email è stato effettuato.

## Recupero del lavoro precedente

Controllati tutti i quattro branch remoti e i branch locali del checkout precedente. Quel checkout contiene lavoro non committato su Flevoland, interfaccia e raccoglitori, oltre a branch locali non allineati: è rimasto intatto. La fase Drenthe usa un clone separato, inizialmente pulito, nel workspace della chat. Controllati PR #2–#4, rapporto iniziale, audit, integrità e verifica remota già presenti. Inventario e stato iniziale: [drenthe-followup-context.json](drenthe-followup-context.json).

## Copertura ampliata nei comuni meno coperti

Il lotto passa da **31 a 34 datori distinti**, da **14 a 17 con dimensione documentata ≥50**. Tutti i dodici comuni hanno ora almeno un datore qualificato nel lotto. Le dimensioni restano del datore, mai attribuite a ogni singola sede; i volontari non sono dipendenti.

| Datore aggiunto | Presenze documentate | Prova dimensionale ufficiale |
|---|---|---|
| Groningen Airport Eelde | Eelde, Tynaarlo | [Circa 80 dipendenti del datore](https://www.groningenairport.nl/en/careers), esclusi gli altri datori del campus |
| EMCO-groep | Emmen e Coevorden, [indirizzi ufficiali](https://emco-groep.nl/contact) | [Oltre 1.500 dipendenti](https://emco-groep.nl/over-emco-groep), per l'intero datore |
| ZZWD Zorgcollectief | Dwingeloo, Havelte e Diever in Westerveld; Ruinen e Koekange in De Wolden, [presenze ufficiali](https://www.zzwd.nl/) | [Circa 400 dipendenti](https://www.zzwd.nl/over-zzwd/), distinti da circa 400 volontari |

Riutilizzati importer, registro e assegnazione ai sedici shard quotidiani. Nessuna nuova automazione, dipendenza o duplicazione di datore. La raccolta completa Drenthe ha effettuato 34 tentativi; i ricontrolli Cegid e Scania portano a **36 tentativi su 34 fonti distinte**. Esiti correnti: **3 inventari raccolti nel perimetro dichiarato, 22 parziali, 4 scoperte incomplete, 5 blocchi/fallimenti**. Il rapporto generato contiene richieste, errori, tempi e date effettive: [drenthe-followup-audit.json](drenthe-followup-audit.json).

## Canali migliorati e risultati effettivi

**Groningen Airport Eelde:** il messaggio di zero vacancy compare solo dopo rendering. Ora il raccoglitore accetta un inventario vuoto esclusivamente con intestazione e messaggio ufficiali revisionati, senza link a vacancy o conteggi contraddittori. Zero riguarda il solo elenco pubblico osservato; non chiude annunci per assenza. Il programma generale stage non diventa uno stage HR.

**Center Parcs:** mantenuto il datore e il suo ID di fonte esistente, inclusa la ricerca su tutti i nove filtri olandesi. Individuato il POST di sola ricerca pubblica Cegid dal client ufficiale. Il lettore ammette soltanto endpoint, dominio, query e payload revisionati, con gli stessi filtri della pagina ufficiale; attende la risposta anziché fotografare il testo Loading. Restano vietate le operazioni candidato, autenticazione, notifiche e mappa; robots rimane attivo, compreso il divieto `/dashboard`.

Letti **31 record distinti**: prima pagina olandese **20/119**, più inventario completo di **De Huttenheugte 11/11**, separatamente documentati. **Nessuno degli undici titoli correnti di Dalen è uno stage HR**. Non si promuovono le copie storiche degli aggregatori. La ricerca complessiva rimane parziale: non sono state completate le pagine successive dell'inventario nazionale, fuori dal sottoinsieme Drenthe completo. Non viene inferita alcuna chiusura. Due stage HR emersi nel sottoinsieme nazionale sono a **Capelle aan den IJssel, fuori Drenthe**: conservati come non verificati perché manca la prova della candidatura, esclusi dal conteggio provinciale.

**EMCO** resta discovery-incomplete: il canale ufficiale non espone un inventario verificabile al lettore. **ZZWD** resta parziale: sei record strutturati ispezionati, collegamenti PDF e programma stage generico non equivalgono a un inventario completo o a vacancy HR specifiche.

## Stage, candidature e lingue

Restano **due stage Drenthe verificati**, entrambi ad Assen: [SKK Kozijnwacht](https://skk.nl/werken-bij-skk/stagiair-hr/) con istruzioni ufficiali email, e [Ziengs/Scapino](https://www.werkenbijziengs.nl/vacatures/hr-stagiaire-scapino-ziengs) con [modulo ufficiale requisizione 4260](https://www.werkenbijziengs.nl/solliciteren?vacature=4260). Ricontrollati in questa fase. Nessun ulteriore stage HR Drenthe ha superato la verifica della candidabilità. Le lingue di lavoro di entrambi restano sconosciute: il testo olandese non dimostra un requisito linguistico né la sufficienza dell'inglese.

Per [Scania Meppel](https://jobs.scania.com/job/Meppel-Stage-Human-Resource-Management-7944HT/1454163033/) il testo corrente nomina esplicitamente olandese e/o inglese. Corretto il riconoscimento delle forme flesse Nederlandse/Engelse e delle alternative en/of e and/or: le due lingue sono ora alternative, non due requisiti simultanei. La sufficienza del solo inglese resta non stabilita secondo la policy conservativa esistente. Il percorso di candidatura resta vietato da robots: nessun aggiramento e nessuna promozione a verificato.

[NNCZ Hoogeveen](https://werkenbij.nncz.nl/algemene-vacaturebeschrijving/hr-stagiaire-hoogeveen-od-1310226) resta non verificato: l'azione AFAS CreateApplication non è un link/form di candidatura confermato dal lettore. Nessuna lingua di lavoro esplicita trovata. Bats mantiene il blocco CAPTCHA.

Ulteriori controlli primari hanno escluso [Smurfit Westrock HR-stage Hoogeveen](https://www.werkenbijsmurfitwestrock.nl/vacature/642/hr-stage), dichiarata non più disponibile, e [BRAND HR afstudeer stage](https://www.brandfrance.fr/nl/career/detail/438), marcata OFFLINE anche nell'[elenco ufficiale](https://www.beis.com/uk/careers). Lo [stage KAM di WILDLANDS a Emmen](https://www.werkenbijwildlands.nl/vacaturebeschrijving/stagiair-e-kwaliteit-arbo-milieu-kam) riguarda qualità, ambiente e gestione documentale: contatti o collaborazione con HR non lo rendono uno stage HR. Il classificatore lo esclude. Le pagine locali degli aggregatori con stage ad Aalsmeer, Zwolle o Enschede non dimostrano posti a Beilen o Meppel.

Hash e timestamp dei controlli primari: [drenthe-followup-primary-checks.json](drenthe-followup-primary-checks.json). Requisiti linguistici e stati di candidatura effettivi sono anche nell'audit.

## Conservazione, test e riproducibilità

Conservati tutti i **1.813 datori**, **1.857 fonti** e **265 annunci** di partenza; il catalogo ha ora 267 record, inclusi i due nuovi non verificati fuori provincia. Nessun ID, URL, collegamento a fonti o luogo confermato di altre province è stato perso. Il controllo confronta main con i dati finali, verifica unicità, conservazione della ricerca delle altre province e assenza di report incompleti marcati completi. I conteggi effettivi della baseline nell'audit prevalgono su eventuali numeri storici.

Comandi eseguiti e risultati finali sono in [drenthe-followup-validation.json](drenthe-followup-validation.json). I test aggiunti coprono inventari vuoti, conflitti tra contatore e link, vincoli del POST Cegid, duplicati, provider esterni e separazione dei perimetri completi/parziali. I quattro nuovi casi linguistici comprendono il testo reale Scania e un caso negativo senza requisito di lingua.

```sh
python3 scripts/integrate_drenthe.py
python3 scripts/collect_province.py drenthe --workers 6
python3 scripts/company_coverage.py
python3 -m unittest discover -s tests
node --test tests/frontend.test.js
python3 scripts/evaluate.py
python3 -m collector.pipeline --validate
python3 scripts/build.py
python3 scripts/audit_province_followup.py drenthe --baseline 699d1a4 \
  --attempts .staging/drenthe/collection.json work/cegid-part.json work/scania-part.json \
  --output docs/drenthe-followup-audit.json
```

I file degli ultimi due tentativi sono checkpoint locali; i relativi report integrali sono salvati nell'audit committato. Gli script temporanei di ricerca e le copie integrali delle pagine restano fuori dal repository.

## Attività residue

La ricerca rimane non esaustiva: ampliare ancora i datori e le località, qualificare le 17 dimensioni ignote, completare le letture parziali e verificare un percorso ufficiale di candidatura AFAS senza invii. Per Cegid il sottoinsieme Drenthe è letto, la paginazione nazionale e le candidature restano incomplete. I blocchi Scania/Bats e i fallimenti comunali restano esiti documentati, non zeri. Nessun nuovo risultato viene pubblicato in produzione da questa fase; eventuali merge e pubblicazione richiedono autorizzazione separata.


## Pubblicazione e verifica finale — 7 novembre 2026

La [PR #5](https://github.com/nightlydeveloper8/eu-hr-internships/pull/5) è stata revisionata e integrata dopo autorizzazione esplicita dell'utente nel commit `3632f74abec2c96a560edec6078ea8594999b1f1`. Le indicazioni precedenti sul merge ancora da autorizzare sono storiche. Ripetuti con successo 175 test Python, 15 frontend, classificazione, validazione e build; sito e anteprima verificati su desktop/mobile, insieme ai filtri e alle pagine Frisia/Groningen. Entrambe le candidature ufficiali SKK e Ziengs/Scapino sono state ricontrollate senza invii.

Il [workflow 42348794504](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42348794504), avviato dal merge, è concluso con tutti i 18 job riusciti: test, 16 shard e pubblicazione. Il bot ha pubblicato `a2a5c920524b48954dc2d1c5c5839f6546b780a6`; Cloudflare lo ha distribuito nel deployment `079dd871-87f0-455c-a505-11788e982565`. Tutti i 1.816 datori hanno ricevuto un tentativo; non tutti i siti sono stati letti completamente. Il catalogo passa da 267 a 305 schede archiviate, senza perdere alcun ID precedente: il totale non rappresenta stage aperti verificati.

La [produzione Drenthe](https://people-placement-eu.pages.dev/drenthe.html) è stata verificata alle 08:02 Europe/Zurich: **34 datori, 17 con dimensione documentata, 17 dimensioni ignote, 12 comuni con almeno un datore qualificato e 2 stage HR candidabili verificati**. Tutte le 34 fonti hanno un tentativo recente. Esiti remoti: 3 inventari osservati letti, 23 letture parziali, 3 scoperte incomplete, 5 blocchi/fallimenti. Nessun esito non riuscito è marcato completo. Dati pubblici uguali al rapporto del commit del bot, nessun errore di pagina o overflow mobile; filtri UE e provinciali funzionanti.

La raccolta ordinaria resta sul workflow esistente alle 06:17 UTC (07:17 invernale / 08:17 estiva a Zurigo), soggetta ai ritardi GitHub. Il ciclo osservato qui è quello avviato dal merge; non si dichiara già osservata un'esecuzione futura dello scheduler. NNCZ/AFAS, Scania, Bats e le altre fonti incomplete restano documentati; non vengono aggirate restrizioni e la ricerca non è un censimento esaustivo. Il precedente lavoro locale su Flevoland/interfaccia è rimasto intatto.

Prove complete: [drenthe-followup-remote-verification.json](drenthe-followup-remote-verification.json).
