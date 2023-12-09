import gspread
import pandas as pd

from ptn.spyplane.constants import gc

# gc = gspread.service_account('spyplane-394209-39d59161dedb.json')
# Spreadsheet
sheet = gc.open("Faction Scouting")

# Worksheet
worksheet = sheet.get_worksheet_by_id(0)

# Values
values = worksheet.get_values('A:E')
headers = values.pop(0)
sheet_dataframe = pd.DataFrame(values, columns=headers)


def get_sheet_row(row_name):
    cell = worksheet.find(row_name, in_column=1)
    row_number = cell.row
    return row_number


def update_row(row_name, usernmame, user_id, timestamp):
    row_number = get_sheet_row(row_name)

    try:
        # Update only the last 3 cells in the sheet
        worksheet.update_cell(row_number, 3, usernmame)
        worksheet.update_cell(row_number, 4, user_id)
        worksheet.update_cell(row_number, 5, timestamp)
        return True

    except:
        return False

def get_systems():
    return sheet_dataframe[['System', 'Priority']].values.tolist()
