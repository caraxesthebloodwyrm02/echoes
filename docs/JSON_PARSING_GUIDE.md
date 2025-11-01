# JSON Parsing Error Guide: "invalid character '{' after top-level value"

## TL;DR

**`json.JSONDecodeError: Expecting value: line 1 column X`** or **`invalid character '{' after top-level value`** means the JSON decoder has already finished parsing a complete value (object, array, string, number, …) and then sees another `{` (or any other non-whitespace character). In other words, the input contains **more than one top-level JSON value**, or there is stray/garbage data before/after the real JSON.

The fix is to make sure the data you feed to `json.loads()` or `json.load()` is **exactly one valid JSON value**—nothing else, not even a stray `{` or a trailing HTML error page.

---

## 1️⃣ What the Error Looks Like in Python

```python
import json

# This will raise a JSONDecodeError:
data = '{"name":"alice"}{"name":"bob"}'
try:
    v = json.loads(data)
except json.JSONDecodeError as e:
    print(f"JSON error: {e}")
```

Output:

```
JSONDecodeError: Expecting value: line 1 column 13 (char 13)
```

The decoder parsed the first object `{"name":"alice"}` successfully, then encountered the second `{` and complained.

---

## 2️⃣ Typical Scenarios that Trigger It

| # | Scenario | Why it fails |
|---|----------|--------------|
| 1 | **Two JSON objects concatenated** (`{...}{...}`) | JSON spec allows only one root value. |
| 2 | **Object + trailing newline + HTML error page** (e.g. server returned a 500 HTML page) | After the JSON the decoder sees `<` or `{` from the HTML. |
| 3 | **BOM or stray characters before the `{`** (e.g. `\ufeff{...}`) | The decoder treats the BOM as a character, not whitespace. |
| 4 | **Reading from a buffer that already consumed part of the stream** | Left-over bytes get fed to the decoder again. |
| 5 | **Using `json.loads()` on a string that contains *multiple* JSON lines** (common in log files) | Same as #1 – only the first line is valid. |
| 6 | **Incorrect Content-Type handling** – you think you have JSON but you actually got a template (e.g. `{{ . }}`) | The first `{` is not part of a JSON object. |

---

## 3️⃣ Quick Diagnostic Steps

1. **Print the raw payload** (as a string or hex dump) *before* you try to parse it.

   ```python
   print(f"raw payload: {data!r}")  # !r shows escape codes
   print(f"hex dump: {data.encode('utf-8').hex()}")
   ```

2. **Validate the JSON** with an online linter (jsonlint.com) or Python's built-in validator:

   ```python
   import json
   try:
       json.loads(data)
       print("Valid JSON")
   except json.JSONDecodeError as e:
       print(f"Invalid: {e}")
   ```

3. **Check the HTTP status code** if the data comes from an HTTP response. A `500` often means you got an HTML error page, not JSON.

   ```python
   import requests
   
   resp = requests.get(url)
   if resp.status_code != 200:
       print(f"Unexpected status {resp.status_code}: {resp.text[:500]}")
       raise ValueError(f"HTTP {resp.status_code}")
   ```

4. **Trim whitespace and possible BOM**:

   ```python
   data = data.strip()
   # Remove UTF-8 BOM
   if data.startswith('\ufeff'):
       data = data[1:]
   ```

5. **If you truly need to read multiple JSON objects**, use a streaming approach or line-by-line parsing instead of `json.loads()`.

---

## 4️⃣ Fixing the Problem in Python

### 4.1 When you *only* expect **one** JSON value

```python
import json
import re

def safe_json_loads(data: str) -> dict:
    """Safely parse JSON with common cleanup steps."""
    if not isinstance(data, str):
        raise TypeError(f"Expected str, got {type(data)}")
    
    # 1️⃣ Trim whitespace/BOM
    data = data.strip()
    data = data.lstrip('\ufeff')  # Remove UTF-8 BOM
    
    # 2️⃣ Try direct parsing first
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        pass  # Fall through to cleanup attempts
    
    # 3️⃣ Clean common formatting artifacts
    data = data.strip('`').strip('"').strip()
    
    # 4️⃣ Extract from code blocks if present
    if '```json' in data:
        match = re.search(r'```json\s*(.*?)\s*```', data, re.DOTALL)
        if match:
            data = match.group(1).strip()
    elif '```' in data:
        match = re.search(r'```\s*(.*?)\s*```', data, re.DOTALL)
        if match:
            data = match.group(1).strip()
    
    # 5️⃣ Extract JSON object if there's extra text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', data)
    if json_match:
        data = json_match.group()
    
    # 6️⃣ Final attempt
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Cannot parse JSON after cleanup. Original error: {e.msg}",
            e.doc,
            e.pos
        ) from e

# Usage
raw = '  {"name":"alice","age":30}   '
person = safe_json_loads(raw)
print(person)  # {'name': 'alice', 'age': 30}
```

### 4.2 When you really have **multiple concatenated JSON objects**

```python
import json
from typing import Iterator, Any

def parse_multiple_json(data: str) -> Iterator[dict]:
    """Parse multiple concatenated JSON objects."""
    decoder = json.JSONDecoder()
    idx = 0
    
    while idx < len(data):
        # Skip whitespace
        data = data[idx:].lstrip()
        idx = 0
        
        if not data:
            break
        
        try:
            obj, idx = decoder.raw_decode(data, idx)
            yield obj
        except json.JSONDecodeError as e:
            print(f"Parse error at position {e.pos}: {e.msg}")
            break

# Usage
payload = '{"id":1,"msg":"first"}{"id":2,"msg":"second"}'
for obj in parse_multiple_json(payload):
    print(f"Got object: {obj}")
```

Output:

```
Got object: {'id': 1, 'msg': 'first'}
Got object: {'id': 2, 'msg': 'second'}
```

### 4.3 Using a **streaming parser** for large files or logs

If you have a log file where each line is a JSON object:

```python
import json
from pathlib import Path

def parse_json_lines(file_path: Path) -> Iterator[dict]:
    """Parse a file with one JSON object per line."""
    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Bad line {line_num} {line[:50]!r}: {e}")
                continue

# Usage
for event in parse_json_lines(Path("events.log")):
    process(event)
```

---

## 5️⃣ Common "Got HTML instead of JSON" Gotchas

```python
import requests
import json

resp = requests.get("https://api.example.com/data")

if resp.status_code != 200:
    # Most servers send an HTML error page; trying to parse it will hit the
    # "invalid character '<' after top-level value" error.
    print(f"HTTP {resp.status_code}: {resp.text[:500]}")
    raise ValueError(f"Unexpected status {resp.status_code}")

# Verify Content-Type
content_type = resp.headers.get('Content-Type', '')
if 'application/json' not in content_type:
    print(f"Unexpected Content-Type: {content_type}")
    print(f"Response preview: {resp.text[:500]}")
    raise ValueError(f"Expected JSON, got {content_type}")

try:
    data = resp.json()
except json.JSONDecodeError as e:
    print(f"JSON parse error: {e}")
    print(f"Response text: {resp.text[:1000]}")
    raise
```

If you *still* see the `{` version of the error, it usually means the server returned **something that starts with `{` but is **not** a valid JSON top-level value**—for example a Go-style template (`{{ . }}`) or an error object *wrapped* inside HTML.

---

## 6️⃣ Checklist – "Did I miss something?"

- [ ] **Only one JSON value** in the string you pass to `json.loads()`.
- [ ] **No stray characters** before or after the value (including invisible BOM).
- [ ] **Correct HTTP status** (200-OK) before attempting to decode.
- [ ] **Content-Type** is `application/json` (or a known variant).
- [ ] If you need **multiple objects**, switch to a streaming parser or line-by-line approach.
- [ ] **Validate** the raw data with a JSON linter if you're unsure.

---

## 7️⃣ TL;DR Code Snippet (copy-paste)

```python
import json
import requests
from typing import Dict, Any

def fetch_and_parse_json(url: str) -> Dict[str, Any]:
    """Fetch JSON from a remote API with error handling."""
    resp = requests.get(url)
    
    # 1️⃣ Verify we got a successful response
    if resp.status_code != 200:
        body = resp.text[:500]
        raise ValueError(f"HTTP {resp.status_code}: {body}")
    
    # 2️⃣ Verify Content-Type
    content_type = resp.headers.get('Content-Type', '')
    if 'application/json' not in content_type:
        raise ValueError(f"Expected JSON, got Content-Type: {content_type}")
    
    # 3️⃣ Read and clean the data
    data = resp.text.strip()
    data = data.lstrip('\ufeff')  # Remove BOM if present
    
    # 4️⃣ Parse (single value)
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Failed to parse JSON: {e.msg}\nFirst 200 chars: {data[:200]}",
            e.doc,
            e.pos
        ) from e

# Usage
try:
    user_data = fetch_and_parse_json("https://api.example.com/user/123")
    print(f"Got user: {user_data}")
except (ValueError, json.JSONDecodeError) as e:
    print(f"Error: {e}")
```

---

## 8️⃣ When to Ask for More Info

If after trying the above you still see the same message, it helps to see:

1. The **exact raw bytes** (or at least the first ~200 characters) you are feeding to `json.loads()`.
2. The **type** you are parsing into (e.g., `dict` vs. a custom class).
3. How you obtain those bytes (HTTP response, file, `sys.stdin`, etc.).
4. Any **custom decoder** or wrapper you may have around `json.loads()`.

---

## 9️⃣ Integration with Echoes

The Echoes codebase already has some robust JSON parsing patterns in:

- `core_modules/context_aware_api.py` - Handles AI model output with formatting artifacts
- `core_modules/llm_client.py` - `parse_json_response()` method with markdown code block extraction

These patterns should be reused when parsing JSON from external sources or AI model outputs.

---

*Based on Go JSON unmarshaling best practices, adapted for Python*

