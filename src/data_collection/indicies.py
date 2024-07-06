import yfinance as yf
import pandas as pd
import os

# List of forex pairs to fetch
pairs = {
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

# Function to fetch forex data with a given interval
def fetch_forex_data_yf(symbol, interval='1d'):
    data = yf.download(symbol, period='max', interval=interval)
    return data

# Fetch and store data
pair_data = {}
for pair, symbol in pairs.items():
    df = fetch_forex_data_yf(symbol)
    if not df.empty:
        pair_data[pair] = df['Close']

save_dir = os.path.abspath('../../data/raw/pair_data/max_daily')
os.makedirs(save_dir, exist_ok=True)

for pair, df in pair_data.items():
    filename = os.path.join(save_dir, f"{pair}.csv")
    df.to_csv(filename)
    print(f"Saved data for {pair} to {filename}")