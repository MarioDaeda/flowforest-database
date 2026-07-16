# Progettazione Concettuale (Modello E-R)

## 1. ENTITÀ E ATTRIBUTI
*(Gli identificatori principali / Chiavi Primarie sono <u>sottolineati</u>)*

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
