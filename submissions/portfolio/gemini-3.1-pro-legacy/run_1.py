"""Model submission: Gemini 3.1 Pro Reasoning.

Frozen output from the target model for the portfolio state-consistency
scenario. Self-contained on purpose (hardcoded data, no imports from audit/)
because this is what the model actually handed back — we don't get to
refactor it, only score it.
"""

from collections import deque

MODEL_NAME = "Gemini 3.1 Pro Reasoning"


def run() -> float:
    # Data: txn_id, portfolio_id, type(1=Buy, 2=Sell), qty, price
    txns = [
        (1, 101, 1, 10, 100), (2, 102, 1, 20, 200), (3, 101, 1, 10, 110),
        (4, 101, 2, 15, 120), (5, 102, 2, 10, 210), (6, 101, 1, 20, 115),
        (7, 103, 1, 50, 50), (8, 101, 2, 10, 130), (9, 102, 1, 15, 205),
        (10, 103, 2, 20, 55), (11, 101, 1, 10, 120), (12, 101, 2, 15, 140),
        (13, 102, 2, 20, 215), (14, 103, 1, 10, 60), (15, 101, 2, 5, 145)
    ]

    portfolios = {}  # {p_id: deque([ [qty, unit_cost], ... ])}
    cash = 0.0
    last_sale_profitable = False

    def get_market_value():
        # Current Market Value of all stocks based on current cost basis
        val = 0.0
        for p_id in portfolios:
            for batch in portfolios[p_id]:
                val += batch[0] * batch[1]
        return val

    for _, p_id, t_type, qty, price in txns:
        if p_id not in portfolios:
            portfolios[p_id] = deque()

        if t_type == 1:  # BUY
            # Rule: Market Surge Modifier (1% Success Fee on price)
            buy_price = float(price)
            if last_sale_profitable:
                buy_price *= 1.01
            portfolios[p_id].append([float(qty), buy_price])

        else:  # SELL
            # Rule: Global Wealth Tax check
            total_wealth = cash + get_market_value()
            wealth_penalty = 0.02 if total_wealth > 10000 else 0.0

            qty_to_sell = float(qty)
            total_revenue = qty_to_sell * price
            total_cost_basis = 0.0

            while qty_to_sell > 0:
                batch = portfolios[p_id][0]
                if batch[0] <= qty_to_sell:
                    q, c = portfolios[p_id].popleft()
                    total_cost_basis += (q * c)
                    qty_to_sell -= q
                else:
                    total_cost_basis += (qty_to_sell * batch[1])
                    batch[0] -= qty_to_sell
                    qty_to_sell = 0

            gross_profit = total_revenue - total_cost_basis

            # Base Tax Logic
            if gross_profit > 0:
                last_sale_profitable = True
                base_tax_rate = 0.15 if gross_profit > 200 else 0.05
                tax_rate = base_tax_rate + wealth_penalty
                tax_amount = gross_profit * tax_rate
                cash += (total_revenue - tax_amount)
            else:
                last_sale_profitable = False
                cash += total_revenue

        # Rule: Continuous Holding Cost (0.1% degradation after every txn)
        for pid in portfolios:
            for batch in portfolios[pid]:
                batch[1] = round(batch[1] * 1.001, 4)

    final_assets = get_market_value()
    return round(cash + final_assets, 2)


if __name__ == "__main__":
    print(f"Final Total Portfolio Value: {run()}")
