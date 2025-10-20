import time
from .ingest_docs import parse_security_protocols


class RateLimiter:
    """A simple token bucket rate limiter."""

    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.tokens = self.requests_per_minute
        self.last_request_time = time.time()

    def is_allowed(self):
        current_time = time.time()
        time_passed = current_time - self.last_request_time
        self.last_request_time = current_time

        self.tokens += time_passed * (self.requests_per_minute / 60)
        if self.tokens > self.requests_per_minute:
            self.tokens = self.requests_per_minute

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class GuardrailMiddleware:
    """Middleware to enforce security protocols parsed from documentation."""

    def __init__(self, doc_path, rate_limit_per_minute=60, max_prompt_length=4096):
        self.protocols = parse_security_protocols(doc_path)
        self.rate_limiter = RateLimiter(rate_limit_per_minute)
        self.max_prompt_length = max_prompt_length

    def validate_request(self, request_body, headers=None):
        """Validates an incoming request against all relevant security protocols."""
        headers = headers or {}

        # --- Protocol: Input Validation & Sanitization ---
        validation_rules = self.protocols.get("input_validation_sanitization", [])
        if not validation_rules:
            return False, "Guardrail failure: No validation rules found in documentation."

        # Rule: Presence and type of 'prompt' and 'stage'
        if "prompt" not in request_body or not isinstance(request_body["prompt"], str):
            return False, "Validation failed: 'prompt' is missing or not a string."
        if "stage" not in request_body or not isinstance(request_body["stage"], str):
            return False, "Validation failed: 'stage' is missing or not a string."

        # Rule: Bound user-provided text length
        if len(request_body["prompt"]) > self.max_prompt_length:
            return False, f"Validation failed: 'prompt' exceeds maximum length of {self.max_prompt_length} characters."

        # --- Protocol: Rate Limiting ---
        if not self.rate_limiter.is_allowed():
            return False, "Validation failed: Rate limit exceeded."

        # --- Protocol: Authentication ---
        if "Authorization" not in headers or not headers["Authorization"].startswith("Bearer "):
            return False, "Validation failed: Missing or invalid Authorization header."

        return True, "Validation successful."
