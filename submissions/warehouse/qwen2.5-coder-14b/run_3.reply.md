<!-- model: ollama:qwen2.5-coder:14b | prompt v1 | 2026-09-30T19:58:13+00:00 -->

```python
from collections import defaultdict, deque

class Warehouse:
    def __init__(self):
        self.stocks = {
            'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00, 'batches': [], 'backorders': deque()},
            'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50, 'batches': [], 'backorders': deque()},
            'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20, 'batches': [], 'backorders': deque()}
        }
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0
        self.in_transit = {}

    def run(self):
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
            self.expiry(day)
            self.arrival(day)
            self.process_events(day, [e for e in events if e[0] == day])

        self.handle_backorders()
        return round(self.revenue - self.cogs - self.write_offs - self.cancellation_penalty(), 2)

    def expiry(self, day):
        for sku, data in self.stocks.items():
            while data['batches'] and data['batches'][0][2] < day:
                quantity, unit_cost, _ = data['batches'].pop(0)
                self.write_offs += quantity * unit_cost

    def arrival(self, day):
        for sku in self.in_transit:
            if self.in_transit[sku] == day:
                self.receive(sku, self.stocks[sku]['reorder_qty'], self.stocks[sku]['standard_cost'])
                del self.in_transit[sku]

    def process_events(self, day, events):
        for event in events:
            event_day, event_type, sku, quantity, price = event
            if event_type == 'RECEIVE':
                self.receive(sku, quantity, price)
            elif event_type == 'ORDER':
                self.order(sku, quantity, price)
                self.reorder_check(sku)

    def receive(self, sku, quantity, unit_cost):
        backorders = self.stocks[sku]['backorders']
        while backorders and quantity > 0:
            backorder_quantity, backorder_price = backorders[0]
            if quantity >= backorder_quantity:
                self.revenue += backorder_quantity * backorder_price * 0.90
                self.cogs += backorder_quantity * unit_cost
                quantity -= backorder_quantity
                backorders.popleft()
            else:
                self.revenue += quantity * backorder_price * 0.90
                self.cogs += quantity * unit_cost
                backorders[0] = (backorder_quantity - quantity, backorder_price)
                quantity = 0

        if quantity > 0:
            self.stocks[sku]['batches'].append((quantity, unit_cost, day + self.stocks[sku]['shelf_life']))
            self.stocks[sku]['batches'].sort(key=lambda x: (x[2], x[1]))

    def order(self, sku, quantity, price):
        batches = self.stocks[sku]['batches']
        while batches and quantity > 0:
            batch_quantity, batch_cost, expiry_day = batches[0]
            if quantity >= batch_quantity:
                self.revenue += batch_quantity * price
                self.cogs += batch_quantity * batch_cost
                quantity -= batch_quantity
                batches.popleft()
            else:
                self.revenue += quantity * price
                self.cogs += quantity * batch_cost
                batches[0] = (batch_quantity - quantity, batch_cost, expiry_day)
                quantity = 0

        if quantity > 0:
            self.stocks[sku]['backorders'].append((quantity, price))

    def reorder_check(self, sku):
        if not self.in_transit.get(sku, False) and len(self.stocks[sku]['batches']) == 0:
            self.in_transit[sku] = 20 + 1  # Reorders arriving after day 20 never arrive

    def handle_backorders(self):
        for sku, data in self.stocks.items():
            for quantity, _ in data['backorders']:
                self.write_offs += quantity * 2.00

def run():
    warehouse = Warehouse()
    return warehouse.run()
```