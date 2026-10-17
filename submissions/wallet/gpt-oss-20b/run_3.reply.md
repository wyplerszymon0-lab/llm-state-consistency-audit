<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:41:31+00:00 -->

```python
import decimal
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

# set decimal context for enough precision
decimal.getcontext().prec = 28

# Events data
_EVENTS = [
    (1,  'DEPOSIT', 'PLN', None, '2500.00'),
    (3,  'PAY',     'EUR', None, '150.00'),
    (5,  'CONVERT', 'PLN', 'EUR', '2000.00'),
    (7,  'RATE',    'EUR', None, '4.3280'),
    (8,  'PAY',     'USD', None, '620.00'),
    (12, 'DEPOSIT', 'USD', None, '4000.00'),
    (14, 'CONVERT', 'USD', 'EUR', '1500.37'),
    (15, 'RATE',    'USD', None, '3.9455'),
    (18, 'DEPOSIT', 'PLN', None, '6000.00'),
    (20, 'CONVERT', 'EUR', 'PLN', '900.00'),
    (22, 'PAY',     'PLN', None, '9000.00'),
    (25, 'RATE',    'EUR', None, '4.2965'),
    (28, 'PAY',     'EUR', None, '2400.00'),
    (33, 'CONVERT', 'PLN', 'USD', '1800.00'),
    (36, 'PAY',     'USD', None, '5200.00'),
    (40, 'RATE',    'USD', None, '4.0110'),
    (41, 'DEPOSIT', 'EUR', None, '300.00'),
    (43, 'CONVERT', 'EUR', 'PLN', '50.00'),
    (45, 'PAY',     'PLN', None, '1500.00'),
    (48, 'CONVERT', 'USD', 'PLN', '755.00'),
    (52, 'RATE',    'EUR', None, '4.3402'),
    (55, 'PAY',     'EUR', None, '700.00'),
    (58, 'PAY',     'USD', None, '2000.00'),
]

# Helper for rounding
def round_half_even(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

def round_half_up(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def _wallet_value(balances, rates):
    """Return wallet value in PLN according to rules (no fee)."""
    pln = balances['PLN']
    eur_val = round_half_up(balances['EUR'] * rates['EUR'])
    usd_val = round_half_up(balances['USD'] * rates['USD'])
    return pln + eur_val + usd_val

def run() -> float:
    # initial balances and rates
    balances = {
        'PLN': Decimal('3000.00'),
        'EUR': Decimal('1200.00'),
        'USD': Decimal('500.00')
    }
    rates = {
        'PLN': Decimal('1.0000'),
        'EUR': Decimal('4.3150'),
        'USD': Decimal('3.9820')
    }

    # evaluate initial value for premium status
    premium = _wallet_value(balances, rates) >= Decimal('20000.00')

    # organize events by day
    events_by_day = {}
    for day, typ, cur, tgt, amt in _EVENTS:
        events_by_day.setdefault(day, []).append((typ, cur, tgt, Decimal(amt)))

    # simulate days 1..60
    for day in range(1, 61):
        # determine spread for this day
        s = Decimal('0.002') if premium else Decimal('0.004')

        # process events for this day in order
        for typ, cur, tgt, amt in events_by_day.get(day, []):
            if typ == 'DEPOSIT':
                balances[cur] += amt

            elif typ == 'RATE':
                rates[cur] = amt

            elif typ == 'CONVERT':
                # only if enough balance
                if balances[cur] >= amt:
                    # step 1
                    p = round_half_even(amt * rates[cur])
                    # step 2
                    received = round_half_even(p / rates[tgt] * (Decimal('1') - s))
                    balances[cur] -= amt
                    balances[tgt] += received

            elif typ == 'PAY':
                # enough balance
                if balances[cur] >= amt:
                    balances[cur] -= amt
                else:
                    shortfall = amt - balances[cur]
                    # cost in PLN
                    cost = round_half_even(shortfall * rates[cur] * (Decimal('1') + s + Decimal('0.005')))
                    if cur == 'PLN' or balances['PLN'] < cost:
                        # declined
                        balances['PLN'] -= Decimal('10.00')
                    else:
                        # payment accepted
                        balances[cur] = Decimal('0')
                        balances['PLN'] -= cost

        # end of day: compute value before fee
        value_before_fee = _wallet_value(balances, rates)

        # monthly fee check
        if day in (30, 60) and value_before_fee < Decimal('5000.00'):
            balances['PLN'] -= Decimal('15.00')

        # compute value after fee for status update
        value_after_fee = _wallet_value(balances, rates)

        # set premium for next day
        premium = value_after_fee >= Decimal('20000.00')

    # after day 60, final value already includes any fee
    final_value = _wallet_value(balances, rates)
    # round to 2 decimals half away from zero (though it should already be)
    final_value = round_half_up(final_value)

    return float(final_value)
```