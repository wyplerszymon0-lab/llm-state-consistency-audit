from collections import deque

SKU_A = 'A'
SKU_B = 'B'
SKU_C = 'C'

SKU_SETTINGS = {
    SKU_A: {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
    SKU_B: {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
    SKU_C: {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
}

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

Event = tuple[int, str, str, int, float]

class Batch:
    def __init__(self, quantity: int, unit_cost: float, expiry_day: int):
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.expiry_day = expiry_day

    def __lt__(self, other: 'Batch') -> bool:
        if self.expiry_day == other.expiry_day:
            return self.expiry_day < other.expiry_day
        return self.expiry_day < other.expiry_day

class Backorder:
    def __init__(self, quantity: int, unit_price: float):
        self.quantity = quantity
        self.unit_price = unit_price

    def __lt__(self, other: 'Backorder') -> bool:
        return self.unit_price < other.unit_price

class SKU:
    def __init__(self):
        self.batches = deque[Batch]()
        self.backorders = deque[Backorder]()
        self.auto_reorder_in_transit = None

    def update_batches(self, day: int):
        while self.batches and self.batches[0].expiry_day < day:
            batch = self.batches.popleft()
            self.write_offs += batch.quantity * batch.unit_cost

    def receive(self, day: int, quantity: int, unit_cost: float):
        self.update_batches(day)
        while self.backorders and self.backorders[0].quantity <= quantity:
            backorder = self.backorders.popleft()
            filled_quantity = min(backorder.quantity, quantity)
            self.revenue += filled_quantity * backorder.unit_price * BACKORDER_DISCOUNT
            self.cogs += filled_quantity * unit_cost
            quantity -= filled_quantity
        if quantity > 0:
            self.backorders.append(Backorder(quantity, unit_cost))

    def order(self, day: int, quantity: int, unit_price: float):
        self.update_batches(day)
        filled_quantity = 0
        for batch in self.batches:
            if batch.quantity <= quantity - filled_quantity:
                filled_quantity += batch.quantity
                self.revenue += batch.quantity * unit_price
                self.cogs += batch.quantity * batch.unit_cost
                batch.quantity = 0
            else:
                filled_quantity += quantity - filled_quantity
                self.revenue += (quantity - filled_quantity) * unit_price
                self.cogs += (quantity - filled_quantity) * batch.unit_cost
                batch.quantity -= quantity - filled_quantity
                break
        if quantity > filled_quantity:
            self.backorders.append(Backorder(quantity - filled_quantity, unit_price))
        self.check_reorder(day)

    def check_reorder(self, day: int):
        if self.batches:
            if self.batches[0].quantity < SKU_SETTINGS[self.sku]['reorder_point'] and self.auto_reorder_in_transit is None:
                self.auto_reorder_in_transit = day + LEAD_TIME

    def receive_auto_reorder(self, day: int):
        self.receive(day, SKU_SETTINGS[self.sku]['reorder_qty'], SKU_SETTINGS[self.sku]['standard_cost'])
        self.auto_reorder_in_transit = None

class Warehouse:
    def __init__(self):
        self.skus = {SKU_A: SKU(), SKU_B: SKU(), SKU_C: SKU()}
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0

    def run(self, events: list[Event]) -> float:
        day = 1
        events = deque(events)
        while day <= 20 or events:
            while events and events[0][0] == day:
                _, event_type, sku, quantity, price = events.popleft()
                if event_type == 'RECEIVE':
                    self.skus[sku].receive(day, quantity, price)
                elif event_type == 'ORDER':
                    self.skus[sku].order(day, quantity, price)
            for sku in (SKU_A, SKU_B, SKU_C):
                self.skus[sku].receive_auto_reorder(day)
                self.skus[sku].check_reorder(day)
            day += 1

        unfilled_backorder_units = sum(backorder.quantity for sku in (SKU_A, SKU_B, SKU_C) for backorder in self.skus[sku].backorders)
        return round(self.revenue - self.cogs - self.write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

def run() -> float:
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
    return Warehouse().run(events)

print(run())
