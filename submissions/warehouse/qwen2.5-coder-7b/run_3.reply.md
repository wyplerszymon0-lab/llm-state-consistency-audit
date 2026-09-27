<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:21:02+00:00 -->

```python
from collections import defaultdict, deque
from typing import List, Tuple

SKU_A = 'A'
SKU_B = 'B'
SKU_C = 'C'

RECEIVE = 'RECEIVE'
ORDER = 'ORDER'

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

PRODUCT_SETTINGS = {
    SKU_A: {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
    SKU_B: {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
    SKU_C: {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
}

class PerishableWarehouse:
    def __init__(self):
        self.batches: defaultdict[str, List[Tuple[int, float, int]]] = defaultdict(list)
        self.backorders: defaultdict[str, List[Tuple[int, float]]] = defaultdict(list)
        self.reorders_in_transit: defaultdict[str, int] = defaultdict(int)
        self.revenue = 0.0
        self.cogs = 0.0
        self.write_offs = 0.0

    def run(self) -> float:
        for day in range(1, 21):
            self.expiry(day)
            self.arrivals(day)
            self.process_events(day)

        unfilled_backorder_units = sum(quantity for quantity, _ in self.backorders[SKU_A])
        unfilled_backorder_units += sum(quantity for quantity, _ in self.backorders[SKU_B])
        unfilled_backorder_units += sum(quantity for quantity, _ in self.backorders[SKU_C])

        return round(self.revenue - self.cogs - self.write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

    def expiry(self, day: int) -> None:
        for sku in [SKU_A, SKU_B, SKU_C]:
            self.batches[sku] = [batch for batch in self.batches[sku] if batch[2] >= day]
            self.write_offs += sum(batch[0] * batch[1] for batch in self.batches[sku])
            self.batches[sku] = []

    def arrivals(self, day: int) -> None:
        for sku in [SKU_A, SKU_B, SKU_C]:
            if self.reorders_in_transit[sku] > 0 and day == self.reorders_in_transit[sku]:
                reorder_qty = PRODUCT_SETTINGS[sku]['reorder_qty']
                unit_cost = PRODUCT_SETTINGS[sku]['standard_cost']
                self.receive(sku, reorder_qty, unit_cost)
                self.reorders_in_transit[sku] = 0

    def process_events(self, day: int) -> None:
        for event in self.events_on_day(day):
            event_type = event[1]
            sku = event[2]
            quantity = event[3]
            if event_type == RECEIVE:
                unit_cost = event[4]
                self.receive(sku, quantity, unit_cost)
            elif event_type == ORDER:
                price = event[4]
                self.order(sku, quantity, price)

    def events_on_day(self, day: int) -> List[List]:
        events = []
        for day_event in events:
            if day_event[0] == day:
                events.append(day_event)
        return events

    def receive(self, sku: str, quantity: int, unit_cost: float) -> None:
        for _ in range(quantity):
            for backorder in self.backorders[sku]:
                if backorder[0] == 1:
                    self.backorders[sku].remove(backorder)
                    self.revenue += backorder[1] * BACKORDER_DISCOUNT
                    self.cogs += unit_cost
                    break
                self.backorders[sku][0] = (backorder[0] - 1, backorder[1])
                self.cogs += unit_cost
                break
            else:
                self.batches[sku].append((1, unit_cost, day + PRODUCT_SETTINGS[sku]['shelf_life']))

    def order(self, sku: str, quantity: int, price: float) -> None:
        filled_quantity = 0
        for batch in sorted(self.batches[sku], key=lambda x: (x[2], x[1])):
            if filled_quantity + batch[0] >= quantity:
                self.batches[sku].remove(batch)
                filled_quantity += batch[0]
                self.revenue += batch[0] * price
                self.cogs += batch[0] * batch[1]
                break
            self.batches[sku].remove(batch)
            filled_quantity += batch[0]
            self.revenue += batch[0] * price
            self.cogs += batch[0] * batch[1]

        unfilled_quantity = quantity - filled_quantity
        if unfilled_quantity > 0:
            self.backorders[sku].append((unfilled_quantity, price))

        if (self.calculate_on_hand_quantity(sku) < PRODUCT_SETTINGS[sku]['reorder_point']
                and not self.reorders_in_transit[sku]):
            self.reorders_in_transit[sku] = day + LEAD_TIME

    def calculate_on_hand_quantity(self, sku: str) -> int:
        return sum(batch[0] for batch in self.batches[sku])

# Example usage:
warehouse = PerishableWarehouse()
print(warehouse.run())
```