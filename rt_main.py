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

warnings.simplefilter(action='ignore', category=FutureWarning)

directory = os.path.dirname(os.path.realpath(__file__))
gspread_pandas.conf.get_config(conf_dir=directory, file_name='client_secret.json')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')

log_directory = os.path.join(directory, "logs")
file_handler = logging.FileHandler(os.path.join(log_directory, 'automate_rt_razorpay.log'))
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

DATE_STRING = "%Y-%m-%d %H:%M:%S"

tz = pytz.timezone('Asia/Kolkata')

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

def get_flatter_df(df,k='name', colname='notes'):
    for key, value in df[colname].items():
        if key == k:
            return value
    return 

cols = ['start_date', 'datetime', 'payment page id', 'payment page name', 'id', 'status', 'created_at', 
            'vpa', 'name', 'email_notes', 'phone', 'amount', 'contact', 'email']

def get_datetime(created, tz=tz):
    result = datetime.fromtimestamp(created, tz=tz)
    result = result.strftime(DATE_STRING)
    return datetime.strptime(result, DATE_STRING)

def create_pl_df(payments, payment_page_id, payment_page_name, start_date, end_date, cols=cols):
    data = pd.DataFrame(payments)
    from_, to = get_timestamp_data(start_date, end_date)

    print('creataing df from', from_, to)

    data['name'] = data.apply(lambda x : get_flatter_df(x, k='name') , axis=1)
    data['email_notes'] = data.apply(lambda x : get_flatter_df(x, k='email') , axis=1)
    data['phone'] = data.apply(lambda x : get_flatter_df(x, k='phone') , axis=1)

    captured_data = data[data['captured'] == True].copy()
    if captured_data.shape[0] == 0: return pd.DataFrame()
    
    captured_data.loc[:, 'datetime'] = captured_data['created_at'].apply(lambda x :get_datetime(x, tz=tz))
    captured_data.loc[:, 'start_date'] = captured_data['datetime'].dt.strftime("%Y-%m-%d")
    captured_data_date =  captured_data[(captured_data['datetime'] > start_date) & (captured_data['datetime'] < end_date)].copy()
    # captured_data_date = captured_data[(captured_data['created_at'] >= from_) & (captured_data['created_at'] < to)].copy()
    print(captured_data_date.shape)

    if captured_data_date.shape[0] == 0: return pd.DataFrame()
#     captured_data_date.loc[:, 'start_date'] = captured_data_date['datetime'].dt.strftime(DATE_STRING)
    captured_data_date.loc[:, 'amount'] = captured_data_date['amount'] /100
    captured_data_date.loc[:, 'payment page id'] = payment_page_id
    captured_data_date.loc[:, 'payment page name'] = payment_page_name

    
    payment_link_df = captured_data_date[cols]
    payment_link_df = payment_link_df.drop_duplicates().copy()
    payment_link_df.reset_index(inplace=True, drop=True)
    
    return payment_link_df


def get_payment_link_data(client, start_date, end_date):
    print(start_date, end_date)
    payment_link_ids = client_info[client]["payment_links"]
    key_id, key_secret = client_info[client]["key"], client_info[client]["secret"]
    auth = HTTPBasicAuth(key_id, key_secret)
    df = pd.DataFrame()
    for payment_page_name, payment_page_id in payment_link_ids.items():
        payments = []
        fetching = True
        skip=0
        count=100
        inc = 0
        while fetching:
            res = requests.get(url=f"https://api.razorpay.com/v1/payments?skip={skip}&count={count}&payment_link_id={payment_page_id}", 
                        auth=auth)
            try:
                if res.json()['items'] == [] : break
            except KeyError as e:
                print(e)
                print(res.json())
                sys.exit()
            payments.extend(res.json()['items'])
            inc += 1
            skip= inc*100
            to = start_date
            fetching = datetime.fromtimestamp(res.json()['items'][-1]['created_at'], tz=tz).strftime(DATE_STRING) > to
            print(payment_page_name, datetime.fromtimestamp(res.json()['items'][-1]['created_at'], tz=tz).strftime(DATE_STRING))

        ##update to google sheet
        print(len(payments))
        if len(payments) != 0:
            payment_link_df = create_pl_df(payments, payment_page_id, payment_page_name, start_date, end_date, cols=cols)
            print(f"Updated Successfully for Payment page {payment_page_name} - {payment_link_df.shape[0]}")
            df = pd.concat([df, payment_link_df])
        else:
            message = f"No data returned for {payment_page_name}"
    print(df.columns)
    df = df.sort_values('datetime', ascending=False) if df.shape[0] > 0 else df
    print("get_payment_link_data", df.shape)
    return df

def get_razorpay_data(client, start_date):
    today = get_yesterday_str(days=0)
    
    end_date = today
    print(end_date)
    if start_date == None:
        since = get_yesterday_str(days=3)
        since = "2024-04-14 00:00:00"
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
    

def update_sheets(client):
    # print(client, level)
    sheet_name = f'{client}_razorpay'
    new_df = pd.DataFrame()
#     # spread = Spread('TEST')
    spread = Spread('realtime razorpay clients')
    if spread.find_sheet(sheet_name):
        print(f'has sheet {sheet_name}')
        df = spread.sheet_to_df(header_rows=1, index=0, start_row=3, sheet=sheet_name)

        # print(df.head())
        has_df = True
#         datetime.strptime(df['datetime'][0], DATE_STRING).date()
        try:
            since_dt = datetime.strptime(df['datetime'][0], DATE_STRING)
            
            
        except ValueError as e:
            print(e)
            has_df = False
        
        print(since_dt, 'update_sheet')

        if has_df:
            print(f'has df in {sheet_name}')
            since_dt = since_dt.strftime(DATE_STRING)
            dff, message = get_razorpay_data(client, start_date=since_dt)
            if dff.shape[0] > 0:
                new_df = pd.concat([dff, df], ignore_index=True)
            ### concat with old ... 
        else:
            ### new_df
            print(f'does not have df in {sheet_name}')
            dff, message = get_razorpay_data(client, start_date=None)
            if dff.shape[0] > 0:
                new_df = dff.copy()
        
    else:
        print(f'did not find {sheet_name}')
        dff, message = get_razorpay_data(client, start_date=None)
        print(dff.shape)
        if dff.shape[0] > 0:
            new_df = dff.copy()
    
    if new_df.shape[0]>0:
        spread.df_to_sheet(new_df, sheet=sheet_name, start='A3', replace=True, index=False)
        result = True
    else:
        result = False
    
    logger.info(f" MESSAGE - {client.capitalize()} : --> {message}")
    return result


if __name__ == '__main__':

    success_dict = {}
    parser = argparse.ArgumentParser(description="Provide Client's name")
    parser.add_argument('-c', '--client', type=str, default='all', help="Client's name")
    start_date, end_date = get_time_range()
    args = parser.parse_args()
    clients = client_info.keys()
    if args.client not in clients and args.client != 'all':
        sys.exit()
    # print('main run')
    if args.client == 'all':
        for client in clients:
            result = update_sheets(client)
            success_dict[client] = result

    else:
        # print(f'main {args.client}')
        # print(f"{attribution_windows[args.client]}")
        if args.client not in clients:
            sys.exit()
        result = update_sheets(args.client)
        success_dict[args.client] = result