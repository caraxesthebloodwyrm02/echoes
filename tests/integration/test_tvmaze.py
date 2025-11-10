from urllib.parse import quote_plus

import requests

# Test TVMaze API
url = f"https://api.tvmaze.com/search/shows?q={quote_plus('Office')}"
try:
    response = requests.get(url, timeout=10)
    print(f"Status code: {response.status_code}")
    data = response.json()
    print(f"Found {len(data)} results")
    if data:
        print(f"First result: {data[0]['show']['name']}")
except Exception as e:
    print(f"Error: {e}")
