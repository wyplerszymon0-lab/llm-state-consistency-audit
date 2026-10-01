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

    # Function to apply a debit
    def apply_debit(balance, total):
        if balance - total < -500:
            balance -= 15.00
            return balance
        else:
            balance -= total
            if balance < 0:
                balance -= 25.00
            return balance

    # Function to apply an interest accrual
    def apply_interest(balance, accrued_interest):
        if balance > 0:
            accrued_interest += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
        else:
            accrued_interest += balance * 0.18 / 365
        return accrued_interest

    # Function to round to 2 decimal places, rounding halves away from zero
    def round_away_from_zero(value):
        return (value + 0.5) if value > 0 else (value - 0.5)

    # Simulate the days
    for day in range(1, 61):
        # Process events for the current day
        for event in events:
            if event[0] == day:
                eventType, account, target_account, amount = event[1], event[2], event[3], event[4]

                if eventType == 'DEPOSIT':
                    if account == 'X':
                        X += amount
                    elif account == 'Y':
                        Y += amount
                    elif account == 'Z':
                        Z += amount

                elif eventType == 'WITHDRAW':
                    if account == 'X':
                        X = apply_debit(X, amount)
                    elif account == 'Y':
                        Y = apply_debit(Y, amount)
                    elif account == 'Z':
                        Z = apply_debit(Z, amount)

                elif eventType == 'TRANSFER':
                    fee = 1.00 if amount > 1000 else 0.00
                    if account == 'X':
                        if X >= amount + fee:
                            X = apply_debit(X, amount + fee)
                            if target_account == 'Y':
                                Y += amount
                            elif target_account == 'Z':
                                Z += amount
                    elif account == 'Y':
                        if Y >= amount + fee:
                            Y = apply_debit(Y, amount + fee)
                            if target_account == 'X':
                                X += amount
                            elif target_account == 'Z':
                                Z += amount
                    elif account == 'Z':
                        if Z >= amount + fee:
                            Z = apply_debit(Z, amount + fee)
                            if target_account == 'X':
                                X += amount
                            elif target_account == 'Y':
                                Y += amount

        # Minimum balance tracking
        if day <= 30:
            min_balance_X_1_30 = min(min_balance_X_1_30, X)
            min_balance_Y_1_30 = min(min_balance_Y_1_30, Y)
            min_balance_Z_1_30 = min(min_balance_Z_1_30, Z)
        else:
            min_balance_X_31_60 = min(min_balance_X_31_60, X)
            min_balance_Y_31_60 = min(min_balance_Y_31_60, Y)
            min_balance_Z_31_60 = min(min_balance_Z_31_60, Z)

        # Interest accrual
        accrued_interest_X = apply_interest(X, accrued_interest_X)
        accrued_interest_Y = apply_interest(Y, accrued_interest_Y)
        accrued_interest_Z = apply_interest(Z, accrued_interest_Z)

        # Period close
        if day == 30 or day == 60:
            X = round_away_from_zero(X + round(accrued_interest_X, 2))
            Y = round_away_from_zero(Y + round(accrued_interest_Y, 2))
            Z = round_away_from_zero(Z + round(accrued_interest_Z, 2))
            accrued_interest_X = 0.00
            accrued_interest_Y = 0.00
            accrued_interest_Z = 0.00

            if day == 30:
                if min_balance_X_1_30 < 1000:
                    X -= 5.00
                if min_balance_Y_1_30 < 1000:
                    Y -= 5.00
                if min_balance_Z_1_30 < 1000:
                    Z -= 5.00
            else:
                if min_balance_X_31_60 < 1000:
                    X -= 5.00
                if min_balance_Y_31_60 < 1000:
                    Y -= 5.00
                if min_balance_Z_31_60 < 1000:
                    Z -= 5.00

    # Return the sum of the balances after day 60
    return round(X + Y + Z, 2)
