import decimal
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

# Use Decimal for accurate arithmetic
decimal.getcontext().prec = 28

# Rounding helpers
def round_bankers(x: Decimal) -> Decimal:
    """Round to 2 decimals using banker's rounding (half to even)."""
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_EVEN)

def round_away(x: Decimal) -> Decimal:
    """Round to 2 decimals using half away from zero (ROUND_HALF_UP)."""
    return x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

def compute_value(balances, rates):
    """Compute wallet value in PLN using current balances and rates."""
    eur_val = round_away(balances["EUR"] * rates["EUR"])
    usd_val = round_away(balances["USD"] * rates["USD"])
    return balances["PLN"] + eur_val + usd_val

def run() -> float:
    # Initial state
    balances = {"PLN": Decimal("3000.00"),
                "EUR": Decimal("1200.00"),
                "USD": Decimal("500.00")}

    rates = {"PLN": Decimal("1"),
             "EUR": Decimal("4.3150"),
             "USD": Decimal("3.9820")}

    # Event list: (day, type, currency, target_currency, amount)
    raw_events = [
        (1, "DEPOSIT", "PLN", None, Decimal("2500.00")),
        (3, "PAY", "EUR", None, Decimal("150.00")),
        (5, "CONVERT", "PLN", "EUR", Decimal("2000.00")),
        (7, "RATE", "EUR", None, Decimal("4.3280")),
        (8, "PAY", "USD", None, Decimal("620.00")),
        (12, "DEPOSIT", "USD", None, Decimal("4000.00")),
        (14, "CONVERT", "USD", "EUR", Decimal("1500.37")),
        (15, "RATE", "USD", None, Decimal("3.9455")),
        (18, "DEPOSIT", "PLN", None, Decimal("6000.00")),
        (20, "CONVERT", "EUR", "PLN", Decimal("900.00")),
        (22, "PAY", "PLN", None, Decimal("9000.00")),
        (25, "RATE", "EUR", None, Decimal("4.2965")),
        (28, "PAY", "EUR", None, Decimal("2400.00")),
        (33, "CONVERT", "PLN", "USD", Decimal("1800.00")),
        (36, "PAY", "USD", None, Decimal("5200.00")),
        (40, "RATE", "USD", None, Decimal("4.0110")),
        (41, "DEPOSIT", "EUR", None, Decimal("300.00")),
        (43, "CONVERT", "EUR", "PLN", Decimal("50.00")),
        (45, "PAY", "PLN", None, Decimal("1500.00")),
        (48, "CONVERT", "USD", "PLN", Decimal("755.00")),
        (52, "RATE", "EUR", None, Decimal("4.3402")),
        (55, "PAY", "EUR", None, Decimal("700.00")),
        (58, "PAY", "USD", None, Decimal("2000.00")),
    ]

    # Group events by day for quick access
    events_by_day = {}
    for ev in raw_events:
        events_by_day.setdefault(ev[0], []).append(ev)

    # Determine initial premium status
    premium = compute_value(balances, rates) >= Decimal("20000.00")

    # Iterate days 1..60
    for day in range(1, 61):
        # Spread based on premium status at start of day
        spread = Decimal("0.002") if premium else Decimal("0.004")

        # Process events of the day in order
        for ev in events_by_day.get(day, []):
            _, typ, cur, tgt, amt = ev

            if typ == "DEPOSIT":
                balances[cur] += amt

            elif typ == "RATE":
                rates[cur] = amt

            elif typ == "CONVERT":
                # Only if enough balance
                if balances[cur] >= amt:
                    # Step 1: convert to PLN
                    p = round_bankers(amt * rates[cur])
                    # Step 2: convert PLN to target currency with spread
                    received = round_bankers(p / rates[tgt] * (Decimal("1") - spread))
                    # Update balances
                    balances[cur] -= amt
                    balances[tgt] += received

            elif typ == "PAY":
                # If enough balance in that currency
                if balances[cur] >= amt:
                    balances[cur] -= amt
                else:
                    shortfall = amt - balances[cur]
                    # Cost in PLN to purchase shortfall of currency
                    cost = round_bankers(shortfall * rates[cur] * (Decimal("1") + spread + Decimal("0.005")))
                    if cur == "PLN" or balances["PLN"] < cost:
                        # Decline
                        balances["PLN"] -= Decimal("10.00")
                    else:
                        # Successful payment
                        balances[cur] = Decimal("0")
                        balances["PLN"] -= cost

        # Monthly fee check on days 30 and 60
        if day in (30, 60):
            # Value before fee
            val_before_fee = compute_value(balances, rates)
            if val_before_fee < Decimal("5000.00"):
                balances["PLN"] -= Decimal("15.00")

        # Recalculate premium status for next day
        val_end = compute_value(balances, rates)
        premium = val_end >= Decimal("20000.00")

    # Final wallet value after day 60 (including monthly fee)
    final_value = compute_value(balances, rates)
    # Return as float rounded to two decimals
    return float(round_away(final_value))

if __name__ == "__main__":
    print(run())
