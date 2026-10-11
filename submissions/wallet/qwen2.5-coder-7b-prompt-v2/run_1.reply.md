<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T11:41:42+00:00 -->

```python
def run() -> float:
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'EUR': 4.3150, 'USD': 3.9820}
    premium_status = balances['PLN'] + balances['EUR'] * rates['EUR'] + balances['USD'] * rates['USD'] >= 20000.00

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

    spread = 0.002 if premium_status else 0.004

    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balances[currency] += amount
        elif event_type == 'RATE':
            if target_currency == 'EUR':
                rates['EUR'] = amount
            elif target_currency == 'USD':
                rates['USD'] = amount
            premium_status = balances['PLN'] + balances['EUR'] * rates['EUR'] + balances['USD'] * rates['USD'] >= 20000.00
            spread = 0.002 if premium_status else 0.004
        elif event_type == 'CONVERT':
            if balances[currency] < amount:
                continue
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

    if day == 60:
        value_pln = balances['PLN']
        value_eur = balances['EUR'] * rates['EUR']
        value_usd = balances['USD'] * rates['USD']
        wallet_value = value_pln + value_eur + value_usd
        return round(wallet_value, 2)
    else:
        raise ValueError("Simulation ended before day 60")
```