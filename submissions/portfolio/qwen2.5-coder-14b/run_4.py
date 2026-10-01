from collections import deque

class Portfolio:
    def __init__(self):
        self.lots = deque()
    
    def buy(self, quantity, unit_price, last_sale_was_profitable):
        if last_sale_was_profitable:
            unit_price *= 1.01
        self.lots.append((quantity, round(unit_price, 4)))
    
    def sell(self, quantity, unit_price):
        total_quantity = 0
        cost_basis = 0.0
        
        while quantity > 0:
            lot_quantity, lot_unit_cost = self.lots.popleft()
            if lot_quantity <= quantity:
                total_quantity += lot_quantity
                cost_basis += lot_quantity * lot_unit_cost
                quantity -= lot_quantity
            else:
                self.lots.appendleft((lot_quantity - quantity, lot_unit_cost))
                total_quantity += quantity
                cost_basis += quantity * lot_unit_cost
                quantity = 0
        
        revenue = total_quantity * unit_price
        gross_profit = revenue - cost_basis
        last_sale_was_profitable = gross_profit > 0
        
        wealth = 0
        for p in portfolios.values():
            for q, c in p.lots:
                wealth += q * c
        
        penalty = 0.02 if wealth > 10000 else 0
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        
        global cash
        cash += revenue - tax
        
        return last_sale_was_profitable

def run() -> float:
    global cash, last_sale_was_profitable, portfolios
    
    cash = 0
    last_sale_was_profitable = False
    portfolios = {101: Portfolio(), 102: Portfolio(), 103: Portfolio()}
    
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
            portfolios[portfolio_id].buy(quantity, unit_price, last_sale_was_profitable)
        elif txn_type == 'SELL':
            last_sale_was_profitable = portfolios[portfolio_id].sell(quantity, unit_price)
        
        for p in portfolios.values():
            for i in range(len(p.lots)):
                q, c = p.lots[i]
                p.lots[i] = (q, round(c * 1.001, 4))
    
    total_wealth = cash
    for p in portfolios.values():
        for q, c in p.lots:
            total_wealth += q * c
    
    return round(total_wealth, 2)

# Example usage
if __name__ == "__main__":
    print(run())
