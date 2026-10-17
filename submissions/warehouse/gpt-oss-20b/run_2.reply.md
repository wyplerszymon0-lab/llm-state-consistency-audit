<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T11:01:24+00:00 -->

```python
import collections
from typing import List, Tuple

def run() -> float:
    # Product configuration
    products = {
        "A": {"shelf_life": 5, "reorder_point": 8, "reorder_qty": 20, "standard_cost": 4.00},
        "B": {"shelf_life": 30, "reorder_point": 5, "reorder_qty": 10, "standard_cost": 12.50},
        "C": {"shelf_life": 3,  "reorder_point": 4, "reorder_qty": 12, "standard_cost": 2.20},
    }

    # Constants
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    # Events (day, type, sku, quantity, price)
    raw_events: List[Tuple[int, str, str, int, float]] = [
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

    # Organise events per day
    events_by_day: dict[int, List[Tuple[str, str, int, float]]] = {}
    for day, ev_type, sku, qty, price in raw_events:
        events_by_day.setdefault(day, []).append((ev_type, sku, qty, price))

    # State per SKU
    skus = {}
    for sku in products:
        skus[sku] = {
            "batches": [],          # list of [qty, unit_cost, expiry_day, received_day]
            "backorders": collections.deque(),  # deque of [qty, unit_price]
            "reorder_arrival": None,  # arrival day of pending reorder or None
        }

    # Totals
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    # Helper functions
    def handle_receive(day: int, sku: str, qty: int, unit_cost: float):
        nonlocal revenue, cogs
        backorders = skus[sku]["backorders"]
        batches = skus[sku]["batches"]
        # Fill backorders first
        while qty > 0 and backorders:
            back_qty, back_price = backorders[0]
            take = qty if qty < back_qty else back_qty
            revenue += back_price * BACKORDER_DISCOUNT * take
            cogs += unit_cost * take
            if take == back_qty:
                backorders.popleft()
            else:
                backorders[0][0] -= take
            qty -= take
        # Remaining becomes a new batch
        if qty > 0:
            expiry = day + products[sku]["shelf_life"]
            batches.append([qty, unit_cost, expiry, day])

    def fill_order(day: int, sku: str, qty: int, price: float) -> int:
        """Attempt to fill from on-hand batches. Return unfilled quantity."""
        nonlocal revenue, cogs
        batches = skus[sku]["batches"]
        remaining = qty
        while remaining > 0 and batches:
            # find earliest batch (by expiry then received)
            idx = min(range(len(batches)), key=lambda i: (batches[i][2], batches[i][3]))
            batch = batches[idx]
            take = remaining if remaining < batch[0] else batch[0]
            revenue += price * take
            cogs += batch[1] * take
            batch[0] -= take
            if batch[0] == 0:
                batches.pop(idx)
            remaining -= take
        return remaining

    def reorder_check(day: int, sku: str):
        nonlocal skus
        if skus[sku]["reorder_arrival"] is not None:
            return
        on_hand = sum(batch[0] for batch in skus[sku]["batches"])
        if on_hand < products[sku]["reorder_point"]:
            arrival = day + LEAD_TIME
            if arrival <= 20:
                skus[sku]["reorder_arrival"] = arrival
            # else: ignore, will never arrive

    # Main simulation loop
    for day in range(1, 21):
        # 1. Expiry
        for sku in products:
            batches = skus[sku]["batches"]
            # iterate over copy to allow removal
            new_batches = []
            for qty, unit_cost, expiry, received in batches:
                if expiry < day:
                    write_offs += qty * unit_cost
                else:
                    new_batches.append([qty, unit_cost, expiry, received])
            skus[sku]["batches"] = new_batches

        # 2. Arrivals from reorder
        for sku in products:
            arrival_day = skus[sku]["reorder_arrival"]
            if arrival_day == day:
                qty = products[sku]["reorder_qty"]
                unit_cost = products[sku]["standard_cost"]
                handle_receive(day, sku, qty, unit_cost)
                skus[sku]["reorder_arrival"] = None

        # 3. Events
        for ev_type, sku, qty, price in events_by_day.get(day, []):
            if ev_type == "RECEIVE":
                handle_receive(day, sku, qty, price)
            elif ev_type == "ORDER":
                unfilled = fill_order(day, sku, qty, price)
                if unfilled > 0:
                    skus[sku]["backorders"].append([unfilled, price])
                reorder_check(day, sku)

    # After day 20: compute remaining backorder penalty
    unfilled_units = sum(q for sku in products for q, _ in skus[sku]["backorders"])
    result = revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_units
    return round(result, 2)

# If executed as a script, print the answer (optional)
if __name__ == "__main__":
    print(run())
```