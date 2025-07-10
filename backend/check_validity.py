import requests
import os
from dotenv import load_dotenv

load_dotenv()

#Has a rate limit - used temporarily
GOOGLE_API_KEY = os.getenv('API_KEY')
PSE_KEY = os.getenv('PSE_KEY')

def check_home_for_sale(address):
    query = f"{address} site:zillow.com"
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": PSE_KEY,
        "q": query,
    }

    res = requests.get(url, params=params)
    data = res.json()

    # Handle errors
    if "items" not in data:
        return False  # No result or quota exceeded

    for item in data["items"]:
        snippet = item.get("snippet", "").lower()
        if "for sale" in snippet:
            return True
        if "off market" in snippet or "sold on" in snippet:
            return False

    return False  # Uncertain status

check_home_for_sale("")