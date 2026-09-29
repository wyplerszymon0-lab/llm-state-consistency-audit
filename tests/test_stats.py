import pytest

from bench.scoring import ERROR, PASS, WRONG, ModelSummary, RunResult
from bench.stats import pass_at_k, wilson_interval


@pytest.mark.parametrize(
    "n,c,k,expected",
    [
        (5, 1, 1, 0.2),         # pass@1 is the plain pass rate
        (5, 1, 3, 1 - 4 / 10),  # 1 - C(4,3)/C(5,3)
        (5, 0, 3, 0.0),
        (5, 3, 3, 1.0),         # fewer than k failures: some sample of k always passes
        (10, 2, 5, 1 - 56 / 252),
    ],
)
def test_pass_at_k(n, c, k, expected):
    assert pass_at_k(n, c, k) == pytest.approx(expected)


def test_pass_at_k_rejects_k_above_n():
    with pytest.raises(ValueError):
        pass_at_k(2, 1, 3)


@pytest.mark.parametrize(
    "successes,total,lo,hi",
    [
        (0, 15, 0.0, 0.2039),   # never below 0 %, unlike p ± 1.96·SE
        (1, 15, 0.0119, 0.2982),
        (1, 1, 0.2065, 1.0),    # one lucky run proves little
        (50, 100, 0.4038, 0.5962),
    ],
)
def test_wilson_interval(successes, total, lo, hi):
    got_lo, got_hi = wilson_interval(successes, total)
    assert got_lo == pytest.approx(lo, abs=1e-4)
    assert got_hi == pytest.approx(hi, abs=1e-4)


def test_wilson_interval_with_no_runs_is_uninformative():
    assert wilson_interval(0, 0) == (0.0, 1.0)


def _runs(scenario, statuses):
    return [RunResult(scenario, "m", f"run_{i}", s, None, 1.0) for i, s in enumerate(statuses, 1)]


def test_model_summary_pass_at_averages_scenarios_with_enough_runs():
    summary = ModelSummary("m", "M")
    summary.runs["a"] = _runs("a", [PASS, WRONG, WRONG, ERROR, WRONG])  # pass@3 = 0.6
    summary.runs["b"] = _runs("b", [WRONG] * 5)                          # pass@3 = 0
    summary.runs["c"] = _runs("c", [PASS])                               # too few runs for k=3
    assert summary.pass_at(3) == pytest.approx(0.3)
    assert summary.pass_at(1) == pytest.approx((0.2 + 0 + 1) / 3)
    assert summary.pass_at(6) is None
    assert summary.pass_rate_interval() == wilson_interval(2, 11)
