def run() -> float:
    PLN = 3000.00
    EUR = 1200.00
    USD = 500.00
    EUR_RATE = 4.3150
    USD_RATE = 3.9820
    SPREAD = 0.004
    MIN_VALUE = 20000.00
    MONTHLY_FEE = 15.00
    DECLINE_FEE = 10.00

    def round_half_even(n):
        return round(n, 2)

    def round_half_away_from_zero(n):
        return round(n, 2)

    def get_value():
        value = PLN + EUR * EUR_RATE + USD * USD_RATE
        return round_half_away_from_zero(value)

    def update_rates(day, currency, rate):
        nonlocal EUR_RATE, USD_RATE
        if currency == "EUR":
            EUR_RATE = rate
        elif currency == "USD":
            USD_RATE = rate

    def convert(amount, currency, target_currency):
        nonlocal PLN, EUR, USD, EUR_RATE, USD_RATE
        if currency == target_currency:
            return

        if currency == "PLN":
            received = round_half_even(amount * (1 - SPREAD))
        elif target_currency == "PLN":
            p = round_half_even(amount * globals()[f"{currency}_RATE"])
            received = round_half_even(p / globals()[f"{target_currency}_RATE"] * (1 - SPREAD))
        else:
            p = round_half_even(amount * globals()[f"{currency}_RATE"])
            received = round_half_even(p / globals()[f"{target_currency}_RATE"] * (1 - 2 * SPREAD))

        if globals()[f"{currency}_balance"] < amount:
            return

        globals()[f"{currency}_balance"] -= amount
        globals()[f"{target_currency}_balance"] += received

    def pay(amount, currency):
        nonlocal PLN, EUR, USD, EUR_RATE, USD_RATE
        if currency == "PLN":
            if PLN >= amount:
                PLN -= amount
            else:
                shortfall = amount - PLN
                cost = round_half_even(shortfall * globals()[f"{currency}_RATE"] * (1 + SPREAD + 0.005))
                if PLN < cost:
                    PLN -= DECLINE_FEE
                else:
                    PLN = 0
                    PLN -= cost
        else:
            if globals()[f"{currency}_balance"] >= amount:
                globals()[f"{currency}_balance"] -= amount
            else:
                shortfall = amount - globals()[f"{currency}_balance"]
                cost = round_half_even(shortfall * globals()[f"{currency}_RATE"] * (1 + SPREAD + 0.005))
                if PLN < cost:
                    PLN -= DECLINE_FEE
                else:
                    globals()[f"{currency}_balance"] = 0
                    PLN -= cost

    events = [
        (1, "DEPOSIT", "PLN", None, 2500.00),
        (3, "PAY", "EUR", None, 150.00),
        (5, "CONVERT", "PLN", "EUR", 2000.00),
        (7, "RATE", "EUR", None, 4.3280),
        (8, "PAY", "USD", None, 620.00),
        (12, "DEPOSIT", "USD", None, 4000.00),
        (14, "CONVERT", "USD", "EUR", 1500.37),
        (15, "RATE", "USD", None, 3.9455),
        (18, "DEPOSIT", "PLN", None, 6000.00),
        (20, "CONVERT", "EUR", "PLN", 900.00),
        (22, "PAY", "PLN", None, 9000.00),
        (25, "RATE", "EUR", None, 4.2965),
        (28, "PAY", "EUR", None, 2400.00),
        (33, "CONVERT", "PLN", "USD", 1800.00),
        (36, "PAY", "USD", None, 5200.00),
        (40, "RATE", "USD", None, 4.0110),
        (41, "DEPOSIT", "EUR", None, 300.00),
        (43, "CONVERT", "EUR", "PLN", 50.00),
        (45, "PAY", "PLN", None, 1500.00),
        (48, "CONVERT", "USD", "PLN", 755.00),
        (52, "RATE", "EUR", None, 4.3402),
        (55, "PAY", "EUR", None, 700.00),
        (58, "PAY", "USD", None, 2000.00),
    ]

    for day, event_type, currency, target_currency, amount in events:
        if event_type == "RATE":
            update_rates(day, currency, amount)
        elif event_type == "DEPOSIT":
            globals()[f"{currency}_balance"] = globals().get(f"{currency}_balance", 0) + amount
        elif event_type == "CONVERT":
            convert(amount, currency, target_currency)
        elif event_type == "PAY":
            pay(amount, currency)

    if get_value() < MIN_VALUE:
        PLN -= MONTHLY_FEE

    return get_value()
