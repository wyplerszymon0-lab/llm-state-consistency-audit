import pytest

from bench.diagnose import _run_with, diagnose, mutant_answers
from bench.prompting import INSTRUCTIONS, build_prompt
from bench.scenarios import load_scenarios

EXPECTED = {"portfolio": 17072.00, "warehouse": 622.67, "ledger": 6553.73, "wallet": 2351.14}


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


# --- prompt version 2: one worked step --------------------------------------


def test_prompt_v1_is_unchanged_by_v2():
    for scenario in load_scenarios().values():
        assert build_prompt(scenario) == build_prompt(scenario, 1) == f"{INSTRUCTIONS}\n{scenario.prompt}"
        assert "Worked example" not in build_prompt(scenario, 1)


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_prompt_v2_adds_the_worked_example_after_the_rules(name):
    scenario = load_scenarios()[name]
    prompt = build_prompt(scenario, 2)
    assert prompt.startswith(INSTRUCTIONS)
    assert prompt.index("## Answer") < prompt.index("## Worked example")
    assert prompt.rstrip().endswith(scenario.worked_example.rstrip())
    assert "def run" not in prompt


def test_unknown_prompt_version_is_rejected():
    with pytest.raises(ValueError):
        build_prompt(load_scenarios()["ledger"], 3)


# Each worked example states numbers; a truncated reference run must reproduce them.
@pytest.mark.parametrize(
    "name,overrides,stated",
    [
        # cash 1763.03295 + lots 5 x 110.2201 + 20 x 200.6006 after transaction 4
        ("portfolio", lambda r: {"TRANSACTIONS": r.TRANSACTIONS[:4]}, 6326.15),
        # X 4200.00 + Y -425.00 + Z 12000.00 at the end of day 3 (no period close yet)
        ("ledger", lambda r: {"EVENTS": r.EVENTS[:2], "LAST_DAY": 3}, 15775.00),
        # PLN 3500.00 + EUR 1511.65 x 4.3150 + USD 500 x 3.9820 after day 5
        ("wallet", lambda r: {"EVENTS": r.EVENTS[:3], "LAST_DAY": 5}, 3500.00 + 6522.77 + 1991.00),
        # SKU B alone: revenue 218.70 - cogs 133.50 after day 5
        ("warehouse", lambda r: {"EVENTS": [e for e in r.EVENTS if e[2] == "B" and e[0] <= 5], "LAST_DAY": 5}, 85.20),
    ],
)
def test_worked_example_numbers_match_the_reference(name, overrides, stated):
    reference = load_scenarios()[name].reference
    assert _run_with(reference, overrides(reference)) == pytest.approx(stated, abs=0.005)
    assert load_scenarios()[name].expected() == pytest.approx(EXPECTED[name], abs=1e-9)  # restored
