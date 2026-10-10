Account Y on days 1-3:

- Day 1: `DEPOSIT 300.00` takes Y from 800.00 to 1100.00. End of day: the
  period minimum so far is 1100.00; interest accrued
  `1100 × 0.02 / 365 = 0.060273972...` (not rounded).
- Day 2: no events; Y stays 1100.00 and accrues another `0.060273972...`.
- Day 3: `WITHDRAW 1500.00`. `1100.00 − 1500.00 = −400.00` is not below −500, so the
  debit is applied. The balance was `>= 0` before and is `< 0` now, so the overdraft
  fee applies: Y = `−400.00 − 25.00 = −425.00`. End of day: the period minimum
  becomes −425.00 and the accrued interest gets `−425 × 0.18 / 365 = −0.209589041...`.
