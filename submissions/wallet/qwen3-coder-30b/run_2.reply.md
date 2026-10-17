<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:54:18+00:00 -->

```python
import math

def run() -> float:
    # Initial balances
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    
    # Initial exchange rates (in PLN per unit)
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Premium status
    premium = False
    
    # Monthly fee
    monthly_fee = 15.00
    
    def round_half_to_even(x):
        return round(x, 2)
    
    def round_half_away_from_zero(x):
        if x >= 0:
            return math.floor(x * 100 + 0.5) / 100
        else:
            return math.ceil(x * 100 - 0.5) / 100
    
    def get_wallet_value():
        value = balances['PLN']
        for currency in ['EUR', 'USD']:
            rate = rates[currency]
            balance = balances[currency]
            value += round_half_away_from_zero(balance * rate)
        return value
    
    def update_premium_status():
        global premium
        premium = get_wallet_value() >= 20000.00
    
    # Initialize premium status
    update_premium_status()
    
    # Events
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
    
    # Process events day by day
    for day in range(1, 61):
        # Sort events by day
        day_events = [event for event in events if event[0] == day]
        
        # Process events for this day
        for event in day_events:
            _, event_type, currency, target_currency, amount = event
            
            if event_type == 'DEPOSIT':
                balances[currency] += amount
                
            elif event_type == 'RATE':
                rates[currency] = amount
                
            elif event_type == 'CONVERT':
                if balances[currency] >= amount:
                    # Step 1: Convert to PLN
                    p = round_half_to_even(amount * rates[currency])
                    
                    # Step 2: Convert from PLN to target currency
                    spread = 0.002 if premium else 0.004
                    received = round_half_to_even(p / rates[target_currency] * (1 - spread))
                    
                    balances[currency] -= amount
                    balances[target_currency] += received
                    
            elif event_type == 'PAY':
                if balances[currency] >= amount:
                    # Enough balance, just subtract
                    balances[currency] -= amount
                else:
                    # Not enough balance, use PLN to cover shortfall
                    shortfall = amount - balances[currency]
                    cost = round_half_to_even(shortfall * rates[currency] * (1 + (0.002 if premium else 0.004) + 0.005))
                    
                    if currency == 'PLN' or balances['PLN'] < cost:
                        # Payment declined
                        if currency == 'PLN':
                            balances['PLN'] -= 10.00
                        else:
                            balances['PLN'] -= 10.00
                    else:
                        # Pay with PLN
                        balances[currency] = 0
                        balances['PLN'] -= cost
                        
        # Update premium status at the end of each day
        update_premium_status()
        
        # Apply monthly fee on days 30 and 60
        if day in [30, 60]:
            wallet_value = get_wallet_value()
            if wallet_value < 5000.00:
                balances['PLN'] -= monthly_fee
    
    # Final wallet value
    final_value = get_wallet_value()
    
    return round(final_value, 2)
```