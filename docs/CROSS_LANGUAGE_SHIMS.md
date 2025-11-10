# Cross-Language Policy Shims

This document defines a minimal, language-agnostic interface for enforcing the egress policy across multiple runtimes (Python, Node.js, Go). Each shim must evaluate outbound requests via the common decision contract and enforce the result consistently.

See `POLICY_SPEC.md` for the canonical rules and decision fields.

## Decision Contract

Input:
- `method`: HTTP method (e.g., `GET`)
- `url`: Absolute URL
- `meta` (optional): Caller name, component, or tags

Output (JSON-like):
```
{
  "allowed": bool,
  "reason": "string",
  "matched_token": "string|null",
  "destination_host": "string"
}
```

If `allowed=false` and `EGRESS_ENFORCE=1`, the shim must prevent the network call and return/raise a policy error.

## Python (requests/urllib3)

```python
# shim_policy.py
import os
from urllib.parse import urlparse

ALLOWED = [t.strip().lower() for t in os.getenv("EGRESS_ALLOWLIST", "openai").split(",") if t.strip()]
ENFORCE = os.getenv("EGRESS_ENFORCE", "1") == "1"

class PolicyViolation(RuntimeError):
    pass

def decide(method: str, url: str, meta: dict | None = None):
    host = urlparse(url).hostname or ""
    token = next((t for t in ALLOWED if t and t in host.lower()), None)
    allowed = token is not None
    reason = "allowed" if allowed else f"blocked: host '{host}' not in allowlist"
    return {"allowed": allowed, "reason": reason, "matched_token": token, "destination_host": host}

def guard_request(method: str, url: str, meta: dict | None = None):
    d = decide(method, url, meta)
    if not d["allowed"] and ENFORCE:
        raise PolicyViolation(d["reason"])
    return d
```

Usage with `requests`:
```python
import requests
from shim_policy import guard_request

def get(url):
    guard_request("GET", url, {"caller": "example"})
    return requests.get(url)
```

## Node.js (fetch/axios)

```js
// shimPolicy.js
const ALLOWED = (process.env.EGRESS_ALLOWLIST || "openai")
  .split(",").map(s => s.trim().toLowerCase()).filter(Boolean);
const ENFORCE = (process.env.EGRESS_ENFORCE || "1") === "1";

class PolicyViolation extends Error {}

function hostFromUrl(url) { return new URL(url).hostname || ""; }

function decide(method, url, meta) {
  const host = hostFromUrl(url);
  const token = ALLOWED.find(t => host.toLowerCase().includes(t));
  const allowed = Boolean(token);
  const reason = allowed ? "allowed" : `blocked: host '${host}' not in allowlist`;
  return { allowed, reason, matched_token: token || null, destination_host: host };
}

function guardRequest(method, url, meta) {
  const d = decide(method, url, meta);
  if (!d.allowed && ENFORCE) throw new PolicyViolation(d.reason);
  return d;
}

module.exports = { decide, guardRequest, PolicyViolation };
```

Usage:
```js
const { guardRequest } = require("./shimPolicy");
const fetch = require("node-fetch");

async function get(url) {
  guardRequest("GET", url, { caller: "example" });
  return fetch(url);
}
```

## Go (net/http)

```go
// shimpolicy/shimpolicy.go
package shimpolicy

import (
    "errors"
    "net/url"
    "os"
    "strings"
)

type Decision struct {
    Allowed        bool
    Reason         string
    MatchedToken   *string
    DestinationHost string
}

var (
    allowed = func() []string {
        raw := os.Getenv("EGRESS_ALLOWLIST")
        if raw == "" { raw = "openai" }
        parts := strings.Split(raw, ",")
        out := make([]string, 0, len(parts))
        for _, p := range parts {
            p = strings.ToLower(strings.TrimSpace(p))
            if p != "" { out = append(out, p) }
        }
        return out
    }()
    enforce = os.Getenv("EGRESS_ENFORCE") == "1" || os.Getenv("EGRESS_ENFORCE") == ""
)

func Decide(method, rawurl string, meta map[string]string) Decision {
    u, _ := url.Parse(rawurl)
    host := ""
    if u != nil { host = u.Hostname() }
    var token *string
    for _, t := range allowed {
        if strings.Contains(strings.ToLower(host), t) { token = &t; break }
    }
    allowedBool := token != nil
    reason := "allowed"
    if !allowedBool { reason = "blocked: host not in allowlist" }
    return Decision{Allowed: allowedBool, Reason: reason, MatchedToken: token, DestinationHost: host}
}

func GuardRequest(method, rawurl string, meta map[string]string) (Decision, error) {
    d := Decide(method, rawurl, meta)
    if !d.Allowed && enforce {
        return d, errors.New(d.Reason)
    }
    return d, nil
}
```

## Requirements

- Do not implement wildcard or bypass paths.
- Always log the decision in local development for visibility.
- Prefer unit tests that assert `GuardRequest/guardRequest` behavior for blocked and allowed hosts.
