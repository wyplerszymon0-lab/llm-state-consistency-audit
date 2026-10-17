#!/usr/bin/env python3
"""
Simulate the portfolio ledger and compute the final net worth.

The implementation follows the rules specified in the problem statement.
"""

from __future__ import annotations

def run() -> float:
    # Transaction data: txn_id, portfolio_id, type, quantity, unit_price
    transactions = [
        (1,  101, 'BUY',  10, 100),
        (2,  102, 'BUY',  20, 200),
        (3,  101, 'BUY',  10, 110),
        (4,  101, 'SELL', 15, 120),
        (5,  102, 'SELL', 10, 210),
        (6,  101, 'BUY',  20, 115),
        (7,  103, 'BUY',  50,  50),
        (8,  101, 'SELL', 10, 130),
        (9,  102, 'BUY',  15, 205),
        (10, 103, 'SELL', 20,  55),
        (11, 101, 'BUY',  10, 120),
        (12, 101, 'SELL', 15, 140),
        (13, 102, 'SELL', 20, 215),
        (14, 103, 'BUY',  10,  60),
        (15, 101, 'SELL',  5, 145),
    ]

    # State
    cash = 0.0
    portfolios: dict[int, list[list[float, float]]] = {}  # id -> list of [qty, unit_cost]
    last_sale_was_profitable = False

    # Helper to ensure a portfolio exists
    def get_portfolio(pid: int):
        if pid not in portfolios:
            portfolios[pid] = []
        return portfolios[pid]

    # Process each transaction
    for _, pid, ttype, qty, unit_price in transactions:
        if ttype == 'BUY':
            # Determine unit cost
            unit_cost = unit_price * (1.01 if last_sale_was_profitable else 1.0)
            # Append lot
            get_portfolio(pid).append([qty, unit_cost])

        elif ttype == 'SELL':
            remaining = qty
            cost_basis = 0.0
            # FIFO removal
            lot_list = get_portfolio(pid)
            while remaining > 0 and lot_list:
                lot_qty, lot_cost = lot_list[0]
                if lot_qty <= remaining:
                    cost_basis += lot_qty * lot_cost
                    remaining -= lot_qty
                    lot_list.pop(0)
                else:
                    cost_basis += remaining * lot_cost
                    lot_list[0][0] = lot_qty - remaining
                    remaining = 0
            # Compute financials
            revenue = qty * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0.0

            # Wealth before revenue is added
            wealth = cash
            for lots in portfolios.values():
                for lqty, lcost in lots:
                    wealth += lqty * lcost
            penalty = 0.02 if wealth > 10000 else 0.0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0.0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

        else:
            raise ValueError(f"Unknown transaction type: {ttype}")

        # Apply holding cost drift after every transaction
        for lots in portfolios.values():
            for lot in lots:
                lot[1] = round(lot[1] * 1.001, 4)

    # Final net worth
    net_worth = cash
    for lots in portfolios.values():
        for qty, unit_cost in lots:
            net_worth += qty * unit_cost

    return round(net_worth, 2)

# Optional: if executed as a script, print the result
if __name__ == "__main__":
    print(run())
