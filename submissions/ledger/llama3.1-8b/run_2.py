def run() -> float:
    import datetime

    accounts = {
        'X': {'balance': 4200.00, 'end_of_day_balance_history': [4200.00], 'accrued_interest': 0.00},
        'Y': {'balance': 800.00, 'end_of_day_balance_history': [800.00], 'accrued_interest': 0.00},
        'Z': {'balance': 12000.00, 'end_of_day_balance_history': [12000.00], 'accrued_interest': 0.00},
    }

    fee = 1.00

    events = [
        (1, 'DEPOSIT', 'Y', None, 300.00),
        (3, 'WITHDRAW', 'Y', None, 1500.00),
        (5, 'TRANSFER', 'Z', 'X', 2500.00),
        (8, 'WITHDRAW', 'Y', None, 200.00),
        (10, 'DEPOSIT', 'Y', None, 2000.00),
        (12, 'TRANSFER', 'X', 'Y', 800.00),
        (15, 'WITHDRAW', 'Z', None, 8000.00),
        (20, 'WITHDRAW', 'Z', None, 700.00),
        (25, 'TRANSFER', 'Y', 'Z', 1200.00),
        (33, 'WITHDRAW', 'X', None, 6300.00),
        (36, 'DEPOSIT', 'X', None, 1000.00),
        (40, 'TRANSFER', 'Z', 'Y', 2100.00),
        (45, 'WITHDRAW', 'Y', None, 5000.00),
        (47, 'DEPOSIT', 'Z', None, 3000.00),
        (50, 'TRANSFER', 'Y', 'X', 1000.00),
        (55, 'WITHDRAW', 'X', None, 300.00),
        (58, 'DEPOSIT', 'Y', None, 150.00),
    ]

    for i in range(60):
        day = i + 1

        if day % 30 == 0:
            for account in accounts:
                # Period close
                end_of_day_balance = accounts[account]['end_of_day_balance_history'][-1]
                if end_of_day_balance < 1000:
                    accounts[account]['balance'] -= 5.00
                # Interest accrual
                if accounts[account]['accrued_interest']:
                    interest = accounts[account]['accrued_interest']
                    accounts[account]['balance'] += interest
                    accounts[account]['accrued_interest'] = 0
                # Rounding and minimum balance tracking
                accounts[account]['balance'] = round(accounts[account]['balance'], 2)
                accounts[account]['end_of_day_balance_history'].append(accounts[account]['balance'])

        for event in events:
            if event[0] <= day:
                # Transaction rules
                account = event[2]
                target_account = event[3]
                amount = event[4]

                if event[1] == 'DEPOSIT':
                    accounts[account]['balance'] += amount
                elif event[1] == 'WITHDRAW':
                    before = accounts[account]['balance']
                    total = amount
                    if before - total < -500:
                        # Rejection
                        accounts[account]['balance'] -= 15.00
                    else:
                        accounts[account]['balance'] -= total
                        if before >= 0 and accounts[account]['balance'] < 0:
                            accounts[account]['balance'] -= 25.00
                elif event[1] == 'TRANSFER':
                    source_account = event[2]
                    fee = 1.00 if amount > 1000 else 0
                    before = accounts[source_account]['balance']
                    total = amount + fee
                    if before - total < -500:
                        # Rejection
                        accounts[source_account]['balance'] -= 15.00
                    else:
                        accounts[source_account]['balance'] -= total
                        if before >= 0 and accounts[source_account]['balance'] < 0:
                            accounts[source_account]['balance'] -= 25.00
                        if target_account:
                            accounts[target_account]['balance'] += amount

    # Answer
    answer = round(accounts['X']['balance'] + accounts['Y']['balance'] + accounts['Z']['balance'], 2)
    return answer
