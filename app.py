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
            SELECT p.password, p.codice_fiscale, p.nome, p.cognome,
                   COALESCE(ru.mansione, 'Staff') AS mansione
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
            conn.rollback()
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

    def create_event_with_relations(
        event_params,
        subtype_query,
        subtype_params,
        area_names,
        module_ids=None,
    ):
        """Crea Evento, sottotipo e associazioni in un'unica transazione."""
        conn = psycopg2.connect(**st.session_state['db_conn_info'])
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max)
                VALUES (%s, %s, %s)
                RETURNING id_evento;
                """,
                event_params,
            )
            event_id = cur.fetchone()[0]

            cur.execute(subtype_query, (event_id, *subtype_params))
            cur.executemany(
                "INSERT INTO EVENTO_AREA (id_evento, nome_area) VALUES (%s, %s);",
                [(event_id, area_name) for area_name in area_names],
            )

            if module_ids:
                cur.executemany(
                    "INSERT INTO LABORATORIO_MODULO (id_evento, id_modulo) VALUES (%s, %s);",
                    [(event_id, module_id) for module_id in module_ids],
                )

            conn.commit()
            return event_id
        except Exception as e:
            conn.rollback()
            st.error(f"Errore durante la creazione dell'evento: {e}")
            return None
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
        
        tab1, tab2, tab3 = st.tabs(["🎫 Ricerca Biglietto & Materiali", "📅 Laboratori Disponibili", "✍️ Compila Feedback"])
        
        with tab1:
            st.subheader("I tuoi Biglietti")

            # Se l'utente è un cliente autenticato via email, mostra automaticamente
            # tutti i biglietti collegati alla sua anagrafica (PERSONA.mail)
            if st.session_state.get('user_email'):
                q_my_tickets = """
                SELECT B.cod_seriale, B.data_emissione, B.prezzo_pagato, B.richiesta_allergie,
                       E.data_inizio, E.data_fine,
                       L.codice_lab, L.titolo AS nome_evento,
                       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
                FROM BIGLIETTO_PERSONA B
                JOIN PERSONA P ON B.codice_fiscale = P.codice_fiscale
                JOIN EVENTO E ON B.id_evento = E.id_evento
                JOIN LABORATORIO L ON E.id_evento = L.id_evento
                JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
                WHERE P.mail = %s
                GROUP BY B.cod_seriale, B.data_emissione, B.prezzo_pagato,
                         B.richiesta_allergie, E.data_inizio, E.data_fine,
                         L.codice_lab, L.titolo
                ORDER BY E.data_inizio DESC;
                """
                df_my_tickets = run_query(q_my_tickets, (st.session_state['user_email'],))

                if df_my_tickets is not None and not df_my_tickets.empty:
                    st.dataframe(df_my_tickets, use_container_width=True)

                    st.subheader("🎒 Materiali richiesti per i tuoi Laboratori:")
                    q_my_equip = """
                    SELECT DISTINCT L.titolo AS nome_evento,
                           M.nome_materiale, IM.quantita_impiegata
                    FROM BIGLIETTO_PERSONA B
                    JOIN PERSONA P ON B.codice_fiscale = P.codice_fiscale
                    JOIN EVENTO E ON B.id_evento = E.id_evento
                    JOIN LABORATORIO L ON E.id_evento = L.id_evento
                    JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
                    JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
                    WHERE P.mail = %s
                    ORDER BY L.titolo, M.nome_materiale;
                    """
                    df_my_equip = run_query(q_my_equip, (st.session_state['user_email'],))
                    if df_my_equip is not None and not df_my_equip.empty:
                        st.dataframe(df_my_equip, use_container_width=True)
                    else:
                        st.info("Nessun materiale particolare richiesto per i tuoi Laboratori.")
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
                       L.codice_lab, L.titolo AS nome_evento,
                       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
                FROM BIGLIETTO_PERSONA B
                JOIN EVENTO E ON B.id_evento = E.id_evento
                JOIN LABORATORIO L ON E.id_evento = L.id_evento
                JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
                WHERE B.cod_seriale = %s
                GROUP BY B.cod_seriale, B.data_emissione, B.prezzo_pagato,
                         B.richiesta_allergie, E.data_inizio, E.data_fine,
                         L.codice_lab, L.titolo;
                """
                df_ticket = run_query(q_ticket, (ticket_serial,))

                if df_ticket is not None and not df_ticket.empty:
                    st.success("Biglietto Trovato!")
                    st.dataframe(df_ticket)

                    # 2. Ricerca Materiali Necessari
                    st.subheader("🎒 Materiali richiesti per il Laboratorio:")
                    q_equip = """
                    SELECT M.codice_articolo, M.nome_materiale, IM.quantita_impiegata
                    FROM BIGLIETTO_PERSONA B
                    JOIN IMPIEGO_MATERIALE IM ON B.id_evento = IM.id_evento
                    JOIN MATERIALE M ON IM.codice_articolo = M.codice_articolo
                    WHERE B.cod_seriale = %s
                    ORDER BY M.nome_materiale;
                    """
                    df_equip = run_query(q_equip, (ticket_serial,))
                    if df_equip is not None and not df_equip.empty:
                        st.dataframe(df_equip)
                    else:
                        st.info("Nessun materiale particolare richiesto per questo Laboratorio.")
                else:
                    st.warning("Nessun biglietto trovato con questo codice seriale.")

        with tab2:
            st.subheader("Esplora i Laboratori in Programma")
            q_events = """
            SELECT E.id_evento, L.codice_lab, L.titolo,
                   E.data_inizio, E.data_fine, E.partecipanti_max,
                   L.costo_biglietto,
                   STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
            FROM EVENTO E
            JOIN LABORATORIO L ON E.id_evento = L.id_evento
            JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
            WHERE E.data_inizio > CURRENT_TIMESTAMP
            GROUP BY E.id_evento, L.codice_lab, L.titolo, E.data_inizio,
                     E.data_fine, E.partecipanti_max, L.costo_biglietto
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
                    q_check_ticket = """
                    SELECT 1
                    FROM BIGLIETTO_PERSONA
                    WHERE cod_seriale = %s
                      AND codice_fiscale = %s;
                    """
                    df_check = run_query(
                        q_check_ticket,
                        (fb_serial, st.session_state['user_cf']),
                    )
                    if df_check is not None and not df_check.empty:
                        q_insert_fb = """
                        INSERT INTO FEEDBACK (voto, commento, data_compilazione, cod_seriale)
                        VALUES (%s, %s, CURRENT_DATE, %s);
                        """
                        if run_transaction([
                            (q_insert_fb, (fb_voto, fb_commento, fb_serial))
                        ]):
                            st.success("Feedback inviato con successo! Grazie per la collaborazione. 🌳")
                    else:
                        st.error("Il codice seriale non appartiene all'utente autenticato.")

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

            ut_email = st.text_input("Email:")

            if ut_tipo == "Cliente Privato (B2C)":
                cf = st.text_input("Codice Fiscale:")
                nome = st.text_input("Nome:")
                cognome = st.text_input("Cognome:")
                ut_tel = st.text_input("Telefono:")
                ut_password = st.text_input(
                    "Password iniziale:",
                    type="password",
                    help="Nel prototipo viene salvata in chiaro. Utilizzare solo credenziali dimostrative.",
                )
                data_nascita = st.date_input(
                    "Data di Nascita:",
                    value=datetime.date(2000, 1, 1),
                    min_value=datetime.date(1920, 1, 1),
                    max_value=datetime.date.today()
                )
                note_allergie = st.text_input("Allergie/Intolleranze:")
                cont_emerg = st.text_input("Contatto di Emergenza:")

                if st.button("Registra Cliente"):
                    if not all([cf, nome, cognome, ut_email, ut_password]):
                        st.error("Codice fiscale, nome, cognome, email e password sono obbligatori.")
                    else:
                        q_cliente = """
                        WITH nuova_persona AS (
                            INSERT INTO PERSONA
                                (codice_fiscale, nome, cognome, note_allergia,
                                 data_nascita, telefono, mail, password,
                                 contatto_emergenza)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING codice_fiscale
                        ),
                        nuovo_cliente AS (
                            INSERT INTO CLIENTE_FLOWFOREST (data_registrazione)
                            VALUES (CURRENT_DATE)
                            RETURNING id_cliente
                        )
                        INSERT INTO PERSONA_CLIENTE (id_cliente, codice_fiscale)
                        SELECT NC.id_cliente, NP.codice_fiscale
                        FROM nuovo_cliente NC
                        CROSS JOIN nuova_persona NP
                        RETURNING id_cliente;
                        """
                        df_cliente = run_query(
                            q_cliente,
                            (
                                cf, nome, cognome, note_allergie, data_nascita,
                                ut_tel, ut_email, ut_password, cont_emerg,
                            ),
                        )
                        if df_cliente is not None and not df_cliente.empty:
                            new_id = int(df_cliente.iloc[0]['id_cliente'])
                            st.success(f"Cliente Privato registrato con successo! ID Cliente: {new_id}")

            else:
                p_iva = st.text_input("Partita IVA:")
                nome_azienda = st.text_input("Nome Azienda:")
                spec = st.text_input("Specializzazione Outdoor:")

                if st.button("Registra Azienda Partner"):
                    if not all([p_iva, nome_azienda, ut_email]):
                        st.error("Partita IVA, nome azienda ed email sono obbligatori.")
                    else:
                        q_partner = """
                        WITH nuovo_cliente AS (
                            INSERT INTO CLIENTE_FLOWFOREST (data_registrazione)
                            VALUES (CURRENT_DATE)
                            RETURNING id_cliente
                        )
                        INSERT INTO AZIENDA_PARTNER
                            (id_cliente, p_iva, nome_azienda, specializzazione, email)
                        SELECT id_cliente, %s, %s, %s, %s
                        FROM nuovo_cliente
                        RETURNING id_cliente;
                        """
                        df_partner = run_query(
                            q_partner,
                            (p_iva, nome_azienda, spec, ut_email),
                        )
                        if df_partner is not None and not df_partner.empty:
                            new_id = int(df_partner.iloc[0]['id_cliente'])
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
                    if not del_cod:
                        st.error("Inserisci il codice del Materiale da rimuovere.")
                    else:
                        statements = [
                            (
                                "DELETE FROM ATTREZZATURA WHERE codice_articolo = %s;",
                                (del_cod,),
                            ),
                            (
                                "DELETE FROM CONSUMABILE WHERE codice_articolo = %s;",
                                (del_cod,),
                            ),
                            (
                                "DELETE FROM MATERIALE WHERE codice_articolo = %s;",
                                (del_cod,),
                            ),
                        ]
                        if run_transaction(statements):
                            st.success("Materiale rimosso dall'inventario.")
                    
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

            st.write("---")
            st.subheader("📋 Quantità ordinate e disponibilità dei Consumabili")
            q_order_details = """
            SELECT O.n_ordine,
                   O.data_ordine,
                   O.stato_consegna,
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
            ORDER BY O.data_ordine DESC, O.n_ordine, M.nome_materiale;
            """
            df_order_details = run_query(q_order_details)
            if df_order_details is not None:
                st.dataframe(df_order_details, use_container_width=True)

        with tab_admin3:
            st.subheader("Crea un Nuovo Evento")
            ev_tipo = st.selectbox("Tipologia Evento:", ["Laboratorio Interno (B2C)", "Evento Partner (B2B2C)"])

            ev_start = st.text_input("Inizio (YYYY-MM-DD HH:MM:SS):", value="2026-07-15 09:00:00")
            ev_end = st.text_input("Fine (YYYY-MM-DD HH:MM:SS):", value="2026-07-15 13:00:00")
            ev_max = st.number_input("Partecipanti Max:", min_value=1, value=20)

            df_aree = run_query("SELECT nome FROM AREA ORDER BY nome;")
            area_options = [] if df_aree is None else df_aree["nome"].tolist()
            ev_aree = st.multiselect(
                "Aree di svolgimento:",
                area_options,
                help="Ogni Evento deve svolgersi in almeno un'Area.",
            )

            if ev_tipo == "Laboratorio Interno (B2C)":
                lab_cod = st.text_input("Codice Univoco Laboratorio:")
                lab_titolo = st.text_input("Titolo Laboratorio:")
                lab_desc = st.text_area("Descrizione:")
                lab_prot = st.text_input("Protocollo Operativo (es. Lavoro Manuale):")
                ev_costo = st.number_input("Costo Biglietto (€):", min_value=0.0, value=30.00)

                # La relazione LABORATORIO_MODULO permette più moduli per Laboratorio.
                df_moduli = run_query("SELECT id_modulo, nome FROM MODULO_DIDATTICO ORDER BY nome;")
                if df_moduli is not None and not df_moduli.empty:
                    modulo_options = {f"{r['nome']} (ID {r['id_modulo']})": int(r['id_modulo']) for _, r in df_moduli.iterrows()}
                    lab_moduli_labels = st.multiselect(
                        "Moduli Didattici Associati:",
                        list(modulo_options.keys()),
                    )
                    lab_moduli = [modulo_options[label] for label in lab_moduli_labels]
                else:
                    st.warning("Nessun modulo didattico presente: creane uno prima di pianificare un laboratorio.")
                    lab_moduli = []

                if st.button("Pianifica Laboratorio"):
                    if not all([lab_cod, lab_titolo, ev_start, ev_end]):
                        st.error("Codice, titolo e date del Laboratorio sono obbligatori.")
                    elif not ev_aree:
                        st.error("Seleziona almeno un'Area.")
                    elif not lab_moduli:
                        st.error("Seleziona almeno un Modulo Didattico.")
                    else:
                        q_lab = """
                        INSERT INTO LABORATORIO
                            (id_evento, codice_lab, titolo, descrizione,
                             protocollo_op, costo_biglietto)
                        VALUES (%s, %s, %s, %s, %s, %s);
                        """
                        new_ev_id = create_event_with_relations(
                            (ev_start, ev_end, ev_max),
                            q_lab,
                            (lab_cod, lab_titolo, lab_desc, lab_prot, ev_costo),
                            ev_aree,
                            lab_moduli,
                        )
                        if new_ev_id is not None:
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

                if st.button("Pianifica Evento Partner"):
                    if not part_titolo:
                        st.error("Inserisci il titolo dell'Evento Partner.")
                    elif part_id is None:
                        st.error("Impossibile creare l'evento senza un'azienda partner.")
                    elif not ev_aree:
                        st.error("Seleziona almeno un'Area.")
                    else:
                        q_part = """
                        INSERT INTO EVENTO_PARTNER (id_evento, titolo, id_partner)
                        VALUES (%s, %s, %s);
                        """
                        new_ev_id = create_event_with_relations(
                            (ev_start, ev_end, ev_max),
                            q_part,
                            (part_titolo, part_id),
                            ev_aree,
                        )
                        if new_ev_id is not None:
                            st.success(f"Evento Partner Creato! ID Evento: {new_ev_id}")

        with tab_admin4:
            st.subheader("Report Finanziari e Analisi")

            st.write("#### 1. Spesa Media Annua dei Clienti")
            q_spesa_media = """
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
            """
            df_spesa = run_query(q_spesa_media)
            if df_spesa is not None:
                st.dataframe(df_spesa, use_container_width=True)

            st.write("#### 2. Partner per numero di Eventi organizzati")
            ricerca_anno = st.number_input("Seleziona Anno:", value=2026)
            q_best_partner = """
            SELECT AP.id_cliente, AP.nome_azienda, AP.email,
                   COUNT(E.id_evento) AS numero_eventi
            FROM AZIENDA_PARTNER AP
            LEFT JOIN EVENTO_PARTNER EP ON AP.id_cliente = EP.id_partner
            LEFT JOIN EVENTO E
              ON EP.id_evento = E.id_evento
             AND EXTRACT(YEAR FROM E.data_inizio) = %s
            GROUP BY AP.id_cliente, AP.nome_azienda, AP.email
            ORDER BY numero_eventi DESC, AP.nome_azienda;
            """
            df_partner = run_query(q_best_partner, (ricerca_anno,))
            if df_partner is not None and not df_partner.empty:
                if int(df_partner.iloc[0]["numero_eventi"]) > 0:
                    st.success(
                        f"Il partner con più Eventi nel {ricerca_anno} è "
                        f"**{df_partner.iloc[0]['nome_azienda']}**."
                    )
                else:
                    st.info(f"Nessun Evento Partner registrato per il {ricerca_anno}.")
                st.dataframe(df_partner, use_container_width=True)
            else:
                st.info("Nessuna Azienda Partner registrata.")

            st.write("#### 3. Fatturato dei Laboratori")
            q_fatt_eventi = """
            SELECT E.id_evento,
                   L.codice_lab,
                   L.titolo,
                   COUNT(B.cod_seriale) AS biglietti_venduti,
                   COALESCE(SUM(B.prezzo_pagato), 0) AS fatturato
            FROM EVENTO E
            JOIN LABORATORIO L ON E.id_evento = L.id_evento
            LEFT JOIN BIGLIETTO_PERSONA B ON E.id_evento = B.id_evento
            WHERE EXTRACT(YEAR FROM E.data_inizio) = %s
            GROUP BY E.id_evento, L.codice_lab, L.titolo
            ORDER BY fatturato DESC, L.titolo;
            """
            df_fatt = run_query(q_fatt_eventi, (ricerca_anno,))
            if df_fatt is not None:
                st.dataframe(df_fatt, use_container_width=True)

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
                    new_costo = st.number_input(
                        "Nuovo Costo Biglietto (€):",
                        min_value=0.0,
                        value=float(df_curr.iloc[0]['costo_biglietto']),
                    )

                    df_all_moduli = run_query(
                        "SELECT id_modulo, nome FROM MODULO_DIDATTICO ORDER BY nome;"
                    )
                    df_moduli_correnti = run_query(
                        """
                        SELECT id_modulo
                        FROM LABORATORIO_MODULO
                        WHERE id_evento = %s;
                        """,
                        (lab_mod_id,),
                    )

                    mod_options = {}
                    moduli_selezionati = []
                    if df_all_moduli is not None and not df_all_moduli.empty:
                        mod_options = {
                            f"{row['nome']} (ID {row['id_modulo']})": int(row['id_modulo'])
                            for _, row in df_all_moduli.iterrows()
                        }
                        current_ids = set()
                        if df_moduli_correnti is not None:
                            current_ids = {
                                int(value)
                                for value in df_moduli_correnti["id_modulo"].tolist()
                            }
                        default_labels = [
                            label
                            for label, module_id in mod_options.items()
                            if module_id in current_ids
                        ]
                        selected_labels = st.multiselect(
                            "Moduli Didattici:",
                            list(mod_options.keys()),
                            default=default_labels,
                        )
                        moduli_selezionati = [
                            mod_options[label] for label in selected_labels
                        ]
                    else:
                        st.warning("Non sono presenti Moduli Didattici associabili.")

                    if st.button("Salva Modifiche"):
                        if not moduli_selezionati:
                            st.error("Il Laboratorio deve prevedere almeno un Modulo Didattico.")
                        else:
                            statements = [
                                (
                                    """
                                    UPDATE LABORATORIO
                                    SET titolo = %s,
                                        descrizione = %s,
                                        protocollo_op = %s,
                                        costo_biglietto = %s
                                    WHERE id_evento = %s;
                                    """,
                                    (new_titolo, new_desc, new_prot, new_costo, lab_mod_id),
                                ),
                                (
                                    "DELETE FROM LABORATORIO_MODULO WHERE id_evento = %s;",
                                    (lab_mod_id,),
                                ),
                            ]
                            for module_id in moduli_selezionati:
                                statements.append(
                                    (
                                        """
                                        INSERT INTO LABORATORIO_MODULO (id_evento, id_modulo)
                                        VALUES (%s, %s);
                                        """,
                                        (lab_mod_id, module_id),
                                    )
                                )
                            if run_transaction(statements):
                                st.success("Modifiche salvate con successo! 🌳")
                else:
                    st.warning("Nessun laboratorio interno trovato con questo ID Evento.")

        with tab_admin6:
            st.subheader("💬 Feedback Ricevuti dai Partecipanti")
            st.write("Elenco di tutti i feedback inviati dai clienti al termine dei laboratori.")
            
            q_feedbacks = """
            SELECT F.id_feedback, F.voto, F.commento, F.data_compilazione, F.cod_seriale,
                   L.titolo AS nome_evento,
                   P.nome, P.cognome
            FROM FEEDBACK F
            JOIN BIGLIETTO_PERSONA BP ON F.cod_seriale = BP.cod_seriale
            JOIN EVENTO E ON BP.id_evento = E.id_evento
            JOIN LABORATORIO L ON E.id_evento = L.id_evento
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
                    "Storico degli Eventi",
                    "Ordini di Acquisto & Fornitori"
                ]
            )
            
            st.write("---")
            
            if registro_selezionato == "Organico & Staff (Dipendenti)":
                st.write("#### Risorse Umane e Competenze Operative")
                q_staff = """
                SELECT RU.id_dipendente,
                       P.nome,
                       P.cognome,
                       RU.iban,
                       RU.data_assunzione,
                       RU.mansione,
                       RU.livello_salariale,
                       F.certificazioni_attive,
                       CASE WHEN A.id_dipendente IS NOT NULL THEN 'Sì' ELSE 'No' END AS amministrativo,
                       CASE WHEN O.id_dipendente IS NOT NULL THEN 'Sì' ELSE 'No' END AS operaio
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
                
                st.write("#### Aziende Partner B2B2C")
                df_partners = run_query("SELECT * FROM AZIENDA_PARTNER;")
                if df_partners is not None:
                    st.dataframe(df_partners, use_container_width=True)

            elif registro_selezionato == "Storico degli Eventi":
                st.write("#### Eventi Conclusi")
                q_event_history = """
                SELECT E.id_evento,
                       COALESCE(L.titolo, EP.titolo) AS titolo,
                       CASE
                           WHEN L.id_evento IS NOT NULL THEN 'Laboratorio'
                           ELSE 'Evento Partner'
                       END AS tipologia,
                       E.data_inizio,
                       E.data_fine,
                       STRING_AGG(EA.nome_area, ', ' ORDER BY EA.nome_area) AS aree
                FROM EVENTO E
                LEFT JOIN LABORATORIO L ON E.id_evento = L.id_evento
                LEFT JOIN EVENTO_PARTNER EP ON E.id_evento = EP.id_evento
                JOIN EVENTO_AREA EA ON E.id_evento = EA.id_evento
                WHERE E.data_fine < CURRENT_TIMESTAMP
                GROUP BY E.id_evento, L.id_evento, L.titolo, EP.titolo,
                         E.data_inizio, E.data_fine
                ORDER BY E.data_inizio DESC;
                """
                df_event_history = run_query(q_event_history)
                if df_event_history is not None:
                    st.dataframe(df_event_history, use_container_width=True)

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
