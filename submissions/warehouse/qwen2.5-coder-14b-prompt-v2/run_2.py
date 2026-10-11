from typing import List, Tuple, Dict
import heapq

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

class Warehouse:
    def __init__(self):
        self.products = {
            'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
            'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
            'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
        }
        self.stocks = {sku: [] for sku in self.products}
        self.backorders = {sku: [] for sku in self.products}
        self.in_transit = {sku: False for sku in self.products}
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0

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
            self.expiry(day)
            self.arrival(day)
            self.process_events(day, [e for e in events if e[0] == day])

        self.handle_backorders()
        return round(self.revenue - self.cogs - self.write_offs, 2)

    def expiry(self, day: int):
        for sku in self.products:
            while self.stocks[sku] and self.stocks[sku][0][2] < day:
                quantity, unit_cost, _ = heapq.heappop(self.stocks[sku])
                self.write_offs += quantity * unit_cost

    def arrival(self, day: int):
        for sku in self.products:
            if self.in_transit[sku]:
                quantity = self.products[sku]['reorder_qty']
                unit_cost = self.products[sku]['standard_cost']
                expiry_day = day + self.products[sku]['shelf_life']
                heapq.heappush(self.stocks[sku], (quantity, unit_cost, expiry_day))
                self.in_transit[sku] = False

    def process_events(self, day: int, events: List[Tuple]):
        for event_type, sku, quantity, price in events:
            if event_type == 'RECEIVE':
                self.receive(sku, quantity, price)
            elif event_type == 'ORDER':
                self.order(sku, quantity, price)
            else:
                raise ValueError(f"Unknown event type: {event_type}")

    def receive(self, sku: str, quantity: int, unit_cost: float):
        while self.backorders[sku] and quantity > 0:
            backorder_qty, backorder_price = heapq.heappop(self.backorders[sku])
            fill_qty = min(quantity, backorder_qty)
            self.revenue += fill_qty * backorder_price * BACKORDER_DISCOUNT
            self.cogs += fill_qty * unit_cost
            quantity -= fill_qty
            backorder_qty -= fill_qty
            if backorder_qty > 0:
                heapq.heappush(self.backorders[sku], (backorder_qty, backorder_price))

        if quantity > 0:
            expiry_day = day + self.products[sku]['shelf_life']
            heapq.heappush(self.stocks[sku], (quantity, unit_cost, expiry_day))

    def order(self, sku: str, quantity: int, price: float):
        while self.stocks[sku] and quantity > 0:
            batch_qty, batch_cost, batch_expiry = heapq.heappop(self.stocks[sku])
            fill_qty = min(quantity, batch_qty)
            self.revenue += fill_qty * price
            self.cogs += fill_qty * batch_cost
            quantity -= fill_qty
            batch_qty -= fill_qty
            if batch_qty > 0:
                heapq.heappush(self.stocks[sku], (batch_qty, batch_cost, batch_expiry))

        if quantity > 0:
            heapq.heappush(self.backorders[sku], (quantity, price))

        self.check_reorder(sku)

    def check_reorder(self, sku: str):
        if self.get_on_hand(sku) < self.products[sku]['reorder_point'] and not self.in_transit[sku]:
            self.in_transit[sku] = True

    def get_on_hand(self, sku: str) -> int:
        return sum(quantity for quantity, _, _ in self.stocks[sku])

    def handle_backorders(self):
        for sku in self.products:
            for backorder_qty, _ in self.backorders[sku]:
                self.write_offs += backorder_qty * CANCELLATION_PENALTY

def run() -> float:
    warehouse = Warehouse()
    return warehouse.run()

# Example usage:
# print(run())
