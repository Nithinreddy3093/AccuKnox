from io import BytesIO

import pytest

from assessment1 import http_json
from assessment1.http_json import ApiError


def test_http_url_validation_rejects_non_http_and_embedded_credentials():
    with pytest.raises(ValueError, match="HTTP or HTTPS"):
        http_json.validate_http_url("file:///etc/passwd")
    with pytest.raises(ValueError, match="credentials"):
        http_json.validate_http_url("https://user:secret@example.com/data")


def test_http_json_rejects_non_json_content_type(monkeypatch):
    class Response(BytesIO):
        headers = {"Content-Type": "text/html"}
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(http_json, "urlopen", lambda *_args, **_kwargs: Response(b"{}"))
    with pytest.raises(ApiError, match="non-JSON"):
        http_json.get_json("https://example.com/data")


def test_http_json_enforces_response_size_limit(monkeypatch):
    class Response(BytesIO):
        headers = {"Content-Type": "application/json"}
        def __enter__(self):
            return self
        def __exit__(self, *_args):
            self.close()

    monkeypatch.setattr(http_json, "MAX_RESPONSE_BYTES", 4)
    monkeypatch.setattr(http_json, "urlopen", lambda *_args, **_kwargs: Response(b"12345"))
    with pytest.raises(ApiError, match="exceeded"):
        http_json.get_json("https://example.com/data")
