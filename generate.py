"""Ask models to solve each scenario and save their replies as submissions.

Usage:
    python generate.py anthropic:claude-opus-5 openai:<model> --runs 3
    python generate.py ollama:qwen3-coder --scenario ledger

Existing runs are kept; new runs get the next free number. Score with run_audit.py.
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone

from bench.extract import extract_code
from bench.prompting import PROMPT_VERSION, build_prompt
from bench.providers import generate
from bench.scenarios import load_scenarios
from bench.scoring import SUBMISSIONS_DIR, run_ids


def slug(spec: str) -> str:
    return re.sub(r"[^a-z0-9.]+", "-", spec.split(":", 1)[1].lower()).strip("-")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("models", nargs="+", help="provider:model, e.g. anthropic:claude-opus-5")
    parser.add_argument("--scenario", action="append", help="limit to these scenarios (repeatable)")
    parser.add_argument("--runs", type=int, default=1, help="new runs per model and scenario")
    args = parser.parse_args(argv)

    scenarios = load_scenarios()
    selected = args.scenario or list(scenarios)
    unknown = set(selected) - set(scenarios)
    if unknown:
        parser.error(f"unknown scenario(s): {', '.join(sorted(unknown))}")

    failures = 0
    for spec in args.models:
        for name in selected:
            model_dir = SUBMISSIONS_DIR / name / slug(spec)
            model_dir.mkdir(parents=True, exist_ok=True)
            meta = model_dir / "meta.json"
            if not meta.exists():
                meta.write_text(json.dumps({"display_name": spec.split(":", 1)[1], "model": spec}, indent=2) + "\n")

            existing = run_ids(model_dir)
            start = max((int(r.split("_")[1]) for r in existing), default=0) + 1
            for n in range(start, start + args.runs):
                label = f"{spec} / {name} / run_{n}"
                try:
                    reply = generate(spec, build_prompt(scenarios[name]))
                except Exception as exc:  # keep going: one bad call shouldn't sink the batch
                    failures += 1
                    print(f"FAILED  {label}: {exc}", file=sys.stderr)
                    continue

                header = (
                    f"<!-- model: {spec} | prompt v{PROMPT_VERSION} | "
                    f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} -->\n\n"
                )
                (model_dir / f"run_{n}.reply.md").write_text(header + reply, encoding="utf-8")
                code = extract_code(reply)
                if code:
                    (model_dir / f"run_{n}.py").write_text(code, encoding="utf-8")
                print(f"saved   {label}" + ("" if code else "  (no code block found)"))

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
