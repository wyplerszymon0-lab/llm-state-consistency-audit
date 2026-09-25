# Perishable warehouse

Simulate a warehouse that stocks three products over days 1 to 20 (inclusive).

## Product settings

| SKU | shelf_life (days) | reorder_point | reorder_qty | standard_cost |
|---|---|---|---|---|
| A | 5 | 8 | 20 | 4.00 |
| B | 30 | 5 | 10 | 12.50 |
| C | 3 | 4 | 12 | 2.20 |

Constants: `LEAD_TIME = 2`, `BACKORDER_DISCOUNT = 0.90`, `CANCELLATION_PENALTY = 2.00`.

## Events

Columns: `day, type, sku, quantity, price`. For `RECEIVE` the price is the unit
cost; for `ORDER` it is the customer's unit selling price. Events on the same day
are processed in the order listed.

```
1, RECEIVE, A, 30, 3.80
1, RECEIVE, B, 8, 12.00
1, RECEIVE, C, 10, 2.00
2, ORDER, A, 12, 7.50
2, ORDER, C, 4, 4.00
3, RECEIVE, A, 10, 3.90
3, ORDER, B, 6, 20.00
4, ORDER, B, 5, 21.00
4, ORDER, C, 3, 4.20
5, ORDER, A, 15, 7.40
6, ORDER, C, 2, 4.10
7, ORDER, A, 9, 7.60
8, ORDER, A, 5, 7.60
8, RECEIVE, A, 2, 3.95
9, ORDER, C, 11, 4.00
10, ORDER, B, 8, 20.50
10, ORDER, C, 2, 4.00
12, ORDER, A, 10, 7.80
13, ORDER, A, 1, 7.80
14, ORDER, C, 5, 4.30
15, ORDER, C, 3, 4.30
16, ORDER, A, 25, 7.90
18, ORDER, B, 9, 22.00
19, ORDER, B, 4, 22.00
19, ORDER, A, 16, 8.00
20, ORDER, C, 10, 4.50
```

## State

- Stock of each SKU is a set of **batches** `(quantity, unit_cost, expiry_day)`.
  A batch received on day `d` has `expiry_day = d + shelf_life`. It can be sold on
  any day `<= expiry_day`.
- Each SKU has a FIFO queue of **backorders** `(quantity, unit_price)`.
- Each SKU has at most one **automatic reorder in transit** at a time.
- Running totals `revenue`, `cogs` (cost of goods sold) and `write_offs` start at 0.

## Daily procedure

For every day `d` from 1 to 20, even days with no events, in this order:

1. **Expiry**: remove every batch with `expiry_day < d`. Add
   `quantity * unit_cost` of each removed batch to `write_offs`.
2. **Arrivals**: an automatic reorder due on day `d` arrives. It is received exactly
   like a `RECEIVE` of `reorder_qty` units at `standard_cost`. That SKU no longer
   has a reorder in transit.
3. **Events** of day `d`, in the listed order.

## Receiving (RECEIVE events and reorder arrivals)

Incoming units first fill that SKU's backorders, oldest backorder first (a backorder
may be partly filled). Each backordered unit filled this way adds
`unit_price * BACKORDER_DISCOUNT` to `revenue` (the price from its original order)
and the incoming `unit_cost` to `cogs`. Any units left over become a new batch.

## Customer orders (ORDER events)

1. Fill the order from batches on hand, **earliest `expiry_day` first**. Ties go to the
   batch that was received earlier. Batches may be partly used. Each unit adds the
   order's `price` to `revenue` and its batch's `unit_cost` to `cogs`.
2. Units that cannot be filled are appended as one backorder
   `(unfilled_quantity, price)`.
3. **Reorder check** (only after ORDER events): if the SKU's units on hand are now
   below its `reorder_point` and it has no reorder in transit, place an automatic
   reorder that arrives on day `d + LEAD_TIME`. Reorders arriving after day 20 never
   arrive.

## Answer

After day 20, every unit still backordered costs `CANCELLATION_PENALTY`. The answer is
`revenue - cogs - write_offs - CANCELLATION_PENALTY * unfilled_backorder_units`,
rounded to 2 decimal places.
