# Raccolta automatica dell'intero registro

Il comando `python -m collector.daily provision` collega ogni azienda priva di una fonte attiva al raccoglitore generale. La trasformazione è ripetibile senza duplicare aziende o fonti. Il registro corrente contiene 842 aziende e 842 fonti attive: 40 connettori specifici e 802 raccoglitori generali.

Ogni mattina il flusso GitHub Actions avvia otto gruppi indipendenti, ciascuno con sei letture concorrenti. L'orario programmato è 06:17 UTC: 07:17 in Svizzera d'inverno, 08:17 d'estate. Il servizio di pianificazione può partire in ritardo. Il computer personale non deve restare acceso.

Per le aziende senza una pagina carriera, il punto di partenza è il sito ufficiale censito. Il raccoglitore segue collegamenti carriera effettivamente presenti, compresi portali esterni. Riconosce sistemi pubblici Greenhouse, Lever, Personio, Recruitee, Ashby e SmartRecruiters; verifica l'accesso e usa i rispettivi connettori quando disponibile. Legge inoltre le sitemap dichiarate dal datore in robots.txt, i dati JobPosting e il contenuto visibile delle pagine aziendali. Per gli elenchi dinamici utilizza un browser isolato senza credenziali, seguendo soltanto controlli di paginazione. Non invia candidature.

La lettura non usa il nome dell'azienda o il paese candidato come prova dell'esistenza o della sede di un'offerta. I titoli degli annunci devono soddisfare i criteri HR e internship/working student. Le sedi provengono da indirizzi strutturati o indicazioni riconoscibili nell'annuncio. I due tipi di posizione restano distinti. Prima della pubblicazione i collegamenti vengono controllati; quelli non verificati restano segnalati come tali.

Le offerte HR già individuate vengono ricontrollate prima della scoperta. Le traduzioni dello stesso identificativo ufficiale vengono unificate. Una verifica più vecchia di 48 ore perde lo stato di offerta verificata. Ogni azienda dispone di un limite di tempo e richieste. Le pagine ancora da leggere vengono conservate per la mattina successiva. Una cache tecnica compressa permette di concentrarsi sulle pagine nuove; il contenuto non viene incluso nel sito o nel catalogo pubblico. Le richieste rispettano robots.txt e i ritardi per dominio. Restrizioni, CAPTCHA ed errori rimangono esiti visibili e non vengono aggirati.

Il risultato viene pubblicato solo dopo avere ricevuto esattamente un esito per ogni fonte assegnata. La mancanza di un gruppo interrompe la pubblicazione e conserva il catalogo precedente. Gli annunci validi trovati da una fonte incompleta possono essere aggiunti; una lettura incompleta non chiude gli annunci assenti. La chiusura per assenza richiede tre fotografie complete distribuite su almeno 48 ore. I soli elenchi di pagine e le esplorazioni generali incomplete non autorizzano chiusure per assenza.

## Esiti consultabili

`data/employer-collection.json` distingue:

- `collected`: inventario completo letto, con annunci, anche se nessuno è un tirocinio HR;
- `verified-empty`: elenco verificato esplicitamente vuoto;
- `partial`: annunci letti, ma copertura incompleta;
- `discovery-incomplete`: navigazione effettuata senza un inventario affidabile;
- `blocked-or-failed`: lettura impedita o fallita;
- `not-attempted`: esito mancante, che il flusso completo rifiuta di pubblicare.

Il report contiene per ogni azienda data del tentativo, annunci letti, corrispondenze HR, pagine in attesa e problemi. Il dettaglio tecnico delle fonti resta in `data/coverage.json`. Il numero di raccoglitori configurati non è presentato come numero di siti letti con successo. I conteggi per paese del report aziendale usano i paesi candidati e possono sovrapporsi; le quote operative per paese richiedono invece annunci e sede effettivamente osservati.

L'automazione amplia anche la copertura futura: quando si aggiunge un'azienda al registro, il tentativo di raccolta viene predisposto automaticamente al successivo avvio. Le fonti ancora bloccate vengono ritentate e rimangono nel report degli interventi necessari.
