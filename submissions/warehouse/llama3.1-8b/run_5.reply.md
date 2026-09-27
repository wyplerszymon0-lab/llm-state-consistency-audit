<!-- model: ollama:llama3.1:8b | prompt v1 | 2026-09-27T14:47:54+00:00 -->

```python
from datetime import timedelta
from dataclasses import dataclass
from typing import List, Optional

class Batch:
    def __init__(self, quantity: int, unit_cost: float, expiry_day: int):
        self.quantity = quantity
        self.unit_cost = unit_cost
        self.expiry_day = expiry_day

    def __repr__(self):
        return f"Batch(quantity={self.quantity}, unit_cost={self.unit_cost}, expiry_day={self.expiry_day})"

@dataclass
class Order:
    sku: str
    quantity: int
    unit_price: float

@dataclass
class Backorder:
    quantity: int
    unit_price: float

class Warehouse:
    def __init__(self):
        self.stock = {
            "A": [],
            "B": [],
            "C": []
        }
        self.backorders = {
            "A": [],
            "B": [],
            "C": []
        }
        self.in_transit = {
            "A": False,
            "B": False,
            "C": False
        }
        self.revenue = 0
        self.cogs = 0
        self.write_offs = 0
        self.unfilled_backorder_units = {
            "A": 0,
            "B": 0,
            "C": 0
        }

    def process_day(self, day: int, events: List[dict]):
        # Expiry
        for sku in self.stock:
            self.stock[sku] = [b for b in self.stock[sku] if b.expiry_day >= day]
            self.write_offs += sum(b.quantity * b.unit_cost for b in self.stock[sku] if b.expiry_day < day)

        # Arrival
        if self.in_transit["A"] and day == 2:
            self.stock["A"].append(Batch(20, 4.00, 4))
        elif self.in_transit["B"] and day == 5:
            self.stock["B"].append(Batch(10, 12.50, 5))
        elif self.in_transit["C"] and day == 8:
            self.stock["C"].append(Batch(12, 2.20, 8))

        # Events
        for event in events:
            sku = event["sku"]
            if event["type"] == "RECEIVE":
                quantity = event["quantity"]
                unit_cost = event["price"]
                while quantity > 0:
                    if self.backorders[sku]:
                        backorder = self.backorders[sku].pop(0)
                        self.revenue += backorder.quantity * backorder.unit_price * 0.9
                        self.cogs += backorder.quantity * unit_cost
                        quantity -= backorder.quantity
                    else:
                        self.stock[sku].append(Batch(quantity, unit_cost, day + 5))
                        break
            elif event["type"] == "ORDER":
                order = Order(sku, event["quantity"], event["price"])
                quantity = order.quantity
                for b in self.stock[sku]:
                    used = min(quantity, b.quantity)
                    self.cogs += used * b.unit_cost
                    self.revenue += used * order.unit_price
                    quantity -= used
                    b.quantity -= used
                    if b.quantity == 0:
                        self.stock[sku].remove(b)
                    if quantity == 0:
                        break
                if quantity > 0:
                    self.backorders[sku].append(Backorder(quantity, order.unit_price))
                if self.stock[sku]:
                    if self.stock[sku][0].expiry_day >= day + 2:
                        self.in_transit[sku] = True
                    elif self.stock[sku][0].expiry_day < day + 2 and not self.in_transit[sku]:
                        self.in_transit[sku] = True
                        self.stock[sku].append(Batch(20, 4.00, day + 2))

        # Reorder check
        for sku in self.stock:
            if self.in_transit[sku] and day >= 2:
                self.in_transit[sku] = False
            if self.stock[sku] and self.stock[sku][0].expiry_day < day + 2 and day >= 2:
                self.in_transit[sku] = True
                self.stock[sku].append(Batch(20, 4.00, day + 2))
            if self.stock[sku] and self.stock[sku][0].expiry_day < day + 2 and day < 2:
                self.in_transit[sku] = True
                self.stock[sku].append(Batch(20, 4.00, day + 2))

    def process_backorders(self):
        for sku in self.backorders:
            for backorder in self.backorders[sku]:
                self.revenue += backorder.quantity * backorder.unit_price * 0.9
                self.cogs += backorder.quantity * 2
                self.unfilled_backorder_units[sku] += backorder.quantity

def run():
    warehouse = Warehouse()
    events = [
        {"day": 1, "type": "RECEIVE", "sku": "A", "quantity": 30, "price": 3.80},
        {"day": 1, "type": "RECEIVE", "sku": "B", "quantity": 8, "price": 12.00},
        {"day": 1, "type": "RECEIVE", "sku": "C", "quantity": 10, "price": 2.00},
        {"day": 2, "type": "ORDER", "sku": "A", "quantity": 12, "price": 7.50},
        {"day": 2, "type": "ORDER", "sku": "C", "quantity": 4, "price": 4.00},
        {"day": 3, "type": "RECEIVE", "sku": "A", "quantity": 10, "price": 3.90},
        {"day": 3, "type": "ORDER", "sku": "B", "quantity": 6, "price": 20.00},
        {"day": 4, "type": "ORDER", "sku": "B", "quantity": 5, "price": 21.00},
        {"day": 4, "type": "ORDER", "sku": "C", "quantity": 3, "price": 4.20},
        {"day": 5, "type": "ORDER", "sku": "A", "quantity": 15, "price": 7.40},
        {"day": 6, "type": "ORDER", "sku": "C", "quantity": 2, "price": 4.10},
        {"day": 7, "type": "ORDER", "sku": "A", "quantity": 9, "price": 7.60},
        {"day": 8, "type": "ORDER", "sku": "A", "quantity": 5, "price": 7.60},
        {"day": 8, "type": "RECEIVE", "sku": "A", "quantity": 2, "price": 3.95},
        {"day": 9, "type": "ORDER", "sku": "C", "quantity": 11, "price": 4.00},
        {"day": 10, "type": "ORDER", "sku": "B", "quantity": 8, "price": 20.50},
        {"day": 10, "type": "ORDER", "sku": "C", "quantity": 2, "price": 4.00},
        {"day": 12, "type": "ORDER", "sku": "A", "quantity": 10, "price": 7.80},
        {"day": 13, "type": "ORDER", "sku": "A", "quantity": 1, "price": 7.80},
        {"day": 14, "type": "ORDER", "sku": "C", "quantity": 5, "price": 4.30},
        {"day": 15, "type": "ORDER", "sku": "C", "quantity": 3, "price": 4.30},
        {"day": 16, "type": "ORDER", "sku": "A", "quantity": 25, "price": 7.90},
        {"day": 18, "type": "ORDER", "sku": "B", "quantity": 9, "price": 22.00},
        {"day": 19, "type": "ORDER", "sku": "B", "quantity": 4, "price": 22.00},
        {"day": 19, "type": "ORDER", "sku": "A", "quantity": 16, "price": 8.00},
        {"day": 20, "type": "ORDER", "sku": "C", "quantity": 10, "price": 4.50}
    ]

    for day in range(1, 21):
        warehouse.process_day(day, [event for event in events if event["day"] == day])
    warehouse.process_backorders()

    answer = round(warehouse.revenue - warehouse.cogs - warehouse.write_offs - 2 * warehouse.unfilled_backorder_units["A"] - 2 * warehouse.unfilled_backorder_units["B"] - 2 * warehouse.unfilled_backorder_units["C"], 2)

    return answer
```