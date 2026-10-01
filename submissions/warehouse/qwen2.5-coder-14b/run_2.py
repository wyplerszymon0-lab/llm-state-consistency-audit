from typing import List, Tuple, Dict, Optional

class Batch:
    def __init__(self, quantity: int, unit_cost: float, expiry_day: int):
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.expiry_day = expiry_day

class Backorder:
    def __init__(self, quantity: int, unit_price: float):
        self.quantity = quantity
        self.unit_price = unit_price

class SKU:
    def __init__(self, shelf_life: int, reorder_point: int, reorder_qty: int, standard_cost: float):
        self.shelf_life = shelf_life
        self.reorder_point = reorder_point
        self.reorder_qty = reorder_qty
        self.standard_cost = standard_cost
        self.batches: List[Batch] = []
        self.backorders: List[Backorder] = []
        self.reorder_in_transit: Optional[int] = None

def run() -> float:
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    skus: Dict[str, SKU] = {
        'A': SKU(5, 8, 20, 4.00),
        'B': SKU(30, 5, 10, 12.50),
        'C': SKU(3, 4, 12, 2.20),
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

    def receive(sku: SKU, quantity: int, unit_cost: float, day: int):
        nonlocal revenue, cogs
        while sku.backorders and quantity > 0:
            backorder = sku.backorders[0]
            fill_quantity = min(quantity, backorder.quantity)
            revenue += fill_quantity * backorder.unit_price * BACKORDER_DISCOUNT
            cogs += fill_quantity * unit_cost
            quantity -= fill_quantity
            backorder.quantity -= fill_quantity
            if backorder.quantity == 0:
                sku.backorders.pop(0)
        if quantity > 0:
            sku.batches.append(Batch(quantity, unit_cost, day + sku.shelf_life))

    def order(sku: SKU, quantity: int, price: float, day: int):
        nonlocal revenue, cogs
        while sku.batches and quantity > 0:
            batch = sku.batches[0]
            if batch.expiry_day < day:
                sku.batches.pop(0)
                continue
            fill_quantity = min(quantity, batch.quantity)
            revenue += fill_quantity * price
            cogs += fill_quantity * batch.unit_cost
            quantity -= fill_quantity
            batch.quantity -= fill_quantity
            if batch.quantity == 0:
                sku.batches.pop(0)
        if quantity > 0:
            sku.backorders.append(Backorder(quantity, price))
        if len(sku.batches) == 0 and sku.reorder_in_transit is None and len(sku.backorders) > 0:
            sku.reorder_in_transit = day + LEAD_TIME

    for day in range(1, 21):
        sku: SKU
        for sku in skus.values():
            # Expiry
            while sku.batches and sku.batches[0].expiry_day < day:
                expired_batch = sku.batches.pop(0)
                write_offs += expired_batch.quantity * expired_batch.unit_cost
            # Arrival
            if sku.reorder_in_transit == day:
                sku.reorder_in_transit = None
                receive(sku, sku.reorder_qty, sku.standard_cost, day)
        # Events
        for day, event_type, sku_id, quantity, price in events:
            if day != day:
                continue
            sku = skus[sku_id]
            if event_type == 'RECEIVE':
                receive(sku, quantity, price, day)
            elif event_type == 'ORDER':
                order(sku, quantity, price, day)

    # Final backorder penalty
    for sku in skus.values():
        for backorder in sku.backorders:
            write_offs += backorder.quantity * CANCELLATION_PENALTY

    return round(revenue - cogs - write_offs, 2)

# Example usage
if __name__ == "__main__":
    print(run())
