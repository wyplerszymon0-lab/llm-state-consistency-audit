def run() -> float:
    X, Y, Z = 4200.00, 800.00, 12000.00
    balances = [X, Y, Z]
    end_of_day_balances = [balances.copy() for _ in range(61)]
    accrued_interest = [0.0] * 3

    def apply_transaction(day, account, target_account, amount):
        fee = 1.0 if amount > 1000 else 0
        total = amount + fee
        before = balances[account]
        if before - total < -500:
            balances[account] -= 15.00
        else:
            balances[account] -= total
            if before >= 0 and balances[account] < 0:
                balances[account] -= 25.00
            if target_account is not None:
                balances[target_account] += amount

    def apply_interest_and_fee(day):
        for i, b in enumerate(balances):
            if day == 30 or day == 60:
                accrued_interest[i] = round(accrued_interest[i], 2)
                balances[i] += accrued_interest[i]
                accrued_interest[i] = 0
                if min(end_of_day_balances[d][i] for d in range(day - 29, day + 1)) < 1000:
                    balances[i] -= 5.00

    events = [
        (1, 'DEPOSIT', 1, None, 300.00),
        (3, 'WITHDRAW', 1, None, 1500.00),
        (5, 'TRANSFER', 2, 0, 2500.00),
        (8, 'WITHDRAW', 1, None, 200.00),
        (10, 'DEPOSIT', 1, None, 2000.00),
        (12, 'TRANSFER', 0, 1, 800.00),
        (15, 'WITHDRAW', 2, None, 8000.00),
        (20, 'WITHDRAW', 2, None, 700.00),
        (25, 'TRANSFER', 1, 2, 1200.00),
        (33, 'WITHDRAW', 0, None, 6300.00),
        (36, 'DEPOSIT', 0, None, 1000.00),
        (40, 'TRANSFER', 2, 1, 2100.00),
        (45, 'WITHDRAW', 1, None, 5000.00),
        (47, 'DEPOSIT', 2, None, 3000.00),
        (50, 'TRANSFER', 1, 0, 1000.00),
        (55, 'WITHDRAW', 0, None, 300.00),
        (58, 'DEPOSIT', 1, None, 150.00),
    ]

    for day, event_type, account, target_account, amount in events:
        apply_transaction(day, account, target_account, amount)

    for day in range(1, 61):
        for i in range(3):
            end_of_day_balances[day][i] = balances[i]

    for day in range(1, 61):
        apply_interest_and_fee(day)

    return round(sum(balances), 2)

print(run())
