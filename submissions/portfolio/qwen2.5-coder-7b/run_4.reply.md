<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:17:58+00:00 -->

```python
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

def run() -> float:
    cash = Decimal(0)
    portfolios = defaultdict(list)
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
        (15, 101, 'SELL', 5, 145)
    ]:
        if txn_type == 'BUY':
            unit_cost = Decimal(unit_price) * (1.01 if last_sale_was_profitable else 1)
            portfolios[portfolio_id].append((quantity, unit_cost))
            last_sale_was_profitable = False
        elif txn_type == 'SELL':
            quantity_to_sell = quantity
            cost_basis = Decimal(0)
            while quantity_to_sell > 0:
                q, uc = portfolios[portfolio_id].pop(0)
                if q > quantity_to_sell:
                    portfolios[portfolio_id].insert(0, (q - quantity_to_sell, uc))
                    quantity_to_sell = 0
                else:
                    quantity_to_sell -= q
                    cost_basis += q * uc
            revenue = quantity * Decimal(unit_price)
            gross_profit = revenue - cost_basis
            if gross_profit > 0:
                last_sale_was_profitable = True
            wealth = cash + sum(q * uc for portfolio in portfolios.values() for q, uc in portfolio)
            penalty = Decimal(0.02) if wealth > 10000 else Decimal(0)
            base_rate = Decimal(0.15) if gross_profit > 200 else Decimal(0.05)
            tax = max(Decimal(0), gross_profit * (base_rate + penalty))
            cash += revenue - tax
        for portfolio in portfolios.values():
            for i in range(len(portfolio)):
                quantity, unit_cost = portfolio[i]
                portfolio[i] = (quantity, round(unit_cost * Decimal(1.001), 4))

    wealth = cash + sum(q * uc for portfolio in portfolios.values() for q, uc in portfolio)
    return round(wealth, 2)

print(run())
```