import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from utils.utils import fetch_options_snapshot

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

from datetime import datetime

# Sample ticker and test parameters
ticker = "SPY"
expiration_date = "2024-11-08"  # A recent past expiration date to fetch historical data
current_price = 598.19  # Approximate close price
strike_range = 10  # ±10 strikes around the current price

# Test function to fetch and print data
def test_fetch_options_snapshot():
    try:
        options_data = fetch_options_snapshot(ticker, expiration_date, current_price, strike_range)
        
        if options_data:
            print("Options data fetched successfully. Displaying sample results:")
            for option in options_data[:5]:  # Display first 5 results for brevity
                print(f"Contract: {option['contract']}")
                print(f"Type: {option['type']}, Strike Price: {option['strike_price']}")
                print(f"Close Price: {option['close_price']}, Volume: {option['volume']}, Open Interest: {option['open_interest']}")
                print(f"Delta: {option['greeks']['delta']}, Gamma: {option['greeks']['gamma']}")
                print(f"Implied Volatility: {option['implied_volatility']}")
                print("----")
        else:
            print("No options data returned. This could be due to data unavailability or permissions.")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# Run the test function
test_fetch_options_snapshot()

def test_db_connnection():
    try:
        client = MongoClient(MONGO_URI)
        db = client['options_data']
        collection = db['snapshots']
        
        test_document = {
            "test": "testing connection",
            "timestamp": datetime.now()
        }
        
        collection.insert_one(test_document)
        print("Test document inserted successfully")
        
        result = collection.find_one({"test": "testing connection"})
        if result:
            print("Test document found in mongoDB:", result)
        else:
            print("Test document not found in database")
    except Exception as e:
        print("Error connecting to MongoDB: {e}")
        
if __name__ == "__main__":
    test_db_connnection()
    test_fetch_options_snapshot()