# Stage HR con metodo Personio distinto e ammissione dei neolaureati

Proposta del 22 novembre 2026 su `main` `f606443`. Le PR #112 e #113 restano indipendenti. Nove datori e nove fonti predisposti con `enabled: false` sulla fonte e hold su datore e fonte. Il provisioning mantiene 1.923 collector attivi. Nessuna variazione del catalogo pubblicato.

## Verifica in staging

Il metodo `personio-feed-same-id-static-form` si applica solo ai tenant Personio configurati esplicitamente. Richiede il posting nel feed XML ufficiale e nello stesso ciclo, una pagina vacancy col titolo corrispondente, un link osservato allo stesso ID e un modulo con nome, cognome, email e upload CV visibili e controllo di invio presente. L'ID di URL, canonical e dati strutturati deve essere coerente quando disponibile. Il submit inizialmente disabilitato è accettato dalla decisione del maintainer. Il metodo compare nella prova di candidatura e nel motivo di verifica. Togliendo il metodo dalla configurazione della fonte, la successiva finalizzazione ritira le relative prove pregresse e conserva gli ID.

Si tratta di GET HTML statiche con controllo robots su host esatti. Nessun JavaScript remoto, compilazione, POST o invio. Il metodo non dimostra che il backend accetti una candidatura. Un form disabilitato dal datore, una copia server-rendered residua o una validazione rotta possono superare la prova. Il portale espone il tipo di controllo nei dettagli e continua ad applicare la finestra di 48 ore.

| Fonte | Paese | Posting | GET | Byte | Secondi | Esito |
| --- | --- | --- | ---: | ---: | ---: | --- |
| Mercedes-Benz.io | PT | 2833968 | 4 | 721.076 | 1,699 | Recruitee v2, aperto anche ai neolaureati |
| ten23 health | CH | 2139342 | 4 | 248.928 | 1,734 | Personio, aperto anche ai neolaureati |
| Watson Farley & Williams LLP | DE | 2634127 | 4 | 223.608 | 1,691 | Personio, preserva l’ID EURES |
| Studyflix | DE | 1119140 | 4 | 272.895 | 1,759 | Personio, un posting contato |
| Bloomwell Group | DE | 2888191 | 4 | 288.595 | 1,766 | Personio |
| Vamo | DE | 2471392 | 4 | 330.055 | 2,287 | Personio |
| Reformer Club | DE | 2669913 | 4 | 328.534 | 2,244 | Personio, aperto anche a chi ha concluso gli studi |
| Wilken Software Group | DE | 2840229 | 4 | 448.002 | 3,270 | Personio, sede esatta `DE_Ulm` ricondotta a Ulm |
| Avantgarde | DE | 2888187 | 4 | 1.338.691 | 4,026 | Personio, Talent & Culture con funzioni HR documentate |
| Watson Farley & Williams, scheda EURES | DE | MTAwMDEtMTAwMzk2MTczMy1TIDE | 2 | 9.944 | 0,258 | Confronto di identità |

Totale dei cicli conclusivi **38 GET / 4.210.328 byte / 20,734 secondi-fonte**, inclusi robots e confronto EURES. I tentativi diagnostici precedenti, inclusi due errori TLS locali su EURES, sono separati. L'endpoint EURES è stato letto con verifica TLS di sistema. Stesso datore, stesso titolo base, stessa sede a Francoforte, stessa durata minima di sei mesi, stessi requisiti linguistici e corrispondenza delle attività. La relazione esatta tra URL EURES e posting Personio è limitata a questa vacancy. L’ID di catalogo `2500a45f998ebbdf4d43` rimane quello storico. Il test copre anche le due osservazioni nello stesso ciclo, con EURES raccolto dopo Personio.

Studyflix pubblica due ID. L'offerta `1119140` enfatizza il recruiting e `1119149` il supporto HR. Sede, durata, condizioni, aree di studio e parte delle attività si sovrappongono. Poiché manca prova di due posti distinti, `1119149` resta escluso dal conteggio e dal feed elaborato di questa fonte. Il feed filtrato non consente chiusure per assenza.

## Effetto misurato

Finalizzazione su copia del catalogo di `f606443`, usando le osservazioni di staging nello stesso riferimento temporale. ID **913 → 921**, **zero persi**. Stage attuali verificati **407 → 415**, candidature dirette **36 → 45**, lead visibili **365 → 365**. Una scheda EURES passa a candidatura diretta mantenendo il suo ID.

| Paese | Stage verificati | Candidature dirette | Lead |
| --- | ---: | ---: | ---: |
| CH | 32 → 33 | 0 → 1 | 4 → 4 |
| DE | 32 → 38 | 4 → 11 | 36 → 36 |
| PT | 1 → 2 | 1 → 2 | 1 → 1 |

Il badge inglese «Also open to recent graduates» è visibile sulle tre schede interessate. Tutte e tre esprimono un'alternativa per studenti attualmente iscritti. I graduate programme e i traineeship per neolaureati rimangono fuori perimetro.

## Accesso e rollout

Controllati robots a runtime su tutti i tenant. Le richieste usano feed e pagine candidature pubblicati dagli stessi tenant. Le condizioni consultate disciplinano principalmente il rapporto fra provider e clienti. La documentazione spiega la pubblicazione dei feed. Non è stata stabilita una licenza generale di riuso da parte di terzi. [Condizioni Personio](https://www.personio.com/terms/) · [Feed Personio](https://support.personio.de/hc/en-us/articles/207576365-Integrate-jobs-from-Personio-into-your-website-via-XML) · [Condizioni Recruitee](https://recruitee.com/terms) · [Feed Recruitee](https://docs.recruitee.com/docs/feed)

Per un eventuale rollout servono verifica fresca, riesame delle condizioni applicabili dei singoli datori e approvazione separata. La PR #113 aggiunge altre fonti disabilitate negli stessi registri, quindi dopo l'integrazione di una delle due PR va riallineata l'altra prima del merge.
