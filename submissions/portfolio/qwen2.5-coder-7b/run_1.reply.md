<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:16:57+00:00 -->

```python
def run() -> float:
    cash = 0.0
    portfolios = {101: [], 102: [], 103: []}
    last_sale_was_profitable = False

    for txn_id, portfolio_id, txn_type, quantity, unit_price in [
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
        (15, 101, 'SELL', 5, 145),
    ]:
        if txn_type == 'BUY':
            if last_sale_was_profitable:
                unit_price *= 1.01
            portfolios[portfolio_id].append((quantity, unit_price))
        elif txn_type == 'SELL':
            remaining_quantity = quantity
            cost_basis = 0
            for _ in range(remaining_quantity):
                if not portfolios[portfolio_id]:
                    break
                lot_quantity, lot_cost = portfolios[portfolio_id][0]
                if lot_quantity <= remaining_quantity:
                    remaining_quantity -= lot_quantity
                    cost_basis += lot_quantity * lot_cost
                    portfolios[portfolio_id].pop(0)
                else:
                    lot_quantity -= remaining_quantity
                    cost_basis += remaining_quantity * lot_cost
                    portfolios[portfolio_id][0] = (lot_quantity, lot_cost)
                    remaining_quantity = 0
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0
            wealth = cash + sum(q * c for p in portfolios.values() for q, c in p)
            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

        for portfolio in portfolios.values():
            for i, (q, c) in enumerate(portfolio):
                portfolio[i] = (q, round(c * 1.001, 4))

    result = cash + sum(q * c for p in portfolios.values() for q, c in p)
    return round(result, 2)
```