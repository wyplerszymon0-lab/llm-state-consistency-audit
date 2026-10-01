def run() -> float:
    # Initial balances
    X, Y, Z = 4200.00, 800.00, 12000.00
    balances = {'X': X, 'Y': Y, 'Z': Z}
    accrued_interest = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    min_balances = {'X': [float('inf')] * 30, 'Y': [float('inf')] * 30, 'Z': [float('inf')] * 30}
    day = 0

    # Events
    events = [
        (1, 'DEPOSIT', 'Y', '-', 300.00),
        (3, 'WITHDRAW', 'Y', '-', 1500.00),
        (5, 'TRANSFER', 'Z', 'X', 2500.00),
        (8, 'WITHDRAW', 'Y', '-', 200.00),
        (10, 'DEPOSIT', 'Y', '-', 2000.00),
        (12, 'TRANSFER', 'X', 'Y', 800.00),
        (15, 'WITHDRAW', 'Z', '-', 8000.00),
        (20, 'WITHDRAW', 'Z', '-', 7000.00),
        (25, 'TRANSFER', 'Y', 'Z', 12000.00),
        (33, 'WITHDRAW', 'X', '-', 6300.00),
        (36, 'DEPOSIT', 'X', '-', 1000.00),
        (40, 'TRANSFER', 'Z', 'Y', 2100.00),
        (45, 'WITHDRAW', 'Y', '-', 5000.00),
        (47, 'DEPOSIT', 'Z', '-', 3000.00),
        (50, 'TRANSFER', 'Y', 'X', 1000.00),
        (55, 'WITHDRAW', 'X', '-', 300.00),
        (58, 'DEPOSIT', 'Y', '-', 150.00),
    ]

    # Process events
    for event_day, event_type, account, target_account, amount in events:
        while day < event_day:
            day += 1
            for acc in balances:
                accrued_interest[acc] += (min(balances[acc], 5000) * 0.02 / 365 +
                                         max(balances[acc] - 5000, 0) * 0.035 / 365)
                min_balances[acc][day % 30] = min(min_balances[acc][day % 30], balances[acc])
                if day % 30 == 29:
                    accrued_interest[acc] = round(accrued_interest[acc], 2)
                    balances[acc] += accrued_interest[acc]
                    accrued_interest[acc] = 0
                    if min(min_balances[acc]) < 1000:
                        balances[acc] -= 5.00

        if event_type == 'DEPOSIT':
            balances[account] += amount
        elif event_type == 'WITHDRAW':
            if balances[account] - amount < -500:
                balances[account] -= 15.00
            else:
                balances[account] -= amount
                if balances[account] >= 0 and balances[account] - amount < 0:
                    balances[account] -= 25.00
        elif event_type == 'TRANSFER':
            fee = 1.00 if amount > 1000 else 0.00
            if balances[account] - amount - fee < -500:
                balances[account] -= 15.00
            else:
                balances[account] -= amount + fee
                if balances[account] >= 0 and balances[account] - amount - fee < 0:
                    balances[account] -= 25.00
                else:
                    balances[target_account] += amount

    # Final day processing
    while day < 60:
        day += 1
        for acc in balances:
            accrued_interest[acc] += (min(balances[acc], 5000) * 0.02 / 365 +
                                     max(balances[acc] - 5000, 0) * 0.035 / 365)
            min_balances[acc][day % 30] = min(min_balances[acc][day % 30], balances[acc])
            if day % 30 == 29:
                accrued_interest[acc] = round(accrued_interest[acc], 2)
                balances[acc] += accrued_interest[acc]
                accrued_interest[acc] = 0
                if min(min_balances[acc]) < 1000:
                    balances[acc] -= 5.00

    # Close period 60
    for acc in balances:
        accrued_interest[acc] = round(accrued_interest[acc], 2)
        balances[acc] += accrued_interest[acc]
        if min(min_balances[acc]) < 1000:
            balances[acc] -= 5.00

    # Return the sum of the balances after day 60
    return round(sum(balances.values()), 2)

# Example usage
if __name__ == "__main__":
    print(run())
