import json

import pytest

import generate
from bench.extract import extract_code
from bench.report import render
from bench.sandbox import execute
from bench.scoring import ERROR, NO_CODE, PASS, TIMEOUT, WRONG, score_all

PORTFOLIO_ANSWER = 17072.00


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# --- extract ---------------------------------------------------------------

def test_extract_prefers_block_defining_run():
    reply = "Plan:\n```python\nx = 1\n```\nFinal:\n```python\ndef run():\n    return 1.0\n```\n"
    assert extract_code(reply) == "def run():\n    return 1.0\n"


def test_extract_accepts_bare_fence():
    assert extract_code("```\ndef run():\n    return 2\n```") == "def run():\n    return 2\n"


def test_extract_returns_none_without_code():
    assert extract_code("I think the answer is 42.") is None


# --- sandbox ---------------------------------------------------------------

def test_execute_returns_value_and_ignores_prints(tmp_path):
    path = write(tmp_path / "s.py", "print(123)\ndef run():\n    print('noise')\n    return 4.5\n")
    result = execute(path)
    assert (result.status, result.value) == ("ok", 4.5)


def test_execute_reports_exception(tmp_path):
    path = write(tmp_path / "s.py", "def run():\n    raise KeyError('boom')\n")
    result = execute(path)
    assert result.status == "error"
    assert "KeyError" in result.error


def test_execute_reports_missing_run(tmp_path):
    path = write(tmp_path / "s.py", "x = 1\n")
    assert execute(path).status == "error"


def test_execute_times_out(tmp_path):
    path = write(tmp_path / "s.py", "def run():\n    while True:\n        pass\n")
    assert execute(path, timeout=1).status == "timeout"


# --- scoring & report ------------------------------------------------------

@pytest.fixture
def submissions(tmp_path):
    root = tmp_path / "submissions" / "portfolio"
    write(root / "good" / "run_1.py", f"def run():\n    return {PORTFOLIO_ANSWER}\n")
    write(root / "good" / "run_2.py", f"def run():\n    return {PORTFOLIO_ANSWER + 0.004}\n")
    write(root / "mixed" / "meta.json", json.dumps({"display_name": "Mixed", "note": "fixture"}))
    write(root / "mixed" / "run_1.py", f"def run():\n    return {PORTFOLIO_ANSWER + 0.5}\n")
    write(root / "mixed" / "run_2.py", "def run():\n    return 1 / 0\n")
    write(root / "mixed" / "run_3.reply.md", "No code, sorry.")
    write(root / "mixed" / "run_10.py", "def run():\n    while True:\n        pass\n")
    return tmp_path / "submissions"


def test_score_all_classifies_every_run(submissions, monkeypatch):
    import bench.scoring as scoring

    real_execute = scoring.execute
    monkeypatch.setattr(scoring, "execute", lambda path: real_execute(path, timeout=1))
    good, mixed = score_all(submissions)

    assert good.model == "good" and good.pass_rate() == 1.0
    statuses = [r.status for r in mixed.runs["portfolio"]]
    assert statuses == [WRONG, ERROR, NO_CODE, TIMEOUT]  # run_10 sorts numerically
    assert mixed.display_name == "Mixed"

    report = render([good, mixed])
    assert "| 1 | good | – | 2/2 | – | 100% [34%–100%] | – |" in report
    assert "Mixed †" in report
    assert "off by +0.50" in report
    assert PASS not in [r.status for r in mixed.runs["portfolio"]]


# --- generate --------------------------------------------------------------

def test_generate_saves_reply_and_code(tmp_path, monkeypatch):
    monkeypatch.setattr(generate, "SUBMISSIONS_DIR", tmp_path)
    monkeypatch.setattr(generate, "generate", lambda spec, prompt: "```python\ndef run():\n    return 1.0\n```")

    assert generate.main(["anthropic:claude-opus-5", "--scenario", "ledger", "--runs", "2"]) == 0

    model_dir = tmp_path / "ledger" / "claude-opus-5"
    assert sorted(p.name for p in model_dir.iterdir()) == [
        "meta.json", "run_1.py", "run_1.reply.md", "run_2.py", "run_2.reply.md",
    ]
    assert "prompt v1" in (model_dir / "run_1.reply.md").read_text(encoding="utf-8")


def test_generate_continues_numbering_and_survives_errors(tmp_path, monkeypatch):
    monkeypatch.setattr(generate, "SUBMISSIONS_DIR", tmp_path)
    write(tmp_path / "ledger" / "m" / "run_1.py", "")

    def flaky(spec, prompt):
        raise RuntimeError("rate limited")

    monkeypatch.setattr(generate, "generate", flaky)
    assert generate.main(["ollama:m", "--scenario", "ledger"]) == 1
    monkeypatch.setattr(generate, "generate", lambda spec, prompt: "no code")
    assert generate.main(["ollama:m", "--scenario", "ledger"]) == 0
    assert (tmp_path / "ledger" / "m" / "run_2.reply.md").exists()
    assert not (tmp_path / "ledger" / "m" / "run_2.py").exists()


def test_slug():
    assert generate.slug("openai:GPT 5/Pro") == "gpt-5-pro"
