"""Reference solver for the portfolio scenario. See prompt.md for the rules."""

BUY = "BUY"
SELL = "SELL"

TRANSACTIONS = [
    (1, 101, BUY, 10, 100),
    (2, 102, BUY, 20, 200),
    (3, 101, BUY, 10, 110),
    (4, 101, SELL, 15, 120),
    (5, 102, SELL, 10, 210),
    (6, 101, BUY, 20, 115),
    (7, 103, BUY, 50, 50),
    (8, 101, SELL, 10, 130),
    (9, 102, BUY, 15, 205),
    (10, 103, SELL, 20, 55),
    (11, 101, BUY, 10, 120),
    (12, 101, SELL, 15, 140),
    (13, 102, SELL, 20, 215),
    (14, 103, BUY, 10, 60),
    (15, 101, SELL, 5, 145),
]

PRICE_MODIFIER = 1.01
WEALTH_TAX_THRESHOLD = 10_000
WEALTH_TAX_RATE = 0.02
HIGH_PROFIT_THRESHOLD = 200
HIGH_PROFIT_TAX_RATE = 0.15
LOW_PROFIT_TAX_RATE = 0.05
DRIFT_RATE = 1.001


def _holdings_value(portfolios):
    return sum(qty * cost for lots in portfolios.values() for qty, cost in lots)


def run() -> float:
    portfolios = {}  # portfolio_id -> FIFO list of [qty, unit_cost]
    cash = 0.0
    last_sale_was_profitable = False

    for _txn_id, pid, kind, qty, price in TRANSACTIONS:
        lots = portfolios.setdefault(pid, [])

        if kind == BUY:
            cost = price * PRICE_MODIFIER if last_sale_was_profitable else price
            lots.append([qty, cost])
        else:
            remaining = qty
            cost_basis = 0.0
            while remaining > 0:
                lot = lots[0]
                take = min(lot[0], remaining)
                cost_basis += take * lot[1]
                lot[0] -= take
                remaining -= take
                if lot[0] == 0:
                    lots.pop(0)

            revenue = qty * price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            wealth = cash + _holdings_value(portfolios)
            penalty = WEALTH_TAX_RATE if wealth > WEALTH_TAX_THRESHOLD else 0.0
            base = HIGH_PROFIT_TAX_RATE if gross_profit > HIGH_PROFIT_THRESHOLD else LOW_PROFIT_TAX_RATE
            tax = max(0.0, gross_profit * (base + penalty))
            cash += revenue - tax

        for lots_ in portfolios.values():
            for lot in lots_:
                lot[1] = round(lot[1] * DRIFT_RATE, 4)

    return round(cash + _holdings_value(portfolios), 2)


if __name__ == "__main__":
    print(run())
