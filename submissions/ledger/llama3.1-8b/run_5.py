def run() -> float:
    accounts = {
        'X': {'balance': 4200.00, 'end_of_day_balances': [], 'accrued_interest': 0.0},
        'Y': {'balance': 800.00, 'end_of_day_balances': [], 'accrued_interest': 0.0},
        'Z': {'balance': 12000.00, 'end_of_day_balances': [], 'accrued_interest': 0.0}
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
        (58, 'DEPOSIT', 'Y', None, 150.00)
    ]

    for day in range(1, 61):
        for event in events:
            if event[0] == day:
                account = event[2]
                amount = event[4]
                target_account = event[3]
                if event[1] == 'DEPOSIT':
                    accounts[account]['balance'] += amount
                elif event[1] == 'WITHDRAW':
                    debit = amount
                    if accounts[account]['balance'] - debit < -500:
                        accounts[account]['balance'] -= 15.00
                    else:
                        accounts[account]['balance'] -= debit
                        if accounts[account]['balance'] < 0:
                            accounts[account]['balance'] -= 25.00
                elif event[1] == 'TRANSFER':
                    if amount > 1000:
                        fee = 1.00
                        debit = amount + fee
                    else:
                        fee = 0
                        debit = amount
                    if accounts[account]['balance'] - debit < -500:
                        accounts[account]['balance'] -= 15.00
                    else:
                        accounts[account]['balance'] -= debit
                        if accounts[account]['balance'] < 0:
                            accounts[account]['balance'] -= 25.00
                        accounts[target_account]['balance'] += amount
                        accounts[account]['balance'] -= fee

        for account in accounts:
            accounts[account]['end_of_day_balances'].append(accounts[account]['balance'])
            if accounts[account]['balance'] > 0:
                interest = (min(accounts[account]['balance'], 5000) * 0.02 / 365 +
                           max(accounts[account]['balance'] - 5000, 0) * 0.035 / 365)
            else:
                interest = accounts[account]['balance'] * 0.18 / 365
            accounts[account]['accrued_interest'] += interest

        if day == 30 or day == 60:
            for account in accounts:
                if accounts[account]['end_of_day_balances'][-1] < 1000:
                    accounts[account]['balance'] -= 5.00
                accounts[account]['accrued_interest'] = round(accounts[account]['accrued_interest'], 2)
                accounts[account]['balance'] += accounts[account]['accrued_interest']
                accounts[account]['accrued_interest'] = 0.0
                accounts[account]['end_of_day_balances'].pop()

    return round(accounts['X']['balance'] + accounts['Y']['balance'] + accounts['Z']['balance'], 2)
