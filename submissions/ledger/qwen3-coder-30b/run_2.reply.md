<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:44:27+00:00 -->

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
    
    # Initialize events list
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
    event_index = 0
    
    for day in range(1, 61):
        # Process all events for this day
        while event_index < len(events) and events[event_index][0] == day:
            _, event_type, account, target_account, amount = events[event_index]
            
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
                
                # Check if debit is rejected due to insufficient funds
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
                source = account
                target = target_account
                
                # Calculate fee
                fee = 1.00 if amount > 1000 else 0.00
                total_debit = amount + fee
                
                # Process transfer
                success = False
                
                if source == 'X':
                    before = balance_X
                    if before - total_debit < -500:
                        balance_X -= 15.00  # Rejection fee
                    else:
                        balance_X -= total_debit
                        success = True
                        if before >= 0 and balance_X < 0:
                            balance_X -= 25.00  # Overdraft fee
                elif source == 'Y':
                    before = balance_Y
                    if before - total_debit < -500:
                        balance_Y -= 15.00  # Rejection fee
                    else:
                        balance_Y -= total_debit
                        success = True
                        if before >= 0 and balance_Y < 0:
                            balance_Y -= 25.00  # Overdraft fee
                elif source == 'Z':
                    before = balance_Z
                    if before - total_debit < -500:
                        balance_Z -= 15.00  # Rejection fee
                    else:
                        balance_Z -= total_debit
                        success = True
                        if before >= 0 and balance_Z < 0:
                            balance_Z -= 25.00  # Overdraft fee
                
                # If transfer succeeded, credit the target account
                if success:
                    if target == 'X':
                        balance_X += amount
                    elif target == 'Y':
                        balance_Y += amount
                    elif target == 'Z':
                        balance_Z += amount
            
            event_index += 1
        
        # End of day processing
        # Update minimum balances
        min_balance_X = min(min_balance_X, balance_X)
        min_balance_Y = min(min_balance_Y, balance_Y)
        min_balance_Z = min(min_balance_Z, balance_Z)
        
        # Accrue interest
        def accrue_interest(balance):
            if balance > 0:
                return min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                return balance * 0.18 / 365
        
        accrued_interest_X += accrue_interest(balance_X)
        accrued_interest_Y += accrue_interest(balance_Y)
        accrued_interest_Z += accrue_interest(balance_Z)
        
        # Period close (days 30 and 60)
        if day == 30 or day == 60:
            # Round accrued interest to 2 decimal places
            rounded_interest_X = round(accrued_interest_X, 2)
            rounded_interest_Y = round(accrued_interest_Y, 2)
            rounded_interest_Z = round(accrued_interest_Z, 2)
            
            # Add interest to balance
            balance_X += rounded_interest_X
            balance_Y += rounded_interest_Y
            balance_Z += rounded_interest_Z
            
            # Reset accrued interest
            accrued_interest_X = 0.0
            accrued_interest_Y = 0.0
            accrued_interest_Z = 0.0
            
            # Apply maintenance fee if minimum balance is below 1000
            if min_balance_X < 1000:
                balance_X -= 5.00
            if min_balance_Y < 1000:
                balance_Y -= 5.00
            if min_balance_Z < 1000:
                balance_Z -= 5.00
            
            # Reset minimum balances for next period
            min_balance_X = float('inf')
            min_balance_Y = float('inf')
            min_balance_Z = float('inf')
    
    # Return sum of final balances rounded to 2 decimal places
    return round(balance_X + balance_Y + balance_Z, 2)
```