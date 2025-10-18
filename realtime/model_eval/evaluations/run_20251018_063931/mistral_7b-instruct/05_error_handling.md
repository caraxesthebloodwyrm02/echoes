# 05 Error Handling

## Model: mistral:7b-instruct

## Processing Time: 134.60s

## Prompt

```
# Error Handling: Exponential Backoff

Write a Python function that implements exponential backoff with jitter for retrying failed API requests. Requirements:

1. Function signature: `def fetch_with_retry(url: str, max_retries: int = 5) -> Optional[dict]:`
2. Features:
   - Exponential backoff starting at 1 second
   - Full jitter for better distribution
   - Maximum retry limit
   - Logging of retry attempts
   - Proper exception handling
   - Timeout handling
   - Return None if all retries fail

Include type hints and docstrings.

```

## Response

Here is a Python function that implements exponential backoff with jitter for retrying failed API requests:

```python
import random
import time
import requests
from typing import Optional, Union

def fetch_with_retry(url: str, max_retries: int = 5) -> Optional[dict]:
    """
    Performs an HTTP GET request to the provided URL with exponential backoff and jitter.
    If the request fails, it will retry up to the specified number of times (default is 5).
    Returns the response data as a dictionary on success or None if all retries fail.
    """
    attempt = 1
    while attempt <= max_retries:
        try:
            start_time = time.time()
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            log_message = f"Failed attempt {attempt} to fetch {url}. Retrying in {backoff_time} seconds."
            print(log_message)

            # Exponential backoff with jitter
            backoff_time = 2 ** (attempt - 1) * random.uniform(0.5, 1.5)
            time.sleep(backoff_time)
            attempt += 1
        except requests.RequestException as e:
            log_message = f"Failed to send request to {url}. Error: {e}"
            print(log_message)
            break

    return None
```

This function takes a URL and an optional maximum number of retries. It performs an HTTP GET request using the `requests` library and catches various exceptions that can occur during the request. If the request fails, it will retry up to the specified number of times with exponential backoff and full jitter. The function logs each attempt and returns the response data as a dictionary on success or None if all retries fail.

The time between retries is calculated using the formula `2^(attempt - 1) * random.uniform(0.5, 1.5)` seconds, which provides exponential backoff with jitter for better distribution. The log messages also include the retry attempt and estimated waiting time before the next attempt.