<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:44:46+00:00 -->

```python
from decimal import Decimal

def run() -> float:
    cash = Decimal(0)
    portfolios = {101: [], 102: [], 103: []}
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
        (15, 101, 'SELL', 5, 145),
    ]

    for txn_id, portfolio_id, type, quantity, unit_price in transactions:
        for portfolio, lots in portfolios.items():
            if portfolio == portfolio_id:
                last_lot = lots[-1] if lots else None

        if type == 'BUY':
            if last_sale_was_profitable:
                unit_price = Decimal(unit_price) * Decimal('1.01')
            lots[portfolio_id].append((quantity, unit_price))
        else:  # 'SELL'
            quantity = int(quantity)
            for _ in range(quantity):
                removed_lot = lots[portfolio_id].pop(0)
                removed_quantity = removed_lot[0]
                unit_cost = round(Decimal(removed_lot[1]) * Decimal('1.001'), 4)
                cost_basis = removed_quantity * unit_cost
                revenue = quantity * Decimal(unit_price)
                gross_profit = revenue - cost_basis
                last_sale_was_profitable = gross_profit > 0
                wealth = sum(lot[0] * Decimal(lot[1]) for lot in lots[portfolio_id]) + cash
                if wealth > 10000:
                    penalty = 0.02
                else:
                    penalty = 0
                base_rate = 0.15 if gross_profit > 200 else 0.05
                tax = max(0, gross_profit * (base_rate + penalty))
                cash += revenue - tax
                quantity -= 1

        for portfolio, lots in portfolios.items():
            for i, (q, unit_price) in enumerate(lots):
                lots[portfolio][i] = (q, unit_price)

    wealth = cash
    for portfolio in portfolios.values():
        wealth += sum(lot[0] * Decimal(lot[1]) for lot in portfolio)
    return round(wealth, 2)

print(run())
```