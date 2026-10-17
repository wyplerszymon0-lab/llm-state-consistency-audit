import math

def run() -> float:
    # Initial balances
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    
    # Initial rates (in PLN per unit)
    rates = {'PLN': 1.0, 'EUR': 4.3150, 'USD': 3.9820}
    
    # Premium status
    premium = False
    
    # Function to round using bank rounding (round half to even)
    def round_banker(x):
        return round(x, 2)
    
    # Function to round using "round half away from zero"
    def round_away(x):
        if x >= 0:
            return math.floor(x * 100 + 0.5) / 100
        else:
            return math.ceil(x * 100 - 0.5) / 100
    
    # Function to compute wallet value in PLN
    def wallet_value():
        value = balances['PLN']
        for currency in ['EUR', 'USD']:
            rate = rates[currency]
            balance = balances[currency]
            value += round_away(balance * rate)
        return value
    
    # Check initial premium status
    premium = wallet_value() >= 20000.00
    
    # Monthly fee function
    def apply_monthly_fee(day):
        nonlocal balances, premium
        if day in [30, 60]:
            value = wallet_value()
            if value < 5000.00:
                balances['PLN'] -= 15.00
    
    # Process events
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
        if day > current_day:
            # Apply monthly fee before processing new day's events
            apply_monthly_fee(current_day)
            # Re-evaluate premium status after monthly fee
            premium = wallet_value() >= 20000.00
            current_day = day
        
        spread = 0.002 if premium else 0.004
        
        if event_type == 'DEPOSIT':
            balances[currency] += amount
            
        elif event_type == 'RATE':
            rates[currency] = amount
            
        elif event_type == 'CONVERT':
            if balances[currency] >= amount:
                # Convert currency to target_currency
                p = round_banker(amount * rates[currency])
                received = round_banker(p / rates[target_currency] * (1 - spread))
                balances[currency] -= amount
                balances[target_currency] += received
                
        elif event_type == 'PAY':
            if balances[currency] >= amount:
                # Payment can be covered directly
                balances[currency] -= amount
            else:
                # Payment cannot be covered directly, must pay with PLN
                shortfall = amount - balances[currency]
                cost = round_banker(shortfall * rates[currency] * (1 + spread + 0.005))
                if currency == 'PLN' or balances['PLN'] < cost:
                    # Decline payment and subtract fee
                    balances['PLN'] -= 10.00
                else:
                    # Pay with PLN
                    balances[currency] = 0
                    balances['PLN'] -= cost
    
    # Apply final monthly fees
    apply_monthly_fee(60)
    
    # Re-evaluate premium status one last time
    premium = wallet_value() >= 20000.00
    
    # Final wallet value
    final_value = wallet_value()
    
    return round(final_value, 2)
