# RELAZIONE
- [ ] far eoperaizone sql di visualizzare quantità materiale specifico o materiali in generale
- [ ] inserire foto schemi
    - [ ] concettuale
    - [ ] concettuale evoluzioni
- [ ] schema scheletro(solo entità e pochi dettagli) (fase distinta, prima dei raffinamenti) — verificare se coincide con "evoluzioni"


- [ ] Gerarchie
    - [ ]scegliere  come tradofromare materiale,  consumabili e attrezzatura

- [ ] gli schemi di navigazione e le tabelle degli accessi
    - [ ] inserire frequenze per tutte le operazioni
    - [ ] controllare note scritte nelle tabelle da llm
    
- [ ] traduzione sistematica di entità/associazioni in relazioni (non solo lo schema finale)
## nice to have
- [] aggiungere CREATE TABLE in SQL prima delle query DML

# CODICE
- [ ] far eoperaizone sql di visualizzare quantità materiale specifico o materiali in generale
- [] trattare questa cosa che mi ha detto opus alla fine della sessione. Problema: disallineamento tra relazione e codice (sezione UI)
Dove si trova: relazione/Relazione_Completa_FlowForest.md, sezione "Progettazione dell'Applicazione" → "2. Interfaccia Utente e Funzionalità" (circa righe 566-576 nel file originale, ora spostate per l'aggiunta della sezione 3).
- [ ] renderlo meno AI style usando opus/fable spinti(prima preparare prompt)


Cosa descrive la relazione (obsoleto):
Tre tab uniche e generiche:

2.1 "Pannello Operativo" (CRUD generico)
2.2 "Registri & Anagrafiche" (SELECT * generico)
2.3 "Recensioni & Feedback" (dashboard analytics)
Cosa fa davvero il codice (app.py):
Due aree applicative selezionate dal ruolo di login (cliente/admin/server), ciascuna con le proprie tab:

Area Partecipanti (B2C) — riga 259 — 3 tab:

🎫 Ricerca Biglietto & Attrezzatura
📅 Eventi Disponibili
✍️ Compila Feedback
Area Gestione Bosco (Admin & Formatori) — riga 397 — 7 tab:

👤 Registrazione Utenti
📦 Gestione Materiali & Ordini
📅 Laboratori & Eventi
📊 Analisi & Report Finanziari
✏️ Modifica Laboratori
💬 Recensioni & Feedback
📋 Registri & Anagrafiche
Inoltre manca completamente nella relazione la descrizione del sistema di login/ruoli (cliente via email, admin, server) che abbiamo costruito nelle sessioni precedenti — quello non è mai stato documentato.

Cosa fare
Riscrivere la sezione "2. Interfaccia Utente e Funzionalità" per descrivere fedelmente:

Il sistema di autenticazione a ruoli (cliente/admin/server) e cosa vede ciascuno
Le due aree applicative reali
Le 3 + 7 tab effettive, con una riga di descrizione ciascuna (cosa fa, quali operazioni OP.x copre)
Nessuna modifica al codice è necessaria — è solo un aggiornamento di documentazione in Relazione_Completa_FlowForest.md.


- [] inserire come codice la query  per il conteggio delle 3 persone. SELECT COUNT(B.cod_seriale) AS numero_partecipazioni 
    "
    SELECT COUNT(B.cod_seriale) AS numero_partecipazioni
    FROM BIGLIETTO_PERSONA B
        JOIN EVENTO E ON B.id_evento = E.id_evento
        JOIN LABORATORIO L ON E.id_evento = L.id_evento
        JOIN PERSONA_CLIENTE PC ON B.codice_fiscale = PC.codice_fiscale
        JOIN PERSONA P ON PC.codice_fiscale = P.codice_fiscale
    WHERE P.mail = 'cliente@email.com' 
        AND L.id_modulo = 1 
        AND E.data_fine < NOW()
        AND B.p_iva_azienda IS NULL
    GROUP BY P.codice_fiscale
    HAVING COUNT(B.cod_seriale) >= 3;
    "
## nice to have
- [] modifcare ordine visualizzazione feedback(evento, voto, cognome...) mettere id vari dopo
