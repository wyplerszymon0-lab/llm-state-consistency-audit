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
        for portfolio_id in portfolios:
            for i in range(len(portfolios[portfolio_id])):
                quantity, unit_cost = portfolios[portfolio_id][i]
                unit_cost *= 1.001
                portfolios[portfolio_id][i] = (quantity, round(unit_cost, 4))
    
    def buy(portfolio_id, quantity, unit_price):
        nonlocal last_sale_was_profitable
        lots = get_portfolio(portfolio_id)
        if last_sale_was_profitable:
            cost = unit_price * 1.01
        else:
            cost = unit_price
        lots.append((quantity, cost))
    
    def sell(portfolio_id, quantity, unit_price):
        nonlocal cash, last_sale_was_profitable
        
        lots = get_portfolio(portfolio_id)
        
        # Calculate cost basis
        cost_basis = 0.0
        remaining_quantity = quantity
        removed_lots = []
        
        while remaining_quantity > 0:
            if not lots:
                raise ValueError("Not enough lots to sell")
            
            lot_quantity, lot_cost = lots[0]
            if lot_quantity <= remaining_quantity:
                # Take entire lot
                removed_lots.append((lot_quantity, lot_cost))
                cost_basis += lot_quantity * lot_cost
                lots.pop(0)
                remaining_quantity -= lot_quantity
            else:
                # Split the lot
                removed_lots.append((remaining_quantity, lot_cost))
                cost_basis += remaining_quantity * lot_cost
                lots[0] = (lot_quantity - remaining_quantity, lot_cost)
                remaining_quantity = 0
        
        # Calculate revenue
        revenue = quantity * unit_price
        gross_profit = revenue - cost_basis
        
        # Update last_sale_was_profitable
        last_sale_was_profitable = gross_profit > 0
        
        # Wealth tax check
        # Compute wealth before adding revenue to cash
        total_wealth = cash
        for pid in portfolios:
            for lot_q, lot_c in portfolios[pid]:
                total_wealth += lot_q * lot_c
        
        penalty = 0.02 if total_wealth > 10000 else 0.0
        
        # Calculate tax
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        
        # Update cash
        cash += revenue - tax
    
    for txn_id, portfolio_id, type_, quantity, unit_price in transactions:
        if type_ == 'BUY':
            buy(portfolio_id, quantity, unit_price)
        elif type_ == 'SELL':
            sell(portfolio_id, quantity, unit_price)
        
        # Apply holding cost drift after every transaction
        apply_holding_cost_drift()
    
    # Compute final answer
    total_value = cash
    for portfolio_id in portfolios:
        for lot_q, lot_c in portfolios[portfolio_id]:
            total_value += lot_q * lot_c
    
    return round(total_value, 2)
