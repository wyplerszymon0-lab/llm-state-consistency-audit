<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T10:19:44+00:00 -->

```python
from decimal import Decimal, ROUND_HALF_DOWN

def run() -> float:
    X = Decimal('4200.00')
    Y = Decimal('800.00')
    Z = Decimal('12000.00')
    
    accounts = {'X': X, 'Y': Y, 'Z': Z}
    events = [
        (1, 'DEPOSIT', 'Y', '-', Decimal('300.00')),
        (3, 'WITHDRAW', 'Y', '-', Decimal('1500.00')),
        (5, 'TRANSFER', 'Z', 'X', Decimal('2500.00')),
        (8, 'WITHDRAW', 'Y', '-', Decimal('200.00')),
        (10, 'DEPOSIT', 'Y', '-', Decimal('2000.00')),
        (12, 'TRANSFER', 'X', 'Y', Decimal('800.00')),
        (15, 'WITHDRAW', 'Z', '-', Decimal('8000.00')),
        (20, 'WITHDRAW', 'Z', '-', Decimal('700.00')),
        (25, 'TRANSFER', 'Y', 'Z', Decimal('1200.00')),
        (33, 'WITHDRAW', 'X', '-', Decimal('6300.00')),
        (36, 'DEPOSIT', 'X', '-', Decimal('1000.00')),
        (40, 'TRANSFER', 'Z', 'Y', Decimal('2100.00')),
        (45, 'WITHDRAW', 'Y', '-', Decimal('5000.00')),
        (47, 'DEPOSIT', 'Z', '-', Decimal('3000.00')),
        (50, 'TRANSFER', 'Y', 'X', Decimal('1000.00')),
        (55, 'WITHDRAW', 'X', '-', Decimal('300.00')),
        (58, 'DEPOSIT', 'Y', '-', Decimal('150.00')),
    ]
    
    for day, event_type, account, target_account, amount in events:
        if event_type == 'DEPOSIT':
            accounts[account] += amount
        elif event_type == 'WITHDRAW':
            total = amount
            before = accounts[account]
            fee = Decimal('15.00') if total > Decimal('1000.00') else Decimal('0.00')
            if before - total - fee < Decimal('-500.00'):
                accounts[account] -= Decimal('15.00')
            else:
                accounts[account] -= total + fee
                if before >= Decimal('0.00') and accounts[account] < Decimal('0.00'):
                    accounts[account] -= Decimal('25.00')
        elif event_type == 'TRANSFER':
            fee = Decimal('15.00') if amount > Decimal('1000.00') else Decimal('0.00')
            total = amount + fee
            before = accounts[account]
            if before - total < Decimal('-500.00'):
                accounts[account] -= Decimal('15.00')
            else:
                accounts[account] -= total
                if before >= Decimal('0.00') and accounts[account] < Decimal('0.00'):
                    accounts[account] -= Decimal('25.00')
                if target_account != '-':
                    accounts[target_account] += amount
    
    for account in accounts:
        accounts[account] += accounts[account] * Decimal('0.002739726')  # 2% / 365
        if account == 'X' and accounts[account] < Decimal('1000.00'):
            accounts[account] -= Decimal('5.00')
        elif account == 'Y' and accounts[account] < Decimal('1000.00'):
            accounts[account] -= Decimal('5.00')
        elif account == 'Z' and accounts[account] < Decimal('1000.00'):
            accounts[account] -= Decimal('5.00')
    
    return round(sum(accounts.values()), 2)

print(run())
```