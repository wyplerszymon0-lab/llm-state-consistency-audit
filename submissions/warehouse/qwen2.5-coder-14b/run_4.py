from typing import List, Tuple, Dict
from collections import namedtuple, deque

# Constants
LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

# Product settings
Product = namedtuple('Product', ['sku', 'shelf_life', 'reorder_point', 'reorder_qty', 'standard_cost'])
products = {
    'A': Product('A', 5, 8, 20, 4.00),
    'B': Product('B', 30, 5, 10, 12.50),
    'C': Product('C', 3, 4, 12, 2.20),
}

# Events
Event = namedtuple('Event', ['day', 'type', 'sku', 'quantity', 'price'])
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
    Event(20, 'ORDER', 'C', 10, 4.50),
]

class Warehouse:
    def __init__(self):
        self.batches = {sku: [] for sku in products}
        self.backorders = {sku: deque() for sku in products}
        self.reorder_in_transit = {sku: None for sku in products}
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0

    def run(self) -> float:
        for day in range(1, 21):
            self.expire_batches(day)
            self.process_arrivals(day)
            self.process_events(day)
        self.process_cancellations()
        return round(self.revenue - self.cogs - self.write_offs, 2)

    def expire_batches(self, day: int):
        for sku in products:
            while self.batches[sku] and self.batches[sku][0][2] < day:
                quantity, unit_cost, _ = self.batches[sku].pop(0)
                self.write_offs += quantity * unit_cost

    def process_arrivals(self, day: int):
        for sku in products:
            if self.reorder_in_transit[sku] == day:
                self.receive(sku, products[sku].reorder_qty, products[sku].standard_cost)
                self.reorder_in_transit[sku] = None

    def process_events(self, day: int):
        for event in events:
            if event.day == day:
                if event.type == 'RECEIVE':
                    self.receive(event.sku, event.quantity, event.price)
                elif event.type == 'ORDER':
                    self.order(event.sku, event.quantity, event.price)

    def receive(self, sku: str, quantity: int, unit_cost: float):
        product = products[sku]
        while self.backorders[sku] and quantity > 0:
            backorder_quantity, unit_price = self.backorders[sku][0]
            if quantity >= backorder_quantity:
                self.revenue += backorder_quantity * unit_price * BACKORDER_DISCOUNT
                self.cogs += backorder_quantity * unit_cost
                quantity -= backorder_quantity
                self.backorders[sku].popleft()
            else:
                self.revenue += quantity * unit_price * BACKORDER_DISCOUNT
                self.cogs += quantity * unit_cost
                self.backorders[sku][0] = (backorder_quantity - quantity, unit_price)
                quantity = 0
        if quantity > 0:
            self.batches[sku].append((quantity, unit_cost, day + product.shelf_life))
            self.batches[sku].sort(key=lambda x: (x[2], x[0]))

    def order(self, sku: str, quantity: int, price: float):
        product = products[sku]
        while quantity > 0 and self.batches[sku]:
            batch_quantity, unit_cost, expiry_day = self.batches[sku][0]
            if quantity >= batch_quantity:
                self.revenue += batch_quantity * price
                self.cogs += batch_quantity * unit_cost
                quantity -= batch_quantity
                self.batches[sku].pop(0)
            else:
                self.revenue += quantity * price
                self.cogs += quantity * unit_cost
                self.batches[sku][0] = (batch_quantity - quantity, unit_cost, expiry_day)
                quantity = 0
        if quantity > 0:
            self.backorders[sku].append((quantity, price))
        if len(self.batches[sku]) < product.reorder_point and self.reorder_in_transit[sku] is None:
            self.reorder_in_transit[sku] = day + LEAD_TIME

    def process_cancellations(self):
        for sku in products:
            for quantity, _ in self.backorders[sku]:
                self.write_offs += quantity * CANCELLATION_PENALTY

def run() -> float:
    warehouse = Warehouse()
    return warehouse.run()

# Example usage
if __name__ == "__main__":
    print(run())
