"""
Script una tantum: converte le password in chiaro presenti in PERSONA
nel formato hash bcrypt. Le righe già hashate (prefisso $2a$/$2b$/$2y$)
vengono saltate. Da eseguire una sola volta dopo il deploy della modifica
che introduce l'hashing in app.py.

Uso:
    python migrate_password_hash.py           # esegue la migrazione
    python migrate_password_hash.py --dry-run # mostra solo cosa farebbe
"""
import os
import sys
import bcrypt
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_DEFAULTS = {
    'host': os.environ.get('DB_HOST', ''),
    'database': os.environ.get('DB_NAME', ''),
    'user': os.environ.get('DB_USER', ''),
    'password': os.environ.get('DB_PASSWORD', ''),
    'port': os.environ.get('DB_PORT', '5432'),
    'sslmode': 'require',
}


def is_bcrypt_hash(value):
    return isinstance(value, str) and value.startswith(("$2a$", "$2b$", "$2y$"))


def main():
    dry_run = "--dry-run" in sys.argv

    conn = psycopg2.connect(**DB_DEFAULTS)
    try:
        cur = conn.cursor()
        cur.execute("SELECT codice_fiscale, mail, password FROM PERSONA")
        rows = cur.fetchall()

        da_migrare = [r for r in rows if not is_bcrypt_hash(r[2])]

        print(f"Totale persone: {len(rows)}")
        print(f"Password già hashate: {len(rows) - len(da_migrare)}")
        print(f"Password da migrare: {len(da_migrare)}")

        if not da_migrare:
            print("Niente da fare.")
            return

        for codice_fiscale, mail, password_chiaro in da_migrare:
            nuovo_hash = bcrypt.hashpw(
                password_chiaro.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            print(f"  {mail} ({codice_fiscale}): {'[dry-run] ' if dry_run else ''}migrata")
            if not dry_run:
                cur.execute(
                    "UPDATE PERSONA SET password = %s WHERE codice_fiscale = %s",
                    (nuovo_hash, codice_fiscale),
                )

        if dry_run:
            conn.rollback()
            print("\nDry run: nessuna modifica salvata.")
        else:
            conn.commit()
            print(f"\n{len(da_migrare)} password migrate e salvate.")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()
