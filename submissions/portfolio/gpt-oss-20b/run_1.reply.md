<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:21:07+00:00 -->

```python
#!/usr/bin/env python3
"""
Portfolio ledger simulation.
"""

from decimal import Decimal, getcontext, ROUND_HALF_EVEN
from collections import defaultdict, deque
from typing import List, Tuple

# Set a high precision for intermediate calculations
getcontext().prec = 28

# Data: (txn_id, portfolio_id, type, quantity, unit_price)
TRANSACTIONS: List[Tuple[int, int, str, int, int]] = [
    (1, 101, "BUY", 10, 100),
    (2, 102, "BUY", 20, 200),
    (3, 101, "BUY", 10, 110),
    (4, 101, "SELL", 15, 120),
    (5, 102, "SELL", 10, 210),
    (6, 101, "BUY", 20, 115),
    (7, 103, "BUY", 50, 50),
    (8, 101, "SELL", 10, 130),
    (9, 102, "BUY", 15, 205),
    (10, 103, "SELL", 20, 55),
    (11, 101, "BUY", 10, 120),
    (12, 101, "SELL", 15, 140),
    (13, 102, "SELL", 20, 215),
    (14, 103, "BUY", 10, 60),
    (15, 101, "SELL", 5, 145),
]

# Constants
DRIFT_FACTOR = Decimal("1.001")
ONE_HUNDRED = Decimal("10000")
PROFIT_PENALTY = Decimal("0.02")
BASE_RATE_HIGH = Decimal("0.15")
BASE_RATE_LOW = Decimal("0.05")
ONE_POINT_ONE = Decimal("1.01")
UNIT_ROUND = Decimal("0.0001")
TOTAL_ROUND = Decimal("0.01")


def _apply_drift(portfolios: defaultdict) -> None:
    """Apply holding cost drift to every lot in every portfolio."""
    for lot_queue in portfolios.values():
        for lot in lot_queue:
            # Multiply by drift factor
            lot[1] *= DRIFT_FACTOR
            # Round to 4 decimal places using round-half-even
            lot[1] = lot[1].quantize(UNIT_ROUND, rounding=ROUND_HALF_EVEN)


def _wealth(portfolios: defaultdict, cash: Decimal) -> Decimal:
    """Calculate wealth as cash plus value of all remaining lots."""
    total = cash
    for lot_queue in portfolios.values():
        for qty, cost in lot_queue:
            total += qty * cost
    return total


def run() -> float:
    """Simulate the portfolio ledger and return the final net worth."""
    # State
    cash = Decimal("0")
    last_sale_was_profitable = False
    portfolios: defaultdict[int, deque] = defaultdict(deque)

    for txn_id, pid, ttype, qty, price in TRANSACTIONS:
        qty = int(qty)
        price = Decimal(str(price))

        if ttype == "BUY":
            # Determine unit cost
            unit_cost = price if not last_sale_was_profitable else price * ONE_POINT_ONE
            # Store as [quantity, unit_cost]
            portfolios[pid].append([qty, unit_cost])

        elif ttype == "SELL":
            remaining = qty
            cost_basis = Decimal("0")

            # Remove units FIFO
            lot_queue = portfolios[pid]
            while remaining > 0 and lot_queue:
                lot_qty, lot_cost = lot_queue[0]
                if lot_qty <= remaining:
                    # Consume entire lot
                    cost_basis += lot_qty * lot_cost
                    remaining -= lot_qty
                    lot_queue.popleft()
                else:
                    # Split the lot
                    cost_basis += remaining * lot_cost
                    lot_queue[0][0] -= remaining
                    remaining = 0

            # At this point, remaining should be zero
            revenue = qty * price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            # Wealth check before adding revenue
            current_wealth = _wealth(portfolios, cash)
            penalty = PROFIT_PENALTY if current_wealth > ONE_HUNDRED else Decimal("0")

            base_rate = BASE_RATE_HIGH if gross_profit > Decimal("200") else BASE_RATE_LOW
            tax = max(Decimal("0"), gross_profit * (base_rate + penalty))

            cash += revenue - tax

        # Apply holding cost drift after each transaction
        _apply_drift(portfolios)

    # Final net worth
    total_value = cash + sum(q * c for q, c in (lot for queue in portfolios.values() for lot in queue))
    total_value = total_value.quantize(TOTAL_ROUND, rounding=ROUND_HALF_EVEN)
    return float(total_value)


# The module can be imported; run() returns the answer.
if __name__ == "__main__":
    print(run())
```