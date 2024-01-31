import pdfplumber
import re
import json
import csv
from datetime import datetime
import pandas as pd


def find_next_one(my_list, index):
    DATE_REGEX = r'\d{2}/\d{2}|\d{2}/\d{2}/d{4}'
    AMOUNT_REGEX = r'\.\d{2}'
    BAL_REGEX = r'\.\d{2}'
    for i in range(index + 1, len(my_list)):
        elements = my_list[i].split()
        if re.match(DATE_REGEX, my_list[i][0:5]) and re.match(BAL_REGEX, elements[-1][-3:]) and re.match(AMOUNT_REGEX, elements[-2][-3:]):
            return i  # Return the index of the first occurrence of 1 after the specified index
    return -1

def process_rows(rows):
    DATE_REGEX = r'\d{2}/\d{2}|\d{2}/\d{2}/d{4}'
    AMOUNT_REGEX = r'\.\d{2}'
    BAL_REGEX = r'\.\d{2}'
    KEYWORDS_TO_REMOVE = ["Important Notice", "You are responsible", "CLOSING BALANCE" , "OPENING BALANCE", "BONUS POINTS", "You can transfer funds,"]
    data = {}
    transaction_number = 1
    transaction = None
    test = 0
    previous_balance = 0

    for row in rows:
        elements = row.split()  # Split the row into elements
        if elements:
            if re.match(DATE_REGEX, elements[0])  and re.match(BAL_REGEX, elements[-1][-3:]) and re.match(AMOUNT_REGEX, elements[-2][-3:]):
                # Start of a new transaction
                test = 1
                if transaction is not None:
                    data[f"{transaction_number}"] = transaction
                    transaction_number += 1

                matching_indices = [idx for idx, el in reversed(list(enumerate(elements))) if re.match(r'\.\d{2}', el[-3:])]
                balance_index = matching_indices[0] if matching_indices else None
                if balance_index:
                    bal = float(elements[balance_index].replace(",", "")) - previous_balance
                    if len(matching_indices)==2:
                        amt = float(elements[balance_index-1].replace(",", ""))
                        description_end = balance_index-1
                    elif len(matching_indices)==3:
                        amt = float(elements[balance_index-2].replace(",", ""))
                        description_end = balance_index-2
                    else:
                        amt = 0
                        description_end = balance_index
                    if bal < 0:
                        A = f'{amt:.2f}-'
                    else:
                        A = f'{amt:.2f}+'
                    description = " ".join(elements[1:description_end])  # Join elements as description
                    transaction = {
                        "Date": elements[0],
                        "Description": description,
                        "Amount": A,
                        "Balance": float(elements[balance_index].replace(",", ""))
                    }
                    previous_balance = transaction["Balance"]
                else:
                    print('no balance found')

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

    KEYWORDS_TO_REMOVE = ["Important Notice", "You are responsible", "CLOSING BALANCE" , "OPENING BALANCE", "BONUS POINTS", "You can transfer funds,"]

    indices_containing = [i for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in KEYWORDS_TO_REMOVE)]
    indices_containing.sort(reverse=True)

    for index in indices_containing:
        if 0 <= index < len(rows):
            result_index = find_next_one(rows, index)
            if 'OPENING BALANCE' in rows[index].upper():
                index = index - 1
            if result_index != -1:
                del rows[index:result_index]
            else:
                del rows[index:]

    data = process_rows(rows)

    df = pd.DataFrame.from_dict(data, orient='index')

    return df

if __name__ == "__main__":
    main()
