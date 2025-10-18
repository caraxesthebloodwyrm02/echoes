# 05 Error Handling

## Model: mistral:7b-instruct

## Processing Time: 118.96s

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
    Fetches data from the given URL using exponential backoff with jitter and retry mechanism.

    Parameters:
        url (str): The API endpoint to fetch data from.
        max_retries (int, optional): The maximum number of retries before giving up. Defaults to 5.

    Returns:
        The fetched data as a dictionary, or None if all retries fail.
    """

    def backoff_time(attempt: int) -> float:
        # Exponential backoff with jitter starting at 1 second
        return min(2 ** attempt * random.uniform(0.5, 1.5), 60)

    def on_success(response: requests.Response) -> None:
        # Logging of successful request
        print(f"Request to {url} succeeded.")

    def on_failure(exception: Exception) -> None:
        # Logging of failed request and increasing the retry count
        current_attempt = retry_count + 1
        print(f"Request to {url} failed (attempt {current_attempt}/{max_retries}).")

    attempts = 0
    retry_count = 0

    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raises RequestException if the request failed
            on_success(response)
            return response.json()
        except (requests.exceptions.RequestException, Timeout) as exception:
            if attempts >= max_retries:
                print("All retries have been exhausted.")
                return None

            retry_count += 1
            wait_time = backoff_time(attempts)
            print(f"Sleeping for {wait_time} seconds before retry...")
            time.sleep(wait_time)
            attempts += 1

    # This code will never be executed as the while loop breaks on successful response or reaching the max retries limit
```

This function defines `fetch_with_retry` that accepts a URL and an optional maximum number of retries. It uses exponential backoff with jitter, logs retry attempts, handles exceptions (including Timeout), and returns None if all retries fail.