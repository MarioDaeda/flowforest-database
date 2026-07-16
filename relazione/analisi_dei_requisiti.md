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
