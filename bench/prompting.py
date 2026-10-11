"""Builds the exact prompt sent to every model. Changing a version invalidates its results.

Version 1 is the scenario alone. Version 2 adds one transaction worked out step by
step (worked_example.md next to the scenario), to test whether an example of the
rules applied helps models get the whole simulation right. Runs made with version 2
are saved under their own model directory with a "-prompt-v2" suffix, so the two
versions appear side by side in the leaderboard.
"""

from bench.scenarios import Scenario

PROMPT_VERSION = 1  # the default; existing results were generated with it
PROMPT_VERSIONS = (1, 2)

INSTRUCTIONS = """\
Write a Python 3 program that computes the answer to the simulation below.

Requirements:
- A single self-contained module using only the standard library.
- It must define a function `run() -> float` that returns the final answer.
- No input, no file or network access. Printing is allowed but ignored.
- Reply with exactly one ```python code block containing the whole module.
"""

WORKED_EXAMPLE_HEADER = """\

## Worked example

One step of the simulation, computed by hand from the rules above. Your program
must reproduce it, and apply the same rules to every other step.

"""


def build_prompt(scenario: Scenario, version: int = PROMPT_VERSION) -> str:
    if version == 1:
        return f"{INSTRUCTIONS}\n{scenario.prompt}"
    if version == 2:
        if not scenario.worked_example:
            raise ValueError(f"scenario {scenario.name!r} has no worked_example.md")
        return f"{INSTRUCTIONS}\n{scenario.prompt.rstrip()}\n{WORKED_EXAMPLE_HEADER}{scenario.worked_example}"
    raise ValueError(f"unknown prompt version {version}; known: {PROMPT_VERSIONS}")


def run_dir_suffix(version: int) -> str:
    """Model-directory suffix for runs made with a non-default prompt."""
    return "" if version == PROMPT_VERSION else f"-prompt-v{version}"
