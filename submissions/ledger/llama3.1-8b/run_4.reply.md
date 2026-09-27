<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-26T17:25:33+00:00 -->

```python
import math

class Account:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance
        self.end_balances = []
        self.accrued_interest = 0

    def debit(self, amount, fee=0):
        if self.balance - amount - fee < -500:
            self.balance -= 15
        else:
            self.balance -= amount + fee

        if self.balance >= 0 and self.balance - amount - fee < 0:
            self.balance -= 25

    def deposit(self, amount):
        self.balance += amount

    def transfer(self, amount, fee=0, target):
        self.debit(amount + fee, fee)
        target.deposit(amount)

    def accrue_interest(self):
        if self.balance > 0:
            min_b = min(self.balance, 5000)
            max_b = max(self.balance - 5000, 0)
            self.accrued_interest += min_b * 0.02 / 365 + max_b * 0.035 / 365
        elif self.balance <= 0:
            self.accrued_interest += self.balance * 0.18 / 365

    def close_period(self, day):
        if day in [30, 60]:
            self.balance += round(self.accrued_interest, 2)
            self.accrued_interest = 0

            if min(self.end_balances) < 1000:
                self.balance -= 5

    def track_end_balance(self, balance):
        self.end_balances.append(balance)

def run() -> float:
    accounts = {
        'X': Account('X', 4200.00),
        'Y': Account('Y', 800.00),
        'Z': Account('Z', 12000.00),
    }

    events = [
        ('1', 'DEPOSIT', 'Y', '', 300.00),
        ('3', 'WITHDRAW', 'Y', '', 1500.00),
        ('5', 'TRANSFER', 'Z', 'X', 2500.00),
        ('8', 'WITHDRAW', 'Y', '', 200.00),
        ('10', 'DEPOSIT', 'Y', '', 2000.00),
        ('12', 'TRANSFER', 'X', 'Y', 800.00),
        ('15', 'WITHDRAW', 'Z', '', 8000.00),
        ('20', 'WITHDRAW', 'Z', '', 700.00),
        ('25', 'TRANSFER', 'Y', 'Z', 1200.00),
        ('33', 'WITHDRAW', 'X', '', 6300.00),
        ('36', 'DEPOSIT', 'X', '', 1000.00),
        ('40', 'TRANSFER', 'Z', 'Y', 2100.00),
        ('45', 'WITHDRAW', 'Y', '', 5000.00),
        ('47', 'DEPOSIT', 'Z', '', 3000.00),
        ('50', 'TRANSFER', 'Y', 'X', 1000.00),
        ('55', 'WITHDRAW', 'X', '', 300.00),
        ('58', 'DEPOSIT', 'Y', '', 150.00),
    ]

    for event in events:
        day, event_type, account, target_account, amount = event
        fee = 1.00 if float(amount) > 1000 else 0
        if event_type == 'DEPOSIT':
            accounts[account].deposit(float(amount))
        elif event_type == 'WITHDRAW':
            accounts[account].debit(float(amount))
        elif event_type == 'TRANSFER':
            accounts[account].transfer(float(amount), fee, accounts[target_account])

        for account_name in accounts:
            accounts[account_name].accrue_interest()
            accounts[account_name].track_end_balance(accounts[account_name].balance)

        if int(day) in [30, 60]:
            for account_name in accounts:
                accounts[account_name].close_period(int(day))

    result = 0
    for account in accounts.values():
        result += round(account.balance, 2)

    return result
```