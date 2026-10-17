from decimal import Decimal, getcontext, ROUND_HALF_UP

def run() -> float:
    # Increase precision for intermediate calculations
    getcontext().prec = 28

    # Opening balances
    accounts = {
        'X': {'balance': Decimal('4200.00'), 'accrued_interest': Decimal('0'), 'period_min': Decimal('Infinity')},
        'Y': {'balance': Decimal('800.00'),  'accrued_interest': Decimal('0'), 'period_min': Decimal('Infinity')},
        'Z': {'balance': Decimal('12000.00'), 'accrued_interest': Decimal('0'), 'period_min': Decimal('Infinity')},
    }

    # Event list: (day, type, src, dst, amount)
    events = [
        (1,  'DEPOSIT',  'Y', None, Decimal('300.00')),
        (3,  'WITHDRAW', 'Y', None, Decimal('1500.00')),
        (5,  'TRANSFER', 'Z', 'X',  Decimal('2500.00')),
        (8,  'WITHDRAW', 'Y', None, Decimal('200.00')),
        (10, 'DEPOSIT',  'Y', None, Decimal('2000.00')),
        (12, 'TRANSFER', 'X', 'Y',  Decimal('800.00')),
        (15, 'WITHDRAW', 'Z', None, Decimal('8000.00')),
        (20, 'WITHDRAW', 'Z', None, Decimal('700.00')),
        (25, 'TRANSFER', 'Y', 'Z',  Decimal('1200.00')),
        (33, 'WITHDRAW', 'X', None, Decimal('6300.00')),
        (36, 'DEPOSIT',  'X', None, Decimal('1000.00')),
        (40, 'TRANSFER', 'Z', 'Y',  Decimal('2100.00')),
        (45, 'WITHDRAW', 'Y', None, Decimal('5000.00')),
        (47, 'DEPOSIT',  'Z', None, Decimal('3000.00')),
        (50, 'TRANSFER', 'Y', 'X',  Decimal('1000.00')),
        (55, 'WITHDRAW', 'X', None, Decimal('300.00')),
        (58, 'DEPOSIT',  'Y', None, Decimal('150.00')),
    ]

    # Map day to events for quick lookup
    events_by_day = {}
    for e in events:
        events_by_day.setdefault(e[0], []).append(e)

    # Helper to process a debit
    def debit(acc, total: Decimal) -> bool:
        before = acc['balance']
        if before - total < Decimal('-500'):
            acc['balance'] -= Decimal('15.00')  # rejection fee
            return False
        else:
            acc['balance'] -= total
            if before >= Decimal('0') and acc['balance'] < Decimal('0'):
                acc['balance'] -= Decimal('25.00')  # overdraft fee
            return True

    # Simulation over days 1 to 60
    for day in range(1, 61):
        # Process events of the day
        for event in events_by_day.get(day, []):
            etype, src, dst, amt = event[1], event[2], event[3], event[4]
            if etype == 'DEPOSIT':
                accounts[src]['balance'] += amt
            elif etype == 'WITHDRAW':
                debit(accounts[src], amt)
            elif etype == 'TRANSFER':
                fee = Decimal('1.00') if amt > Decimal('1000') else Decimal('0.00')
                total = amt + fee
                if debit(accounts[src], total):
                    accounts[dst]['balance'] += amt

        # Minimum balance tracking (end-of-day before interest)
        for key in accounts:
            bal = accounts[key]['balance']
            if bal < accounts[key]['period_min']:
                accounts[key]['period_min'] = bal

        # Interest accrual based on current balance
        for key in accounts:
            bal = accounts[key]['balance']
            if bal > Decimal('0'):
                if bal <= Decimal('5000'):
                    interest = bal * Decimal('0.02') / Decimal('365')
                else:
                    interest = (Decimal('5000') * Decimal('0.02') +
                                (bal - Decimal('5000')) * Decimal('0.035')) / Decimal('365')
            else:
                interest = bal * Decimal('0.18') / Decimal('365')
            accounts[key]['accrued_interest'] += interest

        # Period close on days 30 and 60
        if day in (30, 60):
            for key in accounts:
                # Round accrued interest to 2 decimals, halves away from zero
                rounded = accounts[key]['accrued_interest'].quantize(
                    Decimal('0.01'), rounding=ROUND_HALF_UP)
                accounts[key]['balance'] += rounded
                accounts[key]['accrued_interest'] = Decimal('0')

                # Maintenance fee if period minimum < 1000
                if accounts[key]['period_min'] < Decimal('1000'):
                    accounts[key]['balance'] -= Decimal('5.00')

                # Reset period minimum for next period
                accounts[key]['period_min'] = Decimal('Infinity')

    # Sum of balances rounded to 2 decimals
    total = sum(acc['balance'] for acc in accounts.values())
    total = total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return float(total)

# If executed directly, print the result (optional)
if __name__ == "__main__":
    print(run())
