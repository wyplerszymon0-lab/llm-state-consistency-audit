"""Reference solver for the warehouse scenario. See prompt.md for the rules."""

SKUS = {
    # sku: (shelf_life_days, reorder_point, reorder_qty, standard_cost)
    "A": (5, 8, 20, 4.00),
    "B": (30, 5, 10, 12.50),
    "C": (3, 4, 12, 2.20),
}
LEAD_TIME = 2
LAST_DAY = 20
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

EVENTS = [
    (1, "RECEIVE", "A", 30, 3.80),
    (1, "RECEIVE", "B", 8, 12.00),
    (1, "RECEIVE", "C", 10, 2.00),
    (2, "ORDER", "A", 12, 7.50),
    (2, "ORDER", "C", 4, 4.00),
    (3, "RECEIVE", "A", 10, 3.90),
    (3, "ORDER", "B", 6, 20.00),
    (4, "ORDER", "B", 5, 21.00),
    (4, "ORDER", "C", 3, 4.20),
    (5, "ORDER", "A", 15, 7.40),
    (6, "ORDER", "C", 2, 4.10),
    (7, "ORDER", "A", 9, 7.60),
    (8, "ORDER", "A", 5, 7.60),
    (8, "RECEIVE", "A", 2, 3.95),
    (9, "ORDER", "C", 11, 4.00),
    (10, "ORDER", "B", 8, 20.50),
    (10, "ORDER", "C", 2, 4.00),
    (12, "ORDER", "A", 10, 7.80),
    (13, "ORDER", "A", 1, 7.80),
    (14, "ORDER", "C", 5, 4.30),
    (15, "ORDER", "C", 3, 4.30),
    (16, "ORDER", "A", 25, 7.90),
    (18, "ORDER", "B", 9, 22.00),
    (19, "ORDER", "B", 4, 22.00),
    (19, "ORDER", "A", 16, 8.00),
    (20, "ORDER", "C", 10, 4.50),
]


# Each rule, switched off. Used by the tests (every rule must change the answer)
# and by the report, which checks whether a wrong answer equals one of these.
RULES = {
    "2-day reorder lead time": {"LEAD_TIME": 1},
    "10% backorder discount": {"BACKORDER_DISCOUNT": 1.0},
    "cancellation penalty": {"CANCELLATION_PENALTY": 0.0},
    "expiry of perishable batches": {"SKUS": {sku: (999, *rest) for sku, (_, *rest) in SKUS.items()}},
}


def run() -> float:
    batches = {sku: [] for sku in SKUS}      # [qty, unit_cost, expiry_day, receipt_seq]
    backorders = {sku: [] for sku in SKUS}   # FIFO of [qty, unit_price]
    in_transit = {}                          # sku -> arrival_day
    revenue = cogs = write_offs = 0.0
    seq = 0

    def receive(day, sku, qty, unit_cost):
        nonlocal revenue, cogs, seq
        queue = backorders[sku]
        while qty > 0 and queue:
            bo = queue[0]
            take = min(qty, bo[0])
            revenue += take * bo[1] * BACKORDER_DISCOUNT
            cogs += take * unit_cost
            bo[0] -= take
            qty -= take
            if bo[0] == 0:
                queue.pop(0)
        if qty > 0:
            seq += 1
            batches[sku].append([qty, unit_cost, day + SKUS[sku][0], seq])

    for day in range(1, LAST_DAY + 1):
        for sku, stock in batches.items():
            for b in [b for b in stock if b[2] < day]:
                write_offs += b[0] * b[1]
                stock.remove(b)

        for sku in sorted(s for s, arrival in in_transit.items() if arrival == day):
            del in_transit[sku]
            _, _, reorder_qty, standard_cost = SKUS[sku]
            receive(day, sku, reorder_qty, standard_cost)

        for ev_day, kind, sku, qty, price in EVENTS:
            if ev_day != day:
                continue
            if kind == "RECEIVE":
                receive(day, sku, qty, price)
                continue

            stock = batches[sku]
            stock.sort(key=lambda b: (b[2], b[3]))
            remaining = qty
            while remaining > 0 and stock:
                b = stock[0]
                take = min(remaining, b[0])
                revenue += take * price
                cogs += take * b[1]
                b[0] -= take
                remaining -= take
                if b[0] == 0:
                    stock.pop(0)
            if remaining > 0:
                backorders[sku].append([remaining, price])

            on_hand = sum(b[0] for b in stock)
            if on_hand < SKUS[sku][1] and sku not in in_transit:
                in_transit[sku] = day + LEAD_TIME

    unfilled = sum(bo[0] for queue in backorders.values() for bo in queue)
    profit = revenue - cogs - write_offs - unfilled * CANCELLATION_PENALTY
    return round(profit, 2)


if __name__ == "__main__":
    print(run())
