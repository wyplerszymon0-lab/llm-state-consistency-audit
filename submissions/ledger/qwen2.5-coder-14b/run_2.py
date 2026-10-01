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
        (20, "WITHDRAW", "Z", "-", 700.00),
        (25, "TRANSFER", "Y", "Z", 12000.00),
        (33, "WITHDRAW", "X", "-", 6300.00),
        (36, "DEPOSIT", "X", "-", 1000.00),
        (40, "TRANSFER", "Z", "Y", 2100.00),
        (45, "WITHDRAW", "Y", "-", 5000.00),
        (47, "DEPOSIT", "Z", "-", 3000.00),
        (50, "TRANSFER", "Y", "X", 1000.00),
        (55, "WITHDRAW", "X", "-", 300.00),
        (58, "DEPOSIT", "Y", "-", 150.00),
    ]

    # Initialize accrued interest and minimum balances
    accrued_interest = {
        "X": 0.0,
        "Y": 0.0,
        "Z": 0.0
    }
    min_balances = {
        "X": [float('inf')] * 30,
        "Y": [float('inf')] * 30,
        "Z": [float('inf')] * 30
    }

    def apply_event(day, event_type, account, target_account, amount):
        nonlocal X, Y, Z
        if event_type == "DEPOSIT":
            if account == "X":
                X += amount
            elif account == "Y":
                Y += amount
            elif account == "Z":
                Z += amount
        elif event_type == "WITHDRAW":
            if account == "X":
                if X - amount < -500:
                    X -= 15.00
                else:
                    X -= amount
                    if X < 0:
                        X -= 25.00
            elif account == "Y":
                if Y - amount < -500:
                    Y -= 15.00
                else:
                    Y -= amount
                    if Y < 0:
                        Y -= 25.00
            elif account == "Z":
                if Z - amount < -500:
                    Z -= 15.00
                else:
                    Z -= amount
                    if Z < 0:
                        Z -= 25.00
        elif event_type == "TRANSFER":
            fee = 1.00 if amount > 1000 else 0.00
            total = amount + fee
            if account == "X":
                if X - total < -500:
                    X -= 15.00
                else:
                    X -= total
                    if X < 0:
                        X -= 25.00
                    else:
                        if target_account == "Y":
                            Y += amount
                        elif target_account == "Z":
                            Z += amount
            elif account == "Y":
                if Y - total < -500:
                    Y -= 15.00
                else:
                    Y -= total
                    if Y < 0:
                        Y -= 25.00
                    else:
                        if target_account == "X":
                            X += amount
                        elif target_account == "Z":
                            Z += amount
            elif account == "Z":
                if Z - total < -500:
                    Z -= 15.00
                else:
                    Z -= total
                    if Z < 0:
                        Z -= 25.00
                    else:
                        if target_account == "X":
                            X += amount
                        elif target_account == "Y":
                            Y += amount

    def accrue_interest(balance):
        if balance > 0:
            return min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
        else:
            return balance * 0.18 / 365

    def close_period(account):
        nonlocal accrued_interest, X, Y, Z
        accrued_interest[account] = round(accrued_interest[account], 2)
        if account == "X":
            X += accrued_interest[account]
        elif account == "Y":
            Y += accrued_interest[account]
        elif account == "Z":
            Z += accrued_interest[account]
        accrued_interest[account] = 0.0
        if min(min_balances[account]) < 1000:
            if account == "X":
                X -= 5.00
            elif account == "Y":
                Y -= 5.00
            elif account == "Z":
                Z -= 5.00

    # Process events
    for day, event_type, account, target_account, amount in events:
        apply_event(day, event_type, account, target_account, amount)

    # Process end of day for days 1 to 60
    for day in range(1, 61):
        balances = {"X": X, "Y": Y, "Z": Z}
        for account, balance in balances.items():
            accrued_interest[account] += accrue_interest(balance)
            min_balances[account][day % 30] = min(min_balances[account][day % 30], balance)
        if day == 30 or day == 60:
            close_period("X")
            close_period("Y")
            close_period("Z")

    # Return the sum of balances after day 60
    return round(X + Y + Z, 2)
