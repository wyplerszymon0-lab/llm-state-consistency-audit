The `ORDER, B, 5, 21.00` on day 4, and what follows from it on day 5:

- Before it, B has one batch `(2, 12.00, expiry 31)`: 8 units were received on day 1
  and 6 were sold on day 3. The day-3 order left 2 units on hand, below the reorder
  point 5, so a reorder of 10 units was placed then, arriving on day `3 + 2 = 5`.
- Day 4: 2 units are filled from the batch: revenue `+ 2 × 21.00 = 42.00`, cogs
  `+ 2 × 12.00 = 24.00`. The other 3 units become the backorder `(3, 21.00)`.
  On hand is now 0, but B already has a reorder in transit, so none is placed.
- Day 5, arrivals: the 10 units at standard cost 12.50 first fill the backorder:
  revenue `+ 3 × 21.00 × 0.90 = 56.70`, cogs `+ 3 × 12.50 = 37.50`. The remaining 7
  units become the batch `(7, 12.50, expiry 35)`.
- Counting SKU B alone, `revenue − cogs` after day 5 is `218.70 − 133.50 = 85.20`.
