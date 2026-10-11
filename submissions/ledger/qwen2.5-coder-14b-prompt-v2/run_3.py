def run() -> float:
    # Initial balances
    X = 4200.00
    Y = 800.00
    Z = 12000.00
    
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
        (58, 'DEPOSIT', 'Y', '-', 150.00)
    ]
    
    # Accrued interest
    accrued_interest_X = 0.0
    accrued_interest_Y = 0.0
    accrued_interest_Z = 0.0
    
    # Minimum balances for the last 30 days
    min_balance_X = X
    min_balance_Y = Y
    min_balance_Z = Z
    
    # Process events
    for day, event_type, account, target_account, amount in events:
        if event_type == 'DEPOSIT':
            if account == 'X':
                X += amount
            elif account == 'Y':
                Y += amount
            elif account == 'Z':
                Z += amount
        elif event_type == 'WITHDRAW':
            if account == 'X':
                X = process_debit(X, amount)
            elif account == 'Y':
                Y = process_debit(Y, amount)
            elif account == 'Z':
                Z = process_debit(Z, amount)
        elif event_type == 'TRANSFER':
            if account == 'X':
                X, Y = process_transfer(X, Y, amount)
            elif account == 'X':
                X, Z = process_transfer(X, Z, amount)
            elif account == 'Y':
                Y, X = process_transfer(Y, X, amount)
            elif account == 'Y':
                Y, Z = process_transfer(Y, Z, amount)
            elif account == 'Z':
                Z, X = process_transfer(Z, X, amount)
            elif account == 'Z':
                Z, Y = process_transfer(Z, Y, amount)
        
        # Update minimum balances
        if account == 'X':
            min_balance_X = min(min_balance_X, X)
        elif account == 'Y':
            min_balance_Y = min(min_balance_Y, Y)
        elif account == 'Z':
            min_balance_Z = min(min_balance_Z, Z)
    
    # End of day 60 processing
    X = end_of_day(X, accrued_interest_X, min_balance_X)
    Y = end_of_day(Y, accrued_interest_Y, min_balance_Y)
    Z = end_of_day(Z, accrued_interest_Z, min_balance_Z)
    
    # Return the sum of the balances after day 60
    return round(X + Y + Z, 2)

def process_debit(balance, amount):
    fee = 0.0
    if balance - (amount + fee) < -500:
        balance -= 15.0
    else:
        balance -= (amount + fee)
        if balance >= 0 and balance < 0:
            balance -= 25.0
    return balance

def process_transfer(source, target, amount):
    fee = 0.0 if amount <= 1000 else 1.0
    if source - (amount + fee) < -500:
        source -= 15.0
    else:
        source -= (amount + fee)
        if source >= 0 and source < 0:
            source -= 25.0
        target += amount
    return source, target

def end_of_day(balance, accrued_interest, min_balance):
    # Interest accrual
    if balance > 0:
        accrued_interest += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
    else:
        accrued_interest += balance * 0.18 / 365
    
    # Period close
    balance += round(accrued_interest, 2)
    accrued_interest = 0.0
    
    # Maintenance fee
    if min_balance < 1000:
        balance -= 5.0
    
    return balance
