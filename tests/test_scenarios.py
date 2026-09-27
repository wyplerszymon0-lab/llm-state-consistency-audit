import pytest

from bench.diagnose import _run_with, diagnose, mutant_answers
from bench.prompting import build_prompt
from bench.scenarios import load_scenarios

EXPECTED = {"portfolio": 17072.00, "warehouse": 622.67, "ledger": 6553.73}


def test_all_scenarios_registered():
    assert set(load_scenarios()) == set(EXPECTED)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_reference_answer_is_pinned(name):
    assert load_scenarios()[name].expected() == pytest.approx(EXPECTED[name], abs=1e-9)


@pytest.mark.parametrize(
    "name,rule",
    [(n, rule) for n, sc in load_scenarios().items() for rule in sc.reference.RULES],
)
def test_every_rule_affects_the_answer(name, rule):
    # Disabling any single rule must change the answer, otherwise the scenario
    # cannot tell a model that implements the rule from one that ignores it.
    scenario = load_scenarios()[name]
    value = _run_with(scenario.reference, scenario.reference.RULES[rule])
    assert abs(value - EXPECTED[name]) > scenario.tolerance
    assert scenario.expected() == pytest.approx(EXPECTED[name], abs=1e-9)  # restored


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_prompt_contains_contract_and_rules(name):
    prompt = build_prompt(load_scenarios()[name])
    assert "def run" not in prompt  # the model writes it; we only describe it
    assert "`run() -> float`" in prompt
    assert "## Answer" in prompt


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_diagnose_names_the_skipped_rule(name):
    scenario = load_scenarios()[name]
    for rules, answer in mutant_answers(name):
        if len(rules) == 1:
            assert diagnose(scenario, answer) == rules
    assert diagnose(scenario, EXPECTED[name] + 1234.5) is None
