import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

import pytest

from assessment1.scores import calculate_average, create_bar_chart, fetch_scores


class ScoreHandler(BaseHTTPRequestHandler):
    body = b"[]"
    status = 200

    def do_GET(self):
        self.send_response(type(self).status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(type(self).body)

    def log_message(self, _format, *_args):
        pass


@pytest.fixture
def score_api():
    handler = type("TestScoreHandler", (ScoreHandler,), {})
    handler.body = json.dumps([
        {"student": "Asha", "score": 80},
        {"student": "Dev", "score": 90},
    ]).encode()
    handler.status = 200
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.server_port}/scores"
    server.shutdown()
    thread.join(timeout=2)
    server.server_close()


def test_fetch_scores_over_http_and_average(score_api):
    rows = fetch_scores(score_api)
    assert rows == [("Asha", 80.0), ("Dev", 90.0)]
    assert calculate_average(rows) == 85.0


def test_fetch_scores_accepts_documented_demo_api_envelope(monkeypatch):
    import assessment1.scores as module
    monkeypatch.setattr(module, "get_json", lambda _url: {"success": True, "data": [
        {"name": "Asha", "score": 80}, {"name": "Dev", "score": 90},
    ]})
    assert fetch_scores("https://example.com/api") == [("Asha", 80.0), ("Dev", 90.0)]


@pytest.mark.parametrize("payload", [[], [{"student": "A", "score": True}], [{"student": "A", "score": -1}], [{"student": "A", "score": float("nan")}]])
def test_fetch_scores_rejects_invalid_rows(monkeypatch, payload):
    import assessment1.scores as module
    monkeypatch.setattr(module, "get_json", lambda _url: payload)
    with pytest.raises(ValueError):
        fetch_scores("http://example.invalid/scores")


def test_fetch_scores_rejects_unrepresentable_integer(monkeypatch):
    import assessment1.scores as module
    monkeypatch.setattr(module, "get_json", lambda _url: [{"student": "A", "score": 10 ** 1000}])
    with pytest.raises(ValueError, match="numeric range"):
        fetch_scores("http://example.invalid/scores")


def test_create_chart_writes_png(tmp_path):
    path = tmp_path / "scores.png"
    assert create_bar_chart([("A", 70), ("B", 90)], path) == 80
    assert path.is_file() and path.stat().st_size > 0
