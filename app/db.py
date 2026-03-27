import sqlite3
from pathlib import Path

from flask import current_app, g


# Open the SQLite connection once per request and reuse it through Flask's context.
def get_db():
    if "db" not in g:
        database_path = Path(current_app.config["DATABASE"])
        database_path.parent.mkdir(parents=True, exist_ok=True)

        g.db = sqlite3.connect(database_path)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


# Close the request-scoped database connection when the request ends.
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


# Create tables and backfill required columns for existing local databases.
def init_db():
    db = get_db()
    schema_path = Path(__file__).with_name("schema.sql")
    db.executescript(schema_path.read_text(encoding="utf-8"))
    _ensure_column(db, "users", "role", "TEXT NOT NULL DEFAULT 'user'")
    _ensure_column(db, "journal_entries", "analysis_source", "TEXT")
    _ensure_column(db, "journal_entries", "analysis_model", "TEXT")
    _ensure_column(db, "journal_entries", "analysis_reason", "TEXT")
    db.commit()


# Add a missing column to an existing table without recreating the database.
def _ensure_column(db, table_name, column_name, column_definition):
    columns = db.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_column_names = {column["name"] for column in columns}

    if column_name not in existing_column_names:
        db.execute(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMN {column_name} {column_definition}"
        )
