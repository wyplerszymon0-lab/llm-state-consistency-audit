from typing import Dict

def run() -> float:
    # Initial balances and exchange rates
    balances = {'PLN': 3000.00, 'EUR': 1200.00, 'USD': 500.00}
    rates = {'PLN': 1.0000, 'EUR': 4.3150, 'USD': 3.9820}
    
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
        (58, 'PAY', 'USD', '-', 2000.00),
    ]
    
    # Premium status and spread
    is_premium = False
    spread = 0.004
    
    def calculate_wallet_value() -> float:
        value = balances['PLN']
        value += round(balances['EUR'] * rates['EUR'], 2)
        value += round(balances['USD'] * rates['USD'], 2)
        return value
    
    def update_premium_status():
        nonlocal is_premium, spread
        value = calculate_wallet_value()
        is_premium = value >= 20000.00
        spread = 0.002 if is_premium else 0.004
    
    def deposit(currency: str, amount: float):
        balances[currency] += amount
    
    def update_rate(currency: str, rate: float):
        rates[currency] = rate
    
    def convert(currency: str, target_currency: str, amount: float):
        if balances[currency] < amount:
            return
        pln_amount = round(amount * rates[currency], 2)
        received = round(pln_amount / rates[target_currency] * (1 - spread), 2)
        balances[currency] -= amount
        balances[target_currency] += received
    
    def pay(currency: str, amount: float):
        if balances[currency] >= amount:
            balances[currency] -= amount
        else:
            shortfall = amount - balances[currency]
            cost = round(shortfall * rates[currency] * (1 + spread + 0.005), 2)
            if currency == 'PLN' or balances['PLN'] < cost:
                balances['PLN'] -= 10.00
            else:
                balances[currency] = 0
                balances['PLN'] -= cost
    
    def apply_monthly_fee():
        value = calculate_wallet_value()
        if value < 5000.00:
            balances['PLN'] -= 15.00
    
    # Process events
    for day, event_type, currency, target_currency, amount in events:
        if event_type == 'DEPOSIT':
            deposit(currency, amount)
        elif event_type == 'RATE':
            update_rate(currency, amount)
        elif event_type == 'CONVERT':
            convert(currency, target_currency, amount)
        elif event_type == 'PAY':
            pay(currency, amount)
        
        # Update premium status at the end of each day
        update_premium_status()
    
    # Apply monthly fee at the end of day 30 and day 60
    apply_monthly_fee()
    apply_monthly_fee()
    
    # Calculate final wallet value
    final_value = calculate_wallet_value()
    return round(final_value, 2)

# Example usage
if __name__ == "__main__":
    print(run())
