<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-09-30T14:42:19+00:00 -->

```python
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
        (20, 'WITHDRAW', 'Z', '-', 700.00),
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

    # Interest calculation function
    def interest(b):
        if b > 0:
            return min(b, 5000) * 0.02 / 365 + max(b - 5000, 0) * 0.035 / 365
        else:
            return b * 0.18 / 365

    # Debit function
    def debit(balance, total):
        if balance - total < -500:
            return balance - 15.00, False
        new_balance = balance - total
        if balance >= 0 and new_balance < 0:
            return new_balance - 25.00, True
        return new_balance, True

    # Periods for minimum balance tracking
    periods = [list(range(1, 31)), list(range(31, 61))]

    # Simulate each day
    for d in range(1, 61):
        # Process events for the current day
        for day, event_type, account, target_account, amount in events:
            if day == d:
                if event_type == 'DEPOSIT':
                    if account == 'X':
                        X += amount
                    elif account == 'Y':
                        Y += amount
                    else:
                        Z += amount
                elif event_type == 'WITHDRAW':
                    if account == 'X':
                        X, _ = debit(X, amount)
                    elif account == 'Y':
                        Y, _ = debit(Y, amount)
                    else:
                        Z, _ = debit(Z, amount)
                elif event_type == 'TRANSFER':
                    fee = 1.00 if amount > 1000 else 0.00
                    if account == 'X':
                        X, success = debit(X, amount + fee)
                        if success and target_account == 'Y':
                            Y += amount
                        elif success and target_account == 'Z':
                            Z += amount
                    elif account == 'Y':
                        Y, success = debit(Y, amount + fee)
                        if success and target_account == 'X':
                            X += amount
                        elif success and target_account == 'Z':
                            Z += amount
                    else:
                        Z, success = debit(Z, amount + fee)
                        if success and target_account == 'X':
                            X += amount
                        elif success and target_account == 'Y':
                            Y += amount

        # End of day interest accrual
        X += interest(X)
        Y += interest(Y)
        Z += interest(Z)

        # End of period logic
        if d in [30, 60]:
            # Round accrued interest and add to balance
            X = round(X, 2)
            Y = round(Y, 2)
            Z = round(Z, 2)
            # Reset accrued interest
            X = 0.0
            Y = 0.0
            Z = 0.0
            # Maintenance fee if minimum balance is below 1000
            if min(min(X, Y, Z) for period in periods if d in period) < 1000:
                X -= 5.00
                Y -= 5.00
                Z -= 5.00

    # Return the sum of the balances after day 60
    return round(X + Y + Z, 2)

# Example usage
if __name__ == "__main__":
    print(run())
```

This Python program simulates the described bank ledger system, processes the events for each day, and calculates the final balances after day 60, including interest accrual, overdraft fees, and maintenance fees. The `run()` function returns the sum of the three balances rounded to two decimal places.