"""Ask models to solve each scenario and save their replies as submissions.

Usage:
    python generate.py anthropic:claude-opus-5 openai:<model> --runs 3
    python generate.py ollama:qwen3-coder --scenario ledger
    python generate.py ollama:qwen2.5-coder:14b --prompt-version 2 --runs 5

Existing runs are kept; new runs get the next free number. Score with run_audit.py.
"""

import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone

from bench.extract import extract_code
from bench.pricing import cost_usd
from bench.prompting import PROMPT_VERSIONS, build_prompt, run_dir_suffix
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
    parser.add_argument(
        "--prompt-version",
        type=int,
        choices=PROMPT_VERSIONS,
        default=1,
        help="1: scenario only (default); 2: plus one worked transaction (saved as <model>-prompt-v2)",
    )
    args = parser.parse_args(argv)

    scenarios = load_scenarios()
    selected = args.scenario or list(scenarios)
    unknown = set(selected) - set(scenarios)
    if unknown:
        parser.error(f"unknown scenario(s): {', '.join(sorted(unknown))}")

    version = args.prompt_version
    failures = 0
    for spec in args.models:
        for name in selected:
            model_dir = SUBMISSIONS_DIR / name / (slug(spec) + run_dir_suffix(version))
            model_dir.mkdir(parents=True, exist_ok=True)
            meta = model_dir / "meta.json"
            if not meta.exists():
                display = spec.split(":", 1)[1] + ("" if version == 1 else f" (prompt v{version})")
                info = {"display_name": display, "model": spec, "prompt_version": version}
                meta.write_text(json.dumps(info, indent=2) + "\n")

            existing = run_ids(model_dir)
            start = max((int(r.split("_")[1]) for r in existing), default=0) + 1
            for n in range(start, start + args.runs):
                label = f"{spec} / {name} / run_{n}"
                started = time.perf_counter()
                try:
                    reply = generate(spec, build_prompt(scenarios[name], version))
                except Exception as exc:  # keep going: one bad call shouldn't sink the batch
                    failures += 1
                    print(f"FAILED  {label}: {exc}", file=sys.stderr)
                    continue

                header = (
                    f"<!-- model: {spec} | prompt v{version} | "
                    f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} -->\n\n"
                )
                latency = time.perf_counter() - started
                (model_dir / f"run_{n}.reply.md").write_text(header + reply.text, encoding="utf-8")
                usage = {
                    "model": spec,
                    "prompt_version": version,
                    "latency_s": round(latency, 2),
                    "input_tokens": reply.input_tokens,
                    "output_tokens": reply.output_tokens,
                    "cost_usd": cost_usd(spec, reply.input_tokens, reply.output_tokens),
                }
                (model_dir / f"run_{n}.meta.json").write_text(json.dumps(usage, indent=2) + "\n", encoding="utf-8")
                code = extract_code(reply.text)
                if code:
                    (model_dir / f"run_{n}.py").write_text(code, encoding="utf-8")
                print(f"saved   {label}" + ("" if code else "  (no code block found)"))

    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
