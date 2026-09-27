from collections import defaultdict, deque

def run() -> float:
    cash = 0.0
    portfolios = defaultdict(deque)
    last_sale_was_profitable = False

    def update_lots(portfolio):
        for lot in portfolio:
            lot[1] = round(lot[1] * 1.001, 4)

    def buy(portfolio_id, quantity, unit_price):
        unit_price = unit_price * 1.1 if last_sale_was_profitable else unit_price
        portfolios[portfolio_id].append([quantity, unit_price])
        update_lots(portfolios[portfolio_id])

    def sell(portfolio_id, quantity, unit_price):
        global cash, last_sale_was_profitable
        cost_basis = 0.0
        revenue = quantity * unit_price
        for _ in range(quantity):
            while portfolios[portfolio_id] and portfolios[portfolio_id][0][0] < quantity:
                lot = portfolios[portfolio_id].popleft()
                cost_basis += lot[0] * lot[1]
                quantity -= lot[0]
            lot = portfolios[portfolio_id].popleft()
            cost_basis += quantity * lot[1]
            lot[0] -= quantity
            if lot[0] > 0:
                portfolios[portfolio_id].appendleft(lot)
            quantity = 0
        gross_profit = revenue - cost_basis
        last_sale_was_profitable = gross_profit > 0
        wealth = cash + sum(q * c for p in portfolios.values() for q, c in p)
        penalty = 0.02 if wealth > 10000 else 0
        base_rate = 0.15 if gross_profit > 200 else 0.05
        tax = max(0, gross_profit * (base_rate + penalty))
        cash += revenue - tax

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
            buy(portfolio_id, quantity, unit_price)
        elif txn_type == 'SELL':
            sell(portfolio_id, quantity, unit_price)

    total_value = cash
    for portfolio in portfolios.values():
        for quantity, unit_cost in portfolio:
            total_value += quantity * unit_cost

    return round(total_value, 2)

# The result of run() will be printed here if executed directly
print(run())
