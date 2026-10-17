#!/usr/bin/env python3
"""
Multi-currency wallet simulation – returns final PLN value after day 60.
"""

from decimal import Decimal, getcontext, ROUND_HALF_EVEN, ROUND_HALF_UP

# Set high precision for intermediate calculations
getcontext().prec = 50

# Helper rounding functions
def round_half_even(value: Decimal) -> Decimal:
    """Round to two decimals using round half to even."""
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_EVEN)

def round_half_away(value: Decimal) -> Decimal:
    """Round to two decimals using round half away from zero."""
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def run() -> float:
    # Initial balances
    balances = {
        'PLN': Decimal('3000.00'),
        'EUR': Decimal('1200.00'),
        'USD': Decimal('500.00')
    }

    # Initial exchange rates (PLN per unit)
    rates = {
        'EUR': Decimal('4.3150'),
        'USD': Decimal('3.9820'),
        'PLN': Decimal('1')
    }

    # Event list
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
        (58, 'PAY',     'USD', None,          Decimal('2000.00'))
    ]

    # Group events by day
    events_by_day = {}
    for day, typ, cur, tgt, amt in raw_events:
        events_by_day.setdefault(day, []).append((typ, cur, tgt, amt))

    # Helper to compute wallet value in PLN
    def wallet_value() -> Decimal:
        val = balances['PLN']
        for c in ('EUR', 'USD'):
            prod = balances[c] * rates[c]
            val += round_half_away(prod)
        return val

    # Determine initial premium status (before day 1)
    premium = wallet_value() >= Decimal('20000.00')

    # Process days 1 to 60
    for day in range(1, 61):
        # Apply all events for the day in order
        for typ, cur, tgt, amt in events_by_day.get(day, []):
            s = Decimal('0.002') if premium else Decimal('0.004')
            if typ == 'DEPOSIT':
                balances[cur] += amt
            elif typ == 'RATE':
                rates[cur] = amt
            elif typ == 'CONVERT':
                if balances[cur] < amt:
                    continue
                # Subtract source amount
                balances[cur] -= amt
                # Step 1: PLN amount
                p = round_half_even(amt * rates[cur])
                # Step 2: receive target currency
                factor = Decimal('1') - s
                received = round_half_even((p / rates[tgt]) * factor)
                balances[tgt] += received
            elif typ == 'PAY':
                if balances[cur] >= amt:
                    balances[cur] -= amt
                else:
                    shortfall = amt - balances[cur]
                    if cur == 'PLN':
                        # Decline
                        balances['PLN'] -= Decimal('10.00')
                    else:
                        cost = round_half_even(shortfall * rates[cur] * (Decimal('1') + s + Decimal('0.005')))
                        if balances['PLN'] >= cost:
                            balances[cur] = Decimal('0')
                            balances['PLN'] -= cost
                        else:
                            balances['PLN'] -= Decimal('10.00')
        # Monthly fee at days 30 and 60
        if day in (30, 60):
            val_before_fee = wallet_value()
            if val_before_fee < Decimal('5000.00'):
                balances['PLN'] -= Decimal('15.00')
        # Re-evaluate premium status for next day
        premium = wallet_value() >= Decimal('20000.00')

    # Final value after day 60
    final_value = round_half_away(wallet_value())
    return float(final_value)

if __name__ == "__main__":
    print(run())
