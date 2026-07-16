# Relazione Finale di Progetto: Basi di Dati
**Progetto:** Database per FlowForest

# Analisi dei Requisiti

## 1.1 Testo delle specifiche (Dominio)
L’obiettivo del progetto è realizzare un sistema di supporto gestionale e di analisi dei dati di un Laboratorio di Intelligenza Pratica situato in un contesto boschivo ("FlowForest").

Ogni utente verrà registrato alla piattaforma in base al profilo:
*   Cliente singolo (B2C)
*   Azienda (B2B)
*   Formatore/coach esterno ("Partner"), che utilizzerà il bosco come location.

Un utente (o un'azienda) può partecipare a dei **Laboratori** nel bosco.
Ogni laboratorio specifica le date, il numero di partecipanti, le aree del bosco utilizzate, il fatturato e il protocollo operativo applicato (es. lavoro manuale). Gli eventi interni saranno anche collegati alla gestione della scaletta e ai contenuti dei moduli. Per gli eventi partner invece verrà memorizzata anche una percentuale (fee) sui guadagni dalle vendite.

Una volta concluso il laboratorio, il sistema permette ai partecipanti di descrivere tramite risposte ad un form la propria esperienza.

Nel sistema verranno anche gestiti gli ordini, la disponibilità del materiale e il personale.

## 1.2 Glossario e Risoluzione delle Ambiguità
A seguito della lettura delle specifiche iniziali, i requisiti sono stati formalizzati e le terminologie unificate per evitare ridondanze.

| Termine Originale | Nuovo Termine (Entità) | Motivazione / Definizione |
| :--- | :--- | :--- |
| Utente / Partecipante | **Persona** | Identifica fisicamente chi partecipa all'evento, distinguendolo dal soggetto che paga il biglietto. |
| Azienda / Privato | **Cliente** | Rappresenta l'entità contabile (B2B o B2C) a cui viene intestato il biglietto. |
| Formatore esterno | **Azienda Partner** | Soggetto B2B2C che affitta il bosco per i propri eventi pagando una fee. |
| Laboratorio / Evento | **Evento** | Generalizzazione creata per accorpare sia i laboratori interni sia gli eventi dei partner. |
| Materiale | **Attrezzatura** / **Consumabile** | Scomposto in due sottocategorie per poter gestire scadenze/allergeni (consumabili) o stati di usura (attrezzature). |
| Personale | **Risorsa Umana** | Il termine generico è stato modellato in base ai ruoli effettivi (Formatore, Operaio, Amministrativo). |

## 1.3 Specifica delle Operazioni
Il carico di lavoro del database è guidato dalle seguenti operazioni principali richieste dai due profili di utenza previsti (Partecipanti e Gestori).

### Operazioni per i Partecipanti (Clienti)
*   **(OP.P1) Inserimento Feedback:** Compilare dei form per la soddisfazione a fine laboratorio.
*   **(OP.P2) Ricerca Biglietto:** Ricercare il proprio biglietto e i dettagli dell'evento.
*   **(OP.P3) Eventi Futuri:** Esplorare gli eventi futuri disponibili in calendario.
*   **(OP.P4) Attrezzatura Necessaria:** Visualizzare l’attrezzatura richiesta per gli eventi a cui si è iscritti.
*   **(OP.P5) Sistema Inviti:** Concedere ai partecipanti, dopo 3 partecipazioni, di invitare gratuitamente dei conoscenti.

### Operazioni per i Gestori del Bosco (Amministratori)
*   **(OP.G1) Registrazione Cliente:** Registrare un nuovo utente privato o azienda partner.
*   **(OP.G2) Gestione Ordini:** Registrare nuovi ordini ai fornitori, con controllo degli allergeni per i consumabili.
*   **(OP.G3) Gestione Inventario:** Inserire o eliminare materiale dall’inventario del magazzino.
*   **(OP.G4) Programmazione Eventi:** Creare e prenotare un nuovo Laboratorio (interno o esterno) indicando partecipanti, costi e tipo.
*   **(OP.G5) Modifica Laboratori:** Aggiornare tutti gli elementi testuali e didattici riguardanti i laboratori.
*   **(OP.G6) Storico Eventi:** Visualizzare lo storico e l'esito dei laboratori passati.
*   **(OP.G7) Analisi Spesa Clienti:** Visualizzare la spesa media annua di ogni cliente registrato.
*   **(OP.G8) Classifica Partner:** Scoprire il formatore esterno che ha generato il maggior volume di ricavi tramite fee nell'anno.
*   **(OP.G9) Fatturato:** Visualizzare il fatturato complessivo generato da ogni singolo evento.


---

# Progettazione Concettuale (Modello E-R)

## 1. ENTITÀ E ATTRIBUTI
*(Gli identificatori principali sono <u>sottolineati</u>)*

*   **Persona**: <u>codice_fiscale</u>, nome, cognome, data_nascita, telefono, mail, contatto_emergenza, note_allergia
*   **Azienda Cliente**: <u>p_iva</u>, nome_azienda, pec_fatturazione, email
*   **Cliente FlowForest**: <u>id_cliente</u>, data_registrazione, telefono, email
*   **Risorsa Umana**: <u>id_dipendente</u>, iban, data_assunzione, ruolo
*   **Formatore**: certificazioni_attive
*   **Operaio**: mansione, livello_salariale
*   **Amministrativo**: mansione, livello_salariale
*   **Area**: <u>nome</u>, capienza, scopo
*   **Struttura**: <u>codice_struttura</u>, funzione_uso
*   **Materiale**: <u>codice_articolo</u>, nome_materiale, quantita_inventario, soglia_minima_riordino
*   **Attrezzatura**: stato_usura, data_ultimo_utilizzo
*   **Consumabile**: data_scadenza, allergeni_presenti
*   **Fornitore**: <u>p_iva</u>, ragione_sociale
*   **Ordine**: <u>n_ordine</u>, data_ordine, importo_totale, stato_consegna
*   **Modulo Didattico**: <u>id_modulo</u>, nome, testo
*   **Evento**: <u>id_evento</u>, data_inizio, data_fine, partecipanti_max, costo_biglietto
*   **Laboratorio**: codice_lab *(identificatore secondario)*, titolo, descrizione, protocollo_op
*   **Evento Partner**: titolo, fee_percentuale
*   **Biglietto Persona**: <u>cod_seriale</u>, data_emissione, richiesta_allergie, biglietto_aziendale, prezzo_pagato
*   **Feedback**: <u>id_feedback</u>, voto, commento, data_compilazione

---

## 2. GERARCHIE (Specializzazioni IS-A)
*   **Persona** (Padre) ➔ **Risorsa Umana**, **Persona Cliente** (Figlie).
    *   *Tipo:* Parziale e Sovrapposta *(Una persona può essere contemporaneamente dipendente e cliente, o nessuno dei due).*
*   **Risorsa Umana** (Padre) ➔ **Formatore**, **Operaio**, **Amministrativo** (Figlie).
    *   *Tipo:* Parziale e Sovrapposta *(Un dipendente come "Mario" può ricoprire tutti e tre i ruoli).*
*   **Cliente FlowForest** (Padre) ➔ **Persona Cliente**, **Azienda Partner** (Figlie).
    *   *Tipo:* Totale ed Esclusiva *(Un cliente del bosco o è un privato, o è un'azienda B2B che organizza).*
*   **Materiale** (Padre) ➔ **Attrezzatura**, **Consumabile** (Figlie).
    *   *Tipo:* Totale ed Esclusiva *(Non ci sono materiali che non ricadono in una di queste due categorie).*
*   **Evento** (Padre) ➔ **Laboratorio**, **Evento Partner** (Figlie).
    *   *Tipo:* Totale ed Esclusiva *(Un evento o è gestito internamente come lab, o ha una fee in partnership).*

---

## 3. ASSOCIAZIONI E CARDINALITÀ (Min, Max)
*La lettura indica la partecipazione dell'entità all'associazione.*

*   **Appartiene** tra `Struttura` e `Area`
    *   Struttura **(1,1)**: Ogni struttura si trova in una e una sola area.
    *   Area **(0,N)**: Un'area può contenere da zero a molte strutture.
*   **Ospita** tra `Evento` e `Area`
    *   Evento **(1,1)**: Un evento si tiene esattamente in una specifica area.
    *   Area **(0,N)**: Un'area può ospitare da zero a molti eventi nel tempo.
*   **Invia_A** tra `Ordine` e `Fornitore`
    *   Ordine **(1,1)**: Un ordine contabile è indirizzato a un solo fornitore.
    *   Fornitore **(0,N)**: Un fornitore può ricevere da zero a molti ordini nel tempo.
*   **Include** tra `Ordine` e `Consumabile` *(con attributo dell'associazione: Quantità)*
    *   Ordine **(1,N)**: Ogni ordine deve contenere almeno un articolo consumabile.
    *   Consumabile **(0,N)**: Un consumabile può apparire in più ordini storici.
*   **Impiega** tra `Evento` e `Materiale` *(con attributo dell'associazione: Quantità_Impiegata)*
    *   Evento **(0,N)**: Un evento può richiedere da zero a molti materiali.
    *   Materiale **(0,N)**: Un materiale (es. accetta, legna) può essere usato in molti eventi.
*   **Si_Basa_Su** tra `Laboratorio` e `Modulo Didattico`
    *   Laboratorio **(1,1)**: Un laboratorio didattico ha un solo modulo obbligatorio di riferimento.
    *   Modulo Didattico **(0,N)**: Lo stesso modulo teorico può essere erogato in infiniti laboratori nel tempo.
*   **Co-Organizza** tra `Evento Partner` e `Azienda Partner`
    *   Evento Partner **(1,1)**: Un evento esterno è legato a una singola azienda partner.
    *   Azienda Partner **(0,N)**: Un partner può organizzare vari eventi nel tempo.
*   **Valido_Per** tra `Biglietto Persona` ed `Evento`
    *   Biglietto Persona **(1,1)**: Il biglietto è emesso specificamente per un solo evento.
    *   Evento **(1,N)**: Un evento deve avere almeno un biglietto venduto (o N biglietti).
*   **Intestazione_Fisica** tra `Biglietto Persona` e `Persona`
    *   Biglietto Persona **(1,1)**: Ogni biglietto è nominale, intestato alla persona fisica che si presenterà al bosco.
    *   Persona **(0,N)**: Una persona può acquistare zero o più biglietti nel tempo.
*   **Intestazione_Aziendale** (Fatturazione B2B) tra `Biglietto Persona` e `Azienda Cliente`
    *   Biglietto Persona **(0,1)**: Un biglietto può NON essere intestato ad aziende (B2C privato) oppure esserlo a 1 singola azienda (B2B welfare).
    *   Azienda Cliente **(0,N)**: Un'azienda cliente può pagare zero o più biglietti per i suoi dipendenti.
*   **Lascia** tra `Feedback` e `Biglietto Persona`
    *   Feedback **(1,1)**: Un feedback esiste solo se legato a un biglietto valido.
    *   Biglietto Persona **(0,1)**: Chi ha un biglietto può scegliere di non lasciare feedback (0) oppure di lasciarne al massimo uno (1).


---

# Progettazione Logica

## 1. Stima dei Volumi e delle Frequenze
Al fine di operare scelte progettuali coerenti, si ipotizza il seguente volume di dati in uno scenario reale (basato sulla stima di circa 2 eventi mensili da 30-40 partecipanti) su base annua:
*   **Eventi/Laboratori**: ~24 istanze all'anno (2 al mese).
*   **Biglietti Persona**: ~1000 istanze all'anno (media di 40 biglietti per evento).
*   **Feedback**: ~500 istanze all'anno (stimando che circa il 50% dei partecipanti lasci una recensione).
*   **Clienti e Persone Anagrafate**: ~1000 istanze in progressivo aumento.
*   **Materiale**: ~200 istanze costanti in inventario.

## 2. Analisi delle Ridondanze
Nello schema ER non sono presenti dati mantenuti appositamente per ridondanza strutturale (come il numero totale dei partecipanti calcolato a priori su un evento o il calcolo in tempo reale del fatturato). Si opta per l'assenza totale di ridondanze, preferendo calcolare i totali a runtime tramite istruzioni `COUNT` e `SUM` in SQL, poiché il volume d'accesso e le prestazioni del DBMS cloud lo permettono agilmente senza influire negativamente sull'efficienza.

## 3. Raffinamento dello Schema ed eliminazione Gerarchie
Nel passaggio da Modello Concettuale a Modello Logico si è resa necessaria la traduzione delle gerarchie.
1. **Risorse Umane e Staff:** Utilizzo della *Class Table Inheritance*. Le classi figlie mantengono tabelle distinte relazionate 1:1 con la PK della tabella padre (`RISORSA_UMANA`). La scelta è dettata dal fatto che lo staff può ricoprire ruoli multipli contemporaneamente (es. la stessa persona può essere Formatore e Amministrativo).
2. **Clienti:** Eliminazione e divisione. I clienti privati sono identificati tramite una tabella di puro raccordo con la persona fisica, mentre i partner e le aziende fatturanti mantengono tabelle isolate vista l'esclusività totale.
3. **Eventi:** La struttura per `EVENTO`, `LABORATORIO` ed `EVENTO_PARTNER` adotta la condivisione della chiave primaria derivata dal padre, garantendo isolamento dei metadati (fee percentuale vs moduli didattici).

## 4. Schema Relazionale Finale
*Legenda: **<u>sottolineatura</u>** indica la Chiave Primaria (PK), **FK** (Foreign Key) indica le chiavi esterne e **AK** (Alternate Key) indica le chiavi univoche secondarie.*

**PERSONA**(<u>codice_fiscale</u>, nome, cognome, note_allergia, data_nascita, telefono, mail, contatto_emergenza)
AK: mail

**AZIENDA_CLIENTE**(<u>p_iva</u>, nome_azienda, pec_fatturazione, email)
AK: pec_fatturazione
AK: email

**CLIENTE_FLOWFOREST**(<u>id_cliente</u>, data_registrazione, telefono, email)
AK: email

**PERSONA_CLIENTE**(<u>id_cliente</u>, <u>codice_fiscale</u>)
FK: id_cliente REFERENCES CLIENTE_FLOWFOREST
FK: codice_fiscale REFERENCES PERSONA
AK: codice_fiscale

**AZIENDA_PARTNER**(<u>id_cliente</u>, p_iva, nome_azienda, specializzazione, email)
FK: id_cliente REFERENCES CLIENTE_FLOWFOREST
AK: p_iva
AK: email

**RISORSA_UMANA**(<u>id_dipendente</u>, iban, data_assunzione, codice_fiscale, ruolo)
FK: codice_fiscale REFERENCES PERSONA
AK: codice_fiscale

**FORMATORE**(<u>id_dipendente</u>, certificazioni_attive)
FK: id_dipendente REFERENCES RISORSA_UMANA

**OPERAIO**(<u>id_dipendente</u>, mansione, livello_salariale)
FK: id_dipendente REFERENCES RISORSA_UMANA

**AMMINISTRATIVO**(<u>id_dipendente</u>, mansione, livello_salariale)
FK: id_dipendente REFERENCES RISORSA_UMANA

**AREA**(<u>nome</u>, capienza, scopo)

**STRUTTURA**(<u>codice_struttura</u>, funzione_uso, nome_area)
FK: nome_area REFERENCES AREA

**MATERIALE**(<u>codice_articolo</u>, nome_materiale, quantita_inventario, soglia_minima_riordino)
AK: nome_materiale

**ATTREZZATURA**(<u>codice_articolo</u>, stato_usura, data_ultimo_utilizzo)
FK: codice_articolo REFERENCES MATERIALE

**CONSUMABILE**(<u>codice_articolo</u>, data_scadenza, allergeni_presenti)
FK: codice_articolo REFERENCES MATERIALE

**FORNITORE**(<u>p_iva</u>, ragione_sociale)

**ORDINE**(<u>n_ordine</u>, data_ordine, importo_totale, stato_consegna, p_iva_fornitore)
FK: p_iva_fornitore REFERENCES FORNITORE

**DETTAGLIO_ORDINE**(<u>n_ordine</u>, <u>codice_articolo</u>, quantita)
FK: n_ordine REFERENCES ORDINE
FK: codice_articolo REFERENCES CONSUMABILE

**MODULO_DIDATTICO**(<u>id_modulo</u>, nome, testo)
AK: nome

**EVENTO**(<u>id_evento</u>, data_inizio, data_fine, partecipanti_max, costo_biglietto, nome_area)
FK: nome_area REFERENCES AREA

**LABORATORIO**(<u>id_evento</u>, codice_lab, titolo, descrizione, protocollo_op, id_modulo)
FK: id_evento REFERENCES EVENTO
FK: id_modulo REFERENCES MODULO_DIDATTICO
AK: codice_lab

**EVENTO_PARTNER**(<u>id_evento</u>, titolo, id_partner, fee_percentuale)
FK: id_evento REFERENCES EVENTO
FK: id_partner REFERENCES AZIENDA_PARTNER

**IMPIEGO_MATERIALE**(<u>codice_articolo</u>, <u>id_evento</u>, quantita_impiegata)
FK: codice_articolo REFERENCES MATERIALE
FK: id_evento REFERENCES EVENTO

**BIGLIETTO_PERSONA**(<u>cod_seriale</u>, data_emissione, richiesta_allergie, biglietto_aziendale, prezzo_pagato, id_evento, p_iva_azienda, codice_fiscale)
FK: id_evento REFERENCES EVENTO
FK: p_iva_azienda REFERENCES AZIENDA_CLIENTE
FK: codice_fiscale REFERENCES PERSONA

**FEEDBACK**(<u>id_feedback</u>, voto, commento, data_compilazione, cod_seriale)
FK: cod_seriale REFERENCES BIGLIETTO_PERSONA
AK: cod_seriale


---

# Il Progetto Fisico

## 1. Indicizzazione degli attributi
In quest'ultimo capitolo ci occupiamo di modellare ulteriormente il progetto logico applicando raffinamenti fisici. Tali accorgimenti sono mirati a ottimizzare l'organizzazione fisica dei dati nel database PostgreSQL, riducendo i tempi di ricerca e i costi di accesso al disco. 

Di seguito vengono elencati gli **Indici (Index)** previsti, siano essi generati automaticamente dal DBMS (B-Tree sulle chiavi) o previsti in fase di progettazione per velocizzare le clausole di `JOIN` e `WHERE`.

### 1.1 Indici Primari (Primary Keys)
Il sistema DBMS genera automaticamente un indice B-Tree per ogni chiave primaria. Nel nostro database, gli indici primari garantiscono l'accesso diretto e istantaneo alle entità:
*   `PERSONA`: Indice primario su `codice_fiscale`.
*   `AZIENDA_CLIENTE`: Indice primario su `p_iva`.
*   `CLIENTE_FLOWFOREST`: Indice primario su `id_cliente`.
*   `RISORSA_UMANA`: Indice primario su `id_dipendente`.
*   `AREA`: Indice primario su `nome`.
*   `STRUTTURA`: Indice primario su `codice_struttura`.
*   `MATERIALE`: Indice primario su `codice_articolo`.
*   `FORNITORE`: Indice primario su `p_iva`.
*   `ORDINE`: Indice primario su `n_ordine`.
*   `MODULO_DIDATTICO`: Indice primario su `id_modulo`.
*   `EVENTO`: Indice primario su `id_evento`.
*   `BIGLIETTO_PERSONA`: Indice primario su `cod_seriale`.
*   `FEEDBACK`: Indice primario su `id_feedback`.

### 1.2 Indici Univoci (Alternate Keys)
Anche i vincoli di unicità (`UNIQUE`) prevedono la creazione di un indice dedicato, utile sia per far rispettare il vincolo a livello fisico che per eseguire login veloci.
*   `PERSONA`: Indice univoco su `mail`.
*   `AZIENDA_CLIENTE`: Indice univoco su `pec_fatturazione` e `email`.
*   `CLIENTE_FLOWFOREST`: Indice univoco su `email`.
*   `MATERIALE`: Indice univoco su `nome_materiale` (molto utile per la ricerca testuale in inventario).
*   `MODULO_DIDATTICO`: Indice univoco su `nome`.

### 1.3 Indici Secondari Sulle Chiavi Esterne (Foreign Keys)
A differenza delle chiavi primarie, le chiavi esterne non vengono indicizzate di default da PostgreSQL. Per migliorare sensibilmente le prestazioni delle query complesse e dei JOIN (in particolar modo per il calcolo del fatturato o delle Analytics), si è prevista l'implementazione dei seguenti indici secondari:
*   `BIGLIETTO_PERSONA (id_evento)`: Essenziale in quanto quasi tutte le interrogazioni di spesa o fatturato filtrano i biglietti unendoli all'evento.
*   `BIGLIETTO_PERSONA (codice_fiscale)`: Fondamentale per ritrovare rapidamente lo storico acquisti di una singola persona fisica.
*   `LABORATORIO (id_modulo)`: Utile per trovare tutti i laboratori che adottano un determinato protocollo o testo didattico.
*   `DETTAGLIO_ORDINE (n_ordine, codice_articolo)`: Velocizza il ritrovamento del contenuto di un acquisto in magazzino.
*   `IMPIEGO_MATERIALE (id_evento)`: Velocizza enormemente il recupero della lista attrezzatura per un evento in partenza.

## 2. Ordinamento su attributi
Il motore del database è stato ottimizzato per pre-ordinare i risultati in base a criteri di business specifici, che evitano di appesantire il Front-End e l'interfaccia Streamlit.
*   `EVENTO (data_inizio)`: Gli eventi vengono prevalentemente estratti con `ORDER BY data_inizio ASC` per mostrare prima gli eventi più imminenti.
*   `FEEDBACK (data_compilazione)`: I commenti vengono sempre ordinati in senso decrescente (`DESC`) per poter monitorare il polso della situazione attuale.
*   `ORDINE (data_ordine)`: Allo stesso modo, il cruscotto amministrativo ordina le forniture partendo dall'ordine più recente per monitorare lo stato di consegna in real-time.


---

# Implementazione nel DBMS (Query SQL)

A seguito della progettazione, il database è stato fisicamente implementato su PostgreSQL (versione 16). 
Di seguito si riportano le interrogazioni SQL (DML) sviluppate per rispondere al carico di lavoro e alle operazioni previste dall'Analisi dei Requisiti (Capitolo 1).

## 1. Operazioni per i Partecipanti (Clienti)

### OP.P1: Inserimento Feedback
Compilazione del form di soddisfazione al termine di un laboratorio.
```sql
INSERT INTO FEEDBACK (voto, commento, data_compilazione, cod_seriale) 
VALUES (5, 'Esperienza fantastica nel bosco, formatore bravissimo!', CURRENT_DATE, 'SERIALE_PROVA_123');
```

### OP.P2: Ricerca Biglietto
Trova le informazioni del biglietto e i dettagli dell'evento collegato tramite Join.
```sql
SELECT B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
       E.data_inizio, E.data_fine, 
       COALESCE(L.titolo, EP.titolo) AS nome_evento,
       E.nome_area
FROM BIGLIETTO_PERSONA B
JOIN EVENTO E ON B.id_evento = E.id_evento
LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
WHERE B.cod_seriale = 'SERIALE_PROVA_123';
```

### OP.P3: Ricerca Eventi Futuri
Elenca tutti gli eventi futuri con i relativi dettagli, calcolando a runtime la tipologia (Interno o Partner).
```sql
SELECT E.id_evento, E.data_inizio, E.data_fine, E.costo_biglietto, E.nome_area,
       COALESCE(L.titolo, EP.titolo) AS titolo_evento,
       CASE WHEN L.id_evento IS NOT NULL THEN 'Interno' ELSE 'Partner' END AS tipologia
FROM EVENTO E
LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
WHERE E.data_inizio > NOW()
ORDER BY E.data_inizio ASC;
```

### OP.P4: Ricerca Attrezzatura Necessaria
Seleziona tutti i materiali e le quantità richieste per gli eventi a cui il cliente ha acquistato un biglietto.
```sql
SELECT M.nome_materiale, IM.quantita_impiegata
FROM BIGLIETTO_PERSONA B
JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
WHERE B.cod_seriale = 'SERIALE_PROVA_123';
```

### OP.P5: Sistema Inviti Gratuiti
Verifica tramite Join con l'anagrafica se la persona fisica ha già partecipato ad almeno 3 laboratori formativi.
```sql
SELECT COUNT(B.cod_seriale) AS numero_partecipazioni
FROM BIGLIETTO_PERSONA B
JOIN EVENTO E ON B.id_evento = E.id_evento
JOIN LABORATORIO L ON E.id_evento = L.id_evento
JOIN PERSONA_CLIENTE PC ON (B.p_iva_azienda IS NULL)
JOIN PERSONA P ON PC.codice_fiscale = P.codice_fiscale
WHERE P.mail = 'cliente@email.com' AND L.id_modulo = 1 AND E.data_fine < NOW();
```

---

## 2. Operazioni per i Gestori del Bosco

### OP.G1: Registrazione Nuovi Clienti
Esempio di inserimento gerarchico di una nuova Azienda Partner.
```sql
INSERT INTO CLIENTE_FLOWFOREST (telefono, email) 
VALUES ('0546123456', 'info@partnercorp.it') RETURNING id_cliente;

INSERT INTO AZIENDA_PARTNER (id_cliente, p_iva, nome_azienda, specializzazione, email) 
VALUES (2, '12345678901', 'Partner Corp srl', 'Team Building Outdoor', 'info@partnercorp.it');
```

### OP.G2: Gestione Ordini al Fornitore
Registrazione di un ordine e dei relativi dettagli per i consumabili.
```sql
INSERT INTO ORDINE (n_ordine, data_ordine, importo_totale, stato_consegna, p_iva_fornitore) 
VALUES ('ORD-2026-001', CURRENT_DATE, 350.00, 'In Elaborazione', '12345678901');

INSERT INTO DETTAGLIO_ORDINE (n_ordine, codice_articolo, quantita) 
VALUES ('ORD-2026-001', 'ART-FOOD-01', 50);
```

### OP.G3: Gestione Inventario
Inserimento di nuove attrezzature da campo in magazzino.
```sql
INSERT INTO MATERIALE (codice_articolo, nome_materiale, quantita_inventario, soglia_minima_riordino) 
VALUES ('MAT-TENT-02', 'Tenda da campo 4 posti', 10, 2);

INSERT INTO ATTREZZATURA (codice_articolo, stato_usura, data_ultimo_utilizzo) 
VALUES ('MAT-TENT-02', 'Nuovo', CURRENT_DATE);
```

### OP.G4: Programmazione di un Laboratorio
Creazione di un nuovo evento e aggancio dei metadati specifici del laboratorio didattico.
```sql
INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max, costo_biglietto, nome_area) 
VALUES ('2026-07-15 09:00:00', '2026-07-15 13:00:00', 20, 35.00, 'Area Nord') RETURNING id_evento;

INSERT INTO LABORATORIO (id_evento, codice_lab, titolo, descrizione, protocollo_op, id_modulo) 
VALUES (5, 'LAB_WOOD_02', 'Lavorazione Legno Base', 'Impara a intagliare', 'Lavoro Manuale', 1);
```

### OP.G5: Storico Laboratori Effettuati
Interrogazione basata sulle date per ritrovare i laboratori conclusi.
```sql
SELECT E.id_evento, L.titolo, E.data_inizio, E.data_fine, E.costo_biglietto, L.protocollo_op
FROM EVENTO E
JOIN LABORATORIO L ON E.id_evento = L.id_evento
WHERE E.data_fine < NOW()
ORDER BY E.data_inizio DESC;
```

### OP.G6: Analisi Spesa Media Annua dei Clienti Privati
Report analitico con funzioni aggregate per trovare la spesa media storica.
```sql
SELECT C.id_cliente, C.email,
       COALESCE(SUM(BP.prezzo_pagato), 0) AS spesa_totale,
       COUNT(DISTINCT EXTRACT(YEAR FROM BP.data_emissione)) AS anni_attivi,
       COALESCE(SUM(BP.prezzo_pagato) / NULLIF(COUNT(DISTINCT EXTRACT(YEAR FROM BP.data_emissione)), 0), 0) AS spesa_media_annua
FROM CLIENTE_FLOWFOREST C
LEFT JOIN PERSONA_CLIENTE PC ON C.id_cliente = PC.id_cliente
LEFT JOIN BIGLIETTO_PERSONA BP ON PC.codice_fiscale = BP.codice_fiscale AND BP.p_iva_azienda IS NULL
GROUP BY C.id_cliente, C.email
ORDER BY spesa_media_annua DESC;
```

### OP.G7: Classifica Ricavi dai Partner
Restituisce l'azienda partner che ha generato il maggior volume di entrate per FlowForest calcolando le provvigioni sui biglietti.
```sql
SELECT AP.id_cliente, AP.nome_azienda, AP.email,
       SUM(E.costo_biglietto * (SELECT COUNT(*) FROM BIGLIETTO_PERSONA B WHERE B.id_evento = E.id_evento) * (EP.fee_percentuale / 100)) AS ricavi_fee_totali
FROM AZIENDA_PARTNER AP
JOIN EVENTO_PARTNER EP ON AP.id_cliente = EP.id_partner
JOIN EVENTO E ON EP.id_evento = E.id_evento
WHERE EXTRACT(YEAR FROM E.data_inizio) = 2026
GROUP BY AP.id_cliente, AP.nome_azienda, AP.email
ORDER BY ricavi_fee_totali DESC
LIMIT 1;
```

### OP.G8: Calcolo del Fatturato Lordo e Netto per Evento
Fornisce un'analisi istantanea sulle performance economiche di ogni singola esperienza (Laboratorio o Partner).
```sql
SELECT E.id_evento,
       COALESCE(L.titolo, EP.titolo) AS nome_evento,
       CASE WHEN L.id_evento IS NOT NULL THEN 'Interno' ELSE 'Partner' END AS tipo,
       COUNT(B.cod_seriale) AS biglietti_venduti,
       COALESCE(SUM(B.prezzo_pagato), 0) AS fatturato_lordo,
       CASE 
           WHEN EP.id_evento IS NOT NULL THEN COALESCE(SUM(B.prezzo_pagato), 0) * (EP.fee_percentuale / 100)
           ELSE COALESCE(SUM(B.prezzo_pagato), 0)
       END AS ricavo_netto_flowforest
FROM EVENTO E
LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
LEFT JOIN BIGLIETTO_PERSONA B ON E.id_evento = B.id_evento
GROUP BY E.id_evento, L.titolo, EP.titolo, L.id_evento, EP.id_evento, EP.fee_percentuale
ORDER BY fatturato_lordo DESC;
```


---

# Progettazione dell'Applicazione

## 1. Architettura dell'Applicazione e Scelte Tecnologiche
A differenza dei progetti tradizionali sviluppati esclusivamente in ambiente locale (`localhost`), il gestionale del laboratorio "FlowForest" è stato ingegnerizzato fin dalla sua nascita per essere **operativo e distribuibile in Cloud** sul mercato reale, abbattendo la necessità di installazioni complesse per gli utenti finali (i gestori del bosco).

L'architettura del sistema si fonda su tre pilastri:
1.  **Backend e RDBMS (PostgreSQL):** Il database relazionale è ospitato pubblicamente in Cloud Serverless tramite l'infrastruttura di **Neon.tech** (appoggiata su server AWS a Francoforte). Questa scelta garantisce un'elevata sicurezza transazionale, backup automatici e scalabilità orizzontale in caso di picchi di traffico.
2.  **Linguaggio e Connessione (Python + Psycopg2):** L'intero applicativo è scritto nel linguaggio *Python 3*. La comunicazione tra il client e il DBMS remoto avviene in sicurezza tramite il driver `psycopg2-binary`, incapsulando tutte le operazioni DML sensibili in transazioni protette (`conn.commit()`) per prevenire anomalie o modifiche parziali.
3.  **Frontend Web (Streamlit):** L'interfaccia utente è interamente sviluppata avvalendosi del framework **Streamlit**. Il deployment front-end è gestito da *Streamlit Community Cloud*, il quale preleva automaticamente gli aggiornamenti in continuous integration dalla repository del codice sorgente situata su **GitHub**.

Questa architettura distribuita permette ai fondatori di accedere in mobilità (dal proprio smartphone nel bosco o dal computer in amministrazione) in maniera concorrenziale senza conflitti.

## 2. Interfaccia Utente e Funzionalità
Per agevolare l'amministrazione, l'interfaccia dell'applicazione è divisa in viste logiche (Tab) coerenti con i casi d'uso:

### 2.1 Tab "Pannello Operativo"
Il tab principale è dedicato agli inserimenti interattivi. Contiene form specifici che implementano le operazioni **CRUD** (Create, Read, Update, Delete) dell'Amministratore, incluse la registrazione di nuovi Laboratori, l'acquisizione di nuove Risorse Umane e l'aggiunta di materiale nell'inventario.

### 2.2 Tab "Registri & Anagrafiche"
Questa vista rappresenta l'incarnazione grafica dei comandi standard `SELECT * FROM Tabella`. Permette di navigare lo schema relazionale mostrando in tempo reale lo stato delle anagrafiche dei clienti, delle attrezzature e degli storici ordini.

### 2.3 Tab "Recensioni & Feedback" (Dashboard Analitica)
In quest'area vengono esposte le **Analytics** del progetto. Vengono eseguite le query SQL complesse (contenenti join multipli e funzioni aggregate) necessarie a calcolare in tempo reale il fatturato lordo/netto, ad individuare il partner che ha generato i ricavi più alti o ad esporre la spesa media annua pro capite.

---

> *[NOTA PER GLI STUDENTI: FATE 3 O 4 SCREENSHOT DELL'APP E INCOLLATELI QUI SOTTO]*

![Pannello Operativo]([INSERIRE_SCREENSHOT_1_QUI])

![Registri e Tabelle]([INSERIRE_SCREENSHOT_2_QUI])

![Dashboard Fatturato e Feedback]([INSERIRE_SCREENSHOT_3_QUI])


---

