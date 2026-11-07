# Issue #10 — accuratezza e diagnosi del catalogo

Base: `main` `3ec0afd`; snapshot catalogo 7 novembre 2026, 07:14:56 UTC.
Intervento isolato sul ramo `fix/issue-10-catalog-accuracy`. PR Utrecht #7 non
integrata; checkout con modifiche Flevoland preservato. Nessun lavoro su #8/#9.

## Attribuzione Ennatuurlijk: causa riprodotta

`daily.provision()` aveva configurato Tilburg dalla homepage, perché il registro
non aveva una pagina careers. `Crawler.visit()` promuoveva host di link careers e
ATS osservati nella propria allowlist; non verificava che appartenessero al datore.
`Crawler.feed()` riconosceva anche un singolo link `/o/…` Recruitee come accesso
all'intero tenant e passava il nome della fonte al reader.
`recruitee_records()` assegnava `source['employer']` a tutte le offerte.
La verifica policy v2 confermava la vacancy e il modulo, non l'ownership del tenant.

Riproduzione offline con il collector originale `3ec0afd`, una fixture di link
esterno osservato e il feed ufficiale salvato: offerta `971718` →
`employer=Tilburg University`, `source_id=auto-tilburg-university`, ID stabile
`70d297b765fc2696c836`. La causa del nome e dell'ID è quindi riprodotta esattamente.
I log storici non conservano parent URL/frontiera: non è dimostrabile quale singola
pagina intermedia abbia portato al tenant. La pagina studenti Tilburg elenca
esplicitamente portali terzi, inclusi Greenjobs e NationaleVacaturebank:
[Vacatures studenti](https://www.tilburguniversity.edu/nl/studenten/loopbaan/je-loopbaanpad/vacatures).

La [vacancy primaria Ennatuurlijk](https://ennatuurlijk.nl/werken-bij/hr-stagiaire-gezocht)
identifica il datore e Eindhoven; il pulsante di candidatura collega direttamente
`ennatuurlijkbv.recruitee.com/o/hr-stagiaire-gezocht/c/new`. Il feed pubblico dello
stesso tenant conferma ID `971718`, titolo e vacancy URL. La verifica mirata con
`verify_vacancy()` ha confermato `same-vacancy-applicant-form` senza cambiare policy.
Provenienza, hash delle prove e righe di log: [evidence](issue-10-evidence.json).

## Correzioni

- Fonte Ennatuurlijk già esistente collegata al feed Recruitee con prova ufficiale;
  registro del datore aggiornato senza creare aziende o fonti duplicate.
- Revisione individuale per URL in `data/ownership-reviews.json`, applicata anche
  al merge quotidiano prima della deduplicazione. ID, URL, cronologia e prova di
  candidatura preservati; nessun trasferimento in blocco.
- Un link ATS esterno non autorizza più il feed con il nome del datore iniziale.
  Una pagina esterna richiede `hiringOrganization` corrispondente o un host già
  revisionato. Un'organizzazione diversa non viene riassegnata automaticamente.
- Tilburg resta confinata agli host revisionati; Tilburg e Randstad richiedono
  identità esplicita del datore anche nelle pagine sul proprio dominio. Le vecchie
  righe/cache prive di quella prova non possono generare nuove attribuzioni.
  Gli annunci storici non vengono cancellati o promossi.
- Frontiera e cache crawler legacy invalidate solo per Tilburg; le cache delle
  altre fonti restano utilizzabili. La verifica dell'ownership precede anche
  l'utilizzo di record restituiti da cache/feed nella pipeline.
- KPI: sottoinsiemi verificati internship/working-student/traineeship espliciti;
  contatori chiusi e archivio storico già corretti. Inventari completi entro 48 ore
  mostrati separatamente dalla raccolta configurata nella pagina datori. Conteggi
  di copertura escludono inventari esplicitamente incompleti e date future.
  Annuncio in inglese, inglese documentato e inglese sufficiente restano distinti;
  requisiti ignoti non escludono il candidato.

## Diagnosi dei 89 timeout

Log: [raccolta 42349661189](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/42349661189),
job `128334947371` (shard 2) e `128334947429` (shard 8). Gli orari di inizio/fine
confermano i tempi dei report; il workflow globale riuscito non significa che tutte
le fonti siano complete. [Conteggi e shortlist](issue-10-diagnostics.json).

| Evidenza | Tilburg | Randstad Italia |
|---|---:|---:|
| Record catalogo / timeout | 109 / 76 | 25 / 13 |
| Durata / budget secondi | 121,00 / 120 | 120,61 / 120 |
| Richieste / limite | 78 / 110 | 40 / 110 |
| Pagine lette / snapshot renderizzati | 41 / 0 | 15 / 12 |
| URL lavoro scoperti / URL pendenti | 3.744 / 5.328 | 16 / 2.334 |
| Record ispezionati / cache hit | 161 / 107 | 25 / 25 |

**Limite temporale:** il client ha un'unica deadline per raccolta, enrichment e
verifica. Il crawler prova a fermarsi all'82%, ma la lettura/renderizzazione in
corso può consumare il residuo. Le verifiche successive registrano l'esaurimento
dello stesso budget: non sono 89 timeout di rete indipendenti. Nessun limite di
richieste raggiunto nelle due fonti; il singolo caso DE di request budget è distinto.

**Raccolta ampia e confine fonte:** Tilburg contiene 108 record di
NationaleVacaturebank e uno Ennatuurlijk, con 30 host nel report; non è un
inventario dell'università. Questo spiega la contaminazione e il volume eccessivo.
Randstad resta sul suo dominio per i 25 record, ma parte da careers e homepage,
seguendo ricerca lavori e navigazione ampia; host proprio non dimostra che una
vacancy sia un'assunzione interna anziché per un cliente.

**Paginazione:** la navigazione universale segue link next/rel-next e load-more
con limiti; non c'è evidenza di uno specifico errore API di pagina. La frontiera
salvata è limitata a 2.000 voci, meno delle due code osservate: persistenza troncata
confermata dal codice, rischio di riscoperta e incompletezza. Il report non prova
quali annunci non letti sarebbero validi. Nessun inventario dichiarato completo;
nessuna chiusura per assenza consentita.

**Rendering/verifica:** Tilburg ha zero pagine renderizzate: il browser non è la
causa dei suoi 76 timeout. Randstad ha 12 snapshot e circa 19,3 MB letti: rendering
può contribuire al costo, ma mancano tempi per singola operazione per quantificarlo.
Gli altri 12 record Randstad non stabiliscono una candidatura specifica; non vanno
promossi con un link generico. I 31 analoghi Tilburg restano separati dai 76 timeout
(oltre a un ulteriore mismatch di identità). Gli errori pagina Tilburg sono troncati
a 30; le ragioni complete dei record sono conteggiate dal catalogo.

## Validazione e limiti

182 test Python iniziali dopo la prima correzione; suite finale **184 test Python**,
**20 test frontend**, **64 casi classificazione**, validazione catalogo/registro,
generazione report copertura e build statica superati. Test inclusi per referral,
ATS non revisionati, hiring organization diversa/mancante, cache legacy, merge
quotidiano con stesso ID, tenant autorizzati, KPI, lingue e freshness.
Tutte le 309 opportunità, tutti gli ID e link preservati; solo il record Ennatuurlijk
modificato. Province invariate: Fryslân 1, Groningen 2, Drenthe 2 stage verificati
nello snapshot. [Risultati](issue-10-validation.json).

Snapshot UE invariato nei totali: 15 internship e 3 working-student verificate,
290 non verificate, 1 chiusa. 1.816 datori configurati; 102 relazioni datore–paese
con inventario completo/recente su target 2.700. Otto opportunità verificate
hanno inglese documentato; zero documentano che il solo inglese basti.

Riproduzione diagnostico senza rete:
`python3 scripts/diagnose_issue10.py --ref 3ec0afd --output /tmp/issue10.json`.
Il commit base deve essere presente nella copia Git. Le prove integrali e i log
completi restano localmente in `.staging/issue-10/`, esclusi dal sito e dalla PR;
i JSON in docs espongono solo metadati, conteggi, hash e brevi estratti.

Seguiti: revisione individuale delle altre attribuzioni Tilburg; identificazione
revisionata del canale di assunzioni interne Tilburg; delimitazione Randstad e
verifica delle sue candidature; eventuale revisione di paginazione/frontiera con
telemetria mirata. La shortlist di cinque record dei 97 senza candidatura è solo
triage offline ordinato per fonte strutturata e data; nessuna pagina aggiuntiva
aperta né promessa di conversione. I nuovi host careers/ATS richiedono ora una
prova di ownership prima di ereditare il nome: possibili nuove scoperte restano
incomplete fino alla revisione, mentre gli annunci storici rimangono conservati.

Nessuna raccolta massiva, dipendenza, API AI, aumento di timeout/risorse o bypass.
Nessun merge/deployment e nessuna chiusura automatica dell'Issue #10. La futura
raccolta remota resta da osservare dopo un eventuale merge autorizzato; il percorso
di aggiornamento è coperto da regressione offline nella presente PR.
