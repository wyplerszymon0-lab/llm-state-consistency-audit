#!/usr/bin/env python3
"""
Simulation of a perishable warehouse.
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple

# ---------- Configuration ----------
SKU_CONFIG = {
    "A": {"shelf_life": 5, "reorder_point": 8, "reorder_qty": 20, "standard_cost": 4.00},
    "B": {"shelf_life": 30, "reorder_point": 5, "reorder_qty": 10, "standard_cost": 12.50},
    "C": {"shelf_life": 3, "reorder_point": 4, "reorder_qty": 12, "standard_cost": 2.20},
}
LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00
END_DAY = 20

EVENT_STR = """1, RECEIVE, A, 30, 3.80
1, RECEIVE, B, 8, 12.00
1, RECEIVE, C, 10, 2.00
2, ORDER, A, 12, 7.50
2, ORDER, C, 4, 4.00
3, RECEIVE, A, 10, 3.90
3, ORDER, B, 6, 20.00
4, ORDER, B, 5, 21.00
4, ORDER, C, 3, 4.20
5, ORDER, A, 15, 7.40
6, ORDER, C, 2, 4.10
7, ORDER, A, 9, 7.60
8, ORDER, A, 5, 7.60
8, RECEIVE, A, 2, 3.95
9, ORDER, C, 11, 4.00
10, ORDER, B, 8, 20.50
10, ORDER, C, 2, 4.00
12, ORDER, A, 10, 7.80
13, ORDER, A, 1, 7.80
14, ORDER, C, 5, 4.30
15, ORDER, C, 3, 4.30
16, ORDER, A, 25, 7.90
18, ORDER, B, 9, 22.00
19, ORDER, B, 4, 22.00
19, ORDER, A, 16, 8.00
20, ORDER, C, 10, 4.50"""

# ---------- Simulation helpers ----------

class SKUState:
    def __init__(self, sku: str):
        cfg = SKU_CONFIG[sku]
        self.sku = sku
        self.shelf_life = cfg["shelf_life"]
        self.reorder_point = cfg["reorder_point"]
        self.reorder_qty = cfg["reorder_qty"]
        self.standard_cost = cfg["standard_cost"]

        # batches: list of [qty, unit_cost, expiry_day, received_day]
        self.batches: List[Tuple[int, float, int, int]] = []

        # backorders: deque of [qty, unit_price]
        self.backorders: deque[Tuple[int, float]] = deque()

        # reorder in transit: arrival_day or None
        self.reorder_arrival: int | None = None

    def expiry_and_cleanup(self, day: int, write_offs: List[float]) -> None:
        """Remove expired batches and add to write_offs."""
        new_batches = []
        for qty, unit_cost, expiry_day, received_day in self.batches:
            if expiry_day < day:
                write_offs[0] += qty * unit_cost
            else:
                new_batches.append((qty, unit_cost, expiry_day, received_day))
        self.batches = new_batches

    def receive(self, qty: int, unit_cost: float, day: int,
                revenue: List[float], cogs: List[float]) -> None:
        """Process incoming goods."""
        # First, fill backorders
        while qty > 0 and self.backorders:
            bo_qty, bo_price = self.backorders[0]
            if qty >= bo_qty:
                # fill entire backorder
                revenue[0] += bo_price * BACKORDER_DISCOUNT * bo_qty
                cogs[0] += unit_cost * bo_qty
                qty -= bo_qty
                self.backorders.popleft()
            else:
                # partial fill
                revenue[0] += bo_price * BACKORDER_DISCOUNT * qty
                cogs[0] += unit_cost * qty
                self.backorders[0] = (bo_qty - qty, bo_price)
                qty = 0
        # Remaining qty becomes a new batch
        if qty > 0:
            expiry_day = day + self.shelf_life
            self.batches.append((qty, unit_cost, expiry_day, day))
            # keep batches sorted by (expiry_day, received_day)
            self.batches.sort(key=lambda x: (x[2], x[3]))

    def fulfill_order(self, qty_needed: int, order_price: float,
                      revenue: List[float], cogs: List[float]) -> None:
        """Attempt to fulfill order from on‑hand batches."""
        remaining = qty_needed
        # iterate over batches in order
        i = 0
        while remaining > 0 and i < len(self.batches):
            qty, unit_cost, expiry_day, received_day = self.batches[i]
            if qty <= 0:
                i += 1
                continue
            if qty <= remaining:
                # consume entire batch
                revenue[0] += order_price * qty
                cogs[0] += unit_cost * qty
                remaining -= qty
                self.batches[i] = (0, unit_cost, expiry_day, received_day)
                i += 1
            else:
                # consume part
                revenue[0] += order_price * remaining
                cogs[0] += unit_cost * remaining
                self.batches[i] = (qty - remaining, unit_cost, expiry_day, received_day)
                remaining = 0
        # remove empty batches
        self.batches = [b for b in self.batches if b[0] > 0]
        # any unfilled become backorder
        if remaining > 0:
            self.backorders.append((remaining, order_price))

    def total_on_hand(self) -> int:
        return sum(qty for qty, _, _, _ in self.batches)

    def check_and_place_reorder(self, day: int) -> None:
        """After an order, check for reorder."""
        if self.total_on_hand() < self.reorder_point and self.reorder_arrival is None:
            arrival = day + LEAD_TIME
            if arrival <= END_DAY:
                self.reorder_arrival = arrival
            else:
                # reorder would arrive after simulation, ignore
                pass

# ---------- Main simulation function ----------

def run() -> float:
    # Parse events
    events_by_day: Dict[int, List[Tuple[str, str, int, float]]] = defaultdict(list)
    for line in EVENT_STR.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        day = int(parts[0])
        typ = parts[1]
        sku = parts[2]
        quantity = int(parts[3])
        price = float(parts[4])
        events_by_day[day].append((typ, sku, quantity, price))

    # Initialize SKU states
    sku_states: Dict[str, SKUState] = {sku: SKUState(sku) for sku in SKU_CONFIG}

    # Totals
    revenue = [0.0]
    cogs = [0.0]
    write_offs = [0.0]

    # Simulate days
    for day in range(1, END_DAY + 1):
        # 1. Expiry
        for sku_state in sku_states.values():
            sku_state.expiry_and_cleanup(day, write_offs)

        # 2. Arrivals
        for sku_state in sku_states.values():
            arrival_day = sku_state.reorder_arrival
            if arrival_day == day:
                # receive reorder
                sku_state.receive(
                    sku_state.reorder_qty,
                    sku_state.standard_cost,
                    day,
                    revenue,
                    cogs
                )
                sku_state.reorder_arrival = None

        # 3. Events
        for typ, sku, qty, price in events_by_day.get(day, []):
            sku_state = sku_states[sku]
            if typ == "RECEIVE":
                sku_state.receive(qty, price, day, revenue, cogs)
            elif typ == "ORDER":
                sku_state.fulfill_order(qty, price, revenue, cogs)
                sku_state.check_and_place_reorder(day)

    # After day 20, cancel all backorders
    unfilled_units = sum(q for sku_state in sku_states.values() for q, _ in sku_state.backorders)
    cancellation_cost = unfilled_units * CANCELLATION_PENALTY

    result = revenue[0] - cogs[0] - write_offs[0] - cancellation_cost
    return round(result + 1e-8, 2)  # small epsilon to avoid negative zero

# When run as a script, print the result
if __name__ == "__main__":
    print(run())
