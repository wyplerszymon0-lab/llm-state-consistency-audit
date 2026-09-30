import json
import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from bench import providers


class FakeOllama:
    """A local HTTP server that records requests and answers like Ollama's /api/generate."""

    def __init__(self, status=200, reply="```python\ndef run():\n    return 1.0\n```"):
        self.requests = []
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                fake.requests.append({"path": self.path, "body": json.loads(body)})
                ok = {"response": reply, "prompt_eval_count": 812, "eval_count": 345}
                payload = json.dumps(ok if status == 200 else {"error": "boom"}).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def log_message(self, *args):  # keep test output quiet
                pass

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def ollama(monkeypatch):
    servers = []

    def start(**kwargs):
        server = FakeOllama(**kwargs)
        servers.append(server)
        monkeypatch.setenv("OLLAMA_HOST", server.url)
        return server

    yield start
    for server in servers:
        server.close()


def test_ollama_request_shape(ollama):
    server = ollama()
    reply = providers.generate("ollama:qwen2.5-coder:7b", "PROMPT")

    assert reply.text.startswith("```python")
    assert (reply.input_tokens, reply.output_tokens) == (812, 345)
    [request] = server.requests
    assert request["path"] == "/api/generate"
    assert request["body"]["model"] == "qwen2.5-coder:7b"  # everything after the first colon
    assert request["body"]["prompt"] == "PROMPT"
    assert request["body"]["stream"] is False
    # The default 2–4k context silently truncates long prompts and reasoning.
    assert request["body"]["options"]["num_ctx"] == 16384


def test_ollama_http_error_propagates(ollama):
    ollama(status=500)
    with pytest.raises(urllib.error.HTTPError):
        providers.generate("ollama:llama3.1:8b", "PROMPT")


@pytest.mark.parametrize("spec", ["qwen", "nope:model", "ollama:", ""])
def test_generate_rejects_bad_specs(spec):
    with pytest.raises(ValueError):
        providers.generate(spec, "PROMPT")
