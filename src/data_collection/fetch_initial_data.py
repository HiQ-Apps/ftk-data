import yfinance as yf
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import PAIRS
# Function to fetch forex data with a given interval and start date
def fetch_forex_data_yf(symbol, start_date, interval='1d'):
    data = yf.download(symbol, start=start_date, interval=interval)
    return data

# Fetch and store data
pair_data = {}
start_date = '2003-12-01'  # Starting date for the data

for pair, symbol in PAIRS.items():
    df = fetch_forex_data_yf(symbol, start_date)
    if not df.empty:
        pair_data[pair] = df['Close']

save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/raw/pair_data'))
os.makedirs(save_dir, exist_ok=True)

for pair, df in pair_data.items():
    filename = os.path.join(save_dir, f"{pair}.csv")
    df.to_csv(filename)
    print(f"Saved data for {pair} to {filename}")
