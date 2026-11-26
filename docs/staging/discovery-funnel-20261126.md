# Imbuto del primo dispatch di discovery

[Run 45787800451, tentativo 1](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/45787800451/attempts/1) e artefatto `discovery-observations`. I 203 ID sono disaggregati usando il CSV di riesame. Ogni riga indica il primo arresto, salvo il dettaglio delle condizioni di replay.

| Primo arresto | Host | Fonti migrazione |
| --- | ---: | ---: |
| Robots non letto o percorso negato | 394 | 1 |
| Sitemap assente o non leggibile | 251 | 1 |
| Zero slug candidati nella sitemap letta | 499 | 81 |
| Termini, piattaforma o configurazione da rivedere | 770 | 113 |
| Host già attivo, coperto o in hold | 105 | 6 |
| Esclusione registrata o host non valido | 17 | 0 |
| Replay fallito | 20 | 1 |
| Replay superato | 1 | 0 |
| **Totale** | **2.057** | **203** |

Robots: 322 non letti, 72 senza sitemap consentita. Il controllo è corretto. I redirect e gli errori di accesso restano inconclusivi. Le 251 sitemap non acquisite includono errori HTTP, redirect, parsing e limiti di trasporto. Il difetto è nel tempo a muro del percorso seriale e nell'etichetta del redirect dopo il secondo GET, ora trattenuto come redirect.

Lo zero da slug è corretto per la sola sitemap letta. Il conteggio non prova che il sito o il mercato siano privi di stage. Gli indici con foglie non lette sono parziali. Il blocco di revisione è corretto quando mancano termini, configurazione o esito su un altro sito. L'artefatto storico registra un motivo misto per 770 host, 759 senza piattaforma identificata con precisione e quattro con indizio Phenom o Radancy senza prova positiva distinta nella baseline. Non si può isolare il numero effettivo fermato soltanto dal requisito di piattaforma. Il nuovo report distingue le cause quando i segnali lo consentono. Mantenere la copertura esistente per 105 host evita doppioni o riattivazioni in hold.

Dei 21 replay, zero hanno perso ID, zero hanno registrato titoli esclusi, 12 hanno fallito il controllo aggregato di budget o lettura e tutti e 20 i respinti erano sotto current listing. Otto sono stati respinti solo per prova insufficiente. L'unica migrazione simulata non aveva una scheda current listing. Girteka ha superato il replay con 3 GET e 109.715 byte. Il push è stato respinto e il retry ha raggiunto il timeout. Il primo tentativo registra 3.686 GET di preflight e 147 GET di replay, 12.369.940 byte di replay. I byte di preflight non sono nell'artefatto storico.
