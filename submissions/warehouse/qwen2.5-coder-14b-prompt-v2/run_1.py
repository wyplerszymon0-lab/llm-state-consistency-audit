from typing import List, Tuple, Set, Dict, Deque
from collections import deque

class Batch:
    def __init__(self, quantity: int, unit_cost: float, expiry_day: int):
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.expiry_day = expiry_day

class SKU:
    def __init__(self, shelf_life: int, reorder_point: int, reorder_qty: int, standard_cost: float):
        self.shelf_life = shelf_life
        self.reorder_point = reorder_point
        self.reorder_qty = reorder_qty
        self.standard_cost = standard_cost
        self.batches: Set[Batch] = set()
        self.backorders: Deque[Tuple[int, float]] = deque()
        self.in_transit = False

def run() -> float:
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    products = {
        'A': SKU(shelf_life=5, reorder_point=8, reorder_qty=20, standard_cost=4.00),
        'B': SKU(shelf_life=30, reorder_point=5, reorder_qty=10, standard_cost=12.50),
        'C': SKU(shelf_life=3, reorder_point=4, reorder_qty=12, standard_cost=2.20),
    }

    events = [
        (1, 'RECEIVE', 'A', 30, 3.80),
        (1, 'RECEIVE', 'B', 8, 12.00),
        (1, 'RECEIVE', 'C', 10, 2.00),
        (2, 'ORDER', 'A', 12, 7.50),
        (2, 'ORDER', 'C', 4, 4.00),
        (3, 'RECEIVE', 'A', 10, 3.90),
        (3, 'ORDER', 'B', 6, 20.00),
        (4, 'ORDER', 'B', 5, 21.00),
        (4, 'ORDER', 'C', 3, 4.20),
        (5, 'ORDER', 'A', 15, 7.40),
        (6, 'ORDER', 'C', 2, 4.10),
        (7, 'ORDER', 'A', 9, 7.60),
        (8, 'ORDER', 'A', 5, 7.60),
        (8, 'RECEIVE', 'A', 2, 3.95),
        (9, 'ORDER', 'C', 11, 4.00),
        (10, 'ORDER', 'B', 8, 20.50),
        (10, 'ORDER', 'C', 2, 4.00),
        (12, 'ORDER', 'A', 10, 7.80),
        (13, 'ORDER', 'A', 1, 7.80),
        (14, 'ORDER', 'C', 5, 4.30),
        (15, 'ORDER', 'C', 3, 4.30),
        (16, 'ORDER', 'A', 25, 7.90),
        (18, 'ORDER', 'B', 9, 22.00),
        (19, 'ORDER', 'B', 4, 22.00),
        (19, 'ORDER', 'A', 16, 8.00),
        (20, 'ORDER', 'C', 10, 4.50),
    ]

    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    for day in range(1, 21):
        for sku in products.values():
            # Expiry
            sku.batches = {batch for batch in sku.batches if batch.expiry_day >= day}
            write_offs += sum(batch.quantity * batch.unit_cost for batch in sku.batches if batch.expiry_day < day)
            
            # Arrivals
            if sku.in_transit:
                sku.batches.add(Batch(sku.reorder_qty, sku.standard_cost, day + sku.shelf_life))
                sku.in_transit = False

        for event_day, event_type, sku_name, quantity, price in events:
            if event_day == day:
                sku = products[sku_name]
                if event_type == 'RECEIVE':
                    # Fill backorders
                    while sku.backorders and quantity > 0:
                        back_quantity, back_price = sku.backorders.popleft()
                        fill_quantity = min(back_quantity, quantity)
                        revenue += fill_quantity * back_price * BACKORDER_DISCOUNT
                        cogs += fill_quantity * sku.standard_cost
                        quantity -= fill_quantity
                        if fill_quantity < back_quantity:
                            sku.backorders.appendleft((back_quantity - fill_quantity, back_price))
                    
                    # Add new batch
                    if quantity > 0:
                        sku.batches.add(Batch(quantity, sku.standard_cost, day + sku.shelf_life))
                elif event_type == 'ORDER':
                    # Fill from batches
                    while sku.batches and quantity > 0:
                        batch = min(sku.batches, key=lambda b: (b.expiry_day, b))
                        fill_quantity = min(batch.quantity, quantity)
                        revenue += fill_quantity * price
                        cogs += fill_quantity * batch.unit_cost
                        quantity -= fill_quantity
                        batch.quantity -= fill_quantity
                        if batch.quantity == 0:
                            sku.batches.remove(batch)
                    
                    # Add backorder
                    if quantity > 0:
                        sku.backorders.append((quantity, price))
                    
                    # Reorder check
                    if sum(batch.quantity for batch in sku.batches) < sku.reorder_point and not sku.in_transit:
                        sku.in_transit = True

    # Cancellation penalties
    for sku in products.values():
        for back_quantity, _ in sku.backorders:
            write_offs += back_quantity * CANCELLATION_PENALTY

    return round(revenue - cogs - write_offs, 2)

# Example usage
if __name__ == "__main__":
    print(run())
