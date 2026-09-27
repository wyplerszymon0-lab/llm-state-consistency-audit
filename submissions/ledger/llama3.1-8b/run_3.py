from decimal import Decimal, ROUND_HALF_UP

class BankAccount:
    def __init__(self, initial_balance: float):
        self.balance = Decimal(str(initial_balance))
        self.end_of_day_balances = [[Decimal('0')] * 30 for _ in range(2)]
        self.accrued_interest = Decimal('0')
        self.lowest_balance = Decimal('0')

    def debit(self, amount: float, reject_fee: float = 0, overdraft_fee: float = 0) -> bool:
        if self.balance - Decimal(str(amount)) < Decimal('-500'):
            self.balance -= Decimal(str(reject_fee))
            return False
        self.balance -= Decimal(str(amount))
        if self.balance >= Decimal('0') and self.balance < Decimal('0'):
            self.balance -= Decimal(str(overdraft_fee))
        return True

    def update_interest(self) -> None:
        if self.balance > Decimal('0'):
            min_balance = min(self.balance, Decimal('5000'))
            self.accrued_interest += (min_balance * Decimal('0.02') / Decimal('365')) + \
                                    ((self.balance - Decimal('5000')) * Decimal('0.035') / Decimal('365'))
        else:
            self.accrued_interest += self.balance * Decimal('0.18') / Decimal('365')

    def record_end_of_day_balance(self, day: int) -> None:
        if day <= 30:
            self.end_of_day_balances[0][day - 1] = self.balance
        else:
            self.end_of_day_balances[1][day - 31] = self.balance

    def close_period(self, day: int) -> None:
        if day in [30, 60]:
            self.balance += Decimal(str(round(self.accrued_interest, 2)))
            self.accrued_interest = Decimal('0')
            for balance in self.end_of_day_balances[day // 30]:
                if balance < Decimal('1000'):
                    self.balance -= Decimal('5.00')
                self.lowest_balance = min(self.lowest_balance, balance)


def run() -> float:
    accounts = [BankAccount(Decimal('4200.00')), BankAccount(Decimal('800.00')), BankAccount(Decimal('12000.00'))]

    events = [
        (1, 'DEPOSIT', 1, None, Decimal('300.00')),
        (3, 'WITHDRAW', 1, None, Decimal('1500.00')),
        (5, 'TRANSFER', 2, 0, Decimal('2500.00')),
        (8, 'WITHDRAW', 1, None, Decimal('200.00')),
        (10, 'DEPOSIT', 1, None, Decimal('2000.00')),
        (12, 'TRANSFER', 0, 1, Decimal('800.00')),
        (15, 'WITHDRAW', 2, None, Decimal('8000.00')),
        (20, 'WITHDRAW', 2, None, Decimal('700.00')),
        (25, 'TRANSFER', 1, 2, Decimal('1200.00')),
        (33, 'WITHDRAW', 0, None, Decimal('6300.00')),
        (36, 'DEPOSIT', 0, None, Decimal('1000.00')),
        (40, 'TRANSFER', 2, 1, Decimal('2100.00')),
        (45, 'WITHDRAW', 1, None, Decimal('5000.00')),
        (47, 'DEPOSIT', 2, None, Decimal('3000.00')),
        (50, 'TRANSFER', 1, 0, Decimal('1000.00')),
        (55, 'WITHDRAW', 0, None, Decimal('300.00')),
        (58, 'DEPOSIT', 1, None, Decimal('150.00'))
    ]

    for day, event_type, account, target_account, amount in events:
        for account_obj in accounts:
            if account_obj.balance < Decimal('-500') and (account_obj.balance - Decimal(str(amount)) < Decimal('-500')):
                account_obj.accrued_interest -= Decimal('15.00')
            if event_type == 'TRANSFER':
                if amount > Decimal('1000'):
                    amount += Decimal('1.00')
                if not account_obj.debit(amount):
                    if target_account is not None:
                        target_account_obj = accounts[target_account]
                        target_account_obj.balance += amount
            elif event_type == 'DEPOSIT':
                account_obj.balance += amount
            elif event_type == 'WITHDRAW':
                account_obj.debit(amount)
            elif event_type == 'TRANSFER':
                if not account_obj.debit(amount):
                    if target_account is not None:
                        target_account_obj = accounts[target_account]
                        target_account_obj.balance += amount

        for account_obj in accounts:
            account_obj.update_interest()
            account_obj.record_end_of_day_balance(day)

        if day in [30, 60]:
            for account_obj in accounts:
                account_obj.close_period(day)

    total = sum([float(account.balance) for account in accounts])
    return round(total, 2)


print(run())
