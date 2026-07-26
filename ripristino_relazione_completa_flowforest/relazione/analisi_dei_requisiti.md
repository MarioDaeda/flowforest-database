# 1. Analisi dei requisiti

## 1.1 Intervista

Il seguente testo costituisce la rielaborazione strutturata delle informazioni raccolte durante l'intervista con i referenti di FlowForest.

Si vuole realizzare una base di dati per **FlowForest**, un'azienda che gestisce un bosco e lo utilizza per organizzare attività formative incentrate sullo sviluppo dell'intelligenza pratica e per concedere i propri spazi ad aziende partner che organizzano eventi autonomi.

Il bosco è suddiviso in aree, ciascuna caratterizzata da nome, capienza e scopo. Un evento può utilizzare una o più aree e una stessa area può ospitare eventi differenti nel tempo. Ogni area può inoltre contenere strutture fisiche, come capanne o pergolati, delle quali si registrano un codice identificativo e la funzione d'uso.

Le attività organizzate e vendute direttamente da FlowForest sono chiamate **Laboratori**. Ogni laboratorio possiede un titolo, una descrizione, un protocollo operativo e un costo del biglietto; è inoltre composto da uno o più moduli didattici, dei quali vengono conservati nome e testo. Per partecipare a un laboratorio viene emesso un biglietto nominale, sul quale sono registrati il codice seriale, la data di emissione, il prezzo pagato e le eventuali richieste relative alle allergie. Il biglietto è sempre intestato alla persona che partecipa e può essere fatturato a un'azienda cliente.

Al termine del laboratorio, il titolare del biglietto può compilare un feedback composto da voto, commento e data di compilazione. Ogni biglietto può generare al massimo un feedback, in modo che la valutazione rimanga riferita a una specifica partecipazione.

Gli eventi organizzati da aziende esterne sono denominati **Eventi Partner**. Di ogni azienda partner vengono registrati partita IVA, nome, specializzazione ed email. FlowForest conserva le informazioni organizzative dell'evento e dell'azienda che lo organizza, ma non gestisce i biglietti dei partecipanti né una percentuale sui ricavi dell'evento partner.

FlowForest gestisce anche l'inventario dei materiali necessari alle attività. Di ogni materiale vengono registrati codice, nome, quantità disponibile e soglia minima di riordino. I materiali si dividono in attrezzature riutilizzabili, caratterizzate da stato di usura e data dell'ultimo utilizzo, e consumabili, per i quali si conservano data di scadenza ed eventuali allergeni. Per ogni evento vengono indicati i materiali impiegati e le relative quantità.

I consumabili vengono acquistati mediante ordini indirizzati a fornitori esterni. Ogni ordine registra data, importo totale e stato di consegna e comprende uno o più consumabili, indicando per ciascuno la quantità ordinata.

Il personale viene rappresentato tramite la **Risorsa Umana**, della quale vengono registrati identificativo del dipendente, IBAN, data di assunzione, mansione e livello salariale. Ogni risorsa ricopre almeno uno dei ruoli di formatore, operaio o amministrativo e può ricoprirne più di uno contemporaneamente. Per i formatori vengono inoltre conservate le certificazioni attive. Il sistema non registra l'assegnazione del personale ai singoli laboratori.

Le persone registrate possono accedere all'applicazione mediante email e password. L'interfaccia distingue i clienti dallo staff e rende disponibili funzionalità differenti in base al profilo autenticato. La password costituisce un dato tecnico dell'applicazione e non un concetto autonomo del dominio.

## 1.2 Rilevamento delle ambiguità e correzioni proposte

A seguito della lettura delle specifiche iniziali, la terminologia è stata uniformata e sono state esplicitate le decisioni necessarie per evitare interpretazioni differenti.

| Termine o espressione iniziale | Termine o decisione adottata | Chiarimento |
| :--- | :--- | :--- |
| Utente / partecipante | **Persona** | Identifica il soggetto fisico che partecipa a un laboratorio o lavora per FlowForest. È distinto dal soggetto che sostiene la spesa. |
| Cliente privato | **Persona Cliente** | È una persona fisica registrata come cliente di FlowForest. |
| Azienda che acquista biglietti | **Azienda Cliente** | Rappresenta il soggetto al quale possono essere fatturati i biglietti acquistati per i propri dipendenti. |
| Formatore esterno / partner | **Azienda Partner** | Rappresenta l'azienda esterna che organizza un proprio evento utilizzando gli spazi di FlowForest. Non vengono gestiti biglietti o fee dell'evento partner. |
| Laboratorio / evento | **Evento**, **Laboratorio**, **Evento Partner** | `EVENTO` raccoglie le caratteristiche comuni; `LABORATORIO` ed `EVENTO_PARTNER` rappresentano le due tipologie alternative. |
| Area dell'evento | Una o più **Aree** | Un evento può utilizzare più aree e la stessa area può ospitare molti eventi nel tempo. |
| Gruppo | Concetto derivato | Il gruppo coincide con l'insieme dei titolari dei biglietti emessi per un laboratorio e non possiede attributi o un ciclo di vita autonomo. |
| Clienti dei partner | Fuori dal perimetro | I partecipanti agli eventi partner non vengono registrati e non ricevono biglietti tramite il sistema FlowForest. |
| Materiale | **Attrezzatura** / **Consumabile** | La specializzazione permette di gestire usura e riutilizzo delle attrezzature, nonché scadenze e allergeni dei consumabili. |
| Quantità necessaria | Attributo di **Impiega** | La quantità utilizzata dipende dalla coppia evento-materiale e viene quindi registrata sull'associazione. |
| Contenuto dell'ordine | Associazione **Include** | Per ogni coppia ordine-consumabile viene registrata la quantità ordinata. |
| Personale / ruolo | **Risorsa Umana** e relativi sottotipi | Mansione e livello salariale appartengono alla Risorsa Umana; Formatore, Operaio e Amministrativo rappresentano ruoli anche contemporanei. |
| Feedback per evento | **Feedback per biglietto** | La valutazione è riferita a una specifica partecipazione; ogni biglietto può produrre al massimo un feedback. |
| Diritto all'invito | Informazione derivata | Il diritto è verificato contando le partecipazioni concluse e non viene memorizzato, evitando una ridondanza. |

## 1.3 Specifiche ristrutturate ed estrazione dei concetti principali

FlowForest utilizza il bosco per realizzare due tipologie di evento: i **Laboratori**, organizzati e venduti direttamente dall'azienda, e gli **Eventi Partner**, organizzati da aziende esterne. Ogni evento possiede un identificativo, una data di inizio, una data di fine e un numero massimo di partecipanti e utilizza una o più aree del bosco.

I Laboratori comprendono titolo, descrizione, protocollo operativo e costo del biglietto e prevedono uno o più Moduli Didattici. Gli Eventi Partner conservano invece il titolo e il collegamento all'Azienda Partner che li organizza. Il sistema non gestisce i biglietti dei partecipanti agli Eventi Partner e non registra fee o ricavi derivanti da tali eventi.

La partecipazione a un Laboratorio viene rappresentata da un **Biglietto** nominale, intestato a una Persona e facoltativamente fatturato a un'Azienda Cliente. Il biglietto conserva codice seriale, data di emissione, richieste relative alle allergie e prezzo effettivamente pagato. A ogni biglietto può essere associato al massimo un Feedback.

Le Persone possono essere registrate come clienti privati oppure come componenti del personale. Una Persona Cliente è collegata al corrispondente Cliente FlowForest. L'Azienda Cliente rimane distinta dall'Azienda Partner, perché la prima paga i biglietti dei propri dipendenti mentre la seconda organizza eventi autonomi.

Il bosco è suddiviso in Aree, ognuna delle quali può contenere più Strutture. Una stessa area può essere utilizzata in eventi differenti e un evento può richiedere più aree. Gli eventi impiegano Materiali e per ogni impiego viene specificata la quantità necessaria.

I Materiali si specializzano in Attrezzature e Consumabili. I consumabili vengono approvvigionati mediante Ordini rivolti a Fornitori; ogni ordine comprende almeno un consumabile e per ogni articolo viene registrata la quantità ordinata.

Il personale è modellato mediante Risorsa Umana, collegata alla corrispondente Persona. Mansione e livello salariale sono proprietà comuni della Risorsa Umana. La specializzazione in Formatore, Operaio e Amministrativo è totale e sovrapposta: ogni risorsa ricopre almeno un ruolo e può ricoprirne più di uno. Non viene memorizzato quale risorsa lavori in uno specifico laboratorio.

L'accesso all'applicazione avviene mediante email e password. Il sistema verifica che la Persona appartenga al profilo Cliente oppure allo Staff e presenta l'area applicativa corrispondente.

### Concetti principali estratti

| Concetto | Categoria | Ruolo nel dominio |
| :--- | :---: | :--- |
| PERSONA | Entità | Soggetto fisico che partecipa ai laboratori o lavora per FlowForest. |
| CLIENTE_FLOWFOREST, PERSONA_CLIENTE | Entità / specializzazione | Registrazione del cliente FlowForest e relativo sottotipo privato. |
| AZIENDA_CLIENTE | Entità | Azienda alla quale può essere fatturato un biglietto. |
| AZIENDA_PARTNER | Entità / specializzazione | Azienda registrata come cliente organizzatore di eventi partner. |
| EVENTO, LABORATORIO, EVENTO_PARTNER | Entità / specializzazione | Evento programmato e relative tipologie interna ed esterna. |
| BIGLIETTO | Entità | Partecipazione nominale a un Laboratorio; nello schema logico è denominato `BIGLIETTO_PERSONA`. |
| FEEDBACK | Entità | Valutazione facoltativa riferita a un singolo biglietto. |
| AREA, STRUTTURA | Entità | Spazi del bosco e strutture fisiche in essi contenute. |
| MATERIALE, ATTREZZATURA, CONSUMABILE | Entità / specializzazione | Inventario e relativi tipi riutilizzabile e a esaurimento. |
| IMPIEGA | Associazione | Collega gli eventi ai materiali specificando `quantita_impiegata`. |
| FORNITORE, ORDINE | Entità | Soggetti e documenti dell'approvvigionamento dei consumabili. |
| INCLUDE | Associazione | Collega ordini e consumabili specificando la quantità ordinata. |
| MODULO_DIDATTICO | Entità | Contenuto formativo previsto da uno o più laboratori. |
| RISORSA_UMANA, FORMATORE, OPERAIO, AMMINISTRATIVO | Entità / specializzazione | Personale interno e ruoli, anche contemporanei, ricoperti. |

## 1.4 Analisi delle operazioni e dei profili applicativi

L'applicazione prevede due profili principali: **Partecipante** e **Gestore**. L'autenticazione tramite email e password costituisce una condizione preliminare comune e non viene conteggiata come operazione del carico applicativo.

### 1.4.1 Operazioni per i partecipanti

- **OP.P1 - Inserimento feedback:** compilare il questionario di soddisfazione relativo a un proprio biglietto, se non è già presente un feedback.
- **OP.P2 - Ricerca biglietto:** ricercare un proprio biglietto e visualizzare i dettagli del Laboratorio corrispondente.
- **OP.P3 - Laboratori futuri:** visualizzare i Laboratori futuri disponibili in calendario.
- **OP.P4 - Materiali necessari:** visualizzare attrezzature, consumabili e relative quantità richieste dal Laboratorio al quale si riferisce un proprio biglietto.
- **OP.P5 - Verifica dell'idoneità all'invito gratuito:** verificare se il cliente ha partecipato ad almeno tre Laboratori conclusi. Il diritto viene calcolato mediante interrogazione e non memorizzato; l'effettiva emissione e gestione dell'invito non rientra nel perimetro del prototipo.

### 1.4.2 Operazioni per i gestori

- **OP.G1 - Registrazione dei soggetti:** registrare una Persona Cliente, un'Azienda Cliente, un'Azienda Partner oppure una Risorsa Umana.
- **OP.G2 - Gestione degli ordini:** registrare un ordine rivolto a un fornitore e, per ciascun consumabile incluso, la quantità ordinata.
- **OP.G3 - Gestione dell'inventario:** inserire, aggiornare o eliminare materiali, attrezzature e consumabili.
- **OP.G4 - Programmazione degli eventi:** creare un Laboratorio oppure un Evento Partner, assegnando date e aree e registrando i dati specifici della tipologia scelta.
- **OP.G5 - Modifica dei laboratori:** aggiornare titolo, descrizione, protocollo operativo, costo del biglietto e moduli didattici.
- **OP.G6 - Storico degli eventi:** consultare i Laboratori e gli Eventi Partner già conclusi.
- **OP.G7 - Analisi della spesa dei clienti:** calcolare la spesa media annua dei clienti sulla base dei prezzi effettivamente pagati per i biglietti.
- **OP.G8 - Attività dei partner:** ordinare le Aziende Partner in base al numero di eventi organizzati in un periodo.
- **OP.G9 - Fatturato dei laboratori:** calcolare per ciascun Laboratorio la somma dei prezzi pagati per i relativi biglietti.
- **OP.G10 - Dettaglio degli ordini e disponibilità:** consultare i consumabili inclusi in ogni ordine, le quantità ordinate, la disponibilità corrente, la soglia di riordino e gli eventuali allergeni.
