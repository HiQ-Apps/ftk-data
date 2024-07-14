import os
import pandas as pd
from datetime import datetime
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.utils import fetch_forex_data, load_data, calculate_dynamic_strength, save_to_mongo, PAIRS

pair_data = {}
start_date = '2003-12-01'

for pair, symbol in PAIRS.items():
    df = fetch_forex_data(symbol, start_date, datetime.now().strftime('%Y-%m-%d'))
    if not df.empty:
        pair_data[pair] = df['Close']

save_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data/raw/pair_data/max_daily'))
os.makedirs(save_dir, exist_ok=True)

for pair, df in pair_data.items():
    filename = os.path.join(save_dir, f"{pair}.csv")
    df.to_csv(filename)
    print(f"Saved data for {pair} to {filename}")

# Load data to calculate dynamic strength
data_max_daily = load_data('daily', 'max')

if data_max_daily:
    print("Daily closing prices have been loaded!")

def main():
    for pair in data_max_daily:
        data_max_daily[pair].index = pd.to_datetime(data_max_daily[pair].index)

    common_start_date = max(df.index.min() for df in data_max_daily.values())
    time_points_max_daily = pd.date_range(start=common_start_date, end=datetime.now(), freq='D')

    print(f"Calculating dynamic strength for time points: {time_points_max_daily}")

    strength_max_daily = calculate_dynamic_strength(data_max_daily, time_points_max_daily)
    print(f"Calculated Relative Strengths:\n{strength_max_daily}")

    save_to_mongo(strength_max_daily, 'relative_strengths')

if __name__ == "__main__":
    main()
