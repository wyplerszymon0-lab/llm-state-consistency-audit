import math

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.end_of_day_bals = [balance]
        self.accrued_interest = 0.0

    def debit(self, amount):
        if self.balance - amount < -500:
            self.balance -= 15.0
            return False
        else:
            self.balance -= amount
            if self.balance < 0 and self.balance >= -500:
                self.balance -= 25.0
            return True

    def transfer(self, amount, fee, target):
        if self.debit(amount + fee):
            target.debit(amount)
            return True
        else:
            return False

    def process_day(self, day):
        self.end_of_day_bals.append(self.balance)
        interest = self.calculate_interest()
        self.accrued_interest += interest
        if day % 30 == 0 or day == 60:
            self.process_close()

    def process_close(self):
        self.accrued_interest = round(self.accrued_interest, 2)
        self.balance += self.accrued_interest
        self.accrued_interest = 0.0
        if self.end_of_day_bals[-1] < 1000:
            self.balance -= 5.0

    def calculate_interest(self):
        if self.balance > 0:
            return min(self.balance, 5000) * 0.02 / 365 + max(self.balance - 5000, 0) * 0.035 / 365
        else:
            return self.balance * 0.18 / 365

def run():
    accounts = {
        'X': Account('X', 4200.00),
        'Y': Account('Y', 800.00),
        'Z': Account('Z', 12000.00),
    }

    events = [
        ('1', 'DEPOSIT', 'Y', None, 300.00),
        ('3', 'WITHDRAW', 'Y', None, 1500.00),
        ('5', 'TRANSFER', 'Z', 'X', 2500.00),
        ('8', 'WITHDRAW', 'Y', None, 200.00),
        ('10', 'DEPOSIT', 'Y', None, 2000.00),
        ('12', 'TRANSFER', 'X', 'Y', 800.00),
        ('15', 'WITHDRAW', 'Z', None, 8000.00),
        ('20', 'WITHDRAW', 'Z', None, 700.00),
        ('25', 'TRANSFER', 'Y', 'Z', 1200.00),
        ('33', 'WITHDRAW', 'X', None, 6300.00),
        ('36', 'DEPOSIT', 'X', None, 1000.00),
        ('40', 'TRANSFER', 'Z', 'Y', 2100.00),
        ('45', 'WITHDRAW', 'Y', None, 5000.00),
        ('47', 'DEPOSIT', 'Z', None, 3000.00),
        ('50', 'TRANSFER', 'Y', 'X', 1000.00),
        ('55', 'WITHDRAW', 'X', None, 300.00),
        ('58', 'DEPOSIT', 'Y', None, 150.00),
    ]

    for event in events:
        day, event_type, account, target, amount = event
        fee = 1.00 if int(amount) > 1000 else 0
        accounts[account].process_day(int(day))
        if event_type == 'DEPOSIT':
            accounts[account].balance += float(amount)
        elif event_type == 'WITHDRAW':
            accounts[account].debit(float(amount))
        elif event_type == 'TRANSFER':
            accounts[account].transfer(float(amount), fee, accounts[target])

    total = 0.0
    for account in accounts.values():
        total += round(account.balance, 2)
    return total
