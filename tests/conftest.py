import pytest

from assessment1.db import initialize


@pytest.fixture
def database(tmp_path):
    path = tmp_path / "test.sqlite3"
    initialize(path)
    return path
