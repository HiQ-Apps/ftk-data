import requests
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
import os

load_dotenv()

class HigherFrequencyPrices:
    def __init__(self, instrument, granularity="H1"):
        self.api_key = os.getenv("OANDA_API_KEY")
        self.instrument = instrument
        self.granularity = granularity
        self.base_url = 'https://api-fxtrade.oanda.com/v3/instruments'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}'
        }
        self.data = None

    def fetch_prices(self, start, end):
        params = {
            "from": start,
            "to": end,
            "granularity": self.granularity
        }

        url = f"{self.base_url}/{self.instrument}/candles"
        response = requests.get(url, headers=self.headers, params=params)

        if response.status_code == 200:
            data = response.json()
            candles = data['candles']
            df = pd.DataFrame(candles)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            df['close'] = df['mid'].apply(lambda x: x['c']).astype(float)
            return df[['close']]
        else:
            print(f"Failed to fetch data: {response.status_code}")
            print(f"Response content: {response.content}")
            return None

if __name__ == "__main__":
    instrument = 'EUR_USD'
    granularity = 'H1'
    start_date = datetime(2019, 1, 1)
    end_date = datetime(2021, 2, 1)

    combined_data = pd.DataFrame()

    current_start = start_date
    while current_start < end_date:
        current_end = current_start + relativedelta(months=1)
        if current_end > end_date:
            current_end = end_date

        hf_prices = HigherFrequencyPrices(instrument=instrument, granularity=granularity)
        start_iso = current_start.strftime('%Y-%m-%dT%H:%M:%SZ')
        end_iso = current_end.strftime('%Y-%m-%dT%H:%M:%SZ')
        print(f"Fetching data from {start_iso} to {end_iso}")

        df = hf_prices.fetch_prices(start=start_iso, end=end_iso)
        if df is not None:
            combined_data = pd.concat([combined_data, df])

        current_start = current_end

    output_filename = f'{instrument}_{granularity}_combined.csv'
    combined_data.to_csv(output_filename)
    print(f"Combined data saved to {output_filename}")
