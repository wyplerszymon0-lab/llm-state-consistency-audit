<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-10-10T17:50:09+00:00 -->

```python
def run() -> float:
    # Initial balances and exchange rates
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'PLN': 1.0000, 'EUR': 4.3150, 'USD': 3.9820}
    premium_status = True  # Initial premium status
    spread = 0.002  # Initial spread

    # Events
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
        (58, 'PAY', 'USD', '-', 2000.00)
    ]

    # Function to calculate wallet value in PLN
    def calculate_wallet_value():
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)
        value += round(balances['USD'] * rates['USD'], 2)
        return value

    # Process events
    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balances[currency] += amount
        elif event_type == 'RATE':
            rates[currency] = amount
        elif event_type == 'CONVERT':
            if balances[currency] >= amount:
                p = round(amount * rates[currency], 2)
                received = round(p / rates[target_currency] * (1 - spread), 2)
                balances[currency] -= amount
                balances[target_currency] += received
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                balances[currency] -= amount
            else:
                shortfall = amount - balances[currency]
                cost = round(shortfall * rates[currency] * (1 + spread + 0.005), 2)
                if currency == 'PLN' or balances['PLN'] < cost:
                    balances['PLN'] -= 10.00
                else:
                    balances[currency] = 0
                    balances['PLN'] -= cost

        # Update premium status and spread
        if day in (30, 60):
            value = calculate_wallet_value()
            if value < 5000.00:
                balances['PLN'] -= 15.00
            premium_status = value >= 20000.00
            spread = 0.002 if premium_status else 0.004

    # Return the final wallet value in PLN
    return round(calculate_wallet_value(), 2)
```