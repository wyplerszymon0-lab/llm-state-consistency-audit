<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T10:27:15+00:00 -->

```python
#!/usr/bin/env python3
"""
Simulate the portfolio ledger as described in the problem statement.
"""

def run() -> float:
    """
    Perform the simulation and return the final value (cash + holdings)
    rounded to two decimal places.
    """
    # Initial state
    portfolios = {101: [], 102: [], 103: []}  # each is a list of [quantity, unit_cost]
    cash = 0.0
    last_sale_profitable = False

    # Transaction list (txn_id, portfolio_id, type, quantity, unit_price)
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
        (15, 101, "SELL", 5, 145),
    ]

    for _, port_id, tx_type, qty, unit_price in transactions:
        if tx_type == "BUY":
            # Determine unit cost with possible 1% premium
            unit_cost = unit_price * (1.01 if last_sale_profitable else 1.0)
            portfolios[port_id].append([qty, unit_cost])

        elif tx_type == "SELL":
            # FIFO removal of lots, compute cost basis
            remaining = qty
            cost_basis = 0.0
            lots = portfolios[port_id]
            while remaining > 0 and lots:
                lot_qty, lot_cost = lots[0]
                if lot_qty <= remaining:
                    cost_basis += lot_qty * lot_cost
                    remaining -= lot_qty
                    lots.pop(0)
                else:
                    cost_basis += remaining * lot_cost
                    lots[0][0] = lot_qty - remaining
                    remaining = 0

            # Revenue and profit
            revenue = qty * unit_price
            gross_profit = revenue - cost_basis

            # Wealth before adding revenue
            value_remaining = sum(q * c for p in portfolios.values() for q, c in p)
            wealth = cash + value_remaining
            penalty = 0.02 if wealth > 10000 else 0.0

            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = gross_profit * (base_rate + penalty)
            if tax < 0:
                tax = 0.0

            # Update cash and global flag
            cash += revenue - tax
            last_sale_profitable = gross_profit > 0

        else:
            raise ValueError(f"Unknown transaction type: {tx_type}")

        # Apply holding cost drift to all lots
        for p in portfolios.values():
            for lot in p:
                lot[1] = round(lot[1] * 1.001, 4)

    # Final answer
    final_value = cash + sum(q * c for p in portfolios.values() for q, c in p)
    return round(final_value, 2)


# If the module is executed directly, run the simulation and print the result.
if __name__ == "__main__":
    result = run()
    print(result)
```
