def run() -> float:
    PLN = 3000.00
    EUR = 1200.00
    USD = 500.00
    EUR_RATE = 4.3150
    USD_RATE = 3.9820
    PREMIUM_THRESHOLD = 20000.00
    MONTHLY_FEE = 15.00
    DECLINE_FEE = 10.00
    PREMIUM_SPREAD = 0.002
    NON_PREMIUM_SPREAD = 0.004

    def get_value():
        nonlocal PLN, EUR, USD, EUR_RATE, USD_RATE
        EUR_value = round(EUR * EUR_RATE, 2)
        USD_value = round(USD * USD_RATE, 2)
        return round(PLN + EUR_value + USD_value, 2)

    def pay(amount, currency):
        nonlocal PLN, EUR, USD
        if currency == 'PLN':
            if PLN >= amount:
                PLN -= amount
            else:
                shortfall = amount - PLN
                cost = round(shortfall * get_rate(currency) * (1 + NON_PREMIUM_SPREAD + 0.005), 2)
                if PLN < cost or (currency == 'PLN' and PLN < cost):
                    PLN -= DECLINE_FEE
                else:
                    PLN = 0
        else:
            rate = get_rate(currency)
            if rate == 0:
                return
            p = round(amount * rate, 2)
            received = round(p / get_rate(target_currency) * (1 - spread), 2)
            if currency_balance >= amount:
                currency_balance -= amount
                target_currency_balance += received
            else:
                shortfall = amount - currency_balance
                cost = round(shortfall * get_rate(currency) * (1 + spread + 0.005), 2)
                if currency_balance < cost:
                    PLN -= DECLINE_FEE
                else:
                    currency_balance = 0
                    PLN -= cost

    def convert(amount, currency, target_currency):
        nonlocal PLN, EUR, USD
        rate = get_rate(currency)
        if rate == 0:
            return
        p = round(amount * rate, 2)
        spread = PREMIUM_SPREAD if get_value() >= PREMIUM_THRESHOLD else NON_PREMIUM_SPREAD
        received = round(p / get_rate(target_currency) * (1 - spread), 2)
        if currency_balance >= amount:
            currency_balance -= amount
            target_currency_balance += received
        else:
            shortfall = amount - currency_balance
            cost = round(shortfall * get_rate(currency) * (1 + spread + 0.005), 2)
            if currency_balance < cost:
                PLN -= DECLINE_FEE
            else:
                currency_balance = 0
                PLN -= cost

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
        (58, 'PAY', 'USD', None, 2000.00)
    ]

    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            if currency == 'PLN':
                PLN += amount
            elif currency == 'EUR':
                EUR += amount
            elif currency == 'USD':
                USD += amount
        elif event_type == 'RATE':
            if currency == 'EUR':
                EUR_RATE = amount
            elif currency == 'USD':
                USD_RATE = amount
        elif event_type == 'CONVERT':
            convert(amount, currency, target_currency)
        elif event_type == 'PAY':
            pay(amount, currency)

    if day == 60 and get_value() < PREMIUM_THRESHOLD:
        PLN -= MONTHLY_FEE

    return round(get_value(), 2)

print(run())
