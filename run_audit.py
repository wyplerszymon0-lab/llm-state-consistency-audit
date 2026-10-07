"""Score every submission in submissions/ and write reports/leaderboard.md.

Usage:
    python run_audit.py                    # each submission in a subprocess
    python run_audit.py --sandbox docker   # each submission in a locked-down container
"""

import argparse
import sys

from bench.report import write_report
from bench.sandbox import docker_available, execute, execute_docker
from bench.scenarios import load_scenarios
from bench.scoring import score_all


def main(argv=None):
    parser = argparse.ArgumentParser(description="Score every submission and write the leaderboard.")
    parser.add_argument(
        "--sandbox",
        choices=["subprocess", "docker"],
        default="subprocess",
        help="subprocess (default): fast, not isolated; docker: no network, read-only, CPU/memory limits",
    )
    args = parser.parse_args(argv)
    if args.sandbox == "docker" and not docker_available():
        print("error: --sandbox docker needs a running Docker daemon (`docker info` failed)", file=sys.stderr)
        return 2

    summaries = score_all(executor=execute_docker if args.sandbox == "docker" else execute)
    scenarios = list(load_scenarios())
    width = max((len(s.display_name) for s in summaries), default=10)
    for s in summaries:
        cells = "  ".join(f"{name}={s.passes(name)}/{s.total(name)}" for name in scenarios)
        lo, hi = s.pass_rate_interval()
        print(f"{s.display_name:<{width}}  {cells}  pass_rate={s.pass_rate():.0%} [{lo:.0%}-{hi:.0%}]")
    print(f"\nReport written to {write_report(summaries)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
