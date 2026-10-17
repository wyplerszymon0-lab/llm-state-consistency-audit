import math

def run() -> float:
    # Initialize accounts
    X = 4200.00
    Y = 800.00
    Z = 12000.00
    
    # Track balances and interest
    balance_X = X
    balance_Y = Y
    balance_Z = Z
    
    accrued_interest_X = 0.0
    accrued_interest_Y = 0.0
    accrued_interest_Z = 0.0
    
    # Track minimum balances for each period
    min_balance_X_period1 = X  # Days 1-30
    min_balance_Y_period1 = Y
    min_balance_Z_period1 = Z
    
    min_balance_X_period2 = X  # Days 31-60
    min_balance_Y_period2 = Y
    min_balance_Z_period2 = Z
    
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
    
    # Group events by day
    events_by_day = {}
    for event in events:
        day, event_type, account, target_account, amount = event
        if day not in events_by_day:
            events_by_day[day] = []
        events_by_day[day].append(event)
    
    # Process each day
    for day in range(1, 61):
        # Process events on this day
        if day in events_by_day:
            for event in events_by_day[day]:
                _, event_type, account, target_account, amount = event
                
                if event_type == 'DEPOSIT':
                    if account == 'X':
                        balance_X += amount
                    elif account == 'Y':
                        balance_Y += amount
                    elif account == 'Z':
                        balance_Z += amount
                        
                elif event_type == 'WITHDRAW':
                    total_debit = amount
                    
                    # Apply debit rules
                    if account == 'X':
                        before = balance_X
                        if before - total_debit < -500:
                            # Rejection
                            balance_X -= 15.00  # rejection fee
                        else:
                            balance_X -= total_debit
                            if before >= 0 and balance_X < 0:
                                balance_X -= 25.00  # overdraft fee
                    elif account == 'Y':
                        before = balance_Y
                        if before - total_debit < -500:
                            # Rejection
                            balance_Y -= 15.00  # rejection fee
                        else:
                            balance_Y -= total_debit
                            if before >= 0 and balance_Y < 0:
                                balance_Y -= 25.00  # overdraft fee
                    elif account == 'Z':
                        before = balance_Z
                        if before - total_debit < -500:
                            # Rejection
                            balance_Z -= 15.00  # rejection fee
                        else:
                            balance_Z -= total_debit
                            if before >= 0 and balance_Z < 0:
                                balance_Z -= 25.00  # overdraft fee
                                
                elif event_type == 'TRANSFER':
                    source = account
                    target = target_account
                    
                    # Calculate fee
                    fee = 1.00 if amount > 1000 else 0.00
                    total_debit = amount + fee
                    
                    # Apply debit rules to source account
                    success = True
                    if source == 'X':
                        before = balance_X
                        if before - total_debit < -500:
                            # Rejection
                            balance_X -= 15.00  # rejection fee
                            success = False
                        else:
                            balance_X -= total_debit
                            if before >= 0 and balance_X < 0:
                                balance_X -= 25.00  # overdraft fee
                    elif source == 'Y':
                        before = balance_Y
                        if before - total_debit < -500:
                            # Rejection
                            balance_Y -= 15.00  # rejection fee
                            success = False
                        else:
                            balance_Y -= total_debit
                            if before >= 0 and balance_Y < 0:
                                balance_Y -= 25.00  # overdraft fee
                    elif source == 'Z':
                        before = balance_Z
                        if before - total_debit < -500:
                            # Rejection
                            balance_Z -= 15.00  # rejection fee
                            success = False
                        else:
                            balance_Z -= total_debit
                            if before >= 0 and balance_Z < 0:
                                balance_Z -= 25.00  # overdraft fee
                    
                    # If debit was successful, credit target account
                    if success:
                        if target == 'X':
                            balance_X += amount
                        elif target == 'Y':
                            balance_Y += amount
                        elif target == 'Z':
                            balance_Z += amount
        
        # End of day processing
        # Update minimum balances for current period
        if day <= 30:
            min_balance_X_period1 = min(min_balance_X_period1, balance_X)
            min_balance_Y_period1 = min(min_balance_Y_period1, balance_Y)
            min_balance_Z_period1 = min(min_balance_Z_period1, balance_Z)
        else:
            min_balance_X_period2 = min(min_balance_X_period2, balance_X)
            min_balance_Y_period2 = min(min_balance_Y_period2, balance_Y)
            min_balance_Z_period2 = min(min_balance_Z_period2, balance_Z)
        
        # Accrue interest for each account
        def accrue_interest(balance):
            if balance > 0:
                return min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                return balance * 0.18 / 365
        
        accrued_interest_X += accrue_interest(balance_X)
        accrued_interest_Y += accrue_interest(balance_Y)
        accrued_interest_Z += accrue_interest(balance_Z)
        
        # Period close at day 30 and 60
        if day == 30 or day == 60:
            # Round interest to 2 decimal places, rounding halves away from zero
            rounded_X = round(accrued_interest_X, 2)
            rounded_Y = round(accrued_interest_Y, 2)
            rounded_Z = round(accrued_interest_Z, 2)
            
            balance_X += rounded_X
            balance_Y += rounded_Y
            balance_Z += rounded_Z
            
            # Reset interest
            accrued_interest_X = 0.0
            accrued_interest_Y = 0.0
            accrued_interest_Z = 0.0
            
            # Check for maintenance fees
            if day == 30:
                min_balance_period1 = min(min_balance_X_period1, min_balance_Y_period1, min_balance_Z_period1)
                if min_balance_period1 < 1000:
                    balance_X -= 5.00
                    balance_Y -= 5.00
                    balance_Z -= 5.00
            elif day == 60:
                min_balance_period2 = min(min_balance_X_period2, min_balance_Y_period2, min_balance_Z_period2)
                if min_balance_period2 < 1000:
                    balance_X -= 5.00
                    balance_Y -= 5.00
                    balance_Z -= 5.00
    
    # Return sum of balances rounded to 2 decimal places
    return round(balance_X + balance_Y + balance_Z, 2)
