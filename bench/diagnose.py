"""Explains a wrong answer by matching it against the reference with rules switched off.

Each scenario's reference module lists its rules in RULES, as the constant
overrides that disable each one. A wrong answer that equals the reference with
one rule (or a pair of rules) disabled almost certainly comes from a program
that ignored exactly those rules. Only exact matches (within the scenario
tolerance) are reported: a near miss is not evidence of anything.
"""

from functools import cache
from itertools import combinations

from bench.scenarios import Scenario, load_scenarios


def _run_with(reference, overrides: dict) -> float:
    saved = {name: getattr(reference, name) for name in overrides}
    try:
        for name, value in overrides.items():
            setattr(reference, name, value)
        return reference.run()
    finally:
        for name, value in saved.items():
            setattr(reference, name, value)


@cache
def mutant_answers(scenario_name: str) -> tuple[tuple[tuple[str, ...], float], ...]:
    """Answers with every single rule and every pair of rules switched off."""
    reference = load_scenarios()[scenario_name].reference
    rules = getattr(reference, "RULES", {})
    answers = []
    for size in (1, 2):
        for combo in combinations(rules, size):
            overrides = {k: v for rule in combo for k, v in rules[rule].items()}
            answers.append((combo, _run_with(reference, overrides)))
    return tuple(answers)


def diagnose(scenario: Scenario, value: float) -> tuple[str, ...] | None:
    """The smallest set of skipped rules that reproduces `value` exactly, if any."""
    for rules, answer in mutant_answers(scenario.name):
        if abs(answer - value) <= scenario.tolerance + 1e-9:
            return rules
    return None
