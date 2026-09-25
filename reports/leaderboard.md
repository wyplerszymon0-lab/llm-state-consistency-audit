# LLM State-Consistency Audit — Leaderboard

_Generated 2026-09-25 by `run_audit.py` (prompt v1). Do not hand-edit — rerun the audit instead._

A run **passes** only if its answer is within the scenario tolerance (0.01) of the reference. Anything else — a wrong number, a crash, a timeout or no code — fails.

| Rank | Model | ledger | portfolio | warehouse | Pass rate |
| ---: | :--- | :---: | :---: | :---: | ---: |
| 1 | Gemini 3.1 Pro Reasoning † | – | 1/1 | – | 100% |
| 2 | Baseline (partial drift) † | – | 0/1 | – | 0% |

† **Gemini 3.1 Pro Reasoning**: frozen output from before this harness existed; generated with an earlier, unpreserved prompt, not prompt v1.  
† **Baseline (partial drift)**: hand-written synthetic fixture, not a model. It applies holding-cost drift only after SELLs, to show the harness catches silent state bugs.  

## Reference answers

| Scenario | Answer |
| :--- | ---: |
| Bank ledger (`ledger`) | 6553.73 |
| Portfolio ledger (`portfolio`) | 17072.00 |
| Perishable warehouse (`warehouse`) | 622.67 |

## Failed runs

| Model | Scenario | Run | Status | Answer | Expected | Detail |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| baseline-partial-drift | portfolio | run_1 | wrong | 17035.94 | 17072.00 | off by -36.06 |
