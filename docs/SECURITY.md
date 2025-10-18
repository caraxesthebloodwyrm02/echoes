# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Security Measures

### 1. XML Security
- **Vulnerability Addressed**: XML External Entity (XXE) attacks
- **Implementation**:
  - Replaced `xml.etree.ElementTree` with `defusedxml.ElementTree`
  - Added `forbid_dtd=True` to XML parsing
  - Added `defusedxml` to requirements.txt

### 2. Network Security
- **Vulnerability Addressed**: Insecure network binding
- **Implementation**:
  - Default binding to `127.0.0.1` in development
  - Configurable host/port via environment variables
  - Production template binds to `0.0.0.0` with proper firewall rules

### 3. Command Injection Prevention
- **Vulnerability Addressed**: Command injection via subprocess calls
- **Implementation**:
  - Removed all `shell=True` from `subprocess` calls
  - Implemented `shlex.split()` for safe command parsing
  - Added input validation for all command arguments

### 4. Environment Configuration
- **Files**:
  - `.env.example`: Template with development defaults
  - `.env.production`: Production configuration template
- **Security Features**:
  - Separate configurations for dev/prod
  - Sensitive defaults (e.g., localhost binding)
  - Clear documentation of security-critical settings

### 5. Secure Production Deployment
- **Features**:
  - Dedicated `main_production.py` with security middleware
  - HTTPS redirection
  - Security headers (CSP, XSS Protection, etc.)
  - Trusted host validation

## Reporting a Vulnerability

To report a security vulnerability, please email security@yourapp.com with:
- A description of the vulnerability
- Steps to reproduce
- Any potential impact

We will respond within 48 hours and keep you updated on our progress.

## Security Best Practices

1. **Never commit sensitive data** to version control
2. Use environment variables for all secrets and configurations
3. Keep dependencies updated with `pip list --outdated`
4. Run security scans regularly using:
   ```bash
   # Run Bandit security scanner
   python -m bandit -r app/

   # Check for vulnerable dependencies
   pip install safety
   safety check
   ```

## Security Headers

Production deployments include these security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy: default-src 'self'`

## Monitoring and Logging

- All security-relevant events are logged
- Failed login attempts are monitored
- Suspicious activities trigger alerts

## Dependencies

Regularly update dependencies to include security patches:
```bash
pip install --upgrade pip
pip list --outdated
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
