# Agenzie per il lavoro in Francia

Verifica del 24 novembre 2026 per il lotto **AGENZIE-FR**, in hold. La verifica ha esaminato otto host. Nessuna fonte ha superato tutte le condizioni per entrare nel registro. Nessuna scheda di offerta è stata aperta.

| Host | Risultato |
|---|---|
| www.adecco.com | Robots 200. Le [condizioni francesi](https://www.adecco.com/fr-fr/mentions-legales) vietano espressamente l’estrazione del contenuto. |
| www.randstad.fr | Robots 200. Le [CGU](https://www.randstad.fr/mentions-legales/) vietano l’estrazione di parti sostanziali del sito. Inventario massivo escluso. |
| www.manpower.fr | Robots 200 con crawl delay dichiarato di 10 s. Le [CGU](https://www.manpower.fr/conditions-generales-d-utilisation) vietano l’estrazione anche parziale senza autorizzazione. |
| www.synergie.fr | Robots 200. Le [CGU](https://www.synergie.fr/mentions-legales) riservano dati e contenuti all’uso personale. |
| groupepiment.fr | Robots 200. Le [CGU](https://groupepiment.fr/conditions-generales-utilisation/) limitano l’uso e l’estrazione del database. |
| www.crit-job.com | [CGU](https://www.crit-job.com/conditions-generales-utilisation/) riviste per la sola lettura dell’indice pubblico. La [sitemap delle offerte](https://www.crit-job.com/offres/sitemap.xml) contiene 15.408 URL di vacancy, tutti con un UUID come unico segmento dopo `/offres/`. Il triage per titolo è indeterminato per l’intero inventario. |
| www.partnaire.fr | [Avviso legale](https://www.partnaire.fr/mentions-legales/) rivisto. L’[indice dichiarato](https://www.partnaire.fr/sitemap_index.xml) espone quattro sottoindici editoriali, nessuno dedicato alle vacancy. |
| www.expectra.fr | Robots in redirect 301 verso Randstad Professional. Accesso su Expectra indeterminato. |

I GET hanno usato lo user agent People Placement e almeno 2 s di pausa per host. Il preflight è costato 12 GET e 3.767.525 byte, con 6,008 s HTTP per le quattro richieste dopo robots. Le consultazioni legali esterne sono fuori telemetria. Il costo aggiuntivo di raccolta è 0 richieste e 0 s per ciascuno dei 16 shard.

## Simulazione e recall

Il finalizzatore ha elaborato la baseline catalogo del 24 novembre alle 07:56 UTC con il lotto vuoto. Gli ID sono 944 → 944, con zero persi. Gli stage HR francesi con verifica entro 48 ore alla data della baseline sono 44 → 44. Il recall aperto sulle 30 righe FR è 0/30 → 0/30 tramite URL canonico o ID di catalogo già dimostrato nel [ledger #138](https://github.com/nightlydeveloper8/eu-hr-internships/blob/cac8572b7cc32557a2a2b18c1feeeca633e4f2c9/docs/recall-fonti-ad-alta-densita-2026-11.csv). Sono già previste le regole FR per convention de stage e per l’esclusione di alternance e apprentissage. Il lotto vuoto non ha generato nuovi dettagli su cui applicarle.
