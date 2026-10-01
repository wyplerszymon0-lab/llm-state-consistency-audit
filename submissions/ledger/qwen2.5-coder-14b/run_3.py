def run() -> float:
    # Initial balances
    X = 4200.00
    Y = 800.00
    Z = 12000.00
    
    # Event list
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
    
    # Helper functions
    def apply_fee(balance, fee):
        if balance - fee < -500:
            return balance - 15.00
        else:
            return balance - fee
    
    def apply_debit(balance, debit, fee):
        if balance - debit < -500:
            return apply_fee(balance, 15.00)
        else:
            new_balance = balance - debit
            if balance >= 0 and new_balance < 0:
                new_balance -= 25.00
            return new_balance
    
    def process_deposit(balance, amount):
        return balance + amount
    
    def process_withdraw(balance, amount):
        return apply_debit(balance, amount, 0)
    
    def process_transfer(source_balance, target_balance, amount):
        fee = 1.00 if amount > 1000 else 0.00
        new_source_balance = apply_debit(source_balance, amount + fee, 0)
        if new_source_balance == source_balance:  # Debit was rejected
            return source_balance, target_balance
        else:
            return new_source_balance, target_balance + amount
    
    # Simulation
    balances = {'X': X, 'Y': Y, 'Z': Z}
    accrued_interest = {'X': 0.0, 'Y': 0.0, 'Z': 0.0}
    min_balances = {'X': [X] * 30, 'Y': [Y] * 30, 'Z': [Z] * 30}
    
    for day in range(1, 61):
        for event in events:
            if event[0] == day:
                e_day, e_type, e_account, e_target_account, e_amount = event
                if e_type == 'DEPOSIT':
                    balances[e_account] = process_deposit(balances[e_account], e_amount)
                elif e_type == 'WITHDRAW':
                    balances[e_account] = process_withdraw(balances[e_account], e_amount)
                elif e_type == 'TRANSFER':
                    balances[e_account], balances[e_target_account] = process_transfer(
                        balances[e_account], balances[e_target_account], e_amount
                    )
        
        # End of day processing
        for account in ['X', 'Y', 'Z']:
            balance = balances[account]
            if balance > 0:
                accrued_interest[account] += min(balance, 5000) * 0.02 / 365 + max(balance - 5000, 0) * 0.035 / 365
            else:
                accrued_interest[account] += balance * 0.18 / 365
            
            min_balances[account].append(balance)
            min_balances[account].pop(0)
        
        # Period close
        if day in [30, 60]:
            for account in ['X', 'Y', 'Z']:
                accrued_interest[account] = round(accrued_interest[account], 2)
                balances[account] += accrued_interest[account]
                accrued_interest[account] = 0.0
                if min(min_balances[account]) < 1000:
                    balances[account] -= 5.00
    
    # Final answer
    return round(balances['X'] + balances['Y'] + balances['Z'], 2)

# Example usage
if __name__ == "__main__":
    print(run())
