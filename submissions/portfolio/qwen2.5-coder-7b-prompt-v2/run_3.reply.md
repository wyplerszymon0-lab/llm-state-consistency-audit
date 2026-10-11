<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T10:22:21+00:00 -->

```python
def run() -> float:
    cash = 0.0
    portfolios = {101: [], 102: [], 103: []}
    last_sale_was_profitable = False

    for txn_id, portfolio_id, type, quantity, unit_price in [
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
    ]:
        if type == 'BUY':
            cost = unit_price * 1.01 if last_sale_was_profitable else unit_price
            lots = portfolios[portfolio_id]
            lots.append((quantity, cost))
            last_sale_was_profitable = False
        elif type == 'SELL':
            lots = portfolios[portfolio_id]
            total_cost_basis = 0
            for i in range(quantity):
                if not lots:
                    break
                q, c = lots.pop(0)
                if q > quantity:
                    lots.insert(0, (q - quantity, c))
                    quantity = 0
                else:
                    quantity -= q
                    total_cost_basis += q * c
            revenue = quantity * unit_price
            gross_profit = revenue - total_cost_basis
            if gross_profit > 0:
                last_sale_was_profitable = True
            wealth = cash + sum(q * c for p in portfolios.values() for q, c in p)
            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax
        for p in portfolios.values():
            for i in range(len(p)):
                q, c = p[i]
                p[i] = (q, round(c * 1.001, 4))
    total_value = cash + sum(q * c for p in portfolios.values() for q, c in p)
    return round(total_value, 2)
```