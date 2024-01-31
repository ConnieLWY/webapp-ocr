import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def plot_to_html_image(df):
    # Convert the 'Amount' column to numeric, handling the signs and commas
    df['Amount'] = df['Amount'].str.replace(",", "")

    # Extract the sign from the end of the 'Amount' and multiply with the numeric value
    df['sign'] = df['Amount'].str.extract('([-+])').fillna('+').replace({'-': -1, '+': 1})
    df['Amount'] = pd.to_numeric(df['Amount'].str.replace("[+,-]", "").str.replace(",", ""), errors='coerce')
    df['Amount'] = df.Amount * df.sign

    chart_data = {
        "labels": df['Date'].tolist(),
        "amounts": df['Amount'].tolist(),
    }

    return chart_data
