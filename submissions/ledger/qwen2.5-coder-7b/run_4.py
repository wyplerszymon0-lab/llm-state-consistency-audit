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
        (58, 'DEPOSIT', 'Y', '-', 150.00),
    ]

    for day, event_type, account, target_account, amount in events:
        if event_type == 'DEPOSIT':
            accounts[account] += amount
        elif event_type == 'WITHDRAW':
            accounts[account] -= amount
        elif event_type == 'TRANSFER':
            fee = 1.00 if amount > 1000 else 0.00
            total = amount + fee
            if accounts[account] - total < -500:
                accounts[account] -= 15.00
            else:
                accounts[account] -= total
                if accounts[account] < 0:
                    accounts[account] -= 25.00

    balances = {account: accounts[account] for account in accounts}
    for day in range(1, 61):
        for account in accounts:
            if day % 30 == 0:
                balances[account] += accounts[account] * 0.18 / 365
                if balances[account] < 1000:
                    balances[account] -= 5.00

    return round(sum(balances.values()), 2)
