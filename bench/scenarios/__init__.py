"""Scenario registry. Each scenario is a sub-package with prompt.md and reference.py."""

import importlib
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from types import ModuleType

SCENARIOS_DIR = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Scenario:
    name: str
    prompt: str
    reference: ModuleType
    tolerance: float = 0.01

    @property
    def title(self) -> str:
        first_line = self.prompt.splitlines()[0]
        return first_line.lstrip("# ").strip()

    def expected(self) -> float:
        return self.reference.run()


@cache
def load_scenarios() -> dict[str, Scenario]:
    scenarios = {}
    for path in sorted(SCENARIOS_DIR.iterdir()):
        if not (path / "prompt.md").is_file():
            continue
        reference = importlib.import_module(f"bench.scenarios.{path.name}.reference")
        scenarios[path.name] = Scenario(
            name=path.name,
            prompt=(path / "prompt.md").read_text(encoding="utf-8"),
            reference=reference,
            tolerance=getattr(reference, "TOLERANCE", 0.01),
        )
    return scenarios
