"""Genera lo schema pubblico PostgreSQL finale in database/schema.sql.

Lo script legge le credenziali dal file .env usato da app.py e non esporta
né dati né credenziali.
"""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "database" / "schema.sql"


def quoted(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def qualified(name: str) -> str:
    return f'public.{quoted(name)}'


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

conn = psycopg2.connect(**settings)
cur = conn.cursor()

try:
    cur.execute(
        """
        SELECT sequencename,
               data_type,
               start_value,
               min_value,
               max_value,
               increment_by,
               cycle,
               cache_size
        FROM pg_sequences
        WHERE schemaname = 'public'
        ORDER BY sequencename;
        """
    )
    sequences = cur.fetchall()

    cur.execute(
        """
        SELECT c.relname AS table_name,
               a.attname AS column_name,
               pg_catalog.format_type(a.atttypid, a.atttypmod) AS data_type,
               a.attnotnull,
               pg_get_expr(ad.adbin, ad.adrelid) AS column_default
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a
          ON a.attrelid = c.oid
         AND a.attnum > 0
         AND NOT a.attisdropped
        LEFT JOIN pg_attrdef ad
          ON ad.adrelid = c.oid
         AND ad.adnum = a.attnum
        WHERE n.nspname = 'public'
          AND c.relkind IN ('r', 'p')
        ORDER BY c.relname, a.attnum;
        """
    )
    columns_by_table: dict[str, list[tuple[str, str, bool, str | None]]] = (
        defaultdict(list)
    )
    for table, column, data_type, not_null, default in cur.fetchall():
        columns_by_table[table].append(
            (column, data_type, not_null, default)
        )

    cur.execute(
        """
        SELECT c.relname AS table_name,
               con.conname,
               con.contype,
               pg_get_constraintdef(con.oid, true)
        FROM pg_constraint con
        JOIN pg_class c ON c.oid = con.conrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'public'
          AND con.contype IN ('p', 'u', 'c', 'x', 'f')
        ORDER BY
            CASE con.contype
                WHEN 'p' THEN 1
                WHEN 'u' THEN 2
                WHEN 'c' THEN 3
                WHEN 'x' THEN 4
                WHEN 'f' THEN 5
                ELSE 6
            END,
            c.relname,
            con.conname;
        """
    )
    constraints = cur.fetchall()

    cur.execute(
        """
        SELECT seq.relname AS sequence_name,
               tbl.relname AS table_name,
               att.attname AS column_name
        FROM pg_class seq
        JOIN pg_namespace ns ON ns.oid = seq.relnamespace
        JOIN pg_depend dep
          ON dep.objid = seq.oid
         AND dep.classid = 'pg_class'::regclass
         AND dep.refclassid = 'pg_class'::regclass
         AND dep.deptype IN ('a', 'i')
        JOIN pg_class tbl ON tbl.oid = dep.refobjid
        JOIN pg_attribute att
          ON att.attrelid = tbl.oid
         AND att.attnum = dep.refobjsubid
        WHERE ns.nspname = 'public'
          AND seq.relkind = 'S'
        ORDER BY seq.relname;
        """
    )
    sequence_owners = cur.fetchall()

    cur.execute(
        """
        SELECT pi.indexname, pi.indexdef
        FROM pg_indexes pi
        JOIN pg_class idx ON idx.relname = pi.indexname
        JOIN pg_namespace n
          ON n.oid = idx.relnamespace
         AND n.nspname = pi.schemaname
        LEFT JOIN pg_constraint con ON con.conindid = idx.oid
        WHERE pi.schemaname = 'public'
          AND con.oid IS NULL
        ORDER BY pi.tablename, pi.indexname;
        """
    )
    indexes = cur.fetchall()

finally:
    cur.close()
    conn.close()

lines = [
    "-- Schema logico finale FlowForest",
    "-- Generato dal database PostgreSQL tramite tools/export_schema.py.",
    "-- Non contiene dati né credenziali.",
    "",
    "BEGIN;",
    "",
    "CREATE SCHEMA IF NOT EXISTS public;",
    "SET search_path TO public;",
    "",
]

for (
    sequence_name,
    data_type,
    start_value,
    min_value,
    max_value,
    increment_by,
    cycle,
    cache_size,
) in sequences:
    lines.extend(
        [
            f"CREATE SEQUENCE {qualified(sequence_name)}",
            f"    AS {data_type}",
            f"    INCREMENT BY {increment_by}",
            f"    MINVALUE {min_value}",
            f"    MAXVALUE {max_value}",
            f"    START WITH {start_value}",
            f"    CACHE {cache_size}",
            f"    {'CYCLE' if cycle else 'NO CYCLE'};",
            "",
        ]
    )

for table_name, columns in columns_by_table.items():
    definitions = []
    for column_name, data_type, not_null, default in columns:
        definition = f"    {quoted(column_name)} {data_type}"
        if default is not None:
            definition += f" DEFAULT {default}"
        if not_null:
            definition += " NOT NULL"
        definitions.append(definition)

    lines.append(f"CREATE TABLE {qualified(table_name)} (")
    lines.append(",\n".join(definitions))
    lines.extend([");", ""])

for table_name, constraint_name, constraint_type, definition in constraints:
    if constraint_type == "f":
        continue
    lines.extend(
        [
            f"ALTER TABLE ONLY {qualified(table_name)}",
            f"    ADD CONSTRAINT {quoted(constraint_name)} {definition};",
            "",
        ]
    )

for sequence_name, table_name, column_name in sequence_owners:
    lines.extend(
        [
            f"ALTER SEQUENCE {qualified(sequence_name)}",
            f"    OWNED BY {qualified(table_name)}.{quoted(column_name)};",
            "",
        ]
    )

for table_name, constraint_name, constraint_type, definition in constraints:
    if constraint_type != "f":
        continue
    lines.extend(
        [
            f"ALTER TABLE ONLY {qualified(table_name)}",
            f"    ADD CONSTRAINT {quoted(constraint_name)} {definition};",
            "",
        ]
    )

for _, index_definition in indexes:
    lines.extend([index_definition.rstrip(";") + ";", ""])

lines.extend(["COMMIT;", ""])

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")

print(f"Schema esportato in: {OUTPUT}")
print(f"Tabelle esportate: {len(columns_by_table)}")
print(f"Vincoli esportati: {len(constraints)}")
print(f"Indici aggiuntivi esportati: {len(indexes)}")
