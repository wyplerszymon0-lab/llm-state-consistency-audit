from collections import deque
from typing import NamedTuple, Dict

class Lot(NamedTuple):
    quantity: int
    unit_cost: float

class Portfolio:
    def __init__(self):
        self.lots = deque()
        self.last_sale_was_profitable = False

    def buy(self, quantity: int, unit_price: float) -> None:
        unit_cost = unit_price * 1.01 if self.last_sale_was_profitable else unit_price
        self.lots.append(Lot(quantity, unit_cost))

    def sell(self, quantity: int, unit_price: float) -> None:
        cost_basis = 0.0
        for _ in range(quantity):
            if not self.lots:
                break
            lot = self.lots.popleft()
            cost_basis += lot.quantity * lot.unit_cost
            quantity -= lot.quantity
            if quantity < 0:
                self.lots.appendleft(Lot(-quantity, lot.unit_cost))
                break
        revenue = quantity * unit_price
        gross_profit = revenue - cost_basis
        self.last_sale_was_profitable = gross_profit > 0
        penalty = 0.02 if (self.cash + sum(lot.quantity * lot.unit_cost for lot in self.lots)) > 10000 else 0
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        self.cash += revenue - tax

    def update_unit_costs(self) -> None:
        for lot in self.lots:
            lot.unit_cost = round(lot.unit_cost * 1.001, 4)

class Simulation:
    def __init__(self):
        self.portfolio1 = Portfolio()
        self.portfolio2 = Portfolio()
        self.portfolio3 = Portfolio()
        self.cash = 0.0

    def run(self) -> float:
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
                if portfolio_id == 101:
                    self.portfolio1.buy(quantity, unit_price)
                elif portfolio_id == 102:
                    self.portfolio2.buy(quantity, unit_price)
                elif portfolio_id == 103:
                    self.portfolio3.buy(quantity, unit_price)
            elif txn_type == 'SELL':
                if portfolio_id == 101:
                    self.portfolio1.sell(quantity, unit_price)
                elif portfolio_id == 102:
                    self.portfolio2.sell(quantity, unit_price)
                elif portfolio_id == 103:
                    self.portfolio3.sell(quantity, unit_price)
            for portfolio in [self.portfolio1, self.portfolio2, self.portfolio3]:
                portfolio.update_unit_costs()

        total_value = self.cash
        for portfolio in [self.portfolio1, self.portfolio2, self.portfolio3]:
            for lot in portfolio.lots:
                total_value += lot.quantity * lot.unit_cost

        return round(total_value, 2)

# Example usage
sim = Simulation()
print(sim.run())
