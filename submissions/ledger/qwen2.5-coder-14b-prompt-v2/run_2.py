def run() -> float:
    # Initial balances
    X, Y, Z = 4200.00, 800.00, 12000.00
    
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
    
    # Initialize variables
    balances = {'X': X, 'Y': Y, 'Z': Z}
    accrued_interest = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    min_balances = {'X': [float('inf')] * 60, 'Y': [float('inf')] * 60, 'Z': [float('inf')] * 60}
    
    # Process events
    for day, event_type, account, target_account, amount in events:
        if event_type == 'DEPOSIT':
            balances[account] += amount
        elif event_type == 'WITHDRAW':
            total = amount
            if balances[account] - total < -500:
                balances[account] -= 15.00
            else:
                balances[account] -= total
                if balances[account] >= 0 and balances[account] < 0:
                    balances[account] -= 25.00
        elif event_type == 'TRANSFER':
            fee = 1.00 if amount > 1000 else 0.00
            total = amount + fee
            if balances[account] - total < -500:
                balances[account] -= 15.00
            else:
                balances[account] -= total
                if balances[account] >= 0 and balances[account] < 0:
                    balances[account] -= 25.00
                balances[target_account] += amount
    
    # End of each day processing
    for day in range(1, 61):
        for account in ['X', 'Y', 'Z']:
            balance = balances[account]
            min_balances[account][day - 1] = min(min_balances[account][day - 1], balance)
            if balance > 0:
                accrued_interest[account] += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                accrued_interest[account] += balance * 0.18 / 365
        
        if day == 30 or day == 60:
            for account in ['X', 'Y', 'Z']:
                accrued_interest[account] = round(accrued_interest[account], 2)
                balances[account] += accrued_interest[account]
                accrued_interest[account] = 0.0
                if min(min_balances[account][:day]) < 1000:
                    balances[account] -= 5.00
    
    # Sum of balances after day 60
    return round(balances['X'] + balances['Y'] + balances['Z'], 2)

# Run the simulation and print the result
print(run())
