<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-26T17:33:08+00:00 -->

```python
def run() -> float:
    cash = 0
    data = [
        (1, 101, "BUY", 10, 100),
        (2, 102, "BUY", 20, 200),
        (3, 101, "BUY", 10, 110),
        (4, 101, "SELL", 15, 120),
        (5, 102, "SELL", 10, 210),
        (6, 101, "BUY", 20, 115),
        (7, 103, "BUY", 50, 50),
        (8, 101, "SELL", 10, 130),
        (9, 102, "BUY", 15, 205),
        (10, 103, "SELL", 20, 55),
        (11, 101, "BUY", 10, 120),
        (12, 101, "SELL", 15, 140),
        (13, 102, "SELL", 20, 215),
        (14, 103, "BUY", 10, 60),
        (15, 101, "SELL", 5, 145)
    ]

    # Initialize portfolios
    portfolios = {
        101: [(10, 100)],
        102: [(20, 200)],
        103: [(50, 50)]
    }
    last_sale_was_profitable = False

    for txn_id, portfolio_id, type, quantity, unit_price in data:
        # Compute unit price with drift (1.001) for buys
        if type == "BUY":
            unit_price = unit_price * (1.01 if last_sale_was_profitable else 1)
        # Compute wealth tax check
        wealth = sum(lot[0] * lot[1] for portfolio in portfolios.values() for lot in portfolio)
        if wealth > 10000:
            penalty = 0.02
        else:
            penalty = 0

        # Process buy
        if type == "BUY":
            portfolios[portfolio_id].append((quantity, unit_price))
            cash += quantity * unit_price

        # Process sell
        elif type == "SELL":
            if quantity == 0:
                continue
            lots = portfolios[portfolio_id][: quantity]
            cost_basis = sum(lot[0] * lot[1] for lot in lots)
            revenue = quantity * unit_price
            gross_profit = revenue - cost_basis
            last_sale_was_profitable = gross_profit > 0

            # Wealth tax check
            wealth = sum(lot[0] * lot[1] for portfolio in portfolios.values() for lot in portfolio)
            if wealth > 10000:
                penalty = 0.02
            else:
                penalty = 0

            # Compute tax rate
            base_rate = 0.15 if gross_profit > 200 else 0.05

            # Compute tax
            tax = max(0, gross_profit * (base_rate + penalty))
            cash += revenue - tax

            # Update portfolio
            portfolios[portfolio_id] = portfolios[portfolio_id][quantity:]

        # Apply holding cost drift
        for portfolio_id, lots in portfolios.items():
            portfolios[portfolio_id] = [(round(lot[0], 4), round(lot[1] * 1.001, 4)) for lot in lots]

    # Compute answer
    answer = cash + sum(lot[0] * round(lot[1] * 1.001, 4) for portfolio in portfolios.values() for lot in portfolio)
    return round(answer, 2)

print(run())
```