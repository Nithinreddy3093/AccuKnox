"""Retrieve books from a JSON REST API, store them, and display stored rows."""
from urllib.parse import urlencode

from .db import connection
from .http_json import get_json


OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"


def fetch_books(query="artificial intelligence", limit=10, api_url=OPEN_LIBRARY_SEARCH_URL):
    if not query.strip():
        raise ValueError("Book search query cannot be empty")
    if not 1 <= limit <= 100:
        raise ValueError("Book result limit must be between 1 and 100")
    url = f"{api_url}?{urlencode({'q': query, 'limit': limit, 'fields': 'key,title,author_name,first_publish_year'})}"
    payload = get_json(url)
    if not isinstance(payload, dict) or not isinstance(payload.get("docs"), list):
        raise ValueError("Books API response must contain a docs list")
    books = []
    for index, item in enumerate(payload["docs"]):
        if not isinstance(item, dict):
            raise ValueError(f"Book record {index + 1} must be a JSON object")
        source_id, title = item.get("key"), item.get("title")
        if not isinstance(source_id, str) or not source_id.strip():
            continue
        if not isinstance(title, str) or not title.strip():
            continue
        authors = item.get("author_name") or []
        if not isinstance(authors, list) or any(not isinstance(a, str) for a in authors):
            raise ValueError(f"Book record {index + 1} has invalid author_name")
        year = item.get("first_publish_year")
        if year is not None and (isinstance(year, bool) or not isinstance(year, int)):
            raise ValueError(f"Book record {index + 1} has invalid first_publish_year")
        books.append((source_id.strip(), title.strip(), ", ".join(authors) or "Unknown", year))
    return books


def store_books(books, database_path=None):
    with connection(database_path) as db:
        db.executemany("""
            INSERT INTO books(source_id, title, author, publication_year)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(source_id) DO UPDATE SET
                title = excluded.title,
                author = excluded.author,
                publication_year = excluded.publication_year
        """, books)


def list_books(database_path=None):
    with connection(database_path) as db:
        return db.execute("""
            SELECT title, author, publication_year
            FROM books ORDER BY title COLLATE NOCASE, source_id
        """).fetchall()
