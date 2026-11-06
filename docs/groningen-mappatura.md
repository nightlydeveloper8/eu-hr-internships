# Groningen: prima raccolta degli stage HR

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
