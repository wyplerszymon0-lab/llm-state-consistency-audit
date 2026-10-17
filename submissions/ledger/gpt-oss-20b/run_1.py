#!/usr/bin/env python3
"""
Simulation of a bank ledger with deposits, withdrawals, transfers,
interest accrual, and maintenance fees.
"""

from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import List, Tuple, Dict

# Set decimal precision high enough for intermediate calculations
getcontext().prec = 28


# ---------- Event list ----------
# Each event: (day, type, source, target, amount)
EVENTS: List[Tuple[int, str, str, str, Decimal]] = [
    (1,  "DEPOSIT",   "Y",   "-",    Decimal("300.00")),
    (3,  "WITHDRAW",  "Y",   "-",    Decimal("1500.00")),
    (5,  "TRANSFER",  "Z",   "X",    Decimal("2500.00")),
    (8,  "WITHDRAW",  "Y",   "-",    Decimal("200.00")),
    (10, "DEPOSIT",   "Y",   "-",    Decimal("2000.00")),
    (12, "TRANSFER",  "X",   "Y",    Decimal("800.00")),
    (15, "WITHDRAW",  "Z",   "-",    Decimal("8000.00")),
    (20, "WITHDRAW",  "Z",   "-",    Decimal("700.00")),
    (25, "TRANSFER",  "Y",   "Z",    Decimal("1200.00")),
    (33, "WITHDRAW",  "X",   "-",    Decimal("6300.00")),
    (36, "DEPOSIT",   "X",   "-",    Decimal("1000.00")),
    (40, "TRANSFER",  "Z",   "Y",    Decimal("2100.00")),
    (45, "WITHDRAW",  "Y",   "-",    Decimal("5000.00")),
    (47, "DEPOSIT",   "Z",   "-",    Decimal("3000.00")),
    (50, "TRANSFER",  "Y",   "X",    Decimal("1000.00")),
    (55, "WITHDRAW",  "X",   "-",    Decimal("300.00")),
    (58, "DEPOSIT",   "Y",   "-",    Decimal("150.00")),
]


def apply_debit(account: Dict[str, Decimal], total: Decimal) -> bool:
    """
    Attempt to debit `total` from `account['balance']`.
    Returns True if the debit was applied, False if rejected.
    """
    before = account["balance"]
    # Rejection check
    if before - total < Decimal("-500"):
        account["balance"] = before - Decimal("15")
        return False
    # Successful debit
    after = before - total
    if before >= 0 and after < 0:
        after -= Decimal("25")
    account["balance"] = after
    return True


def run() -> float:
    """Simulate the ledger and return the final total balance rounded to 2 decimals."""
    # Accounts initialization
    accounts: Dict[str, Dict[str, Decimal]] = {
        "X": {"balance": Decimal("4200.00"), "accrued_interest": Decimal("0"),
              "min_balance": Decimal("Infinity")},
        "Y": {"balance": Decimal("800.00"),  "accrued_interest": Decimal("0"),
              "min_balance": Decimal("Infinity")},
        "Z": {"balance": Decimal("12000.00"),"accrued_interest": Decimal("0"),
              "min_balance": Decimal("Infinity")},
    }

    # Sort events by day to ensure correct order
    events = sorted(EVENTS, key=lambda e: e[0])
    event_idx = 0
    total_days = 60

    for day in range(1, total_days + 1):
        # ----- Process all events for this day -----
        while event_idx < len(events) and events[event_idx][0] == day:
            _, typ, src, tgt, amt = events[event_idx]
            if typ == "DEPOSIT":
                accounts[src]["balance"] += amt
            elif typ == "WITHDRAW":
                apply_debit(accounts[src], amt)
            elif typ == "TRANSFER":
                fee = Decimal("1.00") if amt > Decimal("1000") else Decimal("0")
                total = amt + fee
                if apply_debit(accounts[src], total):
                    accounts[tgt]["balance"] += amt
            event_idx += 1

        # ----- Interest accrual -----
        for acc in accounts.values():
            b = acc["balance"]
            if b > 0:
                part1 = min(b, Decimal("5000")) * Decimal("0.02") / Decimal("365")
                part2 = max(b - Decimal("5000"), Decimal("0")) * Decimal("0.035") / Decimal("365")
                interest = part1 + part2
            else:
                interest = b * Decimal("0.18") / Decimal("365")
            acc["accrued_interest"] += interest

        # ----- End-of-day balance recording for min balance tracking -----
        for acc in accounts.values():
            if acc["balance"] < acc["min_balance"]:
                acc["min_balance"] = acc["balance"]

        # ----- Period close on day 30 and 60 -----
        if day in (30, 60):
            for acc in accounts.values():
                # Round accrued interest to 2 decimals (half away from zero)
                interest_rounded = acc["accrued_interest"].quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                acc["balance"] += interest_rounded
                acc["accrued_interest"] = Decimal("0")

                # Maintenance fee if lowest balance < 1000 during this period
                if acc["min_balance"] < Decimal("1000"):
                    acc["balance"] -= Decimal("5.00")

                # Reset min balance for next period
                acc["min_balance"] = Decimal("Infinity")

    # Sum final balances and round to 2 decimals
    total = sum(acc["balance"] for acc in accounts.values())
    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(total)


if __name__ == "__main__":
    print(run())
