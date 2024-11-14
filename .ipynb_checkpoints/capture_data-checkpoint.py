import pandas as pd
from datetime import datetime, timedelta
from db import save_snapshot
import yfinance as yf
from utils import print_colored_pivot_df, fetch_underlying_price, fetch_options_snapshot, calculate_pcr
import logging

def capture_snapshot(ticker, expiration_date, strike_range):
    """
    Captures a snapshot of options data and saves it to database
    
    Params:
        ticker (str)
        expiration_date (str): YYYY-MM-DD
        strike_range (int): The range of strike prices around the current price to fetch
    
    Returns: 
        None
    """
    try:
        underlying_price = fetch_underlying_price(ticker)
        
        if underlying_price is None:
            logging.warning(f"Failed to fetch underlying price for {ticker}")
            
            
        options_data = fetch_options_snapshot(ticker, expiration_date, underlying_price, strike_range)
        
        if not options_data:
            logging.warning(f"Failed to fetch underlying price for {ticker}")
            return

        pcr = calculate_pcr(options_data)
        logging.info(f"Put/Call Ratio: {pcr}")

        snapshot = {
            "timestamp": datetime.now() - timedelta(minutes=15),
            "underlying_ticker": ticker,
            "underlying_price": underlying_price,
            "expiration_date": expiration_date,
            "put_call_ratio": pcr,
            "options_data": options_data
        }

        save_snapshot(snapshot)
        
        
        df = pd.DataFrame(options_data)
        print_colored_pivot_df(df)
    except Exception as e:
        logging.error(f"Error capturing snapshot: {e}")
        
