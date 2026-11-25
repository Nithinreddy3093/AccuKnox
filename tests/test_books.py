import pytest

from assessment1 import books


def test_fetch_books_maps_api_payload(monkeypatch):
    payload = {"docs": [
        {"key": "/works/OL1W", "title": "Example", "author_name": ["A. Writer"], "first_publish_year": 2001},
        {"key": "/works/OL2W", "title": "No author", "first_publish_year": None},
        {"title": "Missing stable key"},
    ]}
    monkeypatch.setattr(books, "get_json", lambda _url: payload)
    assert books.fetch_books("security", 3) == [
        ("/works/OL1W", "Example", "A. Writer", 2001),
        ("/works/OL2W", "No author", "Unknown", None),
    ]


def test_fetch_books_rejects_bad_year(monkeypatch):
    monkeypatch.setattr(books, "get_json", lambda _url: {"docs": [{"key": "x", "title": "t", "first_publish_year": "2000"}]})
    with pytest.raises(ValueError, match="first_publish_year"):
        books.fetch_books()


def test_store_upserts_and_list_books(database):
    books.store_books([("id1", "Title", "Author", 2000)], database)
    books.store_books([("id1", "Updated", "Author Two", 2001)], database)
    rows = books.list_books(database)
    assert len(rows) == 1
    assert tuple(rows[0]) == ("Updated", "Author Two", 2001)
