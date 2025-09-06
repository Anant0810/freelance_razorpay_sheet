import argparse
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
import os
# import razorpay
import requests
from requests.auth import HTTPBasicAuth
import gspread_pandas
from gspread_pandas import Spread
import logging
import sys
import pytz
import warnings
from client_info import clients as client_info
from google_sheets_models import *
import gspread



warnings.simplefilter(action='ignore', category=FutureWarning)

directory = os.path.dirname(os.path.realpath(__file__))
cfg = gspread_pandas.conf.get_config(conf_dir=directory, file_name='client_secret.json')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')

log_directory = os.path.join(directory, "logs")
file_handler = logging.FileHandler(os.path.join(log_directory, 'automate_rt2.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


DATE_STRING = "%Y-%m-%d %H:%M:%S"

tz = pytz.timezone('Asia/Kolkata')

def convert_to_1990_system(date):
    return (date - datetime(1900, 1, 1)+ timedelta(days=2)).days()

def get_time_range():
    yesterday = (datetime.now(tz=tz) - timedelta(days=1)).date().strftime(DATE_STRING)
    today = (datetime.now(tz=tz) - timedelta(days=0)).strftime(DATE_STRING)
    return yesterday, today

def get_timestamp_data(start, end):
    start_date = datetime.strptime(start, DATE_STRING)
    end_date = datetime.strptime(end, DATE_STRING)
    from_ = datetime.timestamp(start_date)
    to = datetime.timestamp(end_date)
    return from_, to

def get_yesterday_str(days=1):
    tz = pytz.timezone('Asia/Kolkata')
#     today_dt = datetime.now(tz).date()
#     today_dt = today_dt - timedelta(days=days)
    today_dt = datetime.now(tz)
    today = today_dt.strftime(DATE_STRING)
    return today

def get_flatter_df(df,k='webinar_name', colname='notes'):
    assert 'notes' in df.index, 'no notes in column'
#     print(df[colname])
    if isinstance(df[colname], dict):
        for key, value in df[colname].items():
            if key == k:
                return value
            elif k == 'course_name':
                if key == 'paymentPage':
                    return value
                elif key == 'desc':
                    return value
                elif key == 'course':
                    return value
                elif key == 'source':
                    return value
                
    return ''

cols = ['Start Date', 'datetime', 'payment page id', 'payment page name', 'id', 'status', 'created_at', 
            'vpa', 'name', 'email_notes', 'phone', 'amount', 'contact', 'email', 'webinar', 'utm_source', 'notes', 'international', 'currency', 'description']

def convert_to_1990_system(date):
    return (date - datetime(1900, 1, 1)+ timedelta(days=2)).days

def get_datetime(created, tz=tz):
    result = datetime.fromtimestamp(created, tz=tz)
    result = result.strftime(DATE_STRING)
    return datetime.strptime(result, DATE_STRING)

def create_pl_df(payments, payment_page_id, payment_page_name, start_date, end_date, cols=cols):
    data = pd.DataFrame(payments)
#     print(data.columns)
    from_, to = get_timestamp_data(start_date, end_date)

    print('creataing df from', from_, to)
#     print(data)

    data['name'] = data.apply(lambda x : get_flatter_df(x, k='name') , axis=1)
    data['email_notes'] = data.apply(lambda x : get_flatter_df(x, k='email') , axis=1)
    data['phone'] = data.apply(lambda x : get_flatter_df(x, k='phone') , axis=1)
    data['webinar'] = data.apply(lambda x : get_flatter_df(x, k='course_name'), axis=1)
    data['utm_source'] = data.apply(lambda x : get_flatter_df(x, k='utm_source'), axis=1)

    captured_data = data[data['captured'] == True].copy()
    if captured_data.shape[0] == 0: return pd.DataFrame()
    
    captured_data.loc[:, 'datetime'] = captured_data['created_at'].apply(lambda x :get_datetime(x, tz=tz))
    captured_data.loc[:, 'Start Date'] = captured_data['datetime'].apply(lambda x : convert_to_1990_system(x))
    captured_data_date =  captured_data[(captured_data['datetime'] > start_date) & (captured_data['datetime'] < end_date)].copy()
    captured_data_date['datetime'] = captured_data_date['datetime'].dt.strftime(DATE_STRING)
    captured_data_date['notes'] = captured_data_date['notes'].apply(str)
    # captured_data_date = captured_data[(captured_data['created_at'] >= from_) & (captured_data['created_at'] < to)].copy()
    print(captured_data_date.shape)

    if captured_data_date.shape[0] == 0: return pd.DataFrame()
#     captured_data_date.loc[:, 'start_date'] = captured_data_date['datetime'].dt.strftime(DATE_STRING)
    captured_data_date.loc[:, 'amount'] = captured_data_date['amount'] /100
    captured_data_date.loc[:, 'payment page id'] = payment_page_id
    captured_data_date.loc[:, 'payment page name'] = payment_page_name

    
    payment_link_df = captured_data_date[cols]
    payment_link_df.reset_index(inplace=True, drop=True)
    
    return payment_link_df

def get_payment_link_data(client, start_date, end_date):
    print(start_date, end_date)
    payment_link_ids = client_info[client]["payment_links"]
    key_id, key_secret = client_info[client]["key"], client_info[client]["secret"]
    auth = HTTPBasicAuth(key_id, key_secret)
    df = pd.DataFrame()
#     for payment_page_name, payment_page_id in payment_link_ids.items():
    payment_page_name = 'all'
    payment_page_id = 'no'
    payments = []
    fetching = True
    skip=0
    count=100
    inc = 0
    while fetching:
        print(skip, inc)
        res = requests.get(
                    url=f"https://api.razorpay.com/v1/payments?skip={skip}&count={count}", 
                    auth=auth)
        try:
            if res.json()['items'] == [] : break
        except KeyError as e:
            print('error', e)
            print(res.json())
            sys.exit()
        payments.extend(res.json()['items'])
        inc += 1
        skip= inc*100
        to = start_date
        try:
            print('to', datetime.fromtimestamp(res.json()['items'][-1]['created_at'], tz=tz).strftime(DATE_STRING) > to)
        except Exception as e:
            print(e)
        fetching = datetime.fromtimestamp(res.json()['items'][-1]['created_at'], tz=tz).strftime(DATE_STRING) > to
        print(payment_page_name, datetime.fromtimestamp(res.json()['items'][-1]['created_at'], tz=tz).strftime(DATE_STRING))

        ##update to google sheet
        print(payments[:5])
    if len(payments) != 0:
        payment_link_df = create_pl_df(payments, payment_page_id, payment_page_name, start_date, end_date, cols=cols)
        print(f"Updated Successfully for Payment page {payment_page_name} - {payment_link_df.shape[0]}")
        df = pd.concat([df, payment_link_df])
    else:
        message = f"No data returned for {payment_page_name}"
    print(df.columns)
    df = df.sort_values('datetime', ascending=True) if df.shape[0] > 0 else df
    print("get_payment_link_data", df.shape)
    return df

def get_razorpay_data(client, start_date):
    today = get_yesterday_str(days=0)
    
    end_date = today
    # end_date = '2024-05-03 00:00:00'
    print(end_date)
    if start_date == None:
        since = get_yesterday_str(days=3)
        since = "2025-09-01 00:00:00"
        message = f"DB initalized from {since}"
        print(since)
        # try:
        dff = get_payment_link_data(client, start_date=since, end_date=end_date)
            # print("get_razorpay_data", dff.shape)
        # except:
        #     message = "Something went wrong in requests!"
            # dff = pd.DataFrame()
    else:
#         since_dt = datetime.strptime(start_date, DATE_STRING)
#         since_d = since_dt + timedelta(days=1)
        since = start_date
        
        
        if since == today:
            return pd.DataFrame(), "Already Updated"
        message = "Updated Successfully"
        try:
            dff = get_payment_link_data(client, start_date=since, end_date=end_date)
        except:
            message = "Something went wrong in requests!"
            dff = pd.DataFrame()

        message = "Updated Successfully"

    message = "No data returned" if dff.shape[0] == 0 else message

    return dff, message
    
import time

def get_start_date_with_retries(sheet, sheet_name, retries=3, delay=60):
    for attempt in range(retries):
        try:
            result = get_start_date(sheet, sheet_name)
            if result:
                return result
            else:
                logger.info(f"{sheet_name} : [Attempt {attempt+1}] No data found, retrying in {delay} seconds...")
        except Exception as e:
            logger.info(f"{sheet_name} : [Attempt {attempt+1}] Error: {e}, retrying in {delay} seconds...")

        time.sleep(delay)

    print("All attempts failed or returned no valid date.")
    return None


def update_sheets(sheet, client):
    # print(client, level)
    sheet_name = f'{client}_razorpay'

    has_sheet = find_sheet(sheet, sheet_name)
    print(sheet_name, has_sheet)
    
    since_dt = None

    if has_sheet:
        since_dt = get_start_date_with_retries(sheet, sheet_name)
        if not since_dt:
            logger.info(f"{sheet_name} : Something went wrong while getting start date")
            return
    
    print(f'start calling api with {since_dt}')
    df, message = get_razorpay_data(client, start_date=since_dt)
    if since_dt:
        # data is there in the sheet and df is new data from api
        worksheet = sheet.worksheet(sheet_name)
        values = df.values.tolist()
        columns = None
    else:
        worksheet = create_worksheet(sheet, sheet_name)
        values =  df.values.tolist()
        columns = df.columns.values.tolist()
        
    try:
        update_data(worksheet, values, ['Start Date', 'id'], columns)
        logger.info(f" MESSAGE - {client.capitalize()} : --> {message}")
    except Exception as e:
        logger.error(f"Error updating sheet {sheet_name} for client {client}: {e}")
        return False

    
    return True        

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Provide Client's name")
    parser.add_argument('-c', '--client', type=str, default='all', help="Client's name")
    
    args = parser.parse_args()
    
    if args.client not in client_info.keys() and args.client != 'all':
        sys.exit()
    directory = os.path.dirname(os.path.realpath(__file__))
    gc = gspread.service_account(filename=os.path.join(directory, './client_secret.json'))
    sheet = gc.open('Astro Arun Pandit Razorpay 2')
    clients = []
    
    if args.client == 'all':
        clients.extend(client_info.keys())
    else:
        clients.append(args.client)
        
    for client in clients:
        print(client)
        update_sheets(sheet, client)