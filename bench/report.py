"""Renders the leaderboard markdown from scored results."""

from datetime import date
from pathlib import Path
from statistics import median

from bench.diagnose import diagnose
from bench.prompting import PROMPT_VERSION
from bench.scenarios import load_scenarios
from bench.scoring import ERROR, PASS, ModelSummary

REPORT_PATH = Path(__file__).resolve().parent.parent / "reports" / "leaderboard.md"


def _cell(summary: ModelSummary, scenario: str) -> str:
    total = summary.total(scenario)
    return f"{summary.passes(scenario)}/{total}" if total else "–"


def _usage_section(summaries: list[ModelSummary]) -> list[str]:
    """Latency, tokens and cost for models whose runs recorded them."""
    rows = []
    for s in summaries:
        runs = [r for rs in s.runs.values() for r in rs if r.usage]
        if not runs:
            continue
        latency = median([r.usage["latency_s"] for r in runs])
        tokens = [r.usage["output_tokens"] for r in runs if r.usage.get("output_tokens") is not None]
        costs = [r.usage.get("cost_usd") for r in runs]
        if any(c is None for c in costs):
            total, per_pass = "–", "–"
        else:
            spent = sum(costs)
            passes = sum(r.status == PASS for r in runs)
            total = f"${spent:.2f}"
            per_pass = f"${spent / passes:.2f}" if passes else "no passes"
        rows.append(
            f"| {s.display_name} | {len(runs)} | {latency:.0f} s | "
            f"{f'{median(tokens):,.0f}' if tokens else '–'} | {total} | {per_pass} |"
        )
    if not rows:
        return []
    return [
        "",
        "## Cost and speed",
        "",
        "Recorded by `generate.py` for each run (runs made before it recorded usage are left out). "
        "Local models cost nothing to call; latency depends on the hardware they ran on.",
        "",
        "| Model | Runs | Median latency | Median output tokens | Total cost | Cost per passed run |",
        "| :--- | ---: | ---: | ---: | ---: | ---: |",
        *rows,
    ]


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
        "| Rank | Model | " + " | ".join(scenarios) + " | Pass rate [95% CI] | pass@3 |",
        "| ---: | :--- | " + " | ".join(":---:" for _ in scenarios) + " | ---: | ---: |",
    ]
    for rank, s in enumerate(summaries, start=1):
        name = s.display_name + (" †" if s.note else "")
        cells = " | ".join(_cell(s, name_) for name_ in scenarios)
        lo, hi = s.pass_rate_interval()
        at3 = s.pass_at(3)
        lines.append(
            f"| {rank} | {name} | {cells} | {s.pass_rate():.0%} [{lo:.0%}–{hi:.0%}] | "
            f"{'–' if at3 is None else f'{at3:.0%}'} |"
        )

    lines += [
        "",
        "*Pass rate* pools every run of the model; the 95% Wilson interval shows how much it could "
        "move with more runs. *pass@3* is the unbiased estimate (Chen et al., 2021) of the chance "
        "that at least one of 3 attempts passes, averaged over scenarios with at least 3 runs.",
    ]
    notes = [s for s in summaries if s.note]
    if notes:
        lines.append("")
        lines.extend(f"† **{s.display_name}**: {s.note}  " for s in notes)

    lines += _usage_section(summaries)

    lines += ["", "## Reference answers", "", "| Scenario | Answer |", "| :--- | ---: |"]
    lines += [f"| {sc.title} (`{sc.name}`) | {sc.expected():.2f} |" for sc in scenarios.values()]

    failures = [r for s in summaries for rs in s.runs.values() for r in rs if r.status != PASS]
    if failures:
        lines += [
            "",
            "## Failed runs",
            "",
            "For every wrong answer the audit also runs the reference with each rule, and each pair "
            "of rules, switched off. If the answer matches one of those exactly, the detail names the "
            "rules the program most likely ignored.",
            "",
            "| Model | Scenario | Run | Status | Answer | Expected | Detail |",
            "| :--- | :--- | :--- | :--- | ---: | ---: | :--- |",
        ]
        for r in failures:
            value = f"{r.value:.2f}" if r.value is not None else "–"
            detail = (r.detail or "").replace("|", "\\|")
            if r.status == ERROR:
                # Exception type only: messages differ between Python versions
                # ("Did you mean ...?" hints), which would make the report unstable.
                detail = f"`{detail.split(':')[0]}`"
            if r.value is not None:
                detail = f"off by {r.value - r.expected:+.2f}"
                skipped = diagnose(scenarios[r.scenario], r.value)
                if skipped:
                    detail += " · equals the answer without: " + ", ".join(skipped)
            lines.append(
                f"| {r.model} | {r.scenario} | {r.run_id} | {r.status} | {value} | "
                f"{r.expected:.2f} | {detail} |"
            )
    return "\n".join(lines) + "\n"


def write_report(summaries: list[ModelSummary], path: Path = REPORT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(summaries), encoding="utf-8")
    return path
