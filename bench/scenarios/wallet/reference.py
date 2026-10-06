"""Reference solver for the multi-currency wallet scenario. See prompt.md for the rules."""

from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

D = Decimal

OPENING = {"PLN": D("3000.00"), "EUR": D("1200.00"), "USD": D("500.00")}
OPENING_RATES = {"PLN": D("1"), "EUR": D("4.3150"), "USD": D("3.9820")}  # PLN per unit
LAST_DAY = 60

SPREAD = D("0.004")
PREMIUM_SPREAD = D("0.002")
PREMIUM_THRESHOLD = D("20000")
CARD_SURCHARGE = D("0.005")
DECLINE_FEE = D("10.00")
MONTHLY_FEE = D("15.00")
MONTHLY_FEE_THRESHOLD = D("5000")
FEE_DAYS = (30, 60)
CONVERSION_ROUNDING = ROUND_HALF_EVEN
APPLY_RATE_UPDATES = True

EVENTS = [
    (1, "DEPOSIT", "PLN", None, "2500.00"),
    (3, "PAY", "EUR", None, "150.00"),
    (5, "CONVERT", "PLN", "EUR", "2000.00"),
    (7, "RATE", "EUR", None, "4.3280"),
    (8, "PAY", "USD", None, "620.00"),
    (12, "DEPOSIT", "USD", None, "4000.00"),
    (14, "CONVERT", "USD", "EUR", "1500.37"),
    (15, "RATE", "USD", None, "3.9455"),
    (18, "DEPOSIT", "PLN", None, "6000.00"),
    (20, "CONVERT", "EUR", "PLN", "900.00"),
    (22, "PAY", "PLN", None, "9000.00"),
    (25, "RATE", "EUR", None, "4.2965"),
    (28, "PAY", "EUR", None, "2400.00"),
    (33, "CONVERT", "PLN", "USD", "1800.00"),
    (36, "PAY", "USD", None, "5200.00"),
    (40, "RATE", "USD", None, "4.0110"),
    (41, "DEPOSIT", "EUR", None, "300.00"),
    (43, "CONVERT", "EUR", "PLN", "50.00"),
    (45, "PAY", "PLN", None, "1500.00"),
    (48, "CONVERT", "USD", "PLN", "755.00"),
    (52, "RATE", "EUR", None, "4.3402"),
    (55, "PAY", "EUR", None, "700.00"),
    (58, "PAY", "USD", None, "2000.00"),
]

# Each rule, switched off. Used by the tests (every rule must change the answer)
# and by the report, which checks whether a wrong answer equals one of these.
RULES = {
    "conversion spread": {"SPREAD": D(0), "PREMIUM_SPREAD": D(0)},
    "premium spread": {"PREMIUM_SPREAD": SPREAD},
    "card auto-conversion surcharge": {"CARD_SURCHARGE": D(0)},
    "decline fee": {"DECLINE_FEE": D(0)},
    "monthly fee": {"MONTHLY_FEE": D(0)},
    "rate updates": {"APPLY_RATE_UPDATES": False},
    "half-even rounding of conversions": {"CONVERSION_ROUNDING": ROUND_HALF_UP},
}

CENT = D("0.01")


def run() -> float:
    balance = dict(OPENING)
    rate = dict(OPENING_RATES)

    def conv_round(x: Decimal) -> Decimal:
        return x.quantize(CENT, rounding=CONVERSION_ROUNDING)

    def value() -> Decimal:
        """Wallet value in PLN: each foreign balance at the current rate, rounded half up."""
        return balance["PLN"] + sum(
            (balance[c] * rate[c]).quantize(CENT, rounding=ROUND_HALF_UP) for c in ("EUR", "USD")
        )

    premium = value() >= PREMIUM_THRESHOLD

    def spread() -> Decimal:
        return PREMIUM_SPREAD if premium else SPREAD

    def convert(src: str, dst: str, amount: Decimal) -> None:
        pln = conv_round(amount * rate[src])  # every conversion goes through PLN
        received = conv_round(pln / rate[dst] * (1 - spread()))
        balance[src] -= amount
        balance[dst] += received

    def pay(currency: str, amount: Decimal) -> None:
        if balance[currency] >= amount:
            balance[currency] -= amount
            return
        shortfall = amount - balance[currency]
        cost = conv_round(shortfall * rate[currency] * (1 + spread() + CARD_SURCHARGE))
        if currency == "PLN" or balance["PLN"] < cost:
            balance["PLN"] -= DECLINE_FEE  # declined: nothing is paid
            return
        balance[currency] = D(0)
        balance["PLN"] -= cost

    for day in range(1, LAST_DAY + 1):
        for ev_day, kind, cur, target, amount in EVENTS:
            if ev_day != day:
                continue
            amount = D(amount)
            if kind == "DEPOSIT":
                balance[cur] += amount
            elif kind == "RATE":
                if APPLY_RATE_UPDATES:
                    rate[cur] = amount
            elif kind == "CONVERT":
                if balance[cur] >= amount:
                    convert(cur, target, amount)
            else:
                pay(cur, amount)

        if day in FEE_DAYS and value() < MONTHLY_FEE_THRESHOLD:
            balance["PLN"] -= MONTHLY_FEE
        premium = value() >= PREMIUM_THRESHOLD

    return float(value().quantize(CENT, rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    print(run())
