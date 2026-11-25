import pytest

from assessment1 import users
from assessment1.db import connection


def test_import_users_normalizes_and_upserts(database, tmp_path):
    csv_path = tmp_path / "users.csv"
    csv_path.write_text("Name,Email\nAsha,ASHA@example.com\nDev,dev@example.com\n", encoding="utf-8")
    assert users.import_users(csv_path, database) == 2
    csv_path.write_text("name,email\nAsha Updated,asha@example.com\n", encoding="utf-8")
    assert users.import_users(csv_path, database) == 1
    with connection(database) as db:
        rows = db.execute("SELECT name,email FROM users ORDER BY email").fetchall()
    assert [tuple(row) for row in rows] == [
        ("Asha Updated", "asha@example.com"),
        ("Dev", "dev@example.com"),
    ]


def test_invalid_csv_row_does_not_insert_partial_data(database, tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("name,email\nValid,valid@example.com\nMissing,not-an-email\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 3"):
        users.import_users(csv_path, database)
    with connection(database) as db:
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0


def test_missing_csv_columns_are_rejected(database, tmp_path):
    csv_path = tmp_path / "bad.csv"
    csv_path.write_text("username,mail\nAsha,asha@example.com\n", encoding="utf-8")
    with pytest.raises(ValueError, match="name and email"):
        users.import_users(csv_path, database)
