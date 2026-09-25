"""Renders the leaderboard markdown from scored results."""

from datetime import date
from pathlib import Path

from bench.prompting import PROMPT_VERSION
from bench.scenarios import load_scenarios
from bench.scoring import PASS, ModelSummary

REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "leaderboard.md"


def _cell(summary: ModelSummary, scenario: str) -> str:
    total = summary.total(scenario)
    return f"{summary.passes(scenario)}/{total}" if total else "–"


def render(summaries: list[ModelSummary]) -> str:
    scenarios = load_scenarios()
    lines = [
        "# LLM State-Consistency Audit — Leaderboard",
        "",
        f"_Generated {date.today().isoformat()} by `run_audit.py` (prompt v{PROMPT_VERSION}). "
        "Do not hand-edit — rerun the audit instead._",
        "",
        "A run **passes** only if its answer is within the scenario tolerance (0.01) of the "
        "reference. Anything else — a wrong number, a crash, a timeout or no code — fails.",
        "",
        "| Rank | Model | " + " | ".join(scenarios) + " | Pass rate |",
        "| ---: | :--- | " + " | ".join(":---:" for _ in scenarios) + " | ---: |",
    ]
    for rank, s in enumerate(summaries, start=1):
        name = s.display_name + (" †" if s.note else "")
        cells = " | ".join(_cell(s, name_) for name_ in scenarios)
        lines.append(f"| {rank} | {name} | {cells} | {s.pass_rate():.0%} |")

    notes = [s for s in summaries if s.note]
    if notes:
        lines.append("")
        lines.extend(f"† **{s.display_name}**: {s.note}  " for s in notes)

    lines += ["", "## Reference answers", "", "| Scenario | Answer |", "| :--- | ---: |"]
    lines += [f"| {sc.title} (`{sc.name}`) | {sc.expected():.2f} |" for sc in scenarios.values()]

    failures = [r for s in summaries for rs in s.runs.values() for r in rs if r.status != PASS]
    if failures:
        lines += [
            "",
            "## Failed runs",
            "",
            "| Model | Scenario | Run | Status | Answer | Expected | Detail |",
            "| :--- | :--- | :--- | :--- | ---: | ---: | :--- |",
        ]
        for r in failures:
            value = f"{r.value:.2f}" if r.value is not None else "–"
            detail = (r.detail or "").replace("|", "\\|")
            if r.value is not None:
                detail = f"off by {r.value - r.expected:+.2f}"
            lines.append(
                f"| {r.model} | {r.scenario} | {r.run_id} | {r.status} | {value} | "
                f"{r.expected:.2f} | {detail} |"
            )
    return "\n".join(lines) + "\n"


def write_report(summaries: list[ModelSummary], path: Path = REPORT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(summaries), encoding="utf-8")
    return path
