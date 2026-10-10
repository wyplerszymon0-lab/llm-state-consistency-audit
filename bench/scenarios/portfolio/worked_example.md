Transaction 4 (`SELL 15` from portfolio 101 at 120), starting from the state after
transactions 1-3:

- Lots before it: portfolio 101 `[(10, 100.3003), (10, 110.11)]`, portfolio 102
  `[(20, 200.4002)]`. (Lot costs have already drifted: 100 → 100.1 → 100.2001 →
  100.3003. The lot bought in transaction 3 cost 110 and drifted once to 110.11.)
- FIFO cost basis: `10 × 100.3003 + 5 × 110.11 = 1553.553`.
- Revenue: `15 × 120 = 1800`; gross profit `1800 − 1553.553 = 246.447`, so
  `last_sale_was_profitable` becomes true.
- Wealth after removing the sold units: cash `0` + holdings
  `5 × 110.11 + 20 × 200.4002 = 4558.554`, not above 10000, so no wealth tax.
- Gross profit is above 200, so the rate is `0.15`: tax `246.447 × 0.15 = 36.96705`.
- Cash: `0 + 1800 − 36.96705 = 1763.03295`.
- Drift: lots become 101 `[(5, 110.2201)]` and 102 `[(20, 200.6006)]`.
