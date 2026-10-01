from collections import deque

LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

class SKU:
    def __init__(self, shelf_life, reorder_point, reorder_qty, standard_cost):
        self.shelf_life = shelf_life
        self.reorder_point = reorder_point
        self.reorder_qty = reorder_qty
        self.standard_cost = standard_cost
        self.stock = []  # List of (quantity, unit_cost, expiry_day)
        self.backorders = deque()  # Queue of (quantity, unit_price)
        self.in_transit = False

def receive(sku, quantity, unit_cost, day):
    expiry_day = day + sku.shelf_life
    batch = (quantity, unit_cost, expiry_day)
    sku.stock.append(batch)
    while sku.backorders and sku.backorders[0][0] <= quantity:
        backorder_qty, backorder_price = sku.backorders.popleft()
        revenue = backorder_qty * backorder_price * BACKORDER_DISCOUNT
        cogs = backorder_qty * unit_cost
        return revenue, cogs, quantity - backorder_qty
    if sku.backorders:
        backorder_qty, _ = sku.backorders[0]
        revenue = backorder_qty * sku.backorders[0][1] * BACKORDER_DISCOUNT
        cogs = backorder_qty * unit_cost
        sku.backorders[0] = (sku.backorders[0][0] - quantity, sku.backorders[0][1])
        return revenue, cogs, 0
    return 0, 0, quantity

def order(sku, quantity, price, day):
    revenue = 0
    cogs = 0
    while sku.stock and quantity > 0:
        batch_qty, batch_cost, expiry_day = sku.stock.pop(0)
        use_qty = min(quantity, batch_qty)
        revenue += use_qty * price
        cogs += use_qty * batch_cost
        quantity -= use_qty
        if use_qty < batch_qty:
            sku.stock.insert(0, (batch_qty - use_qty, batch_cost, expiry_day))
    if quantity > 0:
        sku.backorders.append((quantity, price))
    if len(sku.stock) < sku.reorder_point and not sku.in_transit:
        sku.in_transit = True
        return revenue, cogs, True
    return revenue, cogs, False

def run():
    skus = {
        'A': SKU(5, 8, 20, 4.00),
        'B': SKU(30, 5, 10, 12.50),
        'C': SKU(3, 4, 12, 2.20),
    }
    
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
        (20, 'ORDER', 'C', 10, 4.50),
    ]
    
    revenue = 0
    cogs = 0
    write_offs = 0
    
    for day in range(1, 21):
        # Expiry
        for sku in skus.values():
            sku.stock = [batch for batch in sku.stock if batch[2] >= day]
        
        # Arrivals
        for sku in skus.values():
            if sku.in_transit:
                sku.in_transit = False
                receive(sku, sku.reorder_qty, sku.standard_cost, day)
        
        # Events
        for day_event in events:
            if day_event[0] == day:
                event_type, sku_name, quantity, price = day_event[1], day_event[2], day_event[3], day_event[4]
                sku = skus[sku_name]
                if event_type == 'RECEIVE':
                    received_revenue, received_cogs, _ = receive(sku, quantity, price, day)
                    revenue += received_revenue
                    cogs += received_cogs
                elif event_type == 'ORDER':
                    ordered_revenue, ordered_cogs, placed_reorder = order(sku, quantity, price, day)
                    revenue += ordered_revenue
                    cogs += ordered_cogs
                    if placed_reorder and day + LEAD_TIME <= 20:
                        sku.in_transit = True
    
    # Final write-offs and cancellation penalties
    for sku in skus.values():
        for quantity, _ in sku.backorders:
            write_offs += quantity * sku.standard_cost
        for batch_qty, batch_cost, expiry_day in sku.stock:
            write_offs += batch_qty * batch_cost
        for quantity, _ in sku.backorders:
            revenue -= quantity * CANCELLATION_PENALTY
    
    final_answer = revenue - cogs - write_offs
    return round(final_answer, 2)

if __name__ == "__main__":
    print(run())
