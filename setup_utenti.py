"""
Script una tantum: crea la tabella UTENTE_APP su Neon (se non esiste) e vi
inserisce gli account iniziali con password hashate (bcrypt).

Uso:
    python setup_utenti.py

Richiede le variabili DB_HOST/DB_NAME/DB_USER/DB_PASSWORD/DB_PORT in .env.
Rieseguibile: se un utente esiste già, ne aggiorna solo la password.
"""
import os
import bcrypt
import psycopg2
from dotenv import load_dotenv

load_dotenv()

CONN_INFO = {
    'host': os.environ['DB_HOST'],
    'database': os.environ['DB_NAME'],
    'user': os.environ['DB_USER'],
    'password': os.environ['DB_PASSWORD'],
    'port': os.environ.get('DB_PORT', '5432'),
    'sslmode': 'require',
}

# Utenti iniziali: (identificativo, password_in_chiaro, ruolo, codice_fiscale)
# Cambia le password qui prima di eseguire, poi non serve più tenerle in chiaro da nessuna parte.
UTENTI_INIZIALI = [
    ("admin", "admin123", "admin", None),
    ("server", "server123", "server", None),
    ("cliente@email.com", "client123", "cliente", None),
]


def main():
    with open("schema_utente_app.sql", "r") as f:
        schema_sql = f.read()

    conn = psycopg2.connect(**CONN_INFO)
    cur = conn.cursor()
    try:
        cur.execute(schema_sql)

        for identificativo, password, ruolo, codice_fiscale in UTENTI_INIZIALI:
            password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            cur.execute(
                """
                INSERT INTO UTENTE_APP (identificativo, password_hash, ruolo, codice_fiscale)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (identificativo, ruolo)
                DO UPDATE SET password_hash = EXCLUDED.password_hash
                """,
                (identificativo, password_hash, ruolo, codice_fiscale),
            )
            print(f"OK: {identificativo} ({ruolo})")

        conn.commit()
        print("Setup completato.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
