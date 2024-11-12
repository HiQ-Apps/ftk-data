import pymongo
from config import MONGO_URI
import logging

client = pymongo.MongoClient(MONGO_URI)
db = client['options_data']
collection = db['snapshots']

def save_snapshot(data):
    """
    Saves a snapshot of options chain to database
    
    Params:
        data (dict): Saves data structure outlined in main
        
    Returns:
        None
    """
    try:
        collection.insert_one(data)
        logging.info(f"Snapshot saved at {data['timestamp']} for {data['underlying_ticker']}")
    except Exception as e:
        logging.error(f"Failed to saved snapshot: {e}")
        