<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T10:04:39+00:00 -->

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
    
    # Initialize state
    stock = defaultdict(list)  # sku -> list of (quantity, unit_cost, expiry_day)
    backorders = defaultdict(deque)  # sku -> deque of (quantity, unit_price)
    reorder_in_transit = defaultdict(int)  # sku -> day when reorder arrives
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
        
        # Step 2: Arrivals (reorder in transit)
        for sku in list(reorder_in_transit.keys()):
            if reorder_in_transit[sku] == day:
                qty = products[sku]['reorder_qty']
                cost = products[sku]['standard_cost']
                expiry_day = day + products[sku]['shelf_life']
                stock[sku].append((qty, cost, expiry_day))
                del reorder_in_transit[sku]
        
        # Step 3: Process events of the day
        if day in events_by_day:
            for event_type, sku, quantity, price in events_by_day[day]:
                if event_type == 'RECEIVE':
                    # Receive inventory
                    qty = quantity
                    unit_cost = price
                    
                    # Fill backorders first (FIFO)
                    while qty > 0 and backorders[sku]:
                        backorder_qty, backorder_price = backorders[sku][0]
                        fill_qty = min(qty, backorder_qty)
                        revenue += fill_qty * backorder_price * BACKORDER_DISCOUNT
                        cogs += fill_qty * unit_cost
                        qty -= fill_qty
                        backorder_qty -= fill_qty
                        if backorder_qty == 0:
                            backorders[sku].popleft()
                        else:
                            backorders[sku][0] = (backorder_qty, backorder_price)
                    
                    # Add remaining to stock as new batch
                    if qty > 0:
                        expiry_day = day + products[sku]['shelf_life']
                        stock[sku].append((qty, unit_cost, expiry_day))
                
                elif event_type == 'ORDER':
                    # Process order
                    order_qty = quantity
                    order_price = price
                    
                    # Sort batches by expiry date and then by arrival date (FIFO)
                    # We'll sort by (expiry_day, arrival_day) where arrival_day is the index in stock
                    batch_list = []
                    for i, batch in enumerate(stock[sku]):
                        batch_list.append((batch[2], i, batch))  # expiry_day, index, batch
                    
                    batch_list.sort()
                    
                    # Fill from oldest batches first
                    remaining_qty = order_qty
                    for expiry_day, idx, batch in batch_list:
                        batch_qty, unit_cost, _ = batch
                        if remaining_qty <= 0:
                            break
                        fill_qty = min(remaining_qty, batch_qty)
                        revenue += fill_qty * order_price
                        cogs += fill_qty * unit_cost
                        remaining_qty -= fill_qty
                        
                        # Update stock (we'll handle this after processing all batches)
                        # Actually, we'll just update the quantity in the original list
                        # But we need to be careful with the sorting - let's use a different approach
                    
                    # Let's reprocess to properly handle batch updates
                    # Sort batches by expiry date and arrival time
                    sorted_batches = []
                    for i, batch in enumerate(stock[sku]):
                        sorted_batches.append((batch[2], i, batch))
                    sorted_batches.sort()
                    
                    # Now update stock quantities
                    remaining_qty = order_qty
                    updated_stock = []
                    for expiry_day, idx, batch in sorted_batches:
                        batch_qty, unit_cost, _ = batch
                        if remaining_qty <= 0:
                            updated_stock.append(batch)
                            continue
                        fill_qty = min(remaining_qty, batch_qty)
                        revenue += fill_qty * order_price
                        cogs += fill_qty * unit_cost
                        remaining_qty -= fill_qty
                        new_batch_qty = batch_qty - fill_qty
                        if new_batch_qty > 0:
                            updated_stock.append((new_batch_qty, unit_cost, expiry_day))
                    
                    # Update stock
                    stock[sku] = updated_stock
                    
                    # If there's still unfilled quantity, add to backorders
                    if remaining_qty > 0:
                        backorders[sku].append((remaining_qty, order_price))
                
                # Reorder check (after ORDER events)
                if event_type == 'ORDER':
                    total_stock = sum(batch[0] for batch in stock[sku])
                    if total_stock < products[sku]['reorder_point']:
                        if sku not in reorder_in_transit:
                            reorder_day = day + LEAD_TIME
                            if reorder_day <= 20:
                                reorder_in_transit[sku] = reorder_day
    
    # Calculate final penalty for backorders
    total_backordered = sum(qty for backorder_list in backorders.values() for qty, _ in backorder_list)
    penalty = total_backordered * CANCELLATION_PENALTY
    
    # Final answer
    answer = revenue - cogs - write_offs - penalty
    return round(answer, 2)
```