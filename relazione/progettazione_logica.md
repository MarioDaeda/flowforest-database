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
