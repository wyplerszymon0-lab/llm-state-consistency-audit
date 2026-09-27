<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:18:14+00:00 -->

```python
from collections import deque

def run() -> float:
    cash = 0.0
    portfolios = {101: deque(), 102: deque(), 103: deque()}
    last_sale_was_profitable = False

    def adjust_unit_cost(lots):
        for lot in lots:
            lot[1] = round(lot[1] * 1.001, 4)

    def process_transaction(txn):
        nonlocal cash, last_sale_was_profitable
        portfolio_id = txn[1]
        txn_type = txn[2]
        quantity = txn[3]
        unit_price = txn[4]

        if txn_type == "BUY":
            if last_sale_was_profitable:
                unit_price *= 1.01
            portfolios[portfolio_id].append([quantity, unit_price])
            adjust_unit_cost(portfolios[portfolio_id])
        elif txn_type == "SELL":
            total_cost_basis = 0
            total_revenue = 0
            for _ in range(quantity):
                lot = portfolios[portfolio_id].popleft()
                if lot[0] <= quantity:
                    total_cost_basis += lot[0] * lot[1]
                    total_revenue += lot[0] * unit_price
                    quantity -= lot[0]
                else:
                    total_cost_basis += quantity * lot[1]
                    total_revenue += quantity * unit_price
                    lot[0] -= quantity
                    portfolios[portfolio_id].appendleft(lot)
                    quantity = 0
            gross_profit = total_revenue - total_cost_basis
            last_sale_was_profitable = gross_profit > 0
            wealth = cash + sum(lot[0] * lot[1] for p in portfolios.values() for lot in p)
            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += total_revenue - tax

    transactions = [
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
        (15, 101, "SELL", 5, 145)
    ]

    for txn in transactions:
        process_transaction(txn)

    total_value = cash + sum(lot[0] * lot[1] for p in portfolios.values() for lot in p)
    return round(total_value, 2)
```