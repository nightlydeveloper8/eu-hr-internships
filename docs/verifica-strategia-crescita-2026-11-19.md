# Verifica della strategia di crescita — 19 novembre 2026

Baseline 33 stage con candidatura confermata e 365 annunci attivi dei servizi pubblici. Tutte le prove di questa sessione sono isolate. Il catalogo e le fonti attive su `main` non sono stati aggiornati.

## Adecco, primo lotto NL e Jobandtalent

| Prova | Campione ed esito | Richieste e byte |
| --- | --- | --- |
| Adecco FR / Talentsoft | 6/6 pagine sul tenant esatto con titolo e ID coerenti, 0 moduli candidati abilitati in HTML. Il pilota non ha seguito altri host. Nessuna conclusione sulla disponibilità di un eventuale modulo dinamico. | 14 GET, 1.507.950 B, 18,355 s |
| Stryker, Center Parcs e HB RTS | 2 stage NL per fonte, 0/6 percorsi di candidatura verificati. Le sei pagine hanno restituito la stessa categoria di problema: ingresso di candidatura per la vacancy non stabilito. | 9 GET, 670.259 B, 24,585 s |
| Jobandtalent SE, ricerca ordinaria limitata | Tre query autorizzate, 30 risultati. Posting `31558200` assente o non univoco nel campione, 0 letture ATS. | 4 GET, 324.878 B, 4,760 s |
| Jobandtalent SE, risoluzione esatta | L'endpoint documentato `GET /ad/{id}` ha restituito `31558200` e il controllo ufficiale Teamtailor ha riconfermato inventario, sede a Malmö e form del posting `8503489` il 19/11, dopo la prova del 17/11. La conversione a riga staging è stata bloccata dal controllo della copia pubblica. | 8 GET, 416.358 B, 7,019 s |

Totale dei quattro test: **35 GET**, **2.919.445 B**, zero rendering e zero invii. I due campioni senza moduli verificati non giustificano un rollout in blocco. Le 84 schede Adecco restano una riserva di indizi. Link a prove: [Adecco e NL](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44599543408), [JobTech ricerca](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44600098930), [JobTech ID esatto](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44600388534), [documentazione JobSearch](https://jobsearch.api.jobtechdev.se/), [pilota Jobandtalent del 17/11](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44086636248).

Copia pubblica Jobandtalent: `c8bdac2ae98420d4b1e7`, già presente su `main`. Test offline sulla deduplica corrente con questa copia reale e una riga aziendale sintetica: corrispondenza univoca accorpata alla riga aziendale, link pubblico conservato, secondo passaggio idempotente. Con due possibili controparti le righe sono rimaste separate. La prova conferma il meccanismo di deduplica a valle. Il prossimo intervento è collegarlo al controllo a monte, usando insieme provider ID, ATS ID, località e identità verificata, conservando la provenienza. Il dossier live è positivo su due date, ma nessun nuovo record è stato validato da `finalize()` sul catalogo corrente.

## #63, due snapshot reali e stesso campione

Cache ripristinate per chiave esatta dalle raccolte [18 novembre #44392544160](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44392544160) e [19 novembre #44479557241](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44479557241). La base è il crawler su `3f20f51`, la variante è la #63 a `487d792`. Il replay ha riletto le cache e usato una simulazione deterministica fino a 20 chiamate non servite da cache per fonte. I miss sono pagine vuote simulate. Non sono state richieste pagine degli employer o feed live. Il modello misura il primo tratto della coda, non il traffico HTTP di una raccolta ordinaria.

| Misura, 254 fonti comuni | 18 novembre | 19 novembre |
| --- | ---: | ---: |
| Domanda HTTP simulata prima → dopo | 4.640 → 4.640 | 4.634 → 4.634 |
| Voci da salvare prima → dopo | 136.581 → 111.762 | 136.783 → 112.227 |
| Record HR ritrovati da cache | 3 → 3 | 3 → 3 |
| Record HR da cache persi | 0 | 0 |
| URL puliti rimasti non visitati e persi dal checkpoint | 0 | 0 |

Risultato: **49.375 voci di checkpoint in meno, zero richieste risparmiate sul campione comune**. L'insieme più ampio, con fonti diverse tra i due giorni, ha dato 4.727→4.727 e 4.686→4.695 richieste simulate. Quindi il risparmio HTTP resta da dimostrare. La prima prova si è fermata su un record WEBO con report universal e registro attuale employer-index, senza `start_urls`. Il replay finale l'ha escluso esplicitamente e ha riutilizzato tre shard validi della prima prova. Abbinati 264/270 e 261/262; la tabella usa l'intersezione delle due date. [Replay finale #44600714481](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44600714481).

## Decisione

Prima mossa: riconciliare in staging Jobandtalent con la sua copia pubblica, poi misurare il guadagno di una candidatura diretta in Svezia dopo integrazione e attivazione autorizzate. Per il lotto NL, sostituire il controllo HTML ripetuto con una diagnosi limitata di come il sito pubblica la CTA per la stessa vacancy. Adecco richiede una prova specifica della presenza e accessibilità del modulo prima di estendere il campione. Trattare #63 come riduzione delle voci di coda, con misura separata di HTTP e candidature prima di ogni modifica di frequenza.

Le PR #80 e #81 di Ampelmann restano aperte, con fonte disabilitata nella proposta. I workflow temporanei di questa sessione sono stati rimossi dal ramo di lavoro.
