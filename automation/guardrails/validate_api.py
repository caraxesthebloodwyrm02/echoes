from ingest_docs import parse_security_protocols
import time

# --- Rate Limiter Simulation ---
class RateLimiter:
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
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

def validate_post_input(request_body, protocols, max_prompt_length=4096, rate_limiter=None, headers=None):
    """Validates the request body for a POST to /input based on parsed protocols."""
    headers = headers or {}
    validation_rules = protocols.get('input_validation_sanitization', [])
    if not validation_rules:
        return False, "No validation rules found in documentation."

    # Rule: "Validate JSON body for `POST /input` (presence and type of `prompt`, `stage`)."
    if 'prompt' not in request_body or not isinstance(request_body['prompt'], str):
        return False, "Validation failed: 'prompt' is missing or not a string."

    if 'stage' not in request_body or not isinstance(request_body['stage'], str):
        return False, "Validation failed: 'stage' is missing or not a string."

    # Rule: "Sanitize and bound user-provided text length; throttle oversized inputs."
    if len(request_body['prompt']) > max_prompt_length:
        return False, f"Validation failed: 'prompt' exceeds maximum length of {max_prompt_length} characters."

    # Rule: "Apply per-IP and per-user limits on `POST /input`."
    if rate_limiter and not rate_limiter.is_allowed():
        return False, "Validation failed: Rate limit exceeded."

    # Rule: "For internal deployments, support bearer/API key auth on `POST /input` and `GET /events`."
    if 'Authorization' not in headers or not headers['Authorization'].startswith('Bearer '):
        return False, "Validation failed: Missing or invalid Authorization header."

    return True, "Validation successful."

if __name__ == '__main__':
    doc_path = 'e:\\\\Projects\\\\Development\\\\docs\\\\glimpse\\\\DEPLOYMENT_AND_OPERATIONS.md'
    all_protocols = parse_security_protocols(doc_path)

    print("--- Running validation checks ---")

    # --- Test Cases ---
    valid_request = {'prompt': 'Hello, world!', 'stage': 'initial'}
    valid_headers = {'Authorization': 'Bearer test-token'}
    missing_prompt = {'stage': 'initial'}
    invalid_prompt_type = {'prompt': 123, 'stage': 'initial'}
    missing_stage = {'prompt': 'Hello, world!'}
    invalid_stage_type = {'prompt': 'Hello, world!', 'stage': False}
    oversized_prompt = {'prompt': 'a' * 5000, 'stage': 'initial'}

    test_cases = {
        "Valid Request": (valid_request, valid_headers, True),
        "Missing Auth Header": (valid_request, {}, False),
        "Missing Prompt": (missing_prompt, valid_headers, False),
        "Invalid Prompt Type": (invalid_prompt_type, valid_headers, False),
        "Missing Stage": (missing_stage, valid_headers, False),
        "Invalid Stage Type": (invalid_stage_type, valid_headers, False),
        "Oversized Prompt": (oversized_prompt, valid_headers, False)
    }

    for name, (case, headers, should_pass) in test_cases.items():
        is_valid, message = validate_post_input(case, all_protocols, headers=headers)
        print(f"[{'PASS' if is_valid == should_pass else 'FAIL'}] {name}: {message}")

    # --- Rate Limiter Test ---
    print("\n--- Testing Rate Limiter ---")
    # Set a low limit (e.g., 2 requests per minute) to test exhaustion
    limiter = RateLimiter(requests_per_minute=2)
    print("Attempting 3 requests in quick succession to exceed limit of 2...")
    for i in range(3):
        is_valid, message = validate_post_input(valid_request, all_protocols, rate_limiter=limiter, headers=valid_headers)
        # The first 2 should pass, the 3rd should fail
        expected_pass = (i < 2)
        print(f"Request {i+1}: [{'PASS' if is_valid == expected_pass else 'FAIL'}] {message}")

    # Wait for tokens to replenish
    print("\nWaiting for tokens to replenish...")
    time.sleep(30) 
    is_valid, message = validate_post_input(valid_request, all_protocols, rate_limiter=limiter, headers=valid_headers)
    print(f"Request after delay: [{'PASS' if is_valid else 'FAIL'}] {message}")

    print("\n--- Validation checks complete ---")
