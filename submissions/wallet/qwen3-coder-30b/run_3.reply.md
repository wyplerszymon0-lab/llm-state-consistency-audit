<!-- model: ollama:qwen3-coder:30b | prompt v1 | 2026-10-16T09:55:28+00:00 -->

```python
import math

def run() -> float:
    # Initial balances
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    
    # Initial rates in PLN per unit
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Premium status - evaluated at start
    def is_premium():
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)  # Round half away from zero
        value += round(balances['USD'] * rates['USD'], 2)
        return value >= 20000.00
    
    premium = is_premium()
    
    def round_half_even(x):
        # Banker's rounding: round half to even
        return round(x, 2)
    
    def round_half_away_from_zero(x):
        # Round half away from zero
        if x >= 0:
            return math.floor(x + 0.5)
        else:
            return math.ceil(x - 0.5)
    
    def convert(currency, target_currency, amount):
        nonlocal balances, rates, premium
        
        if balances[currency] < amount:
            return  # Not enough balance
        
        # Convert to PLN
        pln_amount = round_half_even(amount * rates[currency])
        
        # Apply spread
        s = 0.002 if premium else 0.004
        received_pln = pln_amount * (1 - s)
        
        # Convert to target currency
        received = round_half_even(received_pln / rates[target_currency])
        
        balances[currency] -= amount
        balances[target_currency] += received
    
    def pay(currency, amount):
        nonlocal balances, rates, premium
        
        if balances[currency] >= amount:
            balances[currency] -= amount
        else:
            shortfall = amount - balances[currency]
            balances[currency] = 0
            
            # Calculate cost in PLN
            s = 0.002 if premium else 0.004
            cost = round_half_even(shortfall * rates[currency] * (1 + s + 0.005))
            
            if currency == 'PLN' or balances['PLN'] < cost:
                # Decline - subtract decline fee from PLN
                balances['PLN'] -= 10.00
            else:
                balances['PLN'] -= cost
    
    def deposit(currency, amount):
        nonlocal balances
        balances[currency] += amount
    
    def set_rate(currency, rate):
        nonlocal rates
        rates[currency] = rate
    
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
    current_day = 0
    for day, event_type, currency, target_currency, amount in events:
        if day != current_day:
            # Re-evaluate premium status at end of each day
            premium = is_premium()
            current_day = day
        
        if event_type == 'DEPOSIT':
            deposit(currency, amount)
        elif event_type == 'PAY':
            pay(currency, amount)
        elif event_type == 'CONVERT':
            convert(currency, target_currency, amount)
        elif event_type == 'RATE':
            set_rate(currency, amount)
    
    # Re-evaluate premium status one final time
    premium = is_premium()
    
    # Apply monthly fees on day 30 and 60
    if current_day >= 30:
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)  # Round half away from zero
        value += round(balances['USD'] * rates['USD'], 2)
        if value < 5000.00:
            balances['PLN'] -= 15.00
    
    if current_day >= 60:
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)  # Round half away from zero
        value += round(balances['USD'] * rates['USD'], 2)
        if value < 5000.00:
            balances['PLN'] -= 15.00
    
    # Calculate final wallet value in PLN
    value = balances['PLN']
    value += round(balances['EUR'] * rates['EUR'], 2)  # Round half away from zero
    value += round(balances['USD'] * rates['USD'], 2)
    
    return round(value, 2)
```