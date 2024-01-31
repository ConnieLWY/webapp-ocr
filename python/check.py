import pandas as pd
from datetime import datetime

def check_balance_within_month(df, bal):
    current_month = None
    prev_balance = 0
    i = 0
    warning = []
    
    for index, row in df.iterrows():
        # Extract relevant columns
        date_str = row['Date2']
        amount2 = float(row['Amount2'])
        current_balance = float(row['Balance'])
    
        
        # Check if the month has changed
        if current_month is None or date_str.month != current_month:
            # Update current month and reset previous balance
            current_month = date_str.month
            prev_balance = float(bal[i].split()[-1].replace(",", ""))
            i = i + 1
        
        # Calculate previous balance + amount2
        calculated_balance = prev_balance + amount2
        
        # Compare with current balance
        if round(calculated_balance,2) != round(current_balance,2):
            warning.append(f"Balance mismatch at {row['Date']}: Calculated Balance = {calculated_balance}, Current Balance = {current_balance}")
        
        # Update previous balance for the next iteration
        prev_balance = current_balance

    return warning
