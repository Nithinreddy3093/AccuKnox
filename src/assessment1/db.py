"""SQLite schema and connection management."""
import os
import sqlite3
from contextlib import contextmanager


def default_database_path():
    return os.environ.get("ASSESSMENT1_DB", "assessment1.sqlite3")


@contextmanager
def connection(database_path=None):
    db = sqlite3.connect(database_path or default_database_path())
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def initialize(database_path=None):
    with connection(database_path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS books (
                source_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publication_year INTEGER
            );
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            );
        """)
