import yfinance as yf
import requests
import pandas as pd
from tabulate import tabulate
from termcolor import colored
from config import API_KEY
import logging

def fetch_underlying_price(ticker) -> float:
    """
    Fetches the latest underlying price.
    Note: The data is 15 min delayed
    
    Params:
        ticker (str): Ticker symbol
    
    Returns:
        float: The latest closing price rounded to 2 decimal places
    """
    yf_ticker = yf.Ticker(ticker)
    return round(yf_ticker.history(period="1d")['Close'].iloc[-1], 2)

def fetch_options_snapshot(ticker, expiration_date, current_price, strike_count=5):
    """
    Fetches a snapshot of options contracts for the given ticker and expiration date.
    Retrieves options within ±strike_count strikes around the current price.
    
    Params:
        ticker(str)
        expiration_date(str): Options expiration date in YYYY-MM-DDD
        current_price(float): The current stock price from fetch_underlying_price
        strike_count(int): Number of strikes above and below the current price
    
    Returns:
        list: A list of options data dictionary within the specific strike range.
    """
    data = []
    try:
        for strike_price in range(int(current_price - strike_count), int(current_price + strike_count + 1), 1):
            url = (f"https://api.polygon.io/v3/snapshot/options/{ticker}"
                f"?strike_price={strike_price}&expiration_date={expiration_date}&apiKey={API_KEY}")
            response = requests.get(url)
            
            if response.status_code == 200:
                options_snapshot = response.json().get('results', [])
                
                for option in options_snapshot:
                    data.append({
                        "Strike Price": option['details']['strike_price'],
                        "Type": option['details']['contract_type'],
                        "contract": option['details']['ticker'],
                        "Close Price": option['day'].get('close'),
                        "Volume": option['day'].get('volume'),
                        "Open Interest": option.get('open_interest'),
                        "Greeks": {
                            "delta": option['greeks'].get('delta'),
                            "gamma": option['greeks'].get('gamma'),
                            "theta": option['greeks'].get('theta'),
                            "vega": option['greeks'].get('vega')
                        },
                        "Implied Volatility": option.get('implied_volatility'),
                    })
            else:
                logging.warning(f"Failed to fetch options for strike {strike_price} - Status Code {response.status_code}")

        logging.info(f"Total contracts retrieved: {len(data)}")
    except Exception as e:
        logging.error(f"Error fetching options snapshot: {e}")
    return data


def calculate_pcr(options_data):
    """
    Calculates the Put/Call Ratio (PCR) based on volume of the contracts.
    """
    call_volume = sum(option['Volume'] for option in options_data if option['Type'] == 'call')
    put_volume = sum(option['Volume'] for option in options_data if option['Type'] == 'put')
    return round(put_volume / call_volume, 2) if call_volume else None

def print_colored_pivot_df(df):
    """
    Print a side-by-side table of calls and puts for each strike price.
    """

    calls_df = df[df['Type'] == 'call'].copy()
    puts_df = df[df['Type'] == 'put'].copy()
    
    calls_df = calls_df.rename(columns={
        'Volume': 'Call Volume',
        'Open Interest': 'Call Open Interest',
        'Close Price': 'Call Close Price'
    })
    puts_df = puts_df.rename(columns={
        'Volume': 'Put Volume',
        'Open Interest': 'Put Open Interest',
        'Close Price': 'Put Close Price'
    })
    

    calls_df.set_index('Strike Price', inplace=True)
    puts_df.set_index('Strike Price', inplace=True)


    combined_df = pd.concat([calls_df[['contract', 'Call Close Price', 'Call Volume', 'Call Open Interest']],
                             puts_df[['contract', 'Put Close Price', 'Put Volume', 'Put Open Interest']]], 
                            axis=1)

    combined_df['Call Close Price'] = combined_df['Call Close Price'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else '')
    combined_df['Put Close Price'] = combined_df['Put Close Price'].apply(lambda x: f"{x:.2f}" if pd.notnull(x) else '')

    max_call_volume = combined_df['Call Volume'].max()
    max_put_volume = combined_df['Put Volume'].max()

    combined_df['Call Volume'] = combined_df['Call Volume'].apply(lambda x: colored(x, 'green') if x == max_call_volume else x)
    combined_df['Put Volume'] = combined_df['Put Volume'].apply(lambda x: colored(x, 'red') if x == max_put_volume else x)
    
    max_call_open_interest = combined_df["Call Open Interest"].max()
    max_put_open_interest = combined_df["Put Open Interest"].max()
    
    combined_df['Call Open Interest'] = combined_df['Call Open Interest'].apply(lambda x: colored(x, 'green') if x == max_call_open_interest else x)
    combined_df['Put Open Interest'] = combined_df['Put Open Interest'].apply(lambda x: colored(x, 'red') if x == max_put_open_interest else x)
    
    # Print the table
    print(tabulate(combined_df, headers='keys', tablefmt='fancy_grid'))