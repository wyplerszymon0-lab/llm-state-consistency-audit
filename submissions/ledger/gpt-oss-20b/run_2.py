from decimal import Decimal, getcontext, ROUND_HALF_UP

def run() -> float:
    # Set high precision for intermediate calculations
    getcontext().prec = 28

    # Opening balances
    balances = {
        "X": Decimal("4200.00"),
        "Y": Decimal("800.00"),
        "Z": Decimal("12000.00"),
    }

    # Accrued interest per account
    accrued = {"X": Decimal("0"), "Y": Decimal("0"), "Z": Decimal("0")}

    # Minimum end‑of‑day balance for each 30‑day period (0: days 1‑30, 1: days 31‑60)
    min_balance = [None, None]

    # Events list (day, type, source, target, amount)
    raw_events = [
        (1, "DEPOSIT", "Y", None, Decimal("300.00")),
        (3, "WITHDRAW", "Y", None, Decimal("1500.00")),
        (5, "TRANSFER", "Z", "X", Decimal("2500.00")),
        (8, "WITHDRAW", "Y", None, Decimal("200.00")),
        (10, "DEPOSIT", "Y", None, Decimal("2000.00")),
        (12, "TRANSFER", "X", "Y", Decimal("800.00")),
        (15, "WITHDRAW", "Z", None, Decimal("8000.00")),
        (20, "WITHDRAW", "Z", None, Decimal("700.00")),
        (25, "TRANSFER", "Y", "Z", Decimal("1200.00")),
        (33, "WITHDRAW", "X", None, Decimal("6300.00")),
        (36, "DEPOSIT", "X", None, Decimal("1000.00")),
        (40, "TRANSFER", "Z", "Y", Decimal("2100.00")),
        (45, "WITHDRAW", "Y", None, Decimal("5000.00")),
        (47, "DEPOSIT", "Z", None, Decimal("3000.00")),
        (50, "TRANSFER", "Y", "X", Decimal("1000.00")),
        (55, "WITHDRAW", "X", None, Decimal("300.00")),
        (58, "DEPOSIT", "Y", None, Decimal("150.00")),
    ]

    # Group events by day for quick lookup
    events_by_day = {}
    for ev in raw_events:
        events_by_day.setdefault(ev[0], []).append(ev[1:])  # store type, src, tgt, amt

    # Helper to apply a debit with overdraft/rejection rules
    def apply_debit(acc: str, total: Decimal) -> None:
        before = balances[acc]
        if before - total < Decimal("-500"):
            # Rejection fee
            balances[acc] = before - Decimal("15.00")
        else:
            balances[acc] = before - total
            # Overdraft fee
            if before >= 0 and balances[acc] < 0:
                balances[acc] -= Decimal("25.00")

    # Process each day
    for day in range(1, 61):
        period = 0 if day <= 30 else 1

        # Process events of the day
        for ev in events_by_day.get(day, []):
            typ, src, tgt, amt = ev
            if typ == "DEPOSIT":
                balances[src] += amt
            elif typ == "WITHDRAW":
                apply_debit(src, amt)
            elif typ == "TRANSFER":
                fee = Decimal("1.00") if amt > Decimal("1000") else Decimal("0.00")
                total = amt + fee
                before = balances[src]
                if before - total < Decimal("-500"):
                    # Rejection: only fee applied
                    balances[src] = before - Decimal("15.00")
                else:
                    balances[src] = before - total
                    if before >= 0 and balances[src] < 0:
                        balances[src] -= Decimal("25.00")
                    # Transfer money to target
                    balances[tgt] += amt

        # Record end‑of‑day balance for min tracking (after events, before interest)
        for acc in balances:
            bal = balances[acc]
            if min_balance[period] is None or bal < min_balance[period]:
                min_balance[period] = bal

        # Interest accrual
        for acc in balances:
            b = balances[acc]
            if b > 0:
                part1 = min(b, Decimal("5000")) * Decimal("0.02") / Decimal("365")
                part2 = max(b - Decimal("5000"), Decimal("0")) * Decimal("0.035") / Decimal("365")
                accrued[acc] += part1 + part2
            else:
                accrued[acc] += b * Decimal("0.18") / Decimal("365")

        # Period close on days 30 and 60
        if day in (30, 60):
            # Add rounded accrued interest
            for acc in balances:
                ci = accrued[acc].quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                balances[acc] += ci
                accrued[acc] = Decimal("0")
            # Maintenance fee if lowest balance < 1000
            if min_balance[period] is not None and min_balance[period] < Decimal("1000"):
                for acc in balances:
                    balances[acc] -= Decimal("5.00")
            # Reset min balance for next period
            min_balance[period] = None

    # Final sum of balances, rounded to 2 decimal places
    total = sum(balances.values())
    result = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(result)
