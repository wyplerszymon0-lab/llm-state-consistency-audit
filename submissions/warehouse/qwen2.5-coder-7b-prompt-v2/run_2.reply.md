<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T11:44:17+00:00 -->

```python
from collections import defaultdict, deque
from typing import List, Tuple

def run() -> float:
    SKU_A = 'A'
    SKU_B = 'B'
    SKU_C = 'C'
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    product_settings = {
        SKU_A: {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        SKU_B: {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        SKU_C: {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
    }

    events = [
        (1, 'RECEIVE', SKU_A, 30, 3.80),
        (1, 'RECEIVE', SKU_B, 8, 12.00),
        (1, 'RECEIVE', SKU_C, 10, 2.00),
        (2, 'ORDER', SKU_A, 12, 7.50),
        (2, 'ORDER', SKU_C, 4, 4.00),
        (3, 'RECEIVE', SKU_A, 10, 3.90),
        (3, 'ORDER', SKU_B, 6, 20.00),
        (4, 'ORDER', SKU_B, 5, 21.00),
        (4, 'ORDER', SKU_C, 3, 4.20),
        (5, 'ORDER', SKU_A, 15, 7.40),
        (6, 'ORDER', SKU_C, 2, 4.10),
        (7, 'ORDER', SKU_A, 9, 7.60),
        (8, 'ORDER', SKU_A, 5, 7.60),
        (8, 'RECEIVE', SKU_A, 2, 3.95),
        (9, 'ORDER', SKU_C, 11, 4.00),
        (10, 'ORDER', SKU_B, 8, 20.50),
        (10, 'ORDER', SKU_C, 2, 4.00),
        (12, 'ORDER', SKU_A, 10, 7.80),
        (13, 'ORDER', SKU_A, 1, 7.80),
        (14, 'ORDER', SKU_C, 5, 4.30),
        (15, 'ORDER', SKU_C, 3, 4.30),
        (16, 'ORDER', SKU_A, 25, 7.90),
        (18, 'ORDER', SKU_B, 9, 22.00),
        (19, 'ORDER', SKU_B, 4, 22.00),
        (19, 'ORDER', SKU_A, 16, 8.00),
        (20, 'ORDER', SKU_C, 10, 4.50)
    ]

    def process_day(day: int):
        nonlocal revenue, cogs, write_offs
        # Expiry
        for sku, batches in stock.items():
            new_batches = []
            for batch in batches:
                if batch[2] >= day:
                    new_batches.append(batch)
                else:
                    write_offs += batch[0] * batch[1]
            stock[sku] = new_batches
        # Arrivals
        if day in reorder_in_transit:
            sku, quantity = reorder_in_transit[day]
            stock[sku].append((quantity, product_settings[sku]['standard_cost'], day + product_settings[sku]['shelf_life']))
            del reorder_in_transit[day]
        # Events
        for event in events:
            if event[0] == day:
                event_type, sku, quantity, price = event
                if event_type == 'RECEIVE':
                    fill_backorders(sku, quantity, price)
                elif event_type == 'ORDER':
                    fill_order(sku, quantity, price)

    def fill_backorders(sku: str, quantity: int, price: float):
        nonlocal revenue, cogs
        while quantity > 0 and backorders[sku]:
            backorder_quantity, backorder_price = backorders[sku][0]
            if quantity >= backorder_quantity:
                quantity -= backorder_quantity
                revenue += backorder_quantity * backorder_price * BACKORDER_DISCOUNT
                cogs += backorder_quantity * product_settings[sku]['standard_cost']
                backorders[sku].popleft()
            else:
                backorders[sku][0] = (backorder_quantity - quantity, backorder_price)
                quantity = 0

    def fill_order(sku: str, quantity: int, price: float):
        nonlocal revenue, cogs, backorders
        filled = 0
        for batch in sorted(stock[sku], key=lambda x: (x[2], stock[sku].index(x))):
            if batch[0] > quantity - filled:
                batch[0] -= quantity - filled
                filled = quantity
                revenue += (quantity - filled) * price
                cogs += (quantity - filled) * batch[1]
                break
            else:
                filled += batch[0]
                revenue += batch[0] * price
                cogs += batch[0] * batch[1]
                stock[sku].remove(batch)
        if filled < quantity:
            backorders[sku].append((quantity - filled, price))

    stock = defaultdict(list)
    backorders = defaultdict(deque)
    reorder_in_transit = {}
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    for day in range(1, 21):
        process_day(day)

    unfilled_backorder_units = sum(quantity for quantity, _ in backorders.values())
    answer = round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)
    return answer

print(run())
```