import math

def run() -> float:
    # Initial balances
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    
    # Initial rates in PLN per unit
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Premium status (set from opening balances)
    def calculate_wallet_value():
        value = balances['PLN']
        for currency in ['EUR', 'USD']:
            # Round half away from zero
            rounded_value = math.floor(value * rates[currency] * 100 + 0.5) / 100 if value * rates[currency] >= 0 else math.ceil(value * rates[currency] * 100 - 0.5) / 100
            value += rounded_value
        return value
    
    premium = calculate_wallet_value() >= 20000.00
    
    # Spread
    def get_spread():
        return 0.002 if premium else 0.004
    
    # Helper function for rounding
    def round_half_to_even(x):
        # Use Python's built-in round which implements "round half to even"
        return round(x, 2)
    
    def round_half_away_from_zero(x):
        # Round half away from zero
        if x >= 0:
            return math.floor(x * 100 + 0.5) / 100
        else:
            return math.ceil(x * 100 - 0.5) / 100
    
    # Process events day by day
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
    
    current_day = 0
    
    for day, event_type, currency, target_currency, amount in events:
        # Process days in order
        while current_day < day:
            current_day += 1
            # Check for monthly fee at end of days 30 and 60
            if current_day == 30 or current_day == 60:
                wallet_value = calculate_wallet_value()
                if wallet_value < 5000.00:
                    balances['PLN'] -= 15.00
        
        # Process event
        if event_type == 'DEPOSIT':
            balances[currency] += amount
            
        elif event_type == 'RATE':
            rates[currency] = amount
            
        elif event_type == 'CONVERT':
            if balances[currency] >= amount:
                # Convert currency to target_currency through PLN
                spread = get_spread()
                # Step 1: convert to PLN
                pln_value = round_half_to_even(amount * rates[currency])
                # Step 2: convert from PLN to target_currency with spread
                received = round_half_to_even(pln_value / rates[target_currency] * (1 - spread))
                balances[currency] -= amount
                balances[target_currency] += received
                
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                balances[currency] -= amount
            else:
                # Pay shortfall from PLN
                shortfall = amount - balances[currency]
                spread = get_spread()
                cost = round_half_to_even(shortfall * rates[currency] * (1 + spread + 0.005))
                
                if currency == 'PLN' or balances['PLN'] < cost:
                    # Decline payment
                    if currency != 'PLN':
                        balances['PLN'] -= 10.00  # decline fee
                else:
                    balances[currency] = 0.0
                    balances['PLN'] -= cost
    
    # Final day processing (days 30 and 60)
    while current_day < 60:
        current_day += 1
        if current_day == 30 or current_day == 60:
            wallet_value = calculate_wallet_value()
            if wallet_value < 5000.00:
                balances['PLN'] -= 15.00
    
    # Calculate final value in PLN
    final_value = balances['PLN']
    for currency in ['EUR', 'USD']:
        rounded_value = round_half_away_from_zero(balances[currency] * rates[currency])
        final_value += rounded_value
    
    return round(final_value, 2)
