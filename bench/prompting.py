"""Builds the exact prompt sent to every model. Changing it invalidates old results."""

from bench.scenarios import Scenario

PROMPT_VERSION = 1

INSTRUCTIONS = """\
Write a Python 3 program that computes the answer to the simulation below.

Requirements:
- A single self-contained module using only the standard library.
- It must define a function `run() -> float` that returns the final answer.
- No input, no file or network access. Printing is allowed but ignored.
- Reply with exactly one ```python code block containing the whole module.
"""


def build_prompt(scenario: Scenario) -> str:
    return f"{INSTRUCTIONS}\n{scenario.prompt}"
