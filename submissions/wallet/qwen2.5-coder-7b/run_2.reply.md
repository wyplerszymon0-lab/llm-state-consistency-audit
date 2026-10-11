<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-10-10T11:47:02+00:00 -->

```python
def run() -> float:
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'PLN': 1, 'EUR': 4.3150, 'USD': 3.9820}
    premium_threshold = 20000.00
    spread_premium = 0.002
    spread_non_premium = 0.004
    monthly_fee = 15.00
    decline_fee = 10.00
    rounding_precision = 2

    def round_half_even(value: float) -> float:
        return round(value, rounding_precision)

    def round_half_away_from_zero(value: float) -> float:
        if value >= 0:
            return round(value, rounding_precision) + (0.5 / 10 ** rounding_precision)
        else:
            return round(value, rounding_precision) - (0.5 / 10 ** rounding_precision)

    def convert(amount: float, currency: str, target_currency: str) -> None:
        rate = rates[currency]
        p = round_half_even(amount * rate)
        received = round_half_even(p / rates[target_currency] * (1 - spread_premium if is_premium else spread_non_premium))
        balances[currency] -= amount
        balances[target_currency] += received

    def pay(amount: float, currency: str) -> None:
        rate = rates[currency]
        if balances[currency] >= amount:
            balances[currency] -= amount
        else:
            shortfall = amount - balances[currency]
            cost = round_half_even(shortfall * rate * (1 + spread_premium + 0.005))
            if currency == 'PLN' or balances['PLN'] >= cost:
                balances['PLN'] -= cost
            else:
                balances['PLN'] -= decline_fee
            balances[currency] = 0

    def update_value() -> None:
        balances['PLN'] += sum(balances[currency] * rates[currency] for currency in ['EUR', 'USD'])
        balances['PLN'] = round_half_away_from_zero(balances['PLN'])

    is_premium = balances['PLN'] + balances['EUR'] * rates['EUR'] + balances['USD'] * rates['USD'] >= premium_threshold

    events = [
        (1, 'DEPOSIT', 'PLN', None, 2500.00),
        (3, 'PAY', 'EUR', None, 150.00),
        (5, 'CONVERT', 'PLN', 'EUR', 2000.00),
        (7, 'RATE', 'EUR', None, 4.3280),
        (8, 'PAY', 'USD', None, 620.00),
        (12, 'DEPOSIT', 'USD', None, 4000.00),
        (14, 'CONVERT', 'USD', 'EUR', 1500.37),
        (15, 'RATE', 'USD', None, 3.9455),
        (18, 'DEPOSIT', 'PLN', None, 6000.00),
        (20, 'CONVERT', 'EUR', 'PLN', 900.00),
        (22, 'PAY', 'PLN', None, 9000.00),
        (25, 'RATE', 'EUR', None, 4.2965),
        (28, 'PAY', 'EUR', None, 2400.00),
        (33, 'CONVERT', 'PLN', 'USD', 1800.00),
        (36, 'PAY', 'USD', None, 5200.00),
        (40, 'RATE', 'USD', None, 4.0110),
        (41, 'DEPOSIT', 'EUR', None, 300.00),
        (43, 'CONVERT', 'EUR', 'PLN', 50.00),
        (45, 'PAY', 'PLN', None, 1500.00),
        (48, 'CONVERT', 'USD', 'PLN', 755.00),
        (52, 'RATE', 'EUR', None, 4.3402),
        (55, 'PAY', 'EUR', None, 700.00),
        (58, 'PAY', 'USD', None, 2000.00),
    ]

    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balances[currency] += amount
        elif event_type == 'PAY':
            pay(amount, currency)
        elif event_type == 'CONVERT':
            convert(amount, currency, target_currency)
        elif event_type == 'RATE':
            rates[currency] = amount
        update_value()
        if day in [30, 60]:
            if balances['PLN'] < 5000.00:
                balances['PLN'] -= monthly_fee
        is_premium = balances['PLN'] + balances['EUR'] * rates['EUR'] + balances['USD'] * rates['USD'] >= premium_threshold

    return round_half_away_from_zero(balances['PLN'])

print(run())
```