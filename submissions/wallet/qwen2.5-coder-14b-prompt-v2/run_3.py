def run() -> float:
    # Initial state
    balances = {
        'PLN': 3000.00,
        'EUR': 1200.00,
        'USD': 500.00
    }
    rates = {
        'PLN': 1.00,
        'EUR': 4.3150,
        'USD': 3.9820
    }
    premium = False
    spread = 0.004

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

    def calculate_value():
        value = balances['PLN']
        for currency in ['EUR', 'USD']:
            value += balances[currency] * rates[currency]
        return round(value, 2)

    def apply_monthly_fee():
        if calculate_value() < 5000.00:
            balances['PLN'] = round(balances['PLN'] - 15.00, 2)

    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balances[currency] = round(balances[currency] + amount, 2)
        elif event_type == 'RATE':
            rates[currency] = amount
        elif event_type == 'CONVERT':
            if balances[currency] >= amount:
                p = round(amount * rates[currency], 2)
                received = round(p / rates[target_currency] * (1 - spread), 2)
                balances[currency] = round(balances[currency] - amount, 2)
                balances[target_currency] = round(balances[target_currency] + received, 2)
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                balances[currency] = round(balances[currency] - amount, 2)
            else:
                shortfall = amount - balances[currency]
                if currency == 'PLN' or balances['PLN'] < round(shortfall * rates[currency] * (1 + spread + 0.005), 2):
                    balances['PLN'] = round(balances['PLN'] - 10.00, 2)
                else:
                    balances[currency] = 0
                    balances['PLN'] = round(balances['PLN'] - round(shortfall * rates[currency] * (1 + spread + 0.005), 2), 2)

        # Check premium status at the end of the day
        if day in [30, 60]:
            apply_monthly_fee()
        premium = calculate_value() >= 20000.00
        if premium:
            spread = 0.002
        else:
            spread = 0.004

    # Final value after day 60
    return calculate_value()

# Example usage
if __name__ == "__main__":
    print(run())
