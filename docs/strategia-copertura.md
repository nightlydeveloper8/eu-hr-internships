# Strategia: partire dalle aziende, per territorio

## Diagnosi

Il primo catalogo conteneva sette stage in quattro paesi, provenienti da appena dieci bacheche aziendali. Non era una misura del mercato europeo. La selezione delle aziende era guidata soprattutto dalla facilità tecnica di collegare alcuni ATS e lasciava fuori importanti datori di lavoro. Le fonti erano già ufficiali, ma il campione era insufficiente.

L'obiettivo diventa costruire e mantenere un universo di datori di lavoro, poi controllarne i canali ufficiali. Il numero di annunci è un risultato della copertura e della stagione, non una quota da raggiungere includendo offerte dubbie.

## 1. Territori comparabili, nomi locali conservati

`data/geography.json` importa i nomi e i codici ufficiali Eurostat NUTS 2024 per tutti i 27 paesi: 244 aree di livello 2 e 1.165 di livello 3. Sono unità statistiche; non equivalgono tutte a regioni/province amministrative. Nei Paesi Bassi le 12 province corrispondono al livello 2. Le suddivisioni di livello 3 permettono di misurare ulteriori lacune, senza inventare una lista universale di province.

Fonte riproducibile: [tabella Eurostat/GISCO](https://gisco-services.ec.europa.eu/distribution/v2/nuts/csv/NUTS_AT_2024.csv). Sono usati solo nomi e codici, senza geometrie di confine. La versione è esplicita e l'importazione verifica la gerarchia e tutti i 27 paesi.

## 2. Registro persistente delle aziende

`data/companies.json` registra ogni datore una volta, con pagina carriera ufficiale, provenienza della ricerca, paesi da approfondire, sedi documentate, regione, eventuale piccola area, canali di recruiting, priorità e prova di un effettivo stage HR quando disponibile.

**Una sede aziendale non dimostra che esista uno stage.** Un paese candidato non è una sede verificata. Un'azienda individuata non è necessariamente già monitorata. Queste distinzioni compaiono nel registro pubblico e nel rapporto di copertura.

Il primo ampliamento contiene 64 aziende e almeno una sede documentata per ciascuna provincia olandese. Dodici aziende hanno un canale di raccolta abilitato. Le altre restano una coda di integrazione, non sessantaquattro fonti già funzionanti.

## 3. Come individuare aziende per ogni area

Per ogni territorio usare, nell'ordine:

1. Agenzie regionali di sviluppo e investimento: elenchi di imprese, insediamenti industriali, headquarters, shared-service centre e distretti produttivi.
2. Camere di commercio e associazioni industriali: elenchi pubblici e consentiti, senza contatti personali né registri a pagamento.
3. Università e career centre: aziende partner, employer day, programmi di tirocinio e convenzioni pubbliche.
4. Siti ufficiali delle aziende: sedi effettive, team HR, programmi studenti e storico di stage. Le ricerche web servono a scoprire queste pagine, non a sostituire la fonte originale.

Considerare grandi aziende, imprese medie con un team HR, aziende industriali locali, logistica, servizi, sanità, università, enti e scale-up. Limitarsi ai marchi più famosi può aumentare la concentrazione sulle stesse opportunità molto visibili. Non attribuire un numero di candidati o un'etichetta “poca concorrenza” senza dati dell'azienda.

Obiettivo operativo iniziale: portare le province olandesi verso **15–25 datori verificati ciascuna**, con sedi e canali reali. Si tratta di un obiettivo di ricerca, non di una garanzia di offerte e non di una soglia uniforme da imporre a territori con economie differenti. Poi estendere la stessa ricerca agli altri paesi e alle aree meno coperte. Evitare di contare molte sedi dello stesso gruppo come aziende indipendenti.

`docs/company-discovery-queue.json`, generato dallo script di copertura, ordina le aree con priorità ai Paesi Bassi e rende visibili quelle ancora da ricercare. Le query sono compiti da eseguire e verificare, non ricerca già completata. Una ricerca esaustiva di tutte le aziende di ogni area europea resta lavoro da svolgere.

## 4. Collegare il canale più stabile di ogni azienda

Ordine di preferenza:

1. API pubblica e documentata dell'ATS aziendale.
2. Feed ufficiale o elenco strutturato dell'azienda.
3. Sitemap ufficiale e pagine `JobPosting` JSON-LD.
4. Adattatore specifico per la pagina aziendale, quando consentito e testabile.
5. Stato di revisione manuale quando l'accesso richiede autenticazione, presenta restrizioni o non è sufficientemente chiaro.

Il rilevatore in `company_registry.py` può proporre un ATS dai collegamenti della pagina carriera dichiarata. Non indovina identificativi e non abilita automaticamente fonti prive della verifica di accesso.

I nuovi adattatori Danone e Unilever inventariano tutte le URL di lavoro nell'ambito dichiarato delle rispettive sitemap. Gli slug descrittivi aiutano a selezionare le pagine da approfondire; il titolo e la sede estratti dalla pagina ufficiale decidono l'inclusione finale. URL opache, pagine non presenti nella sitemap e sinonimi non ancora riconosciuti sono lacune dichiarate. La scomparsa da una sitemap non chiude un annuncio: non è una prova sufficiente di chiusura.

Danone richiede un parser dei frammenti pubblici presenti nel documento, Unilever pubblica `JobPosting` JSON-LD. Nessun browser automatizzato, endpoint autenticato o aggiramento di protezioni è necessario per questi due canali. I robots vengono verificati a ogni esecuzione. Se robots restituisce HTML invece di regole leggibili, il canale richiede revisione.

## 5. Controlli, freschezza e qualità

- La raccolta giornaliera esistente continua a controllare tutte le fonti abilitate e pubblica insieme catalogo e copertura aziendale.
- La prima scoperta e la data di pubblicazione restano separate: un annuncio appena trovato può essere vecchio. Il sito consente già l'ordinamento per prima scoperta.
- Dopo aver misurato tempi, limiti dei datori e consumo delle risorse, i canali prioritari potranno passare a controlli ogni sei ore. Questa frequenza più alta non è attivata da questo ampliamento.
- Estrarre lingua e iscrizione universitaria solo da affermazioni esplicite. La lingua dell'interfaccia del sito non determina quella del testo dell'annuncio.
- Usare casi negativi reali nella valutazione: per esempio “Global Feed Sustainable Sourcing” riguarda acquisti/fornitori, non Talent Acquisition.
- Conservare gli annunci e segnalare problemi quando una fonte fallisce. Una pagina mancante o un parser cambiato non deve cancellare il catalogo.

## 6. Misure di avanzamento

Controllare per paese, regione e piccola area:

- aziende individuate e sedi confermate;
- aziende con monitoraggio abilitato e fonti riuscite;
- aree ancora non ricercate o senza collegamenti funzionanti;
- offerte effettive, nuove scoperte, lingue esplicite e campi sconosciuti;
- ultimo controllo riuscito e cause dei blocchi.

Il rapporto `data/company-coverage.json` e la pagina `/employers.html` permettono di ispezionare l'avanzamento. Il filtro per regione degli annunci include solo corrispondenze sede/città documentate; non assegna tutte le offerte di un gruppo alla sua sede principale. Le piccole aree senza una sede assegnata restano esplicitamente senza ricerca/conferma, anche se la regione superiore ha già aziende.

## Comandi di manutenzione

```sh
python3 scripts/import_geography.py
python3 scripts/company_coverage.py
python3 scripts/company_coverage.py --inspect-country NL --limit 10
python3 -m collector.pipeline
python3 scripts/company_coverage.py
```

L'importazione geografica è un'operazione di manutenzione: non viene scaricata ogni giorno. La ricerca di nuove aziende resta distinta dalla raccolta giornaliera delle offerte già collegate. Non sono richiesti database a pagamento, API di ricerca a pagamento o inferenza AI periodica.
