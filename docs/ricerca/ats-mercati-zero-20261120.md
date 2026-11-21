# Mercati PL, IE e CZ: inventari aziendali ATS prioritari — 20 novembre 2026

## Baseline e metodo

Snapshot pubblicato di `main` dopo la #86 (catalogo 887 ID, 39 candidature HR dirette in sei paesi). Audit offline del catalogo alla data del 20 novembre: **Polonia 10 record, tutti unverified; Irlanda zero; Cechia tre record, due closed e uno unverified**. Non confondere schede con candidature. Il confronto EURES #88 ha migliorato la pertinenza geografica ma non il rendimento in candidature, quindi non propone l'attivazione della nuova rotazione.

`python -m scripts.official_ats_country_queue --countries PL IE CZ SE` rigenera una graduatoria dai soli record catalogati: conteggi, host ATS riconoscibili, identificativi osservati, sovrapposizioni per URL e piste su cui verificare un modulo. Non fa rete, non modifica il catalogo, non invia candidature. Ogni indicazione di famiglia ATS deriva solo dall'URL osservato e **non dimostra né titolarità né modulo attivo**. Un paese con zero record (IE) richiede discovery separata da inventari ufficiali.

## Piste esterne osservate, NON promosse nel catalogo

| Paese | Inventario ufficiale / datore | Annuncio osservato e ID | Motivo e controllo successivo |
| --- | --- | --- | --- |
| PL | [SmartRecruiters Averna1](https://jobs.smartrecruiters.com/Averna1/744000152889189) | Dział HR – praktyka, `744000152889189`, Wrocław | Stage HR di tre mesi e buona conoscenza inglese. Leggere board aziendale corrente, verificare che ID e form pubblico siano collegati; la CTA “I'm interested” non basta |
| PL | [SmartRecruiters CliffordChance](https://jobs.smartrecruiters.com/CliffordChance/744000151621729) | HR Intern, `744000151621729`, Varsavia | Stage retribuito, inglese almeno B2. Verificare inventario corrente e modulo specifico con ID, senza inferire `oneclick-ui` |
| IE | [Regeneron careers](https://careers.regeneron.com/en/jobs/?employment=Employee_Type_Intern) | Intern, HR Technology and Analytics, `R52961`, Dublino | Indice aziendale corrente e dettaglio dedicato: https://careers.regeneron.com/en/jobs/r52961/intern-hr-technology-and-analytics/ ; scadenza indicata 4 dicembre 2026. Richiede competenze quantitative; confermare idoneità HR e destinazione di candidatura senza accedere al login |
| CZ | [Manifesto Group careers](https://manifesto.careers-page.com/) | HR Intern, `1e8e178e-3cb5-40d7-993b-517ec3ae1c54`, Praga | Pagina https://manifesto.careers-page.com/jobs/1e8e178e-3cb5-40d7-993b-517ec3ae1c54 — stage **non retribuito**, richiede ceco e inglese; verificare form specifico attivo e che resti nell'inventario del datore |
| CZ | [Amazon jobs](https://amazon.jobs/en/jobs/10561439/operations-human-resources-partner-intern-6-months-2027) | HR Partner Intern, `10561439`, Kojetin | Già censito come `unverified` nel catalogo: **non creare duplicato**; account/robots e accesso al modulo non superabili per supposizione |
| SE | [JobTech → Jobandtalent](https://arbetsformedlingen.se/platsbanken/annonser/31558200) | `31558200` → Teamtailor `8503489` | Conversione con prova solo in staging #89/#91; trasferire il metodo ad altri datori soltanto dopo prova autonoma di legal owner e inventario ATS |
| SE | [JobTech → Suzuki Garphyttan Varbi](https://arbetsformedlingen.se/platsbanken/annonser/31718353) | ID pubblico `31718353`, Varbi `989715` | Canale Varbi con ID nel link osservato; idoneità, azienda e modulo da confermare live. Nessuna promozione automatica |
| SE | [JobTech → Bosch SmartRecruiters](https://arbetsformedlingen.se/platsbanken/annonser/31626048) | ID pubblico `31626048`, posting SmartRecruiters `744000156530019` | Nuova famiglia ATS con ID strutturato; verificare possesso employer e modulo same vacancy, senza usare il vecchio gate specifico di Jobandtalent |

Le prime quattro piste esterne emergono da pagine pubbliche del datore e non dalla raccolta ordinaria. La loro presenza qui è una **coda di revisione tecnica**, non un inserimento di offerte nel catalogo né una prova aggiornata di candidabilità policy v2.

## Sequenza proposta, con stop misurabili

1. **PL / SmartRecruiters**: primo lotto due board e provider condiviso. Prima elenco corrente, poi ID esatto, candidatura GET nel perimetro consentito; se manca il form visibile o robots blocca, segnare incomplete. Non costruire `oneclick-ui` da pattern.
2. **CZ / careers-page.com**: testare inventario attuale di Manifesto e corrispondenza ID/form. Il provider consente potenzialmente riuso fra più datori; l'annuncio non retribuito rimane segnalato.
3. **IE / Regeneron**: inventario HR/Intern aziendale e una sola pagina di candidatura. Costo e chiusure basati su GET effettivi, non su stime. Stryker/Fidelity restano piste secondarie per rischio login.
4. **SE / Varbi e SmartRecruiters**: estendere il percorso di review JobTech–ATS solo a identità di datore indipendenti e singole fonti autorizzate, non a tutto il feed nazionale in un solo rollout.

**Misurazione necessaria prima del rollout:** per ciascun board contare GET, byte, pagine HR, ID distinti nuovi/conversioni, moduli same-ID aperti e verifiche v2 entro 48 ore; rapporto nuove candidature / 100 GET, zero closure se inventario parziale. Il rapporto per famiglia ATS **non è ancora misurato live**: non è corretto assegnare una resa numerica a questi inventari. Questa ricerca non modifica sorgenti attive né policy e ha consumato **0 richieste BudgetClient**.
