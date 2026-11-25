"""Validate and import CSV user rows into SQLite."""
import csv
import re

from .db import connection


EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def import_users(csv_path, database_path=None):
    rows = []
    with open(csv_path, newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            raise ValueError("CSV must include a header row with name,email columns")
        columns = {header.strip().lower(): header for header in reader.fieldnames if header}
        if not {"name", "email"}.issubset(columns):
            raise ValueError("CSV must include name and email columns")
        for line_number, row in enumerate(reader, start=2):
            name = (row.get(columns["name"]) or "").strip()
            email = (row.get(columns["email"]) or "").strip().lower()
            if not name or not EMAIL_PATTERN.fullmatch(email):
                raise ValueError(f"Invalid name or email at CSV line {line_number}")
            rows.append((name, email))
    with connection(database_path) as db:
        db.executemany("""
            INSERT INTO users(name, email) VALUES (?, ?)
            ON CONFLICT(email) DO UPDATE SET name = excluded.name
        """, rows)
    return len(rows)
