import streamlit as st
import pandas as pd
import psycopg2
import datetime

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

# Inizializzazione session state per la connessione al database
if 'db_conn_info' not in st.session_state:
    st.session_state['db_conn_info'] = None
if 'db_connected' not in st.session_state:
    st.session_state['db_connected'] = False

# Sidebar per la connessione al DB (Indispensabile per rendere portabile il progetto)
st.sidebar.image("logo flow.jpeg", use_container_width=True)
st.sidebar.title("Configurazione DB")
st.sidebar.markdown("Inserisci le credenziali del database PostgreSQL locale per iniziare.")

db_host = st.sidebar.text_input("Host", value="ep-twilight-sky-asb5geuz.c-4.eu-central-1.aws.neon.tech")
db_name = st.sidebar.text_input("Database Name", value="neondb")
db_user = st.sidebar.text_input("User", value="neondb_owner")
db_password = st.sidebar.text_input("Password", type="password", value="npg_p2cb0yBPwkfi")
db_port = st.sidebar.text_input("Port", value="5432")

def get_connection():
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port
        )
        return conn
    except Exception as e:
        st.sidebar.error(f"Errore di connessione: {e}")
        return None

if st.sidebar.button("Connetti al Database"):
    conn = get_connection()
    if conn:
        st.session_state['db_conn_info'] = {
            'host': db_host,
            'database': db_name,
            'user': db_user,
            'password': db_password,
            'port': db_port
        }
        st.session_state['db_connected'] = True
        st.sidebar.success("Connesso con successo! 🎉")
        conn.close()

# Navbar principale per le aree applicative
st.title("🌳 FlowForest Database Management Portal")
st.markdown("---")

if not st.session_state['db_connected']:
    st.info("👈 Per favore, configura le credenziali di PostgreSQL nella sidebar a sinistra e fai clic su **Connetti al Database** per abilitare il portale.")
    st.image("panorama flow.jpeg", use_container_width=True, caption="Il bosco di FlowForest")
else:
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

    # Selezione dell'Area Applicativa
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
            st.subheader("Cerca il tuo Biglietto")
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
                
                if st.button("Inserisci Materiale"):
                    q_mat = "INSERT INTO MATERIALE (codice_articolo, nome_materiale, quantita_inventario, soglia_minima_riordino) VALUES (%s, %s, %s, %s);"
                    run_query(q_mat, (mat_cod, mat_nome, mat_q, mat_soglia))
                    st.success("Materiale inserito!")
            
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
                lab_modulo = st.number_input("ID Modulo Didattico Associato:", min_value=1, value=1)
                
                if st.button("Pianifica Laboratorio"):
                    q_ev = "INSERT INTO EVENTO (data_inizio, data_fine, partecipanti_max, costo_biglietto, nome_area) VALUES (%s, %s, %s, %s, %s) RETURNING id_evento;"
                    df_ev = run_query(q_ev, (ev_start, ev_end, ev_max, ev_costo, ev_area))
                    if df_ev is not None:
                        new_ev_id = int(df_ev.iloc[0]['id_evento'])
                        q_lab = "INSERT INTO LABORATORIO (id_evento, codice_lab, titolo, descrizione, protocollo_op, id_modulo) VALUES (%s, %s, %s, %s, %s, %s);"
                        run_query(q_lab, (new_ev_id, lab_cod, lab_titolo, lab_desc, lab_prot, lab_modulo))
                        st.success(f"Laboratorio Interno Creato! ID Evento: {new_ev_id}")
            
            else:
                part_titolo = st.text_input("Titolo dell'Evento Partner:")
                part_id = st.number_input("ID Partner (Cliente B2B):", min_value=1)
                part_fee = st.slider("Percentuale di Fee per FlowForest (%):", 0.0, 100.0, 20.0)
                
                if st.button("Pianifica Evento Partner"):
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
