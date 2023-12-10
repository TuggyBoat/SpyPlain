import asyncio
import pprint
import time
from datetime import datetime

import gspread
import pandas as pd

from ptn.spyplane.database.database import get_last_tick

from ptn.spyplane.constants import gc
from ptn.spyplane.modules.Helpers import get_ebgs_system

# gc = gspread.service_account('../data/spyplane-394209-39d59161dedb.json')
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


def update_row(row_name, username, user_id, timestamp):
    row_number = get_sheet_row(row_name)

    try:
        # Update only the last 3 cells in the sheet
        worksheet.update_cell(row_number, 3, username)
        worksheet.update_cell(row_number, 4, str(user_id))
        worksheet.update_cell(row_number, 5, timestamp)
        df_index = sheet_dataframe[sheet_dataframe.iloc[:, 0] == row_name].index

        if not df_index.empty:
            sheet_dataframe.at[df_index[0], sheet_dataframe.columns[2]] = username
            sheet_dataframe.at[df_index[0], sheet_dataframe.columns[3]] = user_id
            sheet_dataframe.at[df_index[0], sheet_dataframe.columns[4]] = timestamp

        return True

    except:
        return False


def get_systems():
    return sheet_dataframe[['System', 'Priority', 'Timestamp']].values.tolist()


async def post_list_by_priority():
    systems_list = get_systems()
    last_tick = int((await get_last_tick())[0].tick_time)

    api_check_systems = []
    for system in systems_list:
        dt_obj = datetime.strptime(system[2], "%d/%m/%Y %H:%M:%S")
        timestamp = int(time.mktime(dt_obj.timetuple()))
        difference_from_tick = ((last_tick - timestamp)/3600)

        # check if system has been checked in less than 3 hours from tick
        if difference_from_tick < 3:
            print('LESS THAN 3 HOURS')
            print(system[0])
            continue

        # check if priority 2 system has been checked in less than 24 hours from tick
        elif difference_from_tick < 24 and system[1] == '2':
            print('DONT POST, POST TOMORROW')
            print(system[0])
            continue

        # check if priority 3 system has been checked in less than 36 hours from tick
        elif difference_from_tick < 36 and system[1] == '3':
            print('DONT POST, POST IN TWO DAYS')
            print(system[0])
            continue

        else:
            api_check_systems.append(system)

    valid_systems = []
    # check ebgs for update times
    for system in api_check_systems:
        try:
            timestamp = get_ebgs_system(system[0])
        except:
            print(f'Error with getting timestamp: {system[0]}')
            continue
        if not timestamp:
            print(':(')
        difference_from_tick = ((last_tick - timestamp)/3600)

        # check if system has been checked in less than 3 hours from tick
        if difference_from_tick < 3:
            print('LESS THAN 3 HOURS')
            print(system[0])
            continue

        # check if priority 2 system has been checked in less than 24 hours from tick
        elif difference_from_tick < 24 and system[1] == '2':
            print('DONT POST, POST TOMORROW')
            print(system[0])
            continue

        # check if priority 3 system has been checked in less than 36 hours from tick
        elif difference_from_tick < 36 and system[1] == '3':
            print('DONT POST, POST IN TWO DAYS')
            print(system[0])
            continue

        else:
            # print('Yessir')
            # print(system[0])
            valid_systems.append(system)

    pprint.pp(valid_systems)
    return valid_systems

