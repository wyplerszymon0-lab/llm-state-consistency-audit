<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:46:43+00:00 -->

```python
from collections import namedtuple
from typing import Dict, List

Event = namedtuple('Event', ['day', 'type', 'sku', 'quantity', 'price'])
Batch = namedtuple('Batch', ['quantity', 'unit_cost', 'expiry_day'])
Backorder = namedtuple('Backorder', ['quantity', 'unit_price'])
Product = namedtuple('Product', ['reorder_point', 'reorder_qty', 'standard_cost'])

def run() -> float:
    products = {
        'A': Product(8, 20, 4.00),
        'B': Product(5, 10, 12.50),
        'C': Product(4, 12, 2.20),
    }
    events: List[Event] = [
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
        Event(20, 'ORDER', 'C', 10, 4.50),
    ]
    state = {
        sku: [
            Batch(quantity, standard_cost, day + products[sku].shelf_life)
            for quantity, standard_cost, day in [
                (30, 3.80, 1),
                (8, 12.00, 1),
                (10, 2.00, 1),
                (12, 7.50, 2),
                (4, 4.00, 2),
                (10, 3.90, 3),
                (6, 20.00, 3),
                (5, 21.00, 4),
                (3, 4.20, 4),
                (15, 7.40, 5),
                (2, 4.10, 6),
                (9, 7.60, 7),
                (5, 7.60, 8),
                (2, 3.95, 8),
                (11, 4.00, 9),
                (8, 20.50, 10),
                (2, 4.00, 10),
                (10, 7.80, 12),
                (1, 7.80, 13),
                (5, 4.30, 14),
                (3, 4.30, 15),
                (25, 7.90, 16),
                (9, 22.00, 18),
                (4, 22.00, 19),
                (16, 8.00, 19),
                (10, 4.50, 20),
            ]
        ]
        for sku in products
    }
    reorder_in_transit = {sku: None for sku in products}
    revenue, cogs, write_offs, unfilled_backorder_units = 0, 0, 0, 0
    for _ in range(20):
        # Expiry
        for sku, batches in state.items():
            state[sku] = [batch for batch in batches if batch.expiry_day > _]
            write_offs += sum(batch.quantity * batch.unit_cost for batch in batches if batch.expiry_day <= _)

        # Arrivals
        sku = reorder_in_transit[_ % 2]
        if sku is not None:
            state[sku].append(Batch(products[sku].reorder_qty, products[sku].standard_cost, _ + products[sku].reorder_point + 2))
            reorder_in_transit[_ % 2] = None

        # Events
        for event in events[_-1:]:
            if event.day <= _:
                continue
            sku = event.sku
            if event.type == 'RECEIVE' or reorder_in_transit[_ % 2] == sku:
                # Receiving (RECEIVE events and reorder arrivals)
                if reorder_in_transit[_ % 2] == sku:
                    reorder_in_transit[_ % 2] = sku
                for batch in state[sku][:]:
                    if batch.quantity > event.quantity:
                        state[sku].remove(batch)
                        event.quantity -= batch.quantity
                    else:
                        state[sku].remove(batch)
                        event.quantity -= batch.quantity
                        batch.quantity -= batch.quantity
                        if event.quantity == 0:
                            break
                state[sku].append(Batch(event.quantity, event.price, _))
                if event.price > products[sku].standard_cost:
                    revenue += event.quantity * event.price * products[sku].BACKORDER_DISCOUNT
                    cogs += event.quantity * products[sku].standard_cost
            elif event.type == 'ORDER':
                # Customer orders (ORDER events)
                quantity_filled = 0
                for batch in sorted(state[sku], key=lambda batch: batch.expiry_day):
                    if batch.quantity > event.quantity:
                        state[sku].remove(batch)
                        quantity_filled += min(batch.quantity, event.quantity)
                        event.quantity -= min(batch.quantity, event.quantity)
                        batch.quantity -= min(batch.quantity, event.quantity)
                        if event.quantity == 0:
                            break
                revenue += event.quantity * event.price
                cogs += quantity_filled * event.price
                if event.quantity > 0:
                    state[sku].append(Backorder(event.quantity, event.price))
            # Reorder check
            if state[sku][0].quantity <= products[sku].reorder_point and reorder_in_transit[_ % 2] != sku:
                reorder_in_transit[_ % 2] = sku
    # Cancellation penalty for backorders
    for sku, backorders in state.items():
        unfilled_backorder_units += sum(backorder.quantity for backorder in backorders if isinstance(backorder, Backorder))
    return round(revenue - cogs - write_offs - unfilled_backorder_units * products['A'].CANCELLATION_PENALTY, 2)

print(run())
```