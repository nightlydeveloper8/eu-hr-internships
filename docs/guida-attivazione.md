# Guida pratica: GitHub e aggiornamenti giornalieri

Il sito e il programma di raccolta sono già realizzati. Restano da collegare i tuoi account per far partire gli aggiornamenti online, senza tenere acceso il computer. Non è necessario programmare per questi passaggi.

## 1. Collega GitHub in questa app

1. Apri l’integrazione **GitHub** proposta nella chat. Se non la trovi, cerca **GitHub** nella sezione **Plugins / Integrazioni** dell’app; il nome della sezione può variare.
2. Se risulta ancora da installare, scegli **Installa / Aggiungi**. Poi completa il collegamento dell’account, se richiesto.
3. Accedi a GitHub nella sua pagina di accesso e leggi la schermata di autorizzazione. Password, codici di verifica ed eventuali autorizzazioni vanno inseriti direttamente lì, mai in chat.
4. Torna qui e scrivi: **“GitHub collegato. L’account proprietario è …”**, indicando il tuo nome utente GitHub oppure l’organizzazione che deve possedere il progetto.

Se non hai un account, puoi crearlo da [GitHub](https://github.com/signup). Per il progetto iniziale è adatto un repository pubblico con il piano gratuito. Non serve condividere l’indirizzo email in chat.

Se l’app richiede una nuova chat per rendere disponibile l’integrazione, aprila nella stessa cartella del progetto e indica: **“Continua l’attivazione di People Placement dalla cartella eu-hr-internships; il sito è già realizzato e i passaggi sono in docs/guida-attivazione.md.”**

**Dopo il collegamento:** verificherò quali operazioni consente l’integrazione. Potrò quindi aiutarti a creare e caricare il repository, oppure completare con te il solo passaggio che richiede un’azione nel tuo account. Il nome proposto è **eu-hr-internships**. Il codice è già disponibile anche nell’archivio `people-placement-source.zip` nella cartella Internship.

## 2. Attiva e verifica il primo aggiornamento

Questa parte va fatta solo dopo che il repository contiene il progetto, inclusa la cartella `.github/workflows`.

1. Apri il repository su GitHub.
2. Entra nella scheda **Actions**. Se compare una richiesta di attivazione delle automazioni, leggila e abilita i workflow del repository.
3. Seleziona **Daily employer collection**.
4. Premi **Run workflow**, mantenendo il ramo **main**, quindi conferma l’avvio.
5. Attendi il risultato: il segno verde indica che il programma ha superato i controlli, raccolto i dati e salvato l’aggiornamento. Apri l’esecuzione se compare un errore; posso aiutarti a interpretarlo.
6. Controlla che sia comparso un nuovo aggiornamento del catalogo nel repository e che il rapporto **catalog-and-coverage** sia disponibile nell’esecuzione.

La raccolta è programmata ogni giorno alle **06:17 UTC**: **07:17 in Svizzera durante l’ora solare**, **08:17 durante l’ora legale**. GitHub può ritardare l’avvio: non è un servizio con un orario garantito al minuto.

Se il programma non può salvare i dati, può essere necessario consentire ai workflow la scrittura nel repository e la creazione di issue. Non modificare protezioni dell’organizzazione o del ramo senza verificarle: analizzeremo l’errore concreto prima di cambiare impostazioni.

## 3. Collega il sito a Cloudflare Pages Free

Questo è il collegamento che renderà visibili sul sito gli aggiornamenti prodotti da GitHub. La pubblicazione iniziale con Sites e il futuro sito Cloudflare sono due destinazioni separate: il collegamento qui sotto crea la destinazione automatizzata prevista dal progetto.

1. Accedi a [Cloudflare](https://dash.cloudflare.com/) oppure crea un account se non ne hai uno.
2. Cerca **Workers & Pages**, poi **Create application / Create**, quindi **Pages** e l’opzione per importare un repository Git.
3. Collega GitHub seguendo la procedura di Cloudflare. Quando possibile, limita l’accesso al repository **eu-hr-internships**.
4. Seleziona il repository e usa queste impostazioni:

| Campo | Valore |
|---|---|
| Production branch | `main` |
| Framework preset | `None` |
| Build command | `python3 scripts/build.py` |
| Build output directory | `dist` |
| Root directory | lascia vuoto se il repository contiene direttamente il progetto |
| Variabili segrete / API key | nessuna richiesta dal progetto |

5. Avvia il deploy. Al termine, Cloudflare mostrerà un indirizzo che termina con **pages.dev**.
6. Apri quell’indirizzo anche in una finestra privata: il sito deve funzionare senza accesso a GitHub, Codex o ChatGPT.
7. Esegui nuovamente **Daily employer collection** su GitHub e verifica che Cloudflare pubblichi il nuovo aggiornamento. Questa è la prova finale che il collegamento giornaliero funziona.

Non occorre acquistare un dominio. Il progetto è predisposto per i servizi gratuiti e non richiede servizi AI a pagamento; controlla comunque il piano selezionato nella schermata del fornitore.

## 4. Ricevi gli avvisi

Su GitHub abilita le notifiche per le esecuzioni Actions e per le issue del repository. Il progetto prepara un avviso se una fonte non si aggiorna correttamente o se il catalogo supera 36 ore senza un aggiornamento riuscito. Anche il sito mostra un avviso quando i dati sono vecchi.

## Come riconoscere che è tutto pronto

- Il repository contiene i file del progetto e i workflow.
- Un’esecuzione manuale di **Daily employer collection** termina con successo.
- Il sito **pages.dev** si apre senza login.
- Dopo un aggiornamento del catalogo, Cloudflare pubblica la nuova versione.
- Il giorno successivo compare un’esecuzione programmata su GitHub.

Solo dopo queste verifiche gli aggiornamenti giornalieri possono essere considerati attivi. La sola presenza dei file di configurazione non li attiva.

Riferimenti ufficiali: [plugin OpenAI](https://developers.openai.com/plugins/quickstart), [collegamento degli account](https://developers.openai.com/plugins/build/auth), [pubblicazione di siti statici su Cloudflare Pages](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).
