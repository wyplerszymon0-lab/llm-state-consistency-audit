def run() -> float:
    SKU_SETTINGS = {
        'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20}
    }
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    SKUs = list(SKU_SETTINGS.keys())
    EVENTS = [
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

    days = list(range(1, 21))
    stock = {sku: [] for sku in SKUs}
    backorders = {sku: [] for sku in SKUs}
    reorder_in_transit = {sku: None for sku in SKUs}
    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    def expire_stock(day):
        for sku in SKUs:
            for batch in stock[sku]:
                if batch[2] < day:
                    write_offs += batch[0] * batch[1]
            stock[sku] = [batch for batch in stock[sku] if batch[2] >= day]

    def receive(sku, quantity, unit_cost):
        for batch in stock[sku]:
            if batch[2] < days[0]:
                write_offs += batch[0] * batch[1]
        stock[sku].append((quantity, unit_cost, days[0] + SKU_SETTINGS[sku]['shelf_life']))

    def order(sku, quantity, unit_price):
        for batch in sorted(stock[sku], key=lambda x: (x[2], -x[0])):
            if quantity > 0:
                sold = min(quantity, batch[0])
                quantity -= sold
                revenue += sold * unit_price
                cogs += sold * batch[1]
                stock[sku][stock[sku].index(batch)] = (batch[0] - sold, batch[1], batch[2])
        if quantity > 0:
            backorders[sku].append((quantity, unit_price))

    def reorder(sku, quantity, unit_cost):
        stock[sku].append((quantity, unit_cost, days[0] + LEAD_TIME))
        reorder_in_transit[sku] = None

    for day in days:
        expire_stock(day)
        if reorder_in_transit[day] is not None:
            reorder(reorder_in_transit[day][0], reorder_in_transit[day][1], SKU_SETTINGS[reorder_in_transit[day][0]]['standard_cost'])
        for event in EVENTS:
            if event[0] == day:
                if event[1] == 'RECEIVE':
                    receive(event[2], event[3], event[4])
                elif event[1] == 'ORDER':
                    order(event[2], event[3], event[4])
        for sku in SKUs:
            if stock[sku] and stock[sku][-1][0] < SKU_SETTINGS[sku]['reorder_point'] and reorder_in_transit[sku] is None:
                reorder_in_transit[sku] = (sku, SKU_SETTINGS[sku]['reorder_qty'])

    unfilled_backorder_units = sum(backorder[0] for backorder in backorders.values())
    return round(revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units, 2)

print(run())
