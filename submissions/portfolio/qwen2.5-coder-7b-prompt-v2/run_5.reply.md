<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T11:41:16+00:00 -->

```python
from collections import defaultdict, deque
from decimal import Decimal, getcontext

def run() -> float:
    getcontext().prec = 4  # Set precision for Decimal operations

    cash = Decimal(0)
    portfolios = defaultdict(lambda: deque())
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

    for txn_id, portfolio_id, type, quantity, unit_price in transactions:
        quantity = Decimal(quantity)
        unit_price = Decimal(unit_price)

        if type == 'BUY':
            if last_sale_was_profitable:
                unit_price *= Decimal(1.01)
            portfolios[portfolio_id].append((quantity, unit_price))
            last_sale_was_profitable = False
        elif type == 'SELL':
            cost_basis = Decimal(0)
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis

            if gross_profit > Decimal(0):
                last_sale_was_profitable = True

            wealth = cash
            for portfolio in portfolios.values():
                for q, u in portfolio:
                    wealth += q * u

            penalty = Decimal(0.02) if wealth > Decimal(10000) else Decimal(0)
            base_rate = Decimal(0.15) if gross_profit > Decimal(200) else Decimal(0.05)
            tax = max(Decimal(0), gross_profit * (base_rate + penalty))

            cash += revenue - tax

            lots = []
            while quantity > Decimal(0):
                q, u = portfolios[portfolio_id].popleft()
                if q > quantity:
                    lots.append((q - quantity, u))
                    portfolios[portfolio_id].appendleft(lots.pop())
                    quantity = Decimal(0)
                else:
                    quantity -= q

            for q, u in lots:
                portfolios[portfolio_id].appendleft((q, u))

        # Drift
        for portfolio in portfolios.values():
            for i in range(len(portfolio)):
                q, u = portfolio[i]
                portfolio[i] = (q, round(u * Decimal(1.001), 4))

    # Calculate final value
    final_value = cash
    for portfolio in portfolios.values():
        for q, u in portfolio:
            final_value += q * u

    return round(final_value, 2)

# Example usage
print(run())
```

This Python 3 program simulates the given investment portfolio transactions according to the specified rules and returns the final value of the portfolios and cash.