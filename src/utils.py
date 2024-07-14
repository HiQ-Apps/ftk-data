import os
import csv
import json
import random
import time
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import datetime
from pymongo import MongoClient
import pymongo
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from colorama import Fore, Style

"""
setup for database connection 'forex'
"""
client = MongoClient('localhost', 27017)
db = client['forex']

"""
constants
"""
PAIRS = {
    'EURUSD': 'EURUSD=X',
    'USDJPY': 'USDJPY=X',
    'GBPUSD': 'GBPUSD=X',
    'USDCHF': 'USDCHF=X',
    'EURJPY': 'EURJPY=X',
    'EURGBP': 'EURGBP=X',
    'GBPJPY': 'GBPJPY=X',
    'CHFJPY': 'CHFJPY=X',
    'EURCHF': 'EURCHF=X',
    'GBPCHF': 'GBPCHF=X'
}

def print_ascii_art():
    ascii_art = r""" 
 $$$$$$\                                                $$\                        $$\ $$\       $$\  $$\     
$$  __$$\                                               $$ |                       $$ |$$ |      \__| $$ |    
$$ /  \__|$$$$$$\   $$$$$$\   $$$$$$\ $$\   $$\       $$$$$$\   $$$$$$\   $$$$$$\  $$ |$$ |  $$\ $$\$$$$$$\   
$$$$\    $$  __$$\ $$  __$$\ $$  __$$\\$$\ $$  |      \_$$  _| $$  __$$\ $$  __$$\ $$ |$$ | $$  |$$ \_$$  _|  
$$  _|   $$ /  $$ |$$ |  \__|$$$$$$$$ |\$$$$  /         $$ |   $$ /  $$ |$$ /  $$ |$$ |$$$$$$  / $$ | $$ |    
$$ |     $$ |  $$ |$$ |      $$   ____|$$  $$<          $$ |$$\$$ |  $$ |$$ |  $$ |$$ |$$  _$$<  $$ | $$ |$$\ 
$$ |     \$$$$$$  |$$ |      \$$$$$$$\$$  /\$$\         \$$$$  \$$$$$$  |\$$$$$$  |$$ |$$ | \$$\ $$ | \$$$$  |
\__|      \______/ \__|       \_______\__/  \__|         \____/ \______/  \______/ \__|\__|  \__|\__|  \____/ 
"""
    print(Fore.GREEN + ascii_art + Style.RESET_ALL)



"""
utility functions for data and files
"""
data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/raw/pair_data/'))

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def read_csv(filename):
    try:
        return pd.read_csv(filename, index_col=0, parse_dates=True)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        return None

def save_csv(df, filename):
    try:
        df.to_csv(filename)
        print(f"Data saved to {filename}")
    except Exception as e:
        print(f"Error saving {filename}: {e}")

def save_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    header = data[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"Data successfully saved to {filename}")

def load_data(interval, period):
    data = {}
    folder = f'{period}_{interval}'
    print("folder", folder)
    folder_path = os.path.join(data_dir, folder)
    print("folder_path", folder_path)
    for pair in PAIRS:
        filename = os.path.join(folder_path, f"{pair}.csv")
        print("filename", filename)
        try:
            df = pd.read_csv(filename)
            date_column = df.columns[0]
            
            df[date_column] = pd.to_datetime(df[date_column], utc=True)
            if interval == 'daily':
                df[date_column] = df[date_column].dt.date

            df.set_index(date_column, inplace=True)
            data[pair] = df['Close']
        except Exception as e:
            print(f"LOAD_DATA Error reading {filename}: {e}")
    return data

def fetch_forex_data(symbol, start_date, end_date):
    print(f"Fetching data for {symbol} from {start_date} to {end_date}")
    try:
        data = yf.download(symbol, start=start_date, end=end_date, interval='1d')
        if data.empty:
            print(f"No data fetched for {symbol} in the given date range.")
        else:
            print(f"Data fetched for {symbol}:")
            print(data.head())
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    return data

def get_next_date(df):
    last_date = df.index[-1]
    return last_date + pd.Timedelta(days=1)

def calculate_dynamic_strength(data, time_points):
    currencies = ['USD', 'EUR', 'JPY', 'GBP', 'CHF']
    results = []
    for time_point in time_points:
        strength = {currency: 0 for currency in currencies}
        count = {currency: 0 for currency in currencies} 
        
        valid_data = True
        for pair, df in data.items():
            try:
                price = df.loc[time_point]
                base_currency, quote_currency = pair[:3], pair[3:]
                if 'JPY' in pair:
                    price /= 100  # Scale JPY to be comparable with other currencies
                if base_currency in currencies and quote_currency in currencies:
                    strength[base_currency] += price
                    strength[quote_currency] += 1 / price
                    count[base_currency] += 1
                    count[quote_currency] += 1
            except KeyError:
                print(f"Date {time_point} not found in {pair} data.")
                valid_data = False
                break
            except IndexError:
                print(f"Index error for {pair} data at {time_point}.")
                valid_data = False
                break
    
        if valid_data:
            for currency in strength:
                if count[currency] > 0:
                    strength[currency] /= count[currency]
            results.append(strength)
        else:
            results.append({currency: 0 for currency in currencies})

    return pd.DataFrame(results, index=time_points)



def save_to_mongo(df, collection_name):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["forex"]
    collection = db[collection_name]

    df = df.reset_index().rename(columns={'index': 'datetime'})
    df['datetime'] = df['datetime'].apply(lambda x: x.strftime('%Y-%m-%d'))

    data_dict = df.to_dict('records')

    filtered_data_dict = [
        record for record in data_dict
        if all(value != 0 for key, value in record.items() if key not in ['datetime', 'metadata'])
    ]

    for record in filtered_data_dict:
        if isinstance(record['datetime'], pd.Timestamp):
            record['datetime'] = record['datetime'].to_pydatetime()
        record['metadata'] = {"source": "relative_strengths"}

    for record in filtered_data_dict:
        if collection.count_documents({'datetime': record['datetime']}) == 0:
            collection.insert_one(record)

    print(f"Data saved to MongoDB collection '{collection_name}' in the '{db.name}' database.")



def fetch_page_source_selenium(url, driver_path='C://Users/Melissa/geckodriver.exe'):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-blink-features=AutomationControlled")
    firefox_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = FirefoxService(executable_path=driver_path)
    driver = webdriver.Firefox(service=service, options=firefox_options)

    try:
        driver.get(url)
        time.sleep(5)
        page_source = driver.page_source
    finally:
        driver.quit()

    return page_source

def fetch_page_source(url):
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0 Safari/537.36',
    ]
    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
    }

    session = requests.Session()
    session.headers.update(headers)

    response = session.get(url)

    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch the page... CODE: {response.status_code}")
