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
