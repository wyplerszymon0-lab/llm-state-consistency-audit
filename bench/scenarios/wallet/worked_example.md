The `CONVERT, PLN, EUR, 2000.00` on day 5:

- Premium status for day 5 comes from the end of day 4. The wallet then holds
  PLN 5500.00 (3000.00 plus the day-1 deposit), EUR 1050.00 (1200.00 minus the
  day-3 payment) and USD 500.00, so its value is
  `5500.00 + 1050 × 4.3150 + 500 × 3.9820 = 5500.00 + 4530.75 + 1991.00 = 12021.75`.
  That is below 20000, so the wallet is not premium and `s = 0.004`.
- The PLN balance 5500.00 is at least 2000.00, so the conversion happens.
- Step 1: `p = 2000.00 × 1 = 2000.00`.
- Step 2: `2000.00 ÷ 4.3150 × (1 − 0.004) = 461.64542...`, rounded half to even:
  `461.65` EUR.
- Balances: PLN `5500.00 − 2000.00 = 3500.00`; EUR `1050.00 + 461.65 = 1511.65`.
