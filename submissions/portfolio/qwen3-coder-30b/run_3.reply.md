<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:50:36+00:00 -->

```python
def run() -> float:
    # Initialize data structures
    portfolios = {}  # portfolio_id -> list of lots (quantity, unit_cost)
    cash = 0.0
    last_sale_was_profitable = False
    
    # Transactions
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
    
    def get_portfolio(portfolio_id):
        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = []
        return portfolios[portfolio_id]
    
    def apply_holding_cost_drift():
        for portfolio in portfolios.values():
            for i in range(len(portfolio)):
                quantity, unit_cost = portfolio[i]
                unit_cost *= 1.001
                portfolio[i] = (quantity, round(unit_cost, 4))
    
    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        if txn_type == 'BUY':
            portfolio = get_portfolio(portfolio_id)
            # Determine unit cost based on last_sale_was_profitable
            if last_sale_was_profitable:
                lot_unit_cost = unit_price * 1.01
            else:
                lot_unit_cost = unit_price
            
            # Add new lot to portfolio
            portfolio.append((quantity, round(lot_unit_cost, 4)))
            
        elif txn_type == 'SELL':
            portfolio = get_portfolio(portfolio_id)
            
            # Remove lots in FIFO order
            cost_basis = 0.0
            units_sold = 0
            
            # Process lots until we have enough units
            while units_sold < quantity:
                if not portfolio:
                    raise ValueError("Not enough lots to sell")
                
                lot_quantity, lot_cost = portfolio[0]
                if lot_quantity <= quantity - units_sold:
                    # Take entire lot
                    units_sold += lot_quantity
                    cost_basis += lot_quantity * lot_cost
                    portfolio.pop(0)
                else:
                    # Split lot
                    remaining_units = quantity - units_sold
                    cost_basis += remaining_units * lot_cost
                    units_sold = quantity
                    portfolio[0] = (lot_quantity - remaining_units, lot_cost)
            
            # Calculate revenue and profit
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            
            # Update flag
            last_sale_was_profitable = gross_profit > 0
            
            # Wealth tax check
            # Compute wealth before adding revenue to cash
            wealth = cash
            for p in portfolios.values():
                for q, c in p:
                    wealth += q * c
            
            penalty = 0.02 if wealth > 10000 else 0
            
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            
            # Update cash
            cash += revenue - tax
        
        # Apply holding cost drift after every transaction
        apply_holding_cost_drift()
    
    # Calculate final answer: cash + value of all remaining lots
    total_value = cash
    for portfolio in portfolios.values():
        for quantity, unit_cost in portfolio:
            total_value += quantity * unit_cost
    
    return round(total_value, 2)
```