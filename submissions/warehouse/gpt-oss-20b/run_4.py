import math
from collections import defaultdict, deque

def run() -> float:
    # Constants
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    # SKU settings
    SKU_SETTINGS = {
        "A": {"shelf_life": 5, "reorder_point": 8, "reorder_qty": 20, "standard_cost": 4.00},
        "B": {"shelf_life": 30, "reorder_point": 5, "reorder_qty": 10, "standard_cost": 12.50},
        "C": {"shelf_life": 3, "reorder_point": 4, "reorder_qty": 12, "standard_cost": 2.20},
    }

    # Prepare SKU data structures
    class SKU:
        __slots__ = ("shelf_life", "reorder_point", "reorder_qty",
                     "standard_cost", "batches", "backorders",
                     "in_transit", "arrival_day")
        def __init__(self, cfg):
            self.shelf_life = cfg["shelf_life"]
            self.reorder_point = cfg["reorder_point"]
            self.reorder_qty = cfg["reorder_qty"]
            self.standard_cost = cfg["standard_cost"]
            self.batches = []          # list of dicts: {'qty', 'cost', 'expiry', 'arrival_idx'}
            self.backorders = deque()  # deque of dicts: {'qty', 'price'}
            self.in_transit = False
            self.arrival_day = None

    skus = {k: SKU(v) for k, v in SKU_SETTINGS.items()}

    # Totals
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    # Global arrival index for tie‑breaking
    arrival_counter = 0

    # Parse hardcoded events
    raw_events = [
        "1, RECEIVE, A, 30, 3.80",
        "1, RECEIVE, B, 8, 12.00",
        "1, RECEIVE, C, 10, 2.00",
        "2, ORDER, A, 12, 7.50",
        "2, ORDER, C, 4, 4.00",
        "3, RECEIVE, A, 10, 3.90",
        "3, ORDER, B, 6, 20.00",
        "4, ORDER, B, 5, 21.00",
        "4, ORDER, C, 3, 4.20",
        "5, ORDER, A, 15, 7.40",
        "6, ORDER, C, 2, 4.10",
        "7, ORDER, A, 9, 7.60",
        "8, ORDER, A, 5, 7.60",
        "8, RECEIVE, A, 2, 3.95",
        "9, ORDER, C, 11, 4.00",
        "10, ORDER, B, 8, 20.50",
        "10, ORDER, C, 2, 4.00",
        "12, ORDER, A, 10, 7.80",
        "13, ORDER, A, 1, 7.80",
        "14, ORDER, C, 5, 4.30",
        "15, ORDER, C, 3, 4.30",
        "16, ORDER, A, 25, 7.90",
        "18, ORDER, B, 9, 22.00",
        "19, ORDER, B, 4, 22.00",
        "19, ORDER, A, 16, 8.00",
        "20, ORDER, C, 10, 4.50",
    ]

    events_by_day = defaultdict(list)
    for line in raw_events:
        day_s, typ, sku, qty_s, price_s = [x.strip() for x in line.split(",")]
        day = int(day_s)
        qty = int(qty_s)
        price = float(price_s)
        events_by_day[day].append((typ, sku, qty, price))

    # Helper functions
    def process_receive(day: int, sku: SKU, qty: int, unit_cost: float):
        nonlocal revenue, cogs, arrival_counter
        # First fill backorders
        while qty > 0 and sku.backorders:
            bo = sku.backorders[0]
            fill_qty = min(qty, bo["qty"])
            revenue += bo["price"] * BACKORDER_DISCOUNT
            cogs += unit_cost * fill_qty
            qty -= fill_qty
            bo["qty"] -= fill_qty
            if bo["qty"] == 0:
                sku.backorders.popleft()
        # Remaining units become a new batch
        if qty > 0:
            arrival_counter += 1
            sku.batches.append({
                "qty": qty,
                "cost": unit_cost,
                "expiry": day + sku.shelf_life,
                "arrival_idx": arrival_counter,
            })

    def process_order(day: int, sku: SKU, qty: int, price: float):
        nonlocal revenue, cogs, arrival_counter
        remaining = qty
        # Sort batches by expiry, then arrival index
        sku.batches.sort(key=lambda b: (b["expiry"], b["arrival_idx"]))
        for batch in sku.batches:
            if remaining == 0:
                break
            use = min(remaining, batch["qty"])
            revenue += use * price
            cogs += use * batch["cost"]
            batch["qty"] -= use
            remaining -= use
        # Remove empty batches
        sku.batches = [b for b in sku.batches if b["qty"] > 0]
        # Backorder if not fully satisfied
        if remaining > 0:
            sku.backorders.append({"qty": remaining, "price": price})
        # Reorder check
        units_on_hand = sum(b["qty"] for b in sku.batches)
        if units_on_hand < sku.reorder_point and not sku.in_transit:
            arrival_day = day + LEAD_TIME
            sku.arrival_day = arrival_day
            sku.in_transit = True

    # Simulation days 1..20
    for day in range(1, 21):
        # 1. Expiry
        for sku in skus.values():
            # Identify expired batches
            remaining_batches = []
            for batch in sku.batches:
                if batch["expiry"] < day:
                    write_offs += batch["qty"] * batch["cost"]
                else:
                    remaining_batches.append(batch)
            sku.batches = remaining_batches

        # 2. Arrivals (automatic reorder)
        for sku in skus.values():
            if sku.arrival_day == day:
                process_receive(day, sku, sku.reorder_qty, sku.standard_cost)
                sku.in_transit = False
                sku.arrival_day = None

        # 3. Events
        for event in events_by_day.get(day, []):
            typ, sku_code, qty, price = event
            sku_obj = skus[sku_code]
            if typ == "RECEIVE":
                process_receive(day, sku_obj, qty, price)
            elif typ == "ORDER":
                process_order(day, sku_obj, qty, price)

    # After day 20, apply cancellation penalty to all unfilled backorders
    unfilled_units = sum(bo["qty"] for sku in skus.values() for bo in sku.backorders)
    result = revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_units
    return round(result + 1e-8, 2)  # small epsilon to avoid issues like 0.005 rounding down

# For manual testing (will not be executed in the judge)
if __name__ == "__main__":
    print(run())
