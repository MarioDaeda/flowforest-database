- [ ] inserire foto schemi
    - [ ] concettuale
    - [ ] conettuale evoluzioni

- [ ]  aggiungere l'indice

- [] dire se è verso l'alto o basso per ogni caso "Raffinamento dello Schema ed eliminazione Gerarchie"

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
