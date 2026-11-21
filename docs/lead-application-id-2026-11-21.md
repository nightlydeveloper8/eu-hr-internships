# Fase 1 — 38 lead con errore di identificativo

Audit #106 ricalcolato sul catalogo pubblicato in `a71b260`, snapshot 21 novembre 07:35 UTC. I [38 record](lead-application-id-2026-11-21.csv) riportano URL, fonte, adapter e identificativi disponibili. `catalog_source_posting_id` è il valore pubblicato per la vacancy. Restano sconosciuti gli eventuali ID strutturati che il verificatore ha letto durante il tentativo fallito. In tutte le 38 righe `apply_url` copia l'URL della vacancy e manca `application_verification`. Il messaggio di errore del verificatore è registrato senza il target scartato.

| Categoria | Lead | Evidenza |
| --- | ---: | --- |
| (a) Stesso posting con rappresentazione diversa dimostrata | 0 | Nessuna coppia documentata |
| (b) Identificativo osservato diverso | 1 | Landal ha pubblicato `JR104108`. La CTA Workday storica contiene `JR104108-1`. L'equivalenza resta sconosciuta. |
| (c) Dati insufficienti | 37 | Per 36 manca la CTA. Per L'Oréal 229626, una lettura storica ha visto lo stesso ID esatto su un host non approvato, con HTTP 406. Il target del tentativo fallito resta sconosciuto. |

Evidenze storiche nel [rapporto JDE/Landal](jde-application-identity-2026-11-15.json) e nella [revisione L'Oréal](eu27-expansion/BATCH-10-REVIEW.md).

**Recupero stimato dalla PR: 0.** I dati disponibili lasciano in vigore il confronto esatto. Il test Workday copre il caso positivo di ID esatto e rifiuta anche la variante con suffisso `-1`, oltre a zeri iniziali e ID più lunghi. Con una coppia di URL e un riscontro autorevole della stessa vacancy si potrà valutare una regola specifica. Un futuro merge che tocchi `collector/**` avvia subito la raccolta di produzione.

Snapshot prima/dopo: 906 → 906 ID, 402 → 402 stage verificati, 37 → 37 candidature dirette, 367 → 367 lead, 0 ID persi. Traffico verso le fonti: 0 GET, 0 byte, 0 secondi.
