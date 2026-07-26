# 2. Progettazione concettuale

## 2.1 Schema scheletro

Lo schema scheletro costituisce la prima rappresentazione sintetica del dominio. In questa fase vengono mostrati soltanto i concetti principali e i collegamenti necessari a descrivere il funzionamento generale di FlowForest, senza introdurre specializzazioni, attributi e identificatori di dettaglio.

I concetti inizialmente individuati sono `CLIENTE`, `PARTECIPAZIONE`, `PERSONA`, `EVENTO`, `AREA`, `MATERIALE`, `MODULO_DIDATTICO`, `FEEDBACK`, `RISORSA_UMANA`, `ORDINE` e `FORNITORE`.

`PARTECIPAZIONE` rappresenta inizialmente l'iscrizione acquistata da un Cliente, intestata alla Persona che prende parte all'Evento. Una Partecipazione può generare un Feedback. Ogni Evento si svolge in una o più Aree, impiega Materiali e può basarsi su Moduli Didattici. Una Persona può essere identificata anche come Risorsa Umana. Gli Ordini comprendono Materiali e vengono ricevuti dai Fornitori.

![Schema scheletro del dominio FlowForest](immagini/schema_scheletro_flowforest.png)

*Figura 2.1 - Schema scheletro del dominio FlowForest.*

Lo schema scheletro non coincide con lo schema concettuale finale. Le entità generiche vengono successivamente specializzate, mentre alcuni collegamenti vengono precisati o trasformati per rappresentare correttamente i vincoli emersi durante l'analisi.

## 2.2 Raffinamenti proposti

L'analisi dettagliata dei requisiti conduce ai seguenti raffinamenti.

1. **Dalla Partecipazione al Biglietto.** L'entità preliminare `PARTECIPAZIONE` viene raffinata in `BIGLIETTO`. Vengono aggiunti codice seriale, data di emissione, prezzo pagato e richieste relative alle allergie. Ogni Biglietto è intestato a una Persona, è valido per un solo Laboratorio e può essere facoltativamente fatturato a un'Azienda Cliente.

2. **Feedback riferito alla partecipazione.** Il Feedback non viene collegato genericamente alla Persona o all'Evento, ma al Biglietto che identifica una specifica partecipazione. In questo modo una persona può valutare separatamente edizioni diverse dello stesso Laboratorio e ogni Biglietto può generare al massimo un Feedback.

3. **Specializzazione degli eventi.** `EVENTO` viene specializzato in `LABORATORIO` ed `EVENTO_PARTNER`. La specializzazione è totale ed esclusiva: ogni evento appartiene esattamente a una delle due categorie. Il Laboratorio è organizzato e venduto direttamente da FlowForest e possiede titolo, descrizione, protocollo operativo e costo del biglietto. L'Evento Partner conserva il titolo ed è collegato all'Azienda Partner che lo organizza. Il sistema non gestisce biglietti, partecipanti o fee degli Eventi Partner.

4. **Utilizzo di più aree.** Il collegamento iniziale tra Evento e Area viene precisato come associazione molti-a-molti. Ogni Evento utilizza almeno un'Area e può utilizzarne diverse; una stessa Area può essere riutilizzata da più Eventi nel tempo.

5. **Composizione didattica dei Laboratori.** Il collegamento generico tra Evento e Modulo Didattico viene limitato ai Laboratori. Ogni Laboratorio prevede uno o più Moduli Didattici, mentre lo stesso Modulo può essere utilizzato in più Laboratori.

6. **Specializzazione dei materiali.** `MATERIALE` viene specializzato in `ATTREZZATURA` e `CONSUMABILE`. La specializzazione è totale ed esclusiva. Le Attrezzature possiedono stato di usura e data dell'ultimo utilizzo; i Consumabili possiedono data di scadenza ed eventuali allergeni.

7. **Quantificazione dei materiali impiegati.** L'associazione molti-a-molti `IMPIEGA` tra Evento e Materiale viene dotata dell'attributo `quantita_impiegata`, perché la quantità necessaria dipende dalla specifica coppia evento-materiale.

8. **Dettaglio degli ordini.** Il collegamento generico tra Ordine e Materiale viene limitato ai Consumabili. L'associazione molti-a-molti `INCLUDE` riceve l'attributo `quantita`, che indica la quantità richiesta di ogni consumabile. La relazione `DETTAGLIO_ORDINE` nascerà soltanto nella successiva traduzione logica dell'associazione e non costituisce un'entità autonoma del modello concettuale.

9. **Distinzione dei soggetti commerciali.** Il concetto iniziale di Cliente viene precisato distinguendo `PERSONA_CLIENTE`, `AZIENDA_CLIENTE` e `AZIENDA_PARTNER`. `PERSONA_CLIENTE` rappresenta il cliente privato e corrisponde a una Persona; `AZIENDA_CLIENTE` rappresenta il soggetto al quale può essere fatturato un Biglietto; `AZIENDA_PARTNER` organizza Eventi Partner. `CLIENTE_FLOWFOREST` generalizza Persona Cliente e Azienda Partner, mentre Azienda Cliente rimane separata per il diverso ruolo di fatturazione.

10. **Anagrafica e ruoli del personale.** Una Risorsa Umana è collegata alla Persona che la identifica. Mansione e livello salariale vengono collocati nella Risorsa Umana perché descrivono il rapporto lavorativo generale. La Risorsa Umana viene specializzata in `FORMATORE`, `OPERAIO` e `AMMINISTRATIVO`; la specializzazione è totale e sovrapposta, perché ogni risorsa ricopre almeno un ruolo e può ricoprirne più di uno. Soltanto il Formatore possiede l'attributo specifico `certificazioni_attive`. Non viene rappresentata l'assegnazione del personale ai singoli Laboratori.

11. **Introduzione delle strutture.** Il concetto di Area viene completato introducendo `STRUTTURA`. Ogni Struttura appartiene esattamente a un'Area, mentre un'Area può contenere zero o più Strutture.

12. **Gruppo come informazione derivata.** Non viene introdotta un'entità Gruppo, perché il gruppo di un Laboratorio coincide con l'insieme delle Persone intestatarie dei relativi Biglietti e non possiede attributi o un ciclo di vita autonomo.

## 2.3 Schema concettuale finale

### 2.3.1 Entità e identificatori

Gli identificatori principali sono indicati con `id`, mentre `id'` indica un identificatore alternativo. I sottotipi ereditano l'identificatore dall'entità padre, salvo la presenza di un identificatore alternativo esplicitamente indicato.

- **PERSONA**: codice_fiscale, nome, cognome, note_allergia, data_nascita, telefono, mail, contatto_emergenza. **Identificatori:** `id: codice_fiscale`; `id': mail`.
- **CLIENTE_FLOWFOREST**: id_cliente, data_registrazione. **Identificatore:** `id: id_cliente`.
- **PERSONA_CLIENTE**: nessun attributo specifico; eredita l'identificatore da `CLIENTE_FLOWFOREST`.
- **AZIENDA_PARTNER**: p_iva, nome_azienda, specializzazione, email. **Identificatore alternativo:** `id': p_iva`; l'identificatore principale è ereditato da `CLIENTE_FLOWFOREST`.
- **AZIENDA_CLIENTE**: p_iva, nome_azienda, pec_fatturazione, email. **Identificatori:** `id: p_iva`; `id': pec_fatturazione`; `id'': email`.
- **RISORSA_UMANA**: id_dipendente, iban, data_assunzione, mansione, livello_salariale. **Identificatore:** `id: id_dipendente`.
- **FORMATORE**: certificazioni_attive; eredita l'identificatore da `RISORSA_UMANA`.
- **OPERAIO**: nessun attributo specifico; eredita l'identificatore da `RISORSA_UMANA`.
- **AMMINISTRATIVO**: nessun attributo specifico; eredita l'identificatore da `RISORSA_UMANA`.
- **AREA**: nome, capienza, scopo. **Identificatore:** `id: nome`.
- **STRUTTURA**: codice_struttura, funzione_uso. **Identificatore:** `id: codice_struttura`.
- **MATERIALE**: codice_articolo, nome_materiale, quantita_inventario, soglia_minima_riordino. **Identificatori:** `id: codice_articolo`; `id': nome_materiale`.
- **ATTREZZATURA**: stato_usura, data_ultimo_utilizzo; eredita l'identificatore da `MATERIALE`.
- **CONSUMABILE**: data_scadenza, allergeni_presenti; eredita l'identificatore da `MATERIALE`.
- **FORNITORE**: p_iva, ragione_sociale. **Identificatore:** `id: p_iva`.
- **ORDINE**: n_ordine, data_ordine, importo_totale, stato_consegna. **Identificatore:** `id: n_ordine`.
- **MODULO_DIDATTICO**: id_modulo, nome, testo. **Identificatori:** `id: id_modulo`; `id': nome`.
- **EVENTO**: id_evento, data_inizio, data_fine, partecipanti_max. **Identificatore:** `id: id_evento`.
- **LABORATORIO**: codice_lab, titolo, descrizione, protocollo_op, costo_biglietto. **Identificatore alternativo:** `id': codice_lab`; l'identificatore principale è ereditato da `EVENTO`.
- **EVENTO_PARTNER**: titolo; eredita l'identificatore da `EVENTO`.
- **BIGLIETTO**: cod_seriale, data_emissione, richiesta_allergie, prezzo_pagato. **Identificatore:** `id: cod_seriale`.
- **FEEDBACK**: id_feedback, voto, commento, data_compilazione. **Identificatore:** `id: id_feedback`.

La password utilizzata dall'applicazione è un attributo tecnico di `PERSONA` e verrà documentata nella progettazione logica e applicativa; non rappresenta un concetto autonomo del dominio.

### 2.3.2 Gerarchie

| Entità padre | Entità figlie | Vincolo | Motivazione |
| :--- | :--- | :--- | :--- |
| `MATERIALE` | `ATTREZZATURA`, `CONSUMABILE` | Totale ed esclusiva | Ogni materiale appartiene a una sola delle due categorie. |
| `EVENTO` | `LABORATORIO`, `EVENTO_PARTNER` | Totale ed esclusiva | Ogni evento è interno oppure organizzato da un partner. |
| `CLIENTE_FLOWFOREST` | `PERSONA_CLIENTE`, `AZIENDA_PARTNER` | Totale ed esclusiva | Ogni cliente registrato assume esattamente uno dei due ruoli. |
| `RISORSA_UMANA` | `FORMATORE`, `OPERAIO`, `AMMINISTRATIVO` | Totale e sovrapposta | Ogni risorsa ricopre almeno un ruolo e può ricoprirne diversi. |

`PERSONA` non costituisce il padre di `PERSONA_CLIENTE` o `RISORSA_UMANA`: i collegamenti sono rappresentati rispettivamente dalle associazioni `CORRISPONDE` e `IDENTIFICA`.

### 2.3.3 Associazioni e cardinalità

| Associazione | Prima partecipazione | Seconda partecipazione | Attributi |
| :--- | :--- | :--- | :--- |
| `CONTIENE` | `STRUTTURA` `(1,1)` | `AREA` `(0,N)` | — |
| `OSPITA` | `EVENTO` `(1,N)` | `AREA` `(0,N)` | — |
| `IMPIEGA` | `EVENTO` `(0,N)` | `MATERIALE` `(0,N)` | `quantita_impiegata` |
| `COMMISSIONA` | `ORDINE` `(1,1)` | `FORNITORE` `(0,N)` | — |
| `INCLUDE` | `ORDINE` `(1,N)` | `CONSUMABILE` `(0,N)` | `quantita` |
| `PREVEDE` | `LABORATORIO` `(1,N)` | `MODULO_DIDATTICO` `(0,N)` | — |
| `ORGANIZZA` | `EVENTO_PARTNER` `(1,1)` | `AZIENDA_PARTNER` `(0,N)` | — |
| `VALIDITÀ` | `BIGLIETTO` `(1,1)` | `LABORATORIO` `(0,N)` | — |
| `INTESTATO` | `BIGLIETTO` `(1,1)` | `PERSONA` `(0,N)` | — |
| `FATTURAZIONE` | `BIGLIETTO` `(0,1)` | `AZIENDA_CLIENTE` `(0,N)` | — |
| `GENERA` | `FEEDBACK` `(1,1)` | `BIGLIETTO` `(0,1)` | — |
| `CORRISPONDE` | `PERSONA_CLIENTE` `(1,1)` | `PERSONA` `(0,1)` | — |
| `IDENTIFICA` | `RISORSA_UMANA` `(1,1)` | `PERSONA` `(0,1)` | — |

Le cardinalità esprimono, tra gli altri, i seguenti vincoli: un Evento deve utilizzare almeno un'Area; un Laboratorio deve prevedere almeno un Modulo Didattico; un Biglietto è sempre intestato a una Persona e valido per un solo Laboratorio; la fatturazione a un'Azienda Cliente e la compilazione del Feedback sono facoltative.

### 2.3.4 Diagramma E-R finale

![Schema concettuale E-R finale di FlowForest](immagini/schema_concettuale_finale_flowforest.png)

*Figura 2.2 - Schema concettuale E-R finale di FlowForest.*
