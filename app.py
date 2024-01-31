from flask import Flask, render_template, request, redirect, url_for, session, flash
import pdfplumber
import os
import pandas as pd
from python import MBB
from python import CIMB
from python import HLBB
from python import PBB
from python import RHB
from python import summary
from python import chart




app = Flask(__name__)

# Generate a secret key
secret_key = os.urandom(24)
app.secret_key = secret_key

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    file_path = None
    bank_selected = ""  # Initialize the variable

    if request.method == 'POST':
        file = request.files['file']
        bank_selected = request.form.get('bank')  # Get the selected bank value

        if file:
            # Save the uploaded PDF file
            file_path = f'{file.filename}'
            file.save(file_path)

            # Store data in session for access in the analysis route
            session['file_path'] = file_path
            session['bank_selected'] = bank_selected

            return redirect(url_for('analysis'))  # Redirect to the analysis route

    return render_template('index.html', bank_selected=bank_selected)

@app.route('/analysis', methods=['GET'])
def analysis():
    current_page = 1
    page_num = 0
    text = ""
    file_path = session.get('file_path')
    bank_selected = session.get('bank_selected')

    if file_path and bank_selected:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_num += 1
                text = f'{text} \n{page.extract_text()}'

        rows = text.split('\n')
        if bank_selected == "MBB":
            df = MBB.main(rows)
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df['Month'] = df['Date2'].dt.month
            except:
                pass
            
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m/%y')
                df['Month'] = df['Date2'].dt.month
            except:
                pass

            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m')
                df['Month'] = df['Date2'].dt.month
            except:
                pass
        elif bank_selected == "CIMB":
            df = CIMB.main(rows)
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df['Month'] = df['Date2'].dt.month
            except:
                pass
        elif bank_selected == "HLBB":
            df = HLBB.main(rows)
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
                df['Month'] = df['Date2'].dt.month
            except:
                pass

            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d-%m')
                df['Month'] = df['Date2'].dt.month
            except:
                pass
        elif bank_selected == "PBB":
            df = PBB.main(rows)
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                df['Month'] = df['Date2'].dt.month
            except:
                pass

            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m')
                df['Month'] = df['Date2'].dt.month
            except:
                pass
        elif bank_selected == "RHB":
            df = RHB.main(rows)
            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%b%d')
                df['Month'] = df['Date2'].dt.month
            except:
                pass

            try:
                df['Date2'] = pd.to_datetime(df['Date'], format='%d%b')
                df['Month'] = df['Date2'].dt.month
            except:
                pass

        num_rows_per_page = 15
        num_pages = (len(df) + num_rows_per_page - 1) // num_rows_per_page

        # Convert DataFrame to HTML
        table_html = df.drop(['Date2', 'Month'],axis=1).to_html(classes='table table-striped', index=False)

        summary_data = summary.main(df)
        chart_data = chart.plot_to_html_image(df)

        return render_template('analysis.html', table=table_html, num_pages=num_pages, bank_selected=bank_selected, current_page=current_page, summary_data=summary_data, chart_data=chart_data)

    # Handle the case where data is not available
    flash('Invalid access to the analysis route.')
    return redirect(url_for('upload_file'))

# @app.errorhandler(Exception)
# def handle_error(e):
#     return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
