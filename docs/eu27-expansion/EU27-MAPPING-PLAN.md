# Piano operativo per mappare UE27 senza falsi positivi

**Checkpoint:** 16 novembre 2026, catalogo del ciclo ordinario 16:51:25 UTC: **362 annunci**, **28 stage HR verificati in 5 paesi**, **1 working student DE**. Nessuna copertura nazionale completa attestata. I dati precedenti sono uno snapshot: per un controllo aggiornabile usare `python -m scripts.audit_eu27_coverage`, un audit **offline** sul catalogo e registri già prodotti, che NON contatta aziende.

## Cosa significa «completare la mappatura»

La coda di ricerca esiste già per **27/27 stati membri**: 1.926 identità di ricerca e 2.202 attività di canale, ma non prova 27 mercati monitorati. Nessuna analisi finita può dimostrare che ogni azienda europea sia stata scoperta. Definiamo quindi una mappatura **operativamente completa e revisionabile** per ogni paese solo quando sono documentati:

1. **Universo/scope di datori e fonti:** identità aziendali uniche, sedi collegate al paese, settore/dimensione quando documentata, fonti aziendali ufficiali con canale ATS e host.
2. **Accesso e inventario:** `robots.txt`, permessi, limiti/timeout, ricerca locale e inglese, paginazione/completezza e checkpoint, distinguendo blocked, partial, verified-empty. Non dichiarare «mercato vuoto» da un blocco.
3. **Opportunità realmente candidabili:** ogni posting HR riconosciuto dalla policy v2 ha titolo/ID/località, data/freschezza, CTA e **modulo anonimo sullo stesso annuncio**, oppure resta unverified. Nessun bypass o invio.
4. **Monitoraggio quotidiano:** source registrata e abilitata solo dopo autorizzazione del rollout, due cicli ordinari stabili, statistiche di richieste, byte, durata, errori, costo incrementale e confronto ID; non forzare la conferma della vacancy.
5. **Review esplicita del paese:** rapporto datato delle fonti nel perimetro dichiarato, lacune residue, copertura geografica effettiva e accettazione del livello di copertura. `national_mapping_complete` resta **false** finché non c'è tale evidenza.

Un paese può avere temporaneamente **zero stage aperti** anche con buone fonti; per contro un solo stage verified non dimostra mappatura nazionale.

## Tabella di avanzamento e assegnazione senza duplicazioni

| Paese | Lotto di verifica | Stage verified | Working student verified | Mappatura nazionale |
| --- | ---: | ---: | ---: | --- |
| AT | 08 | 0 | 0 | Non dimostrata |
| BE | 10 | 3 | 0 | Non dimostrata |
| BG | 06 | 0 | 0 | Non dimostrata |
| HR | 07 | 0 | 0 | Non dimostrata |
| CY | 07 | 0 | 0 | Non dimostrata |
| CZ | 09 | 0 | 0 | Non dimostrata |
| DK | 08 | 0 | 0 | Non dimostrata |
| EE | 06 | 0 | 0 | Non dimostrata |
| FI | 08 | 0 | 0 | Non dimostrata |
| FR | 10 | 5 | 0 | Non dimostrata |
| DE | 08 | 0 | 1 | Non dimostrata |
| GR | 07 | 0 | 0 | Non dimostrata |
| HU | 06 | 0 | 0 | Non dimostrata |
| IE | 09 | 0 | 0 | Non dimostrata |
| IT | 06 | 0 | 0 | Non dimostrata |
| LV | 06 | 0 | 0 | Non dimostrata |
| LT | 06 | 0 | 0 | Non dimostrata |
| LU | 09 | 0 | 0 | Non dimostrata |
| MT | 07 | 0 | 0 | Non dimostrata |
| NL | 10 | 18 | 0 | Non dimostrata |
| PL | 08 | 0 | 0 | Non dimostrata |
| PT | 10 | 1 | 0 | Non dimostrata |
| RO | 09 | 0 | 0 | Non dimostrata |
| SK | 06 | 0 | 0 | Non dimostrata |
| SI | 06 | 0 | 0 | Non dimostrata |
| ES | 10 | 1 | 0 | Non dimostrata |
| SE | 08 | 0 | 0 | Non dimostrata |

I lotti **06–10** coprono esattamente una volta i 27 codici paese. È una **pianificazione**, non cinque job schedulati e non un completamento delle mappature:

- **06 — EE, LV, LT, BG, IT, HU, SI, SK**: completata la ricognizione mirata su dieci indizi, quattro esclusi o separati e cinque piste da confermare; nessuna fonte attivata. <Link in Markdown not needed>
- **07 — CY, GR, HR, MT**: canali ufficiali e termini in greco, croato e lingue locali; almeno un inventario aziendale completo per datore esaminato, poi espandere la coda.
- **08 — AT, DE, DK, FI, PL, SE**: sostituire canali scaduti/bloccati con feed pubblici ufficiali; evitare workaround robots, 403, login e CAPTCHA.
- **09 — CZ, RO, IE, LU**: convertire le piste già raccolte quando i moduli sono specifici e accessibili, senza ripetere Manifesto 429 o offerte chiuse.
- **10 — NL, BE, FR, ES, PT**: approfondire la copertura dei paesi già con stage verificati, recuperare record unverified per cause strutturali, misurare due cicli.

**Metriche dopo ogni lotto:** n. fonti ufficiali nuove/ammissibili; inventari letti e completi vs partial/blocked; HR student jobs nuovi distinti; candidate-to-verified conversion; `verifiedInternships` per paese e delta totale; richieste/tempo/byte/rendering; CI, merge, source activation, workflow e produzione verificata. Nessun numero di aziende o test supera in importanza il conteggio delle candidature reali.

## Implementazione riutilizzabile

```bash
python -m scripts.audit_eu27_coverage --output /tmp/people-placement-eu27-audit.json
```

L'audit legge `data/catalog.json`, `data/companies.json`, `data/sources.json` **senza rete**. Produce 27 righe anche quando un paese non ha annunci; conta soltanto posting HR policy v2 verificati nelle ultime 48 ore, distingue `internship` da `working-student`/traineeship e le sedi ambiguamente dichiarate. Segnala aziende «target di ricerca» separatamente dalle fonti abilitabili e **non** attribuisce automaticamente completezza territoriale. I risultati possono essere ricalcolati al termine di ogni ciclo da un operatore; **non è stata aggiunta una nuova automazione quotidiana**.

**Prossimo passo immediato:** preflight limitato con client consentito per DIGI MEDIA LV e Heritage Holdings IT, poi Girteka LT. Solo fonti con prova robots, tenant e modulo policy v2 entrano in proposta di attivazione. Se nessuna supera il gate, il prossimo lotto geografico prosegue comunque senza conteggi artificiali. [Evidenza lotto 06](BATCH-06-REVIEW.md).
