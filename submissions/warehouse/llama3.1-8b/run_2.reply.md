<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:46:06+00:00 -->

```python
from datetime import timedelta

class Product:
    def __init__(self, sku, shelf_life, reorder_point, reorder_qty, standard_cost):
        self.sku = sku
        self.shelf_life = shelf_life
        self.reorder_point = reorder_point
        self.reorder_qty = reorder_qty
        self.standard_cost = standard_cost
        self.stock = []
        self.backorders = []
        self.reorder_in_transit = None

    def receive(self, quantity, unit_cost, expiry_day):
        self.stock.append((quantity, unit_cost, expiry_day))
        self.reorder_in_transit = None

    def backorder(self, quantity, unit_price):
        self.backorders.append((quantity, unit_price))

    def cancel_backorders(self):
        for quantity, _ in self.backorders:
            self.backorders[0] = (self.backorders[0][0] + quantity, self.backorders[0][1])
            self.stock.append((quantity, self.backorders[0][1], None))

    def process_order(self, price, quantity):
        for batch in sorted(self.stock, key=lambda x: x[2]):
            if batch[0] >= quantity:
                quantity_used = min(batch[0], quantity)
                self.stock[0] = (batch[0] - quantity_used, batch[1], batch[2])
                quantity -= quantity_used
                if batch[2] <= current_day:
                    self.write_offs += quantity_used * batch[1]
                else:
                    revenue += quantity_used * price
                    cogs += quantity_used * batch[1]
            else:
                self.backorders.append((batch[0], price))
                quantity -= batch[0]
        if quantity:
            self.backorders.append((quantity, price))

    def reorder(self, day):
        self.reorder_in_transit = (self.reorder_qty, self.standard_cost, day + 2)

def run():
    global revenue, cogs, write_offs, unfilled_backorder_units
    products = {
        'A': Product('A', 5, 8, 20, 4.00),
        'B': Product('B', 30, 5, 10, 12.50),
        'C': Product('C', 3, 4, 12, 2.20),
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
    global revenue, cogs, write_offs, unfilled_backorder_units
    revenue = 0
    cogs = 0
    write_offs = 0
    unfilled_backorder_units = 0
    for current_day in range(1, 21):
        for product in products.values():
            product.cancel_backorders()
        for product in products.values():
            product.reorder(current_day + 2 if product.reorder_in_transit else None)
        for product in products.values():
            if product.reorder_in_transit:
                product.receive(product.reorder_in_transit[0], product.reorder_in_transit[1], product.reorder_in_transit[2])
        for event in events:
            if event[0] <= current_day:
                product = products.get(event[2])
                if event[1] == 'RECEIVE':
                    product.receive(event[3], event[4], current_day)
                elif event[1] == 'ORDER':
                    product.process_order(event[4], event[3])
                else:
                    raise ValueError(f"Invalid event type: {event[1]}")
        for product in products.values():
            for batch in product.stock[:]:
                if batch[2] < current_day:
                    product.stock.remove(batch)
                    write_offs += batch[0] * batch[1]
    for product in products.values():
        unfilled_backorder_units += sum(quantity for quantity, _ in product.backorders)
    revenue -= unfilled_backorder_units * CANCELLATION_PENALTY
    return round(revenue - cogs - write_offs - unfilled_backorder_units * CANCELLATION_PENALTY, 2)

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

print(run())
```