# LLM State-Consistency Audit

A benchmark for one specific failure mode of LLM-written code: **losing track of
global state across a sequence of dependent operations.**

Each scenario is a small simulation (a portfolio, a warehouse, a bank ledger, a multi-currency wallet)
where several rules interact through shared state: a flag set by one event changes
the next, costs compound after every step, fees depend on balances that other
events just changed. Get one dependency stale or mistimed and the program still
runs and still prints a plausible number. It is just wrong. Unit tests on isolated
functions rarely catch this. This harness does.

## How it works

```
prompt.md ──► model ──► reply ──► extracted run() ──► subprocess ──► value
                                                                      │
reference.py ────────────────────────────────────────────► expected ──┴─► pass / fail
```

1. `generate.py` sends each scenario's prompt to the models you choose and saves
   the raw reply plus the extracted Python module under `submissions/`, and records
   each run's latency, token usage and cost (`run_N.meta.json`; list prices in
   `bench/pricing.py`, local models free, unknown prices left blank).
2. `run_audit.py` executes every submission in a separate process (with a timeout),
   compares `run()` with the reference answer and writes
   [`reports/leaderboard.md`](reports/leaderboard.md).

A run **passes** only if it is within **0.01** of the reference. A wrong number,
a crash, a timeout and a reply without code all count as failures. Run each
model several times: one sample says little about a non-deterministic model.
The leaderboard therefore reports a 95% Wilson interval for each pass rate and
pass@3, the unbiased estimate (Chen et al., 2021) that at least one of three
attempts passes (`bench/stats.py`).

## Scenarios

| Scenario | Interacting state | Reference |
|---|---|---:|
| [`portfolio`](bench/scenarios/portfolio/prompt.md) | FIFO lots across 3 portfolios, global "last sale was profitable" flag, wealth tax computed mid-transaction, cost drift after every transaction | 17072.00 |
| [`warehouse`](bench/scenarios/warehouse/prompt.md) | Perishable batches (expiry, FEFO picking), backorders filled at a discount by later deliveries, automatic reorders with lead time | 622.67 |
| [`ledger`](bench/scenarios/ledger/prompt.md) | Overdraft limit and fees, rejected debits, tiered daily interest accrued at full precision, period close with a minimum-balance fee waiver | 6553.73 |
| [`wallet`](bench/scenarios/wallet/prompt.md) | Conversions at the rate in force at the time, two rounding modes (half-even for conversions, half-up for valuations), a spread that depends on yesterday's converted wallet value, card payments that auto-convert a shortfall or are declined with a fee, a monthly fee on the converted total | 2351.14 |

Every rule is load-bearing: each reference module lists its rules in `RULES`,
and the test suite switches each one off in turn and checks that the answer
changes (`tests/test_scenarios.py`). The same list powers the diagnosis in the
leaderboard: a wrong answer that equals the reference with some rules off names
those rules (`bench/diagnose.py`).

The `wallet` prompt was also checked the other way round: a second implementation written from `prompt.md` alone, without the reference, gives the same 2351.14. Its two rounding rules move the answer by only a cent each, so the events include two exact half-cent ties (e.g. 755.00 USD × 4.0110 = 3028.305 PLN); together they shift the answer by 0.02, more than the 0.01 tolerance, which makes "half-even rounding" a rule a program can be caught ignoring. Rounding at the PLN step of a cross-currency conversion is specified but not counted as a rule: skipping it changes the answer by less than a cent.

## Results so far

Full table: **[live leaderboard](https://wyplerszymon0-lab.github.io/llm-state-consistency-audit/)** (rebuilt on every push) or [`reports/leaderboard.md`](reports/leaderboard.md). Prompt v1, run locally through Ollama on a laptop with an 8 GB GPU (RTX 5050) and 32 GB RAM, 2026-09-26 to 10-16:

| Model | portfolio | warehouse | ledger | wallet | Pass rate [95% CI] | pass@3 | Median time per run |
| :--- | :---: | :---: | :---: | :---: | ---: | ---: | ---: |
| gpt-oss 20B (reasoning, MoE) | 5/5 | 4/5 | 4/5 | 5/5 | **90% [70–97%]** | 100% | 202 s |
| Qwen3-Coder 30B (MoE) | 4/5 | 0/5 | 4/5 | 1/5 | 45% [26–66%] | 65% | 71 s |
| Qwen2.5-Coder 14B | 3/5 | 0/5 | 0/5 | 0/3 | 17% [6–39%] | 25% | 237 s |
| Qwen2.5-Coder 7B | 1/5 | 0/5 | 0/5 | 0/5 | 5% [1–24%] | 15% | 27 s |
| Llama 3.1 8B | 0/5 | 0/5 | 0/5 | – | 0% [0–20%] | 0% | – |
| Qwen3 8B (reasoning), 1 run | – | – | 1/1 | – | 100% [21–100%] | – | 1,634 s |

The `wallet` runs were added on 2026-10-10 with the prompt study below (3 for the 14B model to save time, ~4 min per run). gpt-oss and Qwen3-Coder were added on 2026-10-16 (issue #8): both are mixture-of-experts models (about 3–4B parameters active per token), which is why a 20–30B model runs on an 8 GB GPU with the rest in system RAM. Median times are this laptop's and include each model's first run, which also loads the model (746 s and 250 s).

### Does a worked example help? (prompt v2)

Prompt v2 is prompt v1 plus one step of the simulation worked out by hand: the first SELL in `portfolio`, a backordered order and its refill in `warehouse`, an overdraft in `ledger`, a currency conversion in `wallet` ([`worked_example.md`](bench/scenarios/portfolio/worked_example.md) in each scenario; every number is checked against a truncated reference run in the tests). Same models, same machine, 2026-10-10:

| Model | Prompt | portfolio | warehouse | ledger | wallet | Pooled [95% CI] |
| :--- | :--- | :---: | :---: | :---: | :---: | ---: |
| Qwen2.5-Coder 14B | v1 | 3/5 | 0/5 | 0/5 | 0/3 | 3/18 [6–39%] |
| | v2 | 1/3 | 0/3 | 0/3 | 0/3 | 1/12 [1–35%] |
| Qwen2.5-Coder 7B | v1 | 1/5 | 0/5 | 0/5 | 0/5 | 1/20 [1–24%] |
| | v2 | 0/5 | 0/5 | 0/5 | 0/5 | 0/20 [0–16%] |

**No improvement.** Both models passed fewer runs with the example than without it, but the intervals overlap almost entirely, so the honest reading is "no measurable effect at this sample size", not "examples hurt". The 14B model got 3 v2 runs per scenario instead of 5 to keep the study to an afternoon, which widens its interval.

The failures say why an example of one step does not fix the program as a whole:

- **The example's own step is broken anyway.** One 14B and one 7B v2 portfolio program both return 3,749.96 (off by −13,322.04). Each consumes FIFO lots by counting `quantity` down to 0 and only then computes `revenue = quantity * price`, so every sale earns nothing — even though the worked example spells out `Revenue: 15 × 120 = 1800`.
- **Rules outside the example stay missed.** Two of three 14B v2 wallet answers are +15.01 off, the reference with the monthly fee switched off exactly; the example shows a conversion, not the end-of-month check.
- **Crashes don't go away.** 16 of the 31 failed v2 runs are crashes (`NameError`, `KeyError`, `IndexError`, `UnboundLocalError`, ...), the same state bugs as with prompt v1.

What the runs show:

- **A newer generation changed the picture more than size did.** Doubling Qwen2.5-Coder from 7B to 14B took portfolio from 1/5 to 3/5 and left warehouse and ledger at 0/5. Qwen3-Coder 30B passed ledger 4/5, and gpt-oss 20B, which reasons before it writes code, passed 18 of 20 runs, including the first local passes on warehouse (4/5). Its interval (70–97%) does not overlap the 14B coder's (6–39%), so that gap is not luck of the draw.
- **Two models, one bug.** gpt-oss and Qwen3-Coder each failed one ledger run with exactly the same answer, 6,543.71 (−10.02). Both track the period's lowest balance across all three accounts instead of per account, so a low balance in one account charges the 5.00 maintenance fee to every account. Running the reference with the minimum shared across accounts gives 6,543.71 to the cent. This cross-account state leak is the kind of bug the benchmark was built to catch.
- **A reasoning model solved the ledger on its only try**, the first pass in 16 local ledger attempts. It cost ~16k output tokens (mostly thinking) and 27 minutes on this GPU versus ~1.3k tokens and ~4 minutes for the 14B coder; one run is a signal, not a result, and running 5 per scenario wasn't practical here.
- **Most programs don't survive their own state.** With prompt v1, across the 7B, 8B and 14B models, a large share of failures are crashes from state bugs rather than typos: `UnboundLocalError` and `NameError` from accumulators assigned inside nested functions, a `nonlocal` that points nowhere, `Decimal` mixed with `float`, a `run()` written as a class method.
- **The dangerous failures are the quiet ones.** Several runs finished cleanly and were off by a few units on answers in the thousands (−14.73 and +17.03 on 6,553.73; +6.79; +18.31 on 17,072.00) — mistakes a reviewer would wave through.
- **The diagnosis names a skipped rule only now and then.** 5 of the 94 failed runs in the leaderboard equal the reference with one or two rules switched off exactly (the 2% wealth tax once, the monthly fee or the premium spread in wallet four times), so those programs most likely ignored the rule. The other wrong answers match no single or paired omission: the rules were implemented, but wrongly, like the shared minimum above.

Cost and speed per model are in the leaderboard (every local run costs $0; latency is this laptop's), with a chart of pass rate against median time per run ([`reports/accuracy_vs_time.svg`](reports/accuracy_vs_time.svg)): gpt-oss is the most accurate local model, Qwen3-Coder answers about three times faster at half the pass rate. The table becomes truly informative once frontier models are added (`python generate.py anthropic:<model> openai:<model> google:<model> --runs 5`).

## Usage

```bash
pip install -r requirements.txt       # SDKs for the providers you use
export ANTHROPIC_API_KEY=...          # and/or OPENAI_API_KEY, GEMINI_API_KEY

# 3 runs per scenario for each model (provider:model_id)
python generate.py anthropic:claude-opus-5 openai:<model-id> google:<model-id> --runs 3

# local models through Ollama
python generate.py ollama:qwen3-coder --scenario ledger --runs 5

# prompt v2 (adds one worked step); saved as <model>-prompt-v2
python generate.py ollama:qwen2.5-coder:14b --prompt-version 2 --runs 5

python run_audit.py                   # score everything, rewrite the leaderboard
python run_audit.py --sandbox docker  # the same, each submission in a locked-down container
```

Providers: `anthropic`, `openai`, `google`, `ollama`. New runs never overwrite old
ones; they get the next free number.

> **Security:** submissions are model-generated code. By default they run in a
> subprocess with your user's permissions, which isolates crashes and infinite
> loops, not malicious code. For code you have not read, use `--sandbox docker`:
> each submission runs in a throwaway `python:3.12-slim` container with no network,
> a read-only file system (only a 16 MB `/tmp` is writable), 256 MB of memory and no
> swap, one CPU, at most 64 processes, no Linux capabilities, as user `nobody`, with
> only the submission itself mounted (read-only). The tests run real containers and
> check each of these: no network, no writes, the memory limit, the timeout, the user.
> Scoring all 48 recorded runs this way gives the same leaderboard as the
> subprocess mode, in about 40 s (container start-up costs ~1 s per run).

## Adding a scenario

Create `bench/scenarios/<name>/` with:

- `prompt.md` — the full specification the model sees, starting with a `# Title`.
  It must be unambiguous: every ordering and rounding decision spelled out.
- `reference.py` — a `run() -> float` that implements the spec exactly, with the
  tunable rules as module-level constants (so the tests can switch them off).
- `worked_example.md` — one step computed by hand, used by prompt v2. Check its
  numbers with a truncated reference run in `tests/test_scenarios.py`.

Then pin the answer and add rule mutants in `tests/test_scenarios.py`.

## Project layout

```
bench/
  scenarios/<name>/    prompt.md, reference.py and worked_example.md for each scenario
  prompting.py         shared instructions wrapped around every prompt (v1, v2)
  providers.py         Anthropic / OpenAI / Google / Ollama clients (reply + token usage)
  pricing.py           list prices for the cost column
  extract.py           pulls the code block out of a reply
  sandbox.py           runs a submission in a subprocess or a locked-down Docker container
  scoring.py           classifies every run: pass / wrong / error / timeout / no_code
  diagnose.py          matches wrong answers to rules switched off
  stats.py             pass@k and Wilson confidence intervals
  report.py            renders the leaderboard
  site.py              turns it into the GitHub Pages site
submissions/<scenario>/<model>/run_N.{reply.md,py}
generate.py            CLI: query models
run_audit.py           CLI: score and report
```

## Development

```bash
pip install -r requirements-dev.txt
pytest
```

CI runs the tests on Python 3.11–3.13 and fails if `reports/leaderboard.md` is
out of date.

## License

MIT
