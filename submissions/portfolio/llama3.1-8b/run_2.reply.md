<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-26T17:32:22+00:00 -->

```python
def run() -> float:
    class Portfolio:
        def __init__(self, portfolio_id):
            self.id = portfolio_id
            self.cash = 0
            self.lots = []

        def buy(self, unit_price, quantity):
            unit_cost = unit_price * (1.01 if last_sale_was_profitable else 1)
            self.lots.append((quantity, unit_cost))
            self.cash -= quantity * unit_cost

        def sell(self, unit_price, quantity):
            nonlocal last_sale_was_profitable
            cost_basis = 0
            for i, (lot_quantity, unit_cost) in enumerate(self.lots):
                if quantity <= lot_quantity:
                    cost_basis += quantity * unit_cost
                    self.lots[i] = (lot_quantity - quantity, unit_cost)
                    break
                else:
                    cost_basis += lot_quantity * unit_cost
                    self.lots[i] = (0, unit_cost)
                    quantity -= lot_quantity
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0
            if wealth > 10000:
                penalty = 0.02
            else:
                penalty = 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            self.cash += revenue - tax

        def hold_cost_drift(self):
            for i, (quantity, unit_cost) in enumerate(self.lots):
                self.lots[i] = (quantity, round(unit_cost * 1.001, 4))

    global last_sale_was_profitable
    last_sale_was_profitable = False
    global wealth
    wealth = 0

    portfolios = {101: Portfolio(101), 102: Portfolio(102), 103: Portfolio(103)}

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

    for txn_id, portfolio_id, transaction_type, quantity, unit_price in transactions:
        portfolios[portfolio_id].cash += unit_price * quantity
        wealth += quantity * unit_price
        if transaction_type == 'BUY':
            portfolios[portfolio_id].buy(unit_price, quantity)
        else:
            portfolios[portfolio_id].sell(unit_price, quantity)
        for portfolio in portfolios.values():
            portfolio.hold_cost_drift()

    cash = sum(portfolio.cash for portfolio in portfolios.values())
    wealth = sum(quantity * unit_cost for portfolio in portfolios.values() for quantity, unit_cost in portfolio.lots)
    return round(cash + wealth, 2)

print(run())
```