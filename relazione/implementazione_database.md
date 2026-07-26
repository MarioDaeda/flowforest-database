# 5. Implementazione nel DBMS (query SQL)

A seguito della progettazione, il database è stato fisicamente implementato su PostgreSQL.
Di seguito si riportano le istruzioni SQL sviluppate per rispondere al carico di lavoro e alle operazioni definite nei Capitoli 1 e 3. Le query rispettano lo schema relazionale finale: le Aree e i Moduli sono collegati agli Eventi mediante relazioni associative, il costo del biglietto appartiene al sottotipo `LABORATORIO` e i Biglietti degli Eventi Partner non vengono gestiti dal sistema.

## 5.1 Definizione dello schema fisico (DDL)

Il file `database/schema.sql` contiene il DDL completo necessario a ricostruire lo schema pubblico: definizione delle 26 relazioni, sequenze degli identificatori numerici, chiavi primarie e secondarie, vincoli referenziali, vincoli di dominio e indici. Il file è stato esportato dal database definitivo e validato eseguendolo in uno schema temporaneo; la prova ha ricreato tutte le relazioni, 76 vincoli e 10 indici secondari ed è terminata con `ROLLBACK`, senza modificare i dati operativi.

Il seguente estratto mostra la traduzione fisica dell'entità `EVENTO` e dell'associazione molti-a-molti con `AREA`; lo script allegato applica sistematicamente la stessa traduzione all'intero schema.

```sql
-- La sequenza evento_id_evento_seq è definita nello script completo.
CREATE TABLE public.evento (
    id_evento INTEGER
        DEFAULT nextval('evento_id_evento_seq'::regclass) NOT NULL,
    data_inizio TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    data_fine TIMESTAMP WITHOUT TIME ZONE NOT NULL,
    partecipanti_max INTEGER NOT NULL
);

ALTER TABLE ONLY public.evento
    ADD CONSTRAINT evento_pkey PRIMARY KEY (id_evento);
ALTER TABLE ONLY public.evento
    ADD CONSTRAINT evento_check CHECK (data_fine > data_inizio);
ALTER TABLE ONLY public.evento
    ADD CONSTRAINT evento_partecipanti_max_check
        CHECK (partecipanti_max > 0);

CREATE TABLE public.evento_area (
    id_evento INTEGER NOT NULL,
    nome_area VARCHAR(50) NOT NULL
);

ALTER TABLE ONLY public.evento_area
    ADD CONSTRAINT evento_area_pkey
        PRIMARY KEY (id_evento, nome_area);
ALTER TABLE ONLY public.evento_area
    ADD CONSTRAINT evento_area_evento_fkey
        FOREIGN KEY (id_evento) REFERENCES evento(id_evento)
        ON UPDATE CASCADE ON DELETE CASCADE;
ALTER TABLE ONLY public.evento_area
    ADD CONSTRAINT evento_area_area_fkey
        FOREIGN KEY (nome_area) REFERENCES area(nome)
        ON UPDATE CASCADE ON DELETE RESTRICT;
```

## 5.2 Operazioni per i partecipanti (clienti)

### OP.P1: Inserimento Feedback
Compilazione del form di soddisfazione al termine di un laboratorio.
```sql
INSERT INTO FEEDBACK (voto, commento, data_compilazione, cod_seriale)
VALUES (5, 'Esperienza fantastica nel bosco, formatore bravissimo!', CURRENT_DATE, 'SERIALE_PROVA_123');
```

### OP.P2: Ricerca Biglietto
Trova le informazioni del Biglietto, del Laboratorio e delle Aree nelle quali si svolge.
```sql
SELECT B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
       E.data_inizio, E.data_fine,
       L.codice_lab, L.titolo,
       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
FROM BIGLIETTO_PERSONA B
JOIN EVENTO E ON B.id_evento = E.id_evento
JOIN LABORATORIO L ON E.id_evento = L.id_evento
JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
WHERE B.cod_seriale = 'SERIALE_PROVA_123'
GROUP BY B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
         E.data_inizio, E.data_fine, L.codice_lab, L.titolo;
```

### OP.P3: Ricerca Eventi Futuri
Elenca i Laboratori futuri con costo, numero massimo di partecipanti e Aree di svolgimento.
```sql
SELECT E.id_evento, L.codice_lab, L.titolo,
       E.data_inizio, E.data_fine, E.partecipanti_max,
       L.costo_biglietto,
       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
FROM EVENTO E
JOIN LABORATORIO L ON E.id_evento = L.id_evento
JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
WHERE E.data_inizio > CURRENT_TIMESTAMP
GROUP BY E.id_evento, L.codice_lab, L.titolo, E.data_inizio, E.data_fine,
         E.partecipanti_max, L.costo_biglietto
ORDER BY E.data_inizio ASC;
```

### OP.P4: Ricerca Materiali Necessari
Seleziona tutti i materiali e le quantità richieste per gli eventi a cui il cliente ha acquistato un biglietto.
```sql
SELECT M.codice_articolo, M.nome_materiale, IM.quantita_impiegata
FROM BIGLIETTO_PERSONA B
JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
WHERE B.cod_seriale = 'SERIALE_PROVA_123'
ORDER BY M.nome_materiale;
```

### OP.P5: Verifica dell'idoneità all'invito gratuito
Verifica se il cliente privato autenticato ha concluso almeno tre partecipazioni a Laboratori. La query calcola soltanto il requisito: l'emissione e il ciclo di vita dell'invito non sono gestiti dal prototipo.
```sql
SELECT COUNT(B.cod_seriale) AS numero_partecipazioni,
       COUNT(B.cod_seriale) >= 3 AS idoneo_invito
FROM BIGLIETTO_PERSONA B
JOIN EVENTO E ON B.id_evento = E.id_evento
JOIN LABORATORIO L ON E.id_evento = L.id_evento
JOIN PERSONA_CLIENTE PC ON B.codice_fiscale = PC.codice_fiscale
JOIN PERSONA P ON PC.codice_fiscale = P.codice_fiscale
WHERE P.mail = 'cliente@email.com'
  AND E.data_fine < CURRENT_TIMESTAMP
  AND B.p_iva_azienda IS NULL;
```

---

## 5.3 Operazioni per i gestori del bosco

### OP.G1: Registrazione Nuovi Clienti
Esempio di inserimento atomico di una nuova Azienda Partner nella gerarchia dei Clienti FlowForest. L'identificatore generato viene trasferito al sottotipo senza ricorrere a valori scritti manualmente.
```sql
WITH nuovo_cliente AS (
    INSERT INTO CLIENTE_FLOWFOREST (data_registrazione)
    VALUES (CURRENT_DATE)
    RETURNING id_cliente
)
INSERT INTO AZIENDA_PARTNER
    (id_cliente, p_iva, nome_azienda, specializzazione, email)
SELECT id_cliente, '12345678901', 'Partner Corp srl',
       'Team Building Outdoor', 'info@partnercorp.it'
FROM nuovo_cliente;
```

### OP.G2: Gestione Ordini al Fornitore
Registrazione atomica di un Ordine e della quantità richiesta per ciascun Consumabile.
```sql
BEGIN;

INSERT INTO ORDINE
    (n_ordine, data_ordine, importo_totale, stato_consegna, p_iva_fornitore)
VALUES ('ORD-2026-001', CURRENT_DATE, 350.00, 'In Elaborazione', '12345678901');

INSERT INTO DETTAGLIO_ORDINE (n_ordine, codice_articolo, quantita)
VALUES
    ('ORD-2026-001', 'ART-FOOD-01', 50),
    ('ORD-2026-001', 'ART-WATER-01', 30);

COMMIT;
```

### OP.G3: Gestione Inventario
Inserimento di nuove attrezzature da campo in magazzino.
```sql
BEGIN;

INSERT INTO MATERIALE
    (codice_articolo, nome_materiale, quantita_inventario, soglia_minima_riordino)
VALUES ('MAT-TENT-02', 'Tenda da campo 4 posti', 10, 2);

INSERT INTO ATTREZZATURA (codice_articolo, stato_usura, data_ultimo_utilizzo)
VALUES ('MAT-TENT-02', 'Nuovo', CURRENT_DATE);

COMMIT;
```

### OP.G4: Programmazione di un Laboratorio
Creazione atomica di un Evento, del relativo sottotipo Laboratorio, delle Aree di svolgimento e dei Moduli previsti. L'esempio mostra due Aree e due Moduli, in accordo con le ipotesi utilizzate nelle tavole degli accessi.
```sql
WITH nuovo_evento AS (
    INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max)
    VALUES ('2026-07-15 09:00:00', '2026-07-15 13:00:00', 20)
    RETURNING id_evento
),
nuovo_laboratorio AS (
    INSERT INTO LABORATORIO
        (id_evento, codice_lab, titolo, descrizione, protocollo_op, costo_biglietto)
    SELECT id_evento, 'LAB_WOOD_02', 'Lavorazione Legno Base',
           'Impara a intagliare', 'Lavoro Manuale', 35.00
    FROM nuovo_evento
    RETURNING id_evento
),
nuove_aree AS (
    INSERT INTO EVENTO_AREA (id_evento, nome_area)
    SELECT NL.id_evento, A.nome_area
    FROM nuovo_laboratorio NL
    CROSS JOIN (VALUES ('Area Nord'), ('Area Didattica')) AS A(nome_area)
)
INSERT INTO LABORATORIO_MODULO (id_evento, id_modulo)
SELECT NL.id_evento, M.id_modulo
FROM nuovo_laboratorio NL
CROSS JOIN (VALUES (1), (2)) AS M(id_modulo);
```

### OP.G5: Modifica dei Laboratori
Aggiornamento dei contenuti e sostituzione dell'insieme dei Moduli associati al Laboratorio.
```sql
BEGIN;

UPDATE LABORATORIO
SET titolo = 'Lavorazione del legno - livello base',
    descrizione = 'Introduzione aggiornata alle tecniche di intaglio',
    protocollo_op = 'Lavoro manuale supervisionato'
WHERE id_evento = 5;

DELETE FROM LABORATORIO_MODULO
WHERE id_evento = 5;

INSERT INTO LABORATORIO_MODULO (id_evento, id_modulo)
VALUES (5, 1), (5, 3);

COMMIT;
```

### OP.G6: Storico degli Eventi
Interrogazione basata sulle date per ritrovare sia i Laboratori sia gli Eventi Partner conclusi, riportando anche le rispettive Aree.
```sql
SELECT E.id_evento,
       COALESCE(L.titolo, EP.titolo) AS titolo,
       CASE
           WHEN L.id_evento IS NOT NULL THEN 'Laboratorio'
           ELSE 'Evento Partner'
       END AS tipologia,
       E.data_inizio, E.data_fine,
       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
FROM EVENTO E
LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
WHERE E.data_fine < CURRENT_TIMESTAMP
GROUP BY E.id_evento, L.id_evento, L.titolo, EP.titolo,
         E.data_inizio, E.data_fine
ORDER BY E.data_inizio DESC;
```

### OP.G7: Analisi Spesa Media Annua dei Clienti Privati
Calcola prima la spesa di ciascun cliente in ogni anno di attività e successivamente la media delle spese annuali.
```sql
WITH spesa_per_anno AS (
    SELECT PC.id_cliente,
           EXTRACT(YEAR FROM B.data_emissione)::INTEGER AS anno,
           SUM(B.prezzo_pagato) AS spesa_annua
    FROM PERSONA_CLIENTE PC
    JOIN BIGLIETTO_PERSONA B
      ON B.codice_fiscale = PC.codice_fiscale
     AND B.p_iva_azienda IS NULL
    GROUP BY PC.id_cliente,
             EXTRACT(YEAR FROM B.data_emissione)::INTEGER
)
SELECT C.id_cliente, P.mail,
       COALESCE(AVG(S.spesa_annua), 0) AS spesa_media_annua
FROM CLIENTE_FLOWFOREST C
JOIN PERSONA_CLIENTE PC ON PC.id_cliente = C.id_cliente
JOIN PERSONA P ON P.codice_fiscale = PC.codice_fiscale
LEFT JOIN spesa_per_anno S ON S.id_cliente = C.id_cliente
GROUP BY C.id_cliente, P.mail
ORDER BY spesa_media_annua DESC, C.id_cliente;
```

### OP.G8: Classifica dei Partner per Eventi Organizzati
Ordina le Aziende Partner in base al numero di Eventi organizzati. Non vengono calcolate provvigioni, perché il sistema non gestisce la bigliettazione degli Eventi Partner.
```sql
SELECT AP.id_cliente, AP.nome_azienda, AP.email,
       COUNT(EP.id_evento) AS numero_eventi
FROM AZIENDA_PARTNER AP
LEFT JOIN EVENTO_PARTNER EP ON AP.id_cliente = EP.id_partner
GROUP BY AP.id_cliente, AP.nome_azienda, AP.email
ORDER BY numero_eventi DESC, AP.nome_azienda;
```

### OP.G9: Calcolo del Fatturato dei Laboratori
Calcola a runtime il numero di Biglietti venduti e il fatturato effettivo di ogni Laboratorio. L'uso di `LEFT JOIN` permette di includere anche i Laboratori che non hanno ancora venduto Biglietti.
```sql
SELECT E.id_evento,
       L.codice_lab,
       L.titolo,
       COUNT(B.cod_seriale) AS biglietti_venduti,
       COALESCE(SUM(B.prezzo_pagato), 0) AS fatturato
FROM EVENTO E
JOIN LABORATORIO L ON E.id_evento = L.id_evento
LEFT JOIN BIGLIETTO_PERSONA B ON E.id_evento = B.id_evento
WHERE EXTRACT(YEAR FROM E.data_inizio) = 2026
GROUP BY E.id_evento, L.codice_lab, L.titolo
ORDER BY fatturato DESC, L.titolo;
```

### OP.G10: Consultazione Quantità e Disponibilità dei Consumabili Ordinati
Mostra il contenuto di un Ordine distinguendo la quantità richiesta nella riga d'ordine dalla quantità attualmente disponibile in magazzino. Include anche soglia di riordino, scadenza e allergeni del Consumabile.
```sql
SELECT O.n_ordine,
       O.data_ordine,
       F.ragione_sociale,
       D.codice_articolo,
       M.nome_materiale,
       D.quantita AS quantita_ordinata,
       M.quantita_inventario AS quantita_disponibile,
       M.soglia_minima_riordino,
       C.data_scadenza,
       C.allergeni_presenti
FROM ORDINE O
JOIN FORNITORE F ON F.p_iva = O.p_iva_fornitore
JOIN DETTAGLIO_ORDINE D ON D.n_ordine = O.n_ordine
JOIN CONSUMABILE C ON C.codice_articolo = D.codice_articolo
JOIN MATERIALE M ON M.codice_articolo = C.codice_articolo
WHERE O.n_ordine = 'ORD-2026-001'
ORDER BY M.nome_materiale;
```
