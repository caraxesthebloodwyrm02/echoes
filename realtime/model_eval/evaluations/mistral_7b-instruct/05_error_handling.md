# 05 Error Handling

## Model: mistral:7b-instruct

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

Here's a Python function that implements exponential backoff with jitter for retrying failed API requests:

```python
import time
import random
import requests
from typing import Optional, Callable

def fetch_with_retry(url: str, max_retries: int = 5) -> Optional[dict]:
    """
    Fetches data from the provided URL using exponential backoff with jitter.

    Args:
        url (str): The URL to fetch data from.
        max_retries (int, optional): The maximum number of retries before giving up. Defaults to 5.

    Returns:
        Optional[dict]: The fetched data if successful, None otherwise.
    """

    def backoff_strategy(current_attempt: int) -> float:
        # Exponential backoff starting at 1 second
        # Jitter is added to avoid synchronization issues
        base_backoff = 2 ** current_attempt
        jitter = random.uniform(0, 0.5)
        return base_backoff + jitter

    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
        except (requests.exceptions.RequestException, TimeoutError):
            print(f"Retrying request ({attempts + 1}/{max_retries}) to {url}")

        # Implement exponential backoff with jitter
        wait_time = backoff_strategy(attempts)
        print(f"Waiting {wait_time} seconds before retrying...")
        time.sleep(wait_time)
        attempts += 1

    print("All retries have failed, returning None.")
    return None
```

This function takes a URL and the maximum number of retries as arguments, fetches data from the provided URL using `requests`, implements exponential backoff with jitter for retrying failed requests, logs each retry attempt, handles exceptions, adds a timeout for the request, and returns `None` if all retries fail.