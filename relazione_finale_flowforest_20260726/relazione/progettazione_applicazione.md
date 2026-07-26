# 6. Progettazione dell'applicazione

## 6.1 Architettura dell'applicazione e scelte tecnologiche

Il gestionale FlowForest è realizzato come applicazione web organizzata su tre livelli:

1. **Livello di presentazione — Streamlit:** genera le schermate, i form e le tabelle e conserva lo stato della sessione dell'utente.
2. **Livello applicativo — Python:** controlla i dati inseriti, seleziona le funzioni disponibili in base al profilo e coordina le operazioni che richiedono più istruzioni.
3. **Livello dei dati — PostgreSQL:** conserva le relazioni definite nello schema logico ed è raggiunto mediante il driver `psycopg2`.

Il database è ospitato su Neon e richiede una connessione cifrata mediante `sslmode=require`; l'interfaccia è distribuita mediante Streamlit Community Cloud a partire dal repository GitHub. Le credenziali tecniche di PostgreSQL vengono caricate da variabili d'ambiente e non sono incluse nel codice sorgente.

Le interrogazioni utilizzano parametri separati dal testo SQL, riducendo il rischio di SQL injection. Le operazioni semplici sono eseguite dalla funzione `run_query`, mentre `run_transaction` raggruppa più scritture nella stessa transazione ed effettua `ROLLBACK` in caso di errore. Questa seconda modalità è impiegata, per esempio, per registrare insieme un Ordine e le relative righe.

## 6.2 Autenticazione e profili di accesso

Il login utilizza l'indirizzo email e la password memorizzati in `PERSONA`. L'utente seleziona nel form iniziale il profilo **Cliente** oppure **Staff**; la scelta determina la verifica applicata:

- il **Cliente** viene verificato mediante una `JOIN` tra `PERSONA` e `PERSONA_CLIENTE`;
- lo **Staff** viene verificato mediante una `JOIN` tra `PERSONA` e `RISORSA_UMANA`.

La sessione conserva ruolo applicativo, email e codice fiscale. Il cliente viene indirizzato esclusivamente all'Area Partecipanti, mentre ogni Risorsa Umana autenticata riceve il ruolo applicativo `admin` e accede all'Area Gestione Bosco. I sottotipi `FORMATORE`, `OPERAIO` e `AMMINISTRATIVO` descrivono le competenze lavorative, ma nel prototipo non determinano permessi differenti.

Le operazioni sul database vengono eseguite mediante un'unica utenza tecnica PostgreSQL; l'autorizzazione dei profili è pertanto applicativa e non corrisponde a ruoli distinti del DBMS.

Nel prototipo didattico la password è confrontata direttamente con il valore memorizzato in `PERSONA`. In un rilascio reale dovrà essere conservato esclusivamente un hash prodotto da un algoritmo specifico per password; dovranno inoltre essere introdotte procedure di impostazione, cambio e recupero delle credenziali.

## 6.3 Interfaccia utente e funzionalità

L'interfaccia è organizzata nelle seguenti aree. La copertura indicata descrive il comportamento verificato dopo il riallineamento tecnico elencato nella Sezione 6.4.

### Area partecipanti

L'Area Partecipanti comprende tre schede:

1. **Ricerca Biglietto e Materiali:** mostra i Biglietti associati alla Persona autenticata, permette la ricerca tramite codice seriale e visualizza quantità e Materiali richiesti dal Laboratorio. Copre OP.P2 e OP.P4.
2. **Eventi disponibili:** mostra i Laboratori futuri in ordine cronologico, con date, costo e Aree di svolgimento. Copre OP.P3.
3. **Compila Feedback:** verifica l'esistenza del Biglietto e registra voto, commento e data di compilazione. Copre OP.P1.

### Area gestione bosco

L'Area Gestione Bosco comprende sette schede:

1. **Registrazione utenti:** registra Clienti privati e Aziende Partner. Costituisce una copertura parziale di OP.G1.
2. **Gestione materiali e ordini:** inserisce o elimina Materiali, distingue Attrezzature e Consumabili, registra un Ordine con una o più righe e confronta quantità ordinate e disponibilità corrente. Copre OP.G2, OP.G3 e OP.G10.
3. **Laboratori ed eventi:** crea un Evento e il sottotipo `LABORATORIO` oppure `EVENTO_PARTNER`, associandolo alle Aree e, nel caso del Laboratorio, ai Moduli. Copre OP.G4.
4. **Analisi e report:** calcola la spesa media annua dei clienti privati, ordina i Partner per numero di Eventi e calcola il fatturato dei Laboratori. Copre OP.G7, OP.G8 e OP.G9.
5. **Modifica Laboratori:** aggiorna titolo, descrizione, protocollo operativo e Moduli associati. Copre OP.G5.
6. **Recensioni e Feedback:** mostra le valutazioni insieme al partecipante e al Laboratorio, calcolando anche voto medio e numero complessivo dei Feedback.
7. **Registri e anagrafiche:** permette di consultare personale, Aree, Strutture, Moduli, Persone, Clienti, Partner, Fornitori, Ordini e storico degli Eventi. Copre OP.G6.

## 6.4 Copertura delle operazioni e limiti del prototipo

La copertura delle operazioni non è completa:

- **OP.P5 — Idoneità all'invito gratuito:** la query di verifica delle tre partecipazioni concluse è documentata nel Capitolo 5, ma non è esposta nell'interfaccia. Il ciclo di vita degli inviti non rientra nel prototipo.
- **OP.G1 — Registrazione delle anagrafiche:** l'interfaccia registra Clienti privati e Aziende Partner, ma non offre form dedicati ad Aziende Clienti e Risorse Umane.
- **Assegnazione del personale ai Laboratori:** non è stata introdotta un'associazione tra `RISORSA_UMANA` ed `EVENTO`, perché non interessa stabilire quale dipendente lavori in ogni specifico Laboratorio.

Lo schema relazionale finale supporta più Aree per Evento e più Moduli per Laboratorio tramite `EVENTO_AREA` e `LABORATORIO_MODULO`. L'interfaccia utilizza quindi selezioni multiple e inserisce una tupla per ogni associazione, senza memorizzare `nome_area` in `EVENTO` o `id_modulo` in `LABORATORIO`.

### Allineamento tecnico con lo schema finale

Il file `app.py` è stato riallineato allo schema relazionale finale:

- le Aree sono selezionate tramite `EVENTO_AREA`;
- il costo del Biglietto è memorizzato in `LABORATORIO`;
- i Moduli sono selezionati tramite `LABORATORIO_MODULO`;
- la registrazione dei Clienti valorizza `CLIENTE_FLOWFOREST.data_registrazione` e `PERSONA.password`;
- i report sui Partner contano gli Eventi organizzati e non utilizzano fee o Biglietti degli Eventi Partner;
- il registro del personale utilizza `RISORSA_UMANA.mansione`, `livello_salariale` e la presenza nei relativi sottotipi.

Il codice supera il controllo sintattico Python. Il collaudo integrato sul database PostgreSQL migrato allo schema finale ha verificato la connessione cifrata, l'autenticazione dei due profili, le interrogazioni delle schermate amministrative e partecipante, la registrazione di un Cliente e la creazione e modifica di un Laboratorio con più Aree e più Moduli. Lo script DDL esportato dal database è stato inoltre ricostruito in uno schema temporaneo, verificando la creazione delle 26 relazioni e dei relativi vincoli senza modificare i dati operativi.

## 6.5 Screenshot dell'interfaccia utente

La schermata iniziale consente di selezionare il profilo e di autenticarsi mediante email e password.

![Schermata di autenticazione di FlowForest](immagini/interfaccia/login.png)

*Figura 6.1 - Schermata di autenticazione con scelta del profilo.*

L'area amministrativa permette di registrare un Cliente privato valorizzando i dati anagrafici e le credenziali applicative.

![Registrazione di un cliente privato](immagini/interfaccia/registra_utente.png)

*Figura 6.2 - Form amministrativo per la registrazione di un Cliente privato.*

La gestione degli approvvigionamenti registra l'Ordine e le quantità dei singoli Consumabili, rendendo consultabile il confronto con la disponibilità di magazzino.

![Registrazione di un ordine e quantità dei consumabili](immagini/interfaccia/registro_ordine.png)

*Figura 6.3 - Registrazione di un Ordine e consultazione delle quantità ordinate.*

Il profilo partecipante visualizza esclusivamente i propri Biglietti e, per ciascun Laboratorio, i Materiali richiesti con le relative quantità.

![Area partecipante con biglietti e materiali](immagini/interfaccia/portale_cliente.png)

*Figura 6.4 - Area Partecipanti con Biglietti e Materiali richiesti.*

Infine, la sezione dedicata ai Feedback riassume le valutazioni ricevute e consente allo staff di consultare voto, commento, data, Laboratorio e partecipante.

![Consultazione dei feedback](immagini/interfaccia/feedback.png)

*Figura 6.5 - Consultazione amministrativa dei Feedback ricevuti.*
