<!-- model: ollama:qwen2.5-coder:7b | prompt v1 | 2026-09-26T17:18:43+00:00 -->

```python
from collections import deque

def run() -> float:
    SKU_A = 'A'
    SKU_B = 'B'
    SKU_C = 'C'
    
    shelf_life = {
        SKU_A: 5,
        SKU_B: 30,
        SKU_C: 3
    }
    reorder_point = {
        SKU_A: 8,
        SKU_B: 5,
        SKU_C: 4
    }
    reorder_qty = {
        SKU_A: 20,
        SKU_B: 10,
        SKU_C: 12
    }
    standard_cost = {
        SKU_A: 4.00,
        SKU_B: 12.50,
        SKU_C: 2.20
    }
    
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00
    
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
    
    def process_day(day):
        nonlocal stock, backorders, reorder_in_transit
        
        # Expiry
        for sku, batches in list(stock.items()):
            stock[sku] = [batch for batch in batches if batch[2] >= day]
            write_offs += sum(batch[0] * batch[1] for batch in batches if batch[2] < day)
        
        # Arrivals
        if day in reorder_in_transit:
            sku = reorder_in_transit[day]
            stock[sku].append((reorder_qty[sku], standard_cost[sku], day + shelf_life[sku]))
            del reorder_in_transit[day]
        
        # Events
        for event in events:
            if event[0] == day:
                if event[1] == 'RECEIVE':
                    sku, quantity, unit_cost = event[2], event[3], event[4]
                    for _ in range(quantity):
                        while backorders[sku] and backorders[sku][0][0] > 0:
                            backorder_qty, backorder_price = backorders[sku][0]
                            if backorder_qty > 1:
                                backorders[sku][0] = (backorder_qty - 1, backorder_price)
                                revenue += backorder_price * BACKORDER_DISCOUNT
                                cogs += unit_cost
                            else:
                                backorders[sku].popleft()
                                revenue += backorder_price * BACKORDER_DISCOUNT
                                cogs += unit_cost
                        if backorders[sku]:
                            break
                        stock[sku].append((1, unit_cost, day))
                elif event[1] == 'ORDER':
                    sku, quantity, price = event[2], event[3], event[4]
                    filled_quantity = 0
                    for batch in sorted(stock[sku], key=lambda x: (x[2], x[1])):
                        if batch[0] <= quantity:
                            filled_quantity += batch[0]
                            revenue += batch[0] * price
                            cogs += batch[0] * batch[1]
                            stock[sku].remove(batch)
                            quantity -= batch[0]
                        else:
                            filled_quantity += quantity
                            revenue += quantity * price
                            cogs += quantity * batch[1]
                            stock[sku].remove(batch)
                            stock[sku].append((batch[0] - quantity, batch[1], batch[2]))
                            break
                    if quantity > 0:
                        backorders[sku].append((quantity, price))
        
        # Reorder check
        for sku in reorder_in_transit:
            if day == reorder_in_transit[sku] + LEAD_TIME and stock[sku][0][0] < reorder_point[sku]:
                reorder_in_transit[day + LEAD_TIME] = sku
    
    revenue = 0
    cogs = 0
    write_offs = 0
    stock = {SKU_A: [], SKU_B: [], SKU_C: []}
    backorders = {SKU_A: deque(), SKU_B: deque(), SKU_C: deque()}
    reorder_in_transit = {}
    
    for day in range(1, 21):
        process_day(day)
    
    unfilled_backorder_units = sum(backorder[0] for backorder in backorders[SKU_A]) + sum(backorder[0] for backorder in backorders[SKU_B]) + sum(backorder[0] for backorder in backorders[SKU_C])
    
    return round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)
```