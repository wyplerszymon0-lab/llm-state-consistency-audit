def run() -> float:
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'EUR': 4.3150, 'USD': 3.9820}
    spread = 0.004
    premium = False

    def get_value():
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)
        value += round(balances['USD'] * rates['USD'], 2)
        return value

    def round_half_to_even(n):
        return round(n, 2)

    def round_half_away_from_zero(n):
        if n >= 0:
            return round(n, 2)
        else:
            return round(n - 0.5, 2)

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
        if event_type == 'DEPOSIT':
            balances[currency] += round_half_to_even(amount)
        elif event_type == 'RATE':
            rates[currency] = amount
            premium = get_value() >= 20000.00
            spread = 0.002 if premium else 0.004
        elif event_type == 'CONVERT':
            if currency in balances and balances[currency] >= amount:
                p = round_half_to_even(amount * rates[currency])
                received = round_half_to_even(p / rates[target_currency] * (1 - spread))
                balances[currency] -= amount
                balances[target_currency] += received
        elif event_type == 'PAY':
            if currency in balances and balances[currency] >= amount:
                balances[currency] -= amount
            else:
                shortfall = round_half_to_even(amount - balances[currency])
                cost = round_half_to_even(shortfall * rates[currency] * (1 + spread + 0.005))
                if currency == 'PLN' or (currency != 'PLN' and balances['PLN'] >= cost):
                    balances['PLN'] -= cost
                else:
                    balances['PLN'] -= 10.00

    premium = get_value() >= 20000.00
    spread = 0.002 if premium else 0.004

    if day == 60:
        if get_value() < 5000.00:
            balances['PLN'] -= 15.00

    return round_half_away_from_zero(get_value())

print(run())
