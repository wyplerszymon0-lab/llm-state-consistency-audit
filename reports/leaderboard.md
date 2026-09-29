# LLM State-Consistency Audit — Leaderboard

_Generated 2026-09-29 by `run_audit.py` (prompt v1). Do not hand-edit — rerun the audit instead._

A run **passes** only if its answer is within the scenario tolerance (0.01) of the reference. Anything else — a wrong number, a crash, a timeout or no code — fails.

| Rank | Model | ledger | portfolio | warehouse | Pass rate [95% CI] | pass@3 |
| ---: | :--- | :---: | :---: | :---: | ---: | ---: |
| 1 | Gemini 3.1 Pro Reasoning † | – | 1/1 | – | 100% [21%–100%] | – |
| 2 | qwen2.5-coder:7b | 0/5 | 1/5 | 0/5 | 7% [1%–30%] | 20% |
| 3 | llama3.1:8b | 0/5 | 0/5 | 0/5 | 0% [0%–20%] | 0% |
| 4 | Baseline (partial drift) † | – | 0/1 | – | 0% [0%–79%] | – |

*Pass rate* pools every run of the model; the 95% Wilson interval shows how much it could move with more runs. *pass@3* is the unbiased estimate (Chen et al., 2021) of the chance that at least one of 3 attempts passes, averaged over scenarios with at least 3 runs.

† **Gemini 3.1 Pro Reasoning**: frozen output from before this harness existed; generated with an earlier, unpreserved prompt, not prompt v1.  
† **Baseline (partial drift)**: hand-written synthetic fixture, not a model. It applies holding-cost drift only after SELLs, to show the harness catches silent state bugs.  

## Reference answers

| Scenario | Answer |
| :--- | ---: |
| Bank ledger (`ledger`) | 6553.73 |
| Portfolio ledger (`portfolio`) | 17072.00 |
| Perishable warehouse (`warehouse`) | 622.67 |

## Failed runs

For every wrong answer the audit also runs the reference with each rule, and each pair of rules, switched off. If the answer matches one of those exactly, the detail names the rules the program most likely ignored.

| Model | Scenario | Run | Status | Answer | Expected | Detail |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
| qwen2.5-coder-7b | ledger | run_1 | wrong | 4424.00 | 6553.73 | off by -2129.73 |
| qwen2.5-coder-7b | ledger | run_2 | wrong | 6539.00 | 6553.73 | off by -14.73 |
| qwen2.5-coder-7b | ledger | run_3 | wrong | 865.00 | 6553.73 | off by -5688.73 |
| qwen2.5-coder-7b | ledger | run_4 | wrong | -3105.04 | 6553.73 | off by -9658.77 |
| qwen2.5-coder-7b | ledger | run_5 | wrong | 19345.00 | 6553.73 | off by +12791.27 |
| qwen2.5-coder-7b | portfolio | run_2 | error | – | 17072.00 | `NameError` |
| qwen2.5-coder-7b | portfolio | run_3 | error | – | 17072.00 | `AttributeError` |
| qwen2.5-coder-7b | portfolio | run_4 | error | – | 17072.00 | `TypeError` |
| qwen2.5-coder-7b | portfolio | run_5 | wrong | 17026.06 | 17072.00 | off by -45.94 |
| qwen2.5-coder-7b | warehouse | run_1 | error | – | 622.67 | `UnboundLocalError` |
| qwen2.5-coder-7b | warehouse | run_2 | error | – | 622.67 | `UnboundLocalError` |
| qwen2.5-coder-7b | warehouse | run_3 | error | – | 622.67 | `AttributeError` |
| qwen2.5-coder-7b | warehouse | run_4 | wrong | -384.10 | 622.67 | off by -1006.77 |
| qwen2.5-coder-7b | warehouse | run_5 | error | – | 622.67 | `UnboundLocalError` |
| llama3.1-8b | ledger | run_1 | wrong | 3798.00 | 6553.73 | off by -2755.73 |
| llama3.1-8b | ledger | run_2 | wrong | 5449.00 | 6553.73 | off by -1104.73 |
| llama3.1-8b | ledger | run_3 | wrong | 8450.00 | 6553.73 | off by +1896.27 |
| llama3.1-8b | ledger | run_4 | error | – | 6553.73 | `SyntaxError` |
| llama3.1-8b | ledger | run_5 | wrong | 6570.76 | 6553.73 | off by +17.03 |
| llama3.1-8b | portfolio | run_1 | wrong | -8733.49 | 17072.00 | off by -25805.49 |
| llama3.1-8b | portfolio | run_2 | error | – | 17072.00 | `SyntaxError` |
| llama3.1-8b | portfolio | run_3 | wrong | 29388.35 | 17072.00 | off by +12316.35 |
| llama3.1-8b | portfolio | run_4 | error | – | 17072.00 | `IndexError` |
| llama3.1-8b | portfolio | run_5 | error | – | 17072.00 | `AttributeError` |
| llama3.1-8b | warehouse | run_1 | error | – | 622.67 | `IndexError` |
| llama3.1-8b | warehouse | run_2 | error | – | 622.67 | `TypeError` |
| llama3.1-8b | warehouse | run_3 | error | – | 622.67 | `AttributeError` |
| llama3.1-8b | warehouse | run_4 | error | – | 622.67 | `KeyError` |
| llama3.1-8b | warehouse | run_5 | wrong | 771.53 | 622.67 | off by +148.86 |
| baseline-partial-drift | portfolio | run_1 | wrong | 17035.94 | 17072.00 | off by -36.06 |
