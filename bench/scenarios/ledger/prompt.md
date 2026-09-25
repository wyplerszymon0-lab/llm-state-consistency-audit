# Bank ledger

Simulate three bank accounts over days 1 to 60 (inclusive).

## Opening balances

`X = 4200.00`, `Y = 800.00`, `Z = 12000.00`

## Events

Columns: `day, type, account, target_account, amount`. Events on the same day are
processed in the order listed.

```
1, DEPOSIT, Y, -, 300.00
3, WITHDRAW, Y, -, 1500.00
5, TRANSFER, Z, X, 2500.00
8, WITHDRAW, Y, -, 200.00
10, DEPOSIT, Y, -, 2000.00
12, TRANSFER, X, Y, 800.00
15, WITHDRAW, Z, -, 8000.00
20, WITHDRAW, Z, -, 700.00
25, TRANSFER, Y, Z, 1200.00
33, WITHDRAW, X, -, 6300.00
36, DEPOSIT, X, -, 1000.00
40, TRANSFER, Z, Y, 2100.00
45, WITHDRAW, Y, -, 5000.00
47, DEPOSIT, Z, -, 3000.00
50, TRANSFER, Y, X, 1000.00
55, WITHDRAW, X, -, 300.00
58, DEPOSIT, Y, -, 150.00
```

## Transaction rules

- **DEPOSIT**: add `amount` to the account.
- **WITHDRAW**: a debit of `amount` from the account.
- **TRANSFER**: a debit of `amount + fee` from the source account, where
  `fee = 1.00` if `amount > 1000`, otherwise `0`. If the debit is applied, the target
  account receives `amount` (not the fee). If it is rejected, the target gets nothing.

A **debit** of `total` from an account with balance `before`:

1. If `before - total < -500`, the debit is **rejected**: nothing is withdrawn, but a
   rejection fee of `15.00` is subtracted from the balance (even if that takes the
   balance below -500).
2. Otherwise subtract `total`. If `before >= 0` and the new balance is `< 0`, also
   subtract an overdraft fee of `25.00`.

Rejection fees, overdraft fees and maintenance fees never trigger other fees.

## End of each day

After the day's events, for every day `d` from 1 to 60 (including days with no
events), for each account:

1. **Minimum balance tracking**: record the balance as an end-of-day balance of the
   current 30-day period (days 1–30 and 31–60).
2. **Interest accrual**: using the current balance `b`, add to that account's
   `accrued_interest` (kept at full precision, never rounded while accruing):
   - if `b > 0`: `min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365`
   - if `b <= 0`: `b * 0.18 / 365` (a negative amount, i.e. overdraft interest)
3. **Period close** (only when `d` is 30 or 60):
   - round `accrued_interest` to 2 decimal places, rounding halves away from zero,
     add it to the balance, and reset `accrued_interest` to 0;
   - then, if the lowest end-of-day balance recorded during this period is below
     `1000`, subtract a maintenance fee of `5.00`.

## Answer

The sum of the three balances after the day 60 close, rounded to 2 decimal places.
