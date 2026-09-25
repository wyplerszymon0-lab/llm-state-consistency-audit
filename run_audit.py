"""Score every submission in submissions/ and write reports/leaderboard.md.

Usage:
    python run_audit.py
"""

from bench.report import write_report
from bench.scenarios import load_scenarios
from bench.scoring import score_all


def main():
    summaries = score_all()
    scenarios = list(load_scenarios())
    width = max((len(s.display_name) for s in summaries), default=10)
    for s in summaries:
        cells = "  ".join(f"{name}={s.passes(name)}/{s.total(name)}" for name in scenarios)
        print(f"{s.display_name:<{width}}  {cells}  pass_rate={s.pass_rate():.0%}")
    print(f"\nReport written to {write_report(summaries)}")


if __name__ == "__main__":
    main()
