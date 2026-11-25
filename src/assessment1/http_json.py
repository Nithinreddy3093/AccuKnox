"""Small bounded JSON-over-HTTP client using only the Python standard library."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


MAX_RESPONSE_BYTES = 2 * 1024 * 1024
TIMEOUT_SECONDS = 15


class ApiError(RuntimeError):
    """An HTTP or response-format error from a remote API."""


def validate_http_url(url):
    parts = urlsplit(url)
    if parts.scheme not in {"http", "https"} or not parts.hostname:
        raise ValueError("API URL must be an absolute HTTP or HTTPS URL")
    if parts.username is not None or parts.password is not None:
        raise ValueError("API URL must not contain embedded credentials")


def get_json(url):
    validate_http_url(url)
    request = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "AccuKnoxAssessment1/1.0",
    })
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            content_type = response.headers.get("Content-Type", "")
            if content_type and "json" not in content_type.lower():
                raise ApiError(f"API returned non-JSON content type: {content_type}")
            raw = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        raise ApiError(f"API returned HTTP {exc.code}") from exc
    except (URLError, TimeoutError, OSError) as exc:
        raise ApiError(f"Could not reach API: {exc}") from exc
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ApiError(f"API response exceeded {MAX_RESPONSE_BYTES} bytes")
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApiError("API response was not valid UTF-8 JSON") from exc
