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
    reorder_in_transit = {}  # sku -> day_when_arrives
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
        # 1. Expiry: remove expired batches
        for sku in stock:
            new_batches = []
            for batch in stock[sku]:
                quantity, unit_cost, expiry_day = batch
                if expiry_day < day:
                    write_offs += quantity * unit_cost
                else:
                    new_batches.append(batch)
            stock[sku] = new_batches
        
        # 2. Arrivals: reorder due to arrive
        for sku in list(reorder_in_transit.keys()):
            if reorder_in_transit[sku] == day:
                qty = products[sku]['reorder_qty']
                cost = products[sku]['standard_cost']
                expiry_day = day + products[sku]['shelf_life']
                stock[sku].append((qty, cost, expiry_day))
                del reorder_in_transit[sku]
        
        # 3. Events of the day
        if day in events_by_day:
            for event_type, sku, quantity, price in events_by_day[day]:
                if event_type == 'RECEIVE':
                    # Add to backorders first, then create new batch
                    unit_cost = price
                    expiry_day = day + products[sku]['shelf_life']
                    
                    # Fill backorders first
                    remaining_qty = quantity
                    while remaining_qty > 0 and backorders[sku]:
                        bo_qty, bo_price = backorders[sku][0]
                        if bo_qty <= remaining_qty:
                            # Backorder fully filled
                            revenue += bo_qty * bo_price * BACKORDER_DISCOUNT
                            cogs += bo_qty * unit_cost
                            remaining_qty -= bo_qty
                            backorders[sku].popleft()
                        else:
                            # Partially fill backorder
                            revenue += remaining_qty * bo_price * BACKORDER_DISCOUNT
                            cogs += remaining_qty * unit_cost
                            backorders[sku][0] = (bo_qty - remaining_qty, bo_price)
                            remaining_qty = 0
                    
                    if remaining_qty > 0:
                        stock[sku].append((remaining_qty, unit_cost, expiry_day))
                elif event_type == 'ORDER':
                    # Fill from stock (earliest expiry first)
                    order_qty = quantity
                    order_price = price
                    
                    # Sort batches by expiry day and then by arrival day (FIFO)
                    # We'll sort batches to process earliest expiry first
                    sorted_batches = []
                    for batch in stock[sku]:
                        sorted_batches.append((batch[2], batch[1], batch[0], batch))
                    sorted_batches.sort()  # Sort by expiry_day, then unit_cost (arbitrary)
                    
                    filled_qty = 0
                    new_stock = []
                    for _, _, batch_qty, batch in sorted_batches:
                        if order_qty <= 0:
                            break
                        if batch_qty <= order_qty:
                            # Use entire batch
                            revenue += batch_qty * order_price
                            cogs += batch_qty * batch[1]  # unit_cost from batch
                            order_qty -= batch_qty
                            filled_qty += batch_qty
                        else:
                            # Partially use batch
                            revenue += order_qty * order_price
                            cogs += order_qty * batch[1]
                            new_batch = (batch_qty - order_qty, batch[1], batch[2])
                            new_stock.append(new_batch)
                            order_qty = 0
                            filled_qty += batch_qty
                    
                    # If there are unfilled quantities, create backorder
                    if order_qty > 0:
                        backorders[sku].append((order_qty, order_price))
                    
                    # Remove used batches from stock
                    # We have to rebuild the stock list without the used ones
                    # This is a bit tricky because we already sorted them
                    # Let's use a different approach: mark which batches are used
                    used_batches = set()
                    for i, batch in enumerate(stock[sku]):
                        if (batch[2], batch[1], batch[0]) in [(b[2], b[1], b[0]) for b in sorted_batches]:
                            # Check if this batch was used
                            pass  # We'll handle it later
                    
                    # Simple approach: remove all used batches, keep rest
                    # This is a bit inefficient but works
                    new_stock = []
                    remaining_order_qty = quantity
                    
                    # Create a copy of stock to iterate over and update the original
                    temp_stock = list(stock[sku])
                    stock[sku] = []
                    
                    for batch in temp_stock:
                        batch_qty, unit_cost, expiry_day = batch
                        if remaining_order_qty <= 0:
                            stock[sku].append(batch)
                            continue
                        
                        if batch_qty <= remaining_order_qty:
                            # Use entire batch
                            revenue += batch_qty * order_price
                            cogs += batch_qty * unit_cost
                            remaining_order_qty -= batch_qty
                        else:
                            # Partially use batch
                            revenue += remaining_order_qty * order_price
                            cogs += remaining_order_qty * unit_cost
                            new_batch = (batch_qty - remaining_order_qty, unit_cost, expiry_day)
                            stock[sku].append(new_batch)
                            remaining_order_qty = 0
                    
                    # Reorder check: only after ORDER events
                    total_on_hand = sum(batch[0] for batch in stock[sku])
                    if total_on_hand < products[sku]['reorder_point']:
                        if sku not in reorder_in_transit:
                            reorder_in_transit[sku] = day + LEAD_TIME
    
    # After day 20, calculate cancellation penalties
    unfilled_backorder_units = sum(qty for bo_list in backorders.values() for qty, _ in bo_list)
    final_answer = revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units
    
    return round(final_answer, 2)
