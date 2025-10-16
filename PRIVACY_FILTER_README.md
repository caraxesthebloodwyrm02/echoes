# Privacy Filter Implementation

This document describes the comprehensive PII detection and filtering system implemented in the Echoes platform.

## Overview

The privacy filter system provides three levels of PII protection:

1. **Redact**: Complete removal with `[REDACTED]` placeholders
2. **Anonymize**: Consistent token replacement for data analysis
3. **Mask**: Partial information display for UI contexts

## Components

### PrivacyFilter (`packages/security/privacy_filter.py`)

Main filtering engine that detects and processes PII using regex patterns.

**Supported PII Types:**
- Email addresses
- Phone numbers
- Social Security Numbers (SSN)
- Credit card numbers
- IP addresses
- Dates of birth

**Usage:**
```python
from packages.security.privacy_filter import PrivacyFilter

privacy_filter = PrivacyFilter()

# Complete removal
redacted = privacy_filter.redact(text)

# Consistent token replacement
anonymized = privacy_filter.anonymize(text, deterministic=True)

# Partial masking
masked = privacy_filter.mask(text)
```

### PrivacyMiddleware (`packages/security/privacy_middleware.py`)

FastAPI middleware for automatic PII filtering on API responses.

**Usage:**
```python
from packages.security.privacy_middleware import PrivacyMiddleware

middleware = PrivacyMiddleware(filter_mode="mask")

@middleware.filter_response
def get_user_data():
    return {"email": "user@example.com", "phone": "555-123-4567"}
```

### PrivacyScanner (`packages/security/privacy_scanner.py`)

Command-line tool for scanning codebase for PII exposure.

**Usage:**
```bash
# Run as script (recommended)
python packages/security/privacy_scanner.py . --extensions .py

# Scan with custom extensions
python packages/security/privacy_scanner.py /path/to/code --extensions .py,.txt,.md

# Save results to JSON file
python packages/security/privacy_scanner.py . --output scan_results.json

# Use more workers for faster scanning
python packages/security/privacy_scanner.py . --max-workers 4
```

## Best Practices

- **Use `mask()`** for UI display where some context is needed
- **Use `redact()`** for logs and debugging output
- **Use `anonymize()`** when you need to track relationships while maintaining privacy
- **Always use middleware** for API endpoints to ensure consistent protection
- **Run regular privacy scans** to detect any PII exposure in codebase

## Security Considerations

- Regex patterns are designed to minimize false positives
- Token caching ensures consistent anonymization
- Middleware recursively processes nested data structures
- Scanner excludes common development directories (`.venv`, `__pycache__`, etc.)

## Integration

The privacy modules are automatically imported in `packages/security/__init__.py`:

```python
from packages.security import PrivacyFilter, PrivacyMiddleware, PrivacyScanner
```

## Testing

Run the test suite:

```bash
python test_privacy_filter.py
```

This will demonstrate all filtering modes and middleware functionality.
