import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

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

data_dir = "data/raw/pair_data/max_daily/"

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

def update_csv(pair, symbol):
    filename = os.path.join(data_dir, f"{pair}.csv")
    
    if os.path.exists(filename):
        df = pd.read_csv(filename, index_col=0, parse_dates=True)
        last_date = df.index[-1]
        print(f"Last date for {pair} is {last_date}")
        
        next_date = last_date + timedelta(days=1)
        print(f"Next date for {pair} is {next_date}")

        current_date = datetime.now().date()
        print(f"Current date is {current_date}")

        # Correct date comparison
        if next_date.date() >= current_date:
            print(f"No new data needed for {pair} as the next date is in the future.")
            return
        
        end_date = current_date.strftime('%Y-%m-%d')
        
        new_data = fetch_forex_data(symbol, next_date.strftime('%Y-%m-%d'), end_date)
        if new_data is not None and not new_data.empty:
            new_data = new_data[['Close']]
            new_data.columns = [pair]
            df = df.append(new_data)
            df = df[~df.index.duplicated(keep='last')] 
            print(f"Data to be saved for {pair}:\n{df.tail()}")
            df.to_csv(filename)
            print(f"Updated data for {pair}")
        else:
            print(f"No new data fetched for {pair}")
    else:
        print(f"File {filename} does not exist. Please check the file path.")

if __name__ == "__main__":
    for pair, symbol in pairs.items():
        try:
            update_csv(pair, symbol)
        except Exception as e:
            print(f"Error updating {pair}: {e}")
