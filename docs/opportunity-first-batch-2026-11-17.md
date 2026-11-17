# Lotto di intervento: prove di candidatura degli internship HR (17 novembre 2026)

**Natura:** priorità **offline e documentata**, **non** nuove opportunità verificate né piano di query illimitate. Dati dal catalogo `main ab51981` e dal report corrente `data/coverage.json` del 17/11. La nuova procedura `scripts/opportunity_quality.py` genera una coda analoga a ogni ciclo dopo un eventuale merge autorizzato, mantenendo separati internship, working student e traineeship.

## Baseline verificata

- 363 record catalogo, **28 internship HR policy v2 verified**, 1 working student verified.
- **307 unverified**, di cui **266 internship**, **31 working student** e **10 traineeship**. Sono identificativi non verificati, non annunci candidabili.
- **51 gruppi fonte** con annunci non verificati su host dichiarati e non evidentemente bloccati dal motivo salvato; **48** contengono almeno un internship non verificato.
- 98 record in quarantena ownership storica non vanno promossi senza prova della proprietà; 77 con entry specifica mancante e 35 con ID candidatura non associato sono *cause* esistenti, non stage recuperabili certi. Motivi storici possono essere datati e vanno riesaminati senza dichiarare false prove live.

## Prima coda di otto fonti — nessuna fonte viene qui abilitata o ampliata

| Fonte esistente | Internship non verificati in catalogo | Con problema di candidatura specifica | Ultime richieste fonte osservate | Gate di intervento |
|---|---:|---:|---:|---|
| `auto-randstad-italia-spa` | 22 | 11 | 56 | Verificare ownership e pattern condiviso di apply, senza attribuire offerte di altri datori |
| `auto-l-oreal` | 11 | 10 | 77 | Trovare collegamento identità annuncio→CTA; non inferire dal percorso marketing |
| `auto-center-parcs` | 3 | 3 | 17 | NL; verificare inventario attuale e stesso posting senza ripetere tentativi oltre budget |
| `auto-hb-rts` | 2 | 2 | 9 | NL; valutare una sola prova form su host datore già approvato |
| `auto-kenonz` | 2 | 2 | 16 | NL; prima verificare anche classificazione stage del ruolo dal titolo generico |
| `auto-axs-logistiek` | 3 | 3 | 65 | NL; indagare l'ID sul form ufficiale, non accettare l'apply generico |
| `auto-salomon` | 3 | 3 | 72 | FR; provare modulo corrispondente con limiti e hosts già ammessi |
| `employer-bas-group` | 1 | 1 | 8 | NL; già una vacancy specifica, ma senza form abilitato verificato |

**Non sono 47 candidature disponibili.** Sono **47 record internship non verificati** nelle otto fonti, da filtrare e deduplicare prima di qualsiasi promozione. L'obiettivo del lotto non è visitare tutti i 47 URL: identificare una o due **cause comuni**, provare su un campione ridotto, introdurre un solo fix riutilizzabile e confrontare il catalogo prima/dopo.

### Sospesi o in revisione di proprietà

- **Danone:** 12 internship non verificati, 11 problemi di candidatura specifica; nuova prova solo se l'accesso ordinario torna leggibile. Nel [pilota #44108780920](https://github.com/nightlydeveloper8/eu-hr-internships/actions/runs/44108780920) la pagina NL selezionata ha dato `HTTPError`; il codice preciso non è stato registrato, non inventare un 403/429.
- **Tyche Bank:** pagina stage HR sul datore letta, ma form/ID specifico non dimostrato nello stesso pilota. Nessuna promozione.
- **Achmea:** candidati con modulo dinamico/account/CAPTCHA precedentemente non verificati. Non aggirare.
- **TNG/Personio:** form con submit inizialmente disabilitato; non confondere campi visibili con candidatura disponibile.
- **Econvert Water & Energy B.V.:** nel catalogo alcuni internship su paesi/aziende differenti; prima di qualunque review candidatura è necessaria verifica ownership e attribuzione corretta. Anche un URL ufficiale non sana l'identità del datore errato.
- **SmartRecruiters/Ashby vietati o robots 401:** non avanzare usando API o browser per aggirare i blocchi.

## Contratto per un miglioramento reale

1. Selezionare il pattern migliore dalla prima coda senza crawl completo o lavoro ripetuto sulle singole vacancy. Con **BudgetClient**, robots e allowlist invariati, verificare un solo campione sul medesimo ATS prima di codificare il fix.
2. Il test automatico deve respingere titolo, requisition o datore diverso, redirect a portali generici, domanda chiusa e submit disabilitato. Nessuna conferma tramite solo HTTP 200, JSON-LD o presenza di una CTA.
3. **Metriche di accettazione:** differenza di stage HR **distinti e verified in produzione**, paese reale, ID mantenuti e nessuna perdita/chiusura falsa; richieste/byte/secondi e rendimenti per fonte nei successivi cicli ordinari. Il test offline e l'anteprima non sono produzione.
4. Non attivare nuove fonti o cron e non effettuare merge come effetto di questa coda. Se non c'è un incremento dimostrabile a costo sostenibile, passare al prossimo pattern/fonte anziché visitare ancora gli stessi link.

**Misura di questo intervento:** la sola generazione della classifica legge file locali, **0 richieste HTTP e 0 browser**, nessun catalogo modificato. La prova di applicazione Danone/Tyche già effettuata nell'incarico ha consumato **4 GET/60.427 B** e verificato **0 nuovi stage**.
