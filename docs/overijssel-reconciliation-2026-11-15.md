# Overijssel — riconciliazione e primo lotto, 15 novembre 2026

Il materiale recuperato dai checkpoint OVI-01–17 riporta 171 schede nominali e
piste nei 25 comuni. Non è un registro deduplicato e non prova copertura completa.
Il dettaglio integrale dei checkpoint successivi a OVI-04 non è stato recuperato;
non viene ricostruito per supposizione. Nessun nuovo source attivato.

## Tre lead con pagina ufficiale letta oggi

| Datore | Comune | Pagina ufficiale | Esito candidature |
|---|---|---|---|
| De Nieuwe Zaak | Zwolle | https://www.denieuwezaak.nl/vacatures/hr-meewerkstage-2 | HR Meewerkstage visibile; CTA JavaScript e form senza submit riconosciuto. Unverified. |
| WEBO | Rijssen-Holten | https://www.webo.nl/vacatures/stage-hrm/ | Stage HRM visibile; istruzioni di contatto email, nessun form riconosciuto; seconda lettura in timeout. Unverified. |
| Groothuis Bouwgroep | Zwartewaterland | https://werkenbijgroothuisbouwgroep.nl/vacature/stageplekhr/ | JobPosting Stageplek HR con sede Genemuiden e datore esplicito; form e CTA esterna presenti. Verifica specifica della candidatura incompleta. |

I tre datori non hanno corrispondenze esatte per nome/alias o dominio nel registro
main usato; questo è un controllo preliminare, non una certificazione dell'assenza
di relazioni societarie. Groothuis Bouwgroep Genemuiden va distinto da Groothuisbouw
Emmeloord. Nessuna dimensione aziendale viene attestata di nuovo da queste letture.
Gli importi e le dimensioni riportati nelle vecchie chat restano prove storiche.

Le pagine non diventano automaticamente annunci verificati. De Nieuwe Zaak ha una
pagina nuova con suffisso `-2`: prima di integrare risolvere l'identità rispetto alla
vecchia pagina e all'eventuale tenant Recruitee, senza generare doppioni. Per WEBO
un recapito di contatto non equivale alle istruzioni di candidatura richieste dalla
policy. Per Groothuis la vera denominazione dello stage è nei dati strutturati,
mentre l'H1 è promozionale; il primo script diagnostico richiedeva un H1 HR e non ha
completato quella verifica. Il markup cita reCAPTCHA: nessun tentativo di superarlo.

## Riusi e lacune

- Elis Hardenberg: `elis-cleanroom` esiste. Verificare entità locale e sede, non
  duplicare il gruppo né attribuire automaticamente le offerte di Bolsward.
- Wagenborg Nedlift Hengelo: `royal-wagenborg` esiste, ma il suo source ID corrente
  è `auto-wagenborg-passagiersdiensten`. Non presumere che copra Nedlift: serve
  un canale ufficiale con identità e perimetro corretti.
- Countus Markelo: riusare `countus-groep`, con prova separata della sede.
- TKH Airport Solutions, Coulisse, Justid, Ambiq, Aqua+ e Bakkerij Nollen restano
  lead da riconciliare; non vengono creati come datori operativi sulla sola memoria.

## Costo e consegna

Tre pagine specifiche con robots e al massimo otto richieste/25 s per fonte:
8 richieste conteggiate, 440.566 byte, 71,138 secondi-fonte cumulati; esecuzione
concorrente, quindi il cumulato non è durata a muro. Zero browser, servizi pagati,
invii di candidature o raccolte complete. Esiti e hash nel JSON associato.

Il ramo di ricerca non modifica companies, sources o catalogo. Nessun nuovo stage
verified o monitoraggio di produzione. La correzione tecnica è separata nella
[PR #38](https://github.com/nightlydeveloper8/eu-hr-internships/pull/38), non integrata.

Prossimo lotto concreto: risolvere canale e identità di De Nieuwe Zaak, istruzioni
ufficiali WEBO e form della stessa vacancy Groothuis; poi integrare questi datori
con adapter esistenti, prove di sede e report municipale parziale. Se un canale
resta bloccato, conservarne il limite e avanzare sul lead successivo. Non riprendere
un altro lotto nominale OVI senza trasformare questo lavoro in monitoraggio.
