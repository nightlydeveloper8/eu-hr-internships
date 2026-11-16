# Lotto 03 — Germania, Danimarca, Polonia e Finlandia

**Quattro indizi verificati, zero nuove fonti ammissibili all'integrazione.** Un modulo utilizzabile osservato tecnicamente (Constructor) non basta senza il collegamento ufficiale richiesto dal datore al tenant. Nessun nuovo annuncio verificato aggiunto, nessun registro o gate modificato.

| Paese | Canale | Evidenza osservata | Esito |
|---|---|---|---|
| DE | Constructor TECH / Greenhouse | Feed con 28 posizioni, uno stage HR a Bremen, ID 4772353101; stessa pagina/titolo e modulo visibile abilitato. Il sito aziendale Careers legge un endpoint `/api/v2/jobs` vietato da robots: non scaricato. | Identità del marchio coerente, ma collegamento datore→tenant esatto non stabilito nelle pagine/asset consentiti. Proposta incompleta, non attivabile. |
| DK | FirstMind / Greenhouse | Feed completo con 38 posizioni; il Global Talent Intern indicizzato non compare. Nessun ruolo HR per studenti classificato nel feed. | Non è un errore attuale del filtro da correggere. Non trasformare ruoli commerciali Talent Advisor/Associate in stage HR. L'assenza non equivale a una dichiarazione universale di chiusura. |
| PL | Saint-Gobain | robots 404 gestito secondo la policy; scheda osservata HTTP 403, nessun retry. | Inventario e candidatura sconosciuti. Datore già censito: non creare doppioni. La correzione del titolo polacco è offline, non prova disponibilità. |
| FI | Barona Teollisuus Oy | JobPosting 116361 a Tampere, datore dichiarato, scadenza 7 dicembre; sito corporate collega Barona Careers. Pagina con “Sign in and Apply”, senza modulo anonimo o URL di candidatura anonima stabiliti. | Candidatura non verificata, nessuna autenticazione. La piattaforma è collegata al gruppo; identità legale specifica non inserita nel registro. |

## Constructor: cosa è provato e cosa manca

Il feed pubblico documentato Greenhouse restituisce l'URL EU [HR Intern](https://job-boards.eu.greenhouse.io/constructortech/jobs/4772353101), lo stesso ID e titolo del modulo osservato. I campi candidato e il submit sono visibili abilitati. Il dominio EU è stato letto solo dopo che feed e board pubblicavano il percorso esatto; nessun ampliamento del gate di produzione.

Il [sito aziendale](https://constructor.tech/about-us) riporta 310+ dipendenti, ma la sezione Careers è un guscio client: l'asset pubblicato importa il componente JobBoard, che legge `/api/v2/jobs`. Il controllo robots vieta quel percorso e la richiesta è respinta prima di leggere contenuti. HTML, asset e privacy notice ispezionati non pubblicano il tenant esatto. Backlink ATS→azienda, logo e descrizione coerenti non sono stati sostituiti al requisito azienda→ATS. Nessuna lettura via proxy, mirror o browser del contenuto vietato.

L'annuncio richiede un CV in inglese e offre corsi di inglese: **questi due elementi non provano inglese come lingua di lavoro**. Dice laurea in corso in HR/Business/Psicologia o materia affine e durata da due mesi. Le domande su istituzioni Constructor e presenza a Bremen hanno risposte Yes/No: non si inventa un'esclusione di altri studenti o un diritto a lavorare da qualunque paese UE. Le opzioni remote/hybrid/office non sono estese automaticamente a tutta l'Europa.

[Proposta Constructor incompleta](batch-03-constructor-pending-proposal.json): fuori runtime, disabilitata, senza nuova azienda. Restano collegamento ufficiale al tenant e revisione delle regressioni del modulo prima di qualunque attivazione. Non è un bundle approvato.

## Correzioni riutilizzabili preparate

**Polacco:** il vecchio filtro non riconosceva Stażysta/Stażystka, ma riconosceva erroneamente “staż pracy” (esperienza lavorativa) nel titolo di un ruolo permanente HR. La modifica riconosce le forme di ruolo e le intestazioni di stage, con contesto, senza promuovere requisiti di esperienza o coordinatori di stagisti. Nessuna deduzione di disponibilità dalla pagina Saint-Gobain bloccata.

**Lingue:** riconosce “Inglés nivel B2” e qualifiche opzionali/negate in spagnolo; mantiene esclusi lingua del CV e corsi offerti. Sul campione reale ridotto BSH, il replay passa da inglese sconosciuto a requisito inglese documentato. **Solo inglese resta sconosciuto.** È un miglioramento di metadati proposto; non un nuovo stage o una verifica live rinnovata. Istruzioni CV/corsi Constructor continuano a non provare la lingua di lavoro.

Sono modifiche al codice da rivedere nella PR: se integrate, i filtri si applicheranno alle fonti esistenti. Nessun merge o effetto in produzione in questa attività.

## Misure, prove e stato

- **22 richieste logiche, 10,940 secondi-fonte cumulati, 1.962.584 byte, zero rendering**; cinque query web separate. Budget per datore 12 richieste/45 s, quattro worker al massimo; rispettati. Constructor raggiunge il limite di richieste e resta sospesa, senza scavare ulteriormente in questa sessione.
- Due inventari letti, 66 posizioni complessive; non sono 66 stage, né copertura completa di Germania/Danimarca. Prima lettura Barona corporate fermata a un redirect fuori scope; la pagina `www.barona.fi/en/barona/` era già pubblicata nel footer e viene letta con host esplicitamente revisionati. Non è un aggiramento di autenticazione.
- Le richieste logiche includono robots e richieste respinte prima del fetch; gli hop dei redirect non hanno contatore separato. Le risposte robots recenti della stessa sessione sono riutilizzate rispettandone direttive e ritardi. Non è una misura di costi monetari o tempo a muro della sessione.
- **407 test Python, 26 Node, 64 esempi di classificazione e build superati**; 12 nuove regressioni. Replay prima/dopo conservato nel [rapporto JSON](batch-03-review-2026-11-16.json), distinto dalle evidenze live.
- Catalogo/registri/workflow invariati rispetto a main `876794ae28578f16500a4ce3aaf2efe32e7a3e8d`: **355 record, baseline di 26 stage verificati**, nessun timestamp rinnovato artificialmente. Nessun login, submit, CAPTCHA bypass, raccolta completa manuale o nuova automazione.

## Prossimo punto incompleto

Review delle due correzioni. Per un eventuale Constructor serve una prova consentita azienda→tenant: la candidatura tecnica da sola non autorizza integrazione. Non ripetere il 403 Saint-Gobain o leggere il suo contenuto tramite un altro canale per aggirarlo; non riprovare l'API Constructor vietata. Barona resta non verificata dietro sign-in; FirstMind va rivalutata solo con una nuova evidenza di stage.

Per il prossimo lotto, anticipare il controllo del collegamento pubblico datore→ATS e della candidatura anonima **prima** di investire nell'inventario. Cercare più datori nei paesi senza stage recenti con questi due requisiti osservabili; evitare un'altra sessione dedicata a un singolo blocco. Nessuna autorizzazione di merge/rollout deriva da questa revisione.
