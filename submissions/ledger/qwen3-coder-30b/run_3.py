import math

def run() -> float:
    # Initialize accounts
    X = 4200.00
    Y = 800.00
    Z = 12000.00
    
    # Initialize tracking variables
    accrued_interest = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    min_balances = {'X': [], 'Y': [], 'Z': []}
    balance_history = {'X': [X], 'Y': [Y], 'Z': [Z]}
    
    # Events list
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
    
    # Sort events by day
    events.sort()
    
    # Process each day
    current_day = 1
    event_index = 0
    
    while current_day <= 60:
        # Process all events for this day
        while event_index < len(events) and events[event_index][0] == current_day:
            day, event_type, account, target_account, amount = events[event_index]
            
            if event_type == 'DEPOSIT':
                # Add amount to the account
                if account == 'X':
                    X += amount
                elif account == 'Y':
                    Y += amount
                elif account == 'Z':
                    Z += amount
                    
            elif event_type == 'WITHDRAW':
                # Apply debit rules
                before = 0
                if account == 'X':
                    before = X
                elif account == 'Y':
                    before = Y
                elif account == 'Z':
                    before = Z
                
                total = amount
                # Check for rejection
                if before - total < -500:
                    # Rejection fee of 15.00
                    if account == 'X':
                        X -= 15.00
                    elif account == 'Y':
                        Y -= 15.00
                    elif account == 'Z':
                        Z -= 15.00
                else:
                    # Deduct amount
                    if account == 'X':
                        X -= total
                        # Apply overdraft fee if needed
                        if before >= 0 and X < 0:
                            X -= 25.00
                    elif account == 'Y':
                        Y -= total
                        if before >= 0 and Y < 0:
                            Y -= 25.00
                    elif account == 'Z':
                        Z -= total
                        if before >= 0 and Z < 0:
                            Z -= 25.00
                        
            elif event_type == 'TRANSFER':
                # Apply debit rules for source account
                before = 0
                if account == 'X':
                    before = X
                elif account == 'Y':
                    before = Y
                elif account == 'Z':
                    before = Z
                
                # Calculate fee
                fee = 1.00 if amount > 1000 else 0.00
                total = amount + fee
                
                # Check for rejection
                if before - total < -500:
                    # Rejection fee of 15.00
                    if account == 'X':
                        X -= 15.00
                    elif account == 'Y':
                        Y -= 15.00
                    elif account == 'Z':
                        Z -= 15.00
                else:
                    # Deduct amount from source and add to target
                    if account == 'X':
                        X -= total
                        # Apply overdraft fee if needed
                        if before >= 0 and X < 0:
                            X -= 25.00
                        # Add amount to target
                        if target_account == 'Y':
                            Y += amount
                        elif target_account == 'Z':
                            Z += amount
                    elif account == 'Y':
                        Y -= total
                        if before >= 0 and Y < 0:
                            Y -= 25.00
                        # Add amount to target
                        if target_account == 'X':
                            X += amount
                        elif target_account == 'Z':
                            Z += amount
                    elif account == 'Z':
                        Z -= total
                        if before >= 0 and Z < 0:
                            Z -= 25.00
                        # Add amount to target
                        if target_account == 'X':
                            X += amount
                        elif target_account == 'Y':
                            Y += amount
            
            event_index += 1
        
        # End of day processing
        # Record balances for minimum tracking
        min_balances['X'].append(X)
        min_balances['Y'].append(Y)
        min_balances['Z'].append(Z)
        
        # Calculate interest
        def calculate_interest(balance):
            if balance > 0:
                return min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                return balance * 0.18 / 365
        
        accrued_interest['X'] += calculate_interest(X)
        accrued_interest['Y'] += calculate_interest(Y)
        accrued_interest['Z'] += calculate_interest(Z)
        
        # Period close (days 30 and 60)
        if current_day == 30 or current_day == 60:
            # Round interest to 2 decimal places, rounding halves away from zero
            for acc in ['X', 'Y', 'Z']:
                rounded_interest = round(accrued_interest[acc], 2)
                if (accrued_interest[acc] - math.floor(accrued_interest[acc])) == 0.5:
                    # Round away from zero
                    if accrued_interest[acc] > 0:
                        rounded_interest = math.ceil(accrued_interest[acc] * 100) / 100
                    else:
                        rounded_interest = math.floor(accrued_interest[acc] * 100) / 100
                
                # Add to balance
                if acc == 'X':
                    X += rounded_interest
                elif acc == 'Y':
                    Y += rounded_interest
                elif acc == 'Z':
                    Z += rounded_interest
                    
                # Reset accrued interest
                accrued_interest[acc] = 0.0
                
                # Check for maintenance fee
                period_min_balance = min(min_balances[acc])
                if period_min_balance < 1000:
                    if acc == 'X':
                        X -= 5.00
                    elif acc == 'Y':
                        Y -= 5.00
                    elif acc == 'Z':
                        Z -= 5.00
                
                # Reset min balances for next period
                min_balances[acc] = []
        
        current_day += 1
    
    # Return sum of final balances
    return round(X + Y + Z, 2)
