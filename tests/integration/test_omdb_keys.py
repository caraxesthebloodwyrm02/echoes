from urllib.parse import quote_plus

import requests

# Test OMDb API with different keys
api_keys = ["thewaitingroom", "9f89d0f", "b7a1d4f"]

for api_key in api_keys:
    print(f"\nTesting API key: {api_key}")
    url = f"http://www.omdbapi.com/?apikey={api_key}&s={quote_plus('Matrix')}"
    try:
        response = requests.get(url, timeout=10)
        print(f"Status code: {response.status_code}")
        data = response.json()
        print(f"Response: {data}")
    except Exception as e:
        print(f"Error: {e}")
