<!-- model: ollama:qwen3:8b | prompt v1 | 2026-09-30T20:34:03+00:00 -->

```python
import decimal
from collections import defaultdict

def run():
    # Initialize accounts
    accounts = {
        'X': {'balance': 4200.00, 'accrued_interest': 0.0, 'min_balance_period1': 4200.00, 'min_balance_period2': float('inf')},
        'Y': {'balance': 800.00, 'accrued_interest': 0.0, 'min_balance_period1': 800.00, 'min_balance_period2': float('inf')},
        'Z': {'balance': 12000.00, 'accrued_interest': 0.0, 'min_balance_period1': 12000.00, 'min_balance_period2': float('inf')}
    }

    events = [
        (1, 'DEPOSIT', 'Y', '-', 300.00),
        (3, 'WITHDRAW', 'Y', '-', 1500.00),
        (5, 'TRANSFER', 'Z', 'X', 2500.00),
        (8, 'WITHDRAW', 'Y', '-', 200.00),
        (10, 'DEPOSIT', 'Y', '-', 2000.00),
        (12, 'TRANSFER', 'X', 'Y', 800.00),
        (15, 'WITHDRAW', 'Z', '-', 8000.00),
        (20, 'WITHDRAW', 'Z', '-', 700.00),
        (25, 'TRANSFER', 'Y', 'Z', 1200.00),
        (33, 'WITHDRAW', 'X', '-', 6300.00),
        (36, 'DEPOSIT', 'X', '-', 1000.00),
        (40, 'TRANSFER', 'Z', 'Y', 2100.00),
        (45, 'WITHDRAW', 'Y', '-', 5000.00),
        (47, 'DEPOSIT', 'Z', '-', 3000.00),
        (50, 'TRANSFER', 'Y', 'X', 1000.00),
        (55, 'WITHDRAW', 'X', '-', 300.00),
        (58, 'DEPOSIT', 'Y', '-', 150.00),
    ]

    events_by_day = defaultdict(list)
    for event in events:
        day = event[0]
        events_by_day[day].append(event)

    for day in range(1, 61):
        # Process events for this day
        for event in events_by_day.get(day, []):
            _, event_type, account, target_account, amount = event
            if event_type == 'DEPOSIT':
                accounts[account]['balance'] += amount
            elif event_type == 'WITHDRAW':
                account_data = accounts[account]
                before = account_data['balance']
                total = amount
                if before - total < -500:
                    account_data['balance'] -= 15.00
                else:
                    account_data['balance'] -= total
                    if before >= 0 and account_data['balance'] < 0:
                        account_data['balance'] -= 25.00
            elif event_type == 'TRANSFER':
                source_account = accounts[account]
                target_account_data = accounts[target_account]
                amount_val = amount
                if amount_val > 1000:
                    fee = 1.00
                else:
                    fee = 0.0
                total_debit = amount_val + fee
                before = source_account['balance']
                if before - total_debit < -500:
                    source_account['balance'] -= 15.00
                else:
                    source_account['balance'] -= total_debit
                    if before >= 0 and source_account['balance'] < 0:
                        source_account['balance'] -= 25.00
                    target_account_data['balance'] += amount_val

        # End-of-day processing for all accounts
        for account in ['X', 'Y', 'Z']:
            account_data = accounts[account]
            current_day = day
            if current_day <= 30:
                period = 1
            else:
                period = 2
            if period == 1:
                current_min = account_data['min_balance_period1']
                new_balance = account_data['balance']
                if new_balance < current_min:
                    account_data['min_balance_period1'] = new_balance
            else:
                current_min = account_data['min_balance_period2']
                new_balance = account_data['balance']
                if new_balance < current_min:
                    account_data['min_balance_period2'] = new_balance

            balance = account_data['balance']
            if balance > 0:
                part1 = min(balance, 5000) * 0.02 / 365
                part2 = max(balance - 5000, 0) * 0.035 / 365
                interest = part1 + part2
            else:
                interest = balance * 0.18 / 365
            account_data['accrued_interest'] += interest

        # Check if day is 30 or 60 for period close
        if day in (30, 60):
            for account in ['X', 'Y', 'Z']:
                account_data = accounts[account]
                d = decimal.Decimal(str(account_data['accrued_interest']))
                rounded_interest = d.quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
                rounded_interest_float = float(rounded_interest)
                account_data['balance'] += rounded_interest_float
                account_data['accrued_interest'] = 0.0

                if day == 30:
                    min_balance = account_data['min_balance_period1']
                else:
                    min_balance = account_data['min_balance_period2']
                if min_balance < 1000:
                    account_data['balance'] -= 5.00

    total = accounts['X']['balance'] + accounts['Y']['balance'] + accounts['Z']['balance']
    d = decimal.Decimal(str(total))
    rounded_total = d.quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)
    return float(rounded_total)
```