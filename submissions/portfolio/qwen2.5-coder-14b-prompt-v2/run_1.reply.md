<!-- model: ollama:qwen2.5-coder:14b | prompt v2 | 2026-10-10T12:20:52+00:00 -->

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

        while sold_quantity < quantity:
            lot_quantity, lot_price = self.lots.popleft()
            sell_quantity = min(lot_quantity, quantity - sold_quantity)
            cost_basis += sell_quantity * lot_price
            sold_quantity += sell_quantity

            if sell_quantity < lot_quantity:
                self.lots.appendleft((lot_quantity - sell_quantity, lot_price))

        revenue = quantity * unit_price
        gross_profit = revenue - cost_basis
        last_sale_was_profitable = gross_profit > 0
        return revenue, gross_profit, last_sale_was_profitable

    def apply_drift(self):
        for i in range(len(self.lots)):
            quantity, unit_price = self.lots[i]
            self.lots[i] = (quantity, round(unit_price * 1.001, 4))

class Ledger:
    def __init__(self):
        self.portfolios = {}
        self.cash = 0
        self.last_sale_was_profitable = False

    def process_transaction(self, txn_id, portfolio_id, txn_type, quantity, unit_price):
        if portfolio_id not in self.portfolios:
            self.portfolios[portfolio_id] = Portfolio()

        if txn_type == "BUY":
            self.portfolios[portfolio_id].buy(quantity, unit_price, self.last_sale_was_profitable)
        elif txn_type == "SELL":
            revenue, gross_profit, self.last_sale_was_profitable = self.portfolios[portfolio_id].sell(quantity, unit_price)
            self.wealth_tax_check(revenue, gross_profit)

        for portfolio in self.portfolios.values():
            portfolio.apply_drift()

    def wealth_tax_check(self, revenue, gross_profit):
        wealth = self.cash + sum(quantity * unit_cost for portfolio in self.portfolios.values() for quantity, unit_cost in portfolio.lots)
        penalty = 0.02 if wealth > 10000 else 0
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        self.cash += revenue - tax

    def calculate_final_value(self):
        total_value = self.cash + sum(quantity * unit_cost for portfolio in self.portfolios.values() for quantity, unit_cost in portfolio.lots)
        return round(total_value, 2)

def run():
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

    ledger = Ledger()
    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        ledger.process_transaction(txn_id, portfolio_id, txn_type, quantity, unit_price)

    return ledger.calculate_final_value()

# Example usage
if __name__ == "__main__":
    print(run())
```