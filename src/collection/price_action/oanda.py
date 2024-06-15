import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import json

import yaml


load_dotenv()

def load_config(path):
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
    return config

config_path = os.getenv('V20_CONF', os.path.expanduser('C:/Users/melis/Desktop/ftk-data/v20.conf'))
print(f"Loading config from: {config_path}")
config = load_config(config_path)
print(f"Config loaded: {config}")

def get_data(instrument, granularity, start, end):
    access_token = config['token']
    client = oandapyV20.API(access_token=access_token, environment='live')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)
    print(f"Fetching data from {start_date} to {end_date} with granularity {granularity}")
    params = {
        "from": start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "to": end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
        "granularity": granularity
    }
    r = instruments.InstrumentsCandles(instrument=instrument, params=params)
    
    try:
        client.request(r)
    except oandapyV20.exceptions.V20Error as e:
        print(f"V20Error: {e}")
        print(f"Response: {e.response}")
        raise

    print("Data fetched successfully")
    
    closing_prices = [
        {
            'time': candle['time'],
            'close': candle['mid']['c']
        } for candle in r.response['candles']
    ]
    
    return closing_prices

end_date = datetime.now()
start_date = end_date - timedelta(days=2*365)
start = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
end = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')

print(f"Start date: {start}")
print(f"End date: {end}")

closing_prices = get_data('EUR_USD', 'H1', start, end)

with open('closing_prices.json', 'w') as f:
    json.dump(closing_prices, f, indent=4)

print("Closing prices have been saved to closing_prices.json")
