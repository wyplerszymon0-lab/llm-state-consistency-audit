<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:48:21+00:00 -->

```python
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, getcontext

def run() -> float:
    getcontext().prec = 28  # default precision is enough

    # Helper rounding functions
    TWO_DECIMAL = Decimal('0.01')
    def round_half_even(v: Decimal) -> Decimal:
        return v.quantize(TWO_DECIMAL, rounding=ROUND_HALF_EVEN)

    def round_half_up(v: Decimal) -> Decimal:
        return v.quantize(TWO_DECIMAL, rounding=ROUND_HALF_UP)

    # Initial balances and rates
    balances = {
        'PLN': Decimal('3000.00'),
        'EUR': Decimal('1200.00'),
        'USD': Decimal('500.00')
    }
    rates = {
        'PLN': Decimal('1'),
        'EUR': Decimal('4.3150'),
        'USD': Decimal('3.9820')
    }

    # Constants
    ONE = Decimal('1')
    TEN = Decimal('10.00')
    FIFTEEN = Decimal('15.00')
    FIVE_THOUSAND = Decimal('5000.00')
    TWENTY_THOUSAND = Decimal('20000.00')
    FIVE_HUNDREDTH = Decimal('0.005')
    S_PREMIUM = Decimal('0.002')
    S_STANDARD = Decimal('0.004')

    # Events list
    raw_events = [
        (1,  'DEPOSIT', 'PLN', None,          Decimal('2500.00')),
        (3,  'PAY',     'EUR', None,          Decimal('150.00')),
        (5,  'CONVERT', 'PLN', 'EUR',         Decimal('2000.00')),
        (7,  'RATE',    'EUR', None,          Decimal('4.3280')),
        (8,  'PAY',     'USD', None,          Decimal('620.00')),
        (12, 'DEPOSIT', 'USD', None,          Decimal('4000.00')),
        (14, 'CONVERT', 'USD', 'EUR',         Decimal('1500.37')),
        (15, 'RATE',    'USD', None,          Decimal('3.9455')),
        (18, 'DEPOSIT', 'PLN', None,          Decimal('6000.00')),
        (20, 'CONVERT', 'EUR', 'PLN',         Decimal('900.00')),
        (22, 'PAY',     'PLN', None,          Decimal('9000.00')),
        (25, 'RATE',    'EUR', None,          Decimal('4.2965')),
        (28, 'PAY',     'EUR', None,          Decimal('2400.00')),
        (33, 'CONVERT', 'PLN', 'USD',         Decimal('1800.00')),
        (36, 'PAY',     'USD', None,          Decimal('5200.00')),
        (40, 'RATE',    'USD', None,          Decimal('4.0110')),
        (41, 'DEPOSIT', 'EUR', None,          Decimal('300.00')),
        (43, 'CONVERT', 'EUR', 'PLN',         Decimal('50.00')),
        (45, 'PAY',     'PLN', None,          Decimal('1500.00')),
        (48, 'CONVERT', 'USD', 'PLN',         Decimal('755.00')),
        (52, 'RATE',    'EUR', None,          Decimal('4.3402')),
        (55, 'PAY',     'EUR', None,          Decimal('700.00')),
        (58, 'PAY',     'USD', None,          Decimal('2000.00')),
    ]

    # Organize events per day
    events_by_day = {}
    for day, typ, cur, tgt, amt in raw_events:
        events_by_day.setdefault(day, []).append((typ, cur, tgt, amt))

    # Helper to compute wallet value
    def wallet_value() -> Decimal:
        val = balances['PLN']
        for cur in ('EUR', 'USD'):
            prod = balances[cur] * rates[cur]
            prod = round_half_up(prod)
            val += prod
        return val

    # Initial premium status before day 1
    premium = wallet_value() >= TWENTY_THOUSAND

    # Simulation over days 1..60
    for day in range(1, 61):
        s = S_PREMIUM if premium else S_STANDARD

        # Process events for the day
        for typ, cur, tgt, amt in events_by_day.get(day, []):
            if typ == 'DEPOSIT':
                balances[cur] += amt
            elif typ == 'RATE':
                rates[cur] = amt
            elif typ == 'CONVERT':
                if balances[cur] < amt:
                    continue  # nothing happens
                # conversion steps
                rate_from = rates[cur]
                rate_to = rates[tgt]
                p = round_half_even(amt * rate_from)
                temp = p / rate_to
                received = round_half_even(temp * (ONE - s))
                balances[cur] -= amt
                balances[tgt] += received
            elif typ == 'PAY':
                if balances[cur] >= amt:
                    balances[cur] -= amt
                else:
                    shortfall = amt - balances[cur]
                    cost_raw = shortfall * rates[cur] * (ONE + s + FIVE_HUNDREDTH)
                    cost = round_half_even(cost_raw)
                    if cur == 'PLN' or balances['PLN'] < cost:
                        balances['PLN'] -= TEN
                    else:
                        balances[cur] = Decimal('0')
                        balances['PLN'] -= cost

        # Monthly fee check
        if day in (30, 60):
            val_before_fee = wallet_value()
            if val_before_fee < FIVE_THOUSAND:
                balances['PLN'] -= FIFTEEN

        # Recalculate premium status for next day
        premium = wallet_value() >= TWENTY_THOUSAND

    # Final value after day 60 (after fee already applied)
    final_val = round_half_up(wallet_value())
    return float(final_val)
```