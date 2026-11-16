# Lotto 10 — recupero stage HR da fonti ufficiali, non dai mirror

**16 novembre 2026. Paesi:** Paesi Bassi (NL), Belgio (BE), Francia (FR), Spagna (ES), Portogallo (PT). **Oggetto:** analisi offline del catalogo e riconciliazione dell'ownership storica, senza ampliare fonti o rollout.

## Risultato e valore reale

L'ultimo catalogo verificato **prima** del ciclo ordinario delle 18:53 UTC conteneva **257 annunci** riferiti ai cinque paesi: **28 stage HR open/verified**, 209 unverified e 20 closed. **Nessun nuovo stage è stato verificato in questa revisione.**

| Paese | Record nel catalogo | Stage HR verified | Unverified | Closed | Record storici con fonte esterna non riconciliata | Unverified da riesaminare dopo la separazione |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| NL | 194 | 18 | 160 | 16 | **108** (98 unverified, 10 closed) | **62** |
| BE | 4 | 3 | 1 | 0 | 0 | 1 |
| FR | 45 | 5 | 36 | 4 | 0 | 36 |
| ES | 13 | 1 | 12 | 0 | 0 | 12 |
| PT | 1 | 1 | 0 | 0 | 0 | 0 |
| **Totale** | **257** | **28** | **209** | **20** | **108** | **111** |

**Diagnosi strutturale:** 108 record del vecchio `auto-tilburg-university` hanno URL su `www.nationalevacaturebank.nl`, **non** su `www.tilburguniversity.edu`. Corrispondono a numerosi altri datori, non a 108 stage presso Tilburg. Nessuno aveva una candidatura verificata e l'ultima lettura risale al 7 novembre. Dei **70 timeout** e **28 annunci senza percorso di domanda** della fonte Tilburg, molti sono attribuiti a quei record storici; aumentare il budget per l'università non dimostra annunci ufficiali dei datori.

La correzione **non elimina alcun annuncio né altera il suo ID, il datore pubblicato originariamente, la provenienza storica e le osservazioni**. Per i soli URL esterni a una fonte con `ownership_scope=reviewed-hosts` o `require_employer_identity` aggiunge `ownership_risk`, `review_note` e stato `review-required` sui record non verificati. Un record chiuso rimane chiuso. Una corrispondenza positiva già riconciliata da `data/ownership-reviews.json` resta valida; un host esplicitamente approvato non viene rifiutato. Una falsa vacancy open su host esterno viene declassata a unverified: non è accettabile conservarla verified senza ownership.

**Protezione della vista pubblica:** la scheda `Include unverified` e i relativi conteggi dell'interfaccia ignorano i record con `ownership_risk=historical-unreviewed-external-host`. Gli ID e le URL restano consultabili nel JSON storico e nell'audit, non vengono trasformati in `closed`. Gli annunci senza il flag mantengono la visibilità precedente. La protezione è coperta anche da un test frontend; non conta questi mirror come possibili candidature ufficiali.\n\n**Beneficio misurabile offline:** 108 record impropriamente associati a una fonte ufficiale sono individuati e contrassegnabili; 98 unverified sono esclusi dalla **coda di recupero automatico**, che passa da 209 a **111 candidati alla revisione delle prove**. **Non** sono 98 annunci eliminati né 111 offerte candidabili: il codice mantiene tutti i record. L'audit offline riutilizzabile `python -m scripts.audit_batch10_recovery` ricalcola queste metriche dal catalogo e dai registri; i suoi controlli non promuovono record vecchi, chiusi o privi di policy v2.

Fra i **111** residui, le maggiori classi di problema sono **44** casi senza link di candidatura specifico, **18** con identificativo dell'applicazione non corrispondente, **16** con titolo/scheda non corrispondenti e **8** bloccati su robots 403. Nessun gruppo è stato contato come recuperato senza prove.

## Verifiche mirate su fonti ufficiali

- **FR — L'Oréal**, [stage RH a Parigi](https://careers.loreal.com/fr/emploi/paris/stage-rh-6-mois-de-janvier-a-juin-2027-region-parisienne-master-1-ou-2-1700-brut-mensuels-nombreuse/3456/36074467072), referenza aziendale **229626**, pubblicato il 29 ottobre. La pagina ufficiale conserva titolo, sede e ruolo, ma il pulsante `Postuler` conduce a `careers-apply.loreal.com/job/Applicationmethods?jobId=229626`. Il lettore web ha ricevuto HTTP 406; il nuovo host non è approvato nel registro sorgente. **Non** cambiare host/robots o dichiarare candidato verificato con la sola corrispondenza ID.
- **NL — DAF Trucks**, [HBO Meewerkstage HR Officer PACCAR Parts](https://www.daf.com/en/working-at-daf/vacancies/hbo-meewerkstage-hr-officer), Eindhoven, ruolo di stage confermato dal sito datore e competenza olandese richiesta; un pulsante Apply compare ma non è stato verificato un form anonimo specifico. Due record DAF hanno vecchio errore di estrazione `NoneType`: manca riproduzione live specifica, non correggere per supposizione.
- **NL — AXS Logistiek**, [HR Stage](https://axslogistiek.nl/jobs/24173/hr-stage/): l'indice mostra una scheda HR, ma l'apertura fresca con il lettore web dà 404. Non ripristinare una candidatura da un indice datato.
- **BE — JDE Peet's**: unico annuncio non verificato belga, **Internship/Stage Human Resources** su SmartRecruiters, con divergenza titolo/scheda nel collector precedente. Evitare di contare più traduzioni o mirror come stage distinti finché il form same-ID non è provato.
- **ES — Amazon**: otto stage nel catalogo sono bloccati da `robots.txt unavailable: 403`; non tentare scorciatoie. BSH in Spagna resta una fonte già verificata.
- **PT — Emma Sleep**: un annuncio verificato e nessun record `unverified` portoghese da recuperare nello snapshot.

Le verifiche online dei siti aziendali sono **contestuali**, non preflight `BudgetClient`. Non è stato aggiunto alcun host, API, tenant, scheduler, endpoint di candidatura o richiesta automatica quotidiana.

## Verifica successiva della raccolta ordinaria

La [raccolta #43931128227](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/43931128227) è **success**, incluse test, 16 shard e publish. Commit pubblicazione `9ea137359a3d858b7471fd059dd6a2a81d3b2b24`, catalogo 16 novembre **18:53:11 UTC**:

- **362 record prima e dopo**, **0 nuovi ID e 0 eliminati**; 134 record modificati.
- **28 stage HR policy-v2 verified + 1 working student DE**, invariati, **0 ID verified persi e 0 guadagnati**.
- Report datori: **1.896 attempted, 67 collected, 32 verified-empty, 530 partial, 277 blocked-or-failed, 990 discovery-incomplete**. Questo non significa che 67 aziende abbiano annunci stage attivi.
- `data/catalog.json.update_status` **partial** e `data/coverage.json`: 670 fonti succeeded su 1.894 tentate, 1.507 partial (i raggruppamenti del report aziende e delle fonti non sono la stessa misura).
- Check GitHub **Cloudflare Pages = success** sul medesimo commit dati `9ea1373`. Il lettore web non ha potuto scaricare il catalogo pubblico per confrontarne byte e hash: **la verifica indipendente GET pubblica rimane non eseguita**.

**Regressione del fixture dopo il ciclo ordinario:** il catalogo pubblicato ha aggiunto a un record esistente un alias di deduplicazione valido (`identity_aliases`). Un test di conservazione degli ID copiava quel record per costruire due posti sintetici diversi, ereditandone l'alias e facendoli fondere correttamente. Il fixture ora azzera soltanto gli alias/ID di posting ereditati per gli annunci fittizi: **nessuna modifica alla deduplica di produzione**.\n\n**Importante:** questa raccolta è precedente alla patch di quarantena storica del lotto 10. Il fatto che il workflow sia verde non implica che la mappatura dei cinque paesi, né quella UE27, sia completa.

## Modifiche, costi e punto incompleto

**Patch preparata su ramo distinto**: `collector/ownership.py` (quarantena conservativa dei soli record storici su host esterno non approvato), `collector/pipeline.py` (applicata dopo deduplica/riconciliazione e conteggiata in coverage), `scripts/audit_batch10_recovery.py` (audit offline) e regression test, insieme a questo documento, [evidenza JSON](batch-10-recovery-audit-2026-11-16.json) e `docs/stato-progetto.md`. Nessuna rimozione da `data/catalog.json`, nessuna modifica a `data/sources.json` e `data/companies.json`, nessun runtime ATS abilitato.

**Costi incrementali diretti di ricognizione collector:** **zero GET, zero rendering, zero byte**; sono stati letti file GitHub e alcuni siti pubblici tramite web, non misurati da BudgetClient. La patch non introduce alcuna richiesta giornaliera aggiuntiva né servizi a pagamento. **Il beneficio produttivo non è misurato finché il codice non è integrato e una successiva raccolta ordinaria non pubblica l'esito**. Anche i potenziali risparmi di tempo sulle 108 righe sono un beneficio atteso e non un risparmio registrato dal runner.

**Primo punto incompleto:** far superare CI e review, quindi squash merge senza sovrascrivere modifiche di altre sessioni; misurare al primo ciclo successivo il numero di `historical_unreviewed_external_records`, record e ID verificati invariati e carico di richieste reale. Per aumentare **davvero** gli stage, affrontare per fonte l'identità CTA e il modulo finale di L'Oréal, JDE e AXS quando accessibile, mai promuovendo HTTP 200 o browser history. Per tutti i cinque paesi restano gap nell'universo delle fonti e nessuno è dichiarato mappato nazionalmente.

