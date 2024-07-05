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

save_dir = '../../../data/raw/pair_data/max_daily'
os.makedirs(save_dir, exist_ok=True)

for pair, df in pair_data.items():
    # Calculate the 20-day EMA
    ema_20 = df.ewm(span=20, adjust=False).mean()
    
    # Fill missing data with the 20-day EMA
    df_filled = df.fillna(ema_20)
    
    filename = os.path.join(save_dir, f"{pair}.csv")
    df_filled.to_csv(filename)
    print(f"Saved data for {pair} to {filename}")

# Verify data for EUR/CHF
df_eurchf = pair_data['EURCHF']
print(df_eurchf.loc['2008-07-25':'2008-08-27'])
