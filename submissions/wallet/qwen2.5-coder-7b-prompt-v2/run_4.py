def run() -> float:
    PLN = 3000.00
    EUR = 1200.00
    USD = 500.00
    rates = {'EUR': 4.3150, 'USD': 3.9820}
    spread = 0.004
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
            if currency == 'PLN':
                PLN += amount
            elif currency == 'EUR':
                EUR += amount
            elif currency == 'USD':
                USD += amount
        elif event_type == 'PAY':
            if currency == 'PLN':
                PLN -= amount
            elif currency == 'EUR':
                if EUR >= amount:
                    EUR -= amount
                else:
                    shortfall = amount - EUR
                    cost = round(shortfall * rates['EUR'] * (1 + spread + 0.005), 2)
                    if currency == 'PLN' or PLN >= cost:
                        EUR = 0
                        PLN -= cost
                    else:
                        PLN -= 10.00
            elif currency == 'USD':
                if USD >= amount:
                    USD -= amount
                else:
                    shortfall = amount - USD
                    cost = round(shortfall * rates['USD'] * (1 + spread + 0.005), 2)
                    if currency == 'PLN' or PLN >= cost:
                        USD = 0
                        PLN -= cost
                    else:
                        PLN -= 10.00
        elif event_type == 'CONVERT':
            if currency == 'PLN':
                p = round(amount * rates['EUR'], 2)
                received = round(p / rates['EUR'] * (1 - spread), 2)
                EUR += received
                PLN -= amount
            elif currency == 'EUR':
                p = round(amount * rates['EUR'], 2)
                received = round(p / rates['EUR'] * (1 - spread), 2)
                EUR -= amount
                PLN += received
            elif currency == 'USD':
                p = round(amount * rates['USD'], 2)
                received = round(p / rates['USD'] * (1 - spread), 2)
                USD -= amount
                PLN += received
        elif event_type == 'RATE':
            if currency == 'EUR':
                rates['EUR'] = amount
            elif currency == 'USD':
                rates['USD'] = amount
        
        if day in [30, 60]:
            wallet_value = PLN + EUR * rates['EUR'] + USD * rates['USD']
            if wallet_value >= 20000.00:
                spread = 0.002
            else:
                spread = 0.004
                if wallet_value < 5000.00:
                    PLN -= 15.00
    
    wallet_value = PLN + EUR * rates['EUR'] + USD * rates['USD']
    return round(wallet_value, 2)
