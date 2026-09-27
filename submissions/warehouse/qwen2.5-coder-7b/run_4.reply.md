<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:21:30+00:00 -->

```python
from collections import deque, namedtuple
from typing import List, Tuple

Product = namedtuple('Product', ['sku', 'shelf_life', 'reorder_point', 'reorder_qty', 'standard_cost'])
Event = namedtuple('Event', ['day', 'type', 'sku', 'quantity', 'price'])

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

def run() -> float:
    products = {
        'A': Product('A', 5, 8, 20, 4.00),
        'B': Product('B', 30, 5, 10, 12.50),
        'C': Product('C', 3, 4, 12, 2.20)
    }
    events = [
        Event(1, 'RECEIVE', 'A', 30, 3.80),
        Event(1, 'RECEIVE', 'B', 8, 12.00),
        Event(1, 'RECEIVE', 'C', 10, 2.00),
        Event(2, 'ORDER', 'A', 12, 7.50),
        Event(2, 'ORDER', 'C', 4, 4.00),
        Event(3, 'RECEIVE', 'A', 10, 3.90),
        Event(3, 'ORDER', 'B', 6, 20.00),
        Event(4, 'ORDER', 'B', 5, 21.00),
        Event(4, 'ORDER', 'C', 3, 4.20),
        Event(5, 'ORDER', 'A', 15, 7.40),
        Event(6, 'ORDER', 'C', 2, 4.10),
        Event(7, 'ORDER', 'A', 9, 7.60),
        Event(8, 'ORDER', 'A', 5, 7.60),
        Event(8, 'RECEIVE', 'A', 2, 3.95),
        Event(9, 'ORDER', 'C', 11, 4.00),
        Event(10, 'ORDER', 'B', 8, 20.50),
        Event(10, 'ORDER', 'C', 2, 4.00),
        Event(12, 'ORDER', 'A', 10, 7.80),
        Event(13, 'ORDER', 'A', 1, 7.80),
        Event(14, 'ORDER', 'C', 5, 4.30),
        Event(15, 'ORDER', 'C', 3, 4.30),
        Event(16, 'ORDER', 'A', 25, 7.90),
        Event(18, 'ORDER', 'B', 9, 22.00),
        Event(19, 'ORDER', 'B', 4, 22.00),
        Event(19, 'ORDER', 'A', 16, 8.00),
        Event(20, 'ORDER', 'C', 10, 4.50)
    ]

    stock = {sku: [] for sku in products}
    backorders = {sku: deque() for sku in products}
    reorder_in_transit = {sku: None for sku in products}
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    def remove_expired_batches(sku):
        nonlocal write_offs
        while stock[sku] and stock[sku][0][2] < day:
            batch = stock[sku].pop(0)
            write_offs += batch[0] * batch[1]

    def process_backorders(sku, quantity, price):
        nonlocal revenue, cogs
        while backorders[sku] and quantity > 0:
            backorder = backorders[sku].popleft()
            filled_quantity = min(quantity, backorder[0])
            revenue += filled_quantity * backorder[1] * BACKORDER_DISCOUNT
            cogs += filled_quantity * backorders[sku][0][1]
            quantity -= filled_quantity
        if quantity > 0:
            backorders[sku].append((quantity, price))

    def process_order(sku, quantity, price):
        nonlocal revenue, cogs
        total_filled = 0
        for batch in sorted(stock[sku], key=lambda x: (x[2], x[3])):
            filled_quantity = min(quantity, batch[0])
            total_filled += filled_quantity
            revenue += filled_quantity * price
            cogs += filled_quantity * batch[1]
            batch[0] -= filled_quantity
            if batch[0] == 0:
                stock[sku].remove(batch)
        unfilled_quantity = quantity - total_filled
        if unfilled_quantity > 0:
            backorders[sku].append((unfilled_quantity, price))

    def place_reorder(sku, day):
        nonlocal reorder_in_transit
        reorder_in_transit[sku] = day + LEAD_TIME
        stock[sku].append([products[sku].reorder_qty, products[sku].standard_cost, day + products[sku].shelf_life])

    for day in range(1, 21):
        remove_expired_batches('A')
        remove_expired_batches('B')
        remove_expired_batches('C')

        if reorder_in_transit['A'] == day:
            place_reorder('A', day)
            reorder_in_transit['A'] = None
        if reorder_in_transit['B'] == day:
            place_reorder('B', day)
            reorder_in_transit['B'] = None
        if reorder_in_transit['C'] == day:
            place_reorder('C', day)
            reorder_in_transit['C'] = None

        for event in events:
            if event.day == day:
                if event.type == 'RECEIVE':
                    process_backorders(event.sku, event.quantity, event.price)
                    if backorders[event.sku]:
                        continue
                    stock[event.sku].append([event.quantity, event.price, day + products[event.sku].shelf_life])
                elif event.type == 'ORDER':
                    process_order(event.sku, event.quantity, event.price)

        for sku in products:
            if stock[sku]:
                if stock[sku][-1][0] < products[sku].reorder_point and reorder_in_transit[sku] is None:
                    place_reorder(sku, day)

    unfilled_backorder_units = sum(backorder[0] for backorder in backorders['A']) + \
                                sum(backorder[0] for backorder in backorders['B']) + \
                                sum(backorder[0] for backorder in backorders['C'])

    return round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

print(run())
```