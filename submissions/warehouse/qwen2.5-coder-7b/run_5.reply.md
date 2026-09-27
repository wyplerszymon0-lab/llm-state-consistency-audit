<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:21:57+00:00 -->

```python
from collections import deque, namedtuple

Product = namedtuple('Product', ['sku', 'shelf_life', 'reorder_point', 'reorder_qty', 'standard_cost'])
Event = namedtuple('Event', ['day', 'type', 'sku', 'quantity', 'price'])
Batch = namedtuple('Batch', ['quantity', 'unit_cost', 'expiry_day'])
Backorder = namedtuple('Backorder', ['quantity', 'unit_price'])

def run() -> float:
    products = {
        'A': Product('A', 5, 8, 20, 4.00),
        'B': Product('B', 30, 5, 10, 12.50),
        'C': Product('C', 3, 4, 12, 2.20)
    }
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    def process_receives(day, events):
        for event in events:
            if event.type == 'RECEIVE':
                product = products[event.sku]
                quantity, unit_cost = event.quantity, event.price
                for _ in range(quantity):
                    expiry_day = day + product.shelf_life
                    backorders = product.backorders
                    if backorders and backorders[0].quantity > 0:
                        backorder = backorders.popleft()
                        filled_quantity = min(backorder.quantity, 1)
                        revenue += backorder.unit_price * BACKORDER_DISCOUNT * filled_quantity
                        cogs += unit_cost * filled_quantity
                        backorders.append(Backorder(backorder.quantity - filled_quantity, backorder.unit_price))
                    else:
                        break
                if product.backorders and product.backorders[0].quantity == 0:
                    product.backorders.popleft()
                product.stock.append(Batch(1, unit_cost, expiry_day))

    def process_orders(day, events):
        for event in events:
            if event.type == 'ORDER':
                product = products[event.sku]
                quantity, price = event.quantity, event.price
                filled_quantity = 0
                for batch in product.stock:
                    if batch.expiry_day >= day:
                        if batch.quantity >= quantity - filled_quantity:
                            filled_quantity = quantity
                            cogs += batch.unit_cost * (quantity - filled_quantity)
                            revenue += price * (quantity - filled_quantity)
                            batch.quantity -= (quantity - filled_quantity)
                            break
                        else:
                            filled_quantity += batch.quantity
                            cogs += batch.unit_cost * batch.quantity
                            revenue += price * batch.quantity
                            batch.quantity = 0
                if filled_quantity < quantity:
                    unfilled_quantity = quantity - filled_quantity
                    product.backorders.append(Backorder(unfilled_quantity, price))

    def reorder_check(day, product):
        if product.stock and product.stock[-1].expiry_day < day and product.stock[-1].quantity < product.reorder_point:
            product.reorder_in_transit = True

    def process_day(day, events):
        events.sort(key=lambda x: x.day)
        process_receives(day, events)
        process_orders(day, events)
        reorder_check(day, products['A'])
        reorder_check(day, products['B'])
        reorder_check(day, products['C'])
        remove_expired_batches(day)

    def remove_expired_batches(day):
        for product in products.values():
            product.stock = [batch for batch in product.stock if batch.expiry_day >= day]

    revenue, cogs, write_offs = 0.0, 0.0, 0.0
    for day in range(1, 21):
        events = [event for event in events if event.day == day]
        process_day(day, events)

    unfilled_backorder_units = sum(backorder.quantity for product in products.values() for backorder in product.backorders)
    answer = revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units
    return round(answer, 2)

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

print(run())
```