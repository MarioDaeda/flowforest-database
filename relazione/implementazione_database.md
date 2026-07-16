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
