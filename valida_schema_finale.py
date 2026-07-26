"""Valida database/schema.sql in uno schema PostgreSQL temporaneo.

La validazione viene eseguita in una transazione che termina sempre con
ROLLBACK: il database utilizzato dall'applicazione non viene modificato.
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
SCHEMA_FILE = ROOT / "database" / "schema.sql"

if not SCHEMA_FILE.exists():
    raise SystemExit(f"File non trovato: {SCHEMA_FILE}")

load_dotenv(ROOT / ".env")

settings = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT", "5432"),
    "sslmode": "require",
}

missing = [
    key
    for key in ("host", "database", "user", "password")
    if not settings[key]
]
if missing:
    raise SystemExit(
        "Variabili mancanti nel file .env: " + ", ".join(missing)
    )

temporary_schema = "flowforest_validation_" + uuid.uuid4().hex[:8]
quoted_schema = '"' + temporary_schema.replace('"', '""') + '"'

ddl = SCHEMA_FILE.read_text(encoding="utf-8")
ddl = ddl.replace("\nBEGIN;\n", "\n")
ddl = ddl.replace("\nCOMMIT;\n", "\n")
ddl = ddl.replace(
    "CREATE SCHEMA IF NOT EXISTS public;",
    f"CREATE SCHEMA {quoted_schema};",
)
ddl = ddl.replace(
    "SET search_path TO public;",
    f"SET search_path TO {quoted_schema};",
)
ddl = ddl.replace("public.", f"{quoted_schema}.")

conn = psycopg2.connect(**settings)
cur = conn.cursor()

try:
    cur.execute(ddl)

    cur.execute(
        """
        SELECT COUNT(*)
        FROM information_schema.tables
        WHERE table_schema = %s
          AND table_type = 'BASE TABLE';
        """,
        (temporary_schema,),
    )
    table_count = cur.fetchone()[0]

    cur.execute(
        """
        SELECT COUNT(*)
        FROM pg_constraint con
        JOIN pg_namespace n ON n.oid = con.connamespace
        WHERE n.nspname = %s
          AND con.contype IN ('p', 'u', 'c', 'x', 'f');
        """,
        (temporary_schema,),
    )
    constraint_count = cur.fetchone()[0]

    if table_count != 26:
        raise RuntimeError(
            f"Attese 26 tabelle, trovate {table_count}."
        )

    print("Validazione completata con successo.")
    print(f"Tabelle ricreate: {table_count}")
    print(f"Vincoli ricreati: {constraint_count}")
    print("Nessuna modifica permanente eseguita (ROLLBACK).")

finally:
    conn.rollback()
    cur.close()
    conn.close()
