<!-- model: ollama:gpt-oss:20b | prompt v1 | 2026-10-16T11:17:42+00:00 -->

```python
import sys
from collections import defaultdict

# constants
LEAD_TIME = 2
BACKORDER_DISCOUNT = 0.90
CANCELLATION_PENALTY = 2.00

def run() -> float:
    # SKU configuration
    skus = {
        'A': {
            'shelf_life': 5,
            'reorder_point': 8,
            'reorder_qty': 20,
            'standard_cost': 4.00,
            'batches': [],
            'backorders': [],
            'arrival_day': None,
        },
        'B': {
            'shelf_life': 30,
            'reorder_point': 5,
            'reorder_qty': 10,
            'standard_cost': 12.50,
            'batches': [],
            'backorders': [],
            'arrival_day': None,
        },
        'C': {
            'shelf_life': 3,
            'reorder_point': 4,
            'reorder_qty': 12,
            'standard_cost': 2.20,
            'batches': [],
            'backorders': [],
            'arrival_day': None,
        },
    }

    # Event list as given
    raw_events = [
        "1, RECEIVE, A, 30, 3.80",
        "1, RECEIVE, B, 8, 12.00",
        "1, RECEIVE, C, 10, 2.00",
        "2, ORDER, A, 12, 7.50",
        "2, ORDER, C, 4, 4.00",
        "3, RECEIVE, A, 10, 3.90",
        "3, ORDER, B, 6, 20.00",
        "4, ORDER, B, 5, 21.00",
        "4, ORDER, C, 3, 4.20",
        "5, ORDER, A, 15, 7.40",
        "6, ORDER, C, 2, 4.10",
        "7, ORDER, A, 9, 7.60",
        "8, ORDER, A, 5, 7.60",
        "8, RECEIVE, A, 2, 3.95",
        "9, ORDER, C, 11, 4.00",
        "10, ORDER, B, 8, 20.50",
        "10, ORDER, C, 2, 4.00",
        "12, ORDER, A, 10, 7.80",
        "13, ORDER, A, 1, 7.80",
        "14, ORDER, C, 5, 4.30",
        "15, ORDER, C, 3, 4.30",
        "16, ORDER, A, 25, 7.90",
        "18, ORDER, B, 9, 22.00",
        "19, ORDER, B, 4, 22.00",
        "19, ORDER, A, 16, 8.00",
        "20, ORDER, C, 10, 4.50",
    ]

    # Parse events into a dict keyed by day
    events_by_day = defaultdict(list)
    for line in raw_events:
        parts = [p.strip() for p in line.split(',')]
        day = int(parts[0])
        typ = parts[1]
        sku = parts[2]
        qty = int(parts[3])
        price = float(parts[4])
        events_by_day[day].append((typ, sku, qty, price))

    revenue = 0.0
    cogs = 0.0
    write_offs = 0.0

    # Simulation for days 1..20
    for d in range(1, 21):
        # 1. Expiry
        for sku in skus.values():
            new_batches = []
            for batch in sku['batches']:
                if batch['expiry'] < d:
                    write_offs += batch['qty'] * batch['cost']
                else:
                    new_batches.append(batch)
            sku['batches'] = new_batches

        # 2. Arrivals
        for sku in skus.values():
            if sku['arrival_day'] == d:
                # Receive reorder
                qty = sku['reorder_qty']
                unit_cost = sku['standard_cost']
                # Fill backorders first
                incoming = qty
                backorders = sku['backorders']
                while incoming > 0 and backorders:
                    bo_qty, bo_price = backorders[0]
                    if incoming >= bo_qty:
                        revenue += bo_price * BACKORDER_DISCOUNT * bo_qty
                        cogs += unit_cost * bo_qty
                        incoming -= bo_qty
                        backorders.pop(0)
                    else:
                        revenue += bo_price * BACKORDER_DISCOUNT * incoming
                        cogs += unit_cost * incoming
                        backorders[0][0] -= incoming
                        incoming = 0
                # Remaining becomes a new batch
                if incoming > 0:
                    sku['batches'].append({
                        'expiry': d + sku['shelf_life'],
                        'qty': incoming,
                        'cost': unit_cost,
                        'recv_day': d
                    })
                sku['arrival_day'] = None

        # 3. Events of the day
        for typ, sku_key, qty, price in events_by_day.get(d, []):
            sku = skus[sku_key]
            if typ == 'RECEIVE':
                # Receive event
                incoming = qty
                unit_cost = price
                backorders = sku['backorders']
                while incoming > 0 and backorders:
                    bo_qty, bo_price = backorders[0]
                    if incoming >= bo_qty:
                        revenue += bo_price * BACKORDER_DISCOUNT * bo_qty
                        cogs += unit_cost * bo_qty
                        incoming -= bo_qty
                        backorders.pop(0)
                    else:
                        revenue += bo_price * BACKORDER_DISCOUNT * incoming
                        cogs += unit_cost * incoming
                        backorders[0][0] -= incoming
                        incoming = 0
                if incoming > 0:
                    sku['batches'].append({
                        'expiry': d + sku['shelf_life'],
                        'qty': incoming,
                        'cost': unit_cost,
                        'recv_day': d
                    })
            elif typ == 'ORDER':
                # Order event
                order_qty = qty
                order_price = price
                batches = sku['batches']
                # Sort batches by expiry, then received day
                batches.sort(key=lambda b: (b['expiry'], b['recv_day']))
                while order_qty > 0 and batches:
                    batch = batches[0]
                    use = min(batch['qty'], order_qty)
                    revenue += order_price * use
                    cogs += batch['cost'] * use
                    batch['qty'] -= use
                    order_qty -= use
                    if batch['qty'] == 0:
                        batches.pop(0)
                # Any unfilled quantity becomes backorder
                if order_qty > 0:
                    sku['backorders'].append([order_qty, order_price])
                # Reorder check
                total_on_hand = sum(b['qty'] for b in batches)
                if total_on_hand < sku['reorder_point'] and sku['arrival_day'] is None:
                    arrival_day = d + LEAD_TIME
                    sku['arrival_day'] = arrival_day  # may be >20, will never arrive
            else:
                # Unknown event type, ignore
                pass

    # After day 20: compute cancellation penalty
    unfilled_backorders = sum(
        sum(bo[0] for bo in sku['backorders']) for sku in skus.values()
    )
    penalty = unfilled_backorders * CANCELLATION_PENALTY

    answer = revenue - cogs - write_offs - penalty
    # Round to 2 decimal places
    return round(answer, 2)

# If the module is run directly, print the result (ignored by tests)
if __name__ == "__main__":
    print(run())
```