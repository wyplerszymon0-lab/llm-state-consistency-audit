<!-- model: ollama:qwen2.5-coder:14b | prompt v2 | 2026-10-10T14:20:44+00:00 -->

```python
from collections import deque

class Portfolio:
    def __init__(self):
        self.lots = deque()

    def buy(self, quantity, unit_price, last_sale_was_profitable):
        if last_sale_was_profitable:
            unit_price *= 1.01
        self.lots.append((quantity, round(unit_price, 4)))

    def sell(self, quantity, unit_price):
        cost_basis = 0
        sold_quantity = 0
        while quantity > 0:
            lot_quantity, lot_unit_cost = self.lots.popleft()
            if lot_quantity <= quantity:
                cost_basis += lot_quantity * lot_unit_cost
                sold_quantity += lot_quantity
                quantity -= lot_quantity
            else:
                cost_basis += quantity * lot_unit_cost
                sold_quantity += quantity
                self.lots.appendleft((lot_quantity - quantity, lot_unit_cost))
                quantity = 0

        revenue = sold_quantity * unit_price
        gross_profit = revenue - cost_basis
        return gross_profit

    def apply_holding_cost_drift(self):
        for i in range(len(self.lots)):
            quantity, unit_cost = self.lots[i]
            self.lots[i] = (quantity, round(unit_cost * 1.001, 4))

def run() -> float:
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

    portfolios = {}
    cash = 0
    last_sale_was_profitable = False

    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = Portfolio()

        if txn_type == "BUY":
            portfolios[portfolio_id].buy(quantity, unit_price, last_sale_was_profitable)
        elif txn_type == "SELL":
            gross_profit = portfolios[portfolio_id].sell(quantity, unit_price)
            last_sale_was_profitable = gross_profit > 0

            wealth = cash
            for p in portfolios.values():
                for q, c in p.lots:
                    wealth += q * c

            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

        for p in portfolios.values():
            p.apply_holding_cost_drift()

    total_value = cash
    for p in portfolios.values():
        for q, c in p.lots:
            total_value += q * c

    return round(total_value, 2)

print(run())
```