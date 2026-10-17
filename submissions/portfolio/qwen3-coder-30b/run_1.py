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
    
    def buy(portfolio_id, quantity, unit_price):
        nonlocal last_sale_was_profitable
        lots = get_portfolio(portfolio_id)
        cost = unit_price * 1.01 if last_sale_was_profitable else unit_price
        lots.append((quantity, cost))
    
    def sell(portfolio_id, quantity, unit_price):
        nonlocal cash, last_sale_was_profitable
        
        lots = get_portfolio(portfolio_id)
        
        # Calculate cost basis
        cost_basis = 0.0
        remaining_quantity = quantity
        
        while remaining_quantity > 0:
            if not lots:
                raise ValueError("Not enough lots to sell")
            
            lot_quantity, lot_cost = lots[0]
            if lot_quantity <= remaining_quantity:
                # Take the entire lot
                cost_basis += lot_quantity * lot_cost
                remaining_quantity -= lot_quantity
                lots.pop(0)
            else:
                # Partially take the lot
                cost_basis += remaining_quantity * lot_cost
                lots[0] = (lot_quantity - remaining_quantity, lot_cost)
                remaining_quantity = 0
        
        revenue = quantity * unit_price
        gross_profit = revenue - cost_basis
        
        # Update flag
        last_sale_was_profitable = gross_profit > 0
        
        # Wealth tax check
        total_wealth = cash + sum(qty * cost for qty, cost in get_all_lots())
        penalty = 0.02 if total_wealth > 10000 else 0.0
        
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        
        cash += revenue - tax
    
    def get_all_lots():
        all_lots = []
        for lots in portfolios.values():
            all_lots.extend(lots)
        return all_lots
    
    # Process transactions
    for txn_id, portfolio_id, type_, quantity, unit_price in transactions:
        if type_ == 'BUY':
            buy(portfolio_id, quantity, unit_price)
        elif type_ == 'SELL':
            sell(portfolio_id, quantity, unit_price)
        
        # Apply holding cost drift to all lots
        for lots in portfolios.values():
            for i in range(len(lots)):
                qty, cost = lots[i]
                lots[i] = (qty, round(cost * 1.001, 4))
    
    # Calculate final answer
    total_value = cash + sum(qty * cost for lots in portfolios.values() for qty, cost in lots)
    return round(total_value, 2)
