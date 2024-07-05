import json
from datetime import datetime, timedelta
import requests
from colorama import Fore, Style
import random
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os
import csv

from sklearn.base import r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

def fetch_page_source_selenium(url):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    firefox_options.add_argument("--disable-blink-features=AutomationControlled")
    firefox_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = FirefoxService(executable_path='C://Users/Melissa/geckodriver.exe')
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

def save_to_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_month_list(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m")
    end = datetime.strptime(end_date, "%Y-%m")
    months = []
    while start <= end:
        months.append((start.strftime("%b").lower(), start.year))
        start = datetime(start.year + (start.month // 12), ((start.month % 12) + 1), 1)
    return months

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


def save_to_csv(data, filename):
    """
    Saves the given data to a CSV file.

    Args:
        data (list): A list of dictionaries containing economic calendar data.
        filename (str): The name of the CSV file to save the data to.
    """
    if not data:
        print("No data to save.")
        return

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Define the header based on the keys of the first dictionary
    header = data[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=header)

        # Write the header
        writer.writeheader()

        # Write the data rows
        for row in data:
            writer.writerow(row)

    print(f"Data successfully saved to {filename}")

pairs = [
    'EURUSD', 'USDJPY', 'GBPUSD', 'USDCHF', 
    'EURJPY', 'EURGBP', 'GBPJPY', 'CHFJPY', 
    'EURCHF', 'GBPCHF'
]

def evaluate_model(X_train, X_test, y_train, y_test):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    return model, mse, r2