<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:39:00+00:00 -->

```python
import decimal
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP, getcontext

# set precision high enough for intermediate calculations
getcontext().prec = 28

def round_bankers(x: Decimal) -> Decimal:
    """Round to two decimals using banker's rounding."""
    return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

def round_half_away(x: Decimal) -> Decimal:
    """Round to two decimals with half away from zero (ROUND_HALF_UP)."""
    return x.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def run() -> float:
    # initial balances
    balances = {
        'PLN': Decimal('3000.00'),
        'EUR': Decimal('1200.00'),
        'USD': Decimal('500.00')
    }

    # initial rates
    rates = {
        'PLN': Decimal('1.0000'),
        'EUR': Decimal('4.3150'),
        'USD': Decimal('3.9820')
    }

    # Event data
    events_raw = """
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
    """

    # Parse events into dict of day -> list of events
    day_events = {}
    for line in events_raw.strip().splitlines():
        parts = [p.strip() for p in line.split(',')]
        day = int(parts[0])
        typ = parts[1]
        currency = parts[2]
        target = parts[3]
        amount = Decimal(parts[4])
        day_events.setdefault(day, []).append((typ, currency, target, amount))

    def compute_value() -> Decimal:
        """Compute wallet value in PLN with half away from zero rounding for conversions."""
        val_pln = balances['PLN']
        val_eur = round_half_away(balances['EUR'] * rates['EUR'])
        val_usd = round_half_away(balances['USD'] * rates['USD'])
        return val_pln + val_eur + val_usd

    # initial premium status before day 1
    premium = compute_value() >= Decimal('20000.00')

    # constants
    PLN = 'PLN'
    EUR = 'EUR'
    USD = 'USD'
    DEC_10 = Decimal('10.00')
    DEC_15 = Decimal('15.00')
    DEC_005 = Decimal('0.005')
    DEC_002 = Decimal('0.002')
    DEC_004 = Decimal('0.004')
    DEC_1 = Decimal('1')

    # simulate days
    for day in range(1, 61):
        # process events of the day
        for typ, cur, tgt, amt in day_events.get(day, []):
            if typ == 'DEPOSIT':
                balances[cur] += amt
            elif typ == 'RATE':
                rates[cur] = amt
            elif typ == 'CONVERT':
                # check balance
                if balances[cur] >= amt:
                    # step 1
                    p = round_bankers(amt * rates[cur])
                    # step 2
                    s = DEC_002 if premium else DEC_004
                    received = round_bankers(p / rates[tgt] * (DEC_1 - s))
                    balances[cur] -= amt
                    balances[tgt] += received
            elif typ == 'PAY':
                if balances[cur] >= amt:
                    balances[cur] -= amt
                else:
                    # shortfall
                    shortfall = amt - balances[cur]
                    if cur == PLN:
                        # decline
                        balances[PLN] -= DEC_10
                    else:
                        s = DEC_002 if premium else DEC_004
                        cost = shortfall * rates[cur] * (DEC_1 + s + DEC_005)
                        cost = round_bankers(cost)
                        if balances[PLN] < cost:
                            # decline
                            balances[PLN] -= DEC_10
                        else:
                            # accept payment
                            balances[cur] = Decimal('0')
                            balances[PLN] -= cost
            else:
                # unknown event type
                pass

        # after events, compute value before possible monthly fee
        value_before_fee = compute_value()

        # monthly fee check
        if day in (30, 60):
            if value_before_fee < Decimal('5000.00'):
                balances[PLN] -= DEC_15

        # recompute value after fee for premium status
        value_after_fee = compute_value()
        premium = value_after_fee >= Decimal('20000.00')

    # final value after day 60, after fee
    final_value = compute_value()
    final_value = round_half_away(final_value)
    return float(final_value)

```