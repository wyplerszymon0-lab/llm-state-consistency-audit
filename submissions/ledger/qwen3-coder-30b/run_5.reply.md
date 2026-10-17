<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:48:16+00:00 -->

```python
import math

def run() -> float:
    # Initialize accounts
    X = 4200.00
    Y = 800.00
    Z = 12000.00
    
    # Account balances and accrued interest
    balances = {'X': X, 'Y': Y, 'Z': Z}
    accrued_interest = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    
    # Track minimum balances for each period
    min_balances = {'X': [], 'Y': [], 'Z': []}
    
    # Events list (day, type, account, target_account, amount)
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
    event_dict = {}
    for day, type_, account, target_account, amount in events:
        if day not in event_dict:
            event_dict[day] = []
        event_dict[day].append((type_, account, target_account, amount))
    
    # Process each day from 1 to 60
    for day in range(1, 61):
        # Process events on this day
        if day in event_dict:
            for type_, account, target_account, amount in event_dict[day]:
                if type_ == 'DEPOSIT':
                    balances[account] += amount
                elif type_ == 'WITHDRAW':
                    before = balances[account]
                    total = amount
                    # Check if debit is rejected
                    if before - total < -500:
                        balances[account] -= 15.00  # Rejection fee
                    else:
                        balances[account] -= total
                        # Check overdraft fee
                        if before >= 0 and balances[account] < 0:
                            balances[account] -= 25.00
                elif type_ == 'TRANSFER':
                    source = account
                    target = target_account
                    before_source = balances[source]
                    fee = 1.00 if amount > 1000 else 0.00
                    total_debit = amount + fee
                    
                    # Check if debit is rejected
                    if before_source - total_debit < -500:
                        balances[source] -= 15.00  # Rejection fee
                    else:
                        balances[source] -= total_debit
                        # Check overdraft fee on source account
                        if before_source >= 0 and balances[source] < 0:
                            balances[source] -= 25.00
                        # Credit target account with amount only (not fee)
                        balances[target] += amount
    
        # End of day processing
        for acc in ['X', 'Y', 'Z']:
            balance = balances[acc]
            
            # Record minimum balance for this period
            if len(min_balances[acc]) < 30:
                min_balances[acc].append(balance)
            else:
                # This is a day after the first period, so it's in the second 30-day period
                pass
            
            # Accrue interest
            b = balance
            if b > 0:
                interest = min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365
            else:
                interest = b * 0.18 / 365
            accrued_interest[acc] += interest
            
        # Period close (day 30 or 60)
        if day == 30 or day == 60:
            for acc in ['X', 'Y', 'Z']:
                # Round accrued interest and add to balance
                rounded_interest = round(accrued_interest[acc], 2)
                balances[acc] += rounded_interest
                accrued_interest[acc] = 0.0
                
                # Check maintenance fee
                if len(min_balances[acc]) > 0:
                    period_min_balance = min(min_balances[acc])
                    if period_min_balance < 1000:
                        balances[acc] -= 5.00
                        
            # Reset min balances for next period if day is 30
            if day == 30:
                min_balances = {'X': [], 'Y': [], 'Z': []}
    
    return round(balances['X'] + balances['Y'] + balances['Z'], 2)
```