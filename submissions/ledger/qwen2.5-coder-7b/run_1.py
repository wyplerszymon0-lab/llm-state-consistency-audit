def run() -> float:
    accounts = {'X': 4200.00, 'Y': 800.00, 'Z': 12000.00}
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
    
    end_of_day_balances = {account: [] for account in accounts}
    accrued_interest = {account: 0.0 for account in accounts}
    
    def apply_transaction(account, amount, fee=0):
        if amount > 1000:
            fee = 1.00
        total = amount + fee
        balance = accounts[account]
        if balance - total < -500:
            accounts[account] -= 15.00
        else:
            accounts[account] -= total
            if balance >= 0 and accounts[account] < 0:
                accounts[account] -= 25.00
    
    def process_events(day):
        for event in events:
            if event[0] == day:
                _, event_type, account, target_account, amount = event
                if event_type == 'DEPOSIT':
                    accounts[account] += amount
                elif event_type == 'WITHDRAW':
                    apply_transaction(account, amount)
                elif event_type == 'TRANSFER':
                    apply_transaction(account, amount, fee=1.00 if amount > 1000 else 0.0)
                    if accounts[account] >= 0:
                        accounts[target_account] += amount
    
    for day in range(1, 61):
        process_events(day)
        for account in accounts:
            end_of_day_balances[account].append(accounts[account])
    
    for account in accounts:
        balance = accounts[account]
        if day == 30 or day == 60:
            accrued_interest[account] = round(accrued_interest[account], 2)
            balance += accrued_interest[account]
            accrued_interest[account] = 0
            if min(end_of_day_balances[account]) < 1000:
                balance -= 5.00
        accounts[account] = balance
    
    return round(sum(accounts.values()), 2)

print(run())
