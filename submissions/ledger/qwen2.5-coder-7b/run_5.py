from decimal import Decimal, ROUND_HALF_UP

def run() -> float:
    X, Y, Z = Decimal('4200.00'), Decimal('800.00'), Decimal('12000.00')
    end_of_day_balances = [[], [], []]
    accrued_interests = [Decimal('0.00'), Decimal('0.00'), Decimal('0.00')]
    fees = [Decimal('0.00'), Decimal('0.00'), Decimal('0.00')]
    
    events = [
        (1, 'DEPOSIT', 'Y', '-', Decimal('300.00')),
        (3, 'WITHDRAW', 'Y', '-', Decimal('1500.00')),
        (5, 'TRANSFER', 'Z', 'X', Decimal('2500.00')),
        (8, 'WITHDRAW', 'Y', '-', Decimal('200.00')),
        (10, 'DEPOSIT', 'Y', '-', Decimal('2000.00')),
        (12, 'TRANSFER', 'X', 'Y', Decimal('800.00')),
        (15, 'WITHDRAW', 'Z', '-', Decimal('8000.00')),
        (20, 'WITHDRAW', 'Z', '-', Decimal('700.00')),
        (25, 'TRANSFER', 'Y', 'Z', Decimal('1200.00')),
        (33, 'WITHDRAW', 'X', '-', Decimal('6300.00')),
        (36, 'DEPOSIT', 'X', '-', Decimal('1000.00')),
        (40, 'TRANSFER', 'Z', 'Y', Decimal('2100.00')),
        (45, 'WITHDRAW', 'Y', '-', Decimal('5000.00')),
        (47, 'DEPOSIT', 'Z', '-', Decimal('3000.00')),
        (50, 'TRANSFER', 'Y', 'X', Decimal('1000.00')),
        (55, 'WITHDRAW', 'X', '-', Decimal('300.00')),
        (58, 'DEPOSIT', 'Y', '-', Decimal('150.00'))
    ]
    
    for day, event_type, account, target_account, amount in events:
        if account == 'X':
            account_index = 0
        elif account == 'Y':
            account_index = 1
        elif account == 'Z':
            account_index = 2
        
        if target_account == '-':
            target_index = None
        elif target_account == 'X':
            target_index = 0
        elif target_account == 'Y':
            target_index = 1
        elif target_account == 'Z':
            target_index = 2
        
        if event_type == 'DEPOSIT':
            X += amount if account == 'X' else amount if account == 'Y' else amount
            Y += amount if account == 'Y' else amount if account == 'X' else amount
            Z += amount if account == 'Z' else amount if account == 'X' else amount
        elif event_type == 'WITHDRAW':
            if target_index is None:
                if account == 'X':
                    fees[0] += Decimal('15.00') if X - amount < -500 else Decimal('25.00') if X < 0 else Decimal('0.00')
                    X -= amount if X - amount >= -500 else Decimal('0.00')
                elif account == 'Y':
                    fees[1] += Decimal('15.00') if Y - amount < -500 else Decimal('25.00') if Y < 0 else Decimal('0.00')
                    Y -= amount if Y - amount >= -500 else Decimal('0.00')
                elif account == 'Z':
                    fees[2] += Decimal('15.00') if Z - amount < -500 else Decimal('25.00') if Z < 0 else Decimal('0.00')
                    Z -= amount if Z - amount >= -500 else Decimal('0.00')
            else:
                if account == 'X':
                    fees[0] += Decimal('15.00') if X - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if X < 0 else Decimal('0.00')
                    X -= amount + Decimal('1.00') if X - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
                elif account == 'Y':
                    fees[1] += Decimal('15.00') if Y - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if Y < 0 else Decimal('0.00')
                    Y -= amount + Decimal('1.00') if Y - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
                elif account == 'Z':
                    fees[2] += Decimal('15.00') if Z - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if Z < 0 else Decimal('0.00')
                    Z -= amount + Decimal('1.00') if Z - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
        elif event_type == 'TRANSFER':
            if account == 'X':
                fees[0] += Decimal('15.00') if X - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if X < 0 else Decimal('0.00')
                X -= amount + Decimal('1.00') if X - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
            elif account == 'Y':
                fees[1] += Decimal('15.00') if Y - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if Y < 0 else Decimal('0.00')
                Y -= amount + Decimal('1.00') if Y - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
            elif account == 'Z':
                fees[2] += Decimal('15.00') if Z - (amount + Decimal('1.00')) < -500 else Decimal('25.00') if Z < 0 else Decimal('0.00')
                Z -= amount + Decimal('1.00') if Z - (amount + Decimal('1.00')) >= -500 else Decimal('0.00')
            if target_index is not None:
                if target_account == 'X':
                    Y += amount
                elif target_account == 'Y':
                    X += amount
                elif target_account == 'Z':
                    Z += amount
    
    for day in range(1, 61):
        if day % 30 == 1:
            end_of_day_balances[0].append(X)
            end_of_day_balances[1].append(Y)
            end_of_day_balances[2].append(Z)
            accrued_interests[0] += min(X, Decimal('5000.00')) * Decimal('0.02') / Decimal('365') + max(X - Decimal('5000.00'), Decimal('0.00')) * Decimal('0.035') / Decimal('365')
            accrued_interests[1] += min(Y, Decimal('5000.00')) * Decimal('0.02') / Decimal('365') + max(Y - Decimal('5000.00'), Decimal('0.00')) * Decimal('0.035') / Decimal('365')
            accrued_interests[2] += min(Z, Decimal('5000.00')) * Decimal('0.02') / Decimal('365') + max(Z - Decimal('5000.00'), Decimal('0.00')) * Decimal('0.035') / Decimal('365')
            if day in [30, 60]:
                accrued_interests[0] = accrued_interests[0].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                accrued_interests[1] = accrued_interests[1].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                accrued_interests[2] = accrued_interests[2].quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
                X += accrued_interests[0]
                Y += accrued_interests[1]
                Z += accrued_interests[2]
                if min(end_of_day_balances[0]) < Decimal('1000.00'):
                    X -= Decimal('5.00')
                if min(end_of_day_balances[1]) < Decimal('1000.00'):
                    Y -= Decimal('5.00')
                if min(end_of_day_balances[2]) < Decimal('1000.00'):
                    Z -= Decimal('5.00')
                end_of_day_balances[0] = []
                end_of_day_balances[1] = []
                end_of_day_balances[2] = []
                accrued_interests[0] = Decimal('0.00')
                accrued_interests[1] = Decimal('0.00')
                accrued_interests[2] = Decimal('0.00')
    
    return round(X + Y + Z, 2)

# Example usage
# result = run()
# print(result)
