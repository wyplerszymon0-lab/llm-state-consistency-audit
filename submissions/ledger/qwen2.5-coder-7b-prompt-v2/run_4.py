def run() -> float:
    balances = {'X': 4200.00, 'Y': 800.00, 'Z': 12000.00}
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

    min_balances = {'X': [], 'Y': [], 'Z': []}
    accrued_interest = {'X': 0.00, 'Y': 0.00, 'Z': 0.00}

    def apply_event(day, event_type, account, target_account, amount):
        nonlocal balances, accrued_interest, min_balances

        if event_type == 'DEPOSIT':
            balances[account] += amount
        elif event_type == 'WITHDRAW':
            fee = 1.00 if amount > 1000 else 0.00
            total = amount + fee
            if balances[account] - total < -500:
                balances[account] -= 15.00
            else:
                balances[account] -= total
                if balances[account] < 0:
                    balances[account] -= 25.00
        elif event_type == 'TRANSFER':
            fee = 1.00 if amount > 1000 else 0.00
            total = amount + fee
            if balances[account] - total < -500:
                balances[account] -= 15.00
                balances[target_account] += amount
            else:
                balances[account] -= total
                balances[target_account] += amount

        if day % 30 == 0:
            for acc in balances:
                min_balances[acc].append(balances[acc])
                accrued_interest[acc] = round(accrued_interest[acc] + (balances[acc] * 0.18 / 365), 2)
                if balances[acc] < 1000:
                    balances[acc] -= 5.00
                    accrued_interest[acc] = 0.00

    for day, event_type, account, target_account, amount in events:
        apply_event(day, event_type, account, target_account, amount)

    for day in range(1, 61):
        for acc in balances:
            if day % 30 == 0:
                min_balances[acc].append(balances[acc])
                accrued_interest[acc] = round(accrued_interest[acc] + (balances[acc] * 0.18 / 365), 2)
                if balances[acc] < 1000:
                    balances[acc] -= 5.00
                    accrued_interest[acc] = 0.00

    return round(balances['X'] + balances['Y'] + balances['Z'], 2)

print(run())
