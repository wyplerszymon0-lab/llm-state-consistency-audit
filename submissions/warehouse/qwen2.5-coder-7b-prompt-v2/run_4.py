from collections import deque, namedtuple
from typing import List, Tuple

class Batch(namedtuple('Batch', ['quantity', 'unit_cost', 'expiry_day'])):
    pass

class Backorder(namedtuple('Backorder', ['quantity', 'unit_price'])):
    pass

def run() -> float:
    SKU = namedtuple('SKU', ['shelf_life', 'reorder_point', 'reorder_qty', 'standard_cost'])
    products = {
        'A': SKU(5, 8, 20, 4.00),
        'B': SKU(30, 5, 10, 12.50),
        'C': SKU(3, 4, 12, 2.20)
    }
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    def process_day(day: int, events: List[Tuple[str, str, str, int, float]]) -> None:
        nonlocal revenue, cogs, write_offs, stock, backorders, reorder_in_transit

        # Expiry
        while stock and stock[0].expiry_day < day:
            batch = stock.popleft()
            write_offs += batch.quantity * batch.unit_cost

        # Arrivals
        if reorder_in_transit is None and day in products:
            reorder_in_transit = (day + LEAD_TIME, products[day].reorder_qty, products[day].standard_cost)

        # Events
        for event_type, sku, _, quantity, price in events:
            if event_type == 'RECEIVE':
                batch = Batch(quantity, price, day + products[sku].shelf_life)
                while backorders and backorders[0].quantity <= batch.quantity:
                    backorder = backorders.popleft()
                    revenue += backorder.quantity * backorder.unit_price * BACKORDER_DISCOUNT
                    cogs += backorder.quantity * batch.unit_cost
                    batch.quantity -= backorder.quantity
                if batch.quantity > 0:
                    stock.append(batch)
            elif event_type == 'ORDER':
                filled = 0
                while stock and filled < quantity:
                    batch = stock[0]
                    if batch.expiry_day >= day:
                        if batch.quantity > quantity - filled:
                            batch.quantity -= quantity - filled
                            filled = quantity
                            revenue += (quantity - filled) * price
                            cogs += (quantity - filled) * batch.unit_cost
                        else:
                            filled += batch.quantity
                            revenue += batch.quantity * price
                            cogs += batch.quantity * batch.unit_cost
                            stock.popleft()
                if filled < quantity:
                    backorders.append(Backorder(quantity - filled, price))
                if (stock and stock[0].expiry_day >= day) or reorder_in_transit:
                    if reorder_in_transit is None and day in products:
                        reorder_in_transit = (day + LEAD_TIME, products[sku].reorder_qty, products[sku].standard_cost)

        # Reorder check
        if reorder_in_transit is None and day in products and stock[0].quantity < products[sku].reorder_point:
            reorder_in_transit = (day + LEAD_TIME, products[sku].reorder_qty, products[sku].standard_cost)

    # Initialize state
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0
    stock: List[Batch] = []
    backorders: List[Backorder] = []
    reorder_in_transit = None

    # Process events
    events = [
        ('RECEIVE', 'A', '', 30, 3.80),
        ('RECEIVE', 'B', '', 8, 12.00),
        ('RECEIVE', 'C', '', 10, 2.00),
        ('ORDER', 'A', '', 12, 7.50),
        ('ORDER', 'C', '', 4, 4.00),
        ('RECEIVE', 'A', '', 10, 3.90),
        ('ORDER', 'B', '', 6, 20.00),
        ('ORDER', 'B', '', 5, 21.00),
        ('ORDER', 'C', '', 3, 4.20),
        ('ORDER', 'A', '', 15, 7.40),
        ('ORDER', 'C', '', 2, 4.10),
        ('ORDER', 'A', '', 9, 7.60),
        ('ORDER', 'A', '', 5, 7.60),
        ('RECEIVE', 'A', '', 2, 3.95),
        ('ORDER', 'C', '', 11, 4.00),
        ('ORDER', 'B', '', 8, 20.50),
        ('ORDER', 'C', '', 2, 4.00),
        ('ORDER', 'A', '', 10, 7.80),
        ('ORDER', 'A', '', 1, 7.80),
        ('ORDER', 'C', '', 5, 4.30),
        ('ORDER', 'C', '', 3, 4.30),
        ('ORDER', 'A', '', 25, 7.90),
        ('ORDER', 'B', '', 9, 22.00),
        ('ORDER', 'B', '', 4, 22.00),
        ('ORDER', 'A', '', 16, 8.00),
        ('ORDER', 'C', '', 10, 4.50)
    ]
    events.sort(key=lambda e: e[0])
    for day in range(1, 21):
        process_day(day, [e for e in events if e[0] == str(day)])

    # Calculate final answer
    unfilled_backorder_units = sum(backorder.quantity for backorder in backorders)
    return round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

print(run())
