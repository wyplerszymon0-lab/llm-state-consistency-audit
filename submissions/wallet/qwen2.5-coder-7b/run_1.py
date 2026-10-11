def run() -> float:
    from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

    PLN = 3000.00
    EUR = 1200.00
    USD = 500.00
    EUR_RATE = Decimal('4.3150')
    USD_RATE = Decimal('3.9820')
    SPREAD_PREMIUM = Decimal('0.002')
    SPREAD_NON_PREMIUM = Decimal('0.004')
    DECLINE_FEE = Decimal('10.00')
    MONTHLY_FEE = Decimal('15.00')

    def convert(amount, from_currency, to_currency, rate, spread):
        p = amount * rate
        p = p.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
        received = (p / rate / (1 - spread)).quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
        return received

    def pay(amount, currency, rate, spread):
        if balance[currency] >= amount:
            balance[currency] -= amount
        else:
            shortfall = amount - balance[currency]
            cost = shortfall * rate * (1 + spread + Decimal('0.005'))
            cost = cost.quantize(Decimal('0.00'), rounding=ROUND_HALF_EVEN)
            if currency == 'PLN' or balance['PLN'] < cost:
                balance['PLN'] -= DECLINE_FEE
            else:
                balance['PLN'] -= cost
                balance[currency] = 0

    def update_wallet_value():
        nonlocal wallet_value
        wallet_value = balance['PLN'] + \
                      (balance['EUR'] * EUR_RATE).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP) + \
                      (balance['USD'] * USD_RATE).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    balance = {'PLN': Decimal(PLN), 'EUR': Decimal(EUR), 'USD': Decimal(USD)}
    wallet_value = update_wallet_value()

    events = [
        (1, 'DEPOSIT', 'PLN', None, Decimal('2500.00')),
        (3, 'PAY', 'EUR', None, Decimal('150.00')),
        (5, 'CONVERT', 'PLN', 'EUR', Decimal('2000.00')),
        (7, 'RATE', 'EUR', None, Decimal('4.3280')),
        (8, 'PAY', 'USD', None, Decimal('620.00')),
        (12, 'DEPOSIT', 'USD', None, Decimal('4000.00')),
        (14, 'CONVERT', 'USD', 'EUR', Decimal('1500.37')),
        (15, 'RATE', 'USD', None, Decimal('3.9455')),
        (18, 'DEPOSIT', 'PLN', None, Decimal('6000.00')),
        (20, 'CONVERT', 'EUR', 'PLN', Decimal('900.00')),
        (22, 'PAY', 'PLN', None, Decimal('9000.00')),
        (25, 'RATE', 'EUR', None, Decimal('4.2965')),
        (28, 'PAY', 'EUR', None, Decimal('2400.00')),
        (33, 'CONVERT', 'PLN', 'USD', Decimal('1800.00')),
        (36, 'PAY', 'USD', None, Decimal('5200.00')),
        (40, 'RATE', 'USD', None, Decimal('4.0110')),
        (41, 'DEPOSIT', 'EUR', None, Decimal('300.00')),
        (43, 'CONVERT', 'EUR', 'PLN', Decimal('50.00')),
        (45, 'PAY', 'PLN', None, Decimal('1500.00')),
        (48, 'CONVERT', 'USD', 'PLN', Decimal('755.00')),
        (52, 'RATE', 'EUR', None, Decimal('4.3402')),
        (55, 'PAY', 'EUR', None, Decimal('700.00')),
        (58, 'PAY', 'USD', None, Decimal('2000.00'))
    ]

    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            balance[currency] += amount
        elif event_type == 'RATE':
            if currency == 'EUR':
                EUR_RATE = amount
            elif currency == 'USD':
                USD_RATE = amount
        elif event_type == 'CONVERT':
            if balance[currency] >= amount:
                spread = SPREAD_PREMIUM if wallet_value >= Decimal('20000.00') else SPREAD_NON_PREMIUM
                received = convert(amount, currency, target_currency, EUR_RATE if currency == 'EUR' else USD_RATE, spread)
                balance[currency] -= amount
                balance[target_currency] += received
        elif event_type == 'PAY':
            if currency == 'EUR':
                spread = SPREAD_PREMIUM if wallet_value >= Decimal('20000.00') else SPREAD_NON_PREMIUM
                cost = convert(amount, currency, 'PLN', EUR_RATE, spread)
                pay(amount, currency, EUR_RATE, spread)
            elif currency == 'USD':
                spread = SPREAD_PREMIUM if wallet_value >= Decimal('20000.00') else SPREAD_NON_PREMIUM
                cost = convert(amount, currency, 'PLN', USD_RATE, spread)
                pay(amount, currency, USD_RATE, spread)

        if day == 30 or day == 60:
            update_wallet_value()
            if wallet_value < Decimal('5000.00'):
                balance['PLN'] -= MONTHLY_FEE

    update_wallet_value()
    return wallet_value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

print(run())
