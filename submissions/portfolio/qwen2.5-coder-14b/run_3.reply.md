<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-09-30T19:41:42+00:00 -->

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
        total_cost_basis = 0
        total_quantity_sold = 0
        lots_to_remove = []
        
        for lot in self.lots:
            if quantity == 0:
                break
            q, c = lot
            if q <= quantity:
                quantity -= q
                total_quantity_sold += q
                total_cost_basis += q * c
                lots_to_remove.append(lot)
            else:
                q -= quantity
                total_quantity_sold += quantity
                total_cost_basis += quantity * c
                lots_to_remove.append((q, c))
                quantity = 0
        
        for lot in lots_to_remove:
            self.lots.remove(lot)
        
        revenue = total_quantity_sold * unit_price
        gross_profit = revenue - total_cost_basis
        last_sale_was_profitable = gross_profit > 0
        
        wealth = sum(quantity * unit_cost for _, (quantity, unit_cost) in sum((p.lots for p in portfolios.values()), []))
        penalty = 0.02 if wealth > 10000 else 0
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        
        global cash
        cash += revenue - tax
        
        return last_sale_was_profitable

def run():
    global cash, portfolios, last_sale_was_profitable
    
    cash = 0
    portfolios = {101: Portfolio(), 102: Portfolio(), 103: Portfolio()}
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
    
    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        if txn_type == 'BUY':
            portfolios[portfolio_id].buy(quantity, unit_price, last_sale_was_profitable)
        elif txn_type == 'SELL':
            last_sale_was_profitable = portfolios[portfolio_id].sell(quantity, unit_price)
        
        # Apply holding cost drift
        for p in portfolios.values():
            for i in range(len(p.lots)):
                q, c = p.lots[i]
                p.lots[i] = (q, round(c * 1.001, 4))
    
    total_value = cash + sum(quantity * unit_cost for _, (quantity, unit_cost) in sum((p.lots for p in portfolios.values()), []))
    return round(total_value, 2)

# Example usage
if __name__ == "__main__":
    print(run())
```