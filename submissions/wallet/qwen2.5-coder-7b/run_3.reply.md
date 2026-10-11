<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-10-10T11:47:26+00:00 -->

```python
class Wallet:
    def __init__(self):
        self.balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
        self.rates = {'PLN': 1, 'EUR': 4.3150, 'USD': 3.9820}
        self.spread = 0.004
        self.is_premium = False

    def run(self) -> float:
        events = [
            (1, 'DEPOSIT', 'PLN', '-', 2500.00),
            (3, 'PAY', 'EUR', '-', 150.00),
            (5, 'CONVERT', 'PLN', 'EUR', 2000.00),
            (7, 'RATE', 'EUR', '-', 4.3280),
            (8, 'PAY', 'USD', '-', 620.00),
            (12, 'DEPOSIT', 'USD', '-', 4000.00),
            (14, 'CONVERT', 'USD', 'EUR', 1500.37),
            (15, 'RATE', 'USD', '-', 3.9455),
            (18, 'DEPOSIT', 'PLN', '-', 6000.00),
            (20, 'CONVERT', 'EUR', 'PLN', 900.00),
            (22, 'PAY', 'PLN', '-', 9000.00),
            (25, 'RATE', 'EUR', '-', 4.2965),
            (28, 'PAY', 'EUR', '-', 2400.00),
            (33, 'CONVERT', 'PLN', 'USD', 1800.00),
            (36, 'PAY', 'USD', '-', 5200.00),
            (40, 'RATE', 'USD', '-', 4.0110),
            (41, 'DEPOSIT', 'EUR', '-', 300.00),
            (43, 'CONVERT', 'EUR', 'PLN', 50.00),
            (45, 'PAY', 'PLN', '-', 1500.00),
            (48, 'CONVERT', 'USD', 'PLN', 755.00),
            (52, 'RATE', 'EUR', '-', 4.3402),
            (55, 'PAY', 'EUR', '-', 700.00),
            (58, 'PAY', 'USD', '-', 2000.00),
        ]

        for day, event_type, currency, target_currency, amount in events:
            self.process_event(event_type, currency, target_currency, amount)

        self.calculate_value()
        return self.calculate_value()

    def process_event(self, event_type, currency, target_currency, amount):
        if event_type == 'DEPOSIT':
            self.balances[currency] += amount
        elif event_type == 'RATE':
            self.rates[currency] = amount
        elif event_type == 'CONVERT':
            if currency == target_currency or amount > self.balances[currency]:
                return
            p = round(amount * self.rates[currency], 2)
            received = round(p / self.rates[target_currency] * (1 - self.spread), 2)
            self.balances[currency] -= amount
            self.balances[target_currency] += received
        elif event_type == 'PAY':
            if self.balances[currency] >= amount:
                self.balances[currency] -= amount
            else:
                shortfall = amount - self.balances[currency]
                cost = round(shortfall * self.rates[currency] * (1 + self.spread + 0.005), 2)
                if currency == 'PLN' or self.balances['PLN'] < cost:
                    self.balances['PLN'] -= 10.00
                else:
                    self.balances[currency] = 0
                    self.balances['PLN'] -= cost

    def calculate_value(self):
        pln_balance = self.balances['PLN']
        eur_balance = self.balances['EUR'] * self.rates['EUR']
        usd_balance = self.balances['USD'] * self.rates['USD']
        total_value = pln_balance + round(eur_balance, 2) + round(usd_balance, 2)
        self.is_premium = total_value >= 20000.00
        if self.is_premium:
            self.spread = 0.002
        if self.is_premium and (30 in events or 60 in events):
            pln_balance -= 15.00
        return pln_balance

# Run the simulation
wallet = Wallet()
result = wallet.run()
print(result)
```

This Python program simulates the wallet operations as described in the problem statement and calculates the final wallet value in PLN at the end of day 60.