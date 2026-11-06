# Stage HR e mappatura dei datori in Fryslân

Fotografia della ricerca:6 novembre 2026. La procedura giornaliera continua ad aggiornare gli annunci e gli esiti nel rapporto pubblico.

La composizione territoriale è completa:18 comuni e 419 località ufficiali, con codici CBS 2026. La mappa delle aziende è in ampliamento:893 datori con presenza provinciale documentata, 146 con prova dimensionale≥50 addetti (145 gruppi). Il gruppo può avere una sede locale più piccola; non si attribuiscono i suoi addetti alla singola filiale. Sono inclusi imprese, enti pubblici, sanità, istruzione e altri datori strutturati.

| Comune | Datori qualificati≥50 | Candidati da qualificare | Sotto soglia documentata |
|---|---:|---:|---:|
| Achtkarspelen | 3 | 17 | 0 |
| Ameland | 14 | 2 | 0 |
| Dantumadiel | 2 | 14 | 0 |
| De Fryske Marren | 9 | 87 | 2 |
| Harlingen | 5 | 14 | 0 |
| Heerenveen | 15 | 87 | 0 |
| Leeuwarden | 35 | 225 | 2 |
| Noardeast-Fryslân | 10 | 35 | 0 |
| Ooststellingwerf | 3 | 15 | 0 |
| Opsterland | 6 | 19 | 0 |
| Schiermonnikoog | 9 | 0 | 0 |
| Smallingerland | 18 | 60 | 0 |
| Súdwest-Fryslân | 23 | 98 | 0 |
| Terschelling | 16 | 3 | 0 |
| Tytsjerksteradiel | 4 | 22 | 0 |
| Vlieland | 12 | 0 | 0 |
| Waadhoeke | 4 | 33 | 1 |
| Weststellingwerf | 3 | 10 | 1 |

Un datore con sedi in più comuni compare in più righe; il totale provinciale elimina le duplicazioni. Le presenze solo comunali, senza città precisa, non vengono usate per dedurre la sede di un'offerta.

## Come vengono raccolti i dati

1. Comuni e località dalle tabelle CBS 2026 [86247NED](https://www.cbs.nl/nl-nl/cijfers/detail/86247NED) e[86312NED](https://www.cbs.nl/nl-nl/cijfers/detail/86312ned).
2. Ricerca dei datori comune per comune: tutti i 901 profili della[directory WRK](https://www.wrk.frl/werken-in-friesland/werkgevers/), associazioni territoriali, siti istituzionali e ricerca specifica sulle isole. L'audit ha letto 1650 pagine ufficiali di 780 datori. La directory contiene anche piccole imprese: il numero dei profili non dimostra il numero delle medio-grandi.
3. Qualificazione con una fonte per organico e sede: sito del datore, relazione annuale, profilo aziendale o fonte istituzionale. Dati storici e organici stagionali rimangono espliciti; dimensione ignota non equivale a dimensione≥50.
4. Individuazione del recruiting ufficiale, compresi sistemi esterni realmente collegati dal datore. Lettura dei feed pubblici, degli elenchi e delle singole schede, con controlli di accesso e limiti per dominio. Gli aggregatori servono alla scoperta.
5. Selezione delle mansioni HR e dello stage; verifica della sede effettiva, del collegamento e della disponibilità quando il sito la espone. Un quartier generale frisone non rende locale uno stage a Baarn, Amsterdam oApeldoorn. PaginaHTTP 200 e pulsante di candidatura non garantiscono che la candidatura sia ancora possibile: Kapenga è stato scartato dopo il messaggio ufficiale di chiusura.
6. Pubblicazione degli annunci distinti e dei requisiti documentati. Le traduzioni e le copie dello stesso identificativo ufficiale vengono unite. I programmi generici HR sono mostrati separatamente.

## Risultato utile agli studenti

Sono confermati 7 annunci HR locali presso datori qualificati. Le schede originali, la sede e la data del controllo sono disponibili nella[ pagina della Frisia](https://people-placement-eu.pages.dev/friesland.html). Philips e Sijperda indicano partenza da febbraio 2027; Kenonz mantiene un riferimento a settembre 2026 e va contattato per confermare la prossima disponibilità. I programmi HR di Frisius MC, Dewulf, Huhtamaki ed Enitor Primo sono opportunità di contatto, non quattro vacancy aggiuntive.

## Autonomia e limiti verificati

La raccolta già attiva su GitHub Actions comprende tutti i datori regionali integrati. Parte ogni giorno alle 06:17 UTC (07:17 invernale / 08:17 estiva nei Paesi Bassi e in Svizzera), salvo ritardi della piattaforma. Non dipende dal computer locale. Sono usati 16 gruppi paralleli e 6 letture per gruppo; i datori frisoni qualificati e gli annunci già trovati hanno precedenza. Il medesimo ciclo aggiorna catalogo, rapporto per azienda e rapporto per comune. Un controllo di salute segnala i problemi nel repository.

La prova locale ha prodotto un esito per tutti gli 893 datori regionali. Fra i 146 qualificati:13 inventari osservati letti, 71 letture parziali, 48 scoperte ancora incomplete e 14 canali bloccati/falliti. Il processo automatico è assegnato ed eseguito per tutti, ma la copertura completa dei siti non è raggiunta. I numeri sono una fotografia di questa passata: il file pubblico riporta gli esiti più recenti.

Per un censimento provinciale esaustivo occorre una base completa dei datori, come il registro provinciale delle sedi/occupazione, e una verifica della dimensione con criteri confrontabili. Il materiale pubblico della[ Provincia](https://www.fryslan.frl/besluitenlijst-gedeputeerde-staten-18-augustus-2026) documenta l'esistenza di quel sistema statistico; il rapporto aggregato non fornisce qui un elenco nominativo completo con il filtro≥50. Non si calcola quindi una percentuale di copertura dell'intera provincia.

## File pubblici

- `data/friesland-geography.json`: tutti i comuni, località e fonti CBS.
- `data/friesland-employers.json`: datori, sedi, gruppi e prove dimensionali.
- `data/friesland-discovery.json`: audit dei 901 profili e delle pagine ufficiali.
- `data/friesland-opportunities.json`: programmi HR, distinti dagli annunci.
- `data/friesland-coverage.json`: esiti aggiornati, conteggi comunali e identificativi degli stage verificati.
- `data/catalog.json`: annunci pubblicati; nessuna descrizione integrale viene esportata.

I dati non contengono credenziali, curriculum o candidature degli studenti.
