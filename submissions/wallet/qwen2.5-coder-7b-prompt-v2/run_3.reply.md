<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T11:42:26+00:00 -->

```python
def run() -> float:
    # Initial balances and exchange rates
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Event processing
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
    
    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balances[currency] += amount
        elif event_type == 'RATE':
            rates[currency] = amount
        elif event_type == 'CONVERT':
            if balances[currency] < amount:
                continue
            p = round(amount * rates[currency], 2)
            received = round(p / rates[target_currency] * (1 - 0.002), 2) if rates[currency] == rates[target_currency] else round(p / rates[target_currency] * (1 - 0.004), 2)
            balances[currency] -= amount
            balances[target_currency] += received
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                balances[currency] -= amount
            else:
                shortfall = amount - balances[currency]
                cost = round(shortfall * rates[currency] * (1 + 0.004 + 0.005), 2)
                if currency == 'PLN' or balances['PLN'] < cost:
                    balances['PLN'] -= 10.00
                else:
                    balances['PLN'] -= cost
                    balances[currency] = 0
    
    # Calculate the wallet value in PLN
    wallet_value = balances['PLN']
    wallet_value += round(balances['EUR'] * rates['EUR'], 2)
    wallet_value += round(balances['USD'] * rates['USD'], 2)
    
    # Apply monthly fee if applicable
    if day in [30, 60]:
        if wallet_value < 5000.00:
            wallet_value -= 15.00
    
    return round(wallet_value, 2)

# Print the final wallet value
print(run())
```