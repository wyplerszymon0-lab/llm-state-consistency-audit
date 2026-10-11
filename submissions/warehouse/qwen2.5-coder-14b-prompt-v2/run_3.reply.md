<!-- model: ollama:qwen2.5-coder:14b | prompt v2 | 2026-10-10T17:35:47+00:00 -->

```python
from typing import List, Tuple, Dict, Set
from collections import deque

class WarehouseSimulator:
    def __init__(self):
        self.stock: Dict[str, List[Tuple[int, float, int]]] = {
            'A': [],
            'B': [],
            'C': []
        }
        self.backorders: Dict[str, deque[Tuple[int, float]]] = {
            'A': deque(),
            'B': deque(),
            'C': deque()
        }
        self.reorders: Set[str] = set()
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0
        self.product_settings = {
            'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
            'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
            'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
        }
        self.LEAD_TIME = 2
        self.BACKORDER_DISCOUNT = 0.90
        self.CANCELLATION_PENALTY = 2.00

    def process_expiry(self, day: int):
        for sku in self.stock:
            while self.stock[sku] and self.stock[sku][0][2] < day:
                quantity, unit_cost, _ = self.stock[sku].pop(0)
                self.write_offs += quantity * unit_cost

    def process_arrivals(self, day: int):
        for sku in self.reorders:
            reorder_qty = self.product_settings[sku]['reorder_qty']
            standard_cost = self.product_settings[sku]['standard_cost']
            self.stock[sku].append((reorder_qty, standard_cost, day + self.product_settings[sku]['shelf_life']))
        self.reorders.clear()

    def process_receive(self, sku: str, quantity: int, unit_cost: float, day: int):
        while self.backorders[sku] and quantity > 0:
            backorder_quantity, unit_price = self.backorders[sku][0]
            fill_quantity = min(quantity, backorder_quantity)
            self.revenue += fill_quantity * unit_price * self.BACKORDER_DISCOUNT
            self.cogs += fill_quantity * unit_cost
            quantity -= fill_quantity
            if fill_quantity == backorder_quantity:
                self.backorders[sku].popleft()
            else:
                self.backorders[sku][0] = (backorder_quantity - fill_quantity, unit_price)
        if quantity > 0:
            self.stock[sku].append((quantity, unit_cost, day + self.product_settings[sku]['shelf_life']))

    def process_order(self, sku: str, quantity: int, price: float):
        while self.stock[sku] and quantity > 0:
            batch_quantity, unit_cost, expiry_day = self.stock[sku][0]
            fill_quantity = min(quantity, batch_quantity)
            self.revenue += fill_quantity * price
            self.cogs += fill_quantity * unit_cost
            quantity -= fill_quantity
            if fill_quantity == batch_quantity:
                self.stock[sku].pop(0)
            else:
                self.stock[sku][0] = (batch_quantity - fill_quantity, unit_cost, expiry_day)
        if quantity > 0:
            self.backorders[sku].append((quantity, price))
        self.check_reorder(sku)

    def check_reorder(self, sku: str):
        if len(self.stock[sku]) == 0 or self.stock[sku][0][0] < self.product_settings[sku]['reorder_point']:
            if sku not in self.reorders:
                self.reorders.add(sku)

    def run(self) -> float:
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
            (20, 'ORDER', 'C', 10, 4.50)
        ]

        for day in range(1, 21):
            self.process_expiry(day)
            self.process_arrivals(day)
            for event in events:
                if event[0] == day:
                    if event[1] == 'RECEIVE':
                        self.process_receive(event[2], event[3], event[4], day)
                    elif event[1] == 'ORDER':
                        self.process_order(event[2], event[3], event[4])

        for sku in self.backorders:
            for backorder_quantity, _ in self.backorders[sku]:
                self.write_offs += backorder_quantity * self.CANCELLATION_PENALTY

        return round(self.revenue - self.cogs - self.write_offs, 2)

# The function to be called
def run() -> float:
    simulator = WarehouseSimulator()
    return simulator.run()
```