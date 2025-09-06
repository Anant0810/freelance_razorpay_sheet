import pandas as pd
from datetime import datetime, timedelta
from gspread.exceptions import APIError
import time

ROWS = 10000
COLS = 26

DATE_STRING = "%Y-%m-%d %H:%M:%S"

def char_position(letter):
    return ord(letter) - 97

def pos_to_char(pos):
    return chr(pos + 97)


def find_sheet(sheet, sheet_name):
    try:
        for ix, ws in enumerate(sheet.worksheets()):
            if sheet_name == ws.title:
                return True
        return False
    except APIError as e:
        print(e)
        time.sleep(5)
        return find_sheet(sheet, sheet_name)
    except Exception as e:
        print(e)
        raise Exception("Something went wrong while finding sheet")
        


def create_worksheet(sheet, sheet_name:str, rows:int=ROWS, cols:int=COLS):
    """create worksheet with given rows and cols"""
    if not find_sheet(sheet, sheet_name):
        # create the sheet in worksheet
        sheet.add_worksheet(sheet_name, rows=rows, cols=cols)
    
    return sheet.worksheet(sheet_name)


## read functionality

def read_data(worksheet):
    try:
        values = worksheet.get_all_values()
    except APIError as e:
        print(e)
        time.sleep(5)
        values = worksheet.get_all_values()
    except Exception as e:
        print(e)
        raise Exception("Something went wrong while reading data")


    return values

def get_shape(worksheet):
    
    values = read_data(worksheet)
    if not values:
        return 0, 0
    return len(values), len(values[0])

def get_start_date(sheet, sheet_name):
    worksheet = sheet.worksheet(sheet_name)
    if find_sheet(sheet, sheet_name):
        worksheet = sheet.worksheet(sheet_name)
        values = read_data(worksheet)
        df = pd.DataFrame(data=values[1:], columns=values[0])
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.sort_values(['datetime'], inplace=True, ascending=True)
        print(type(df.iloc[-1, 1]))

        return df.iloc[-1, 1].strftime(DATE_STRING)
    return None

def add_data(worksheet, new_data, columns=None):
    rows, cols = get_shape(worksheet)
    row_count = worksheet.row_count
    if row_count < ROWS :
         total_rows = ROWS 
    else:
        total_rows = row_count

    if len(new_data) == 0:
        n_rows, n_cols = 0, 0
    else:
        n_rows, n_cols = len(new_data), len(new_data[0])
    print(f'old rows: {rows} \nnew rows: {n_rows}\n ROWS: {total_rows}')

    if (rows + n_rows + 500) > total_rows:
        print('adding rows')
        worksheet.add_rows(3000)

    if (cols + n_cols + 5) > total_rows:
        worksheet.add_cols(10)
    
    if new_data :
        df = pd.DataFrame(data=new_data, columns=columns)
        df.fillna(0, inplace=True)
        df.sort_values(df.columns[1], inplace=True, ascending=True)
        if columns:
            new_data = [df.columns.values.tolist()] + df.values.tolist()
        else:    
            new_data = df.values.tolist()
    
    worksheet.append_rows(new_data)

def update_data(worksheet, new_data, subset_cols, columns):

    add_data(worksheet, new_data, columns)
    ## read the data and remove for duplicates
    # time.sleep(2)
    # values = read_data(worksheet)
    # df = pd.DataFrame(data=values[1:], columns=values[0])
    # try: 
    #     idxs = df[df.duplicated(keep='last', subset=subset_cols)].index.values.tolist()
    # except IndexError:
    #     print("No duplicate found")
    #     idxs = []
    #     pass
    
    # if idxs: delete_data(worksheet, idxs)

    



def delete_data(worksheet, indexes):
    print('duplicates', len(indexes))
    # for idx in indexes:
    #     worksheet.delete_rows(idx+1)