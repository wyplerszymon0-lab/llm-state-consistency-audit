# LLM State-Consistency Audit

A benchmark for one specific failure mode of LLM-written code: **losing track of
global state across a sequence of dependent operations.**

Each scenario is a small simulation (a portfolio, a warehouse, a bank ledger)
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
   the raw reply plus the extracted Python module under `submissions/`.
2. `run_audit.py` executes every submission in a separate process (with a timeout),
   compares `run()` with the reference answer and writes
   [`reports/leaderboard.md`](reports/leaderboard.md).

A run **passes** only if it is within **0.01** of the reference. A wrong number,
a crash, a timeout and a reply without code all count as failures. Run each
model several times: one sample says little about a non-deterministic model.

## Scenarios

| Scenario | Interacting state | Reference |
|---|---|---:|
| [`portfolio`](bench/scenarios/portfolio/prompt.md) | FIFO lots across 3 portfolios, global "last sale was profitable" flag, wealth tax computed mid-transaction, cost drift after every transaction | 17072.00 |
| [`warehouse`](bench/scenarios/warehouse/prompt.md) | Perishable batches (expiry, FEFO picking), backorders filled at a discount by later deliveries, automatic reorders with lead time | 622.67 |
| [`ledger`](bench/scenarios/ledger/prompt.md) | Overdraft limit and fees, rejected debits, tiered daily interest accrued at full precision, period close with a minimum-balance fee waiver | 6553.73 |

Every rule is load-bearing: the test suite switches each rule off in turn and
checks that the reference answer changes (`tests/test_scenarios.py`).

## Results so far

Full table: [`reports/leaderboard.md`](reports/leaderboard.md). Five runs per model and scenario, prompt v1, run locally through Ollama (default sampling, 8k context) on 2026-09-26/27:

| Model | portfolio | warehouse | ledger | Pass rate |
| :--- | :---: | :---: | :---: | ---: |
| Qwen2.5-Coder 7B | 1/5 | 0/5 | 0/5 | 7% |
| Llama 3.1 8B | 0/5 | 0/5 | 0/5 | 0% |

What the 29 failed runs show:

- **Most programs don't survive their own state.** 15 of 29 crashed, and the most common crashes are state bugs rather than typos: `UnboundLocalError` and `NameError` from accumulators assigned inside nested functions, a `nonlocal` that points nowhere, `Decimal` mixed with `float`, a `run()` written as a class method.
- **The dangerous failures are the quiet ones.** Two ledger runs finished cleanly and were off by only −14.73 and +17.03 on a 6,553.73 answer, which is the kind of mistake a reviewer would wave through. The harness exists to catch exactly those.
- **The warehouse scenario broke both models**: 0/10, and 8 of the 10 runs crashed.

These are 7–8B models on a consumer GPU, so low scores are expected; the table becomes informative once frontier models are added (`python generate.py anthropic:<model> openai:<model> google:<model> --runs 5`). Until a strong model passes the new warehouse and ledger prompts, part of a low score could also reflect how demanding those specs are.

## Usage

```bash
pip install -r requirements.txt       # SDKs for the providers you use
export ANTHROPIC_API_KEY=...          # and/or OPENAI_API_KEY, GEMINI_API_KEY

# 3 runs per scenario for each model (provider:model_id)
python generate.py anthropic:claude-opus-5 openai:<model-id> google:<model-id> --runs 3

# local models through Ollama
python generate.py ollama:qwen3-coder --scenario ledger --runs 5

python run_audit.py                   # score everything, rewrite the leaderboard
```

Providers: `anthropic`, `openai`, `google`, `ollama`. New runs never overwrite old
ones; they get the next free number.

> **Security:** submissions are model-generated code and run with your user's
> permissions. The subprocess isolates crashes and infinite loops, not malicious
> code. Run untrusted submissions in a container or VM.

## Adding a scenario

Create `bench/scenarios/<name>/` with:

- `prompt.md` — the full specification the model sees, starting with a `# Title`.
  It must be unambiguous: every ordering and rounding decision spelled out.
- `reference.py` — a `run() -> float` that implements the spec exactly, with the
  tunable rules as module-level constants (so the tests can switch them off).

Then pin the answer and add rule mutants in `tests/test_scenarios.py`.

## Project layout

```
bench/
  scenarios/<name>/    prompt.md + reference.py for each scenario
  prompting.py         shared instructions wrapped around every prompt (versioned)
  providers.py         Anthropic / OpenAI / Google / Ollama clients
  extract.py           pulls the code block out of a reply
  sandbox.py           runs a submission in a subprocess with a timeout
  scoring.py           classifies every run: pass / wrong / error / timeout / no_code
  report.py            renders the leaderboard
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
