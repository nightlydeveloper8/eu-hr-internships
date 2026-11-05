# Ampliamento del registro — 5 novembre 2026

Il registro passa da 70 a **530 datori**, con 460 aggiunte nette. Sono datori potenziali per la ricerca: la compatibilità con stage HR resta da accertare. Comprendono imprese, università, ricerca ed enti pubblici.

## Fonti eseguite

- [Fontys Career Event](https://fontyscareerevent.nl/eindhoven/deelnemende-bedrijven.php?lang=en), Paesi Bassi.
- [IKOM — Technische Universität München](https://ikom-tum.de/de/messen/ikom/2026), Germania, con collegamento al singolo espositore.
- [PhDTalent Career Fair](https://careerfair.phdtalent.fr/en/exhibitors/), Francia.

Dai tre elenchi pubblici sono stati selezionati 472 candidati non già riconosciuti per nome o dominio. Per ciascuno è stata tentata la lettura del sito indicato dall'organizzatore, rispettando robots.txt. Sono stati cercati collegamenti carriera realmente presenti sulla pagina e verificata la raggiungibilità del primo collegamento candidato. Nessun percorso o identificativo ATS è stato indovinato. Errori, restrizioni e collegamenti candidati restano nell'audit `employer-mapping-audit.json`; non sono stati conservati contatti personali o descrizioni di offerte.

Cinque candidati con collegamento HTTP e senza una destinazione HTTPS verificata restano solo nell'audit: CBRE, Evergy Engineering, JetBrains, RD2 Conseil e Tortoise. Questo non indica che non abbiano opportunità; serve approfondire il loro canale ufficiale.

Le regole esplicite in `data/company-identity-rules.json` consolidano Volkswagen/SEAT/TRATON/MAN/Porsche/MHP, Bosch/Rexroth e le due denominazioni di Boston Consulting Group. Le denominazioni alternative e i collegamenti restano conservati. La deduplicazione per nome, dominio e queste regole non equivale a una ricostruzione esaustiva di tutti i gruppi societari: altre affiliazioni richiedono revisione.

## Risultato verificabile

- 530 record univoci nel registro.
- 401 record con pagina carriera registrata, incluse quelle già presenti prima di questa tranche.
- 331 record con pagina carriera raggiungibile verificata nella nuova mappatura, dopo il consolidamento.
- 13 datori con raccolta automatica configurata.
- 67 nuovi record richiedono revisione dell'accesso al sito; non sono presentati come verificati.

La raggiungibilità di una pagina non prova che il canale copra tutti gli annunci dell'azienda, né che vi siano stage HR. Una pagina di un'agenzia può anche contenere offerte per clienti: serve una revisione del perimetro prima dell'integrazione. Nessuna nuova fonte è abilitata automaticamente da questa importazione.

La distribuzione dei nuovi candidati si concentra su tre territori. Questa tranche non costituisce copertura uniforme dei 27 paesi UE. Il paese del career fair compare solo fra i paesi da approfondire; non vengono dedotte sedi né regioni da tale partecipazione. Il conteggio delle sedi confermate rimane indipendente.

## Proseguimento operativo

1. Dare priorità alle pagine ufficiali con programmi studenti e offerte HR esplicite, verificando il perimetro del canale.
2. Identificare gli ATS, le sitemap e i feed ammessi e integrarli con prove di raccolta effettive.
3. Confermare le sedi con fonti aziendali e assegnare le regioni quando documentabili.
4. Estendere gli elenchi universitari con fonti regionali per i territori meno rappresentati, soprattutto gli altri paesi UE e le province olandesi meno coperte.

Per ripetere la ricerca: `python3 scripts/map_employers.py --cache /tmp/employer-mapping --workers 6`, poi `python3 scripts/company_coverage.py`. La cache deve esistere; se mancano le pagine degli elenchi vengono lette dalle fonti ufficiali. I record già presenti, gli alias e i domini conosciuti vengono esclusi; l'audit conserva i dettagli delle nuove verifiche.

Validazione: 49 test Python superati e sito statico ricostruito. La nuova pagina del registro gestisce i candidati con solo sito aziendale, mostra la provenienza e permette la ricerca delle denominazioni alternative.
