# Portfolio ledger

Simulate three investment portfolios that share one cash account.

## Data

Process these transactions strictly in the order given.
Columns: `txn_id, portfolio_id, type, quantity, unit_price`

```
1, 101, BUY, 10, 100
2, 102, BUY, 20, 200
3, 101, BUY, 10, 110
4, 101, SELL, 15, 120
5, 102, SELL, 10, 210
6, 101, BUY, 20, 115
7, 103, BUY, 50, 50
8, 101, SELL, 10, 130
9, 102, BUY, 15, 205
10, 103, SELL, 20, 55
11, 101, BUY, 10, 120
12, 101, SELL, 15, 140
13, 102, SELL, 20, 215
14, 103, BUY, 10, 60
15, 101, SELL, 5, 145
```

## State

- `cash` starts at 0. Buying does **not** reduce cash (purchases are funded externally).
- Each portfolio holds a FIFO queue of lots. A lot is `(quantity, unit_cost)`.
- A global flag `last_sale_was_profitable` starts as `False`.

## Rules

1. **BUY**: the lot's unit cost is `unit_price`, or `unit_price * 1.01` if
   `last_sale_was_profitable` is `True`. Append the lot to that portfolio's queue.
   The flag is global, across all portfolios, and is only changed by SELLs.
2. **SELL**: remove `quantity` units from that portfolio's queue in FIFO order,
   splitting a lot if needed. `cost_basis` is the sum of `units * unit_cost`
   over the removed units, using each lot's *current* unit cost.
   - `revenue = quantity * unit_price` (the 1.01 modifier never applies to sells)
   - `gross_profit = revenue - cost_basis`
   - set `last_sale_was_profitable = gross_profit > 0`
   - **Wealth tax check**: `wealth = cash + sum(quantity * unit_cost)` over all
     remaining lots in all portfolios, computed *after* the sold units are removed
     and *before* this sale's revenue is added to cash. If `wealth > 10000`,
     `penalty = 0.02`, otherwise `0`.
   - `base_rate = 0.15` if `gross_profit > 200`, otherwise `0.05`
   - `tax = max(0, gross_profit * (base_rate + penalty))`
   - `cash += revenue - tax`
3. **Holding cost drift**: after *every* transaction (buy or sell), multiply the
   unit cost of every lot still held (in every portfolio, including a lot bought in
   this same transaction) by `1.001` and round it to 4 decimal places with Python's
   built-in `round`.

## Answer

After all transactions, the answer is
`cash + sum(quantity * unit_cost)` over all remaining lots, rounded to 2 decimal places.
