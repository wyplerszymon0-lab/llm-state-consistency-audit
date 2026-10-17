<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T10:00:23+00:00 -->

```python
import heapq
from collections import defaultdict

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
    backorders = defaultdict(list)  # sku -> list of (quantity, unit_price)
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
    event_dict = defaultdict(list)
    for event in events:
        day, event_type, sku, quantity, price = event
        event_dict[day].append((event_type, sku, quantity, price))
    
    # Process each day
    for day in range(1, 21):
        # Step 1: Expiry
        for sku in stock:
            new_batches = []
            for quantity, unit_cost, expiry_day in stock[sku]:
                if expiry_day >= day:
                    new_batches.append((quantity, unit_cost, expiry_day))
                else:
                    write_offs += quantity * unit_cost
            stock[sku] = new_batches
        
        # Step 2: Arrivals (reorder arrivals)
        for sku in list(reorder_in_transit.keys()):
            if reorder_in_transit[sku] == day:
                qty = products[sku]['reorder_qty']
                cost = products[sku]['standard_cost']
                expiry_day = day + products[sku]['shelf_life']
                stock[sku].append((qty, cost, expiry_day))
                del reorder_in_transit[sku]
        
        # Step 3: Events of the day
        if day in event_dict:
            for event_type, sku, quantity, price in event_dict[day]:
                if event_type == 'RECEIVE':
                    # Receive new stock
                    unit_cost = price
                    expiry_day = day + products[sku]['shelf_life']
                    # Fill backorders first
                    remaining_qty = quantity
                    new_backorders = []
                    while backorders[sku] and remaining_qty > 0:
                        bo_qty, bo_price = backorders[sku].pop(0)
                        if bo_qty <= remaining_qty:
                            # Backorder fully filled
                            revenue += bo_qty * bo_price * BACKORDER_DISCOUNT
                            cogs += bo_qty * unit_cost
                            remaining_qty -= bo_qty
                        else:
                            # Backorder partially filled
                            revenue += remaining_qty * bo_price * BACKORDER_DISCOUNT
                            cogs += remaining_qty * unit_cost
                            new_backorders.append((bo_qty - remaining_qty, bo_price))
                            remaining_qty = 0
                    backorders[sku] = new_backorders + backorders[sku]
                    # Add remaining to stock
                    if remaining_qty > 0:
                        stock[sku].append((remaining_qty, unit_cost, expiry_day))
                elif event_type == 'ORDER':
                    # Process order
                    order_qty = quantity
                    order_price = price
                    
                    # Sort batches by expiry day and then by received day (FIFO)
                    # We'll sort based on expiry_day, but we need to track the day when batch was added.
                    # For now we'll use a simple approach: sort by expiry day first, then by the insertion order
                    # But since we don't track insertion day, let's just make sure it's FIFO for batches with same expiry day
                    # We'll create a list of (expiry_day, received_day, quantity, unit_cost) and sort by expiry_day and then received_day
                    # Since we have no way to know received_day in the batch, let's assume all batches added at the same time are FIFO
                    # So we can just sort by expiry day first.
                    
                    # Let's make a list of batches with their original received days
                    batch_info = []
                    for i, (batch_qty, unit_cost, expiry_day) in enumerate(stock[sku]):
                        batch_info.append((expiry_day, i, batch_qty, unit_cost))
                    
                    batch_info.sort(key=lambda x: (x[0], x[1]))
                    
                    remaining_qty = order_qty
                    new_stock = []
                    for expiry_day, received_order, batch_qty, unit_cost in batch_info:
                        if remaining_qty <= 0:
                            new_stock.append((batch_qty, unit_cost, expiry_day))
                        else:
                            if batch_qty <= remaining_qty:
                                # Use up entire batch
                                revenue += batch_qty * order_price
                                cogs += batch_qty * unit_cost
                                remaining_qty -= batch_qty
                            else:
                                # Partially use batch
                                revenue += remaining_qty * order_price
                                cogs += remaining_qty * unit_cost
                                new_stock.append((batch_qty - remaining_qty, unit_cost, expiry_day))
                                remaining_qty = 0
                    
                    # Update stock with remaining batches
                    stock[sku] = new_stock
                    
                    # Handle backorders if needed
                    if remaining_qty > 0:
                        backorders[sku].append((remaining_qty, order_price))
                    
                    # Reorder check
                    total_on_hand = sum(batch[0] for batch in stock[sku])
                    if total_on_hand <= products[sku]['reorder_point']:
                        if sku not in reorder_in_transit:
                            reorder_day = day + LEAD_TIME
                            if reorder_day <= 20:
                                reorder_in_transit[sku] = reorder_day
    
    # Calculate final result
    unfilled_backorder_units = sum(qty for backorders_list in backorders.values() for qty, _ in backorders_list)
    
    total_revenue = revenue
    total_cogs = cogs
    total_write_offs = write_offs
    cancellation_cost = CANCELLATION_PENALTY * unfilled_backorder_units
    
    answer = total_revenue - total_cogs - total_write_offs - cancellation_cost
    return round(answer, 2)
```