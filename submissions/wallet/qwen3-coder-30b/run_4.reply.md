<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:56:29+00:00 -->

```python
import math

def run() -> float:
    # Initial balances
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    
    # Initial rates (in PLN per unit)
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Premium status
    premium = False
    
    # Check initial premium status
    def calculate_wallet_value():
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)
        value += round(balances['USD'] * rates['USD'], 2)
        return value
    
    # Set initial premium status
    if calculate_wallet_value() >= 20000.00:
        premium = True
    
    # Spread
    def get_spread():
        return 0.002 if premium else 0.004
    
    # Helper function for rounding
    def round_half_to_even(x):
        # Banker's rounding: round half to even
        return round(x)
    
    def round_half_away_from_zero(x):
        # Round half away from zero
        if x >= 0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)
    
    # Events list
    events = [
        (1, 'DEPOSIT', 'PLN', '-', 2500.00),
        (3, 'PAY', 'EUR', '-', 150.00),
        (5, 'CONVERT', 'PLN', 'EUR', 2000.00),
        (7, 'RATE', 'EUR', '-', 4.3280),
        (8, 'PAY', 'USD', '-', 620.00),
        (12, 'DEPOSIT', 'USD', '-', 4000.00),
        (14, 'CONVERT', 'USD', 'EUR', 1500.37),
        (15, 'RATE', 'USD', '-', 3.9455),
        (18, 'DEPOSIT', 'PLN', '-', 6000.00),
        (20, 'CONVERT', 'EUR', 'PLN', 900.00),
        (22, 'PAY', 'PLN', '-', 9000.00),
        (25, 'RATE', 'EUR', '-', 4.2965),
        (28, 'PAY', 'EUR', '-', 2400.00),
        (33, 'CONVERT', 'PLN', 'USD', 1800.00),
        (36, 'PAY', 'USD', '-', 5200.00),
        (40, 'RATE', 'USD', '-', 4.0110),
        (41, 'DEPOSIT', 'EUR', '-', 300.00),
        (43, 'CONVERT', 'EUR', 'PLN', 50.00),
        (45, 'PAY', 'PLN', '-', 1500.00),
        (48, 'CONVERT', 'USD', 'PLN', 755.00),
        (52, 'RATE', 'EUR', '-', 4.3402),
        (55, 'PAY', 'EUR', '-', 700.00),
        (58, 'PAY', 'USD', '-', 2000.00)
    ]
    
    # Sort events by day
    events.sort(key=lambda x: x[0])
    
    # Process events day by day
    current_day = 0
    for day, event_type, currency, target_currency, amount in events:
        if day != current_day:
            # Update premium status at the end of each day
            if calculate_wallet_value() >= 20000.00:
                premium = True
            else:
                premium = False
            current_day = day
            
        if event_type == 'DEPOSIT':
            balances[currency] += amount
        elif event_type == 'RATE':
            rates[currency] = amount
        elif event_type == 'CONVERT':
            if balances[currency] >= amount:
                spread = get_spread()
                # Step 1: Convert to PLN
                pln_amount = round_half_to_even(amount * rates[currency])
                # Step 2: Convert from PLN to target currency
                received = pln_amount / rates[target_currency] * (1 - spread)
                received = round_half_to_even(received)
                balances[currency] -= amount
                balances[target_currency] += received
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                balances[currency] -= amount
            else:
                # Pay with shortfall from PLN
                shortfall = amount - balances[currency]
                spread = get_spread()
                cost = round_half_to_even(shortfall * rates[currency] * (1 + spread + 0.005))
                if currency == 'PLN' or balances['PLN'] < cost:
                    # Payment declined
                    if currency == 'PLN':
                        balances['PLN'] -= 10.00
                    else:
                        balances['PLN'] -= 10.00
                else:
                    # Make payment
                    balances[currency] = 0
                    balances['PLN'] -= cost
    
    # Update premium status one more time at end of day 60
    if calculate_wallet_value() >= 20000.00:
        premium = True
    else:
        premium = False
    
    # Apply monthly fees on days 30 and 60
    if current_day == 30 or current_day == 60:
        wallet_value = calculate_wallet_value()
        if wallet_value < 5000.00:
            balances['PLN'] -= 15.00
    
    # Final calculation
    final_value = calculate_wallet_value()
    
    return round(final_value, 2)
```