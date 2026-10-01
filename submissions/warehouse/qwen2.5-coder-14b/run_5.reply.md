<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-09-30T20:06:47+00:00 -->

```python
from typing import List, Tuple, Dict

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

class Warehouse:
    def __init__(self):
        self.products = {
            'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00, 'stock': [], 'backorders': []},
            'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50, 'stock': [], 'backorders': []},
            'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20, 'stock': [], 'backorders': []}
        }
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0

    def receive(self, sku: str, quantity: int, unit_cost: float, day: int):
        product = self.products[sku]
        while quantity > 0 and product['backorders']:
            backorder_qty, backorder_price = product['backorders'][0]
            fill_qty = min(quantity, backorder_qty)
            self.revenue += fill_qty * backorder_price * BACKORDER_DISCOUNT
            self.cogs += fill_qty * unit_cost
            quantity -= fill_qty
            backorder_qty -= fill_qty
            if backorder_qty == 0:
                product['backorders'].pop(0)
            else:
                product['backorders'][0] = (backorder_qty, backorder_price)
        
        if quantity > 0:
            product['stock'].append((quantity, unit_cost, day + product['shelf_life']))
            product['stock'].sort(key=lambda x: (x[2], x[1]))

    def order(self, sku: str, quantity: int, price: float, day: int):
        product = self.products[sku]
        stock_used = 0
        while quantity > 0 and product['stock']:
            stock_qty, stock_cost, expiry_day = product['stock'][0]
            if expiry_day >= day:
                fill_qty = min(quantity, stock_qty)
                self.revenue += fill_qty * price
                self.cogs += fill_qty * stock_cost
                quantity -= fill_qty
                stock_used += fill_qty
                stock_qty -= fill_qty
                if stock_qty == 0:
                    product['stock'].pop(0)
                else:
                    product['stock'][0] = (stock_qty, stock_cost, expiry_day)
            else:
                product['stock'].pop(0)

        if quantity > 0:
            product['backorders'].append((quantity, price))

        if len(product['stock']) < product['reorder_point'] and not any(day + LEAD_TIME <= d for _, _, d in product['stock']):
            product['stock'].append((product['reorder_qty'], product['standard_cost'], day + LEAD_TIME + product['shelf_life']))
            product['stock'].sort(key=lambda x: (x[2], x[1]))

    def expiry(self, day: int):
        for sku in self.products:
            product = self.products[sku]
            while product['stock'] and product['stock'][0][2] < day:
                quantity, unit_cost, _ = product['stock'].pop(0)
                self.write_offs += quantity * unit_cost

    def run(self, events: List[Tuple[int, str, str, int, float]]) -> float:
        for day in range(1, 21):
            self.expiry(day)
            for sku in self.products:
                product = self.products[sku]
                if any(day + LEAD_TIME == d for _, _, d in product['stock']):
                    product['stock'].remove((product['reorder_qty'], product['standard_cost'], day + LEAD_TIME + product['shelf_life']))
                    self.receive(sku, product['reorder_qty'], product['standard_cost'], day)
            for event in events:
                if event[0] == day:
                    if event[1] == 'RECEIVE':
                        self.receive(event[2], event[3], event[4], day)
                    elif event[1] == 'ORDER':
                        self.order(event[2], event[3], event[4], day)
        
        cancellation_penalty = sum(sum(qty for qty, _ in product['backorders']) * CANCELLATION_PENALTY for product in self.products.values())
        return round(self.revenue - self.cogs - self.write_offs - cancellation_penalty, 2)

def run() -> float:
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
    warehouse = Warehouse()
    return warehouse.run(events)

if __name__ == "__main__":
    print(run())
```