import os
import json
import argparse
from datetime import datetime, timedelta

# Import your scripts as modules
from collection.news.economic_calendar import fetch_and_save_calendar_data
from collection.price_action.oanda import get_data

def run_economic_calendar(start_date, end_date):
    output_filename = f'economic_calendar_data_{start_date.split(" ")[0]}_{end_date.split(" ")[0]}_2024.json'
    fetch_and_save_calendar_data(start_date, end_date, output_filename)

def run_oanda_data():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=2*365)
    start = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    closing_prices = get_data('EUR_USD', 'H1', start, end)
    save_path = os.path.join(os.path.dirname(__file__), 'collection', 'price_action', 'closing_prices.json')
    with open(save_path, 'w') as f:
        json.dump(closing_prices, f, indent=4)
    print(f"Closing prices have been saved to {save_path}")

def main(start_date, end_date):
    print("Starting data collection...")
    run_economic_calendar(start_date, end_date)
    run_oanda_data()
    print("Data collection completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run data collection scripts for economic calendar and price data.")
    parser.add_argument('start_date', type=str, help="Start date in the format MonYYYY (e.g., Jan2024)")
    parser.add_argument('end_date', type=str, help="End date in the format MonYYYY (e.g., May2024)")

    args = parser.parse_args()

    main(args.start_date, args.end_date)
