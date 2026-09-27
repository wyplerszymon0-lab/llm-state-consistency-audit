<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:22:30+00:00 -->

```python
def run() -> float:
    accounts = {'X': 4200.00, 'Y': 800.00, 'Z': 12000.00}
    end_of_day_balances = {'X': [], 'Y': [], 'Z': []}
    accrued_interest = {'X': 0, 'Y': 0, 'Z': 0}
    
    events = [
        (1, 'DEPOSIT', 'Y', None, 300.00),
        (3, 'WITHDRAW', 'Y', None, 1500.00),
        (5, 'TRANSFER', 'Z', 'X', 2500.00),
        (8, 'WITHDRAW', 'Y', None, 200.00),
        (10, 'DEPOSIT', 'Y', None, 2000.00),
        (12, 'TRANSFER', 'X', 'Y', 800.00),
        (15, 'WITHDRAW', 'Z', None, 8000.00),
        (20, 'WITHDRAW', 'Z', None, 700.00),
        (25, 'TRANSFER', 'Y', 'Z', 1200.00),
        (33, 'WITHDRAW', 'X', None, 6300.00),
        (36, 'DEPOSIT', 'X', None, 1000.00),
        (40, 'TRANSFER', 'Z', 'Y', 2100.00),
        (45, 'WITHDRAW', 'Y', None, 5000.00),
        (47, 'DEPOSIT', 'Z', None, 3000.00),
        (50, 'TRANSFER', 'Y', 'X', 1000.00),
        (55, 'WITHDRAW', 'X', None, 300.00),
        (58, 'DEPOSIT', 'Y', None, 150.00)
    ]
    
    def process_event(day, event_type, account, target_account, amount):
        nonlocal accrued_interest, end_of_day_balances
        if event_type == 'DEPOSIT':
            accounts[account] += amount
        elif event_type == 'WITHDRAW':
            fee = 0 if amount <= 1000 else 1.00
            if accounts[account] - (amount + fee) >= -500:
                accounts[account] -= (amount + fee)
                if accounts[account] < 0:
                    accounts[account] -= 25.00
            else:
                accounts[account] -= 15.00
        elif event_type == 'TRANSFER':
            fee = 0 if amount <= 1000 else 1.00
            if accounts[account] - (amount + fee) >= -500:
                accounts[account] -= (amount + fee)
                accounts[target_account] += amount
                if accounts[account] < 0:
                    accounts[account] -= 25.00
            else:
                accounts[account] -= 15.00
    
    for day, event_type, account, target_account, amount in events:
        process_event(day, event_type, account, target_account, amount)
        end_of_day_balances[account].append(accounts[account])
    
    for account in 'XYZ':
        if day % 30 == 0:
            accrued_interest[account] = round(accrued_interest[account], 2)
            accounts[account] += accrued_interest[account]
            accrued_interest[account] = 0
            min_balance = min(end_of_day_balances[account])
            if min_balance < 1000:
                accounts[account] -= 5.00
    
    return round(sum(accounts.values()), 2)
```