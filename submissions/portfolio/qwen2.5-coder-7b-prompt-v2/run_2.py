def run() -> float:
    cash = 0.0
    portfolios = {}
    last_sale_was_profitable = False

    def drift(lots):
        return [(quantity, round(unit_cost * 1.001, 4)) for quantity, unit_cost in lots]

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
        if portfolio_id not in portfolios:
            portfolios[portfolio_id] = []

        if txn_type == 'BUY':
            unit_cost = unit_price * 1.01 if last_sale_was_profitable else unit_price
            portfolios[portfolio_id].append((quantity, unit_cost))
        elif txn_type == 'SELL':
            cost_basis = 0
            for _ in range(quantity):
                lot = portfolios[portfolio_id].pop(0)
                cost_basis += lot[0] * lot[1]
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            if gross_profit > 0:
                last_sale_was_profitable = True
            else:
                last_sale_was_profitable = False
            penalty = 0.02 if cash + sum(q * c for p in portfolios for q, c in p) > 10000 else 0
            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax
            portfolios[portfolio_id] = drift(portfolios[portfolio_id])

    final_value = cash + sum(q * c for p in portfolios for q, c in p)
    return round(final_value, 2)

# print(run())  # Uncomment to run and print the result
