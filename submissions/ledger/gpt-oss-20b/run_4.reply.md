<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:14:12+00:00 -->

```python
import decimal
from decimal import Decimal, ROUND_HALF_UP

def run() -> float:
    # Use Decimal for full precision
    decimal.getcontext().prec = 28

    # Opening balances
    accounts = {
        'X': {
            'balance': Decimal('4200.00'),
            'accrued_interest': Decimal('0.00'),
            'period_min': None
        },
        'Y': {
            'balance': Decimal('800.00'),
            'accrued_interest': Decimal('0.00'),
            'period_min': None
        },
        'Z': {
            'balance': Decimal('12000.00'),
            'accrued_interest': Decimal('0.00'),
            'period_min': None
        }
    }

    # List of events: (day, type, source, target, amount)
    events = [
        (1,  'DEPOSIT',  'Y', None, Decimal('300.00')),
        (3,  'WITHDRAW', 'Y', None, Decimal('1500.00')),
        (5,  'TRANSFER', 'Z', 'X', Decimal('2500.00')),
        (8,  'WITHDRAW', 'Y', None, Decimal('200.00')),
        (10, 'DEPOSIT',  'Y', None, Decimal('2000.00')),
        (12, 'TRANSFER', 'X', 'Y', Decimal('800.00')),
        (15, 'WITHDRAW', 'Z', None, Decimal('8000.00')),
        (20, 'WITHDRAW', 'Z', None, Decimal('700.00')),
        (25, 'TRANSFER', 'Y', 'Z', Decimal('1200.00')),
        (33, 'WITHDRAW', 'X', None, Decimal('6300.00')),
        (36, 'DEPOSIT',  'X', None, Decimal('1000.00')),
        (40, 'TRANSFER', 'Z', 'Y', Decimal('2100.00')),
        (45, 'WITHDRAW', 'Y', None, Decimal('5000.00')),
        (47, 'DEPOSIT',  'Z', None, Decimal('3000.00')),
        (50, 'TRANSFER', 'Y', 'X', Decimal('1000.00')),
        (55, 'WITHDRAW', 'X', None, Decimal('300.00')),
        (58, 'DEPOSIT',  'Y', None, Decimal('150.00')),
    ]

    # Group events by day for quick lookup
    day_events = {}
    for ev in events:
        day_events.setdefault(ev[0], []).append(ev)

    # Helper to apply a debit and return new balance and success flag
    def apply_debit(balance_before: Decimal, total: Decimal):
        if balance_before - total < Decimal('-500'):
            # Rejected debit: apply rejection fee
            return balance_before - Decimal('15.00'), False
        else:
            new_balance = balance_before - total
            if balance_before >= 0 and new_balance < 0:
                new_balance -= Decimal('25.00')
            return new_balance, True

    # Interest rates
    RATE_0_02 = Decimal('0.02')
    RATE_0_035 = Decimal('0.035')
    RATE_0_18 = Decimal('0.18')
    DAYS_IN_YEAR = Decimal('365')

    for day in range(1, 61):
        # Process all events for the day
        for ev in day_events.get(day, []):
            ev_day, ev_type, src, tgt, amount = ev
            if ev_type == 'DEPOSIT':
                accounts[src]['balance'] += amount
            elif ev_type == 'WITHDRAW':
                new_bal, _ = apply_debit(accounts[src]['balance'], amount)
                accounts[src]['balance'] = new_bal
            elif ev_type == 'TRANSFER':
                fee = Decimal('1.00') if amount > Decimal('1000') else Decimal('0.00')
                debit_total = amount + fee
                new_bal, success = apply_debit(accounts[src]['balance'], debit_total)
                accounts[src]['balance'] = new_bal
                if success:
                    accounts[tgt]['balance'] += amount
            else:
                raise ValueError(f"Unknown event type: {ev_type}")

        # End-of-day processing
        for acc in accounts.values():
            bal = acc['balance']

            # Minimum balance tracking
            if acc['period_min'] is None or bal < acc['period_min']:
                acc['period_min'] = bal

            # Interest accrual
            if bal > 0:
                part1 = min(bal, Decimal('5000')) * RATE_0_02 / DAYS_IN_YEAR
                part2 = max(bal - Decimal('5000'), Decimal('0')) * RATE_0_035 / DAYS_IN_YEAR
                interest = part1 + part2
            else:
                interest = bal * RATE_0_18 / DAYS_IN_YEAR
            acc['accrued_interest'] += interest

        # Period close on days 30 and 60
        if day in (30, 60):
            for acc in accounts.values():
                # Round accrued interest to 2 decimal places
                rounded_interest = acc['accrued_interest'].quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
                acc['balance'] += rounded_interest
                acc['accrued_interest'] = Decimal('0.00')

                # Maintenance fee if minimum balance < 1000
                if acc['period_min'] is not None and acc['period_min'] < Decimal('1000'):
                    acc['balance'] -= Decimal('5.00')

                # Reset period min for next period
                acc['period_min'] = None

    # Sum final balances
    total = sum(acc['balance'] for acc in accounts.values())
    final_sum = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(final_sum)
```