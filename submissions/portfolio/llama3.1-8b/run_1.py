def run() -> float:
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
        (15, 101, 'SELL', 5, 145),
    ]

    cash = 0
    portfolios = {101: [], 102: [], 103: []}
    last_sale_was_profitable = False

    for txn_id, portfolio_id, txn_type, quantity, unit_price in transactions:
        if txn_type == 'BUY':
            current_price = unit_price
            if last_sale_was_profitable:
                current_price *= 1.01
            portfolios[portfolio_id].append((quantity, current_price))
            cash += quantity * current_price
        else:
            queue = portfolios[portfolio_id]
            revenue = quantity * unit_price
            cost_basis = 0
            for i, (q, unit_cost) in enumerate(queue):
                if i < quantity:
                    cost_basis += q * unit_cost
                    queue[i] = (q - quantity, unit_cost)
                    quantity -= q
                else:
                    break
            cost_basis += quantity * queue[-1][1]
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0
            wealth = cash
            for queue in portfolios.values():
                wealth += sum(q * unit_c for q, unit_c in queue)
            penalty = 0.02 if wealth > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax
            queue[:] = [(q, round(unit_c * 1.001, 4)) for q, unit_c in queue]

    total_value = cash
    for queue in portfolios.values():
        total_value += sum(q * unit_c for q, unit_c in queue)
    return round(total_value, 2)
