import pytest

from bench.prompting import build_prompt
from bench.scenarios import load_scenarios

EXPECTED = {"portfolio": 17072.00, "warehouse": 622.67, "ledger": 6553.73}

# Disabling any single rule must change the answer, otherwise the scenario
# cannot tell a model that implements the rule from one that ignores it.
MUTANTS = {
    "portfolio": {
        "PRICE_MODIFIER": 1.0,
        "WEALTH_TAX_RATE": 0.0,
        "HIGH_PROFIT_TAX_RATE": 0.05,
        "DRIFT_RATE": 1.0,
    },
    "warehouse": {
        "LEAD_TIME": 1,
        "BACKORDER_DISCOUNT": 1.0,
        "CANCELLATION_PENALTY": 0.0,
        "SKUS": {"A": (99, 8, 20, 4.00), "B": (30, 5, 10, 12.50), "C": (99, 4, 12, 2.20)},
    },
    "ledger": {
        "OVERDRAFT_FEE": 0,
        "REJECTION_FEE": 0,
        "TRANSFER_FEE": 0,
        "RATE_HIGH": 0.02,
        "RATE_OVERDRAFT": 0,
        "MAINTENANCE_FEE": 0,
    },
}


def test_all_scenarios_registered():
    assert set(load_scenarios()) == set(EXPECTED)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_reference_answer_is_pinned(name):
    assert load_scenarios()[name].expected() == pytest.approx(EXPECTED[name], abs=1e-9)


@pytest.mark.parametrize(
    "name,constant", [(n, c) for n, consts in MUTANTS.items() for c in consts]
)
def test_every_rule_affects_the_answer(monkeypatch, name, constant):
    reference = load_scenarios()[name].reference
    value = MUTANTS[name][constant]
    if name == "ledger" and not isinstance(value, dict):
        from decimal import Decimal

        value = Decimal(str(value))
    monkeypatch.setattr(reference, constant, value)
    assert abs(reference.run() - EXPECTED[name]) > 0.01


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_prompt_contains_contract_and_rules(name):
    prompt = build_prompt(load_scenarios()[name])
    assert "def run" not in prompt  # the model writes it; we only describe it
    assert "`run() -> float`" in prompt
    assert "## Answer" in prompt
