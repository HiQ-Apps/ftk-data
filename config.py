import os
import logging
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

logging.basicConfig(level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)