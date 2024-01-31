import pandas as pd


def plot_to_html_image(df):
    # Convert the 'Amount' column to numeric, handling the signs and commas
    # df['Amount'] = df['Amount'].str.replace(",", "")

    # # Extract the sign from the end of the 'Amount' and multiply with the numeric value
    # df['sign'] = df['Amount'].str.extract('([-+])').fillna('+').replace({'-': -1, '+': 1})
    # df['Amount'] = pd.to_numeric(df['Amount'].str.replace("[+,-]", "").str.replace(",", ""), errors='coerce')
    # df['Amount'] = df.Amount * df.sign

    # chart_data = {
    #     "labels": df['Date'].tolist(),
    #     "balances": df['Balance'].tolist(),
    # }
    # Group by 'Date' and calculate the average balance
    grouped_df = df.groupby('Date', sort=False)['Balance'].mean().reset_index()


    chart_data = {
        "labels": grouped_df['Date'].tolist(),
        "average_balances": grouped_df['Balance'].tolist(),
    }

    return chart_data

