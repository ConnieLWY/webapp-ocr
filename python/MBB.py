import re
import json
import csv
from datetime import datetime
import pandas as pd
import pandas as pd


def find_next_one(my_list, index):
    DATE_REGEX = r'\d{2}/\d{2}'
    AMOUNT_REGEX = r'\.\d{2}[+-]'
    BAL_REGEX = r'\.\d{2}|\.\d{2}DR'
    for i in range(index + 1, len(my_list)):
        elements = my_list[i].split()
        if re.match(DATE_REGEX, my_list[i][0:5]) and (re.match(BAL_REGEX, elements[-1][-3:]) or re.match(BAL_REGEX, elements[-1][-5:])) and re.match(AMOUNT_REGEX, elements[-2][-4:]):
            return i  # Return the index of the first occurrence of 1 after the specified index
    return -1

def process_rows(rows):
    DATE_REGEX = r'\d{2}/\d{2}'
    AMOUNT_REGEX = r'\.\d{2}[+-]'
    BAL_REGEX = r'\.\d{2}|\.\d{2}DR'
    KEYWORDS_TO_REMOVE = ["BAKI", "BAKILEGAR", "ENDING", "BEGINNING BALANCE"]
    data = {}
    transaction_number = 1
    transaction = None
    test = 0
    previous_balance = None

    for row in rows:
        elements = row.split()  # Split the row into elements
        if elements:
            if re.match(DATE_REGEX, elements[0]) and (re.match(BAL_REGEX, elements[-1][-3:]) or re.match(BAL_REGEX, elements[-1][-5:])) and re.match(AMOUNT_REGEX, elements[-2][-4:]):
                # Start of a new transaction
                test = 1
                if transaction is not None:
                    data[f"{transaction_number}"] = transaction
                    transaction_number += 1

                amount_index = next((idx for idx, el in enumerate(elements) if re.match(AMOUNT_REGEX, el[-4:])), None)
                if amount_index is None:
                    # No such element found, initialize description_end with a value that ensures it's not used
                    description_end = len(elements) - 2
                    amt = float(elements[description_end + 1].replace(",", "")) - previous_balance
                    if amt < 0:
                        amt = abs(amt)
                        A = f'{amt:.2f}-'
                        sign = -1
                    else:
                        A = f'{amt:.2f}+'
                        sign = 1
                    description = " ".join(elements[1:description_end+1])  # Join elements as description
                    if "DR" in elements[description_end + 1]:
                        B = elements[description_end + 1].replace("DR","")
                        B = float(B.replace(",",""))
                        B = -B
                        transaction = {
                            "Date": elements[0],
                            "Description": description,
                            "Amount": A,
                            "Balance": round(B, 2),
                            "Sign": sign,
                            "Amt": round(float(elements[description_end][0:-1].replace(",","")), 2)
                        }
                        previous_balance = transaction["Balance"]
                    else:
                        transaction = {
                            "Date": elements[0],
                            "Description": description,
                            "Amount": A,
                            "Balance": float(elements[description_end + 1].replace(",","")),
                            "Sign": sign,
                            "Amt": round(float(elements[description_end][0:-1].replace(",","")), 2)
                        }
                        previous_balance = transaction["Balance"]
                else:
                    description_end = amount_index
                    description = " ".join(elements[1:description_end])  # Join elements as description
                    if elements[description_end][-1] == "-":
                        sign = -1
                    elif elements[description_end][-1] == "+":
                        sign = 1
                    if "DR" in elements[description_end + 1]:
                        B = elements[description_end + 1].replace("DR","")
                        B = float(B.replace(",",""))
                        B = -B
                        transaction = {
                            "Date": elements[0],
                            "Description": description,
                            "Amount": elements[description_end],
                            "Balance": round(B, 2),
                            "Sign": sign,
                            "Amt": round(float(elements[description_end][0:-1].replace(",","")), 2)
                            
                        }
                        previous_balance = transaction["Balance"]
                    else:
                        transaction = {
                            "Date": elements[0],
                            "Description": description,
                            "Amount": elements[description_end],
                            "Balance": float(elements[description_end + 1].replace(",","")),
                            "Sign": sign,
                            "Amt": round(float(elements[description_end][0:-1].replace(",","")), 2)
                        }
                        previous_balance = transaction["Balance"]

            elif test == 1 and elements[0] not in KEYWORDS_TO_REMOVE :
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
    KEYWORDS_TO_REMOVE = ["BAKI", "BAKILEGAR", "ENDING", "BEGINNING BALANCE"]

    indices_containing = [i for i, s in enumerate(rows) if any(keyword.lower() in s.lower() for keyword in KEYWORDS_TO_REMOVE )]
    indices_containing.sort(reverse=True)

    for index in indices_containing:
        if 0 <= index < len(rows):
            result_index = find_next_one(rows, index)
            if result_index != -1:
                del rows[index:result_index]
            else:
                del rows[index:]

    data = process_rows(rows)

    df = pd.DataFrame.from_dict(data, orient='index')

    df['Amount2'] = df.Amt * df.Sign

    return df

