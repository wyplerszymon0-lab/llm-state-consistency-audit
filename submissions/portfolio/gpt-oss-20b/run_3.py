#!/usr/bin/env python3
"""
Simulation of a multi‑portfolio ledger with a shared cash account.
"""

from collections import deque
from typing import Deque, Tuple

# Transaction data: (txn_id, portfolio_id, type, quantity, unit_price)
TRANSACTIONS = [
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


def _drift_all(portfolios: dict[int, Deque[Tuple[int, float]]]) -> None:
    """Apply a 0.1% drift to every lot in every portfolio and round to 4 decimals."""
    for lots in portfolios.values():
        for i, (qty, cost) in enumerate(lots):
            new_cost = round(cost * 1.001, 4)
            lots[i] = (qty, new_cost)


def run() -> float:
    """Execute the simulation and return the final value."""
    # State
    cash: float = 0.0
    last_sale_was_profitable: bool = False
    portfolios: dict[int, Deque[Tuple[int, float]]] = {}

    for txn_id, pid, ttype, qty, unit_price in TRANSACTIONS:
        if pid not in portfolios:
            portfolios[pid] = deque()

        if ttype == "BUY":
            # Determine unit cost at purchase time
            unit_cost = unit_price * (1.01 if last_sale_was_profitable else 1.0)
            # Append lot
            portfolios[pid].append((qty, unit_cost))
            # Apply drift to all lots (including the new one)
            _drift_all(portfolios)

        else:  # SELL
            # Remove units FIFO
            qty_needed = qty
            cost_basis = 0.0
            while qty_needed > 0:
                lot_qty, lot_cost = portfolios[pid][0]
                if lot_qty <= qty_needed:
                    # Take entire lot
                    cost_basis += lot_qty * lot_cost
                    qty_needed -= lot_qty
                    portfolios[pid].popleft()
                else:
                    # Take part of the lot
                    cost_basis += qty_needed * lot_cost
                    new_qty = lot_qty - qty_needed
                    portfolios[pid][0] = (new_qty, lot_cost)
                    qty_needed = 0

            revenue = qty * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            # Wealth check BEFORE adding revenue to cash
            wealth = cash
            for lots in portfolios.values():
                for lot_qty, lot_cost in lots:
                    wealth += lot_qty * lot_cost
            penalty = 0.02 if wealth > 10000 else 0.0

            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0.0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

            # Drift after sale
            _drift_all(portfolios)

    # Final answer
    total_value = cash
    for lots in portfolios.values():
        for lot_qty, lot_cost in lots:
            total_value += lot_qty * lot_cost
    return round(total_value, 2)


if __name__ == "__main__":
    print(run())
