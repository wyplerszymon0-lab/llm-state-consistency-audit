<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:29:16+00:00 -->

```python
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
    min_balance_X = float('inf')
    min_balance_Y = float('inf')
    min_balance_Z = float('inf')
    
    # Store end-of-day balances for period tracking
    period1_balances_X = []
    period1_balances_Y = []
    period1_balances_Z = []
    period2_balances_X = []
    period2_balances_Y = []
    period2_balances_Z = []
    
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
        # Process events for the current day
        while event_index < len(events) and events[event_index][0] == current_day:
            day, event_type, account, target_account, amount = events[event_index]
            
            if event_type == 'DEPOSIT':
                if account == 'X':
                    balance_X += amount
                elif account == 'Y':
                    balance_Y += amount
                elif account == 'Z':
                    balance_Z += amount
                    
            elif event_type == 'WITHDRAW':
                # Calculate total to debit (amount + potential fee)
                total = amount
                
                # Check if debit is rejected
                if account == 'X':
                    before = balance_X
                    if before - total < -500:
                        balance_X -= 15.00  # Rejection fee
                    else:
                        balance_X -= total
                        if before >= 0 and balance_X < 0:
                            balance_X -= 25.00  # Overdraft fee
                elif account == 'Y':
                    before = balance_Y
                    if before - total < -500:
                        balance_Y -= 15.00  # Rejection fee
                    else:
                        balance_Y -= total
                        if before >= 0 and balance_Y < 0:
                            balance_Y -= 25.00  # Overdraft fee
                elif account == 'Z':
                    before = balance_Z
                    if before - total < -500:
                        balance_Z -= 15.00  # Rejection fee
                    else:
                        balance_Z -= total
                        if before >= 0 and balance_Z < 0:
                            balance_Z -= 25.00  # Overdraft fee
                        
            elif event_type == 'TRANSFER':
                source_account = account
                target_account = target_account
                
                # Calculate fee
                fee = 1.00 if amount > 1000 else 0.00
                total_debit = amount + fee
                
                # Check if transfer is possible (source account)
                source_balance = balance_X if source_account == 'X' else balance_Y if source_account == 'Y' else balance_Z
                before = source_balance
                
                debit_successful = True
                if before - total_debit < -500:
                    debit_successful = False
                    # Apply rejection fee
                    if source_account == 'X':
                        balance_X -= 15.00
                    elif source_account == 'Y':
                        balance_Y -= 15.00
                    elif source_account == 'Z':
                        balance_Z -= 15.00
                else:
                    # Apply debit
                    if source_account == 'X':
                        balance_X -= total_debit
                        if before >= 0 and balance_X < 0:
                            balance_X -= 25.00
                    elif source_account == 'Y':
                        balance_Y -= total_debit
                        if before >= 0 and balance_Y < 0:
                            balance_Y -= 25.00
                    elif source_account == 'Z':
                        balance_Z -= total_debit
                        if before >= 0 and balance_Z < 0:
                            balance_Z -= 25.00
                
                # If debit was successful, credit target account
                if debit_successful:
                    if target_account == 'X':
                        balance_X += amount
                    elif target_account == 'Y':
                        balance_Y += amount
                    elif target_account == 'Z':
                        balance_Z += amount
            
            event_index += 1
        
        # End of day processing
        # Record end-of-day balance for the period tracking
        if current_day <= 30:
            period1_balances_X.append(balance_X)
            period1_balances_Y.append(balance_Y)
            period1_balances_Z.append(balance_Z)
        else:
            period2_balances_X.append(balance_X)
            period2_balances_Y.append(balance_Y)
            period2_balances_Z.append(balance_Z)
        
        # Compute interest for this day
        # For account X
        b = balance_X
        if b > 0:
            interest = min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365
        else:
            interest = b * 0.18 / 365
        accrued_interest_X += interest
        
        # For account Y
        b = balance_Y
        if b > 0:
            interest = min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365
        else:
            interest = b * 0.18 / 365
        accrued_interest_Y += interest
        
        # For account Z
        b = balance_Z
        if b > 0:
            interest = min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365
        else:
            interest = b * 0.18 / 365
        accrued_interest_Z += interest
        
        # Period close at day 30 and 60
        if current_day == 30:
            # Apply interest to balances and reset
            balance_X += round(accrued_interest_X, 2)
            balance_Y += round(accrued_interest_Y, 2)
            balance_Z += round(accrued_interest_Z, 2)
            
            accrued_interest_X = 0.0
            accrued_interest_Y = 0.0
            accrued_interest_Z = 0.0
            
            # Check maintenance fee for period 1
            min_bal_X = min(period1_balances_X) if period1_balances_X else float('inf')
            min_bal_Y = min(period1_balances_Y) if period1_balances_Y else float('inf')
            min_bal_Z = min(period1_balances_Z) if period1_balances_Z else float('inf')
            
            if min_bal_X < 1000:
                balance_X -= 5.00
            if min_bal_Y < 1000:
                balance_Y -= 5.00
            if min_bal_Z < 1000:
                balance_Z -= 5.00
                
        elif current_day == 60:
            # Apply interest to balances and reset
            balance_X += round(accrued_interest_X, 2)
            balance_Y += round(accrued_interest_Y, 2)
            balance_Z += round(accrued_interest_Z, 2)
            
            accrued_interest_X = 0.0
            accrued_interest_Y = 0.0
            accrued_interest_Z = 0.0
            
            # Check maintenance fee for period 2
            min_bal_X = min(period2_balances_X) if period2_balances_X else float('inf')
            min_bal_Y = min(period2_balances_Y) if period2_balances_Y else float('inf')
            min_bal_Z = min(period2_balances_Z) if period2_balances_Z else float('inf')
            
            if min_bal_X < 1000:
                balance_X -= 5.00
            if min_bal_Y < 1000:
                balance_Y -= 5.00
            if min_bal_Z < 1000:
                balance_Z -= 5.00
        
        current_day += 1
    
    # Return sum of balances rounded to 2 decimal places
    return round(balance_X + balance_Y + balance_Z, 2)
```