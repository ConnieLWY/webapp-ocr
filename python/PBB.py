import re
import pandas as pd


def find_next_one(my_list, index):
    DATE_REGEX = r'\d{2}/\d{2}'
    AMOUNT_REGEX = r'\.\d{2}'

    date = ""
    for i in range(index + 1, len(my_list)):
        elements = my_list[i].split()
        if re.match(DATE_REGEX, my_list[i][0:5]):
            date = my_list[i][0:5]
        if re.match(AMOUNT_REGEX, elements[-1][-3:]) and re.match(AMOUNT_REGEX, elements[-2][-3:]):
            return (date, i)  # Return the index of the first occurrence of 1 after the specified index
    return (date, -1)

def process_rows(rows):
    DATE_REGEX = r'\d{2}/\d{2}'
    AMOUNT_REGEX = r'\.\d{2}'
    KEYWORDS_TO_REMOVE = ["Thank You For Banking With Public Bank", "Penyata ini dicetak melalui kompute", "Closing Balance", "Balance From", "Balance B/F", "Balance C/F"]

    data = {}
    transaction_number = 1
    transaction = None
    test = 0
    previous_balance = 0
    b = 0

    for row in rows:
        elements = row.split()  # Split the row into elements
        if elements:
            if re.match(AMOUNT_REGEX, elements[-1][-3:]) and re.match(AMOUNT_REGEX, elements[-2][-3:]):
                test = 1
                if transaction is not None:
                    data[f"{transaction_number}"] = transaction
                    transaction_number += 1
                    
                balance = float(elements[-1].replace(",", ""))
                amt = float(elements[-2].replace(",", ""))
                if re.match(DATE_REGEX, elements[0]):
                    date = elements[0]
                    description_start = 1
                else:
                    description_start = 0
                bal = float(elements[-1].replace(",", "")) - previous_balance
                if bal < 0:
                    A = f'{amt:.2f}-'
                else:
                    A = f'{amt:.2f}+'

                description = " ".join(elements[description_start:-2])  # Join elements as description
                transaction = {
                    "Date": date,
                    "Description": description,
                    "Amount": A,
                    "Balance": round(float(balance), 2)
                }
                previous_balance = transaction["Balance"]

            elif test == 1 and all(s not in "".join(elements) for s in KEYWORDS_TO_REMOVE):
                # This is a continuation of the description, skip if "**"
                if "Description" not in transaction:
                    transaction["Description"] = " ".join(elements)
                else:
                    transaction["Description"] += " " + " ".join(elements)
            else:
                test = 0

    # Append the last transaction to the data dictionary for the current page
    if transaction is not None:
        data[f"{transaction_number}"] = transaction

    return data


def main(rows):
    DATE_REGEX = r'\d{2}/\d{2}'
    KEYWORDS_TO_REMOVE = ["Thank You For Banking With Public Bank", "Penyata ini dicetak melalui kompute", "Closing Balance", "Balance From", "Balance B/F", "Balance C/F"]


    indices_containing = [i for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in KEYWORDS_TO_REMOVE)]
    indices_containing.sort(reverse=True)

    for index in indices_containing:
        if 0 <= index < len(rows):
            date, result_index = find_next_one(rows, index)
            if result_index != -1:
                if not re.match(DATE_REGEX, rows[result_index][0:5]):
                    rows[result_index] = " ".join([date, rows[result_index]])
                del rows[index:result_index]
            else:
                del rows[index:]

    data = process_rows(rows)
    df = pd.DataFrame.from_dict(data, orient='index')
    return df

