<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:28:17+00:00 -->

```python
import math
from collections import deque
from typing import Deque, Dict, Tuple

def run() -> float:
    # Transactions data
    txns = [
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

    # State variables
    cash: float = 0.0
    last_sale_was_profitable: bool = False
    portfolios: Dict[int, Deque[Tuple[int, float]]] = {}  # lot: (qty, unit_cost)

    def apply_drift() -> None:
        """Multiply unit cost of all lots by 1.001 and round to 4 decimals."""
        for lot_queue in portfolios.values():
            for i, (qty, cost) in enumerate(lot_queue):
                new_cost = round(cost * 1.001, 4)
                lot_queue[i] = (qty, new_cost)

    def compute_wealth() -> float:
        """Compute cash + sum of (qty * unit_cost) over all remaining lots."""
        total = cash
        for lot_queue in portfolios.values():
            for qty, cost in lot_queue:
                total += qty * cost
        return total

    for _id, port_id, t_type, qty, unit_price in txns:
        if port_id not in portfolios:
            portfolios[port_id] = deque()
        lot_queue = portfolios[port_id]

        if t_type == "BUY":
            # Determine unit cost
            cost = unit_price
            if last_sale_was_profitable:
                cost = unit_price * 1.01
            # Append new lot
            lot_queue.append((qty, cost))

        elif t_type == "SELL":
            remaining = qty
            cost_basis = 0.0
            # Remove FIFO lots
            while remaining > 0 and lot_queue:
                lot_qty, lot_cost = lot_queue[0]
                if lot_qty <= remaining:
                    # Take whole lot
                    cost_basis += lot_qty * lot_cost
                    remaining -= lot_qty
                    lot_queue.popleft()
                else:
                    # Split lot
                    cost_basis += remaining * lot_cost
                    lot_queue[0] = (lot_qty - remaining, lot_cost)
                    remaining = 0

            revenue = qty * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            # Wealth check before adding revenue to cash
            wealth_before = compute_wealth()
            penalty = 0.02 if wealth_before > 10000 else 0.0

            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0.0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

        # Apply drift after every transaction
        apply_drift()

    # Final result
    final = cash + compute_wealth() - cash  # compute_wealth already includes cash
    # compute_wealth includes cash; we just need cash + holdings; it's same as compute_wealth
    final = compute_wealth()
    return round(final, 2)

if __name__ == "__main__":
    print(run())
```