<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T10:17:18+00:00 -->

```python
def run() -> float:
    accounts = {'X': 4200.00, 'Y': 800.00, 'Z': 12000.00}
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
        (58, 'DEPOSIT', 'Y', '-', 150.00)
    ]
    interest_rates = (0.02, 0.035)
    overdraft_fee = 25.00
    rejection_fee = 15.00
    maintenance_fee = 5.00
    min_balance_periods = [[], [], []]

    def apply_event(event):
        day, event_type, account, target_account, amount = event
        fee = 1.00 if amount > 1000 else 0.00
        total = amount + fee
        before = accounts[account]
        if event_type == 'DEPOSIT':
            accounts[account] += total
        elif event_type == 'WITHDRAW':
            if before - total < -500:
                accounts[account] -= rejection_fee
            else:
                accounts[account] -= total
                if before >= 0 and accounts[account] < 0:
                    accounts[account] -= overdraft_fee
        elif event_type == 'TRANSFER':
            apply_event((day, 'WITHDRAW', account, target_account, amount))
            apply_event((day, 'DEPOSIT', target_account, '-', amount))

    for event in events:
        apply_event(event)

    def calculate_interest_and_fee(account, day):
        balance = accounts[account]
        if day == 30 or day == 60:
            accrued_interest = accounts[account].pop('accrued_interest', 0)
            accrued_interest = round(accrued_interest, 2)
            accounts[account] += accrued_interest
            if min_balance_periods[day // 30].min() < 1000:
                accounts[account] -= maintenance_fee

    for day in range(1, 61):
        if day % 30 == 0:
            min_balance_periods[day // 30].clear()
        for account, balance in accounts.items():
            min_balance_periods[day // 30].append(balance)
            accounts[account] += balance * (interest_rates[day % 30 > 15] if balance > 0 else 0.18) / 365
        for account in accounts:
            calculate_interest_and_fee(account, day)

    return round(sum(accounts.values()), 2)

print(run())
```