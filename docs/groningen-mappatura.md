# Groningen: prima raccolta degli stage HR

Stato aggiornato al 6 novembre 2026, 19:10 Europe/Zurich: **PR #2 integrata, raccolta remota completa e pubblicazione automatica in produzione verificate**. Le sezioni di revisione prima del merge sono storiche; le prove finali sono nella sezione conclusiva e nel rapporto JSON.

Verifica del 6 novembre 2026. Inventario iniziale in ampliamento, non censimento esaustivo.

## Risultati per gli studenti

- **HANOS — HR Stagiair**, Groningen: [annuncio e candidatura](https://www.werkenbijhanos.nl/vacatures/hr-stagiair-groningen-2801404). Partenza febbraio 2027, 20 settimane, almeno 4 giorni/settimana, formazione HBO HRM. Il browser del raccoglitore ha caricato il modulo ufficiale con i campi del candidato.
- **Fotofabriek — Stage: HRM**, Groningen: [annuncio](https://www.werkenbijfotofabriek.nl/jobs/stage-hrm-306), [modulo attivo 306](https://www.werkenbijfotofabriek.nl/jobs/apply/306). Partenza febbraio 2027, almeno 20 settimane e 4 giorni/settimana; HBO/WO HRM, psicologia applicata o percorso comparabile. La candidatura mostra la stessa posizione e la sede Fotofabriek, risolta nell’indirizzo ufficiale Osloweg 75, Groningen.

Le date di verifica per ciascuna scheda sono nel catalogo. Nessuna scadenza esplicita è stata pubblicata per queste due posizioni; disponibilità e moduli saranno ricontrollati al ciclo successivo. Non viene dedotta la sufficienza dell’inglese dal testo o dal marchio.

I due annunci IKEA (requisizioni 376337 e 375629) sono distinti, entrambi a Groningen con partenza febbraio 2027. Restano **non verificati e nascosti dai risultati ordinari**: l’elenco ufficiale espone quattro posizioni e i due pulsanti conducono ad Avature, ma robots.txt vieta al raccoglitore il controllo del canale di candidatura. HTTP 200 sulla descrizione non basta. Nessuna restrizione viene aggirata.

Il vecchio stage Global-Tickets restituisce 404; lo stage del Comune di Groningen indicizzato nel PDF aveva scadenza 18 maggio 2026. Nessuno dei due è pubblicato come stage aperto. La posizione Talent & Recruitment di Belsimpel è un working student, non una vacancy di stage. I percorsi HR generali di Belsimpel e Veiligheidsregio Groningen sono separati dagli annunci; Veiligheidsregio accetta soltanto candidature a stage pubblicati.

## Geografia, datori e riuso

Import integrale e paginato delle API CBS 2026 [86247NED](https://www.cbs.nl/nl-nl/cijfers/detail/86247NED) e [86312NED](https://www.cbs.nl/nl-nl/cijfers/detail/86312NED): **10 comuni, 199 località**, riferimento amministrativo 1 gennaio 2026. Il dato BAG annuale è provvisorio. Omonimie nazionali e varianti, inclusi Haren Gn, Harkstede GN e Lageland GN, restano esplicite; nomi senza suffisso richiedono comune/indirizzo. Groningen provincia, comune e città sono unità diverse.

**31 datori provinciali**, di cui **27 qualificati ≥50 addetti**, **26 gruppi qualificati distinti** e **4 dimensioni ignote**. Le qualificazioni su FTE, gruppo, sede e personale retribuito sono esplicite. Volontari e partecipanti a percorsi non vengono sommati agli addetti. Le fonti storiche mantengono il loro anno; le sedi locali non ereditano l’organico del gruppo.

Riutilizzati gli identificativi di Gasunie, Essity, Koninklijke Oosterhof Holman e RUG. RUG ed Essity conservano i propri identificativi storici mentre il nome e i canali si estendono al datore/gruppo. Wagenborg Passagiersdiensten, Royal Wagenborg e Niestern Sander riutilizzano un solo feed del gruppo; i report provinciali deduplicano i gruppi. Non sono tre gruppi indipendenti.

| Comune | Datori qualificati | Dimensione ignota | Stage verificati |
|---|---:|---:|---:|
| Eemsdelta | 4 | 0 | 0 |
| Groningen | 9 | 2 | 2 |
| Het Hogeland | 3 | 0 | 0 |
| Midden-Groningen | 3 | 0 | 0 |
| Oldambt | 3 | 0 | 0 |
| Pekela | 3 | 0 | 0 |
| Stadskanaal | 2 | 0 | 0 |
| Veendam | 3 | 1 | 0 |
| Westerkwartier | 3 | 0 | 0 |
| Westerwolde | 3 | 1 | 0 |

I totali comunali si sovrappongono per i datori con più sedi; quelli provinciali non duplicano il datore. Non esiste ancora un denominatore completo dei datori provinciali, quindi non si dichiara una percentuale di copertura del mercato.

## Raccolta eseguita e automazione

Eseguiti realmente tutti i **30 canali distinti** dei 31 datori. L’ultimo controllo comprende le due verifiche mirate IKEA, che mantengono le candidature non verificate. Il rapporto pubblico distingue configurazione, tentativo recente, inventario osservato letto, lettura parziale, scoperta incompleta e blocco/fallimento. Non si presenta un canale parziale come prova dell’assenza di stage.

Fotografia locale fra i 27 qualificati: 10 discovery-incomplete, 12 partial, 3 collected, 2 blocked-or-failed. I numeri cambiano al ciclo remoto; fa fede il rapporto JSON pubblicato.

Report e interfaccia provinciali ora condividono `collector/provinces.py` e `src/province.js`; il vecchio ingresso Frisia resta compatibile. Nessun modello viene invocato dalla raccolta ordinaria. I controlli dei nuovi moduli sono ripetuti ad ogni raccolta HR, anche quando il testo della scheda arriva dalla cache. L’elenco IKEA confronta i link distinti con il totale pubblicato; l’elenco Fotofabriek segue tutte le pagine numerate osservate. Le limitazioni e gli errori di ogni pagina restano nel rapporto.

Il workflow esistente include Groningen nei 16 gruppi e nella pubblicazione dei rapporti. Orario invariato: **06:17 UTC, 07:17 invernale / 08:17 estiva** in Europa/Amsterdam e Zurigo, soggetto ai ritardi di GitHub.

La prova remota e l’aggiornamento del sito sono registrati separatamente in `docs/groningen-remote-verification.json`: finché non viene osservato un ciclo concluso, non vengono dichiarati verificati.

## File e comandi riproducibili

- `data/groningen-geography.json`: frame CBS completo, omonimie e fonti.
- `data/groningen-employers.json`: lotto di ricerca integrato, sedi e dimensioni.
- `data/groningen-opportunities.json`: programmi HR separati dalle vacancy.
- `data/groningen-coverage.json`: risultati per datore e comune.
- `docs/groningen-research-city.json` e `docs/groningen-research-municipalities.json`: evidenze di partenza.
- `python3 scripts/import_province_geography.py`: import geografico separato dalla raccolta quotidiana.
- `python3 scripts/integrate_groningen.py`: integrazione idempotente senza duplicare i datori già censiti.
- `python3 scripts/collect_province.py groningen`: esecuzione mirata di tutti i canali provinciali.

Verifica locale: 130 test Python, 12 test frontend, 52 esempi di classificazione e build statica. I test coprono paginazione, conteggi dichiarati, gruppi/feed condivisi, separazione delle province, freschezza delle verifiche e moduli con requisizione corrispondente.


## Revisione prima del merge — 6 novembre 2026

La PR #2 è ancora aperta. Main rimane al commit `a3732da8e17b39c4d86ef33774a934d573202fd4`; non è stata tentata alcuna modifica a main in questa revisione, come richiesto dall’utente. Il confronto con main conserva tutti i 1.757 datori, le 1.803 fonti e i 147 annunci precedenti: nessuna perdita di stato, paesi, codici regionali, sedi extra Groningen o metadati della Frisia. Non risultano nomi di aziende normalizzati o URL di annunci duplicati.

Corretta una discordanza nei rapporti: se fallisce una scheda o il controllo della candidatura, lo stato rimane parziale e `complete`/`closure_complete` diventano falsi. L’eventuale inventario iniziale letto resta documentato separatamente in `inventory_complete`. Normalizzati soltanto i due esiti storici discordanti IKEA/Fotofabriek, mantenendo le date dei tentativi originali. Due test aggiuntivi verificano conservazione degli annunci precedenti e nuovo controllo della candidatura anche con testo in cache.

Il codice corretto `4a0b5f6c0735f239e35c009c46c559ed14f6e8a1` supera 132 test Python, 12 test frontend e 52 esempi di classificazione, sia in locale sia nei controlli remoti. [Anteprima revisionata](https://336bab89.people-placement-eu.pages.dev/groningen.html): due stage, dieci comuni, due programmi distinti, filtro funzionante, nessun errore di pagina o overflow mobile; Frisia mantiene sette stage e diciotto comuni. I moduli ufficiali HANOS/Fotofabriek sono stati ricontrollati con esito positivo.

La produzione pubblica è stata aperta in una sessione anonima: catalogo di 147 annunci e 27 paesi, Frisia con sette stage. Groningen non è ancora pubblicata: `/groningen.html` restituisce HTTP 200 tramite il fallback del sito, senza la pagina provinciale. L’ultima raccolta completa già in produzione è riuscita ([workflow 42221643385](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42221643385)); non include Groningen. Il ciclo remoto con Groningen e l’aggiornamento automatico della produzione rimangono da verificare dopo il merge esplicitamente autorizzato. Nessun criterio di completamento della produzione viene dichiarato soddisfatto sulla base della sola anteprima.

Prove dettagliate, date UTC e verifiche ancora necessarie: `docs/groningen-remote-verification.json`.


## Verifica finale in produzione — 6 novembre 2026

La [PR #2](https://github.com/nightlydeveloper8/eu-hr-internships/pull/2) è stata integrata dopo autorizzazione esplicita nel commit `e8a692d630079f8aadb1c3c1542370a28ecb6686`. Il [workflow 42264583427](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42264583427) è concluso con successo: test, tutti i 16 gruppi, consolidamento, validazione e pubblicazione. I log confermano 132 test Python, 12 test frontend e 52 esempi di classificazione.

Il bot ha pubblicato il [commit 119c6fb825b4b25c1f01bfb51e0d49a914cecc52](https://github.com/nightlydeveloper8/eu-hr-internships/commit/119c6fb825b4b25c1f01bfb51e0d49a914cecc52). L’[artefatto catalog-and-coverage](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42264583427/artifacts/13527423064), conservato da GitHub per 14 giorni, contiene nove file tutti identici al commit del bot. Cloudflare ha distribuito automaticamente quel commit nel deployment `ca0da97e-4a3b-44cd-930c-c433179c9cb7`.

La [produzione Groningen](https://people-placement-eu.pages.dev/groningen.html) è stata aperta in una sessione anonima dopo il deployment del bot. La pagina provinciale effettiva è presente all’URL ordinario, con due stage verificati, dieci comuni, due programmi distinti e filtro funzionante. Moduli ufficiali HANOS e Fotofabriek ricontrollati senza inviare candidature. Desktop e mobile non presentano errori di pagina né overflow del documento; anche apertura/chiusura dei filtri mobili, filtro regionale, filtro Portogallo e reset del catalogo funzionano. La [Frisia](https://people-placement-eu.pages.dev/friesland.html) mantiene sette stage e diciotto comuni.

Il dataset pubblico ha timestamp `2026-11-06T18:05:57.251698+00:00` (19:05:57 Europe/Zurich), identico al commit del bot: 183 record, 30 nuovi, tutti i 153 record precedenti conservati. Il controllo specifico sulle 50 fonti parziali/fallite che avevano annunci precedenti conferma la conservazione di tutti i loro 106 record e nessuna chiusura per assenza. I cambiamenti di disponibilità restano espliciti: due precedenti schede sono nuovamente verificate, due diventano non verificate secondo le normali regole di disponibilità, senza eliminazioni.

Sono stati tentati tutti i 1.782 canali attivi dei 1.784 datori, compresi i 30 canali dei 31 datori Groningen e tutti gli 893 datori frisoni. Questo **non significa che tutti i siti siano stati letti completamente**. Fra i 27 qualificati Groningen: 3 datori con inventario osservato letto, 12 letture parziali, 9 scoperte incomplete e 3 blocchi/fallimenti. Non risultano esiti non riusciti con `complete: true`. I due annunci IKEA restano non verificati e nascosti; il monitor di salute continua a segnalare le fonti problematiche.

La catena merge → raccolta → consolidamento → commit del bot → Cloudflare → dati pubblici è verificata. La pianificazione giornaliera esistente resta alle 06:17 UTC (07:17 in inverno / 08:17 in estate a Zurigo e Amsterdam), soggetta ai ritardi di GitHub; il prossimo avvio schedulato del codice aggiornato è un evento futuro, non viene dichiarato già osservato. Nessun servizio a pagamento, chiamata ricorrente a modelli o modifica architetturale aggiuntiva è stato introdotto.

Date dei controlli, passaggi per job, hash dell’artefatto, confronto dei file e risultati completi: `docs/groningen-remote-verification.json`.
