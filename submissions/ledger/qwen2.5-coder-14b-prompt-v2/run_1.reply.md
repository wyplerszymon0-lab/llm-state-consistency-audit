<!-- model: ollama:qwen2.5-coder:14b | prompt v2 | 2026-10-10T12:10:04+00:00 -->

```python
def run() -> float:
    # Initial balances
    X = 4200.00
    Y = 800.00
    Z = 12000.00

    # Events
    events = [
        (1, "DEPOSIT", "Y", "-", 300.00),
        (3, "WITHDRAW", "Y", "-", 1500.00),
        (5, "TRANSFER", "Z", "X", 2500.00),
        (8, "WITHDRAW", "Y", "-", 200.00),
        (10, "DEPOSIT", "Y", "-", 2000.00),
        (12, "TRANSFER", "X", "Y", 800.00),
        (15, "WITHDRAW", "Z", "-", 8000.00),
        (20, "WITHDRAW", "Z", "-", 7000.00),
        (25, "TRANSFER", "Y", "Z", 1200.00),
        (33, "WITHDRAW", "X", "-", 6300.00),
        (36, "DEPOSIT", "X", "-", 1000.00),
        (40, "TRANSFER", "Z", "Y", 2100.00),
        (45, "WITHDRAW", "Y", "-", 5000.00),
        (47, "DEPOSIT", "Z", "-", 3000.00),
        (50, "TRANSFER", "Y", "X", 1000.00),
        (55, "WITHDRAW", "X", "-", 300.00),
        (58, "DEPOSIT", "Y", "-", 150.00),
    ]

    # Function to apply a debit with fees
    def apply_debit(balance, total):
        if balance - total < -500:
            balance -= 15.00
            return balance, True
        else:
            balance -= total
            if balance >= 0 and balance < 0:
                balance -= 25.00
            return balance, False

    # Function to apply an event
    def apply_event(balance, event):
        day, event_type, account, target_account, amount = event
        if event_type == "DEPOSIT":
            balance += amount
        elif event_type == "WITHDRAW":
            balance, _ = apply_debit(balance, amount)
        elif event_type == "TRANSFER":
            fee = 1.00 if amount > 1000 else 0.00
            balance, rejected = apply_debit(balance, amount + fee)
            if not rejected and target_account != "-":
                if target_account == "X":
                    X += amount
                elif target_account == "Y":
                    Y += amount
                elif target_account == "Z":
                    Z += amount
        return balance

    # Track minimum balances for each account
    min_balance_X = float('inf')
    min_balance_Y = float('inf')
    min_balance_Z = float('inf')

    # Track accrued interest for each account
    accrued_interest_X = 0.0
    accrued_interest_Y = 0.0
    accrued_interest_Z = 0.0

    # Process events
    current_day = 0
    for day, event_type, account, target_account, amount in events:
        if day > current_day:
            current_day = day
            # Apply interest and period close if necessary
            if current_day == 30 or current_day == 60:
                X = round(X + accrued_interest_X, 2)
                Y = round(Y + accrued_interest_Y, 2)
                Z = round(Z + accrued_interest_Z, 2)
                accrued_interest_X = 0.0
                accrued_interest_Y = 0.0
                accrued_interest_Z = 0.0
                if min_balance_X < 1000:
                    X -= 5.00
                if min_balance_Y < 1000:
                    Y -= 5.00
                if min_balance_Z < 1000:
                    Z -= 5.00
                min_balance_X = float('inf')
                min_balance_Y = float('inf')
                min_balance_Z = float('inf')
        # Apply the event
        if account == "X":
            X = apply_event(X, event)
        elif account == "Y":
            Y = apply_event(Y, event)
        elif account == "Z":
            Z = apply_event(Z, event)
        # Update minimum balances
        min_balance_X = min(min_balance_X, X)
        min_balance_Y = min(min_balance_Y, Y)
        min_balance_Z = min(min_balance_Z, Z)
        # Accrue interest
        accrued_interest_X += min(X, 5000) * 0.02 / 365 + max(X - 5000, 0) * 0.035 / 365 if X > 0 else X * 0.18 / 365
        accrued_interest_Y += min(Y, 5000) * 0.02 / 365 + max(Y - 5000, 0) * 0.035 / 365 if Y > 0 else Y * 0.18 / 365
        accrued_interest_Z += min(Z, 5000) * 0.02 / 365 + max(Z - 5000, 0) * 0.035 / 365 if Z > 0 else Z * 0.18 / 365

    # Apply interest and period close for day 60
    X = round(X + accrued_interest_X, 2)
    Y = round(Y + accrued_interest_Y, 2)
    Z = round(Z + accrued_interest_Z, 2)
    if min_balance_X < 1000:
        X -= 5.00
    if min_balance_Y < 1000:
        Y -= 5.00
    if min_balance_Z < 1000:
        Z -= 5.00

    # Return the final sum of balances
    return round(X + Y + Z, 2)
```