import pytest

from bench.pricing import cost_usd
from bench.report import _usage_section
from bench.scoring import PASS, WRONG, ModelSummary, RunResult


def test_cost_uses_list_prices_and_never_guesses():
    assert cost_usd("anthropic:claude-sonnet-5", 1_000_000, 1_000_000) == pytest.approx(12.0)
    assert cost_usd("ollama:qwen3:8b", 5000, 5000) == 0.0
    assert cost_usd("openai:some-model", 5000, 5000) is None       # price unknown
    assert cost_usd("anthropic:claude-opus-5", None, 100) is None  # usage unknown


def _run(status, latency, tokens, cost):
    usage = {"latency_s": latency, "output_tokens": tokens, "cost_usd": cost}
    return RunResult("s", "m", "run_1", status, 1.0, 1.0, usage=usage)


def test_usage_section_reports_medians_and_cost_per_pass():
    paid = ModelSummary("paid", "Paid model")
    paid.runs["s"] = [_run(PASS, 10, 1000, 0.10), _run(WRONG, 30, 3000, 0.30), _run(PASS, 20, 2000, 0.20)]
    local = ModelSummary("local", "Local model")
    local.runs["s"] = [_run(WRONG, 60, 500, 0.0)]
    unknown = ModelSummary("unknown", "Unpriced model")
    unknown.runs["s"] = [_run(PASS, 5, 100, None)]
    legacy = ModelSummary("legacy", "No usage recorded")
    legacy.runs["s"] = [RunResult("s", "legacy", "run_1", PASS, 1.0, 1.0)]

    table = "\n".join(_usage_section([paid, local, unknown, legacy]))
    assert "| Paid model | 3 | 20 s | 2,000 | $0.60 | $0.30 |" in table
    assert "| Local model | 1 | 60 s | 500 | $0.00 | no passes |" in table
    assert "| Unpriced model | 1 | 5 s | 100 | – | – |" in table
    assert "No usage recorded" not in table


def test_usage_section_is_omitted_without_any_usage():
    legacy = ModelSummary("legacy", "Legacy")
    legacy.runs["s"] = [RunResult("s", "legacy", "run_1", PASS, 1.0, 1.0)]
    assert _usage_section([legacy]) == []
