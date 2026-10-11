def run() -> float:
    cash = 0.0
    portfolios = {101: [], 102: [], 103: []}
    last_sale_was_profitable = False

    def drift_lots(lots):
        return [(quantity, round(unit_cost * 1.001, 4)) for quantity, unit_cost in lots]

    def sell(portfolio_id, quantity, unit_price):
        nonlocal last_sale_was_profitable
        lots = portfolios[portfolio_id]
        cost_basis = 0.0
        for _ in range(quantity):
            if not lots:
                break
            lot_quantity, lot_unit_cost = lots.pop(0)
            if lot_quantity == quantity:
                cost_basis += quantity * lot_unit_cost
                break
            elif lot_quantity > quantity:
                cost_basis += quantity * lot_unit_cost
                lots.insert(0, (lot_quantity - quantity, lot_unit_cost))
                break
            else:
                cost_basis += lot_quantity * lot_unit_cost
                quantity -= lot_quantity
        revenue = quantity * unit_price
        gross_profit = revenue - cost_basis
        if gross_profit > 0:
            last_sale_was_profitable = True
        else:
            last_sale_was_profitable = False
        penalty = 0.0
        wealth = cash + sum(q * u for q, u in lots)
        if wealth > 10000:
            penalty = 0.02
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        cash += revenue - tax
        return lots

    def buy(portfolio_id, quantity, unit_price):
        nonlocal last_sale_was_profitable
        if last_sale_was_profitable:
            unit_price *= 1.01
        last_sale_was_profitable = False
        portfolios[portfolio_id].append((quantity, unit_price))
        return portfolios[portfolio_id]

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
            portfolios[portfolio_id] = buy(portfolio_id, quantity, unit_price)
        elif txn_type == 'SELL':
            portfolios[portfolio_id] = sell(portfolio_id, quantity, unit_price)
        portfolios[portfolio_id] = drift_lots(portfolios[portfolio_id])

    final_wealth = cash + sum(quantity * unit_cost for quantity, unit_cost in lots for lots in portfolios.values())
    return round(final_wealth, 2)

print(run())
