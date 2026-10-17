import heapq
from collections import defaultdict

def run():
    # Constants
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00
    
    # Product settings
    products = {
        'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
    }
    
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
    
    # Initialize state
    stock = defaultdict(list)  # sku -> list of batches [(quantity, unit_cost, expiry_day)]
    backorders = defaultdict(list)  # sku -> list of backorders [(quantity, unit_price)]
    reorder_in_transit = defaultdict(int)  # sku -> day when reorder arrives (0 if none)
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0
    
    # Process events by day
    event_dict = defaultdict(list)
    for day, event_type, sku, quantity, price in events:
        event_dict[day].append((event_type, sku, quantity, price))
    
    # Process each day from 1 to 20
    for day in range(1, 21):
        # Expiry: remove expired batches
        for sku in stock:
            new_batches = []
            for quantity, unit_cost, expiry_day in stock[sku]:
                if expiry_day >= day:
                    new_batches.append((quantity, unit_cost, expiry_day))
                else:
                    write_offs += quantity * unit_cost
            stock[sku] = new_batches
        
        # Arrivals: handle reorders arriving today
        for sku in reorder_in_transit:
            if reorder_in_transit[sku] == day:
                qty = products[sku]['reorder_qty']
                cost = products[sku]['standard_cost']
                expiry_day = day + products[sku]['shelf_life']
                stock[sku].append((qty, cost, expiry_day))
                reorder_in_transit[sku] = 0
        
        # Process events for the day
        if day in event_dict:
            for event_type, sku, quantity, price in event_dict[day]:
                if event_type == 'RECEIVE':
                    # Receive units and fill backorders first
                    unit_cost = price
                    expiry_day = day + products[sku]['shelf_life']
                    
                    # Fill backorders first (FIFO)
                    remaining_quantity = quantity
                    new_backorders = []
                    while backorders[sku] and remaining_quantity > 0:
                        backorder_qty, backorder_price = backorders[sku].pop(0)
                        if backorder_qty <= remaining_quantity:
                            # Fill entire backorder
                            revenue += backorder_qty * backorder_price * BACKORDER_DISCOUNT
                            cogs += backorder_qty * unit_cost
                            remaining_quantity -= backorder_qty
                        else:
                            # Partially fill backorder
                            revenue += remaining_quantity * backorder_price * BACKORDER_DISCOUNT
                            cogs += remaining_quantity * unit_cost
                            backorder_qty -= remaining_quantity
                            remaining_quantity = 0
                            new_backorders.append((backorder_qty, backorder_price))
                    
                    backorders[sku] = new_backorders
                    
                    # Add remaining to stock as a new batch if any
                    if remaining_quantity > 0:
                        stock[sku].append((remaining_quantity, unit_cost, expiry_day))
                elif event_type == 'ORDER':
                    # Fill order from existing batches (earliest expiry first)
                    order_qty = quantity
                    order_price = price
                    
                    # Sort batches by expiry day and then by arrival date (we'll use a heap)
                    # We need to sort by expiry day, then by arrival date (but we don't track that directly)
                    # Since batches are added in order, we can just sort by expiry day
                    batch_heap = []
                    for i, (batch_qty, unit_cost, expiry_day) in enumerate(stock[sku]):
                        heapq.heappush(batch_heap, (expiry_day, i, batch_qty, unit_cost))
                    
                    remaining_qty = order_qty
                    new_stock = []
                    while batch_heap and remaining_qty > 0:
                        expiry_day, _, batch_qty, unit_cost = heapq.heappop(batch_heap)
                        if batch_qty <= remaining_qty:
                            # Use entire batch
                            revenue += batch_qty * order_price
                            cogs += batch_qty * unit_cost
                            remaining_qty -= batch_qty
                        else:
                            # Partially use batch
                            revenue += remaining_qty * order_price
                            cogs += remaining_qty * unit_cost
                            batch_qty -= remaining_qty
                            remaining_qty = 0
                            new_stock.append((batch_qty, unit_cost, expiry_day))
                    
                    # If we couldn't fulfill the entire order, add to backorders
                    if remaining_qty > 0:
                        backorders[sku].append((remaining_qty, order_price))
                    else:
                        # Update stock with remaining batches
                        while batch_heap:
                            expiry_day, _, batch_qty, unit_cost = heapq.heappop(batch_heap)
                            new_stock.append((batch_qty, unit_cost, expiry_day))
                    
                    # Update stock
                    stock[sku] = new_stock
                    
                    # Reorder check (after ORDER events)
                    total_on_hand = sum(qty for qty, _, _ in stock[sku])
                    if total_on_hand < products[sku]['reorder_point']:
                        if reorder_in_transit[sku] == 0:
                            reorder_in_transit[sku] = day + LEAD_TIME
                            if reorder_in_transit[sku] > 20:
                                reorder_in_transit[sku] = 0
    
    # Calculate final penalty for unfilled backorders
    unfilled_backorder_units = sum(qty for sku in backorders for qty, _ in backorders[sku])
    penalty = unfilled_backorder_units * CANCELLATION_PENALTY
    
    # Final calculation
    answer = revenue - cogs - write_offs - penalty
    return round(answer, 2)
