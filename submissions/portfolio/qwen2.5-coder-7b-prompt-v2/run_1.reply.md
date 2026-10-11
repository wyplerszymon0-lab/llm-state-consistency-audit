<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T10:20:35+00:00 -->

```python
from collections import deque

def run() -> float:
    cash = 0.0
    lots = {101: deque(), 102: deque(), 103: deque()}
    last_sale_was_profitable = False

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
            if last_sale_was_profitable:
                unit_price *= 1.01
            lots[portfolio_id].append((quantity, unit_price))
            last_sale_was_profitable = False
        elif txn_type == 'SELL':
            cost_basis = 0
            for _ in range(quantity):
                q, uc = lots[portfolio_id].popleft()
                cost_basis += q * uc
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0
            wealth = cash + sum(q * uc for p in lots.values() for q, uc in p)
            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax
            lots[portfolio_id] = deque((q, round(uc * 1.001, 4)) for q, uc in lots[portfolio_id] if q > 0)

    total_value = cash + sum(q * uc for p in lots.values() for q, uc in p)
    return round(total_value, 2)

# Example usage:
print(run())
```