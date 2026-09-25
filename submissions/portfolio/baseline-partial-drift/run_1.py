"""Model submission: Baseline (Partial State Update).

A synthetic fixture demonstrating a genuine state-desynchronization bug, for
exercising the harness's ability to catch it. Not attributed to any real
vendor or model — this is a hand-written "what a plausible mistake looks
like" baseline, not a frozen LLM transcript.

Bug: the 0.1% Holding Cost Drift is supposed to compound every open lot's
cost basis after *every* transaction, buy or sell alike. This version only
applies it after SELL transactions — as if drift were mistakenly reasoned to
be a consequence of trading activity rather than of holding time — so BUY
transactions leave the freshly-added (and existing) lots undrifted for a
step. Over 15 transactions the missed compounding steps compile into a
real, silent divergence from the reference result.
"""

BUY = 1
SELL = 2

TRANSACTIONS = [
    (1, 101, BUY, 10, 100), (2, 102, BUY, 20, 200), (3, 101, BUY, 10, 110),
    (4, 101, SELL, 15, 120), (5, 102, SELL, 10, 210), (6, 101, BUY, 20, 115),
    (7, 103, BUY, 50, 50), (8, 101, SELL, 10, 130), (9, 102, BUY, 15, 205),
    (10, 103, SELL, 20, 55), (11, 101, BUY, 10, 120), (12, 101, SELL, 15, 140),
    (13, 102, SELL, 20, 215), (14, 103, BUY, 10, 60), (15, 101, SELL, 5, 145),
]

MODEL_NAME = "Baseline (Partial State Update)"


def _market_value(portfolios):
    return sum(b[0] * b[1] for units in portfolios.values() for b in units)


def run() -> float:
    portfolios = {}
    cash = 0.0
    last_sale_was_profitable = False

    for _txn_id, p_id, t_type, qty, price in TRANSACTIONS:
        portfolios.setdefault(p_id, [])

        current_price = price
        if t_type == BUY and last_sale_was_profitable:
            current_price *= 1.01

        if t_type == BUY:
            portfolios[p_id].append([qty, current_price])
        else:
            qty_to_sell = qty
            total_cost_basis = 0
            while qty_to_sell > 0 and portfolios[p_id]:
                batch = portfolios[p_id][0]
                if batch[0] <= qty_to_sell:
                    units = batch[0]
                    total_cost_basis += units * batch[1]
                    qty_to_sell -= units
                    portfolios[p_id].pop(0)
                else:
                    units = qty_to_sell
                    total_cost_basis += units * batch[1]
                    batch[0] -= units
                    qty_to_sell = 0

            revenue = qty * current_price
            gross_profit = revenue - total_cost_basis
            last_sale_was_profitable = gross_profit > 0

            current_inv_val = _market_value(portfolios)
            wealth_penalty = 0.02 if (cash + current_inv_val) > 10_000 else 0

            base_rate = 0.15 if gross_profit > 200 else 0.05
            tax_amount = max(0, gross_profit * (base_rate + wealth_penalty))
            cash += revenue - tax_amount

        # BUG: drift should apply after every transaction, not just SELLs.
        if t_type == SELL:
            for pid in portfolios:
                for batch in portfolios[pid]:
                    batch[1] = round(batch[1] * 1.001, 4)

    final_val = round(cash + _market_value(portfolios), 2)
    return final_val


if __name__ == "__main__":
    print(f"Result: {run()}")
