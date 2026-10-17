import decimal
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from typing import List, Dict

# Set up Decimal precision
decimal.getcontext().prec = 28

# Event types
DEPOSIT = "DEPOSIT"
WITHDRAW = "WITHDRAW"
TRANSFER = "TRANSFER"

@dataclass
class Account:
    balance: Decimal
    accrued_interest: Decimal = Decimal("0")
    period_min: Decimal = Decimal("Infinity")  # Will be updated on first day


def debit(acc: Account, total: Decimal) -> bool:
    """
    Attempt to debit `total` from `acc`.
    Returns True if debit applied, False if rejected.
    """
    before = acc.balance
    # Rejection rule
    if before - total < Decimal("-500"):
        acc.balance -= Decimal("15.00")  # rejection fee
        return False
    # Apply debit
    acc.balance -= total
    # Overdraft fee rule
    if before >= Decimal("0") and acc.balance < Decimal("0"):
        acc.balance -= Decimal("25.00")
    return True


def deposit(acc: Account, amount: Decimal) -> None:
    acc.balance += amount


def transfer(src: Account, tgt: Account, amount: Decimal) -> None:
    fee = Decimal("1.00") if amount > Decimal("1000") else Decimal("0.00")
    total = amount + fee
    if debit(src, total):
        tgt.balance += amount


def accrue_interest(acc: Account) -> None:
    b = acc.balance
    if b > Decimal("0"):
        part1 = min(b, Decimal("5000")) * Decimal("0.02") / Decimal("365")
        part2 = Decimal("0")
        if b > Decimal("5000"):
            part2 = (b - Decimal("5000")) * Decimal("0.035") / Decimal("365")
        interest = part1 + part2
    else:
        interest = b * Decimal("0.18") / Decimal("365")
    acc.accrued_interest += interest


def close_period(acc: Account) -> None:
    # Round accrued interest half away from zero to 2 decimals
    accrued = acc.accrued_interest.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    acc.balance += accrued
    acc.accrued_interest = Decimal("0")
    # Maintenance fee
    if acc.period_min < Decimal("1000"):
        acc.balance -= Decimal("5.00")
    # Reset period min to current balance for next period
    acc.period_min = acc.balance


def run() -> float:
    # Initial balances
    X = Account(balance=Decimal("4200.00"))
    Y = Account(balance=Decimal("800.00"))
    Z = Account(balance=Decimal("12000.00"))

    # Event list
    raw_events: List[str] = [
        "1, DEPOSIT, Y, -, 300.00",
        "3, WITHDRAW, Y, -, 1500.00",
        "5, TRANSFER, Z, X, 2500.00",
        "8, WITHDRAW, Y, -, 200.00",
        "10, DEPOSIT, Y, -, 2000.00",
        "12, TRANSFER, X, Y, 800.00",
        "15, WITHDRAW, Z, -, 8000.00",
        "20, WITHDRAW, Z, -, 700.00",
        "25, TRANSFER, Y, Z, 1200.00",
        "33, WITHDRAW, X, -, 6300.00",
        "36, DEPOSIT, X, -, 1000.00",
        "40, TRANSFER, Z, Y, 2100.00",
        "45, WITHDRAW, Y, -, 5000.00",
        "47, DEPOSIT, Z, -, 3000.00",
        "50, TRANSFER, Y, X, 1000.00",
        "55, WITHDRAW, X, -, 300.00",
        "58, DEPOSIT, Y, -, 150.00",
    ]

    # Parse events into day->list mapping
    events_by_day: Dict[int, List[tuple]] = {}
    for line in raw_events:
        day_str, typ, src, tgt, amt_str = [x.strip() for x in line.split(",")]
        day = int(day_str)
        amt = Decimal(amt_str)
        events_by_day.setdefault(day, []).append((typ, src, tgt, amt))

    # Simulation over days 1..60
    for day in range(1, 61):
        # Process events for the day in listed order
        if day in events_by_day:
            for typ, src, tgt, amt in events_by_day[day]:
                if typ == DEPOSIT:
                    if src == "X":
                        deposit(X, amt)
                    elif src == "Y":
                        deposit(Y, amt)
                    elif src == "Z":
                        deposit(Z, amt)
                elif typ == WITHDRAW:
                    if src == "X":
                        debit(X, amt)
                    elif src == "Y":
                        debit(Y, amt)
                    elif src == "Z":
                        debit(Z, amt)
                elif typ == TRANSFER:
                    if src == "X":
                        if tgt == "Y":
                            transfer(X, Y, amt)
                        elif tgt == "Z":
                            transfer(X, Z, amt)
                    elif src == "Y":
                        if tgt == "X":
                            transfer(Y, X, amt)
                        elif tgt == "Z":
                            transfer(Y, Z, amt)
                    elif src == "Z":
                        if tgt == "X":
                            transfer(Z, X, amt)
                        elif tgt == "Y":
                            transfer(Z, Y, amt)
        # End-of-day processing for each account
        for acc in (X, Y, Z):
            # Record minimum end-of-day balance for the period
            if acc.balance < acc.period_min:
                acc.period_min = acc.balance
            # Accrue interest
            accrue_interest(acc)
            # Period close on day 30 and 60
            if day in (30, 60):
                close_period(acc)

    # Final answer: sum of balances after day 60 close, rounded to 2 decimals
    total = X.balance + Y.balance + Z.balance
    total = total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return float(total)
