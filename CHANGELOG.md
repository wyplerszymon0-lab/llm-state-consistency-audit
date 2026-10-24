# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Prompt version 2: the scenario plus one step worked out by hand
  (`worked_example.md`, each checked against a truncated reference run in the tests).
  `generate.py --prompt-version 2` saves runs as `<model>-prompt-v2`, and the
  leaderboard compares both versions on the scenarios each model ran (#7).
- gpt-oss 20B and Qwen3-Coder 30B, 5 runs per scenario: 18/20 and 9/20, the first
  local passes on warehouse. Both failed one ledger run with the same cross-account
  minimum-balance bug (#8).
- Accuracy vs. time chart (pass rate with its Wilson interval against median seconds per run),
  written next to the leaderboard as SVG and inlined on the Pages site with per-point tooltips (#21).

## [1.0.0] - 2026-10-01

First tagged release of the benchmark: three business-rule scenarios, a sandboxed
harness with strict scoring, and a leaderboard of local models.

### Added

- Qwen2.5-Coder 14B results (5 runs per scenario) and a single Qwen3 8B run, marked as
  such because one run took ~27 minutes on the test GPU (#8, partly).
- Latency, input/output tokens and cost recorded for every run (`run_N.meta.json`),
  with a "Cost and speed" table on the leaderboard; unknown prices stay blank instead
  of being guessed (#4).
- Leaderboard published on GitHub Pages and rebuilt on every push to `main` (#6).
- pass@3 (unbiased estimator) and 95% Wilson score intervals on the leaderboard (#2).
- `bench/diagnose.py`: replays the reference with every rule and pair of rules switched
  off to name the rules a wrong answer most likely ignored (#3).
- Tests for the Ollama provider against a local fake HTTP server (#9).
- First leaderboard results: Qwen2.5-Coder 7B and Llama 3.1 8B, 5 runs per scenario.
- Multi-scenario, multi-model harness: portfolio, warehouse and ledger scenarios with
  reference solvers; `generate.py` for Anthropic, OpenAI, Google and Ollama models;
  submissions run in a subprocess with a timeout; rule-mutant tests proving every rule
  changes the answer; CI on Python 3.11–3.13.

### Changed

- Ollama requests a 16k context and a 30-minute timeout so prompts and reasoning are not
  silently truncated (#4).
- Crashed runs show only the exception type, so the leaderboard is identical across
  Python versions.

### Earlier development

- 2026-04-20: original single-model audit (Gemini output against a ground-truth script).
- 2026-07-28: rebuilt as a multi-model audit harness.

[1.0.0]: https://github.com/wyplerszymon0-lab/llm-state-consistency-audit/releases/tag/v1.0.0
