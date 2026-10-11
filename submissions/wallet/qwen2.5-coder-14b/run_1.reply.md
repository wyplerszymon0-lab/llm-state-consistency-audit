<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-10-10T17:39:21+00:00 -->

```python
def run() -> float:
    # Initial state
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'PLN': 1.00, 'EUR': 4.3150, 'USD': 3.9820}
    premium_status = False
    spread = 0.004

    # Function to calculate wallet value in PLN
    def calculate_value():
        value = balances['PLN']
        for currency in ['EUR', 'USD']:
            value += round(balances[currency] * rates[currency], 2)
        return value

    # Function to handle DEPOSIT event
    def deposit(currency, amount):
        balances[currency] += amount

    # Function to handle RATE event
    def rate_change(currency, new_rate):
        rates[currency] = new_rate

    # Function to handle CONVERT event
    def convert(currency, target_currency, amount):
        if balances[currency] < amount:
            return
        p = round(amount * rates[currency], 2)
        received = round(p / rates[target_currency] * (1 - spread), 2)
        balances[currency] -= amount
        balances[target_currency] += received

    # Function to handle PAY event
    def pay(currency, amount):
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

    # Process events
    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            deposit(currency, amount)
        elif event_type == 'RATE':
            rate_change(currency, amount)
        elif event_type == 'CONVERT':
            convert(currency, target_currency, amount)
        elif event_type == 'PAY':
            pay(currency, amount)

        # Check premium status at the end of each day
        premium_status = calculate_value() >= 20000.00
        spread = 0.002 if premium_status else 0.004

    # Apply monthly fee at the end of day 30 and 60
    for day in [30, 60]:
        if calculate_value() < 5000.00:
            balances['PLN'] -= 15.00

    # Return the final wallet value in PLN
    return round(calculate_value(), 2)

# Example usage
if __name__ == "__main__":
    print(run())
```