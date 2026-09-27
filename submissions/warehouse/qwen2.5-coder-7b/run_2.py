from collections import deque

def run() -> float:
    SKU_A = 'A'
    SKU_B = 'B'
    SKU_C = 'C'

    SHLF_LIFE_A = 5
    SHLF_LIFE_B = 30
    SHLF_LIFE_C = 3

    REORD_PT_A = 8
    REORD_PT_B = 5
    REORD_PT_C = 4

    REORD_QTY_A = 20
    REORD_QTY_B = 10
    REORD_QTY_C = 12

    STD_COST_A = 4.00
    STD_COST_B = 12.50
    STD_COST_C = 2.20

    LEAD_TIME = 2
    BACKORD_DISC = 0.90
    CANCELL_PENALTY = 2.00

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

    def process_events(events, sku, shelf_life, reorder_point, reorder_qty, standard_cost):
        stock = []
        backorders = deque()
        reorder_in_transit = None
        revenue = 0.0
        cogs = 0.0
        write_offs = 0.0

        def expire_batches():
            nonlocal write_offs
            while stock and stock[0][2] < day:
                batch = stock.pop(0)
                write_offs += batch[0] * batch[1]

        def receive(quantity, unit_cost):
            nonlocal revenue, cogs
            while backorders and quantity > 0:
                backorder_quantity, backorder_price = backorders.popleft()
                if backorder_quantity <= quantity:
                    revenue += backorder_quantity * backorder_price * BACKORD_DISC
                    cogs += backorder_quantity * unit_cost
                    quantity -= backorder_quantity
                else:
                    revenue += quantity * backorder_price * BACKORD_DISC
                    cogs += quantity * unit_cost
                    backorders.appendleft((backorder_quantity - quantity, backorder_price))
                    quantity = 0

            if quantity > 0:
                stock.append((quantity, unit_cost, day + shelf_life))

        def order(quantity, unit_price):
            nonlocal revenue, cogs
            filled_quantity = 0
            while stock and filled_quantity < quantity:
                batch_quantity, batch_cost, batch_expiry = stock[0]
                if batch_expiry <= day:
                    stock.pop(0)
                else:
                    if batch_quantity > quantity - filled_quantity:
                        filled_quantity = quantity
                    else:
                        filled_quantity += batch_quantity
                        stock.popleft()

            if filled_quantity < quantity:
                backorders.append((quantity - filled_quantity, unit_price))

            revenue += filled_quantity * unit_price
            cogs += filled_quantity * batch_cost

        for day, event_type, event_sku, event_quantity, event_price in events:
            if event_sku != sku:
                continue

            if event_type == 'RECEIVE':
                receive(event_quantity, event_price)
            elif event_type == 'ORDER':
                order(event_quantity, event_price)

            if reorder_in_transit and day == reorder_in_transit + LEAD_TIME:
                receive(reorder_qty, standard_cost)
                reorder_in_transit = None

        if len(stock) > 0:
            reorder_in_transit = day

        return revenue, cogs, write_offs, sum(backorder[0] for backorder in backorders)

    def calculate_answer():
        revenue_A, cogs_A, write_offs_A, backorder_A = process_events(events, SKU_A, SHLF_LIFE_A, REORD_PT_A, REORD_QTY_A, STD_COST_A)
        revenue_B, cogs_B, write_offs_B, backorder_B = process_events(events, SKU_B, SHLF_LIFE_B, REORD_PT_B, REORD_QTY_B, STD_COST_B)
        revenue_C, cogs_C, write_offs_C, backorder_C = process_events(events, SKU_C, SHLF_LIFE_C, REORD_PT_C, REORD_QTY_C, STD_COST_C)

        return round((revenue_A + revenue_B + revenue_C) - (cogs_A + cogs_B + cogs_C) - (write_offs_A + write_offs_B + write_offs_C) - CANCELL_PENALTY * (backorder_A + backorder_B + backorder_C), 2)

    return calculate_answer()

# The answer is run() when the module is executed
