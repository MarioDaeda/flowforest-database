import streamlit as st
import pandas as pd
import psycopg2
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Configurazione della Pagina
st.set_page_config(
    page_title="FlowForest Database Portal",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tema & Stili CSS personalizzati per Estetica Premium
st.markdown("""
<style>
    .main {
        background-color: #f4f6f3;
    }
    h1, h2, h3 {
        color: #1e3f20;
        font-family: 'Inter', sans-serif;
    }
    .reportview-container {
        background: #f4f6f3;
    }
    .sidebar .sidebar-content {
        background: #2d5a27;
    }
    div.stButton > button:first-child {
        background-color: #2d5a27;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 8px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1e3f20;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    .db-status {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Inizializzazione session state
if 'db_conn_info' not in st.session_state:
    st.session_state['db_conn_info'] = None
if 'db_connected' not in st.session_state:
    st.session_state['db_connected'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'user_email' not in st.session_state:
    st.session_state['user_email'] = None
if 'user_cf' not in st.session_state:
    st.session_state['user_cf'] = None

# Credenziali del database: SOLO da variabili d'ambiente (.env in locale,
# secrets del servizio di hosting in produzione). Mai committate nel repo.
# Neon richiede sslmode=require per connessioni sicure.
DB_DEFAULTS = {
    'host': os.environ.get('DB_HOST', ''),
    'database': os.environ.get('DB_NAME', ''),
    'user': os.environ.get('DB_USER', ''),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port': os.environ.get('DB_PORT', '5432'),
    'sslmode': 'require',
}

# Anche lo STAFF fa login "da persona": sono le persone fisiche presenti in
# RISORSA_UMANA. Login con mail + password di PERSONA. Ogni dipendente accede
# come 'admin' (accesso pieno). Nessun account applicativo separato.
def verifica_credenziali_staff(mail, password):
    try:
        conn = psycopg2.connect(**DB_DEFAULTS)
    except Exception as e:
        st.sidebar.error(f"Errore di connessione al database: {e}")
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.password, p.codice_fiscale, p.nome, p.cognome, ru.ruolo
            FROM PERSONA p
            JOIN RISORSA_UMANA ru ON ru.codice_fiscale = p.codice_fiscale
            WHERE p.mail = %s
            """,
            (mail,),
        )
        row = cur.fetchone()
        if row is None:
            return {"found": False}
        password_reale, codice_fiscale, nome, cognome, ruolo_lavorativo = row
        if password == password_reale:
            return {
                "found": True,
                "ok": True,
                "ruolo": "admin",  # tutta la risorsa_umana ha accesso pieno
                "ruolo_lavorativo": ruolo_lavorativo,
                "codice_fiscale": codice_fiscale,
                "nome": nome,
                "cognome": cognome,
            }
        return {"found": True, "ok": False}
    finally:
        cur.close()
        conn.close()


# I CLIENTI, invece, sono le persone fisiche già registrate: il login avviene
# direttamente contro PERSONA (mail + password) verificando che quella persona
# sia effettivamente un cliente (presente in PERSONA_CLIENTE). Nessun account
# applicativo separato: si accede "da persona".
def verifica_credenziali_cliente(mail, password):
    try:
        conn = psycopg2.connect(**DB_DEFAULTS)
    except Exception as e:
        st.sidebar.error(f"Errore di connessione al database: {e}")
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT p.password, p.codice_fiscale, p.nome, p.cognome
            FROM PERSONA p
            JOIN PERSONA_CLIENTE pc ON pc.codice_fiscale = p.codice_fiscale
            WHERE p.mail = %s
            """,
            (mail,),
        )
        row = cur.fetchone()
        if row is None:
            return {"found": False}
        password_reale, codice_fiscale, nome, cognome = row
        if password == password_reale:
            return {
                "found": True,
                "ok": True,
                "codice_fiscale": codice_fiscale,
                "nome": nome,
                "cognome": cognome,
            }
        return {"found": True, "ok": False}
    finally:
        cur.close()
        conn.close()

# Sidebar per l'autenticazione utente
st.sidebar.image("logo_flow.jpeg", use_container_width=True)
st.sidebar.title("🔐 Login Portale")

# Mostra form di login se non autenticato
if not st.session_state['authenticated']:
    login_tipo = st.sidebar.radio("Accedi come:", ["Cliente", "Staff (Admin/Server)"])

    if login_tipo == "Cliente":
        st.sidebar.markdown("Accedi con la mail usata in fase di registrazione.")
        email_input = st.sidebar.text_input("Email:", placeholder="mario.rossi@email.com")
        password_input = st.sidebar.text_input("Password:", type="password", placeholder="Inserisci password")

        if st.sidebar.button("Accedi"):
            esito = verifica_credenziali_cliente(email_input, password_input)
            if esito is None:
                pass  # errore di connessione già mostrato
            elif not esito["found"]:
                st.sidebar.error("❌ Email non trovata tra i clienti!")
            elif not esito["ok"]:
                st.sidebar.error("❌ Password errata!")
            else:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'cliente'
                st.session_state['user_email'] = email_input
                st.session_state['user_cf'] = esito["codice_fiscale"]
                st.sidebar.success(f"✅ Benvenuto/a {esito['nome']}!")
                st.rerun()
    else:
        st.sidebar.markdown("Accedi con la mail aziendale (personale dipendente).")
        email_staff_input = st.sidebar.text_input("Email:", placeholder="nome.cognome@email.com")
        password_input = st.sidebar.text_input("Password:", type="password", placeholder="Inserisci password")

        if st.sidebar.button("Accedi"):
            esito = verifica_credenziali_staff(email_staff_input, password_input)
            if esito is None:
                pass  # errore di connessione già mostrato
            elif not esito["found"]:
                st.sidebar.error("❌ Email non trovata tra il personale!")
            elif not esito["ok"]:
                st.sidebar.error("❌ Password errata!")
            else:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = esito["ruolo"]
                st.session_state['user_email'] = email_staff_input
                st.session_state['user_cf'] = esito["codice_fiscale"]
                st.sidebar.success(f"✅ Benvenuto/a {esito['nome']} ({esito['ruolo_lavorativo']})!")
                st.rerun()

if st.session_state['authenticated']:
    st.sidebar.success(f"✅ Autenticato come: **{st.session_state['user_role'].upper()}**")

    def get_connection(conn_info):
        try:
            return psycopg2.connect(**conn_info)
        except Exception as e:
            st.sidebar.error(f"Errore di connessione: {e}")
            return None

    # Cliente e Admin si connettono in automatico con le credenziali predefinite,
    # senza vedere/poter modificare la configurazione del DB
    if st.session_state['user_role'] in ['cliente', 'admin']:
        if not st.session_state['db_connected']:
            conn_info = dict(DB_DEFAULTS)
            conn = get_connection(conn_info)
            if conn:
                st.session_state['db_conn_info'] = conn_info
                st.session_state['db_connected'] = True
                conn.close()
    else:
        # Solo server vede il form di configurazione DB
        st.sidebar.markdown("---")
        st.sidebar.title("Configurazione DB")
        st.sidebar.markdown("Inserisci le credenziali del database PostgreSQL (precompilate da variabili d'ambiente, se presenti).")

        db_host = st.sidebar.text_input("Host", value=DB_DEFAULTS['host'])
        db_name = st.sidebar.text_input("Database Name", value=DB_DEFAULTS['database'])
        db_user = st.sidebar.text_input("User", value=DB_DEFAULTS['user'])
        db_password = st.sidebar.text_input("Password", type="password", value=DB_DEFAULTS['password'])
        db_port = st.sidebar.text_input("Port", value=DB_DEFAULTS['port'])

        if st.sidebar.button("Connetti al Database"):
            conn_info = {
                'host': db_host,
                'database': db_name,
                'user': db_user,
                'password': db_password,
                'port': db_port
            }
            conn = get_connection(conn_info)
            if conn:
                st.session_state['db_conn_info'] = conn_info
                st.session_state['db_connected'] = True
                st.sidebar.success("Connesso con successo! 🎉")
                conn.close()

    # Button logout
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Logout"):
        st.session_state['authenticated'] = False
        st.session_state['user_role'] = None
        st.session_state['user_email'] = None
        st.session_state['user_cf'] = None
        st.session_state['db_connected'] = False
        st.session_state['db_conn_info'] = None
        st.rerun()

# Navbar principale per le aree applicative
st.title("🌳 FlowForest Database Management Portal")
st.markdown("---")

if not st.session_state['authenticated']:
    st.warning("🔒 Per favore, accedi con le tue credenziali nella sidebar per continuare.")
    st.image("panorama flow.jpeg", use_container_width=True, caption="Il bosco di FlowForest")
elif not st.session_state['db_connected']:
    st.info("👈 Per favore, configura le credenziali di PostgreSQL nella sidebar a sinistra e fai clic su **Connetti al Database** per abilitare il portale.")
    st.image("panorama flow.jpeg", use_container_width=True, caption="Il bosco di FlowForest")
elif st.session_state['authenticated'] and st.session_state['db_connected']:
    # Definizione delle funzioni di utilità per le query
    def run_query(query, params=None):
        conn = psycopg2.connect(**st.session_state['db_conn_info'])
        cur = conn.cursor()
        try:
            cur.execute(query, params)
            if cur.description:
                columns = [desc[0] for desc in cur.description]
                data = cur.fetchall()
                df = pd.DataFrame(data, columns=columns)
            else:
                df = None
            conn.commit()
            return df
        except Exception as e:
            st.error(f"Errore durante l'esecuzione della query: {e}")
            return None
        finally:
            cur.close()
            conn.close()

    def run_transaction(statements):
        """Esegue una lista di (query, params) in un'unica transazione atomica.
        In caso di errore esegue il rollback e non lascia dati parziali.
        Restituisce True se il commit va a buon fine, False altrimenti."""
        conn = psycopg2.connect(**st.session_state['db_conn_info'])
        cur = conn.cursor()
        try:
            for query, params in statements:
                cur.execute(query, params)
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            st.error(f"Errore durante la transazione (nessuna modifica applicata): {e}")
            return False
        finally:
            cur.close()
            conn.close()

    # Selezione dell'Area Applicativa in base al ruolo
    if st.session_state['user_role'] == 'cliente':
        app_mode = "Area Partecipanti (B2C)"
        st.info("👤 Accesso limitato - Visualizzi solo l'Area Partecipanti")
    elif st.session_state['user_role'] == 'admin':
        app_mode = "Area Gestione Bosco (Admin & Formatori)"
        st.info("⚙️ Accesso amministratore - Area Gestione Bosco")
    else:
        app_mode = st.selectbox(
            "Seleziona l'Area Applicativa:",
            ["Area Partecipanti (B2C)", "Area Gestione Bosco (Admin & Formatori)"]
        )

    st.markdown("---")

    # =========================================================================
    # AREA PARTECIPANTI (B2C)
    # =========================================================================
    if app_mode == "Area Partecipanti (B2C)":
        st.header("👤 Servizi per i Partecipanti")
        
        tab1, tab2, tab3 = st.tabs(["🎫 Ricerca Biglietto & Attrezzatura", "📅 Eventi Disponibili", "✍️ Compila Feedback"])
        
        with tab1:
            st.subheader("I tuoi Biglietti")

            # Se l'utente è un cliente autenticato via email, mostra automaticamente
            # tutti i biglietti collegati alla sua anagrafica (PERSONA.mail)
            if st.session_state.get('user_email'):
                q_my_tickets = """
                SELECT B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
                       E.data_inizio, E.data_fine,
                       COALESCE(L.titolo, EP.titolo) AS nome_evento,
                       E.nome_area
                FROM BIGLIETTO_PERSONA B
                JOIN PERSONA P ON B.codice_fiscale = P.codice_fiscale
                JOIN EVENTO E ON B.id_evento = E.id_evento
                LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
                LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
                WHERE P.mail = %s
                ORDER BY E.data_inizio DESC;
                """
                df_my_tickets = run_query(q_my_tickets, (st.session_state['user_email'],))

                if df_my_tickets is not None and not df_my_tickets.empty:
                    st.dataframe(df_my_tickets, use_container_width=True)

                    st.subheader("🎒 Attrezzatura Richiesta per i tuoi Eventi:")
                    q_my_equip = """
                    SELECT DISTINCT COALESCE(L.titolo, EP.titolo) AS nome_evento, M.nome_materiale, IM.quantita_impiegata
                    FROM BIGLIETTO_PERSONA B
                    JOIN PERSONA P ON B.codice_fiscale = P.codice_fiscale
                    JOIN EVENTO E ON B.id_evento = E.id_evento
                    LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
                    LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
                    JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
                    JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
                    WHERE P.mail = %s;
                    """
                    df_my_equip = run_query(q_my_equip, (st.session_state['user_email'],))
                    if df_my_equip is not None and not df_my_equip.empty:
                        st.dataframe(df_my_equip, use_container_width=True)
                    else:
                        st.info("Nessuna attrezzatura particolare richiesta per i tuoi eventi.")
                else:
                    st.info("Non risulta ancora nessun biglietto associato alla tua mail.")

                st.markdown("---")

            st.subheader("Cerca un Biglietto per Codice Seriale")
            ticket_serial = st.text_input("Inserisci il Codice Seriale del Biglietto:", placeholder="Esempio: SERIALE_PROVA_123")

            if ticket_serial:
                # 1. Ricerca Biglietto
                q_ticket = """
                SELECT B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
                       E.data_inizio, E.data_fine,
                       COALESCE(L.titolo, EP.titolo) AS nome_evento,
                       E.nome_area
                FROM BIGLIETTO_PERSONA B
                JOIN EVENTO E ON B.id_evento = E.id_evento
                LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
                LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
                WHERE B.cod_seriale = %s;
                """
                df_ticket = run_query(q_ticket, (ticket_serial,))

                if df_ticket is not None and not df_ticket.empty:
                    st.success("Biglietto Trovato!")
                    st.dataframe(df_ticket)

                    # 2. Ricerca Attrezzatura Necessaria
                    st.subheader("🎒 Attrezzatura Richiesta per l'Evento:")
                    q_equip = """
                    SELECT M.nome_materiale, IM.quantita_impiegata
                    FROM BIGLIETTO_PERSONA B
                    JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
                    JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
                    WHERE B.cod_seriale = %s;
                    """
                    df_equip = run_query(q_equip, (ticket_serial,))
                    if df_equip is not None and not df_equip.empty:
                        st.dataframe(df_equip)
                    else:
                        st.info("Nessuna attrezzatura particolare richiesta per questo evento.")
                else:
                    st.warning("Nessun biglietto trovato con questo codice seriale.")

        with tab2:
            st.subheader("Esplora gli Eventi in Programma")
            q_events = """
            SELECT E.id_evento, E.data_inizio, E.data_fine, E.costo_biglietto, E.nome_area,
                   COALESCE(L.titolo, EP.titolo) AS titolo_evento,
                   CASE WHEN L.id_evento IS NOT NULL THEN 'Interno' ELSE 'Partner' END AS tipologia
            FROM EVENTO E
            LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
            LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
            WHERE E.data_inizio > NOW()
            ORDER BY E.data_inizio ASC;
            """
            df_events = run_query(q_events)
            if df_events is not None:
                st.dataframe(df_events, use_container_width=True)

        with tab3:
            st.subheader("Invia un Feedback sul Laboratorio")
            st.write("Aiutaci a migliorare compilando il form di gradimento a fine attività.")
            
            fb_serial = st.text_input("Codice Seriale Biglietto (Feedback):", key="fb_serial")
            fb_voto = st.slider("Assegna un voto (1-5):", min_value=1, max_value=5, value=5)
            fb_commento = st.text_area("Inserisci un commento:", placeholder="Scrivi qui cosa ne pensi...")
            
            if st.button("Invia Feedback"):
                if not fb_serial:
                    st.error("Inserisci il codice seriale del biglietto.")
                else:
                    q_check_ticket = "SELECT 1 FROM BIGLIETTO_PERSONA WHERE cod_seriale = %s;"
                    df_check = run_query(q_check_ticket, (fb_serial,))
                    if df_check is not None and not df_check.empty:
                        q_insert_fb = """
                        INSERT INTO FEEDBACK (voto, commento, data_compilazione, cod_seriale) 
                        VALUES (%s, %s, CURRENT_DATE, %s);
                        """
                        res = run_query(q_insert_fb, (fb_voto, fb_commento, fb_serial))
                        st.success("Feedback inviato con successo! Grazie per la collaborazione. 🌳")
                    else:
                        st.error("Il codice seriale inserito non corrisponde a nessun biglietto registrato.")

    # =========================================================================
    # AREA GESTIONE BOSCO (ADMIN)
    # =========================================================================
    elif app_mode == "Area Gestione Bosco (Admin & Formatori)":
        # Controllo accesso: solo admin e server possono accedere
        if st.session_state['user_role'] not in ['admin', 'server']:
            st.error("🔐 Accesso negato! Solo admin e server possono accedere a questa area.")
            st.stop()

        st.header("⚙️ Portale Amministratore Bosco")
        
        tab_admin1, tab_admin2, tab_admin3, tab_admin4, tab_admin5, tab_admin6, tab_admin7 = st.tabs([
            "👤 Registrazione Utenti", 
            "📦 Gestione Materiali & Ordini", 
            "📅 Laboratori & Eventi", 
            "📊 Analisi & Report Finanziari",
            "✏️ Modifica Laboratori",
            "💬 Recensioni & Feedback",
            "📋 Registri & Anagrafiche"
        ])
        
        with tab_admin1:
            st.subheader("Registra un Nuovo Utente")
            ut_tipo = st.radio("Tipo di Utente:", ["Cliente Privato (B2C)", "Azienda Partner (B2B)"])
            
            ut_tel = st.text_input("Telefono:")
            ut_email = st.text_input("Email:")
            
            if ut_tipo == "Cliente Privato (B2C)":
                cf = st.text_input("Codice Fiscale:")
                nome = st.text_input("Nome:")
                cognome = st.text_input("Cognome:")
                data_nascita = st.date_input(
                    "Data di Nascita:",
                    value=datetime.date(2000, 1, 1),
                    min_value=datetime.date(1920, 1, 1),
                    max_value=datetime.date.today()
                )
                note_allergie = st.text_input("Allergie/Intolleranze:")
                cont_emerg = st.text_input("Contatto di Emergenza:")
                
                if st.button("Registra Cliente"):
                    # 1. Inserimento Persona
                    q_pers = """
                    INSERT INTO PERSONA (codice_fiscale, nome, cognome, note_allergia, data_nascita, telefono, mail, contatto_emergenza)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (codice_fiscale) DO NOTHING;
                    """
                    run_query(q_pers, (cf, nome, cognome, note_allergie, data_nascita, ut_tel, ut_email, cont_emerg))
                    
                    # 2. Inserimento Cliente FF
                    q_cl = "INSERT INTO CLIENTE_FLOWFOREST (telefono, email) VALUES (%s, %s) RETURNING id_cliente;"
                    df_cl = run_query(q_cl, (ut_tel, ut_email))
                    if df_cl is not None:
                        new_id = int(df_cl.iloc[0]['id_cliente'])
                        q_pc = "INSERT INTO PERSONA_CLIENTE (id_cliente, codice_fiscale) VALUES (%s, %s);"
                        run_query(q_pc, (new_id, cf))
                        st.success(f"Cliente Privato registrato con successo! ID Cliente: {new_id}")
            
            else:
                p_iva = st.text_input("Partita IVA:")
                nome_azienda = st.text_input("Nome Azienda:")
                spec = st.text_input("Specializzazione Outdoor:")
                
                if st.button("Registra Azienda Partner"):
                    q_cl = "INSERT INTO CLIENTE_FLOWFOREST (telefono, email) VALUES (%s, %s) RETURNING id_cliente;"
                    df_cl = run_query(q_cl, (ut_tel, ut_email))
                    if df_cl is not None:
                        new_id = int(df_cl.iloc[0]['id_cliente'])
                        q_ap = """
                        INSERT INTO AZIENDA_PARTNER (id_cliente, p_iva, nome_azienda, specializzazione, email)
                        VALUES (%s, %s, %s, %s, %s);
                        """
                        run_query(q_ap, (new_id, p_iva, nome_azienda, spec, ut_email))
                        st.success(f"Azienda Partner registrata con successo! ID Partner: {new_id}")

        with tab_admin2:
            st.subheader("Gestione Inventario")
            
            inv_col1, inv_col2 = st.columns(2)
            with inv_col1:
                st.write("**Aggiungi Materiale**")
                mat_cod = st.text_input("Codice Articolo:")
                mat_nome = st.text_input("Nome:", key="inv_materiale_nome")
                mat_q = st.number_input("Quantità Iniziale:", min_value=0, value=0)
                mat_soglia = st.number_input("Soglia Riordino:", min_value=0, value=2)

                # La gerarchia MATERIALE è Totale ed Esclusiva: ogni materiale
                # è o Attrezzatura (riutilizzabile) o Consumabile (a esaurimento).
                mat_tipo = st.radio("Tipo di Materiale:", ["Attrezzatura", "Consumabile"], key="inv_materiale_tipo")

                if mat_tipo == "Attrezzatura":
                    attr_stato = st.text_input("Stato di Usura:", value="Nuovo", key="inv_attr_stato")
                    attr_data = st.date_input("Data Ultimo Utilizzo:", value=datetime.date.today(), key="inv_attr_data")
                else:
                    cons_scadenza = st.date_input(
                        "Data di Scadenza:",
                        value=datetime.date.today() + datetime.timedelta(days=365),
                        key="inv_cons_scadenza"
                    )
                    cons_allergeni = st.text_input("Allergeni Presenti:", placeholder="Es. glutine, lattosio", key="inv_cons_allergeni")

                if st.button("Inserisci Materiale"):
                    if not mat_cod or not mat_nome:
                        st.error("Codice articolo e nome sono obbligatori.")
                    else:
                        statements = [(
                            "INSERT INTO MATERIALE (codice_articolo, nome_materiale, quantita_inventario, soglia_minima_riordino) VALUES (%s, %s, %s, %s);",
                            (mat_cod, mat_nome, mat_q, mat_soglia)
                        )]
                        if mat_tipo == "Attrezzatura":
                            statements.append((
                                "INSERT INTO ATTREZZATURA (codice_articolo, stato_usura, data_ultimo_utilizzo) VALUES (%s, %s, %s);",
                                (mat_cod, attr_stato, attr_data)
                            ))
                        else:
                            statements.append((
                                "INSERT INTO CONSUMABILE (codice_articolo, data_scadenza, allergeni_presenti) VALUES (%s, %s, %s);",
                                (mat_cod, cons_scadenza, cons_allergeni)
                            ))
                        if run_transaction(statements):
                            st.success(f"Materiale inserito come {mat_tipo}!")
            
            with inv_col2:
                st.write("**Elimina Materiale**")
                del_cod = st.text_input("Codice Articolo da Rimuovere:")
                if st.button("Elimina Materiale"):
                    q_del = "DELETE FROM MATERIALE WHERE codice_articolo = %s;"
                    run_query(q_del, (del_cod,))
                    st.warning("Materiale rimosso dall'inventario.")
                    
            st.write("---")
            st.write("**Inventario Attuale**")
            df_inv = run_query("SELECT * FROM MATERIALE;")
            if df_inv is not None:
                st.dataframe(df_inv, use_container_width=True)

            # =================================================================
            # OP.G2 - Gestione Ordini al Fornitore (ORDINE + DETTAGLIO_ORDINE)
            # =================================================================
            st.write("---")
            st.subheader("📥 Registra un Ordine al Fornitore")
            st.write("Crea un ordine di rifornimento consumabili, con controllo degli allergeni.")

            # Elenco fornitori per la selezione
            df_forn = run_query("SELECT p_iva, ragione_sociale FROM FORNITORE ORDER BY ragione_sociale;")
            # Elenco consumabili ordinabili (solo materiali che sono consumabili)
            q_consumabili = """
            SELECT C.codice_articolo, M.nome_materiale, C.allergeni_presenti
            FROM CONSUMABILE C
            JOIN MATERIALE M ON C.codice_articolo = M.codice_articolo
            ORDER BY M.nome_materiale;
            """
            df_cons = run_query(q_consumabili)

            if df_forn is None or df_forn.empty:
                st.info("Nessun fornitore presente. Registra prima un fornitore per poter creare ordini.")
            elif df_cons is None or df_cons.empty:
                st.info("Nessun consumabile in inventario. Aggiungi consumabili per poterli ordinare.")
            else:
                ord_num = st.text_input("Numero Ordine:", placeholder="Es. ORD-2026-001", key="ord_num")
                ord_stato = st.selectbox("Stato Consegna:", ["In Elaborazione", "Spedito", "Consegnato"], key="ord_stato")

                # Mappa "nome (codice)" -> codice per la selezione fornitore e consumabili
                forn_options = {f"{r['ragione_sociale']} ({r['p_iva']})": r['p_iva'] for _, r in df_forn.iterrows()}
                ord_forn_label = st.selectbox("Fornitore:", list(forn_options.keys()), key="ord_forn")
                ord_forn_piva = forn_options[ord_forn_label]

                cons_options = {f"{r['nome_materiale']} ({r['codice_articolo']})": r['codice_articolo'] for _, r in df_cons.iterrows()}
                ord_articoli_labels = st.multiselect("Consumabili da ordinare:", list(cons_options.keys()), key="ord_articoli")

                # Quantità e importo per riga
                righe = []
                for label in ord_articoli_labels:
                    q = st.number_input(f"Quantità - {label}", min_value=1, value=1, key=f"ord_q_{label}")
                    righe.append((cons_options[label], q))

                ord_importo = st.number_input("Importo Totale Ordine (€):", min_value=0.0, value=0.0, key="ord_importo")

                # Controllo allergeni: mostra gli allergeni dei consumabili selezionati
                if ord_articoli_labels:
                    allergeni_map = {r['codice_articolo']: r['allergeni_presenti'] for _, r in df_cons.iterrows()}
                    allergeni_presenti = [
                        f"{label}: {allergeni_map[cons_options[label]]}"
                        for label in ord_articoli_labels
                        if allergeni_map[cons_options[label]]
                    ]
                    if allergeni_presenti:
                        st.warning("⚠️ Attenzione allergeni nei consumabili ordinati:\n\n" + "\n\n".join(allergeni_presenti))

                if st.button("Registra Ordine"):
                    if not ord_num:
                        st.error("Inserisci il numero d'ordine.")
                    elif not righe:
                        st.error("Seleziona almeno un consumabile da ordinare (un ordine deve contenere almeno un articolo).")
                    else:
                        # Ordine + dettagli in un'unica transazione atomica
                        statements = [(
                            "INSERT INTO ORDINE (n_ordine, data_ordine, importo_totale, stato_consegna, p_iva_fornitore) VALUES (%s, CURRENT_DATE, %s, %s, %s);",
                            (ord_num, ord_importo, ord_stato, ord_forn_piva)
                        )]
                        for cod_art, qta in righe:
                            statements.append((
                                "INSERT INTO DETTAGLIO_ORDINE (n_ordine, codice_articolo, quantita) VALUES (%s, %s, %s);",
                                (ord_num, cod_art, qta)
                            ))
                        if run_transaction(statements):
                            st.success(f"Ordine {ord_num} registrato con {len(righe)} righe! 📦")

        with tab_admin3:
            st.subheader("Crea un Nuovo Evento")
            ev_tipo = st.selectbox("Tipologia Evento:", ["Laboratorio Interno (B2C)", "Evento Partner (B2B2C)"])
            
            ev_start = st.text_input("Inizio (YYYY-MM-DD HH:MM:SS):", value="2026-07-15 09:00:00")
            ev_end = st.text_input("Fine (YYYY-MM-DD HH:MM:SS):", value="2026-07-15 13:00:00")
            ev_max = st.number_input("Partecipanti Max:", min_value=1, value=20)
            ev_costo = st.number_input("Costo Biglietto (€):", min_value=0.0, value=30.00)
            ev_area = st.text_input("Nome Area Bosco:", value="Area Nord")
            
            if ev_tipo == "Laboratorio Interno (B2C)":
                lab_cod = st.text_input("Codice Univoco Laboratorio:")
                lab_titolo = st.text_input("Titolo Laboratorio:")
                lab_desc = st.text_area("Descrizione:")
                lab_prot = st.text_input("Protocollo Operativo (es. Lavoro Manuale):")

                # Selezione del modulo didattico da elenco (evita di dover conoscere l'id numerico)
                df_moduli = run_query("SELECT id_modulo, nome FROM MODULO_DIDATTICO ORDER BY nome;")
                if df_moduli is not None and not df_moduli.empty:
                    modulo_options = {f"{r['nome']} (ID {r['id_modulo']})": int(r['id_modulo']) for _, r in df_moduli.iterrows()}
                    lab_modulo_label = st.selectbox("Modulo Didattico Associato:", list(modulo_options.keys()))
                    lab_modulo = modulo_options[lab_modulo_label]
                else:
                    st.warning("Nessun modulo didattico presente: creane uno prima di pianificare un laboratorio.")
                    lab_modulo = None

                if st.button("Pianifica Laboratorio"):
                    if lab_modulo is None:
                        st.error("Impossibile creare il laboratorio senza un modulo didattico.")
                    else:
                        q_ev = "INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max, costo_biglietto, nome_area) VALUES (%s, %s, %s, %s, %s) RETURNING id_evento;"
                        df_ev = run_query(q_ev, (ev_start, ev_end, ev_max, ev_costo, ev_area))
                        if df_ev is not None:
                            new_ev_id = int(df_ev.iloc[0]['id_evento'])
                            q_lab = "INSERT INTO LABORATORIO (id_evento, codice_lab, titolo, descrizione, protocollo_op, id_modulo) VALUES (%s, %s, %s, %s, %s, %s);"
                            run_query(q_lab, (new_ev_id, lab_cod, lab_titolo, lab_desc, lab_prot, lab_modulo))
                            st.success(f"Laboratorio Interno Creato! ID Evento: {new_ev_id}")

            else:
                part_titolo = st.text_input("Titolo dell'Evento Partner:")

                # Selezione dell'azienda partner da elenco.
                # NB: EVENTO_PARTNER.id_partner referenzia AZIENDA_PARTNER.id_cliente (che è la PK).
                df_partner = run_query("SELECT id_cliente, nome_azienda, p_iva FROM AZIENDA_PARTNER ORDER BY nome_azienda;")
                if df_partner is not None and not df_partner.empty:
                    partner_options = {f"{r['nome_azienda']} - P.IVA {r['p_iva']} (id_cliente {r['id_cliente']})": int(r['id_cliente']) for _, r in df_partner.iterrows()}
                    part_label = st.selectbox("Azienda Partner Organizzatrice:", list(partner_options.keys()))
                    part_id = partner_options[part_label]
                else:
                    st.warning("Nessuna azienda partner registrata: registrane una nella tab 'Registrazione Utenti'.")
                    part_id = None

                part_fee = st.slider("Percentuale di Fee per FlowForest (%):", 0.0, 100.0, 20.0)

                if st.button("Pianifica Evento Partner"):
                    if part_id is None:
                        st.error("Impossibile creare l'evento senza un'azienda partner.")
                    else:
                        q_ev = "INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max, costo_biglietto, nome_area) VALUES (%s, %s, %s, %s, %s) RETURNING id_evento;"
                        df_ev = run_query(q_ev, (ev_start, ev_end, ev_max, ev_costo, ev_area))
                        if df_ev is not None:
                            new_ev_id = int(df_ev.iloc[0]['id_evento'])
                            q_part = "INSERT INTO EVENTO_PARTNER (id_evento, titolo, id_partner, fee_percentuale) VALUES (%s, %s, %s, %s);"
                            run_query(q_part, (new_ev_id, part_titolo, part_id, part_fee))
                            st.success(f"Evento Partner Creato! ID Evento: {new_ev_id}")

        with tab_admin4:
            st.subheader("Report Finanziari e Analisi")
            
            st.write("#### 1. Spesa Media Annua dei Clienti")
            q_spesa_media = """
            SELECT C.id_cliente, C.email,
                   COALESCE(SUM(BP.prezzo_pagato), 0) AS spesa_totale,
                   COUNT(DISTINCT EXTRACT(YEAR FROM BP.data_emissione)) AS anni_attivi,
                   COALESCE(SUM(BP.prezzo_pagato) / NULLIF(COUNT(DISTINCT EXTRACT(YEAR FROM BP.data_emissione)), 0), 0) AS spesa_media_annua
            FROM CLIENTE_FLOWFOREST C
            LEFT JOIN PERSONA_CLIENTE PC ON C.id_cliente = PC.id_cliente
            LEFT JOIN BIGLIETTO_PERSONA BP ON PC.codice_fiscale = BP.codice_fiscale AND BP.p_iva_azienda IS NULL
            GROUP BY C.id_cliente, C.email
            ORDER BY spesa_media_annua DESC;
            """
            df_spesa = run_query(q_spesa_media)
            if df_spesa is not None:
                st.dataframe(df_spesa)
                
            st.write("#### 2. Miglior Partner dell'Anno Solare (Fee Generate)")
            ricerca_anno = st.number_input("Seleziona Anno:", value=2026)
            q_best_partner = """
            SELECT AP.id_cliente, AP.nome_azienda, AP.email,
                   SUM(E.costo_biglietto * (SELECT COUNT(*) FROM BIGLIETTO_PERSONA B WHERE B.id_evento = E.id_evento) * (EP.fee_percentuale / 100)) AS ricavi_fee_totali
            FROM AZIENDA_PARTNER AP
            JOIN EVENTO_PARTNER EP ON AP.id_cliente = EP.id_partner
            JOIN EVENTO E ON EP.id_evento = E.id_evento
            WHERE EXTRACT(YEAR FROM E.data_inizio) = %s
            GROUP BY AP.id_cliente, AP.nome_azienda, AP.email
            ORDER BY ricavi_fee_totali DESC
            LIMIT 1;
            """
            df_partner = run_query(q_best_partner, (ricerca_anno,))
            if df_partner is not None and not df_partner.empty:
                st.success(f"Il miglior partner del {ricerca_anno} è **{df_partner.iloc[0]['nome_azienda']}** con ricavi da fee di **€{df_partner.iloc[0]['ricavi_fee_totali']:.2f}**")
                st.dataframe(df_partner)
            else:
                st.info("Nessun ricavo da fee registrato per questo anno solare.")
                
            st.write("#### 3. Fatturato Dettagliato per Evento")
            q_fatt_eventi = """
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
            """
            df_fatt = run_query(q_fatt_eventi)
            if df_fatt is not None:
                st.dataframe(df_fatt)

        with tab_admin5:
            st.subheader("Modifica Elementi Laboratorio (Area Formatore)")
            
            lab_mod_id = st.number_input("ID Evento del Laboratorio da Modificare:", min_value=1)
            
            if lab_mod_id:
                # Carica i dati attuali
                q_get_lab = "SELECT * FROM LABORATORIO WHERE id_evento = %s;"
                df_curr = run_query(q_get_lab, (lab_mod_id,))
                
                if df_curr is not None and not df_curr.empty:
                    st.info(f"Modifica del Laboratorio: {df_curr.iloc[0]['titolo']}")
                    new_titolo = st.text_input("Nuovo Titolo:", value=df_curr.iloc[0]['titolo'])
                    new_desc = st.text_area("Nuova Descrizione:", value=df_curr.iloc[0]['descrizione'])
                    new_prot = st.text_input("Nuovo Protocollo:", value=df_curr.iloc[0]['protocollo_op'])
                    
                    if st.button("Salva Modifiche"):
                        q_up = "UPDATE LABORATORIO SET titolo = %s, descrizione = %s, protocollo_op = %s WHERE id_evento = %s;"
                        run_query(q_up, (new_titolo, new_desc, new_prot, lab_mod_id))
                        st.success("Modifiche salvate con successo! 🌳")
                else:
                    st.warning("Nessun laboratorio interno trovato con questo ID Evento.")

        with tab_admin6:
            st.subheader("💬 Feedback Ricevuti dai Partecipanti")
            st.write("Elenco di tutti i feedback inviati dai clienti al termine dei laboratori.")
            
            q_feedbacks = """
            SELECT F.id_feedback, F.voto, F.commento, F.data_compilazione, F.cod_seriale,
                   COALESCE(L.titolo, EP.titolo) AS nome_evento,
                   P.nome, P.cognome
            FROM FEEDBACK F
            JOIN BIGLIETTO_PERSONA BP ON F.cod_seriale = BP.cod_seriale
            JOIN EVENTO E ON BP.id_evento = E.id_evento
            LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
            LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
            JOIN PERSONA P ON BP.codice_fiscale = P.codice_fiscale
            ORDER BY F.data_compilazione DESC;
            """
            df_feedbacks = run_query(q_feedbacks)
            if df_feedbacks is not None:
                if df_feedbacks.empty:
                    st.info("Nessun feedback registrato al momento.")
                else:
                    # Metriche riassuntive
                    avg_voto = float(df_feedbacks['voto'].mean())
                    col_met1, col_met2 = st.columns(2)
                    col_met1.metric("Voto Medio del Bosco", f"⭐️ {avg_voto:.2f} / 5.00")
                    col_met2.metric("Feedback Ricevuti", f"💬 {len(df_feedbacks)}")
                    
                    st.dataframe(df_feedbacks, use_container_width=True)

        with tab_admin7:
            st.subheader("📋 Registri Generali del Database")
            st.write("Consulta i registri interni e le anagrafiche statiche caricate nel sistema.")
            
            registro_selezionato = st.selectbox(
                "Seleziona il Registro da Visualizzare:",
                [
                    "Organico & Staff (Dipendenti)",
                    "Aree & Strutture del Bosco",
                    "Didattica (Moduli Formativi)",
                    "Anagrafica Persone & Clienti B2C",
                    "Aziende Clienti (B2B) & Partner (B2B2C)",
                    "Ordini di Acquisto & Fornitori"
                ]
            )
            
            st.write("---")
            
            if registro_selezionato == "Organico & Staff (Dipendenti)":
                st.write("#### Risorse Umane e Competenze Operative")
                q_staff = """
                SELECT RU.id_dipendente, P.nome, P.cognome, RU.iban, RU.data_assunzione, RU.ruolo AS ruolo_principale,
                       COALESCE(F.certificazioni_attive, 'No') AS formatore,
                       COALESCE(A.mansione, 'No') AS amministrativo,
                       COALESCE(O.mansione, 'No') AS operaio
                FROM RISORSA_UMANA RU
                JOIN PERSONA P ON RU.codice_fiscale = P.codice_fiscale
                LEFT JOIN FORMATORE F ON RU.id_dipendente = F.id_dipendente
                LEFT JOIN AMMINISTRATIVO A ON RU.id_dipendente = A.id_dipendente
                LEFT JOIN OPERAIO O ON RU.id_dipendente = O.id_dipendente;
                """
                df_staff = run_query(q_staff)
                if df_staff is not None:
                    st.dataframe(df_staff, use_container_width=True)
                    
            elif registro_selezionato == "Aree & Strutture del Bosco":
                st.write("#### Aree Mappate e relative Strutture Semi-Permanenti")
                col_area1, col_area2 = st.columns(2)
                with col_area1:
                    st.write("**Aree del Bosco**")
                    df_areas = run_query("SELECT * FROM AREA;")
                    if df_areas is not None:
                        st.dataframe(df_areas, use_container_width=True)
                with col_area2:
                    st.write("**Strutture Installate**")
                    df_structs = run_query("SELECT * FROM STRUTTURA;")
                    if df_structs is not None:
                        st.dataframe(df_structs, use_container_width=True)
                        
            elif registro_selezionato == "Didattica (Moduli Formativi)":
                st.write("#### Moduli Didattici Disponibili per i Laboratori")
                df_modules = run_query("SELECT * FROM MODULO_DIDATTICO;")
                if df_modules is not None:
                    st.dataframe(df_modules, use_container_width=True)
                    
            elif registro_selezionato == "Anagrafica Persone & Clienti B2C":
                st.write("#### Persone Fisiche Registrate e Collegamento Clienti")
                q_people = """
                SELECT P.codice_fiscale, P.nome, P.cognome, P.data_nascita, P.telefono, P.mail, 
                       P.note_allergia, P.contatto_emergenza, PC.id_cliente
                FROM PERSONA P
                LEFT JOIN PERSONA_CLIENTE PC ON P.codice_fiscale = PC.codice_fiscale;
                """
                df_people = run_query(q_people)
                if df_people is not None:
                    st.dataframe(df_people, use_container_width=True)
                    
            elif registro_selezionato == "Aziende Clienti (B2B) & Partner (B2B2C)":
                st.write("#### Aziende Sponsor B2B (Fatturazione Biglietti Dipendenti)")
                df_b2b = run_query("SELECT * FROM AZIENDA_CLIENTE;")
                if df_b2b is not None:
                    st.dataframe(df_b2b, use_container_width=True)
                
                st.write("#### Aziende Partner B2B2C (Corsi Esterni con Fee)")
                df_partners = run_query("SELECT * FROM AZIENDA_PARTNER;")
                if df_partners is not None:
                    st.dataframe(df_partners, use_container_width=True)
                    
            elif registro_selezionato == "Ordini di Acquisto & Fornitori":
                st.write("#### Fornitori di Logistica e Catering")
                df_prov = run_query("SELECT * FROM FORNITORE;")
                if df_prov is not None:
                    st.dataframe(df_prov, use_container_width=True)
                    
                st.write("#### Storico degli Ordini di Acquisto Consumabili")
                q_orders = """
                SELECT O.n_ordine, O.data_ordine, O.importo_totale, O.stato_consegna, O.p_iva_fornitore, F.ragione_sociale
                FROM ORDINE O
                JOIN FORNITORE F ON O.p_iva_fornitore = F.p_iva;
                """
                df_orders = run_query(q_orders)
                if df_orders is not None:
                    st.dataframe(df_orders, use_container_width=True)
