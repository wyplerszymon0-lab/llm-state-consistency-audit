<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T11:05:56+00:00 -->

```python
import math

def run() -> float:
    # Constants
    LEAD_TIME = 2
    BACKORDER_DISCOUNT = 0.90
    CANCELLATION_PENALTY = 2.00

    # SKU configuration
    SKU_INFO = {
        'A': {'shelf_life': 5, 'reorder_point': 8, 'reorder_qty': 20, 'standard_cost': 4.00},
        'B': {'shelf_life': 30, 'reorder_point': 5, 'reorder_qty': 10, 'standard_cost': 12.50},
        'C': {'shelf_life': 3, 'reorder_point': 4, 'reorder_qty': 12, 'standard_cost': 2.20},
    }

    # Events as listed
    raw_events = [
        (1,  'RECEIVE', 'A', 30, 3.80),
        (1,  'RECEIVE', 'B', 8,  12.00),
        (1,  'RECEIVE', 'C', 10, 2.00),
        (2,  'ORDER',   'A', 12, 7.50),
        (2,  'ORDER',   'C', 4,  4.00),
        (3,  'RECEIVE', 'A', 10, 3.90),
        (3,  'ORDER',   'B', 6,  20.00),
        (4,  'ORDER',   'B', 5,  21.00),
        (4,  'ORDER',   'C', 3,  4.20),
        (5,  'ORDER',   'A', 15, 7.40),
        (6,  'ORDER',   'C', 2,  4.10),
        (7,  'ORDER',   'A', 9,  7.60),
        (8,  'ORDER',   'A', 5,  7.60),
        (8,  'RECEIVE', 'A', 2,  3.95),
        (9,  'ORDER',   'C', 11, 4.00),
        (10, 'ORDER',   'B', 8,  20.50),
        (10, 'ORDER',   'C', 2,  4.00),
        (12, 'ORDER',   'A', 10, 7.80),
        (13, 'ORDER',   'A', 1,  7.80),
        (14, 'ORDER',   'C', 5,  4.30),
        (15, 'ORDER',   'C', 3,  4.30),
        (16, 'ORDER',   'A', 25, 7.90),
        (18, 'ORDER',   'B', 9,  22.00),
        (19, 'ORDER',   'B', 4,  22.00),
        (19, 'ORDER',   'A', 16, 8.00),
        (20, 'ORDER',   'C', 10, 4.50),
    ]

    # Build day -> list of events mapping (maintaining order)
    events_by_day = {}
    for ev in raw_events:
        day = ev[0]
        events_by_day.setdefault(day, []).append(ev[1:])  # store (type, sku, qty, price)

    # SKU state initialization
    state = {}
    for sku, info in SKU_INFO.items():
        state[sku] = {
            'batches': [],                # list of dicts: qty, unit_cost, expiry_day, arrival_day
            'backorders': [],             # list of tuples: (qty, price)
            'reorder_in_transit': None,   # arrival_day or None
            'reorder_point': info['reorder_point'],
            'reorder_qty': info['reorder_qty'],
            'standard_cost': info['standard_cost'],
            'shelf_life': info['shelf_life'],
        }

    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    # Helper functions
    def process_receive(sku: str, qty: int, unit_cost: float, day: int):
        nonlocal revenue, cogs
        backorders = state[sku]['backorders']
        batches = state[sku]['batches']

        # Fill backorders first
        while qty > 0 and backorders:
            bo_qty, bo_price = backorders[0]
            fill_qty = min(qty, bo_qty)
            revenue += bo_price * BACKORDER_DISCOUNT * fill_qty
            cogs += unit_cost * fill_qty
            if fill_qty == bo_qty:
                backorders.pop(0)
            else:
                backorders[0] = (bo_qty - fill_qty, bo_price)
            qty -= fill_qty

        # Remaining quantity becomes a new batch
        if qty > 0:
            batches.append({
                'qty': qty,
                'unit_cost': unit_cost,
                'expiry_day': day + state[sku]['shelf_life'],
                'arrival_day': day
            })
            # Keep batches sorted by expiry, then arrival
            batches.sort(key=lambda b: (b['expiry_day'], b['arrival_day']))

    def process_order(sku: str, qty: int, price: float, day: int):
        nonlocal revenue, cogs
        batches = state[sku]['batches']
        backorders = state[sku]['backorders']

        remaining = qty
        # Use inventory first, FIFO by expiry
        while remaining > 0 and batches:
            batch = batches[0]
            use_qty = min(remaining, batch['qty'])
            revenue += price * use_qty
            cogs += batch['unit_cost'] * use_qty
            batch['qty'] -= use_qty
            if batch['qty'] == 0:
                batches.pop(0)
            remaining -= use_qty

        # Unfulfilled units become backorder
        if remaining > 0:
            backorders.append((remaining, price))

        # Reorder check
        units_on_hand = sum(b['qty'] for b in batches)
        if (units_on_hand < state[sku]['reorder_point'] and
                state[sku]['reorder_in_transit'] is None):
            arrival_day = day + LEAD_TIME
            if arrival_day <= 20:  # only schedule if it can arrive within simulation
                state[sku]['reorder_in_transit'] = arrival_day
            # else: do not schedule (never arrives)

    # Simulation loop
    for day in range(1, 21):
        # 1. Expiry
        for sku in SKU_INFO:
            batches = state[sku]['batches']
            while batches and batches[0]['expiry_day'] < day:
                batch = batches.pop(0)
                write_offs += batch['qty'] * batch['unit_cost']

        # 2. Arrivals
        for sku in SKU_INFO:
            if state[sku]['reorder_in_transit'] == day:
                qty = state[sku]['reorder_qty']
                unit_cost = state[sku]['standard_cost']
                process_receive(sku, qty, unit_cost, day)
                state[sku]['reorder_in_transit'] = None

        # 3. Events
        for ev in events_by_day.get(day, []):
            ev_type, sku, qty, price = ev
            if ev_type == 'RECEIVE':
                process_receive(sku, qty, price, day)  # price is unit_cost here
            elif ev_type == 'ORDER':
                process_order(sku, qty, price, day)

    # After day 20, compute unfilled backorder units
    total_unfilled = sum(q for sku in SKU_INFO for q, _ in state[sku]['backorders'])
    result = revenue - cogs - write_offs - CANCELLATION_PENALTY * total_unfilled
    return round(result + 1e-9, 2)  # small epsilon to avoid rounding issues

# The module can be tested by calling run()
if __name__ == "__main__":
    print(run())
```