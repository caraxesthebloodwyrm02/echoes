import requests

# Test OMDb API
url = "http://www.omdbapi.com/?apikey=thewaitingroom&s=Matrix"
try:
    response = requests.get(url, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Response text: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
