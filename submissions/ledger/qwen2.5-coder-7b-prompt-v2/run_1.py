def run() -> float:
    accounts = {
        'X': 4200.00,
        'Y': 800.00,
        'Z': 12000.00
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
        (58, 'DEPOSIT', 'Y', '-', 150.00)
    ]

    for day, eventType, account, targetAccount, amount in events:
        if eventType == 'DEPOSIT':
            accounts[account] += amount
        elif eventType == 'WITHDRAW':
            if accounts[account] >= amount:
                accounts[account] -= amount
            else:
                if accounts[account] - amount < -500:
                    accounts[account] -= 15.00
                else:
                    accounts[account] -= amount
                    accounts[account] -= 25.00
        elif eventType == 'TRANSFER':
            fee = 1.00 if amount > 1000 else 0
            if accounts[account] >= amount + fee:
                accounts[account] -= amount + fee
                accounts[targetAccount] += amount
            else:
                if accounts[account] - amount - fee < -500:
                    accounts[account] -= 15.00
                else:
                    accounts[account] -= amount + fee
                    accounts[account] -= 25.00

    for d in range(1, 61):
        minBalances = [accounts['X'], accounts['Y'], accounts['Z']]
        accruedInterest = [0.0, 0.0, 0.0]
        for account in accounts:
            balance = accounts[account]
            if d <= 30:
                if balance < minBalances[0]:
                    minBalances[0] = balance
                accruedInterest[0] += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                if balance < minBalances[1]:
                    minBalances[1] = balance
                accruedInterest[1] += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            if d == 30 or d == 60:
                accruedInterest[1] = round(accruedInterest[1], 2)
                accounts[account] += accruedInterest[1]
                accruedInterest[1] = 0
                if minBalances[1] < 1000:
                    accounts[account] -= 5.00

    return round(accounts['X'] + accounts['Y'] + accounts['Z'], 2)
