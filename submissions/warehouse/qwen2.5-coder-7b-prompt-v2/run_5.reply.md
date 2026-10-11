<!-- model: ollama:qwen2.5-coder:7b | prompt v2 | 2026-10-10T11:45:49+00:00 -->

```python
from collections import defaultdict, deque

def run() -> float:
    SKU_SETTINGS = {
        'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
    }
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00
    
    def process_day(day):
        nonlocal stock, backorders, reorder_in_transit
        
        # Expiry
        for sku in stock:
            stock[sku] = [(q, c, e) for q, c, e in stock[sku] if e >= day]
        
        # Arrivals
        if day in reorder_in_transit:
            sku = reorder_in_transit[day]
            stock[sku].append((SKU_SETTINGS[sku]['reorder_qty'], SKU_SETTINGS[sku]['standard_cost'], day + SKU_SETTINGS[sku]['shelf_life']))
            reorder_in_transit.pop(day)
        
        # Events
        events = sorted(events_by_day[day])
        for event in events:
            if event[0] == 'RECEIVE':
                sku, quantity, price = event[1], event[2], event[3]
                for _ in range(quantity):
                    while backorders[sku] and backorders[sku][0][0] > 0:
                        backorder_quantity, backorder_price = backorders[sku][0]
                        filled_quantity = min(backorder_quantity, 1)
                        revenue += filled_quantity * backorder_price * BACKORDER_DISCOUNT
                        cogs += filled_quantity * price
                        backorders[sku][0] = (backorder_quantity - filled_quantity, backorder_price)
                        if backorders[sku][0][0] == 0:
                            backorders[sku].popleft()
                    stock[sku].append((1, price, day))
            elif event[0] == 'ORDER':
                sku, quantity, price = event[1], event[2], event[3]
                total_filled = 0
                for q, c, e in sorted(stock[sku], key=lambda x: (x[2], x[1])):
                    if total_filled + q >= quantity:
                        filled_quantity = quantity - total_filled
                        revenue += filled_quantity * price
                        cogs += filled_quantity * c
                        if filled_quantity == q:
                            stock[sku].popleft()
                        else:
                            stock[sku][0] = (q - filled_quantity, c, e)
                        total_filled = quantity
                        break
                if total_filled < quantity:
                    backorders[sku].append((quantity - total_filled, price))
        
        # Reorder check
        for sku, details in stock.items():
            if len(details) < SKU_SETTINGS[sku]['reorder_point'] and day + LEAD_TIME <= 20 and sku not in reorder_in_transit:
                reorder_in_transit[day + LEAD_TIME] = sku
    
    stock = defaultdict(list)
    backorders = defaultdict(deque)
    reorder_in_transit = {}
    events_by_day = defaultdict(list)
    
    # Parse events
    events = [
        ('RECEIVE', 'A', 30, 3.80), ('RECEIVE', 'B', 8, 12.00), ('RECEIVE', 'C', 10, 2.00),
        ('ORDER', 'A', 12, 7.50), ('ORDER', 'C', 4, 4.00), ('RECEIVE', 'A', 10, 3.90), ('ORDER', 'B', 6, 20.00),
        ('ORDER', 'B', 5, 21.00), ('ORDER', 'C', 3, 4.20), ('ORDER', 'A', 15, 7.40), ('ORDER', 'C', 2, 4.10),
        ('ORDER', 'A', 9, 7.60), ('ORDER', 'A', 5, 7.60), ('RECEIVE', 'A', 2, 3.95), ('ORDER', 'C', 11, 4.00),
        ('ORDER', 'B', 8, 20.50), ('ORDER', 'C', 2, 4.00), ('ORDER', 'A', 10, 7.80), ('ORDER', 'A', 1, 7.80),
        ('ORDER', 'C', 5, 4.30), ('ORDER', 'C', 3, 4.30), ('ORDER', 'A', 25, 7.90), ('ORDER', 'B', 9, 22.00),
        ('ORDER', 'B', 4, 22.00), ('ORDER', 'A', 16, 8.00), ('ORDER', 'C', 10, 4.50)
    ]
    for event in events:
        day = event[0] == 'RECEIVE' and day + 1 or day
        events_by_day[day].append((event[0], event[1], event[2], event[3]))
    
    for day in range(1, 21):
        process_day(day)
    
    # Calculate final answer
    unfilled_backorder_units = sum(q for _, q in backorders.values())
    answer = revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units
    return round(answer, 2)

print(run())
```

This Python program simulates the perishable warehouse scenario as described, computing the final answer based on the given rules and events.