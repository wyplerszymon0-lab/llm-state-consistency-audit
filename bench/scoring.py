"""Scores every submission under submissions/<scenario>/<model>/ against its reference.

Layout of one model's directory:
    meta.json           optional: {"display_name": ..., "note": ...}
    run_1.reply.md      raw model reply (written by generate.py)
    run_1.py            code extracted from the reply (missing if none was found)
"""

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from bench.sandbox import execute
from bench.scenarios import Scenario, load_scenarios

SUBMISSIONS_DIR = Path(__file__).resolve().parent.parent / "submissions"

PASS, WRONG, ERROR, TIMEOUT, NO_CODE = "pass", "wrong", "error", "timeout", "no_code"


@dataclass(frozen=True)
class RunResult:
    scenario: str
    model: str
    run_id: str
    status: str
    value: float | None
    expected: float
    detail: str | None = None


@dataclass
class ModelSummary:
    model: str
    display_name: str
    note: str | None = None
    runs: dict[str, list[RunResult]] = field(default_factory=lambda: defaultdict(list))

    def passes(self, scenario: str | None = None) -> int:
        return sum(r.status == PASS for r in self._select(scenario))

    def total(self, scenario: str | None = None) -> int:
        return len(self._select(scenario))

    def pass_rate(self) -> float:
        return self.passes() / self.total() if self.total() else 0.0

    def _select(self, scenario):
        if scenario is not None:
            return self.runs.get(scenario, [])
        return [r for results in self.runs.values() for r in results]


def classify(value: float, scenario: Scenario, expected: float) -> str:
    return PASS if abs(value - expected) <= scenario.tolerance + 1e-9 else WRONG


def score_run(scenario: Scenario, expected: float, model_dir: Path, run_id: str) -> RunResult:
    code = model_dir / f"{run_id}.py"
    base = dict(scenario=scenario.name, model=model_dir.name, run_id=run_id, expected=expected)
    if not code.is_file():
        return RunResult(status=NO_CODE, value=None, detail="no code block in reply", **base)

    execution = execute(code)
    if execution.status != "ok":
        return RunResult(status=execution.status, value=None, detail=execution.error, **base)
    return RunResult(
        status=classify(execution.value, scenario, expected), value=execution.value, **base
    )


def run_ids(model_dir: Path) -> list[str]:
    ids = {p.name.split(".")[0] for p in model_dir.glob("run_*.py")}
    ids |= {p.name.split(".")[0] for p in model_dir.glob("run_*.reply.md")}
    return sorted(ids, key=lambda s: int(s.split("_")[1]))


def score_all(submissions_dir: Path = SUBMISSIONS_DIR) -> list[ModelSummary]:
    summaries: dict[str, ModelSummary] = {}
    for scenario in load_scenarios().values():
        scenario_dir = submissions_dir / scenario.name
        if not scenario_dir.is_dir():
            continue
        expected = scenario.expected()
        for model_dir in sorted(p for p in scenario_dir.iterdir() if p.is_dir()):
            meta_path = model_dir / "meta.json"
            meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
            summary = summaries.setdefault(
                model_dir.name,
                ModelSummary(model_dir.name, meta.get("display_name", model_dir.name), meta.get("note")),
            )
            for run_id in run_ids(model_dir):
                summary.runs[scenario.name].append(score_run(scenario, expected, model_dir, run_id))

    return sorted(summaries.values(), key=lambda s: (-s.pass_rate(), -s.total(), s.display_name))
