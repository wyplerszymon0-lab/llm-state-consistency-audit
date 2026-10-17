<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T10:03:11+00:00 -->

```python
import heapq
from collections import defaultdict, deque

def run():
    # Product settings
    products = {
        'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
    }
    
    # Constants
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00
    
    # State
    stock = defaultdict(list)  # sku -> list of (quantity, unit_cost, expiry_day)
    backorders = defaultdict(deque)  # sku -> deque of (quantity, unit_price)
    reorder_in_transit = {}  # sku -> day when reorder arrives
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0
    
    # Events
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
    
    # Group events by day
    events_by_day = defaultdict(list)
    for event in events:
        day, event_type, sku, quantity, price = event
        events_by_day[day].append((event_type, sku, quantity, price))
    
    # Process each day from 1 to 20
    for day in range(1, 21):
        # Step 1: Expiry
        for sku in stock:
            new_batches = []
            for batch in stock[sku]:
                quantity, unit_cost, expiry_day = batch
                if expiry_day < day:
                    write_offs += quantity * unit_cost
                else:
                    new_batches.append(batch)
            stock[sku] = new_batches
        
        # Step 2: Arrivals
        for sku in reorder_in_transit:
            if reorder_in_transit[sku] == day:
                qty = products[sku]['reorder_qty']
                cost = products[sku]['standard_cost']
                expiry_day = day + products[sku]['shelf_life']
                stock[sku].append((qty, cost, expiry_day))
                del reorder_in_transit[sku]
        
        # Step 3: Events
        if day in events_by_day:
            for event_type, sku, quantity, price in events_by_day[day]:
                if event_type == 'RECEIVE':
                    # Add to backorders first, then to stock
                    remaining = quantity
                    while remaining > 0 and backorders[sku]:
                        backorder_qty, backorder_price = backorders[sku][0]
                        if backorder_qty <= remaining:
                            # Fill entire backorder
                            remaining -= backorder_qty
                            revenue += backorder_qty * backorder_price * BACKORDER_DISCOUNT
                            cogs += backorder_qty * price
                            backorders[sku].popleft()
                        else:
                            # Partially fill backorder
                            revenue += remaining * backorder_price * BACKORDER_DISCOUNT
                            cogs += remaining * price
                            backorders[sku][0] = (backorder_qty - remaining, backorder_price)
                            remaining = 0
                    
                    if remaining > 0:
                        expiry_day = day + products[sku]['shelf_life']
                        stock[sku].append((remaining, price, expiry_day))
                elif event_type == 'ORDER':
                    # Fill from batches
                    # Sort batches by expiry day and then by received day (earlier first)
                    # We'll use a priority queue to simulate this
                    batch_heap = []
                    for i, batch in enumerate(stock[sku]):
                        quantity, unit_cost, expiry_day = batch
                        heapq.heappush(batch_heap, (expiry_day, i, quantity, unit_cost))
                    
                    remaining = quantity
                    filled_batches = []
                    
                    while remaining > 0 and batch_heap:
                        expiry_day, i, batch_qty, unit_cost = heapq.heappop(batch_heap)
                        if batch_qty <= remaining:
                            # Fill entire batch
                            remaining -= batch_qty
                            revenue += batch_qty * price
                            cogs += batch_qty * unit_cost
                            filled_batches.append((batch_qty, unit_cost, expiry_day))
                        else:
                            # Partially fill batch
                            revenue += remaining * price
                            cogs += remaining * unit_cost
                            # Put back the leftover batch
                            heapq.heappush(batch_heap, (expiry_day, i, batch_qty - remaining, unit_cost))
                            remaining = 0
                    
                    # If there are unfilled orders, add to backorders
                    if remaining > 0:
                        backorders[sku].append((remaining, price))
                    
                    # Reorder check
                    total_on_hand = sum(batch[0] for batch in stock[sku])
                    if total_on_hand <= products[sku]['reorder_point']:
                        if sku not in reorder_in_transit:
                            reorder_day = day + LEAD_TIME
                            if reorder_day <= 20:
                                reorder_in_transit[sku] = reorder_day
    
    # Calculate cancellation penalties for backorders
    unfilled_units = sum(quantity for quantities in backorders.values() for quantity, _ in quantities)
    penalty = unfilled_units * CANCELLATION_PENALTY
    
    # Final result
    answer = revenue - cogs - write_offs - penalty
    return round(answer, 2)
```