<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-09-30T19:28:33+00:00 -->

```python
from collections import deque

def run() -> float:
    # Initial state
    cash = 0
    portfolios = {101: deque(), 102: deque(), 103: deque()}
    last_sale_was_profitable = False

    # Transactions
    transactions = [
        (1, 101, 'BUY', 10, 100),
        (2, 102, 'BUY', 20, 200),
        (3, 101, 'BUY', 10, 110),
        (4, 101, 'SELL', 15, 120),
        (5, 102, 'SELL', 10, 210),
        (6, 101, 'BUY', 20, 115),
        (7, 103, 'BUY', 50, 50),
        (8, 101, 'SELL', 10, 130),
        (9, 102, 'BUY', 15, 205),
        (10, 103, 'SELL', 20, 55),
        (11, 101, 'BUY', 10, 120),
        (12, 101, 'SELL', 15, 140),
        (13, 102, 'SELL', 20, 215),
        (14, 103, 'BUY', 10, 60),
        (15, 101, 'SELL', 5, 145)
    ]

    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        if txn_type == 'BUY':
            # Adjust unit price if last sale was profitable
            if last_sale_was_profitable:
                unit_price *= 1.01
            portfolios[portfolio_id].append((quantity, round(unit_price, 4)))
        elif txn_type == 'SELL':
            remaining_quantity = quantity
            cost_basis = 0.0
            while remaining_quantity > 0:
                lot_quantity, lot_unit_cost = portfolios[portfolio_id][0]
                if lot_quantity <= remaining_quantity:
                    cost_basis += lot_quantity * lot_unit_cost
                    remaining_quantity -= lot_quantity
                    portfolios[portfolio_id].popleft()
                else:
                    cost_basis += remaining_quantity * lot_unit_cost
                    portfolios[portfolio_id][0] = (lot_quantity - remaining_quantity, lot_unit_cost)
                    remaining_quantity = 0

            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            # Wealth tax check
            wealth = cash
            for p in portfolios.values():
                for q, c in p:
                    wealth += q * c

            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))

            cash += revenue - tax

        # Holding cost drift
        for p in portfolios.values():
            for i in range(len(p)):
                q, c = p[i]
                p[i] = (q, round(c * 1.001, 4))

    # Calculate final wealth
    final_wealth = cash
    for p in portfolios.values():
        for q, c in p:
            final_wealth += q * c

    return round(final_wealth, 2)

# Example usage
if __name__ == "__main__":
    print(run())
```