import os
from pathlib import Path

import psycopg
from psycopg.rows import dict_row


def connect():
    database_url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if not database_url:
        raise RuntimeError("Configure DATABASE_URL or POSTGRES_URL for the Studio database")
    return psycopg.connect(database_url, row_factory=dict_row, connect_timeout=8)


def migrate():
    with connect() as conn:
        conn.execute("SELECT pg_advisory_xact_lock(76421001)")
        conn.execute("CREATE TABLE IF NOT EXISTS schema_migrations (name text PRIMARY KEY)")
        applied = {row["name"] for row in conn.execute("SELECT name FROM schema_migrations")}
        for path in sorted(Path(__file__).with_name("migrations").glob("*.sql")):
            if path.name not in applied:
                conn.execute(path.read_text(encoding="utf-8"))
                conn.execute("INSERT INTO schema_migrations VALUES (%s)", (path.name,))


if __name__ == "__main__":
    migrate()
