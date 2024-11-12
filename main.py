import time
from datetime import datetime
from capture_data import capture_snapshot
from utils import fetch_underlying_price


def run_daily_capture(interval=1):
    ticker = "SPY"
    underlying_price = fetch_underlying_price(ticker)
    expiration_date = datetime.now().strftime("%Y-%m-%d")
    strike_range = 5
    market_open_time = datetime.now().replace(hour=6, minute=45, second=0, microsecond=0)
    market_close_time = datetime.now().replace(hour=13, minute=15, second=0, microsecond=0)

    while datetime.now() < market_close_time:
        if datetime.now() >= market_open_time:
            print(f"Market is open! Starting the next {interval} minute intervals")
            print(f"{ticker} is currently trading at {underlying_price}")
            capture_snapshot(ticker, expiration_date, strike_range)

            next_capture_in = interval * 60  
            while next_capture_in > 0:
                mins, secs = divmod(next_capture_in, 60)
                timer = f"Next snapshot to DB in {mins:02}:{secs:02}"
                print(timer, end="\r")
                time.sleep(1)
                next_capture_in -= 1
        else:
            print(f"Market is closed. The current time is {datetime.now().strftime('%H:%M:%S')} PST. Trying again in 1 minute...")
            time.sleep(60)

if __name__ == "__main__":
    run_daily_capture()
