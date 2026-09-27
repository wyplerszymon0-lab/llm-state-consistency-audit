<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:47:10+00:00 -->

```python
from typing import List, Tuple, Dict

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

class Product:
    def __init__(self, sku, shelf_life, reorder_point, reorder_qty, standard_cost):
        self.sku = sku
        self.shelf_life = shelf_life
        self.reorder_point = reorder_point
        self.reorder_qty = reorder_qty
        self.standard_cost = standard_cost
        self.stock = []
        self.backorders = []
        self.in_transit = False

    def add_batch(self, quantity, unit_cost, expiry_day):
        self.stock.append((quantity, unit_cost, expiry_day))

    def remove_expired_batches(self, day):
        self.stock = [(quantity, unit_cost, expiry_day) for quantity, unit_cost, expiry_day in self.stock if expiry_day >= day]

    def fill_backorders(self, quantity, unit_cost):
        while self.backorders and self.backorders[0][0] <= quantity:
            quantity -= self.backorders[0][0]
            revenue += self.backorders[0][1] * BACKORDER_DISCOUNT
            cogs += self.backorders[0][1] * unit_cost
            self.backorders.pop(0)
        if quantity:
            self.stock.append((quantity, unit_cost, 0))  # dummy expiry day

    def place_reorder(self, day):
        if not self.in_transit and self.quantity < self.reorder_point:
            self.in_transit = True
            reorder_day = day + LEAD_TIME
            if reorder_day <= 20:
                # receive reorder on reorder_day
                revenue += self.standard_cost * self.reorder_qty
                cogs += self.standard_cost * self.reorder_qty
            else:
                # reorder will never arrive
                self.in_transit = False

def run() -> float:
    global revenue, cogs, write_offs
    revenue, cogs, write_offs = 0, 0, 0
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

    for d in range(1, 21):
        for product in products.values():
            product.remove_expired_batches(d)
            if product.in_transit:
                product.fill_backorders(product.reorder_qty, product.standard_cost)
                product.in_transit = False

        for event in events:
            if event[0] == d:
                sku, event_type, quantity, price = event[1], event[2], event[3], event[4]
                product = products[sku]

                if event_type == 'RECEIVE':
                    product.fill_backorders(quantity, price)
                    revenue += product.standard_cost * quantity
                    cogs += product.standard_cost * quantity

                elif event_type == 'ORDER':
                    product.remove_expired_batches(d)
                    product.fill_backorders(quantity, price)
                    revenue += price * quantity
                    cogs += price * quantity
                    if product.quantity < product.reorder_point and not product.in_transit:
                        product.place_reorder(d)

    unfilled_backorder_units = sum(product.quantity for product in products.values() if product.backorders)
    return round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

# testing
print(run())
```