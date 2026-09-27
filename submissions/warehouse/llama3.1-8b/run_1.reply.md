<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:45:36+00:00 -->

```python
from dataclasses import dataclass
from typing import List, Tuple

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

@dataclass
class Batch:
    quantity: float
    unit_cost: float
    expiry_day: int

@dataclass
class Backorder:
    quantity: float
    unit_price: float

class Warehouse:
    def __init__(self):
        self.products = {
            'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
            'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
            'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20},
        }
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0
        self.batches = {sku: [] for sku in self.products}
        self.backorders = {sku: [] for sku in self.products}
        self.in_transit = {}

    def remove_expired_batches(self, d):
        for sku in self.products:
            self.batches[sku] = [b for b in self.batches[sku] if b.expiry_day >= d]
            self.write_offs += sum(b.quantity * b.unit_cost for b in self.batches[sku] if b.expiry_day < d)

    def receive(self, sku, quantity, unit_cost):
        if quantity < self.products[sku]['reorder_qty']:
            self.batches[sku].append(Batch(quantity, unit_cost, d + self.products[sku]['shelf_life']))
            self.cogs += quantity * unit_cost
        else:
            self.in_transit[sku] = self.products[sku]['reorder_qty']
            self.cogs += self.products[sku]['reorder_qty'] * self.products[sku]['standard_cost']

    def process_order(self, sku, quantity, price):
        for b in self.batches[sku]:
            if b.quantity >= quantity:
                self.revenue += quantity * price
                self.cogs += quantity * b.unit_cost
                b.quantity -= quantity
                break
        else:
            self.backorders[sku].append(Backorder(quantity, price))

    def process_events(self, d):
        self.remove_expired_batches(d)
        sku = self.in_transit.keys()
        if sku:
            sku = list(sku)[0]
            self.receive(sku, self.in_transit[sku], self.products[sku]['standard_cost'])
            del self.in_transit[sku]
        for sku in self.products:
            for e in events[d-1]:
                if e[1] == 'RECEIVE':
                    self.receive(sku, e[3], e[4])
                elif e[1] == 'ORDER':
                    self.process_order(sku, e[3], e[4])

    def calculate_answer(self):
        unfilled_backorder_units = sum(b.quantity for b in self.backorders['A'])
        return round(self.revenue - self.cogs - self.write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

events = [
    [('1', 'RECEIVE', 'A', 30, 3.80), ('1', 'RECEIVE', 'B', 8, 12.00), ('1', 'RECEIVE', 'C', 10, 2.00)],
    [('2', 'ORDER', 'A', 12, 7.50), ('2', 'ORDER', 'C', 4, 4.00)],
    [('3', 'RECEIVE', 'A', 10, 3.90), ('3', 'ORDER', 'B', 6, 20.00)],
    [('4', 'ORDER', 'B', 5, 21.00), ('4', 'ORDER', 'C', 3, 4.20)],
    [('5', 'ORDER', 'A', 15, 7.40)],
    [('6', 'ORDER', 'C', 2, 4.10)],
    [('7', 'ORDER', 'A', 9, 7.60)],
    [('8', 'ORDER', 'A', 5, 7.60), ('8', 'RECEIVE', 'A', 2, 3.95)],
    [('9', 'ORDER', 'C', 11, 4.00)],
    [('10', 'ORDER', 'B', 8, 20.50), ('10', 'ORDER', 'C', 2, 4.00)],
    [('12', 'ORDER', 'A', 10, 7.80)],
    [('13', 'ORDER', 'A', 1, 7.80)],
    [('14', 'ORDER', 'C', 5, 4.30)],
    [('15', 'ORDER', 'C', 3, 4.30)],
    [('16', 'ORDER', 'A', 25, 7.90)],
    [('18', 'ORDER', 'B', 9, 22.00)],
    [('19', 'ORDER', 'B', 4, 22.00), ('19', 'ORDER', 'A', 16, 8.00)],
    [('20', 'ORDER', 'C', 10, 4.50)],
]

warehouse = Warehouse()
for d in range(1, 21):
    if d % 2 == 0 or events[d-1]:
        warehouse.process_events(d)
print(warehouse.calculate_answer())
```