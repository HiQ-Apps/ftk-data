import yfinance as yf
import pandas as pd
from datetime import datetime

# Define the symbol for EURUSD
symbol = 'EURUSD=X'

# Define the date range
start_date = '2023-07-03'
end_date = '2023-07-04'  # End date is exclusive, so this fetches data up to and including July 3rd

# Fetch the data
data = yf.download(symbol, start=start_date, end=end_date, interval='1d')

# Display the data
print(data)