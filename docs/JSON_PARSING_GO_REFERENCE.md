# Go JSON Unmarshaling Error Guide (Reference)

*Original Go guide for JSON parsing errors - kept as reference for Python developers*

---

## TL;DR

**`unmarshal: invalid character '{' after top‑level value`** means the JSON decoder has already finished parsing a complete value (object, array, string, number, …) and then sees another "`{`" (or any other non‑whitespace character). In other words, the input contains **more than one top‑level JSON value**, or there is stray/garbage data before/after the real JSON.

The fix is to make sure the data you feed to `json.Unmarshal` (or `json.Decoder.Decode`) is **exactly one valid JSON value**—nothing else, not even a stray `{` or a trailing HTML error page.

---

## 1️⃣ What the error looks like in Go

```go
package main

import (
    "encoding/json"
    "fmt"
)

func main() {
    // This will panic with the error you saw:
    data := []byte(`{"name":"alice"}{"name":"bob"}`)
    var v map[string]string
    if err := json.Unmarshal(data, &v); err != nil {
        fmt.Printf("Unmarshal error: %v\n", err)
    }
}
```

Output:

```
Unmarshal error: invalid character '{' after top-level value
```

The decoder parsed the first object `{"name":"alice"}` successfully, then encountered the second `{` and complained.

---

## 2️⃣ Typical Scenarios that Trigger It

| # | Scenario | Why it fails |
|---|----------|--------------|
| 1 | **Two JSON objects concatenated** (`{...}{...}`) | JSON spec allows only one root value. |
| 2 | **Object + trailing newline + HTML error page** (e.g. server returned a 500 HTML page) | After the JSON the decoder sees `<` or `{` from the HTML. |
| 3 | **BOM or stray characters before the `{`** (e.g. `\ufeff{...}`) | The decoder treats the BOM as a character, not whitespace. |
| 4 | **Reading from a `bufio.Reader` that already consumed part of the stream** | Left‑over bytes get fed to the decoder again. |
| 5 | **Using `json.Unmarshal` on a `[]byte` that contains *multiple* JSON lines** (common in log files) | Same as #1 – only the first line is valid. |
| 6 | **Incorrect Content‑Type handling** – you think you have JSON but you actually got a template (e.g. `{{ . }}`) | The first `{` is not part of a JSON object. |

---

## 3️⃣ Quick Diagnostic Steps

1. **Print the raw payload** (as a string or hex dump) *before* you try to unmarshal it.

   ```go
   fmt.Printf("raw payload: %q\n", data) // `%q` shows escape codes
   ```

2. **Validate the JSON** with an online linter (jsonlint.com) or the built‑in `go vet`:

   ```bash
   echo '{"a":1}{"b":2}' | go run ./cmd/validate-json
   ```

3. **Check the HTTP status code** if the data comes from an HTTP response. A `500` often means you got an HTML error page, not JSON.

   ```go
   if resp.StatusCode != http.StatusOK {
       body, _ := io.ReadAll(resp.Body)
       log.Fatalf("unexpected status %d: %s", resp.StatusCode, string(body))
   }
   ```

4. **Trim whitespace and possible BOM**:

   ```go
   data = bytes.TrimSpace(data)
   data = bytes.TrimPrefix(data, []byte("\xef\xbb\xbf")) // UTF‑8 BOM
   ```

5. **If you truly need to read multiple JSON objects**, use a `json.Decoder` in a loop instead of `json.Unmarshal`.

---

## 4️⃣ Fixing the Problem in Go

### 4.1 When you *only* expect **one** JSON value

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "log"
)

func main() {
    // Simulate reading from an HTTP body or a file
    raw := []byte(`  {"name":"alice","age":30}   `) // note the surrounding spaces

    // 1️⃣ Trim whitespace/BOM
    raw = bytes.TrimSpace(raw)
    raw = bytes.TrimPrefix(raw, []byte("\xef\xbb\xbf"))

    // 2️⃣ Unmarshal
    var person struct {
        Name string `json:"name"`
        Age  int    `json:"age"`
    }
    if err := json.Unmarshal(raw, &person); err != nil {
        log.Fatalf("cannot unmarshal: %v\npayload: %s", err, raw)
    }

    fmt.Printf("Decoded: %+v\n", person)
}
```

**Result** – no error.

### 4.2 When you really have **multiple concatenated JSON objects**

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "log"
)

func main() {
    // Example payload with two objects back‑to‑back
    payload := []byte(`{"id":1,"msg":"first"}{"id":2,"msg":"second"}`)

    dec := json.NewDecoder(bytes.NewReader(payload))

    for {
        // We don't know the concrete type, so decode into map[string]any
        var m map[string]any
        if err := dec.Decode(&m); err != nil {
            if err == io.EOF {
                break // finished reading all objects
            }
            log.Fatalf("decode error: %v", err)
        }
        fmt.Printf("Got object: %+v\n", m)
    }
}
```

Output:

```
Got object: map[id:1 msg:first]
Got object: map[id:2 msg:second]
```

**Why this works** – `json.Decoder` stops after the first complete value, leaves the cursor at the start of the next one, and you can call `Decode` again.

### 4.3 Using a **streaming decoder** for large files or logs

If you have a log file where each line is a JSON object, you can combine `bufio.Scanner` with `json.Unmarshal`:

```go
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Bytes()
    var ev Event
    if err := json.Unmarshal(line, &ev); err != nil {
        log.Printf("bad line %q: %v", line, err)
        continue
    }
    // process ev …
}
if err := scanner.Err(); err != nil {
    log.Fatalf("scanner error: %v", err)
}
```

---

## 5️⃣ Common "Got HTML instead of JSON" Gotchas

```go
resp, err := http.Get("https://api.example.com/data")
if err != nil {
    log.Fatal(err)
}
defer resp.Body.Close()

if resp.StatusCode != http.StatusOK {
    // Most servers send an HTML error page; trying to unmarshal it will hit the
    // "invalid character '<' after top-level value" error.
    body, _ := io.ReadAll(resp.Body)
    log.Fatalf("HTTP %d: %s", resp.StatusCode, string(body))
}

body, err := io.ReadAll(resp.Body)
if err != nil {
    log.Fatal(err)
}
```

If you *still* see the `{` version of the error (`invalid character '{' after top-level value`), it usually means the server returned **something that starts with `{` but is **not** a valid JSON top‑level value**—for example a Go‐style template (`{{ . }}`) or an error object *wrapped* inside HTML.

**Solution**: Verify the `Content-Type` header:

```go
if ct := resp.Header.Get("Content-Type"); !strings.HasPrefix(ct, "application/json") {
    log.Fatalf("unexpected content type %q", ct)
}
```

---

## 6️⃣ Checklist – "Did I miss something?"

- [ ] **Only one JSON value** in the byte slice / string you pass to `json.Unmarshal`.
- [ ] **No stray characters** before or after the value (including invisible BOM).
- [ ] **Correct HTTP status** (200‑OK) before attempting to decode.
- [ ] **Content‑Type** is `application/json` (or a known variant).
- [ ] If you need **multiple objects**, switch to `json.Decoder` or a line‑oriented scanner.
- [ ] **Validate** the raw data with a JSON linter if you're unsure.

---

## 7️⃣ TL;DR Code Snippet (copy‑paste)

```go
package main

import (
    "bytes"
    "encoding/json"
    "fmt"
    "io"
    "log"
    "net/http"
)

func main() {
    // Example: fetch JSON from a remote API
    resp, err := http.Get("https://api.example.com/user/123")
    if err != nil {
        log.Fatalf("request error: %v", err)
    }
    defer resp.Body.Close()

    // 1️⃣ Verify we got JSON
    if ct := resp.Header.Get("Content-Type"); !strings.HasPrefix(ct, "application/json") {
        body, _ := io.ReadAll(resp.Body)
        log.Fatalf("expected JSON, got %q: %s", ct, string(body))
    }

    // 2️⃣ Read *exactly* the body
    data, err := io.ReadAll(resp.Body)
    if err != nil {
        log.Fatalf("read error: %v", err)
    }

    // 3️⃣ Clean up whitespace/BOM
    data = bytes.TrimSpace(data)
    data = bytes.TrimPrefix(data, []byte("\xef\xbb\xbf"))

    // 4️⃣ Unmarshal (single value)
    var payload struct {
        ID   int    `json:"id"`
        Name string `json:"name"`
    }
    if err := json.Unmarshal(data, &payload); err != nil {
        // If the error is exactly the one you reported, print the raw payload.
        log.Fatalf("unmarshal error: %v\npayload: %s", err, data)
    }

    fmt.Printf("Got user: %+v\n", payload)
}
```

---

## 8️⃣ When to Ask for More Info

If after trying the above you still see the same message, it helps to see:

1. The **exact raw bytes** (or at least the first ~200 characters) you are feeding to `json.Unmarshal`.
2. The **type** you are unmarshaling into (e.g., `map[string]interface{}` vs. a struct).
3. How you obtain those bytes (HTTP response, file, `os.Stdin`, etc.).
4. Any **custom decoder** you may have wrapped around `json.Unmarshal`.

---

*Original Go guide - kept for reference. See `JSON_PARSING_GUIDE.md` for Python equivalent.*

