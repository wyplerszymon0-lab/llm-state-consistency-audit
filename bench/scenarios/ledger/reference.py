"""Reference solver for the ledger scenario. See prompt.md for the rules."""

from decimal import ROUND_HALF_UP, Decimal

D = Decimal

OPENING = {"X": D("4200.00"), "Y": D("800.00"), "Z": D("12000.00")}
LAST_DAY = 60
PERIOD = 30

OVERDRAFT_LIMIT = D("-500")
OVERDRAFT_FEE = D("25.00")
REJECTION_FEE = D("15.00")
TRANSFER_FEE = D("1.00")
TRANSFER_FEE_THRESHOLD = D("1000")
TIER_LIMIT = D("5000")
RATE_LOW = D("0.02")
RATE_HIGH = D("0.035")
RATE_OVERDRAFT = D("0.18")
MAINTENANCE_FEE = D("5.00")
WAIVER_MIN_BALANCE = D("1000")

EVENTS = [
    (1, "DEPOSIT", "Y", None, "300.00"),
    (3, "WITHDRAW", "Y", None, "1500.00"),
    (5, "TRANSFER", "Z", "X", "2500.00"),
    (8, "WITHDRAW", "Y", None, "200.00"),
    (10, "DEPOSIT", "Y", None, "2000.00"),
    (12, "TRANSFER", "X", "Y", "800.00"),
    (15, "WITHDRAW", "Z", None, "8000.00"),
    (20, "WITHDRAW", "Z", None, "700.00"),
    (25, "TRANSFER", "Y", "Z", "1200.00"),
    (33, "WITHDRAW", "X", None, "6300.00"),
    (36, "DEPOSIT", "X", None, "1000.00"),
    (40, "TRANSFER", "Z", "Y", "2100.00"),
    (45, "WITHDRAW", "Y", None, "5000.00"),
    (47, "DEPOSIT", "Z", None, "3000.00"),
    (50, "TRANSFER", "Y", "X", "1000.00"),
    (55, "WITHDRAW", "X", None, "300.00"),
    (58, "DEPOSIT", "Y", None, "150.00"),
]


def _daily_interest(balance: Decimal) -> Decimal:
    if balance > 0:
        low = min(balance, TIER_LIMIT)
        high = max(balance - TIER_LIMIT, D(0))
        return low * RATE_LOW / 365 + high * RATE_HIGH / 365
    return balance * RATE_OVERDRAFT / 365


def run() -> float:
    balance = dict(OPENING)
    accrued = {a: D(0) for a in balance}
    period_min = {a: None for a in balance}

    def debit(account, amount):
        """Withdraw `amount` (fees included) or reject it. Returns True if applied."""
        before = balance[account]
        if before - amount < OVERDRAFT_LIMIT:
            balance[account] -= REJECTION_FEE
            return False
        balance[account] -= amount
        if before >= 0 and balance[account] < 0:
            balance[account] -= OVERDRAFT_FEE
        return True

    for day in range(1, LAST_DAY + 1):
        for ev_day, kind, account, target, amount in EVENTS:
            if ev_day != day:
                continue
            amount = D(amount)
            if kind == "DEPOSIT":
                balance[account] += amount
            elif kind == "WITHDRAW":
                debit(account, amount)
            else:
                fee = TRANSFER_FEE if amount > TRANSFER_FEE_THRESHOLD else D(0)
                if debit(account, amount + fee):
                    balance[target] += amount

        for a in balance:
            if period_min[a] is None or balance[a] < period_min[a]:
                period_min[a] = balance[a]
            accrued[a] += _daily_interest(balance[a])

        if day % PERIOD == 0:
            for a in balance:
                balance[a] += accrued[a].quantize(D("0.01"), rounding=ROUND_HALF_UP)
                accrued[a] = D(0)
                if period_min[a] < WAIVER_MIN_BALANCE:
                    balance[a] -= MAINTENANCE_FEE
                period_min[a] = None

    return float(sum(balance.values()).quantize(D("0.01"), rounding=ROUND_HALF_UP))


if __name__ == "__main__":
    print(run())
