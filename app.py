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
from python import check




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
            # Save the uploaded PDF file to the local storage directory
            file_path = os.path.join(os.getenv('TMP', '/tmp'), file.filename)
            # file_path = f'static/{file.filename}'
            file.save(file_path)

            # Store the file path in the session for access in the analysis route
            session['file_path'] = file_path
            session['bank_selected'] = bank_selected

            return redirect(url_for('analysis'))

    return render_template('index.html', bank_selected=bank_selected)

@app.route('/analysis', methods=['GET'])
def analysis():
    try:
        current_page = 1
        page_num = 0
        text = ""
        file_path = session.get('file_path')
        bank_selected = session.get('bank_selected')

        if file_path and bank_selected:
            with pdfplumber.open(file_path) as pdf:
                bal = []
                p2p = []
                text = ""
                for page in pdf.pages:
                    page_num += 1
                    text = f'{text} \n{page.extract_text()}'

            rows = text.split('\n')

            if bank_selected == "MBB":
                bal = [s for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in  ['BEGINNING BALANCE'])]
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
                bal = [s for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in  ['OPENING BALANCE'])]
                df = CIMB.main(rows)
                try:
                    df['Date2'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
                    df['Month'] = df['Date2'].dt.month
                except:
                    pass
            elif bank_selected == "HLBB":
                bal = [s for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in  ['Balance from'])]
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
                bal = [s for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in  ['Balance B/F'])]
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
                bal = [s for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in  ['B/FBALANCE'])]
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
            final_df = df.drop(['Sign', 'Amt', 'Amount2', 'Date2', 'Month'],axis=1)
            # Convert DataFrame to HTML
            table_html = final_df.to_html(classes='table table-striped', index=False)
            p2p_keywords = ['Bay Smart', 'BM Ram Capital', 'B2B Finpal', 'Capsphere Services', 'Crowd Sense', 'P2P nusa kapital', 'fbm crowdtech', 'microleap', 'modalku ventures', 'moneysave', 'quickash']
            p2p_df = final_df[final_df.apply(lambda row: any(keyword.lower() in row['Description'].lower() for keyword in p2p_keywords), axis=1)]
            p2p_list = p2p_df.to_dict(orient='records')
            warning = check.check_balance_within_month(df, bal)
            summary_data = summary.main(df)
            chart_data = chart.plot_to_html_image(df)

            return render_template('analysis.html', table=table_html, num_pages=num_pages, bank_selected=bank_selected, current_page=current_page, summary_data=summary_data, chart_data=chart_data, warning=warning, p2p = p2p_list)

        # Handle the case where data is not available
        flash('Invalid access to the analysis route.')
        return redirect(url_for('upload_file'))
    except KeyError as e:
        return render_template('error.html', error=f'KeyError: {str(e)}')

@app.errorhandler(Exception)
def handle_error(e):
    return render_template('error.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
