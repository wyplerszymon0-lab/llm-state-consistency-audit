# Multi-currency wallet

Simulate one wallet holding three currencies over days 1 to 60 (inclusive).

## Opening state

Balances: `PLN = 3000.00`, `EUR = 1200.00`, `USD = 500.00`

Exchange rates, in PLN per unit: `EUR = 4.3150`, `USD = 3.9820` (and `PLN = 1`).

## Events

Columns: `day, type, currency, target_currency, amount`. Events on the same day are
processed in the order listed.

```
1, DEPOSIT, PLN, -, 2500.00
3, PAY, EUR, -, 150.00
5, CONVERT, PLN, EUR, 2000.00
7, RATE, EUR, -, 4.3280
8, PAY, USD, -, 620.00
12, DEPOSIT, USD, -, 4000.00
14, CONVERT, USD, EUR, 1500.37
15, RATE, USD, -, 3.9455
18, DEPOSIT, PLN, -, 6000.00
20, CONVERT, EUR, PLN, 900.00
22, PAY, PLN, -, 9000.00
25, RATE, EUR, -, 4.2965
28, PAY, EUR, -, 2400.00
33, CONVERT, PLN, USD, 1800.00
36, PAY, USD, -, 5200.00
40, RATE, USD, -, 4.0110
41, DEPOSIT, EUR, -, 300.00
43, CONVERT, EUR, PLN, 50.00
45, PAY, PLN, -, 1500.00
48, CONVERT, USD, PLN, 755.00
52, RATE, EUR, -, 4.3402
55, PAY, EUR, -, 700.00
58, PAY, USD, -, 2000.00
```

## Rules

**Rounding.** Conversions round to 2 decimal places with **round half to even**
(banker's rounding: `x.xx5` goes to the even cent). Valuations round to 2 decimal
places with **round half away from zero**. Nothing else is rounded.

**Wallet value** in PLN: the PLN balance plus, for EUR and USD, `balance × rate`
rounded to 2 decimals (half away from zero), using the rates in force at that moment.

**Premium status.** The wallet is premium while its value is at least `20000.00`.
The status is set from the opening balances and rates before day 1, and then
re-evaluated at the end of each day (after the monthly fee, if any). It applies to
everything on the following day.

**Spread** `s` = `0.002` while premium, otherwise `0.004`.

- **DEPOSIT**: add `amount` to that currency's balance.
- **RATE**: from this event on, the currency's rate is `amount`.
- **CONVERT** `amount` of `currency` into `target_currency`. If the balance in
  `currency` is smaller than `amount`, nothing happens. Otherwise every conversion
  goes through PLN in two rounded steps:
  1. `p = amount × rate(currency)`, rounded half to even;
  2. received `= p ÷ rate(target_currency) × (1 − s)`, rounded half to even.

  Subtract `amount` from `currency` and add the received amount to `target_currency`.
- **PAY** `amount` by card in `currency`:
  - if the balance in `currency` is at least `amount`, subtract it;
  - otherwise the shortfall `amount − balance(currency)` is bought from PLN at
    `cost = shortfall × rate(currency) × (1 + s + 0.005)`, rounded half to even.
    If `currency` is PLN, or the PLN balance is smaller than `cost`, the payment is
    **declined**: nothing is paid, but a decline fee of `10.00` is subtracted from
    PLN (even if that makes it negative). Otherwise set the `currency` balance to
    `0` and subtract `cost` from PLN.

**Monthly fee.** At the end of days 30 and 60, after that day's events: if the
wallet value is below `5000.00`, subtract `15.00` from PLN.

## Answer

The wallet value in PLN at the end of day 60 (after the monthly fee), rounded to 2
decimal places.
